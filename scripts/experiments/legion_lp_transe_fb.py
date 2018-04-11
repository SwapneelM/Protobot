#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
import os
import os.path

import sys
import logging


def cartesian_product(dicts):
    return (dict(zip(dicts, x)) for x in itertools.product(*dicts.values()))


def summary(configuration):
    kvs = sorted([(k, v) for k, v in configuration.items()], key=lambda e: e[0])
    return '_'.join([('%s=%s' % (k, v)) for (k, v) in kvs])


def to_cmd(c):
    command = 'python3 ./bin/jack-train.py ' \
              'with config=conf/lp/transe_fb.yaml ' \
              'learning_rate={} repr_dim={} num_negative={} batch_size={} ' \
              'save_dir=/tmp/distmult_fb_{}_{}_{}_{}' \
              ''.format(c['lr'], c['dim'], c['nn'], c['bs'],
                        c['lr'], c['dim'], c['nn'], c['bs'])
    return command


def to_logfile(c, path):
    outfile = "%s/legion_lp_distmult_fb.%s.log" % (path, summary(c).replace("/", "_"))
    return outfile


def main(_):
    hyperparameters_space_1 = dict(
        lr=[0.001, 0.005, 0.01],
        dim=[100, 150, 200, 250, 300, 350],
        nn=[1, 2, 4, 8, 16],
        bs=[32, 64, 128, 256]
    )

    configurations = list(cartesian_product(hyperparameters_space_1))

    path = '/home/ucacmin/Scratch/jack/scripts/experiments/logs/legion_lp_transe_fb/'

    # Check that we are on the Legion cluster first
    if os.path.exists('/home/ucacmin/'):
        # If the folder that will contain logs does not exist, create it
        if not os.path.exists(path):
            os.makedirs(path)

    command_lines = set()
    for cfg in configurations:
        logfile = to_logfile(cfg, path)

        completed = False
        if os.path.isfile(logfile):
            with open(logfile, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                completed = 'hits@10' in content

        if not completed:
            command_line = '{} > {} 2>&1'.format(to_cmd(cfg), logfile)
            command_lines |= {command_line}

    # Sort command lines and remove duplicates
    sorted_command_lines = sorted(command_lines)
    nb_jobs = len(sorted_command_lines)

    header = """#!/bin/bash -l

#$ -cwd
#$ -S /bin/bash
#$ -o /dev/null
#$ -e /dev/null
#$ -t 1-{}
#$ -l mem=8G
#$ -l h_rt=12:00:00

cd /home/ucacmin/workspace/jack

""".format(nb_jobs)

    print(header)

    for job_id, command_line in enumerate(sorted_command_lines, 1):
        print('test $SGE_TASK_ID -eq {} && {}'.format(job_id, command_line))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1:])
