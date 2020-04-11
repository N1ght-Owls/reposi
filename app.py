import markovify
import requests
import flask
app = flask.Flask(__name__)


@app.route("/api/<username>")
def thing(username):
    req = requests.get(
        f"https://www.allmytweets.net/get_tweets.php?count=200&tweet_mode=extended&trim_user&screen_name={username}")

    text = ''
    for tweet in req.json():
        text += tweet['full_text'] + "\n"

    mark = markovify.NewlineText(text)
    sent = mark.make_sentence()
    if sent == None:
        sent = "Too few tweets to imitate"
    print(sent)
    return sent


@app.route("/")
def serveMain():
    return flask.render_template('index.html')
