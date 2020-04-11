import requests
import flask
import redis
import os
app = flask.Flask(__name__)

db_ip = os.environ['DBIP']
db_conn = redis.Redis(host=db_ip, port=6379, db=0)

def parseRepos(repo):
    parsedRepos = []
    for repo in repo:
        parsedRepo = {
            'name': repo['name'],
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
