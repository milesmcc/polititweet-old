import twitterinterface
import database
from random import shuffle
import json

config_location = "../configs_real/twitter.config.json"
config = json.load(open(config_location, "r"))

following = [802399136012177408, 945391013828313088]

"""
Loads the followers into memory, as well as their data.

Required to run before archiveAll() and scanForDeletedAccounts().

If a followed user cannot be found in the database, its data is
retrieved from Twitter.

It also does preliminary updating functions on the database.
"""
def loadDatabase():
    global following

    print("Loading database...")
    following = []
    following.extend(twitterinterface.getListMembers(account_name=config["monitorListOwner"], slug=config["monitorListSlug"]))
    friend_data = twitterinterface.api.GetFriends()
    for account in friend_data:
        database.writeAccountData(account.AsDict())

"""
Smart archive.

Scans for deleted tweets AND archives everything.

Only run this for accounts that exist on Twitter.
"""
def smarchive(id):
    print("Smarchiving " + str(id) + "...")
    tweets = twitterinterface.getAllStatuses(id)
    account = twitterinterface.getAccount(id)
    database.writeAccountData(account)
    print("Retrieved " + str(len(tweets)) + " tweets from Twitter. Archiving...")
    for tweet in tweets:
        tweet_dict = tweet.AsDict()
        tweet_dict["deleted"] = False
        tweet_dict["retrieved"] = database.time()
        database.writeTweet(tweet_dict)
    print("Retrieving tweets from database...")
    database_tweets = database.getTweets(id)
    twitter_tweet_ids = [t.id for t in tweets]
    database_tweet_ids = [t["id"] for t in database_tweets]
    deleted_tweets = [t for t in database_tweet_ids if t not in twitter_tweet_ids]
    print("Found " + str(len(deleted_tweets)) + " deletion candidates... checking")
    for tweet in deleted_tweets:
        if twitterinterface.doesStatusExist(tweet):
            deleted_tweets.remove(tweet)
        else:
            database.markTweetAsDeleted(tweet)
            print("[!] deleted tweet: " + str(tweet))
    print("Found " + str(len(deleted_tweets)) + " deleted tweets!")


"""
Archive every user that is being followed.
"""
def archiveAll(repeat=True):
    shuffle(following)  # so that accounts at end will get same coverage over time
    first = []
    for account in following:
        if not database.hasAccountData(account):
            first.append(account)
            following.remove(account)
    print("Processing accounts first: " + str(first))
    for account in first:
        if not database.hasAccountData(account) or repeat:
            smarchive(account)
        else:
            print("Already archived " + str(account))
    print("Now processing others...")
    for account in following:
        if not database.hasAccountData(account) or repeat:
            smarchive(account)
        else:
            print("Already archived " + str(account))


while True:
    # try:
        loadDatabase()
        shuffle(following)
        while True:
            archiveAll()  # includes Smarchive, which does deleted tweets!
    # except Exception as e:
    #     print(e)
    #     print("Restarting...")
