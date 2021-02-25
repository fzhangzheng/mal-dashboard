import json
from os import path
class Utils():
    #gets token from token.json
    def get_token(self):
        if path.exists("token.json"):
            tokenjson = open('token.json')
            tokendict = json.load(tokenjson)
            token = tokendict['access_token']
            return token
        else:
            return False