from os import listdir
from ratelimit import limits, sleep_and_retry
import tweepy
from scraperadapter import ScraperAdapter

class TwitterAdapter(ScraperAdapter):
    def __init__(self, api_key, api_secret, access_token, access_token_secret):
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
        self.raw_files = listdir('./raw/twitter')

    @sleep_and_retry
    @limits(calls=450, period=900)
    def scrape(self, query, max_results=100):
        tweets = []

        for tweet in tweepy.Cursor(self.api.search_tweets, q=query, tweet_mode='extended').items(max_results):
            tweets.append(tweet.full_text)

        return tweets