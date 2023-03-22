This is the README file for A0268807N's and A0269064X submission
Email(s): e1103307@u.nus.edu and e1109901@u.nus.edu

== Python Version ==

I'm (We're) using Python Version <3.8> for this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

In the indexing stage, similarly to assignment 2, we build a postings list indicating in which files we can find all
the words found in the articles, which we then save as a file to memory. In this file we also save the number of terms
in each document, to be used when calculating cosine scores in the search stage. The postings list part is structured
as a text file, where each new line corresponds to a term, and where we then, separated by whitespaces, list document
numbers with their corresponding term frequencies separated by commas. We also save the number of terms in each
document to memory, as a dictionary indexed by the document number.

In the search file, we then use this indexing to calculate similarities between queries and documents by calculating
cosine scores. To calculate the cosine scores, we iterate over the query terms and calculate the query weights based
on the frequencies at the terms that appear in the query. This is called w_tq and the formula can be seen in the code
or found in lecture 7 slides. We then fetch the postings list constructed in the indexing stage and calculate the
document weights w_tq, again based on the formula given in the lecture slides. For each pair of document and term,
we add the product of the query and document weight for each term to an array called Scores, constituting a dot
product in the vector space of embedded queries and documents, measuring how close the query and document are. We
then select the 10 largest, or all if the number of scores is less than 10, cosine scores and write their corresponding
document numbers to the output file, finding the most relevant documents for the search.


== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py
This file contains the code to index all files and terms.

search.py
This file contains the logic to calculate the cosine score and outputs the most relevant documents numbers based on their scores

dictionary.txt
Is a pickle-file containing each term and their offset into the postings list as well as the length of each document.
Term and offset is a dictionary with term as key, and length of documents is a dictionary with document id as key.

postings.txt
Contains the documents that terms appear in, with the frequency of said term in the document.
Format: docID,docFreq, docID,docFreq, ...

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0268807N and A0269064X, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

https://piazza.com/class/la0p9ydharl54v/post/189

https://piazza.com/class/la0p9ydharl54v/post/194