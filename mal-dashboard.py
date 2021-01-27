from flask import Flask, request, redirect, session, url_for
from dotenv import load_dotenv
import json
import requests
import secrets
import os

load_dotenv()

def get_new_code_verifier() -> str:
    token = secrets.token_urlsafe(100)
    return token[:128]

def print_new_authorisation_url(code_challenge: str):
    url = f"https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={os.getenv('client_id')}&code_challenge={code_challenge}"
    print(f'Authorize by clicking here: {url}\n')

def generate_new_token(authoization_code: str, code_verifier: str) -> dict:
    url = 'https://myanimelist.net/v1/oauth2/token'
    data = {
        'client_id': os.getenv('client_id'),
        'client_secret': os.getenv('client_secret'),
        'code': authorization_code,
        'code_verifier': code_verifier,
        'grant_type': 'authorization_code'
    }

    response = requests.post(url, data)
    response.raise_for_status()

    token = response.json()
    response.close()
    print('Token generated')

    with open('token.json', 'w') as file:
        json.dump(token, file, indent = 4)
        print('Token saved in token.json')

    return token

def print_user_info(access_token: str):
    url = 'https://api.myanimelist.net/v2/users/@me'
    response = requests.get(url, headers={
        'Authorization': f'Bearer {access_token}'
    })

    response.raise_for_status()
    user = response.json()
    response.close()

    print(f"Your username {user['name']}")

if __name__ == '__main__':
    code_verifier = code_challenge = get_new_code_verifier()
    print_new_authorisation_url(code_challenge)

    authorization_code = input('Copy-paste the Authorisation Code: ').strip()
    token = generate_new_token(authorization_code, code_verifier)

    print_user_info(token['access_token'])