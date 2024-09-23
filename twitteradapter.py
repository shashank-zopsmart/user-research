import json
import os

from ratelimit import limits, sleep_and_retry
from twikit import Client

class TwitterAdapter:
    def __init__(self, auth_info, language='en-US', threshold_criteria=None):
        self.client = Client(language)
        self.auth_info = auth_info
        self.scraped_tweets = os.listdir('./raw/twitter/')
        self.threshold_criteria = threshold_criteria

    async def scrape(self, query, max_results=100):
        results = []
        try:
            await self.client.login(**self.auth_info)
            tweets = await self.client.search_tweet(query=query, max_results=max_results)
            for tweet in tweets:
                if f'{tweet["id"]}.json' in self.scraped_tweets:
                    continue

                if self.threshold_criteria is not None:
                    if not self.threshold_criteria(tweet):
                        continue

                tweet_data = {
                    'body': tweet['full_text'],
                    'likes': tweet['favorite_count'],
                    'retweets': tweet['retweet_count'],
                    'user_info': {
                        'username': tweet['user']['screen_name'],
                        'followers_count': tweet['user']['followers_count'],
                        'following_count': tweet['user']['friends_count']
                    },
                    'tweet_id': tweet['id']
                }

                self.save_response(tweet['id'], tweet_data)
                self.scraped_tweets.append(f'{tweet["id"]}.json')

                results.append(tweet_data)

        except Exception as e:
            print(f'Error during scraping: {e}')
        return results

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

