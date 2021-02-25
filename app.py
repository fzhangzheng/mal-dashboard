from flask import Flask, request, redirect, session, url_for, render_template
from dotenv import load_dotenv
import json
import requests
import secrets
import os
from os import path
from mal_dashboard import oauth2
from manga import Manga
from login import Login

app = Flask(__name__)
application = app

Login = Login()
Manga = Manga()




#checks token.json to see if token.json exists. 
@app.route("/", methods = ['GET','POST'])
def main():
    return Login.login()

@app.route("/get-manga-ranking", methods = ["GET"])
def mangaRanking():
    return Manga.getMangaRanking()

if __name__ == "__main__":
    app.run()