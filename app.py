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
@app.route("/", methods = ['GET','POST'])
def main():
    print("hi")
    key = request.args.get('key')
    print("bye")
    if path.exists("token.json"):
        tokenjson = open('token.json')
        tokendict = json.load(tokenjson)
        token = tokendict['access_token']
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

# @app.route("/dashboard", methods = ['POST','GET'])
# def authenticate():
#     key = request.form['key']
#     auth_code = key[key.find("code=")+5:]
#     print(auth_code)
#     tokendict = Oauth2.generate_new_token(auth_code, code_verifier)
#     token = tokendict['access_token']
#     user = Oauth2.print_user_info(token)
#     return render_template("dashboard.html",user = user)

if __name__ == "__main__":
    app.run()