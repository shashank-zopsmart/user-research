import os
import time
import json
import argparse
from distutils.log import fatal

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

def get_configs(configs):
    app_confgis = {
        'reddit': {
        "client_id": configs.get("REDDIT_CLIENT_ID"),
        "client_secret": configs.get("REDDIT_CLIENT_SECRET"),
        "user_agent": configs.get("REDDIT_USER_AGENT"),
        "threshold_criteria": None,
    },
    'youtube': {
        "api_key": configs.get("YOUTUBE_API_KEY"),
        "threshold_criteria": None,
    },
    'twitter': {
        "auth_info": {
            "auth_info_1": configs.get("TWITTER_AUTH_INFO_1"),
            "auth_info_2": configs.get("TWITTER_AUTH_INFO_2"),
            "password": configs.get("TWITTER_AUTH_INFO_PASSWORD"),
        },
        "language": "en-US",
        "threshold_criteria": None,
    }}
    
    return app_confgis

def add_adapters(app_configs, scraper, sources):
    sources = sources.split(',')

    for source in sources:
        if source == 'youtube':
            scraper.add_adapter('youtube', YouTubeAdapter(**app_configs[source]))
        elif source == 'reddit':
            scraper.add_adapter('reddit', RedditAdapter(**app_configs[source]))
        elif source == 'twitter':
            scraper.add_adapter('twitter', TwitterAdapter(**app_configs[source]))
        elif source == 'g2':
            scraper.add_adapter('g2', G2Adapter())
        else:
            logger.exception(f"Invalid source: {source}")
            return


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
                logger.exception(f"Error scraping {name}: {str(e)}")
                results[name] = []
        return results


def main():
    parser = argparse.ArgumentParser(description="Multi-source scraper and transcript processor")
    parser.add_argument('action', choices=['scrape', 'process-transcript'], help="Action to perform")
    parser.add_argument('--scrape_sources', type=str, help="Source of scrape")
    parser.add_argument('--transcript_source', choices=['youtube'], required=False, help="Source of transcript")
    parser.add_argument('--query', type=str, help="Search query")
    parser.add_argument('--max_results', type=int, default=100, help="Maximum number of results to scrape")
    args = parser.parse_args()

    configs = load_env()
    appp_configs = get_configs(configs)
    
    # scraper.add_adapter('reddit', RedditAdapter(**redditConfigs))
    # scraper.add_adapter('twitter', TwitterAdapter(**twitterConfigs))
    # scraper.add_adapter('g2', G2Adapter())
    # scraper.add_adapter('youtube', YouTubeAdapter(**appp_configs['youtubeConfigs']))

    openai_key = configs.get("OPENAI_API_KEY")

    start_time = time.time()

    if args.action == 'scrape':
        if not args.query:
            logger.exception("The --query argument is required for scraping")
            return

        if not args.scrape_sources:
            logger.exception("The --scrape_sources argument is required for scraping")
            return

        scraper = MultiSourceScraper()

        add_adapters(appp_configs, scraper, args.scrape_sources)

        logger.info(f"Starting scraping with query: {args.query} and max_results: {args.max_results}")
        results = scraper.scrape(args.query, max_results=args.max_results)
        logger.info(f"Results: {results}")
        time_since = time.time() - start_time
        logger.info(f"Time since start: {time_since} seconds")

    elif args.action == 'process-transcript':
        if not os.path.exists('./processed-transcripts/'):
            os.makedirs('./processed-transcripts/')

        logger.info("Starting transcript processing for YouTube results")
        results = {args.transcript_source: os.listdir(f"./raw/{args.transcript_source}/")}
        transcriptProcessor = TranscriptProcessor(openai_key, "youtube", results.get('youtube', []))
        transcriptProcessor.process_transcripts()
        logger.info("Finished transcript processing for YouTube results")

        time_since = time.time() - start_time
        logger.info(f"Time since start: {time_since} seconds")


if __name__ == '__main__':
    main()
