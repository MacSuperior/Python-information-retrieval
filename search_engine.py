from os import listdir
import csv
import spacy
import math
nlp = spacy.load('en_core_web_sm')

def lemmatize(input):
    query = nlp(input)
    Lemquery = " ".join([token.lemma_ for token in query])
    return Lemquery

#Lemmatize documents for use in all other functions
def lemmatize_docs(doc_folder="doc_collection"):
    for file in listdir(doc_folder):
        with open(f"doc_collection/{file}", "r") as f:
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

    write_pagerank(pagerankScores)
    return pagerankScores

#Write file pageranks to file
def write_pagerank(pagerankScores, fileLocation = "database/pagerank_scores.txt"):
    with open(fileLocation, "w") as f:
        for k, v, in pagerankScores.items():
            f.write(f"{k} {v}\n")

#TODO Optional: create (random) pagerank file
#Performs a boolean AND query and returns all relevant documents
def search_bool(query,incidenceMatrix="database/term_incidence.csv", pagerankScores = "database/pagerank_scores.txt"):
    vectorList = []
    relDocs = []
    result = {}
    query = lemmatize(query)
    query = query.split()

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
    return result

def update_database():
    lemmatize_docs()
    calc_term_frequency()
    calc_indice_matrix() #depends on $tf_db
    calc_pageranks()
    print("database updated")

# THIS HAS TO HAPPEN ONLY ONCE, BUT ALSO WHEN DOC_COLLECION IS UPDATED
#1. lemmatize every doc in collection
#2. create term frequency DB
#3. create term incidence csv
#4 create pagerank scores
#5 create term frequency csv
#6 create term weight matrix csv

#THIS HAS TO HAPPEN FOR EVERY SEARCH QUERY
#1. lemmatize query
#2. search with boolean boolean model and order by pagerank
#3. search with tf-idf model and order by cosine similarity
#4. show ranked outputs

#calculate tf-idf model
def calc_tf_idf(doc_folder="database"):
    #calculate document frequency for all terms
    df_db = {}
    docfreq_db = {}

    #list all unique terms // total term frequency
    for file in listdir("database"):
        if file.startswith("lemmatized"):
            with open(f"database/{file}", "r") as f:
                content = f.read()
                for word in content.split():
                    if word in df_db:
                        df_db[word] += 1
                    else:
                        df_db.update({word:1})
    
    calc_term_frequency()
    #document frequency
    for word in df_db:
        for doc, docContent in tf_db.items():
            if word in docContent:
                if word in docfreq_db:
                    docfreq_db[word] += 1
                else:
                    docfreq_db.update({word:1})

    #inverse document frequency
    N = len(listdir("doc_collection"))
    for word, freq in docfreq_db.items():
        docfreq_db[word] = math.log2(N/freq)
    

    ##previous code below, to remove later
    #convert into inverse document frequency
    global idf_db
    N = 10    #number of documents
    idf_db = {}
    for term in df_db:
        idf_value = math.log2(N/df_db[term])
        idf_db.update({term:idf_value})

    #create term frequency dictionary
    calc_term_frequency()

    #calculate term weight for all terms
    global term_weight_db
    term_weight_db = {}
    for doc in tf_db:
        term_weight_db.update({doc:{}})
        for term in tf_db[doc]:
            weight = idf_db[term] * tf_db[doc][term]
            term_weight_db[doc].update({term:weight})

    #create vector lenghts for all documents
    global vector_lenghts_db
    vector_lenghts_db = {}
    for doc in term_weight_db:
        x = 0
        for term in term_weight_db[doc]:
                x += term_weight_db[doc][term] ** 2
        doc_lenght = math.sqrt(x)
        vector_lenghts_db.update({doc:doc_lenght})

#search relevant documents with tf-idf
def search_tf_idf(query):
    global relDocs
    relDocs = {}
    query = lemmatize(query)
    query = query.split()

    #filter relevant documents
    calc_tf_idf()
    for doc in term_weight_db:
        relDocs.update({doc:{}})
        for query_word in query:
            for key in term_weight_db[doc]:
                if query_word == key:
                    relDocs[doc].update({key:term_weight_db[doc][key]})
                else:
                    pass        

    #calculate vector lenght for query
    global query_vlength
    query_vlength = math.sqrt(len(query))

    #calculate dot product for relevant documents and query
    global dot_product_db
    dot_product_db = {}
    for doc in relDocs:
        score = 0
        if bool(relDocs[doc]) == True:     #docs with no query terms are skipped
            for key in relDocs[doc]:
                product = term_weight_db[doc][key] * 1      #query terms weigh 1
                score += product
            dot_product_db.update({doc:score})
        else:
            pass

    #calculate cosine similarity between query and docs
    global cosine_sim_db
    cosine_sim_db = {}
    for doc in dot_product_db:
        cos_sim = dot_product_db[doc] / (query_vlength * vector_lenghts_db[doc])
        cosine_sim_db.update({doc:cos_sim})

    #write cosine similarity dict to matrix
    global result
    unranked = ([[k, v] for k,v in cosine_sim_db.items()])     #source: stackoverflow.com

    #rank results
    result = sorted(unranked, key=lambda score : score[1], reverse=True)
    print(result)
    

