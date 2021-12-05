import re
import requests

from bs4 import BeautifulSoup
from parse_tululu import save_books, check_for_redirect


def get_category_html(category_id, page=1):
    page_prefix = f"{page}/" if page > 1 else ""
    response = requests.get(f"https://tululu.org/{category_id}/" + page_prefix, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

    return response.text


def parse_category_page(page_html):
    book_ids = []
    soup = BeautifulSoup(page_html, "lxml")
    book_links = soup.find(id="content").find_all(href=re.compile(r"^\/b\d+"))
    for book_link in book_links:
        book_ids.append(book_link["href"][2:-1])
    return book_ids


if __name__ == "__main__":
    for page in range(1, 3):
        category_html = get_category_html("l55", page=page)
        book_ids = parse_category_page(category_html)

        save_books(book_ids)
