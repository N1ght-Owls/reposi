from werkzeug.wrappers import Request
from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import os
import requests
import random
from flask_dance.contrib.github import make_github_blueprint, github
import flask
from os import path

app = Flask(__name__,  template_folder="templates", static_folder='static')

# Various environmental variables
app.secret_key = os.environ.get("FLASK_SECRET")
app.config["GITHUB_OAUTH_CLIENT_ID"] = os.environ.get(
    "REPOSI_GITHUB_CLIENT_ID")
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.environ.get(
    "REPOSI_GITHUB_SECRET")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# Github blueprint
github_bp = make_github_blueprint()
app.register_blueprint(github_bp, url_prefix="/login")

# Database model & connection
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    git_hash = db.Column(db.String(80), unique=True, nullable=False)
    git_type = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


if path.exists("db.sqlite") == True:
    print("Database exists")
else:
    print("Creating database")
    db.create_all()

# Routing and repository parsing for github
@app.route("/signup")
def signup():

    resp = github.get("/user")
    if not github.authorized:
        return redirect(url_for("github.login"))
    print(resp)
    assert resp.ok
    user = User.query.filter_by(
        username=resp.json()['login'].lower(), git_type="github").first()
    if user:
        username = resp.json()['login']
        git_hash = user.git_hash
    else:
        user = User(username=resp.json()['login'].lower(),
                    git_hash=str(random.getrandbits(128)),
                    git_type="github")
        db.session.add(user)
        db.session.commit()
        username = resp.json()['login']
        git_hash = user.git_hash
    return redirect(f"{os.environ.get('FLASK_HOST')}/docs?username={username}&token={git_hash}")


def parseGithubRepos(repos):
    parsedRepos = []
    for repo in repos:
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
        if parsedRepo['description'] == None:
            parsedRepo['description'] = "No description provided"
        parsedRepos.append(parsedRepo)
    parsedRepos.sort(key=lambda repo: repo["stars"], reverse=True)
    return parsedRepos


def getGitlabRepoLanguage(repo):
    resp = requests.get(
        f"https://gitlab.com/api/v4/projects/{repo['id']}/languages").json()
    return next(iter(resp))


def parseGitlabRepos(repos):
    parsedRepos = []
    for repo in repos:
        parsedRepo = {}
        parsedRepo['name'] = repo['name']
        if repo['description'] == None:
            parsedRepo['description'] = "No description provided"
        else:
            parsedRepo['description'] = repo['description']
        try:
            parsedRepo['issues'] = repo['open_issues_count']
        except:
            parsedRepo['issues'] = 0
        parsedRepo['owner'] = repo['namespace']['name']
        parsedRepo['stars'] = repo['star_count']
        parsedRepo['forks'] = repo['forks_count']
        parsedRepo['url'] = repo['web_url']
        try:
            parsedRepo['size'] = repo['statistics']['repository_size'],
        except:
            parsedRepo['size'] = None
        parsedRepo['language'] = getGitlabRepoLanguage(repo)
        parsedRepos.append(parsedRepo)
    return parsedRepos


@app.route("/widget/<username>")
def thing(username):
    token = request.args.get('token')
    db.session.commit()
    user = User.query.filter_by(
        username=username.lower(), git_type="github").first()
    resp = {}
    if user == None:
        return "User not found"
    else:
        if user.git_hash != token:
            return "You do not have the correct api token"
        resp = requests.get(
            f"https://api.github.com/users/{username}/repos").json()
    if type(resp) is dict:
        return f'ERROR: {resp["message"]}'

    return flask.render_template('widget.html', repos=parseGithubRepos(resp))


@app.route("/gitlab/widget/<username>")
def gitlabThing(username):
    # token = request.args.get('token')
    # db.session.commit()
    # user = User.query.filter_by(
    #     username=username.lower(), git_type="gitlab").first()
    # resp = {}
    # if user == None:
    #     return "User not found"
    # else:
    # if user.git_hash != token:
    #     return "You do not have the correct api token"
    resp = requests.get(
        f"https://gitlab.com/api/v4/users/{username}/projects").json()
    print(resp)
    return flask.render_template('widget.html', repos=parseGitlabRepos(resp))


@app.route("/")
def serveMain():
    return flask.render_template('index.html')


@app.route("/docs")
def docs():
    return flask.render_template('docs.html', username=request.args.get('username'), token=request.args.get("token"), hostname=os.environ.get('FLASK_HOST'))


if __name__ == '__main__':
    app.run(debug=True)
