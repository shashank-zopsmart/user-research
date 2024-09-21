from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Set up Selenium WebDriver with the appropriate driver installed
chromedriver_path = './chromedriver'
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)

# URL of the G2 product review page
url = 'https://www.g2.com/products/docker/reviews'

try:
    # Open the page using Selenium
    driver.get(url)

    # Wait for the content to load (e.g., wait for a particular element to be present)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'review__content'))  # Adjust class name as needed
    )

    # Get the page source
    page_source = driver.page_source

    # Parse with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extract review titles, ratings, and other relevant info
    reviews = soup.find_all('div', class_='review__content')  # Adjust class name as per the site

    for review in reviews:
        title = review.find('h3').text.strip() if review.find('h3') else 'N/A'  # Example: Get the title of the review
        rating = review.find('span', class_='rating').text.strip() if review.find('span',
                                                                                  class_='rating') else 'N/A'  # Example: Get the rating
        text = review.find('p').text.strip() if review.find('p') else 'N/A'  # Example: Get the review content

        print(f'Title: {title}\nRating: {rating}\nReview: {text}\n')

finally:
    # Close the WebDriver
    driver.quit()
