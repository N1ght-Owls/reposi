from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import os, requests, random
from flask_dance.contrib.github import make_github_blueprint, github
import flask

app = Flask(__name__,  template_folder="templates", static_folder = 'static')
#Various environmental variables
app.secret_key = os.environ.get("FLASK_SECRET")
app.config["GITHUB_OAUTH_CLIENT_ID"] = os.environ.get("REPOSI_GITHUB_CLIENT_ID")
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.environ.get("REPOSI_GITHUB_SECRET")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

#Github blueprint
github_bp = make_github_blueprint()
app.register_blueprint(github_bp, url_prefix="/login")

#Database model & connection
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    github_hash = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


#Routing and repository parsing
@app.route("/signup")
def signup():

    resp = github.get("/user")
    if not github.authorized:
        return redirect(url_for("github.login"))
    print(resp.json())
    assert resp.ok
    user = User.query.filter_by(username=resp.json()['login']).first()
    if user:
        message = f"You have successfully logged in as @{resp.json()['login']}. Your api token is {user.github_hash}"
    else:
        user = User(username= resp.json()['login'], github_hash= str(random.getrandbits(128)))
        db.session.add(user)
        db.session.commit()
        message = f"You have successfully logged in as @{resp.json()['login']} on GitHub"
    return redirect(f"/docs?message={message}")


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
    token = request.args.get('token')
    db.session.commit()
    user = User.query.filter_by(username=username).first()
    if (user.github_hash != token):
        return "You do not have the correct api token"
    resp = requests.get(
        f"https://api.github.com/users/{username}/repos").json()
    print(resp)
    if type(resp) is dict:
        return f'ERROR: {resp["message"]}'
    
    return flask.render_template('widget.html', repos=parseRepos(resp))


@app.route("/")
def serveMain():
    return flask.render_template('index.html')

@app.route("/docs")
def docs():
    return flask.render_template('docs.html', message=request.args.get('message'))

if __name__ == '__main__':
   app.run(debug=True)