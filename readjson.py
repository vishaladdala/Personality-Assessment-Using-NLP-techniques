import os
import re
import sys
import json
import nltk

import gensim
import Levenshtein
import difflib

from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from bs4 import BeautifulSoup
from gensim.models import word2vec
from nltk.corpus import stopwords

# counts = {
# 	'extroverts': 0,
# 	'introverts': 0,
# 	'sensing': 0,
# 	'intuition': 0,
# 	'thinking': 0,
# 	'feeling': 0,
# 	'judging': 0,
# 	'perceiving': 0
# }

#*******************************************************************************
#                           IO METHODS
#*******************************************************************************

def write_file(vocabulary):
	j = json.dumps(vocabulary, indent=4)
	f = open('vocabulary.json', 'w')
	print >> f, j
	f.close()

# Method to read input from a file
def read_input(input_file):
    try:
        return open(input_file).read()
    except IOError:
        print "File '" + input_file + "' does not exist"
        sys.exit(1)

# Method to check whether user has passed corpus file as input
def is_args():
    if (len(sys.argv) == 2):
        return read_input(sys.argv[1])
    else:
        print 'Please provide input file as an argument'
        sys.exit(1)

def print_output(counts):
	output = ""

	temp_dict = {
		"I" : False,
		"E" : False,
		"N" : False,
		"S" : False,
		"T" : False,
		"F" : False,
		"P" : False,
		"J" : False
	}

	if counts["extroverts"] > 0 or counts["introverts"] > 0:
		if counts["extroverts"] > counts["introverts"]:
			output += "E"
		else:
			output += "I"
		temp_dict["E"] = True
		temp_dict["I"] = True

	if counts["sensing"] > 0 or counts["intuition"] > 0:
		if counts["sensing"] > counts["intuition"]:
			output += "S"
		else:
			output += "N"
		temp_dict["S"] = True
		temp_dict["N"] = True

	if counts["thinking"] > 0 or counts["feeling"] > 0:
		if counts["thinking"] > counts["feeling"]:
			output += "T"
		else:
			output += "F"
		temp_dict["T"] = True
		temp_dict["F"] = True

	if counts["judging"] > 0 or counts["perceiving"] > 0:
		if counts["judging"] > counts["perceiving"]:
			output += "J"
		else:
			output += "P"
		temp_dict["J"] = True
		temp_dict["P"] = True

	if len(output) == 4:
		print output
	else:
		traits = output.strip()
		missing_traits = []
		for key in temp_dict:
			if temp_dict[key] is False:
				missing_traits.append(key)
		
		for i in range(len(missing_traits)/2):
			if output[0] == "I":
				output += missing_traits[i*2]
			else:
				output += missing_traits[i*2+1]
		print output


#*******************************************************************************
#                           INTERNAL METHODS
#*******************************************************************************

def update_vocabulary(sentence, vocabulary, max_count_key):
	# tags = ['JJ', 'NN', 'NNS', 'VB', 'VBG', 'VBD', 'RB']
	tags = ['JJ', 'RB']

	pos_tags = nltk.pos_tag(nltk.word_tokenize(sentence))
	# print(pos_tags)
	for token in pos_tags:
		if token[1] in tags:
			if token[0] not in vocabulary[max_count_key]:
				vocabulary[max_count_key].append(token[0].lower())
	write_file(vocabulary)

def get_max(counts):
	max_count_key = "extroverts"

	for key in counts:
		if counts[key] > counts[max_count_key]:
			max_count_key = key
	return max_count_key

def process_text(sentence):
	text = BeautifulSoup(sentence).get_text()
	text = re.sub("[^a-zA-Z]"," ", text)
	return text.lower()

def increase_count(text_list, vocabulary, counts):
	max_count_key = ""

	temp = {
		'extroverts': 0,
		'introverts': 0,
		'sensing': 0,
		'intuition': 0,
		'thinking': 0,
		'feeling': 0,
		'judging': 0,
		'perceiving': 0
	}
	for word in text_list:
		for key in vocabulary:
			if word.lower() in vocabulary[key]:
				counts[key] += 1
				temp[key] += 1
			if len(re.findall(r'\?', word)) > 0:
				counts["thinking"] += len(re.findall(r'\?', word))
	return get_max(temp)

