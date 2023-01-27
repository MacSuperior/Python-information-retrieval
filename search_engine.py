from os import listdir
import csv
import spacy
import math
nlp = spacy.load('en_core_web_sm')
stopwords = nlp.Defaults.stop_words


#Lemmatizes a string
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

def remove_stopwords(query):
    Nquery = []
    for term in query.split():
        if term not in stopwords:
            Nquery.append(term)
    return " ".join(Nquery)
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

#Performs a boolean AND query and ranks by pagerank
def search_bool(query,incidenceMatrix="database/term_incidence.csv", pagerankScores = "database/pagerank_scores.txt"):
    vectorList = []
    relDocs = []
    result = {}
    query = remove_stopwords(query)
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
    return result

#calculate tf-idf matrix
def calc_tf_idf_matrix():

    #list all unique terms // total term frequency
    termsFreqs = {}

    for file in listdir("database"):
        if file.startswith("lemmatized"):
            with open(f"database/{file}", "r") as f:
                content = f.read()
                for word in content.split():
                    word = word.casefold()
                    if word in termsFreqs:
                        termsFreqs[word] += 1
                    else:
                        termsFreqs.update({word:1})

    #document frequency
    docFreqs = {}
    calc_term_frequency()
    for word in termsFreqs:
        for doc, docContent in tf_db.items():
            if word in docContent:
                if word in docFreqs:
                    docFreqs[word] += 1
                else:
                    docFreqs.update({word:1})
            else:
                pass

    #inverse document frequency
    N = len(listdir("doc_collection"))
    for word, freq in docFreqs.items():
        docFreqs[word] = math.log2(N/freq)

    #term weights
    tf_idf_db = {}
    for term, freq in termsFreqs.items():
        tf_idf_db.update({term:docFreqs[term] * freq})
    
    global twMatrix
    twMatrix = {}
    for doc, content in tf_db.items():
        twMatrix.update({doc:{}})
        for term in content:
            twMatrix[doc].update({term:tf_idf_db[term]})
    return

#Performs a tf-idf query and ranks by cosine similarity
def search_tf_idf(query):
    query = remove_stopwords(query)
    query = lemmatize(query).split()  

    dotProd = 0
    qLen = math.sqrt(len(query))
    cosSimMatrix = {}
    for doc, content in twMatrix.items():
        for x in query:
            if x not in content:
                pass
            else:
                tws = 0
                for term, tw in content.items():
                    tws += math.pow(tw, 2)
                    if term in query:
                        dotProd += tw

                dLen = math.sqrt(tws)
                cosSim = dotProd / qLen * dLen
                cosSimMatrix.update({doc:cosSim})

                cosSimMatrix = {key: val for key, val in sorted(cosSimMatrix.items(), key = lambda ele: ele[1], reverse = True)}
    return cosSimMatrix

#Initializes/Updates database, runs on startup
def update_database():
    lemmatize_docs()
    calc_term_frequency()
    calc_indice_matrix() #depends on $tf_db
    calc_pageranks()
    calc_tf_idf_matrix()
    calc_tf_idf2()
    print("database updated")

#calculates tf-idf model (other version of calc_tf_idf_matrix)
def calc_tf_idf2(doc_folder="database"):
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

#search relevant documents with tf-idf (other version of search_tf_idf)
def search_tf_idf2(query):
    global relDocs
    relDocs = {}
    query = remove_stopwords(query)
    query = lemmatize(query)
    query = query.split()

    #filter relevant documents
    calc_tf_idf_matrix()
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

update_database()
print(search_bool("what is aerodynamic"))
search_tf_idf2("what is aerodynamic")
print(search_tf_idf("what is aerodynamic"))