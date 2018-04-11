from django.shortcuts import render
from django.http import JsonResponse
from jack import readers
from jack.core import QASetting
import generate_idf
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
		fastqa_reader = readers.reader_from_file("/home/rudresh/Documents/machine_comprehension/jack/fastqa_reader")	
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