#!/usr/bin/python3
import math
import sys
import getopt
import os
import pickle
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    # This is an empty method
    # Pls implement your code in below
    path = in_dir

    dictionary = {}
    stemmer = PorterStemmer()
    postings_lists = {}
    lengthdict = {}

    try:
        with os.scandir(path) as it:
            for entry in it:
                file = open(entry, 'r')
                file_name = int(entry.name)
                text = file.read()
                terms = []

                # Tokenize the text and iterate over them
                w_text = word_tokenize(text)
                if len(w_text) != 0:
                    for t in w_text:
                        # Perform stemming on each token
                        stemmed = stemmer.stem(t).lower()
                        terms.append(stemmed)

                        # Add tokens to temporary postings list dictionary
                        # postings_lists[key] contains lists of document id's followed by frequency.
                        if stemmed in dictionary:
                            if file_name in list(list(zip(*postings_lists[stemmed]))[0]):
                                postings_lists[stemmed][list(list(zip(*postings_lists[stemmed]))[0]).index(file_name)][1] += 1
                            else:
                                postings_lists[stemmed].append([file_name, 1])
                        elif stemmed not in dictionary:
                            dictionary[stemmed] = 0
                            postings_lists[stemmed] = [[file_name, 1]]

                # Calculate document lengths. sqrt(w_1^2 + w_2^2 + ... + w_n^2)
                terms_set = set(terms)
                sq_len = 0
                for t in terms_set:
                    c = terms.count(t)
                    sq_len += ((1 + math.log(c, 10))**2)
                lengthdict[file_name] = math.sqrt(sq_len)

    # Handles errors if we can't find the file.
    except IOError:
        print("No such file in path:", path)

    # Create dictionary of all terms and the offset in postings for them, this initializes the offset to 0 for every term
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
    # and updating the offset in the term_doc_occ dictionary
    postings_output = []
    current_pos = 0
    for k in postings_lists:
        # How many files that contains the word, and offset to word in postings
        term_doc_occ[k] = (len(term_doc_occ[k]), current_pos)
        posting_str = ""
        postings = postings_lists[k]
        for i in postings:
            str_i = str(i[0]) + "," + str(i[1]) + " "
            posting_str += str_i
            current_pos += len(str_i)
        postings_output.append(posting_str + "\n")
        current_pos += 1

    # Write everything to files.
    postings_file = open(out_postings, "w+")
    postings_file.writelines(postings_output)
    with open(out_dict, "wb") as handle:
        pickle.dump(term_doc_occ, handle, protocol=pickle.HIGHEST_PROTOCOL)
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
