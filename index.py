#!/usr/bin/python3
import math
import sys
import getopt
import os
import pickle
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.porter import PorterStemmer


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


ELEMENT_SIZE = 6


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    # This is an empty method
    # Pls implement your code in below
    # path = "./nltk_data/corpora/reuters/first"
    path = in_dir
    # path = "./nltk_data/corpora/reuters/first"

    dictionary = {}
    stemmer = PorterStemmer()
    postings_lists = {}
    lengthdict = {}

    # Tokenizing and stemming of words in documents
    try:
        with os.scandir(path) as it:
            for entry in it:
                file = open(entry, 'r')
                file_name = int(entry.name)
                lines = file.readlines()
                length = 0
                for line in lines:
                    length += len(line.split())
                    tokens = [word_tokenize(t) for t in sent_tokenize(line)]
                    if len(tokens) != 0:
                        for t in tokens[0]:
                            stemmed = stemmer.stem(t).lower()

                            # Add tokens to temporary postings list
                            if stemmed in dictionary:
                                # print(list(list(zip(*postings_lists[stemmed]))[0]))
                                if file_name in list(list(zip(*postings_lists[stemmed]))[0]):
                                    postings_lists[stemmed][list(list(zip(*postings_lists[stemmed]))[0]).index(file_name)][1] += 1
                                else:
                                    postings_lists[stemmed].append([file_name, 1])
                            elif stemmed not in dictionary:
                                dictionary[stemmed] = 0
                                postings_lists[stemmed] = [[file_name, 1]]
                lengthdict[file_name] = length
    # Handles errors if we can't find the file.
    except IOError:
        print("No such file in path:", path)

    # This becomes the Dictionary file
    term_doc_occ = {}
    for k in sorted(postings_lists.keys()):
        sorted_docs = sorted(postings_lists[k])
        postings_lists[k] = sorted(postings_lists[k])
        tups = []
        for doc in sorted_docs:
            tups.append([doc[0], 0])
        term_doc_occ[k] = tups

    # Building the output file postings.txt
    postings_output = []
    current_pos = 0
    for k in postings_lists:
        # How many occurrences files with word, and offset to word in postings
        term_doc_occ[k] = (len(term_doc_occ[k]), current_pos)
        posting_str = ""
        postings = postings_lists[k]
        for i in postings:
            str_i = str(i)
            str_i = str(i[0]) + "," + str(i[1]) + " "
            posting_str += str_i
            current_pos += len(str_i)
            # Add skip pointers if the number of documents are more than 3
        postings_output.append(posting_str + "\n")
        current_pos += 1

    # Write everything fo files.
    postings_file = open(out_postings, "w+")
    postings_file.writelines(postings_output)
    with open(out_dict, "wb") as handle:
        pickle.dump(term_doc_occ, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open ("lengthdict", "wb") as handle:
        pickle.dump(lengthdict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print("indexing done...")


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i':  # input directory
        input_directory = a
    elif o == '-d':  # dictionary file
        output_file_dictionary = a
    elif o == '-p':  # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
