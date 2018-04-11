import logging

import numpy as np
import tensorflow as tf

from jack.tfutil import attention
from jack.tfutil import rnn
from jack.tfutil.activations import activation_from_string
from jack.tfutil.highway import highway_network

logger = logging.getLogger(__name__)


def encoder(sequence, seq_length, repr_dim=100, module='lstm', num_layers=1, conv_width=3,
            dilations=None, reuse=False, residual=False, attn_type=None, num_attn_heads=1, scaled=False,
            activation=None, with_sentinel=False, with_projection=False, name='encoder', num_parallel=1, **kwargs):
    if num_layers == 1:
        if num_parallel == 1:
            if module == 'lstm':
                out = bi_lstm(repr_dim, sequence, seq_length, name, reuse, with_projection)
                if activation:
                    out = activation_from_string(activation)(out)
            elif module == 'sru':
                with_residual = sequence.get_shape()[2].value == repr_dim
                out = bi_sru(repr_dim, sequence, seq_length, with_residual, name, reuse, with_projection)
                if activation:
                    out = activation_from_string(activation)(out)
            elif module == 'gru':
                out = bi_rnn(repr_dim, tf.contrib.rnn.BlockGRUCell(repr_dim), sequence,
                             seq_length, name, reuse, with_projection)
                if activation:
                    out = activation_from_string(activation)(out)
            elif module == 'gldr':
                out = gated_linear_dilated_residual_network(
                    repr_dim, sequence, dilations, conv_width, name, reuse)
            elif module == 'conv':
                out = convnet(repr_dim, sequence, 1, conv_width, activation_from_string(activation), name, reuse)
            elif module == 'conv_glu':
                out = gated_linear_convnet(repr_dim, sequence, 1, conv_width, name, reuse)
            elif module == 'dense':
                out = tf.layers.dense(sequence, repr_dim, name=name, reuse=reuse)
                if activation:
                    out = activation_from_string(activation)(out)
            elif module == 'highway':
                out = highway_network(sequence, num_layers, activation_from_string(activation), name=name, reuse=reuse)
            elif module == 'self_attn':
                outs = []
                for i in range(num_attn_heads):
                    attn = self_attention(sequence, seq_length, attn_type, scaled, repr_dim,
                                          activation_from_string(activation), with_sentinel, name + str(i), reuse)
                    outs.append(attn)
                out = tf.concat(outs, 2) if num_layers > 1 else outs[0]
            else:
                raise ValueError("Unknown encoder type: %s" % module)
        else:
            outs = []
            for i in range(num_parallel):
                outs.append(encoder(sequence, seq_length, repr_dim, module, 1, conv_width,
                                    dilations, reuse, False, attn_type, num_attn_heads, scaled, activation,
                                    with_sentinel, with_projection, name + "_p" + str(i)))
            return tf.concat(outs, 2)
    else:
        out = encoder(sequence, seq_length, repr_dim, module, num_layers - 1, conv_width,
                      dilations, reuse, False, attn_type, num_attn_heads, scaled, activation, with_sentinel,
                      with_projection, name)
        out = encoder(out, seq_length, repr_dim, module, 1, conv_width,
                      dilations, reuse, False, attn_type, num_attn_heads, scaled, activation, with_sentinel,
                      with_projection, name + str(num_layers - 1))
    if residual:
        if out.get_shape()[-1].value != sequence.get_shape()[-1].value:
            logging.error('Residual connection only possible if input to sequence encoder %s of type %s has same '
                          'dimension (%d) as output (%d).' % (name, module, sequence.get_shape()[-1].value,
                                                              out.get_shape()[-1].value))
            raise RuntimeError()
        out += sequence
    return out


# RNN Encoders
def _bi_rnn(size, fused_rnn, sequence, seq_length, name, reuse=False, with_projection=False):
    with tf.variable_scope(name, reuse=reuse):
        output = rnn.fused_birnn(fused_rnn, sequence, seq_length, dtype=tf.float32, scope='rnn')[0]
        output = tf.concat(output, 2)
        if with_projection:
            projection_initializer = tf.constant_initializer(np.concatenate([np.eye(size), np.eye(size)]))
            output = tf.layers.dense(output, size, kernel_initializer=projection_initializer, name='projection')
    return output


def bi_lstm(size, sequence, seq_length, name='bilstm', reuse=False, with_projection=False):
    return _bi_rnn(size, tf.contrib.rnn.LSTMBlockFusedCell(size), sequence, seq_length, name, reuse, with_projection)


def bi_rnn(size, rnn_cell, sequence, seq_length, name='bi_rnn', reuse=False, with_projection=False):
    fused_rnn = tf.contrib.rnn.FusedRNNCellAdaptor(rnn_cell, use_dynamic_rnn=True)
    return _bi_rnn(size, fused_rnn, sequence, seq_length, name, reuse, with_projection)


