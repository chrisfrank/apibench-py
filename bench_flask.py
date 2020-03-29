import flask
import db

app = flask.Flask(__name__)


db_client = db.SQLClient()
http_client = db.HTTPClient()

@app.route("/posts")
def list_posts():
    posts = db_client.fetch_posts()
    return flask.jsonify({ "data": posts })

@app.route("/users")
def list_users():
    users = http_client.fetch_users()
    return flask.jsonify({ "data": users })

@app.route("/hi")
def hello():
    return flask.jsonify({ "hello": "world" })
