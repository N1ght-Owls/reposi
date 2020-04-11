import markovify
import requests
import flask
app = flask.Flask(__name__)


@app.route("/widget/<username>")
def thing(username):
    resp = requests.get(
        f"https://api.github.com/users/{username}/repos").json()
    print(resp)
    if type(resp) is dict:
        return f'ERROR: {resp["message"]}'
    parsedRepos = []
    for repo in resp:
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
        parsedRepos += parsedRepo
    return flask.render_template('widget.html', **context={repos=parsedRepos})


@app.route("/")
def serveMain():
    return flask.render_template('index.html')
