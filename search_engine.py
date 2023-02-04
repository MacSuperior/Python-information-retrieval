from os import listdir
import csv
import spacy
import math
import random
nlp = spacy.load('en_core_web_sm')
stopwords = nlp.Defaults.stop_words


# Lemmatizes a string
def lemmatize(input):
    query = nlp(input)
    Lemquery = " ".join([token.lemma_ for token in query])
    return Lemquery


# Lemmatize documents for use in all other functions
def lemmatize_docs(doc_folder="docs"):
    for file in listdir(doc_folder):
        with open(f"{doc_folder}/{file}", "r") as f:
            content = " ".join(f.read().splitlines())
            lemContent = lemmatize(content)
            with open(f"database/lemmatized_{file}", "w") as lemFile:
                lemFile.write(lemContent)
    return


def remove_stopwords(query):
    Nquery = []
    for term in query.split():
        if term not in stopwords:
            Nquery.append(term)
    return " ".join(Nquery)


# Create a tf_indice for every document in the given folder.
def calc_term_frequency(folder="database"):
    global tf_db
    tf_db = dict()

    for file in listdir(folder):
        if file.startswith("lemmatized_doc"):
            tf_db.update({file: dict()})
            with open(f"{folder}/{file}", "r") as doc:
                for line in doc:
                    for word in line.split():
                        word = word.lower()
                        if word in tf_db[file].keys():
                            tf_db[file][word] += 1
                        else:
                            tf_db[file].update({word: 1})
        else:
            pass
    return


