import requests
from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, render_template
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
    data = myanimelist.get('https://api.myanimelist.net/v2/users/@me').json()
    print(data)
    return render_template('dashboard.html', user=data)


@app.route('/anime-list', methods=['GET'])
def animeList():
    access_token = session['oauth_token']['access_token']
    url = 'https://api.myanimelist.net/v2/users/@me/animelist?fields=list_status&limit=4'
    response = requests.get(url,
                            headers={
                                'Authorization', f'Bearer {access_token}'
                            })
    data = response.json()['data']
    response.close()
    return render_template('animelist.html', data=data)


@app.route('/manga-ranking', methods=['GET'])
def mangaRanking():
    valuestring = 'all,manga,oneshots,doujin,lightnovels,novels,manhwa,manhua,bypopularity,favorite'
    rankingtypes = valuestring.split(',')
    limitvalues = [i for i in range(1, 501)]\

    rankingType = request.args.get('ranking_type')
    limitType = request.args.get('limit')
    if rankingType == None:
        rankingType = rankingtypes[0]
    if limitType == None or limitType.isdigit() == False:
        limitTypeInt = limitvalues[-1]
    else:
        limitTypeInt = int(limitType)
    access_token = session['oauth_token']['access_token']

    if limitTypeInt <= 500:
        url = 'https://api.myanimelist.net/v2/manga/ranking?ranking_type={!s}&limit={!s}'.format(rankingType,
                                                                                                 str(limitTypeInt))
        response = requests.get(url, headers={
            'Authorization': f'Bearer {access_token}'
        })
        data = response.json()['data']
        response.close()
        return render_template('mangarankings.html', data=data, ranking_types=rankingtypes)
    else:
        url = 'https://api.myanimelist.net/v2/manga/ranking?ranking_type={!s}&limit={!s}'.format(rankingType, '500')

        response = requests.get(url, headers={
            'Authorization': f'Bearer {access_token}'
        })
        data = response.json()['data']
        url = response.json()['paging']['next']
        response.close()
        originalLimit = limitTypeInt
        limitTypeInt -= 500
        while limitTypeInt > 0:
            response = requests.get(url, headers={
                'Authorization': f'Bearer {access_token}'
            })
            data += response.json()['data']
            url = response.json()['paging']
            response.close()
            limitTypeInt -= 500
        data = data[:originalLimit]
        return render_template('mangarankings.html', data=data, ranking_types=rankingtypes)

if __name__ == '__main__':
    load_dotenv()

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.secret_key = os.urandom(24)
    app.run(debug=True)
