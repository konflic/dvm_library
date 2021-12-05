import argparse
import requests

from bs4 import BeautifulSoup
from parse_tululu import save_books, check_for_redirect


def get_category_html(category_id="l55", page=1):
    page_prefix = f"{page}/" if page > 1 else ""
    response = requests.get(f"https://tululu.org/{category_id}/" + page_prefix, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

    return response.text


def parse_category_page(page_html):
    book_ids = []
    soup = BeautifulSoup(page_html, "lxml")
    book_links = soup.select(selector="#content a[href^='/b']")
    for book_link in book_links:
        book_ids.append(book_link["href"][2:-1]) # /b300/ -> b300
    return book_ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--dest_folder", type=str, required=True)
    parser.add_argument("--skip_imgs", action="store_true", default=False)
    parser.add_argument("--skip_txt", action="store_true", default=False)
    parser.add_argument("--json_path", type=str, required=True)
    parser.add_argument("--start_page", type=int, default=1, required=False)
    parser.add_argument("--end_page", type=int, default=701, required=False)

    args = parser.parse_args()

    book_ids = []
    for page in range(args.start_page, args.end_page):
        page_html = get_category_html(page=page)
        book_ids.extend(parse_category_page(page_html))

    save_books(
        book_ids=book_ids,
        json_path=args.json_path,
        dest_folder=args.dest_folder,
        skip_imgs=args.skip_imgs,
        skip_txt=args.skip_txt
    )
