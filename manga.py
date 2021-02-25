from flask import Flask, request, redirect, session, url_for, render_template
from dotenv import load_dotenv
import json
import requests
import secrets
import os
from os import path
from mal_dashboard import oauth2
from utils import Utils

class Manga():
    Utils = Utils()
    Oauth2 = oauth2()
    def getMangaRanking(self):
        code_verifier = code_challenge = self.Oauth2.get_new_code_verifier()
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
        access_token = self.Utils.get_token()
        if limitTypeInt <= 500:
            url = 'https://api.myanimelist.net/v2/manga/ranking?ranking_type={!s}&limit={!s}'.format(rankingType,str(limitTypeInt))
            response = requests.get(url, headers={
                'Authorization': f'Bearer {access_token}'
            })

            response.raise_for_status()
            #401 is for token refresh
            if response.status_code == 401:
                if os.path.exists("token.json"):
                    os.remove("token.json")
                url = self.Oauth2.print_new_authorisation_url(code_challenge)
                return render_template("login.html", url = url)
            data = response.json()["data"]
            response.close()
            return render_template("mangarankings.html",data = data, ranking_types = rankingtypes)
        else:
            url = 'https://api.myanimelist.net/v2/manga/ranking?ranking_type={!s}&limit={!s}'.format(rankingType,"500")
            
            response = requests.get(url, headers={
                'Authorization': f'Bearer {access_token}'
            })

            response.raise_for_status()
            #401 is for token refresh
            if response.status_code == 401:
                if os.path.exists("token.json"):
                    os.remove("token.json")
                url = self.Oauth2.print_new_authorisation_url(code_challenge)
                return render_template("login.html", url = url)
            data = response.json()["data"]
            url = response.json()["paging"]["next"]
            response.close()
            originalLimit = limitTypeInt
            limitTypeInt-=500
            while limitTypeInt>0:
                response = requests.get(url, headers={
                    'Authorization': f'Bearer {access_token}'
                })
                response.raise_for_status()
                #401 is for token refresh
                if response.status_code == 401:
                    if os.path.exists("token.json"):
                        os.remove("token.json")
                    url = self.Oauth2.print_new_authorisation_url(code_challenge)
                    return render_template("login.html", url = url)
                elif response.status_code != 200:
                    break

                data += response.json()["data"]
                url = response.json()["paging"]
                response.close()
                limitTypeInt-=500
            data = data[:originalLimit]
            return render_template("mangarankings.html",data = data, ranking_types = rankingtypes)