def calc_incidence_matrix(fileLocation="database/term_incidence.csv"):
    headers = [""]
    terms = []

    # Create headers list of all document names
    for doc in tf_db.keys():
        headers.append(doc)

    # Create terms list
    for k, v in tf_db.items():
        v = v.keys()
        for term in v:
            terms.append([term])

    # Create word + an indice for each document
    for i, word in enumerate(terms):
        word = terms[i][0]  # Word needs to be string to check its presence
        for docName in headers[1:]:
            if word in tf_db[docName].keys():
                terms[i].append(1)
            else:
                terms[i].append(0)

    # Write file indice matrix to $file_location
    with open(fileLocation, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(terms)
    return terms


# Calculate pagerank for every file in $pagerankGraph
def calc_pageranks(pagerankGraph="database/pagerank_graph.txt", dmp=0.9, itr=100):
    pagerankScores = dict()
    pagerankData = dict()  # Dict of what files a file links to

    # Store pagerank graph
    with open(pagerankGraph, "r") as f:
        for row in f:
            row = row.split()
            pagerankScores.update({row[0]: 1})  # Set PR for documents
            if len(row) == 1:
                pagerankData.update({row[0]: None})
            else:
                pagerankData.update({row[0]: row[1:]})  # Pagerank graph

    for i in range(itr):
        for docName in pagerankData:
            pagerank = pagerankScores[docName]
            temp = 0

            for val in pagerankData.values():
                if val is None:
                    pass
                else:
                    if type(val) == list:
                        if docName in val:
                            temp += pagerank / len(val)
                    else:
                        pass
                pagerank = (1 - dmp) + dmp * temp
                pagerankScores.update({docName: pagerank})

    write_pagerank(pagerankScores)
    return pagerankScores


# Write file pageranks to file
def write_pagerank(pagerankScores, fileLocation="database/pagerank_scores.txt"):
    with open(fileLocation, "w") as f:
        for k, v, in pagerankScores.items():
            f.write(f"{k} {v}\n")


# load big dataset into list
def create_doc_collection():
    global lg_doc_collection
    lg_doc_collection = []
    with open("database/cran_all_1400.txt") as f:
        content = f.readlines()
        for i, line in enumerate(content):
            if line == ".W\n":
                lg_doc_collection.append([])
                for line in content[i+1:]:
                    if line.startswith(".I") is not True:
                        lg_doc_collection[-1].append(line)
                    else:
                        break
    return


# create pagerank graph for specified document collection
def create_pagerank_graph(fileName="pagerank_graph.txt", docCollection="docs"):
    with open(f"database/{fileName}", "w") as f:
        allFiles = listdir(docCollection)
        for doc in allFiles:
            line = f"{doc} {' '.join(random.choices(allFiles, k=random.randint(1, 6)))}"
            f.write(f"{line}\n")


# Preview relevant document content
def preview_document(query, result):
    preview = dict()
    for doc in result.keys():
        with open(f"docs/{doc}") as f:
            content = f.readlines()
            for i, line in enumerate(content):
                content[i] = line.rstrip().strip()
            for line in content:
                for term in query:
                    if term in line:
                        try:
                            preview.update({doc: f"{' '.join(content[i-3:i+1])}..."})
                        except IndexError:
                            try:
                                preview.update({doc: f"{content[i:i+3]}..."})
                            except IndexError:
                                preview.update({doc: f"{content[i-3:i]}..."})
                        break
    return preview


# Performs a boolean AND query and ranks by pagerank
def search_bool(query, incdnceMatrix="database/term_incidence.csv", prScores="database/pagerank_scores.txt"):
    vectorList = []
    relDocs = []
    result = dict()
    query = remove_stopwords(query)
    query = lemmatize(query).split()

    # Create document incidence vectors
    with open(incdnceMatrix, "r") as f:
        matrix = csv.reader(f)
        matrix = list(matrix)
        for row in matrix[1:]:
            if row[0] in query:
                rowVector = [int(a) for a in row[1:]]  # All indices from current row
                vectorList.append(rowVector)

    for i, colVector in enumerate(zip(*vectorList)):
        if 0 in colVector:
            pass
        else:
            relDocs.append(matrix[0][i + 1])

    # Rank relevant documents
    with open(prScores, "r") as f:
        for row in f:
            row = row.split()
            if f"lemmatized_{row[0]}" in relDocs:
                result.update({row[0]: str(row[1])})
        result = {key: val for key, val in sorted(result.items(), key=lambda ele: ele[1], reverse=True)}
    boolPreview = preview_document(query, result)
    return result, boolPreview


# calculate tf-idf matrix
def calc_tf_idf_matrix():

    # list all unique terms
    calc_term_frequency()
    termsFreqs = set()
    for content in tf_db.values():
        for term in content:
            termsFreqs.add(term)

    # document frequency
    docFreqs = dict()
    for term in termsFreqs:
        for doc, content in tf_db.items():
            if term in content:
                if term in docFreqs:
                    docFreqs[term] += 1
                else:
                    docFreqs.update({term: 1})
            else:
                pass

    # inverse document frequency
    idf_matrix = dict()
    N = len(listdir("docs"))
    for term, freq in docFreqs.items():
        idf = math.log2(N/freq)
        idf_matrix.update({term: idf})

    # tf to term weights
    for doc, content in tf_db.items():
        for term, freq in content.items():
            tf_db[doc][term] *= idf_matrix[term]

    global tw_matrix
    tw_matrix = tf_db
    return tw_matrix


# Performs a tf-idf query and ranks by cosine similarity
def search_tf_idf(query):
    query = remove_stopwords(query)
    query = lemmatize(remove_stopwords(query)).split()
    cosSimMatrix = dict()

    # query vector length
    qLen = math.sqrt(len(query))

    # document vectors
    calc_tf_idf_matrix()
    for doc, content in tw_matrix.items():
        # check if doc contains query terms:
        for x in query:
            if x not in content:
                pass
            else:
                # calc document length
                dotProd = 0
                tws = 0
                for term, tw in content.items():
                    tws += math.pow(tw, 2)
                    if term in query:
                        dotProd += tw

                dLen = math.sqrt(tws)
                cosSim = dotProd / (qLen * dLen)
                cosSimMatrix.update({doc[11:]: str(cosSim)})

        cosSimMatrix = {key: val for key, val in sorted(cosSimMatrix.items(), key=lambda ele: ele[1], reverse=True)}
    tfIdfPreview = preview_document(query, cosSimMatrix)
    return cosSimMatrix, tfIdfPreview


# Initializes/Updates database, runs on startup
def update_database():
    lemmatize_docs()
    calc_term_frequency()
    create_doc_collection()  # load big dataset
    create_pagerank_graph()
    calc_incidence_matrix()  # depends on $tf_db
    calc_pageranks()
    calc_tf_idf_matrix()
    print("database updated")