def count_unigrams(data, vocabulary):

	counts = {
		'extroverts': 0,
		'introverts': 0,
		'sensing': 0,
		'intuition': 0,
		'thinking': 0,
		'feeling': 0,
		'judging': 0,
		'perceiving': 0
	}

	max_count_key = ""

	for d in data:
		text_list = d["text"].split()
		# for word in text_list:
			# for key in vocabulary:
			# 	if word in vocabulary[key]:
			# 		counts[key] += 1
		max_count_key = increase_count(text_list, vocabulary, counts)
		# print d['text'], max_count_key
		# update_vocabulary(d["text"], vocabulary, max_count_key)

	# print counts
	print_output(counts)
	return counts

def lemmatize_input(data, vocabulary):

	counts = {
		'extroverts': 0,
		'introverts': 0,
		'sensing': 0,
		'intuition': 0,
		'thinking': 0,
		'feeling': 0,
		'judging': 0,
		'perceiving': 0
	}

	wnl = WordNetLemmatizer()
	for d in data:
		text_list = d["text"].split()
		for word in text_list:
			for key in vocabulary:
				lword = wnl.lemmatize(word)
				if word in vocabulary[key] or lword.lower() in vocabulary[key]:
					counts[key] += 1
				if len(re.findall(r'\?', word)) > 0:
					counts["thinking"] += len(re.findall(r'\?', word))
	print_output(counts)
	return counts

def increase_pos_count(data, counts):
	for d in data:
		counts["extroverts"] += len(d["entities"]["hashtags"])
		counts["thinking"] += len(d["entities"]["urls"])

		text = (d["text"]).encode('unicode-escape').decode('utf-8')
		result = re.findall(r'\\U|\\u', text)
		counts["sensing"] += len(result)

		pos_tags = nltk.pos_tag(nltk.word_tokenize(d["text"]))
		for token in pos_tags:
			if token[1] == "UH":
				counts["extroverts"] += 1
			if token[1] == "PRP":
				counts["introverts"] += 1
			if token[1] == "JJ" or token[1] == "JJR" or token[1] == "JJS":
				counts["feeling"] += 1
			if token[1] == "WP" or token[1] == "WP$" or token[1] == "WRB":
				counts["thinking"] += 1
			if token[1] == "IN" or token[1] == "CC":
				counts["intuition"] += 1
			if token[1] == "RB" or token[1] == "RBR" or token[1] == "RBS" and len(d["entities"]["user_mentions"]) > 0:
				counts["judging"] += len(d["entities"]["user_mentions"])

def pos_tag(data):
	counts = {
		'extroverts': 0,
		'introverts': 0,
		'sensing': 0,
		'intuition': 0,
		'thinking': 0,
		'feeling': 0,
		'judging': 0,
		'perceiving': 0
	}

	increase_pos_count(data, counts)
	print_output(counts)
	return counts
	
def parse_tree(data):
	grammar = nltk.CFG.fromstring("""
		S -> NP N
		S -> DT NP
		NP -> JJ NN
		NP -> NN NN
		NP -> DT NN
		NP -> JJ NP
	""")

	cp = nltk.ChartParser(grammar)

	for d in data:
		text = d["text"]
		tokens = nltk.pos_tag(nltk.word_tokenize(text))
		for tree in cp.parse(tokens):
			print tree

def noun_headwords(data, vocabulary):
	counts = {
		'extroverts': 0,
		'introverts': 0,
		'sensing': 0,
		'intuition': 0,
		'thinking': 0,
		'feeling': 0,
		'judging': 0,
		'perceiving': 0
	}
	for d in data:
		text = d["text"].lower()
		word_list = text.split()
		if "i'm" in word_list or "me" in word_list or "my" in word_list or "mine" in word_list or "myself" in word_list:
			increase_count(word_list, vocabulary, counts)
	print_output(counts)
	return counts


# def process_vocabulary(data, vocabulary, counts):
# 	# for d in data:
# 	text = data[0]["text"]
# 	tokens = nltk.pos_tag(nltk.word_tokenize(text))
# 	# print tokens
# 	# for key in vocabulary:
# 	# for word in vocabulary["feeling"]:
# 	# 	syn_set = wn.synsets(word)
# 	# 	for sense in syn_set:
# 	# 		for lemma in sense.lemmas:
# 	# 			print lemma.name, lemma.sense.pos

# 	for word in vocabulary["feeling"]:
# 		for synset in wn.synsets(word):
# 			print synset.definition()
# 			# for lemma in synset.lemmas():
# 			# 	print lemma.pos

