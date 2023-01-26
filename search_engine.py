from os import listdir
import csv
import spacy
import math
import random
nlp = spacy.load('en_core_web_sm')

#lemmatize input
def lemmatize(input):
    content = nlp(input)
    lemContent = " ".join([token.lemma_ for token in content])
    return lemContent

#Lemmatize documents for use in all other functions
def lemmatize_docs(doc_folder="doc_collection"):
    for file in listdir(doc_folder):
        with open(f"{doc_folder}/{file}", "r") as f:
            content = " ".join(f.read().splitlines())
            lemContent = lemmatize(content)
            with open(f"database/lemmatized_{file}", "w") as lemFile:
                lemFile.write(lemContent)
    return

#Create a tf_indice for every document in the given folder.
def calc_term_frequency(folder="database"):
    global tf_db
    tf_db = {}
    
    for file in listdir(folder):
        if file.startswith("lemmatized_doc"):
            tf_db.update({file:{}})
            with open(f"{folder}/{file}", "r") as doc:
                for line in doc:
                    for word in line.split():
                        word = word.lower()
                        if word in tf_db[file].keys():
                            tf_db[file][word] += 1
                        else:
                            tf_db[file].update({word:1})
        else:
            pass
    return

def calc_indice_matrix(fileLocation="database/term_incidence.csv"):
    headers = [""]
    terms = []

    #Create headers list of all document names
    for doc in tf_db.keys():
        headers.append(doc)

    #Create terms list
    for k, v in tf_db.items():
            v = v.keys()
            for term in v:
                terms.append([term])

    #Create word + an indice for each document 
    for i, word in enumerate(terms):
        word = terms[i][0] #Word needs to be type string to check its presence   
        for docName in headers[1:]:
            if word in tf_db[docName].keys():
                terms[i].append(1)
            else:
                terms[i].append(0)

    #Write file indice matrix to $file_location
    with open(fileLocation, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(terms) 
    return terms

#Calculate pagerank for every file in $pagerankGraph
def calc_pageranks(pagerankGraph = "database/pagerank_graph.txt", damping = 0.9, iterations = 100):
    pagerankScores = {}
    pagerankData = {} #Dict of what files a file (the dict key) points to

    #Store pagerank graph
    with open(pagerankGraph, "r") as f:
        for row in f:
            row = row.split()
            pagerankScores.update({row[0]:1}) #Set starting pagerank for documents
            if len(row) == 1:
                pagerankData.update({row[0]:None})
            else:
                pagerankData.update({row[0]:row[1:]}) #Pagerank graph

    for i in range(iterations):
        for docName in pagerankData:
            pagerank = pagerankScores[docName]
            temp = 0

            for val in pagerankData.values():
                if val == None:
                    pass
                else:
                    if type(val) == list:
                        if docName in val:
                            temp += pagerank / len(val)
                    else:
                        pass
                pagerank = (1 - damping) + damping * temp
                pagerankScores.update({docName:pagerank})

    create_pagerank_file(pagerankScores)
    return pagerankScores

#Write file pageranks to file
def create_pagerank_file(pagerankScores, fileLocation = "database/pagerank_scores.txt"):
    with open(fileLocation, "w") as f:
        for k, v, in pagerankScores.items():
            f.write(f"{k} {v}\n")

#TODO Optional: create (random) pagerank file
#Performs a boolean AND query and returns all relevant documents
def search_bool(query,incidenceMatrix="database/term_incidence.csv", pagerankScores = "database/pagerank_scores.txt"):
    vectorList = []
    relDocs = []
    result = {}
    query = lemmatize(query).split()

    #Create document incidence vectors
    with open (incidenceMatrix, "r") as f:
        matrix = csv.reader(f)
        matrix = list(matrix)
        for row in matrix[1:]:
            if row[0] in query:
                rowVector = [int(a) for a in row[1:]] #Get all indices from rurrent row
                vectorList.append(rowVector)

    for i, colVector in enumerate(zip(*vectorList)):
        if 0 in colVector:
            pass
        else:
            relDocs.append(matrix[0][i + 1])

    #Rank relevant documents
    with open(pagerankScores, "r") as f:
        for row in f:
            row = row.split()
            if f"lemmatized_{row[0]}" in relDocs:
                result.update({row[0]:row[1]})
        result = {key: val for key, val in sorted(result.items(), key = lambda ele: ele[1], reverse=True)}
        preview = preview_document(query, result)
    return result, preview

def preview_document(query, result):
    print(f"query:{query}")
    print(f"result:{result}")
    preview = {}
    for doc in result.keys():
        with open(f"doc_collection/{doc}") as f:
            content = f.readlines()
            for line in content:
                line = line.rstrip()
                for x in query:
                    if x in line:
                        preview.update({doc:f"...{line}..."})
    return preview

#calculate tf-idf model
def calc_tf_idf(doc_folder="database"):
    #calculate document frequency for all terms
    global df_db
    df_db = {}

    #list all unique terms
    for file in listdir(doc_folder):
        if file.startswith("lemmatized_doc"):
            with open(f"{doc_folder}/{file}", "r") as doc:
                for line in doc:
                    for word in line.split():
                        word = word.lower()
                        df_db.update({word:0})
        else:
            pass

    #count document frequencies
    for term in df_db:
        for file in listdir(doc_folder):
            if file.startswith("lemmatized_doc"):
                with open(f"{doc_folder}/{file}", "r") as doc:
                    if term in doc.read():
                        df_db[term] += 1
            else:
                pass

    #convert into inverse document frequency
    global idf_db
    N = 10    #number of documents
    idf_db = {}
    for term in df_db:
        idf_value = math.log2(N/df_db[term])
        idf_db.update({term:idf_value})

    #create term frequency dictionary
    global tf_db_weights
    tf_db_weights = {}
    for file in listdir(doc_folder):
        if file.startswith("lemmatized_doc"):
            with open(f"{doc_folder}/{file}", "r") as doc:
                for line in doc:
                    for word in line.split():
                        word = word.lower()
                        if word in tf_db_weights:
                            tf_db_weights[word] += 1
                        else:
                            tf_db_weights.update({word:1})
        else:
            pass

    #calculate term weight for all terms
    global term_weight_db
    term_weight_db = {}
    for term in idf_db:
            weight = idf_db[term] * tf_db_weights[term]
            term_weight_db.update({term:weight})

def create_doc_collection(createFiles = False):
    global lg_doc_collection
    lg_doc_collection = []
    with open("database/cran_all_1400.txt") as f:
        content = f.readlines()
        for i, line in enumerate(content):
            if line == ".W\n":
                lg_doc_collection.append([])
                for line in content[i+1:]:
                    if line.startswith(".I") != True:
                        lg_doc_collection[-1].append(line)
                    else:
                        break

    #we dont want 1400 document files when we can search a list, maybe later remove code underneath
    if createFiles == True:
        fileNum = 1
        for doc in lg_doc_collection:
            with open(f"huge_doc_collection/doc{fileNum}.txt", "w") as f:
                f.writelines(doc)
            fileNum += 1
    return

#create pagerank graph for specified document collection
def create_pagerank_graph(fileName = "pagerank_graph", docCollection="doc_collection"):
    with open(f"database/{fileName}.txt", "w") as f:
        allFiles = listdir(docCollection)
        for doc in allFiles:
            line = f"{doc} {' '.join(random.choices(allFiles, k= random.randint(1, 6)))}"
            f.write(f"{line}\n")

def update_database():
    lemmatize_docs()
    calc_term_frequency()
    calc_indice_matrix() #depends on $tf_db
    create_pagerank_graph()
    calc_pageranks()
    print("database updated")
# THIS HAS TO HAPPEN ONLY ONCE, BUT ALSO WHEN DOC_COLLECION IS UPDATED
#1. lemmatize every doc in collection
#2. create term frequency DB
#3. create term incidence csv
#4. create pagerank scores
#5. create pagerank graph
#6. create term frequency csv
#7. create term weight matrix csv

#THIS HAS TO HAPPEN FOR EVERY SEARCH QUERY
#1. lemmatize query
#2. search with boolean boolean model and order by pagerank
#3. search with tf-idf model and order by cosine similarity
#4. show ranked outputs