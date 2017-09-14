import sys
import json

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


vocabulary = json.loads(read_input("vocabulary.json"))

lvocabulary = {
	"extroverts" : [],
	"introverts" : [],
	"sensing" : [],
	"intuition" : [],
	"thinking" : [],
	"feeling" : [],
	"judging" : [],
	"perceiving" : []
}

for key in vocabulary:
	for word in vocabulary[key]:
		lvocabulary[key].append(word.lower())

write_file(lvocabulary)
