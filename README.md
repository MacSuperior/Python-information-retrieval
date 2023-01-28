# Information Retrieval Using Python

> This repo is currently a work in progress, the system is not finished

Welcome! This Flask app is a small scale information retrieval system using Python and html combined with jinja2.

## Functionality

The system searches a collection of N plain text documents in the doc_collection folder.
It will retrieve them using two models:

### Boolean + PageRank model

* queries terms are treated as a boolean AND query.
* Results are ordered by PageRank values.

### Tf-idf model

* Queries and documents are treated as vectors.
* Results are ordered by cosine similarity.

### Possible future extensions on the system

> These features are not implemented in the current system

* it has a 'next' button for showing  more results.
* the user can indicate a minimum recommendation threshold (e.g., 0.6 or a level in the scale, i.e., high, medium, or low). Only the documents with a similarity equal to or bigger than the threshold are displayed in the results.
* it can deal with structured documents, such as HTML pages.
* it shows metadata of documents in the ranked output.
* it implements some non-trivial form of personalization.
* visualization of the graph with the PageRank values.
