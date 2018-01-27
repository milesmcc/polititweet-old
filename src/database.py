from time import gmtime, strftime
import json
import os
from pymongo import MongoClient

client = MongoClient()

config_location = "../configs/database.config.json"
config = json.load(open(config_location, "r"))

db = MongoClient(config["mongodb"]["address"], config["mongodb"]["port"])['polititweet']

db.profiles.create_index([('id', pymongo.DESCENDING)], unique=True, background=True)

def time():
    return strftime("%Y-%m-%d--%H-%M-%S", gmtime())

def getLatestTweets(num=16):
    return db.tweets.find().sort({"id": pymongo.DESCENDING}).limit(num)

def writeLatestTweet(data):
    db.tweets.insert_one(data)

def markTweetAsDeleted(tweet_id):
    tweet = db.tweets.update({'id': tweet_id}, {'deleted': True})

def getTweet(tweet_id):
    return db.tweets.find_one({'id': tweet_id})

def getAccountFromDatabase(account_id):
    return db.accounts.find_one({'id': account_id})

def hasAccountData(account_id):
    return db.accounts.find_one({'id': account_id}) != None;

def getTotalDeletedTweets():
    return db.tweets.find({'deleted': True}).count()

def getLatestDeletedTweets(num):
    return db.tweets.find({'deleted': True}).sort({"id": pymongo.DESCENDING}).limit(num)

def getAllDeletedTweets():
    return db.tweets.find({'deleted': True}).sort({"id": pymongo.DESCENDING})

def getDeletedTweets(user_id):
    return db.tweets.find({'deleted': True, "user.id": user_id}).sort({"id": pymongo.DESCENDING})

def getAllAccountsInDatabase():
    return db.accounts.find()

def writeAccountMetadata(metadata):
    return db.accounts.insert_one(metadata)

def hasAccountMetadata(account_id):
    return hasAccountData(account_id)

def writeTweet(tweet_data_str):
    data = json.loads(tweet_data_str)
    data["retrieved"] = time()
    db.tweets.insert_one(data)

def getHighestLowestArchivedStatus(account_id):
    lowest_archived_status = -1  # for the max_id parameter for subsequent searches
    highest_archived_status = -1
    for tweet in db.tweets.find({"user.id": account_id}):
        status = tweet["id"]
        if status < lowest_archived_status or lowest_archived_status == -1:
            lowest_archived_status = status
        if status > highest_archived_status or highest_archived_status == -1:
            highest_archived_status = status
    return [highest_archived_status, lowest_archived_status]

def getAllTweetsInDatabase(account_id):
    return db.tweets.find({"user.id": account_id})

def getAccountMetadata(account_id):
    return db.accounts.find_one({"user.id": account_id}) # finds the latest
