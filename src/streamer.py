"""
This is a completely self-contained streaming program for Politiwatch.

It is very lightweight, and will simply write tweets
to their respective files as they come in.

Because of its streaming capabilities, this file uses
tweepy as opposed to python-twitter. Sorry.
"""

import tweepy
from tweepy import StreamListener, Stream
import json
import time
import os
import database

config_location = "configs/twitter.config.json"
config = json.load(open(config_location, "r"))

consumer_key = config["consumerKey"]
consumer_secret = config["consumerSecret"]
access_token_key = config["accessTokenKey"]
access_token_secret = config["accessTokenSecret"]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)

api = tweepy.API(auth)

previous_userdata = {}

def time():
    return database.time()

class Handler(StreamListener):
    def on_data(self, data):
        # try:
        print(data)
        dataDict = json.loads(str(data), encoding="utf8")
        print(dataDict)
        if "user" not in dataDict.keys():
            print("[i] not a tweet")
            return
        if dataDict["user"]["id"] in previous_userdata.keys():
            if previous_userdata[dataDict["user"]["id"]]["statuses_count"] <= dataDict["user"]["statuses_count"]:
                print("has deleted tweet!")
                print("[!] " + dataDict["user"]["id_str"] + " has deleted a tweet!")
                database.markAsHasDeletedTweet(dataDict["user"]["id_str"])
        dataDict["deleted"] = False
        dataDict["retrieved"] = time()
        previous_userdata[dataDict["user"]["id"]] = dataDict["user"]
        database.initializeTweetArchive(dataDict["user"]["id"])
        database.writeTweet(dataDict["user"]["id"], dataDict["id"], json.dumps(dataDict))
        database.writeLatestTweet(dataDict)
        print("Detected tweet and wrote to file: " + dataDict["id_str"] + " of " + dataDict["user"]["id_str"])
        # except Exception as e:
        #     print(e)
        return True
    def on_error(self, status):
        print "Error: "
        print(status)

while True:
    try:
        stream = tweepy.Stream(auth = api.auth, listener=Handler())
        #try:
        stream.userstream()
    except Exception as e:
        print(e)
    #except Exception as e:
    #    print("Error: ")
    #    e.print
    #    print("Reconnecting in 5 seconds...")
    #    time.sleep(5)

    # (courtesy of StackOverflow)
