#!/usr/bin/python3
import nltk
import sys
import getopt
import pickle

from nltk import PorterStemmer

stemmer = PorterStemmer()


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def searching(dictionary, postings, query, length_dict):
    print("not done")
    # Göra length grejen.
    # Ge scores :P

def find_docs(token, dictionary, postings):
    """
    Help function to index into the postings file.
    """
    nr_docs, offset = dictionary[token]
    postings.seek(offset)
    return postings.readline()


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    dictionary = pickle.load(open(dict_file, "rb"))
    postings = open(postings_file, "r+")
    queries = open(queries_file, "r+")
    length_dict = pickle.load(open("lengthdict", "rb"))
    output = []

    # For each query, evaluate
    for query in queries.readlines():
        tokens = nltk.word_tokenize(query)
        output.append(searching(dictionary, postings, tokens, length_dict))

    # Create the output and write to file
    out_file = open(results_file, "w+")
    for line in output:
        out_file.writelines(" ".join(line) + "\n")


dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None:
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
