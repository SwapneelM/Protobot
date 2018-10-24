from django.shortcuts import render
from django.http import JsonResponse
from jack import readers
from jack.core import QASetting
import os
from .custom_tf_idf import *

# Adding imports for wikipedia
import wikipedia
from collections import OrderedDict
import unicodedata

document_seen = 99999
# Create your views here.
def home(request):
	document_seen = 0
	request.session['context_passed'] = 0
	return render(request, 'index.html')

def response(request):
	'''
	if request.session['is_asked'] is 0:
		question = request.GET.get('msg')
		document_selected = generate_idf.make_query(question)
		data = {
		'response' : document_selected
		}
		request.session['is_asked'] = 1
		request.session['document_selected'] = document_selected
		return JsonResponse(data)
	else:
		'''
	print(request.session['context_passed'])
	
	if request.session['context_passed'] is 0:
		context = request.GET.get('msg')
		data = {
			'response': 'Ok, ask the question'
			}
		request.session['context'] = context
		request.session['context_passed'] = 1
		return JsonResponse(data)
	else:
		fastqa_reader = readers.reader_from_file(
			os.path.join(
				os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
				'fastqa_reader'
			)
		)	
		#request.session['is_asked'] = 1
		#document_selected = request.GET.get('doc')
		#document_path ='knowledgebase/' + (document_selected.split('/')[-1]).split('.')[0] + '.txt'
		#document_path = 'k'
		'''
		document_path = 'knowledgebase/' + document_selected + '.txt'
		with open(document_path,'r') as myfile:
			support = myfile.read()
			#print (support)
		'''
		question = request.GET.get('msg')
		context = request.session['context']
		answers = fastqa_reader([QASetting(
	    question= question,
	    support=[context]
		)])
		print (answers[0][0].text)
		data = {
		'response': answers[0][0].text
		}
		return JsonResponse(data)

def wikisearch(request):
    for x in request.session['subjects']:
        wikisearch = wikipedia.search(x)
        search_terms = list(OrderedDict.fromkeys(wikisearch))
        for y in search_terms:
            page = wikipedia.page(y)
            title = unicodedata.normalize('NFKD', page.title)\
                .encode('ascii', 'ignore')
            content = unicodedata.normalize('NFKD', page.content)\
                .encode('ascii', 'ignore')
            
            # path to knowledge base (downloaded)

            datapath = os.path.join(os.path.dirname(os.path.dirname(sys.path(__file__))),
							"knowledgebase") + title
            with open(datapath, 'w') as datafile:
                print('Writing file: %s\n' % (title))
                datafile.write(content)
    return True

