import tornado.web
import json
import database
from operator import itemgetter
import html.parser
import requests.status_codes as codes

def unescape(text):
    return html.parser.HTMLParser().unescape(text)

def render(tweets):
    rendered = []
    for tweet in tweets:
        tweet["text"] = unescape(tweet["text"])
        rendered.append(tweet)
    return rendered

def status_code_str(code):
    return codes._codes[code][0].replace("_", " ")

def httpsify(link):
    link.replace("http://", "https://", 1)

def injectHeaders(handler):
    pass
    #handler.set_header("Content-Security-Policy", "upgrade-insecure-requests")

brand = "PolitiTweet"

class IndexHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        injectHeaders(self)
        self.render("pages/error.html", message=status_code_str(status_code), error=status_code, brand=brand)
    def get(self):
        injectHeaders(self)
        self.render("pages/index.html", count=database.getTotalAccounts(), total_deleted=database.getTotalDeletedTweets(), brand=brand)
class DeletedHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        injectHeaders(self)
        self.render("pages/error.html", message=status_code_str(status_code), brand=brand, error=status_code)
    def get(self):
        injectHeaders(self)
        deleted_tweets = database.getLatestDeletedTweets(32)
        for tweet in deleted_tweets:
            tweet["user"] = database.getAccountData(tweet["user"]["id"])
        self.render("pages/deleted.html", count=len(deleted_tweets), brand=brand, deleted=render(deleted_tweets))
class AboutHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        injectHeaders(self)
        self.render("pages/error.html", message=status_code_str(status_code), brand=brand, error=status_code)
    def get(self):
        injectHeaders(self)
        self.render("pages/about.html", count=database.getTotalAccounts(), brand=brand, total_deleted=database.getTotalDeletedTweets())
class FiguresHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        injectHeaders(self)
        self.render("pages/error.html", message=status_code_str(status_code), brand=brand, error=status_code)
    def get(self):
        injectHeaders(self)
        figures = []
        for account in database.getAllAccounts():
            if account is None:
                continue
            try:
                account["archive_url"] = "figure?account=" + str(account["id"])
                figures.append(account)
            except Exception as e:
                print(account)
                print(e)
                continue
        figures_sorted = sorted(figures, key=itemgetter('name'))
        for figure in figures_sorted:
            try:
                figure["deleted_tweets_length"] = len(database.getDeletedTweets(figure["id"]))
            except KeyError:
                figure["deleted_tweets_length"] = 0
        self.render("pages/figures.html", figures=figures_sorted, brand=brand)
class FigureHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        injectHeaders(self)
        self.render("pages/error.html", message=status_code_str(status_code), brand=brand, error=status_code)
    def get(self):
        injectHeaders(self)
        user = self.get_argument("account")
        account = database.getAccountData(user)
        account["json"] = json.dumps(account)
        account["description"] = unescape(account["description"])
        account["deleted_tweets"] = database.getDeletedTweets(int(user))
        account["deleted_tweets_length"] = len(account["deleted_tweets"])
        self.render("pages/figure.html", brand=brand, figure=account)
class TweetsHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        injectHeaders(self)
        self.render("pages/error.html", brand=brand, message=status_code(status_code), error=status_code)
    def get(self):
        injectHeaders(self)
        user = self.get_argument("account")
        deleted = bool(self.get_argument("deleted", default=False))
        tweets = []
        title = "Tweets of @"
        if deleted:
            title = "Deleted " + title
            tweets.extend(database.getDeletedTweets(int(user)))
        else:
            tweets.extend(database.getTweets(int(user)))
        last = int(self.get_argument("last", default=len(tweets)))
        account = database.getAccountData(int(user))
        title = title + account["screen_name"]
        account["json"] = json.dumps(account)
        tweets_sorted = sorted(tweets, key=lambda tweet: int(tweet["id"]), reverse=True)
        self.render("pages/tweets.html", figure=account, brand=brand, title=title, statuses=render(tweets_sorted[:last]))
class TweetHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        injectHeaders(self)
        self.render("pages/error.html", brand=brand, message=status_code(status_code), error=status_code)
    def get(self):
        injectHeaders(self)
        user = self.get_argument("account")
        tweet = self.get_argument("tweet")
        tweet_data = database.getTweet(int(tweet))
        account = database.getAccountData(int(user))
        account["json"] = json.dumps(account)
        account["description"] = unescape(account["description"])
        account["deleted_tweets_length"] = len(database.getDeletedTweets(int(user)))
        tweet_data["json"] = json.dumps(tweet_data)
        tweet_data["text"] = unescape(tweet_data["text"])
        if "favorite_count" not in tweet_data:  # for some reason if =0 twitter omits favorite count
            tweet_data["favorite_count"] = 0
        if "retweet_count" not in tweet_data:  # for some reason if =0 twitter omits retweet count
            tweet_data["retweet_count"] = 0
        self.render("pages/tweet.html", brand=brand, figure=account, tweet=tweet_data)
class ErrorHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        injectHeaders(self)
        self.render("pages/error.html", brand=brand, message=status_code_str(status_code), error=status_code)
    def get(self):
        injectHeaders(self)
        self.render("pages/error.html", brand=brand, message="Page not found", error="404")
application = tornado.web.Application([
    (r"/", IndexHandler),
    (r"/figures", FiguresHandler),
    (r"/about", AboutHandler),
    (r"/figure", FigureHandler),
    (r"/tweets", TweetsHandler),
    (r"/deleted", DeletedHandler),
    (r"/tweet", TweetHandler),
    (r'/static/(.*)$', tornado.web.StaticFileHandler, {'path': "pages/static"})
    ], default_handler_class=ErrorHandler)
if __name__ == "__main__":
    print("Launching...")
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