def process_vocabulary(data, vocabulary, counts):
	for d in data:
		text = data[0]["text"]
		word_list = text.split()
		for dword in word_list:
			dsyn_set = wn.synsets(dword.lower())
			for key in vocabulary:
				ratio = 0;
				for vword in vocabulary[key]:
					vsyn_set = wn.synsets(vword.lower())
					for dsense in dsyn_set:
						for vsense in vsyn_set:
							lratio = Levenshtein.ratio(dsense.definition(), vsense.definition())
							dratio = difflib.SequenceMatcher(None, dsense.definition(), vsense.definition()).ratio()
							if lratio > dratio and lratio > ratio:
								ratio = lratio
							if dratio > lratio and dratio > ratio:
								ratio = dratio
				if ratio > 0.8:
					counts[key] += 1;


def count_synonyms(data, vocabulary):
	counts = {
		'extroverts': 0,
		'introverts': 0,
		'sensing': 0,
		'intuition': 0,
		'thinking': 0,
		'feeling': 0,
		'judging': 0,
		'perceiving': 0
	}
	process_vocabulary(data, vocabulary, counts)
	print_output(counts)
	return counts

class MySentences(object):
    def __init__(self, path):
        self.path = path
 
    def __iter__(self):
        for line in open(self.path):
            yield line.split()

def extrovert_model():
	sentences = MySentences("sentences/extroverts.txt")
	# gensim.build_vocab(sentences, keep_raw_vocab=False, trim_rule=None, progress_per=10000, update=False)
	voc_vec = word2vec.Word2Vec(sentences, min_count=1)
	return voc_vec

def remove_stopwords(text):
	temp = []
	for w in text:
		if w not in stopwords.words():
			temp.append(w)
	return temp

def count_extrovert_vectors(data, counts):
	voc_vec = extrovert_model()
	for d in data:
		ttext = remove_stopwords(open("sentences/extroverts.txt").read().lower().split())
		dtext = remove_stopwords(d["text"].lower().split())

		distance = voc_vec.wmdistance(ttext, dtext)
		if distance < 1:
			counts["extroverts"] += 1;

def introvert_model():
	sentences = MySentences("sentences/introverts.txt")
	# gensim.build_vocab(sentences, keep_raw_vocab=False, trim_rule=None, progress_per=10000, update=False)
	voc_vec = word2vec.Word2Vec(sentences, min_count=1)
	return voc_vec

def count_introvert_vectors(data, counts):
	voc_vec = introvert_model()
	for d in data:
		ttext = remove_stopwords(open("sentences/introverts.txt").read().lower().split())
		dtext = remove_stopwords(d["text"].lower().split())

		distance = voc_vec.wmdistance(ttext, dtext)
		if distance < 1:
			counts["introverts"] += 1;

def sensing_model():
	sentences = MySentences("sentences/sensing.txt")
	# gensim.build_vocab(sentences, keep_raw_vocab=False, trim_rule=None, progress_per=10000, update=False)
	voc_vec = word2vec.Word2Vec(sentences, min_count=1)
	return voc_vec

def count_sensing_vectors(data, counts):
	voc_vec = sensing_model()
	for d in data:
		ttext = remove_stopwords(open("sentences/sensing.txt").read().lower().split())
		dtext = remove_stopwords(d["text"].lower().split())

		distance = voc_vec.wmdistance(ttext, dtext)
		if distance < 1:
			counts["sensing"] += 1;

def intuition_model():
	sentences = MySentences("sentences/intuition.txt")
	# gensim.build_vocab(sentences, keep_raw_vocab=False, trim_rule=None, progress_per=10000, update=False)
	voc_vec = word2vec.Word2Vec(sentences, min_count=1)
	return voc_vec

def count_intuition_vectors(data, counts):
	voc_vec = intuition_model()
	for d in data:
		ttext = remove_stopwords(open("sentences/intuition.txt").read().lower().split())
		dtext = remove_stopwords(d["text"].lower().split())

		distance = voc_vec.wmdistance(ttext, dtext)
		if distance < 1:
			counts["intuition"] += 1;

def feeling_model():
	sentences = MySentences("sentences/feeling.txt")
	# gensim.build_vocab(sentences, keep_raw_vocab=False, trim_rule=None, progress_per=10000, update=False)
	voc_vec = word2vec.Word2Vec(sentences, min_count=1)
	return voc_vec

def count_feeling_vectors(data, counts):
	voc_vec = feeling_model()
	for d in data:
		ttext = remove_stopwords(open("sentences/feeling.txt").read().lower().split())
		dtext = remove_stopwords(d["text"].lower().split())

		distance = voc_vec.wmdistance(ttext, dtext)
		if distance < 1:
			counts["feeling"] += 1;

