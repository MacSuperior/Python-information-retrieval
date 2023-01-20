from flask import Flask, render_template, request
import search_engine

app = Flask(__name__)

tf_db = search_engine.calc_term_frequency()

#index
@app.route("/")
def index():
    search_engine.update_database()
    return render_template("index.html",  tf_db = tf_db)

#after searching
@app.route('/search', methods = ["GET", "POST"])
def search():
    query = request.args.get("query")
    q_res = search_engine.search_bool(query)
    return render_template('index.html', query = query, q_res = q_res)

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD']=True
    app.config['DEBUG'] = True
    app.config['SERVER_NAME'] = "127.0.0.1:5000"
    app.run()