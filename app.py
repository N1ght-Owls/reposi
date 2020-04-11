import requests
import flask
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import random
from flask_dance.contrib.github import make_github_blueprint, github


app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)

app.secret_key = os.environ.get("FLASK_SECRET")
app.config["GITHUB_OAUTH_CLIENT_ID"] = os.environ.get("REPOSI_GITHUB_CLIENT_ID")
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.environ.get("REPOSI_GITHUB_SECRET")
github_bp = make_github_blueprint()
app.register_blueprint(github_bp, url_prefix="/login")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    github_hash = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

@app.route("/signup")
def signup():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    
    print(resp.json())
    assert resp.ok
    user = User(username= resp.json()['login'], github_hash= str(random.getrandbits(128)))
    db.session.add(user)
    db.session.commit()
    return f"You have successfully logged in as @{resp.json()['login']} on GitHub"


def parseRepos(repo):
    parsedRepos = []
    for repo in repo:
        parsedRepo = {
            'name': repo['full_name'],
            'description': repo['description'],
            'issues': repo['open_issues'],
            'owner': repo['owner']['login'],
            'stars': repo['stargazers_count'],
            'forks': repo['forks_count'],
            'url': repo['html_url'],
            'size': repo['size'],
            'language': repo['language']
        }
        parsedRepos.append(parsedRepo)
    return parsedRepos


@app.route("/widget/<username>")
def thing(username):
    resp = requests.get(
        f"https://api.github.com/users/{username}/repos").json()
    print(resp)
    if type(resp) is dict:
        return f'ERROR: {resp["message"]}'
    
    return flask.render_template('widget.html', repos=parseRepos(resp))


@app.route("/")
def serveMain():
    return flask.render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)