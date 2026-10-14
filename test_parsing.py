"""Offline tests: parsing and cleaning, no network needed.

Run with:  python test_parsing.py   (or pytest)
"""

from cleaner import clean_books, parse_price
from scraper import parse_page

PAGE_1 = """
<html><body>
<article class="product_pod">
  <p class="star-rating Three"></p>
  <h3><a href="catalogue/book-a_1/index.html" title="Book A">Book A...</a></h3>
  <div class="product_price"><p class="price_color">Â£51.77</p>
  <p class="instock availability"> In stock </p></div>
</article>
<article class="product_pod">
  <p class="star-rating One"></p>
  <h3><a href="catalogue/book-b_2/index.html" title="Book B">Book B</a></h3>
  <div class="product_price"><p class="price_color">£12.50</p>
  <p class="instock availability">In stock</p></div>
</article>
<li class="next"><a href="catalogue/page-2.html">next</a></li>
</body></html>
"""

PAGE_2 = """
<html><body>
<article class="product_pod">
  <p class="star-rating Five"></p>
  <h3><a href="book-c_3/index.html" title="Book C">Book C</a></h3>
  <div class="product_price"><p class="price_color">£30.00</p>
  <p class="instock availability">Out of stock</p></div>
</article>
<article class="product_pod">
  <p class="star-rating One"></p>
  <h3><a href="book-b_2/index.html" title="Book B">Book B</a></h3>
  <div class="product_price"><p class="price_color">£12.50</p>
  <p class="instock availability">In stock</p></div>
</article>
</body></html>
"""


def test_parse_price():
    assert parse_price("£51.77") == 51.77
    assert parse_price("Â£51.77") == 51.77  # mojibake still parses
    assert parse_price("") is None
    assert parse_price(None) is None


def test_parse_page_and_pagination():
    books, next_url = parse_page(PAGE_1, "https://books.toscrape.com/")
    assert len(books) == 2
    assert books[0]["title"] == "Book A"
    assert books[0]["url"] == "https://books.toscrape.com/catalogue/book-a_1/index.html"
    assert next_url == "https://books.toscrape.com/catalogue/page-2.html"

    books2, next_url2 = parse_page(PAGE_2, next_url)
    assert len(books2) == 2
    assert books2[0]["url"] == "https://books.toscrape.com/catalogue/book-c_3/index.html"
    assert next_url2 is None  # last page


def test_cleaning():
    b1, nxt = parse_page(PAGE_1, "https://books.toscrape.com/")
    b2, _ = parse_page(PAGE_2, nxt)
    raw = b1 + b2 + [{"title": "", "price_raw": "£5", "rating_raw": "One",
                      "availability_raw": "In stock", "url": "x"}]
    rows, stats = clean_books(raw)

    assert stats["raw"] == 5
    assert stats["invalid"] == 1
    assert stats["duplicates"] == 1       # Book B appears twice
    assert stats["clean"] == 3
    assert [r["Price (GBP)"] for r in rows] == [12.5, 30.0, 51.77]  # sorted
    assert rows[1]["In Stock"] == "NO"
    assert rows[0]["Rating (1-5)"] == 1


if __name__ == "__main__":
    test_parse_price()
    test_parse_page_and_pagination()
    test_cleaning()
    print("All tests passed.")
