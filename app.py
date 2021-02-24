from flask import Flask, request, redirect, session, url_for, render_template
from dotenv import load_dotenv
import json
import requests
import secrets
import os
from os import path
from mal_dashboard import oauth2


app = Flask(__name__)
application = app

Oauth2 = oauth2()
code_verifier = code_challenge = Oauth2.get_new_code_verifier()

def get_token():
    if path.exists("token.json"):
        tokenjson = open('token.json')
        tokendict = json.load(tokenjson)
        token = tokendict['access_token']
        return token
    else:
        return False

@app.route("/", methods = ['GET','POST'])
def main():
    #key = request.args.get('key')
    try:
        key = request.form['key']
    except:
        key = None
    if path.exists("token.json"):
        token = get_token()
        user = Oauth2.print_user_info(token)
        return render_template("dashboard.html",user = user)
    elif key!=None:
        auth_code = key[key.find("code=")+5:]
        print(auth_code)
        tokendict = Oauth2.generate_new_token(auth_code, code_verifier)
        token = tokendict['access_token']
        user = Oauth2.print_user_info(token)
        return render_template("dashboard.html",user = user)
    else:
        
        url = Oauth2.print_new_authorisation_url(code_challenge)
        return render_template("login.html", url = url)

@app.route("/get-manga-ranking", methods = ["GET"])
def mangaRanking():
    valuestring = "all,manga,oneshots,doujin,lightnovels,novels,manhwa,manhua,bypopularity,favorite"
    rankingtypes = valuestring.split(',')
    limitvalues = [i for i in range(1,501)]

    rankingType = request.args.get('ranking_type')
    limitType = request.args.get('limit')
    if rankingType == None:
        rankingType = rankingtypes[0]
    if limitType == None or limitType.isdigit()==False:
        limitTypeInt = limitvalues[-1]
    else:
        limitTypeInt = int(limitType)
    access_token = get_token()
    if limitTypeInt <= 500:
        url = 'https://api.myanimelist.net/v2/manga/ranking?ranking_type={!s}&limit={!s}'.format(rankingType,str(limitTypeInt))
        response = requests.get(url, headers={
            'Authorization': f'Bearer {access_token}'
        })

        response.raise_for_status()
        data = response.json()["data"]
        response.close()
        return render_template("mangarankings.html",data = data, ranking_types = rankingtypes)
    else:
        url = 'https://api.myanimelist.net/v2/manga/ranking?ranking_type={!s}&limit={!s}'.format(rankingType,"500")
        
        response = requests.get(url, headers={
            'Authorization': f'Bearer {access_token}'
        })

        response.raise_for_status()
        data = response.json()["data"]
        url = response.json()["paging"]["next"]
        print(url)
        response.close()
        originalLimit = limitTypeInt
        limitTypeInt-=500
        while limitTypeInt>0:
            response = requests.get(url, headers={
                'Authorization': f'Bearer {access_token}'
            })
            response.raise_for_status()
            if response.status_code != 200:
                break
            data += response.json()["data"]
            url = response.json()["paging"]
            response.close()
            limitTypeInt-=500
        data = data[:originalLimit]
        return render_template("mangarankings.html",data = data, ranking_types = rankingtypes)


if __name__ == "__main__":
    app.run()