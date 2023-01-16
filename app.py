from flask import Flask, render_template, request
from search_engine import calc_term_frequency

app = Flask(__name__)

@app.route("/")
def index():
    global tf_db
    tf_db = calc_term_frequency("cran_doc_collection")
    return render_template("index.html",  tf_db = tf_db)

@app.route('/search', methods = ["GET", "POST"])
def search():
    query = request.args.get("query")
    return render_template('index.html', query = query, tf_db = tf_db)

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD']=True
    app.config['DEBUG'] = True
    app.config['SERVER_NAME'] = "127.0.0.1:5000"
    app.run()