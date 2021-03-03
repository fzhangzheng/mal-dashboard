from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
from dotenv import load_dotenv
import secrets
import os

app = Flask(__name__)

client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')
authorization_base_url = 'https://myanimelist.net/v1/oauth2/authorize'
token_url = 'https://myanimelist.net/v1/oauth2/token'

# Initial OAuth connection
@app.route('/')
def login():
    token = secrets.token_urlsafe(100)
    code_challenge = token[:128]

    myanimelist = OAuth2Session(os.getenv('client_id'))
    authorization_url, state = myanimelist.authorization_url(authorization_base_url,
                                                             code_challenge=code_challenge)

    session['oauth_state'] = state
    session['code_challenge'] = code_challenge
    return redirect(authorization_url)

# Getting redirect and then getting token
@app.route('/callback', methods=['GET'])
def callback():
    myanimelist = OAuth2Session(client_id, state=session['oauth_state'])
    token = myanimelist.fetch_token(token_url,
                                    client_secret=client_secret,
                                    authorization_response=request.url,
                                    code_verifier=session['code_challenge'])
    session['oauth_token'] = token

    return redirect(url_for('.profile'))

@app.route('/profile', methods=['GET'])
def profile():
    myanimelist = OAuth2Session(client_id, token=session['oauth_token'])
    return jsonify(myanimelist.get('https://api.myanimelist.net/v2/users/@me').json())


if __name__ == '__main__':
    load_dotenv()

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=True)
