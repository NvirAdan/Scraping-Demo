"""Entry point: scrape -> clean -> export."""

import argparse
import os

import config
from cleaner import clean_books
from exporter import ensure_dir, export_csv, export_xlsx
from scraper import scrape_all


def main():
    parser = argparse.ArgumentParser(description="Books scraper demo")
    parser.add_argument("--pages", type=int, default=config.MAX_PAGES,
                        help="Number of listing pages to scrape")
    parser.add_argument("--output-dir", default=config.OUTPUT_DIR)
    args = parser.parse_args()

    raw_books, failed = scrape_all(max_pages=args.pages)
    rows, stats = clean_books(raw_books)

    ensure_dir(args.output_dir)
    export_csv(rows, os.path.join(args.output_dir, "books.csv"))
    export_xlsx(rows, os.path.join(args.output_dir, "books.xlsx"))

    print("\n--- Summary ---")
    print(f"Raw records:        {stats['raw']}")
    print(f"Invalid removed:    {stats['invalid']}")
    print(f"Duplicates removed: {stats['duplicates']}")
    print(f"Clean records:      {stats['clean']}")
    print(f"Failed pages:       {failed}")


if __name__ == "__main__":
    main()
