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
import twitterinterface

config_location = "../configs_real/twitter.config.json"
config = json.load(open(config_location, "r"))

consumer_key = config["consumerKey"]
consumer_secret = config["consumerSecret"]
access_token_key = config["accessTokenKey"]
access_token_secret = config["accessTokenSecret"]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)

api = tweepy.API(auth)

following = twitterinterface.getListMembers(account_name=config["monitorListOwner"], slug=config["monitorListSlug"])

def time():
    return database.time()

class Handler(StreamListener):
    def on_data(self, data):
        dataDict = json.loads(str(data), encoding="utf8")
        if "user" not in dataDict.keys():
            print("[i] not a tweet")
            return
        if dataDict["user"]["id"] not in following:
            print("[i] not a relevant tweet (@" + dataDict["user"]["screen_name"] + ")")
            return
        dataDict["deleted"] = False
        userData = dataDict["user"]
        dataDict["user"] = {
            'id': dataDict["user"]["id"]
        }
        database.writeTweet(dataDict)
        database.writeAccountData(userData)
        print("Detected tweet and wrote to database: " + str(dataDict["id"]) + " of " + (userData["screen_name"]))
        return True
    def on_error(self, status):
        print("Error: " + str(status))

while True:
    try:
        stream = tweepy.Stream(auth=api.auth, listener=Handler())
        stream.filter(follow=[str(id) for id in following])
    except Exception as e:
        print(e)
