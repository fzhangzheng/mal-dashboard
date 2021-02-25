from flask import Flask, request, redirect, session, url_for, render_template
from dotenv import load_dotenv
import json
import requests
import secrets
import os
from os import path
from mal_dashboard import oauth2
from utils import Utils
class Login():
    Utils = Utils()
    Oauth2 = oauth2()
    code_verifier = code_challenge = Oauth2.get_new_code_verifier()
    def login(self):
        
        try:
            key = request.form['key']
        except:
            key = None
        if path.exists("token.json"):
            token = self.Utils.get_token()
            user = self.Oauth2.print_user_info(token)
            #render dashboard
            return render_template("dashboard.html",user = user)

        #set authentication page to get auth token.
        elif key==None:
            url = self.Oauth2.print_new_authorisation_url(self.code_challenge)
            return render_template("login.html", url = url)
        #create new token after authentication
        else:
            auth_code = key[key.find("code=")+5:]
            print(auth_code)
            tokendict = self.Oauth2.generate_new_token(auth_code, self.code_verifier)
            token = tokendict['access_token']
            user = self.Oauth2.print_user_info(token)
            return render_template("dashboard.html",user = user)