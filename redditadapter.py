import json
import os

from ratelimit import limits, sleep_and_retry
import praw
from prawcore.exceptions import PrawcoreException
from scraperadapter import ScraperAdapter
from loguru import logger


class RedditAdapter(ScraperAdapter):
    def __init__(self, client_id, client_secret, user_agent, threshold_criteria=None):
        self.reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
        self.scraped_posts = os.listdir('./raw/reddit/')
        self.threshold_criteria = threshold_criteria

    @sleep_and_retry
    @limits(calls=60, period=60)
    def scrape(self, query, max_results=100):
        try:
            for submission in self.reddit.subreddit("all").search(query, limit=max_results):
                if f'{submission.id}.json' in self.scraped_posts:
                    continue

                if self.threshold_criteria is not None:
                    if not self.threshold_criteria(submission):
                        continue

                post = {
                    'title': submission.title,
                    'text': submission.selftext,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'comments': [
                        {
                            "id": comment.id,
                            "body": comment.body,
                            "author": comment.author.name if comment.author else None
                        }
                        for comment in submission.comments
                    ]
                }

                self.save_response(submission.id, post)
                self.scraped_posts.append(f'{submission.id}.json')
        except PrawcoreException as e:
            logger.exception(f'An error occurred with Reddit API: {e}')
        except Exception as e:
            logger.exception(f'An unexpected error occurred: {e}')
        else:
            logger.info('Scraping completed successfully.')
        finally:
            return self.scraped_posts

    @staticmethod
    def save_response(post_id, data):
        filename = f'./raw/reddit/{post_id}.json'
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f'Data has been successfully written to {filename}')
        except IOError as e:
            logger.exception(f'An I/O error occurred while writing the file: {e}')
        except json.JSONDecodeError as e:
            logger.exception(f'An error occurred while encoding JSON: {e}')
        except Exception as e:
            logger.exception(f'An unexpected error occurred: {e}')
