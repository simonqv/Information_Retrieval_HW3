#!/usr/bin/python3
import math

import nltk
import sys
import getopt
import pickle

from nltk import PorterStemmer

stemmer = PorterStemmer()


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def searching(dictionary, postings, query, document_lengths, collection_size):
    scores = cosine_score(dictionary, postings, query, document_lengths, collection_size)
    # Two cases. More than 10 docs or less than 10 docs
    sorted_dict = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    if len(scores) < 10:
        largest_elements = [key for key, value in sorted_dict[:len(scores)]]
    else:
        largest_elements = [key for key, value in sorted_dict[:10]]

    return largest_elements


def find_docs(token, dictionary, postings):
    """
    Help function to index into the postings file.
    """
    nr_docs, offset = dictionary[token]
    postings.seek(offset)
    return postings.readline()


def cosine_score(dictionary, postings, query, document_lengths, collection_size):
    scores = {}
    q_terms = query
    doc_weights = []
    for term in q_terms:
        docs = find_docs(term, dictionary, postings).split()
        df = document_freq(term, dictionary, postings)
        print("COLL: ", collection_size)
        print("DF:   ", df)
        wtq = math.log(collection_size / df, 10)
        print("WTQ:  ", wtq)
        doc_weights.append(wtq)
        for pair in docs:
            pair_elems = pair.split(",")
            doc = int(pair_elems[0])
            D = document_lengths[doc]
            tf = int(pair_elems[1])#  / D  # DELA MED # TERMS IN DOC
            if doc not in scores:
                scores[doc] = 0

            scores[doc] += tf_idf(tf, wtq)
        sum_squares = 0
        for w in doc_weights:

            sum_squares += w ** 2
        length = math.sqrt(sum_squares)
        for doc in scores:
            scores[doc] = scores[doc] / length

    return scores


def tf_idf(tf, wtq):
    """
    Calculate the tf-idf
    """
    print(tf, wtq)
    print(math.log(tf, 10))
    return (1 + math.log(tf, 10)) * wtq if (tf > 0) else 0


def document_freq(term, dictionary, postings):
    return len(find_docs(term, dictionary, postings).split())


def collection_size_calc(dictionary, postings):
    all_docs = set()
    try:
        for key in dictionary:
            row = find_docs(key, dictionary, postings)
            for pair in row.split():
                x = int(pair.split(",")[0])
                all_docs.add(x)
    except IndexError:
        pass
    return len(all_docs)


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    dictionary = pickle.load(open(dict_file, "rb"))
    postings = open(postings_file, "r+")
    queries = open(queries_file, "r+")
    document_lengths = pickle.load(open("lengthdict", "rb"))
    collection_size = collection_size_calc(dictionary, postings)
    output = []

    # For each query, evaluate
    for query in queries.readlines():
        tokens = nltk.word_tokenize(query)
        output.append(searching(dictionary, postings, tokens, document_lengths, collection_size))

    # Create the output and write to file
    out_file = open(results_file, "w+")
    print("out_file: ", output)
    for line in output:
        out_str = ""
        for elem in line:
            out_str = out_str + str(elem) + " "
        out_file.writelines(out_str.rstrip() + "\n")


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
