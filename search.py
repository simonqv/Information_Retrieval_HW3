#!/usr/bin/python3
import nltk
import sys
import getopt
import pickle

from nltk import PorterStemmer

stemmer = PorterStemmer()

ELEMENT_SIZE = 6


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def shunting_yard(tokens):
    """
    Performs shunting yard algorithm to create postfix notation.
    """
    output = []
    operators = []
    for token in tokens:
        if token not in ['(', ')', 'AND', 'OR', 'NOT']:
            token = stemmer.stem(token).lower()
        if token == '(':
            operators.append(token)
        elif token == ')':
            while operators[-1] != '(':
                output.append(operators.pop())
            operators.pop()
        elif token == 'AND':
            while operators and operators[-1] == 'NOT':
                output.append(operators.pop())
            operators.append(token)
        elif token == 'OR':
            while operators and operators[-1] != '(':
                output.append(operators.pop())
            operators.append(token)
        elif token == 'NOT':
            operators.append(token)
        else:
            output.append(token)
    while operators:
        output.append(operators.pop())
    return output


def OR(stack):
    # union of a and b
    a = stack.pop()
    b = stack.pop()
    output = ""
    # Pointers for lists a and b
    pa, pb = 0, 0
    # Iterate over lists a and b
    while pa <= len(a) and pb <= len(b):
        block_a = a[pa: pa + ELEMENT_SIZE]
        block_b = b[pb: pb + ELEMENT_SIZE]
        if block_a.strip().startswith("@"):
            pa += ELEMENT_SIZE
            continue
        if block_b.strip().startswith("@"):
            pb += ELEMENT_SIZE
            continue

        if pa == len(a):
            output += block_b
            pb += ELEMENT_SIZE
            continue
        if pb == len(b):
            output += block_a
            pa += ELEMENT_SIZE
            continue

        block_a_int = int(block_a.strip())
        block_b_int = int(block_b.strip())

        # Increment pointer depending on which on points at the smaller number and add elements we've found to output
        if block_a_int < block_b_int:
            output += block_a
            pa += ELEMENT_SIZE
        elif block_a_int > block_b_int:
            output += block_b
            pb += ELEMENT_SIZE
        else:
            output += block_a
            pa += ELEMENT_SIZE
            pb += ELEMENT_SIZE

    stack.append(output)


def AND(stack):
    # intersection of a and b
    a = stack.pop()
    b = stack.pop()
    output = ""
    # Pointers for lists a and b
    pa, pb = 0, 0
    # Iterate over lists a and b
    while pa < len(a) and pb < len(b):
        block_a = a[pa: pa + ELEMENT_SIZE]
        block_b = b[pb: pb + ELEMENT_SIZE]

        # Check if we want to use skip pointer
        if block_a.strip().startswith("@"):
            a_len = int(block_a.split("@")[1])
            a_next = int(a[pa + ELEMENT_SIZE + a_len: pa + 2 * ELEMENT_SIZE + a_len])
            b_int = int(block_b.strip())

            # Use skip pointer
            if a_next <= b_int:
                pa += a_len + ELEMENT_SIZE
                block_a = a[pa: pa + ELEMENT_SIZE]
            # Don't use skip pointer
            else:
                pa += ELEMENT_SIZE
                block_a = a[pa: pa + ELEMENT_SIZE]

        # Check if we want to use skip pointer
        if block_b.strip().startswith("@"):
            b_len = int(block_b.split("@")[1])
            b_next = int(b[pb + ELEMENT_SIZE + b_len: pb + 2 * ELEMENT_SIZE + b_len])
            a_int = int(block_a.strip())

            # Use skip pointer
            if b_next <= a_int:
                pb += b_len + ELEMENT_SIZE
                block_b = b[pb: pb + ELEMENT_SIZE]
            # Don't use skip pointer
            else:
                pb += ELEMENT_SIZE
                block_b = b[pb: pb + ELEMENT_SIZE]

        block_a_int = int(block_a.strip())
        block_b_int = int(block_b.strip())

        # Increment pointer depending on which on points at the smaller number
        if block_a_int < block_b_int:
            pa += ELEMENT_SIZE
        elif block_a_int > block_b_int:
            pb += ELEMENT_SIZE
        else:
            # We found a match
            output += block_a
            pa += ELEMENT_SIZE
    stack.append(output)


def NOT(stack, all_docs):
    # Inverts the list
    a = stack.pop()
    to_exclude = [int(i) for i in a.split() if not i.startswith("@")]
    temp = [t for t in all_docs if t not in to_exclude]
    output = ""
    for t in temp:
        t = str(t)
        while len(t) < ELEMENT_SIZE:
            t = " " + t
        output += t
    stack.append(output)


def evaluate(shunting_yard_list, dictionary, postings):
    """
    Main function for evaluating the query.
    """
    stack = []
    all_docs = set()
    only_one_token = True
    try:
        for key in dictionary:
            row = find_docs(key, dictionary, postings)
            [all_docs.add(int(x)) for x in row.split() if not x.startswith("@")]

        for token in shunting_yard_list:
            if token == 'OR':
                OR(stack)
                only_one_token = False
            elif token == 'AND':
                AND(stack)
                only_one_token = False
            elif token == 'NOT':
                NOT(stack, all_docs)
                only_one_token = False
            else:
                temp = find_docs(token, dictionary, postings)
                stack.append(temp.rstrip())
    except IndexError:
        pass

    # Format output
    try:
        output = []
        temp_output = stack.pop().split()
        # Special case if the query only consist of one word/token and no operators, remove skip pointers.
        if only_one_token:
            for o in temp_output:
                if not o.startswith("@"):
                    output.append(o)

    except:
        output = []
    return output


def find_docs(token, dictonary, postings):
    """
    Help function to index into the postings file.
    """
    nr_docs, offset = dictonary[token]
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
    output = []

    # For each query, evaluate
    for query in queries.readlines():
        tokens = nltk.word_tokenize(query)
        output.append(evaluate(shunting_yard(tokens), dictionary, postings))

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