def bi_sru(size, sequence, seq_length, with_residual=True, name='bi_sru', reuse=False, with_projection=False):
    """Simple Recurrent Unit, very fast.  https://openreview.net/pdf?id=rJBiunlAW."""
    fused_rnn = rnn.SRUFusedRNN(size, with_residual)
    return _bi_rnn(size, fused_rnn, sequence, seq_length, name, reuse, with_projection)


# Convolution Encoders

def convnet(out_size, inputs, num_layers, width=3, activation=tf.nn.relu, name='convnet', reuse=False):
    with tf.variable_scope(name, reuse=reuse):
        # dim reduction
        output = inputs
        for i in range(num_layers):
            output = _convolutional_block(output, out_size, width=width, name="conv_%d" % i)
    return output


def _convolutional_block(inputs, out_channels, width=3, name='conv', activation=tf.nn.relu):
    channels = inputs.get_shape()[2].value
    # [filter_height, filter_width, in_channels, out_channels]
    f = tf.get_variable(name + '_filter', [width, channels, out_channels])
    output = tf.nn.conv1d(inputs, f, 1, padding='SAME', name=name)
    return activation(output)


# following implementation of fast encoding in https://openreview.net/pdf?id=HJRV1ZZAW
def _residual_dilated_convolution_block(inputs, dilation=1, width=3, name="dilated_conv"):
    # [filter_height, filter_width, in_channels, out_channels]
    output = inputs
    channels = inputs.get_shape()[2].value
    for i in range(2):
        # [filter_height, filter_width, in_channels, out_channels]
        output = _convolutional_glu_block(output, channels, dilation, width, name=name + '_' + str(i))
    return output + inputs


def _convolutional_glu_block(inputs, out_channels, dilation=1, width=3, name='dilated_conv'):
    channels = inputs.get_shape()[2].value
    # [filter_height, filter_width, in_channels, out_channels]
    f = tf.get_variable(name + '_filter', [1, width, channels, out_channels * 2])
    output = tf.nn.atrous_conv2d(tf.expand_dims(inputs, 1), f, dilation, 'SAME', name=name)
    output = tf.squeeze(output, 1)
    output, gate = tf.split(output, 2, 2)
    output *= tf.sigmoid(gate)
    return output


def gated_linear_dilated_residual_network(out_size, inputs, dilations, width=3, name='gldr_network', reuse=False):
    """Follows https://openreview.net/pdf?id=HJRV1ZZAW.

    Args:
        out_size: size of output
        inputs: input sequence tensor [batch_size, length, size]
        dilations: list, representing (half of the) network depth; each residual dilation block comprises 2 convolutions

    Returns:
        [batch_size, length, out_size] tensor
    """
    with tf.variable_scope(name, reuse=reuse):
        # dim reduction
        output = _convolutional_glu_block(inputs, out_size, name='conv_dim_reduction')
        for i, d in enumerate(dilations):
            output = _residual_dilated_convolution_block(output, d, width, name='dilated_conv_%d' % i)
    return output


def gated_linear_convnet(out_size, inputs, num_layers, width=3, name='gated_linear_convnet', reuse=False):
    """Follows https://openreview.net/pdf?id=HJRV1ZZAW.

    Args:
        out_size: size of output
        inputs: input sequence tensor [batch_size, length, size]
        num_layers: number of conv layers with width

    Returns:
        [batch_size, length, out_size] tensor
    """
    with tf.variable_scope(name, reuse=reuse):
        # dim reduction
        output = inputs
        for i in range(num_layers):
            output = _convolutional_glu_block(output, out_size, width=width, name="conv_%d" % i)
    return output


# Self attention layers
def self_attention(inputs, lengths, attn_type='bilinear', scaled=True, repr_dim=None, activation=None,
                   with_sentinel=False, name='self_attention', reuse=False):
    with tf.variable_scope(name, reuse=reuse):
        if attn_type == 'bilinear':
            attn_states = attention.bilinear_attention(inputs, inputs, lengths, scaled, with_sentinel)[2]
        elif attn_type == 'dot':
            attn_states = attention.dot_attention(inputs, inputs, lengths, scaled, with_sentinel)[2]
        elif attn_type == 'diagonal_bilinear':
            attn_states = attention.diagonal_bilinear_attention(inputs, inputs, lengths, scaled, with_sentinel)[2]
        elif attn_type == 'mlp':
            attn_states = attention.mlp_attention(repr_dim, inputs, inputs, lengths, activation, with_sentinel)[2]
        else:
            raise ValueError("Unknown attention type: %s" % attn_type)

    return attn_states
