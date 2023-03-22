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
    """
    Gets all scores, sorts them and output the top 10 (or less if less documents exists)
    """
    # Calculates all scores
    scores = cosine_score(dictionary, postings, query, document_lengths, collection_size)

    # Sort the output in descending order with regards to document score,
    # if scores are identical sort with ascending order on document ID.
    # Two cases. More than 10 docs or less than 10 docs
    sorted_dict = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    if len(scores) < 10:
        largest_elements = [key for key, value in sorted_dict[:len(scores)]]
    else:
        largest_elements = [key for key, value in sorted_dict[:10]]

    return largest_elements


def find_docs(token, dictionary, postings):
    """
    Help function to index into the postings file. And fetch the documents and term frequencies.
    """
    try:
        nr_docs, offset = dictionary[token]
        postings.seek(offset)
        line = postings.readline()
        return line
    except:
        return " "


def cosine_score(dictionary, postings, query, document_lengths, collection_size):
    """
    Calculate the cosine_score following the pseudocode from lecture.
    Returns: a dictionary containing the scores for the documents found for the query.
    """
    scores = {}
    query_term_freq = {}

    # Perform stemming on query and count frequency of term in query
    for i in range(len(query)):
        stemmed_q_term = stemmer.stem(query[i]).lower()
        query[i] = stemmed_q_term
        if stemmed_q_term not in query_term_freq:
            query_term_freq[stemmed_q_term] = 0
        query_term_freq[stemmed_q_term] += 1

    # The main loop of the function. Calculates the scores
    for term in set(query):
        if term in dictionary:
            docs = find_docs(term, dictionary, postings).split()
            df = dictionary[term][0]
            idf = math.log(collection_size / df, 10) if (df > 0) else 0
            wtq = (1 + math.log(query_term_freq[term], 10)) * idf if (query_term_freq[term] > 0) else 0

            for pair in docs:
                pair_elems = pair.split(",")
                doc = int(pair_elems[0])
                tf = int(pair_elems[1])
                if doc not in scores:
                    scores[doc] = 0

                wtd = (1 + math.log(tf, 10))
                scores[doc] += wtd * wtq

    # Normalization with the length of documents. Document length is calculated during indexing.
    for doc in scores:
        scores[doc] = scores[doc] / document_lengths[doc]
    return scores


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    # Load all files. Dictionary file contains both the dictionary and the lengths of documents
    with open(dict_file, "rb") as handle:
        dictionary = pickle.load(handle)
        document_lengths = pickle.load(handle)
    postings = open(postings_file, "r+")
    queries = open(queries_file, "r+")
    collection_size = len(document_lengths)
    output = []

    # For each query, evaluate
    for query in queries.readlines():
        tokens = nltk.word_tokenize(query)
        output.append(searching(dictionary, postings, tokens, document_lengths, collection_size))

    # Create the output and write to file
    out_file = open(results_file, "w+")
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
