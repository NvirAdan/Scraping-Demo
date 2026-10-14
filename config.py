"""Central configuration for the books scraper demo."""

BASE_URL = "https://books.toscrape.com/"
MAX_PAGES = 50                  # The site has 50 pages (1000 books)
REQUEST_DELAY = (0.5, 1.2)      # Random pause between requests (seconds)
TIMEOUT = 15                    # Seconds before a request is abandoned
MAX_RETRIES = 3                 # Attempts per page before skipping it
USER_AGENT = "Mozilla/5.0 (compatible; books-scraper-demo/1.0)"
OUTPUT_DIR = "output"
