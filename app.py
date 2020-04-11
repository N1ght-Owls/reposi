import requests
import flask
from flask import Flask, redirect, url_for
#import redis
import os
from flask_dance.contrib.github import make_github_blueprint, github
#db_ip = os.environ['DBIP']
#db_conn = redis.Redis(host=db_ip, port=6379, db=0)

app = flask.Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET")
blueprint = make_github_blueprint(
    client_id=os.environ.get("REPOSI_GITHUB_CLIENT"),
    client_secret=os.environ.get("REPOSI_GITHUB_SECRET"),
)
app.register_blueprint(blueprint, url_prefix="/login")


@app.route("/")
def signup():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    assert resp.ok
    return "You have successfully logged in as @{login} on GitHub".format(login=resp.json()["login"])


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
