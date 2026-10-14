"""Page fetching and HTML parsing for books.toscrape.com."""

import random
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

import config

RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def build_session():
    """Create a reusable HTTP session with a fixed User-Agent."""
    session = requests.Session()
    session.headers.update({"User-Agent": config.USER_AGENT})
    return session


def fetch_html(session, url):
    """GET a URL with retries and exponential backoff.

    Returns the HTML text, or None if every attempt failed.
    """
    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=config.TIMEOUT)
            response.raise_for_status()
            response.encoding = "utf-8"  # avoids broken currency symbols
            return response.text
        except requests.RequestException as exc:
            print(f"[!] Attempt {attempt}/{config.MAX_RETRIES} failed for {url}: {exc}")
            if attempt < config.MAX_RETRIES:
                time.sleep(2 ** attempt)
    return None


def parse_page(html, page_url):
    """Extract the books on one listing page.

    Returns (books, next_page_url). next_page_url is None on the last page.
    """
    soup = BeautifulSoup(html, "html.parser")
    books = []

    for card in soup.select("article.product_pod"):
        link = card.select_one("h3 a")
        if link is None:
            continue  # unexpected layout: skip instead of crashing

        price = card.select_one("p.price_color")
        rating = card.select_one("p.star-rating")
        stock = card.select_one("p.availability")

        rating_word = ""
        if rating is not None:
            rating_word = next(
                (c for c in rating.get("class", []) if c in RATING_WORDS), ""
            )

        books.append({
            "title": link.get("title", "").strip(),
            "price_raw": price.get_text(strip=True) if price else "",
            "rating_raw": rating_word,
            "availability_raw": stock.get_text(strip=True) if stock else "",
            "url": urljoin(page_url, link.get("href", "")),
        })

    next_link = soup.select_one("li.next a")
    next_url = urljoin(page_url, next_link["href"]) if next_link else None
    return books, next_url


def scrape_all(max_pages=None):
    """Walk the listing pages and return (raw_books, failed_pages)."""
    max_pages = max_pages or config.MAX_PAGES
    session = build_session()

    url = config.BASE_URL
    all_books = []
    failed_pages = 0
    page_number = 0

    while url and page_number < max_pages:
        page_number += 1
        print(f"[*] Page {page_number}/{max_pages}: {url}")

        html = fetch_html(session, url)
        if html is None:
            failed_pages += 1
            print(f"[!] Giving up on page {page_number}; stopping here.")
            break  # next-page link is unknown without this page

        books, url = parse_page(html, url)
        all_books.extend(books)

        if url:
            time.sleep(random.uniform(*config.REQUEST_DELAY))

    return all_books, failed_pages
