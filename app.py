from flask import Flask, render_template, request
import search_engine

app = Flask(__name__)


# Index
@app.route("/")
def index():
    search_engine.update_database()
    return render_template("index.html")


# Results page
@app.route('/search', methods=["GET", "POST"])
def search():
    global query
    global q_res_bool
    global q_res_tf_idf
    global boolPreview
    global tfIdfPreview

    query = request.args.get("query")
    resEnd = 5
    resStart = 0
    q_res_bool, boolPreview = search_engine.search_bool(query)
    q_res_tf_idf, tfIdfPreview = search_engine.search_tf_idf(query)

    return render_template("index.html", query=query, q_res_bool=q_res_bool,
                           q_res_tf_idf=q_res_tf_idf,
                           tfIdfPreview=tfIdfPreview,
                           boolPreview=boolPreview,
                           resStart=resStart,
                           resEnd=resEnd)


@app.route('/updateresults', methods=["GET", "POST"])
def updateresults():
    resultPage = int(request.args.get("pageNum")) + 1
    resEnd = resultPage * 5
    resStart = resEnd - 4
    print("results updated!")

    return render_template("index.html", query=query, q_res_bool=q_res_bool,
                           q_res_tf_idf=q_res_tf_idf,
                           tfIdfPreview=tfIdfPreview,
                           boolPreview=boolPreview,
                           resStart=resStart,
                           resEnd=resEnd)


# Document page
@app.route('/docs/<doc>', methods=['GET', 'POST'])
def view_document(doc):
    print("route received")
    with open(f"docs/{doc}") as f:
        document = f.read()
    return render_template("result.html", document = document, title = doc)


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['DEBUG'] = True
    app.config['SERVER_NAME'] = "127.0.0.1:5000"
    app.run()
