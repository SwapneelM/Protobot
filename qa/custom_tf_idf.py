from collections import Counter
import os
import json
import math
import string

# translator = maketrans("", "", string.punctuation)
# BASEPATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print("\nBASEPATH: ", BASEPATH)

def generate_filepath_list(filepath):
	mypath = filepath
	file_paths_list = []
	print (mypath)
	for path, subdirs, files in os.walk(mypath):
		for name in files:
			filepath = os.path.join(path, name)
			file_paths_list.append(filepath)
	return file_paths_list

def generate_idf():
	BASEPATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	datapath = os.path.join(BASEPATH, "knowledgebase")
	file_paths_list = generate_filepath_list(datapath)
	# word_dict = {}
	# word_dict['document_count_frequency'] = 0

	idf_lookup_table = os.path.join(datapath, 'idf_lookup2.json')

	with open(idf_lookup_table,'r') as myfile:
		word_dict = json.load(myfile)
	# word_dict = json.loads('idf_lookup.json')
	for filepath in file_paths_list:
		word_dict['document_count_frequency'] = word_dict['document_count_frequency'] + 1
		text = ''
		with open(filepath,'r') as myfile:
			text = myfile.read()
		words = text.split()
		words = [word.strip().lower() for word in words]
		word_count = Counter(words)
		# print word_count
		for word in word_count:
			if word in word_dict:
				word_dict[word] = word_dict[word] + 1
			else:
				word_dict[word] = 1
	with open(idf_lookup_table,'w') as fp:
		json.dump(word_dict,fp)


#generate_idf()

def generate_tf():
	# filepath = '/home/rudresh/Documents/be-project/doc'
	BASEPATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	filepath = os.path.join(BASEPATH, "knowledgebase")
	file_paths_list = generate_filepath_list(filepath)
	for filepath in file_paths_list:
		with open(filepath,'r') as myfile:
			text = myfile.read()
		words = text.split()
		words = [word.strip().lower() for word in words]
		word_count = Counter(words)
		filename =  "freq2_stats/" + (filepath.split('/')[-1]).split('.')[0] + '.json'
		print("Filename: ", filename)
		with open(os.path.join(BASEPATH, filename),'w') as fp:
			json.dump(word_count, fp)

#generate_tf()

def make_query(query):
	#query = input('enter query in quotes \n')
	translator = str.maketrans("", "", string.punctuation)
	BASEPATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

	query = query.translate(translator)
	filepath = filepath = os.path.join(BASEPATH, "freq2_stats")

	idf_dict = {}
	with open('idf_lookup2.json','r') as fp:
		idf_dict = json.load(fp)
	file_paths_list = generate_filepath_list(filepath)
	query = query.lower().strip()
	query_words = query.split()
	query_words_idf_scores = {}
	for word in query_words:
		try:
			print (idf_dict['document_count_frequency'])
			print(word)
			print (idf_dict[word])
			query_words_idf_scores[word] = math.log((float(idf_dict['document_count_frequency'])/float(idf_dict[word])))
		except KeyError:
			print('ERROR THROWN')
			query_words_idf_scores[word] = 0
	print (query_words_idf_scores)
	list_of_filepath_dicts = []

	for file_path in file_paths_list:
		flag = 0
		filepath_dict = {}
		words_dict = {}
		filepath_dict['filepath'] = file_path
		filepath_dict['words'] = words_dict
		filepath_dict['score'] = 0
		frequency_stats = {}
		with open(file_path,'r') as fp:
			frequency_stats = json.load(fp)
		sum_freq = sum(frequency_stats.values())
		for word in query_words:
			if word in frequency_stats:
				flag = 1
				words_dict[word] = float(frequency_stats[word])/sum_freq
		filepath_dict['words'] = words_dict
		if flag:
			list_of_filepath_dicts.append(filepath_dict)
	for index, filepath_dict in enumerate(list_of_filepath_dicts):
		score = 0
		for word in filepath_dict['words']:
			score = score + float(query_words_idf_scores[word])*filepath_dict['words'][word]
		list_of_filepath_dicts[index]['score'] = score

	#print list_of_filepath_dicts
	newlist = sorted(list_of_filepath_dicts, key=lambda k: k['score'],reverse=True)
	#print newlist[0]
	print (newlist[0]['filepath'])
	print (newlist[1]['filepath'])
	print (newlist[2]['filepath'])
	return newlist[0]['filepath']

	#print newlist[1]
