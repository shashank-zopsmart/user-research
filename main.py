import os
import time
import json
import argparse
from dotenv import load_dotenv
from loguru import logger
from g2adapter import G2Adapter
from redditadapter import RedditAdapter
from twitteradapter import TwitterAdapter
from youtubeadapter import YouTubeAdapter
from transcriptprocessor import TranscriptProcessor


def load_env():
    env = os.environ.get("APP_ENV", "")
    filepath = f"./configs/.{env}.env"
    load_dotenv(filepath)
    return os.environ


class MultiSourceScraper:
    def __init__(self):
        self.adapters = {}

    def add_adapter(self, name, adapter):
        self.adapters[name] = adapter

    def scrape(self, query, max_results=100):
        results = {}
        for name, adapter in self.adapters.items():
            try:
                logger.info(f"Starting scrape for {name}")
                results[name] = adapter.scrape(query, max_results)
                logger.info(f"Finished scrape for {name}")
            except Exception as e:
                logger.error(f"Error scraping {name}: {str(e)}")
                results[name] = []
        return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Multi-source scraper")
    parser.add_argument('--query', type=str, required=True, help="Search query")
    parser.add_argument('--max_results', type=int, default=100, help="Maximum number of results to scrape")
    args = parser.parse_args()

    configs = load_env()

    redditConfigs = {
        "client_id": configs.get("REDDIT_CLIENT_ID"),
        "client_secret": configs.get("REDDIT_CLIENT_SECRET"),
        "user_agent": configs.get("REDDIT_USER_AGENT"),
        "threshold_criteria": None,
    }

    youtubeConfigs = {
        "api_key": configs.get("YOUTUBE_API_KEY"),
        "threshold_criteria": None,
    }

    twitterConfigs = {
        "api_key": configs.get("TWITTER_API_KEY"),
        "api_secret": configs.get("TWITTER_API_SECRET"),
        "access_token": configs.get("TWITTER_ACCESS_TOKEN"),
        "access_token_secret": configs.get("TWITTER_ACCESS_TOKEN_SECRET"),
        "threshold_criteria": None,
    }

    scraper = MultiSourceScraper()
    scraper.add_adapter('reddit', RedditAdapter(**redditConfigs))
    scraper.add_adapter('twitter', TwitterAdapter(**twitterConfigs))
    # scraper.add_adapter('g2', G2Adapter())
    scraper.add_adapter('youtube', YouTubeAdapter(**youtubeConfigs))

    start_time = time.time()
    logger.info(f"Starting scraping with query: {args.query} and max_results: {args.max_results}")
    results = scraper.scrape(args.query, max_results=args.max_results)

    openai_key = configs.get("OPENAI_API_KEY")

    if 'youtube' in results:
        logger.info("Starting transcript processing for YouTube results")
        transcriptProcessor = TranscriptProcessor(openai_key, "youtube", results['youtube'])
        transcriptProcessor.process_transcripts()
        logger.info("Finished transcript processing for YouTube results")

    time_since = time.time() - start_time
    logger.info(f"Time since start: {time_since} seconds")
