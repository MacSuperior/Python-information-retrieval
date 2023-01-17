from flask import Flask, render_template, request
from search_engine import calc_term_frequency, results, create_csv

app = Flask(__name__)

tf_db = calc_term_frequency()

#index
@app.route("/")
def index():
    return render_template("index.html",  tf_db = tf_db)

#after searching
@app.route('/search', methods = ["GET", "POST"])
def search():
    query = request.args.get("query")
    print("query:", query)
    q_res = results(query)
    print("q_res:", q_res)
    return render_template('index.html', query = query, q_res = q_res)

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD']=True
    app.config['DEBUG'] = True
    app.config['SERVER_NAME'] = "127.0.0.1:5000"
    app.run()