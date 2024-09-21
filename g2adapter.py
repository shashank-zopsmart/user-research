from ratelimit import limits, sleep_and_retry
import requests
from bs4 import BeautifulSoup
from scraperadapter import ScraperAdapter

class G2Adapter(ScraperAdapter):
    @sleep_and_retry
    @limits(calls=10, period=60)  # Be respectful to the website
    def scrape(self, query, max_results=100):
        base_url = f"https://www.g2.com/products/{query}/reviews"
        reviews = []
        page = 1

        while len(reviews) < max_results:
            url = f"{base_url}?page={page}"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')

            new_reviews = soup.find_all('div', class_='review__body')
            if not new_reviews:
                break

            for review in new_reviews:
                if len(reviews) >= max_results:
                    break
                reviews.append({
                    'text': review.text.strip(),
                    'rating': review.find_previous('meta', itemprop='ratingValue')['content']
                })

            page += 1

        return reviews