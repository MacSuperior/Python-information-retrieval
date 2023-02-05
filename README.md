# Information Retrieval Using Python

Welcome! This Flask app is a small scale information retrieval system using Python and html combined with jinja2.

## Functionality

The system searches a collection of plain text documents in the `docs` folder.
It will retrieve them using two models:

## How to use

The system searches a collection of documents. It comes preloaded with 200 documents, on the topic of aeronautica.
You can provide extra documents yourself, as long as these are plain text.
To start searching, open your command line interface, navigate to the project folder and run `flask run`.

### Example queries

* Engineer
* What is a wing?
* Lift on aeroplanes

### Boolean + PageRank model

* queries terms are treated as a boolean AND query.
* Results are ordered by PageRank values.

### Tf-idf model

* Queries and documents are treated as vectors.
* Results are ordered by cosine similarity.

### Possible future extensions on the system

> These features are not implemented in the current system

* the user can indicate a minimum recommendation threshold (e.g., 0.6 or a level in the scale, i.e., high, medium, or low). Only the documents with a similarity equal to or bigger than the threshold are displayed in the results.
* it can deal with structured documents, such as HTML pages.
* it shows metadata of documents in the ranked output.
* it implements some non-trivial form of personalization.
* visualization of the graph with the PageRank values.
