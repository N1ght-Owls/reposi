from werkzeug.wrappers import Request
from flask import Flask, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
import os
import requests
import random
from contact_form import ContactForm
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.contrib.gitlab import make_gitlab_blueprint, gitlab
from discord_webhook import DiscordWebhook
import flask
from os import path
from flask_dance.consumer import oauth_authorized

app = Flask(__name__,  template_folder="templates", static_folder='static')

# Various environmental variables
app.secret_key = os.environ.get("FLASK_SECRET")
discord_url = os.environ.get("WEBHOOK")
app.config["GITHUB_OAUTH_CLIENT_ID"] = os.environ.get(
    "REPOSI_GITHUB_CLIENT_ID")
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.environ.get(
    "REPOSI_GITHUB_SECRET")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# Github blueprint
github_bp = make_github_blueprint()
github_bp.redirect_url = "https://reposi.0cdn.me/docs"
app.register_blueprint(github_bp, url_prefix="/login")

app.config["GITLAB_OAUTH_CLIENT_ID"] = os.environ.get(
    "REPOSI_GITLAB_ID")
app.config["GITLAB_OAUTH_CLIENT_SECRET"] = os.environ.get(
    "REPOSI_GITLAB_SECRET")
gitlab_bp = make_gitlab_blueprint()
app.register_blueprint(gitlab_bp, url_prefix="/login")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# Database model & connection
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
db = SQLAlchemy(app)
git_token = os.environ.get("GITHUB_TOKEN")
print(git_token)
@oauth_authorized.connect
def redirect_to_docs(blueprint, token):
    blueprint.token = token
    user = []
    git_hash = []
    resp = github.get("/user")
    user = User.query.filter_by(username=resp.json()['login']).first()
    if not user:
        user = User(username=resp.json()['login'],
                    github_hash=str(random.getrandbits(128)))
        db.session.add(user)
        db.session.commit()
        DiscordWebhook(url=discord_url, content=f"New user: {resp.json()['login']}. Check out profile at https://github.com/{resp.json()['login']}").execute()
    git_hash = user.github_hash
    return redirect(f"/docs?username={resp.json()['login']}&token={git_hash}")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    github_hash = db.Column(db.String(80), unique=True, nullable=True)
   # gitlab_hash = db.Column(db.String(80), unique=True, nullable=True)

    def __repr__(self):
        return '<User %r>' % self.username


if path.exists("db.sqlite") == True:
    print("Database exists")
else:
    print("Creating database")
    db.create_all()

# Routing and repository parsing
@app.route("/signup")
def signup():
    resp = github.get("/user")
    if not github.authorized:
        return redirect(url_for("github.login"))
    print(resp)
    assert resp.ok
    user = User.query.filter_by(username=resp.json()['login']).first()
    username = resp.json()['login']
    github_hash = user.github_hash
    return redirect(f"/docs?username={username}&token={github_hash}")


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
        if repo['fork'] == False: parsedRepos.append(parsedRepo)
    parsedRepos.sort(key=lambda repo: repo["stars"], reverse=True)
    return parsedRepos


@app.route("/widget/<username>")
def thing(username):
    token = request.args.get('token')
    db.session.commit()
    user = User.query.filter_by(username=username).first()
    resp = {}
    theme = request.args.get('theme')
    if theme != 'dark': theme = 'light'
    if user == None:
        return "User not found"
    else:
        if user.github_hash == token:
            resp = requests.get(
                f"https://api.github.com/users/{username}/repos?per_page=100", auth=("Uzay-G", git_token)).json()
            if type(resp) is dict:
                return f'ERROR: {resp["message"]}'
            return flask.render_template('widget.html', repos=parseGithubRepos(resp), theme=theme)
        else:
            return "You do not have a valid api token"


@app.route("/")
def serveMain():
    form = ContactForm()
    return flask.render_template('index.html', form=form)


@app.route("/docs")
def docs():
    form = ContactForm()
    return flask.render_template('docs.html', username=request.args.get('username'), token=request.args.get("token"), hostname=os.environ.get('FLASK_HOST'), form=form)

@app.route("/contact", methods=['POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        flash('Your message was received')
        DiscordWebhook(url=discord_url, content=f"Contact @hackathon: name: {form.name.data}, email: {form.email.data}, message: {form.message.data}").execute()
    else:
        flash('Your message was not transferred correctly.')
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)


# @app.route("/signup_gitlab")
# def signup_gitlab():
#     resp = gitlab.get("/user")
#     if not gitlab.authorized:
#         return redirect(url_for("gitlab.login"))
#     print(resp)
#     assert resp.ok
#     user = User.query.filter_by(username=resp.json()['login']).first()
#     username = resp.json()['login']
#     gitlab_hash = user.gitlab_hash
#     return redirect(f"/docs?username={username}&token={gitlab_hash}")

# def getGitlabRepoLanguage(repo):
#     resp = requests.get(f"https://gitlab.com/api/v4/projects/{repo['id']}/languages").json()
#     return next(iter(resp))


# def parseGitlabRepos(repos):
#     parsedRepos = []
#     for repo in repos:
#         parsedRepo = {}
#         parsedRepo['name'] = repo['name']
#         if repo['description'] == None:
#             parsedRepo['description'] = "No description provided"
#         else:
#             parsedRepo['description'] = repo['description']
#         try:
#             parsedRepo['issues'] = repo['open_issues_count']
#         except:
#             parsedRepo['issues'] = 0
#         parsedRepo['owner'] = repo['namespace']['name']
#         parsedRepo['stars'] = repo['star_count']
#         parsedRepo['forks'] = repo['forks_count']
#         parsedRepo['url'] = repo['web_url']
#         try:
#             parsedRepo['size'] = repo['statistics']['repository_size'],
#         except:
#             parsedRepo['size'] = None
#         parsedRepo['language'] = getGitlabRepoLanguage(repo)
#         parsedRepos.append(parsedRepo)
#     return parsedRepos