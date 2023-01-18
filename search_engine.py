from os import listdir
import csv

#create a tf_indice for every document in the given folder.
def calc_term_frequency(folder_path="cran_doc_collection"):
    global tf_db
    tf_db = {}
    folder_content = listdir(folder_path)
    for file in folder_content:
        tf_db.update({file:{}})
        with open(f"{folder_path}/{file}", "r") as doc:
            for line in doc:
                for word in line.split():
                    word = word.lower()
                    if word in tf_db[file].keys():
                        tf_db[file][word] += 1
                    else:
                        tf_db[file].update({word:1})
    return tf_db

#performs a boolean AND query and returns all relevant documents
def results(query,incidenceMatrix="csv_files/term_incidence.csv"):
    vectorList = []
    relDocs = []
    query = query.split()
    print("query inside func", query)
    with open (incidenceMatrix, "r") as f:
        matrix = csv.reader(f)
        matrix = list(matrix)
        for row in matrix[1:]:
            if row[0] in query:
                rowVector = [int(a) for a in row[1:]] #get all indices from rurrent row
                vectorList.append(rowVector)
    for ind, colVector in enumerate(zip(*vectorList)):
        if 0 in colVector:
            pass
        else:
            relDocs.append(matrix[0][ind + 1])
    return relDocs    

def create_csv(file_location="csv_files/term_incidence.csv"):
    calc_term_frequency() #necessary to get $tf_db
    headers = [""]
    terms = []

    #create headers list consisting of all document names
    for doc in tf_db.keys():
        headers.append(doc)

    #terms list
    for k, v in tf_db.items():
            v = v.keys()
            for term in v:
                terms.append([term])

    #create word + an indice for each document 
    for i, word in enumerate(terms):
        word = terms[i][0] #word needs to be type string to check its' presence   
        for docName in headers[1:]:
            if word in tf_db[docName].keys():
                terms[i].append(1)
            else:
                terms[i].append(0)

    #write to $file_location
    with open(file_location, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(terms) 
    return

#TODO write func that reads pagerank file and calculates pagerank for every file
#TODO optional: create random pagerank file
def calc_pagerank(pagerank_file = "pagerank.txt", damping=0.9):
    pagerank_scores = {}
    pagerank_data = {}
    with open(pagerank_file, "r") as f:
        for row in f:
            row = row.split()
            pagerank_scores.update({row[0]:1})
            if len(row) == 1:
                pagerank_data.update({row[0]:None})
            else:
                pagerank_data.update({row[0]:row[1:]})

        for document in pagerank_scores:
            #bereken pagerank voor document en voeg toe aan pagerank scores
            pass
                    
    return pagerank_scores