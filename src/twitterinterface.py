import twitter
import json
import time

config_location = "../configs_real/twitter.config.json"
config = json.load(open(config_location, "r"))

consumer_key = config["consumerKey"]
consumer_secret = config["consumerSecret"]
access_token_key = config["accessTokenKey"]
access_token_secret = config["accessTokenSecret"]

api = twitter.Api(consumer_key=consumer_key,
                  consumer_secret=consumer_secret,
                  access_token_key=access_token_key,
                  access_token_secret=access_token_secret,
                  sleep_on_rate_limit=True)

"""
Get the last 3200 statuses of a user from Twitter.
"""
def getAllStatuses(id, lowest_archived_status=-1):
    max_id = lowest_archived_status
    statuses = []
    if lowest_archived_status == -1:
        statuses = api.GetUserTimeline(user_id=id, include_rts=False, count=200, trim_user=False)
        max_id = statuses[0].id
    if lowest_archived_status < max_id and lowest_archived_status != -1: # for redundancy
        max_id = lowest_archived_status
    print("Lowest archived status: " + str(lowest_archived_status))
    print(api.GetUser(user_id=id).AsDict())
    while len(statuses) < api.GetUser(user_id=id).statuses_count:
        try:
            print("    ...from " + str(max_id))
            new_statuses = api.GetUserTimeline(user_id=id, count=200, max_id=max_id, trim_user=True)
            statuses.extend(new_statuses)
            if max_id == new_statuses[-1].id:
                break
            max_id = new_statuses[-1].id
        except Exception as e:
            print(e)
            break
        time.sleep(1)  # to avoid rate limiting
    return statuses

def getAllStatusesSince(id, since):
    statuses = api.GetUserTimeline(user_id=id, include_rts=False, count=200, trim_user=True, since_id=since)
    time.sleep(1)  # to avoid rate limiting
    if len(statuses) >= 200:  # more than 200 tweets since last grab
        max_id = statuses[-1].id
        max_id_old = -1
        while max_id != max_id_old:  # weird way of doing this, but it's clever. As soon as we reach the end of the new items, we will get a non-%200 length array OR the max-id will be the same as last time (assuming perfect 200)!
            statuses.extend(api.GetUserTimeline(user_id=id, include_rts=False, count=200, trim_user=True, since_id=since, max_id=max_id))
            max_id_old = max_id
            max_id = statuses[-1].id
            print("   ...from " + str(max_id))
            time.sleep(1)  # to avoid rate limiting
    return statuses

"""Check whether or not a tweet exists (or if it has been deleted)"""
def doesStatusExist(status):
    try:
        api.GetStatus(status_id=status)
        return True
    except Exception as error:
        try:
            valid_codes = [144, 50, 63]  # the error codes which would designate a deleted account
            if error[0][0]["code"] in valid_codes:
                return False
            else:
                print("Error: " + str(error))
                return True
        except Exception as e:
            print(e)