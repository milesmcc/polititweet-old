from time import gmtime, strftime
import json
import pymongo

"""
This is pretty nice as far as non-objective code goes.
"""

MongoClient = pymongo.MongoClient

client = MongoClient()

config_location = "../configs/database.config.json"
config = json.load(open(config_location, "r"))

db = MongoClient(config["mongodb"]["address"], config["mongodb"]["port"])['polititweet']

db.profiles.create_index([('id', pymongo.DESCENDING)], unique=True, background=True)

def clean(dict):
    del dict['_id']
    return dict

def time():
    return strftime("%Y-%m-%d--%H-%M-%S", gmtime())

def getLatestTweets(num=16):
    return [clean(t) for t in db.tweets.find().sort([("id", pymongo.DESCENDING)]).limit(num)]

def getTweets(user_id):
    return [clean(t) for t in db.tweets.find({"user.id": int(user_id)})]

def markTweetAsDeleted(tweet_id):
    db.tweets.update({'id': int(tweet_id)}, {'deleted': True})

def getTweet(tweet_id):
    return clean(db.tweets.find_one({'id': int(tweet_id)}))

def getTotalTweets():
    return db.tweets.distinct('id').count()

def getAccountData(account_id):
    return clean(db.accounts.find_one({'id': int(account_id)}))

def hasAccountData(account_id):
    return getAccountData(account_id) != None;

def getTotalDeletedTweets():
    return db.tweets.find({'deleted': True}).count()

def getLatestDeletedTweets(num):
    return [clean(t) for t in db.tweets.find({'deleted': True}).sort([("id", pymongo.DESCENDING)]).limit(num)]

def getAllDeletedTweets():
    return [clean(t) for t in db.tweets.find({'deleted': True}).sort([("id", pymongo.DESCENDING)])]

def getDeletedTweets(user_id):
    return [clean(t) for t in db.tweets.find({'deleted': True, "user.id": int(user_id)}).sort([("id", pymongo.DESCENDING)])]

def getAllAccounts():
    return [clean(t) for t in db.accounts.find()]

def writeAccountData(metadata):
    return db.accounts.insert_one(metadata)

def getTotalAccounts():
    return db.accounts.distinct('id').count(True)

def writeTweet(tweet_data):
    tweet_data["retrieved"] = time()
    db.tweets.insert_one(tweet_data)

def getHighestLowestArchivedStatus(account_id):
    lowest_archived_status = -1  # for the max_id parameter for subsequent searches
    highest_archived_status = -1
    for tweet in getTweets(account_id):
        status = tweet["id"]
        if status < lowest_archived_status or lowest_archived_status == -1:
            lowest_archived_status = status
        if status > highest_archived_status or highest_archived_status == -1:
            highest_archived_status = status
    return [highest_archived_status, lowest_archived_status]
