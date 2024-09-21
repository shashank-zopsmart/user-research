import json
import os
from ratelimit import limits, sleep_and_retry
import tweepy
from scraperadapter import ScraperAdapter


class TwitterAdapter(ScraperAdapter):
    def __init__(self, api_key, api_secret, access_token, access_token_secret, threshold_criteria=None):
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
        self.scraped_tweets = os.listdir('./raw/twitter/')
        self.threshold_criteria = threshold_criteria

    @sleep_and_retry
    @limits(calls=450, period=900)
    def scrape(self, query, max_results=100):
        try:
            for tweet in tweepy.Cursor(self.api.search_tweets, q=query, tweet_mode='extended').items(max_results):
                tweet_id = tweet.id_str
                if f'{tweet_id}.json' in self.scraped_tweets:
                    continue

                if self.threshold_criteria is not None:
                    if not self.threshold_criteria(tweet):
                        continue

                tweet_data = {
                    'full_text': tweet.full_text,
                    'author': {
                        'name': tweet.user.name,
                        'screen_name': tweet.user.screen_name
                    },
                    'likes': tweet.favorite_count,
                    'retweets': tweet.retweet_count,
                    'comments': self.get_comments(tweet_id),
                    'comment_count': tweet.reply_count  # Assuming this is how replies are counted
                }

                self.save_response(tweet_id, tweet_data)
                self.scraped_tweets.append(f'{tweet_id}.json')
        except tweepy.TweepError as e:
            print(f'An error occurred with Twitter API: {e}')
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
        finally:
            return self.scraped_tweets

    @staticmethod
    def get_comments(tweet_id):
        # Placeholder method to get comments. Implementation could vary.
        # NOTE: Twitter API v1.1 doesn't provide an easy way to get comments.
        # In a real-world scenario, you might need to use Twitter API v2 or a different method.
        return []

    @staticmethod
    def save_response(tweet_id, data):
        filename = f'./raw/twitter/{tweet_id}.json'
        try:
            with open(filename, 'w') as f:
                f.write(json.dumps(data, indent=4))
            print(f'Data has been successfully written to {filename}')
        except IOError as e:
            print(f'An I/O error occurred while writing the file: {e}')
        except json.JSONDecodeError as e:
            print(f'An error occurred while encoding JSON: {e}')
        except Exception as e:
            print(f'An unexpected error occurred: {e}')

