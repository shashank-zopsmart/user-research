import os
import time
import json
from dotenv import load_dotenv
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
                results[name] = adapter.scrape(query, max_results)
            except Exception as e:
                print(f"Error scraping {name}: {str(e)}")
                results[name] = []
        return results


if __name__ == '__main__':
    configs = load_env()

    redditConfigs = {
        "client_id": configs.get("REDDIT_CLIENT_ID"),
        "client_secret": configs.get("REDDIT_CLIENT_SECRET"),
        "user_agent": configs.get("REDDIT_USER_AGENT"),
        "threshold_criteria": None,
    }

    scraper = MultiSourceScraper()
    # scraper.add_adapter('twitter', TwitterAdapter('aozAEjJt2slPLEiHNgRMGCXS7', 'e85zRAxwKkvaY2zbAl9JiHtGhyXH3YNZh6Zfkw0cNMWQPYIJq4', \
    #                                               '588918106-vVnToT0wu262rehKwXhWqqGAhvBnPIkzJbBgOBcI', 'EqiN6G4Y2tT3YkTcO0iv0by5zK8dRCddWmTmvsOl1KIVc'))
    scraper.add_adapter('reddit', RedditAdapter(**redditConfigs))
    # scraper.add_adapter('g2', G2Adapter())

    # scraper.add_adapter('youtube', YouTubeAdapter('AIzaSyAayConHIWS_LABo1Dz0zQv31iO96dAMlQ'))

    start_time = time.time()
    results = scraper.scrape('docker', max_results=10)

    openai_key = configs.get("OPENAI_API_KEY")

    transcriptProcessor = TranscriptProcessor(openai_key, "reddit", results['reddit'])

    transcriptProcessor.process_transcripts()

    time_since = time.time() - start_time
    
    print(f"Time since start: {time_since} seconds")
