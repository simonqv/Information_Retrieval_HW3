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

    dictionary = {}
    stemmer = PorterStemmer()
    postings_lists = {}

    # Tokenizing and stemming of words in documents
    try:
        with os.scandir(path) as it:
            for entry in it:
                file = open(entry, 'r')
                file_name = int(entry.name)
                lines = file.readlines()
                for line in lines:
                    tokens = [word_tokenize(t) for t in sent_tokenize(line)]
                    if len(tokens) != 0:
                        for t in tokens[0]:
                            stemmed = stemmer.stem(t).lower()

                            # Add tokens to temporary postings list
                            if stemmed in dictionary:
                                postings_lists[stemmed].append(file_name)
                            elif stemmed not in dictionary:
                                dictionary[stemmed] = 0
                                postings_lists[stemmed] = [file_name]
    # Handles errors if we can't find the file.
    except IOError:
        print("No such file in path:", path)

    # This becomes the Dictionary file
    term_doc_occ = {}
    for k in sorted(postings_lists.keys()):
        sorted_docs = sorted(list(set([t for t in postings_lists[k]])))
        tups = []
        for doc in sorted_docs:
            tups.append([doc, 0])
        term_doc_occ[k] = tups

    # Finding unique documents for each key
    for k in postings_lists:
        postings_lists[k] = sorted(set(postings_lists[k]))

    # Building the output file postings.txt
    postings_output = []
    current_pos = 0
    for k in postings_lists:
        # How many occurrences files with word, and offset to word in postings
        term_doc_occ[k] = (len(term_doc_occ[k]), current_pos)
        posting_str = ""
        postings = postings_lists[k]
        step_size = math.floor(math.sqrt(len(postings)))    # Finding a length for skip pointers as described during lecture
        steps = [i for i in range(0, len(postings), math.floor(math.sqrt(len(postings))))]
        counter = 0
        for index, i in enumerate(postings):
            str_i = str(i)
            # Padding the strings with white spaces
            while len(str_i) < ELEMENT_SIZE:
                str_i = " " + str_i
            posting_str += str_i
            current_pos += ELEMENT_SIZE
            # Add skip pointers if the number of documents are more than 3
            if len(postings) > 3:
                if steps[counter] == index and steps[-1] != index:
                    jump_size = "@" + str((step_size - 1) * ELEMENT_SIZE)
                    # Padding the strings with white spaces
                    while len(jump_size) < ELEMENT_SIZE:
                        jump_size = " " + jump_size
                    posting_str += jump_size
                    counter += 1
                    current_pos += ELEMENT_SIZE
        postings_output.append(posting_str + "\n")
        current_pos += 1

    # Write everything fo files.
    postings_file = open(out_postings, "w+")
    postings_file.writelines(postings_output)
    with open(out_dict, "wb") as handle:
        pickle.dump(term_doc_occ, handle, protocol=pickle.HIGHEST_PROTOCOL)

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