def thinking_model():
	sentences = MySentences("sentences/thinking.txt")
	# gensim.build_vocab(sentences, keep_raw_vocab=False, trim_rule=None, progress_per=10000, update=False)
	voc_vec = word2vec.Word2Vec(sentences, min_count=1)
	return voc_vec

def count_thinking_vectors(data, counts):
	voc_vec = thinking_model()
	for d in data:
		ttext = remove_stopwords(open("sentences/thinking.txt").read().lower().split())
		dtext = remove_stopwords(d["text"].lower().split())

		distance = voc_vec.wmdistance(ttext, dtext)
		if distance < 1:
			counts["thinking"] += 1;

def judging_model():
	sentences = MySentences("sentences/judging.txt")
	# gensim.build_vocab(sentences, keep_raw_vocab=False, trim_rule=None, progress_per=10000, update=False)
	voc_vec = word2vec.Word2Vec(sentences, min_count=1)
	return voc_vec

def count_judging_vectors(data, counts):
	voc_vec = judging_model()
	for d in data:
		ttext = remove_stopwords(open("sentences/judging.txt").read().lower().split())
		dtext = remove_stopwords(d["text"].lower().split())

		distance = voc_vec.wmdistance(ttext, dtext)
		if distance < 1:
			counts["judging"] += 1;

def perceiving_model():
	sentences = MySentences("sentences/perceiving.txt")
	# gensim.build_vocab(sentences, keep_raw_vocab=False, trim_rule=None, progress_per=10000, update=False)
	voc_vec = word2vec.Word2Vec(sentences, min_count=1)
	return voc_vec

def count_perceiving_vectors(data, counts):
	voc_vec = sensing_model()
	for d in data:
		ttext = remove_stopwords(open("sentences/perceiving.txt").read().lower().split())
		dtext = remove_stopwords(d["text"].lower().split())

		distance = voc_vec.wmdistance(ttext, dtext)
		if distance < 1:
			counts["perceiving"] += 1;

def word_vectors(data, counts):
	counts = {
		'extroverts': 0,
		'introverts': 0,
		'sensing': 0,
		'intuition': 0,
		'thinking': 0,
		'feeling': 0,
		'judging': 0,
		'perceiving': 0
	}
	
	count_extrovert_vectors(data, counts)
	count_introvert_vectors(data, counts)
	count_sensing_vectors(data, counts)
	count_thinking_vectors(data, counts)
	count_feeling_vectors(data, counts)
	count_intuition_vectors(data, counts)
	count_judging_vectors(data, counts)
	count_perceiving_vectors(data, counts)
	print_output(counts)
	return counts

def combine_features(ucount, lcount, pcount, ncount, wcount):
	counts = {
		'extroverts': 0,
		'introverts': 0,
		'sensing': 0,
		'intuition': 0,
		'thinking': 0,
		'feeling': 0,
		'judging': 0,
		'perceiving': 0
	}
	for key in counts:
		counts[key] = ucount[key]*0.4 + lcount[key]*0.05 + pcount[key]*0.4 + ncount[key]*0.05 + wcount[key]*0.1
	print_output(counts)

#*******************************************************************************
#                           INTERNAL METHOD CALLS
#*******************************************************************************

# vocabulary = json.loads(read_input("vocabulary.json"))
vocabulary = json.loads(read_input("vocabulary.json"))
# wnl = WordNetLemmatizer()

# for key in vocabulary:
# 	for word in vocabulary[key]:
# 		print wnl.lemmatize(word)

# print vocabulary

# print(vocabulary["thinking"])
data = json.loads(is_args())

# data = (data[0]["text"]).encode('unicode-escape').decode('utf-8')

# lexical feature 1
print "Bag of unigrams: "
ucount = count_unigrams(data, vocabulary)
print ""

# lexical feature 2
print "Lemmatization: "
lcount = lemmatize_input(data, vocabulary)
print ""

# syntactic feature 1
print "POS Tagging: "
pcount = pos_tag(data)
print ""

# syntactic feature 2
print "Head of noun phrases: "
ncount = noun_headwords(data, vocabulary)
print ""

# semantic feature 1
# print "Synonymy: "
# scount = count_synonyms(data, vocabulary)
# print ""

# semantic feature 2
print "Word Vectors: "
wcount = word_vectors(data, vocabulary)
print ""

print "Combined Features: "
combine_features(ucount, lcount, pcount, ncount, wcount)
print ""
