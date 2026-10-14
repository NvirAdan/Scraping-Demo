"""Cleaning and quality control for the scraped records."""

import re

from scraper import RATING_WORDS


def parse_price(raw):
    """'£51.77' -> 51.77. Returns None if no number is found."""
    digits = re.sub(r"[^\d.]", "", raw or "")
    try:
        return float(digits)
    except ValueError:
        return None


def clean_books(raw_books):
    """Normalize fields, drop invalid rows and duplicates.

    Returns (clean_rows, stats) where stats counts what was removed.
    """
    stats = {"raw": len(raw_books), "invalid": 0, "duplicates": 0}
    seen_urls = set()
    clean = []

    for book in raw_books:
        price = parse_price(book["price_raw"])

        if not book["title"] or price is None:
            stats["invalid"] += 1
            continue
        if book["url"] in seen_urls:
            stats["duplicates"] += 1
            continue
        seen_urls.add(book["url"])

        clean.append({
            "Title": book["title"],
            "Price (GBP)": price,
            "Rating (1-5)": RATING_WORDS.get(book["rating_raw"]),
            "In Stock": "YES" if "in stock" in book["availability_raw"].lower() else "NO",
            "URL": book["url"],
        })

    clean.sort(key=lambda row: row["Price (GBP)"])
    stats["clean"] = len(clean)
    return clean, stats
