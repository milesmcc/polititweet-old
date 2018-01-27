"""
It is very lightweight, and will simply write tweets
to their respective files as they come in.

Because of its streaming capabilities, this file uses
tweepy as opposed to python-twitter. Sorry.
"""

import tweepy
from tweepy import StreamListener
import json
import database

config_location = "../configs_real/twitter.config.json"
config = json.load(open(config_location, "r"))

consumer_key = config["consumerKey"]
consumer_secret = config["consumerSecret"]
access_token_key = config["accessTokenKey"]
access_token_secret = config["accessTokenSecret"]
trackList = config["monitorList"]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)

api = tweepy.API(auth)

def time():
    return database.time()

class Handler(StreamListener):
    def on_data(self, data):
        dataDict = json.loads(str(data), encoding="utf8")
        if "user" not in dataDict.keys():
            print("[i] not a tweet")
            return
        dataDict["deleted"] = False
        userData = dataDict["user"]
        dataDict["user"] = {
            'id': dataDict["user"]["id"]
        }
        database.writeTweet(dataDict)
        database.writeAccountData(userData)
        print("Detected tweet and wrote to file: " + dataDict["id_str"] + " of " + dataDict["user"]["id_str"])
        return True
    def on_error(self, status):
        print("Error: " + str(status))

while True:
    # try:
        stream = tweepy.Stream(auth=api.auth, listener=Handler())
        stream.filter(track=trackList)
    # except Exception as e:
    #     print(e)
