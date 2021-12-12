import json
import os
import sys
import requests
import argparse

from urllib.parse import urljoin, urlsplit, unquote
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def get_book_info(book_id):
    book_html = get_book_html(book_id)
    book_info = parse_book_page(book_html)
    return book_info


def extract_filename_from_url(file_url):
    unquoted_url = unquote(file_url)
    return os.path.split(urlsplit(unquoted_url).path)[1]


def download_book_image(image_url, image_name, folder):
    save_as = os.path.join(folder, image_name)
    os.makedirs(folder, exist_ok=True)

    with open(save_as, "wb+") as f:
        response = requests.get(image_url, verify=False)
        response.raise_for_status()
        f.write(response.content)


def download_book_text(book_id, book_name, folder):
    save_as = os.path.join(folder, book_name)
    os.makedirs(folder, exist_ok=True)

    with open(save_as, "w+") as f:
        response = requests.get(
            url="https://tululu.org/txt.php",
            params={"id": book_id},
            verify=False,
            allow_redirects=False
        )
        response.raise_for_status()
        check_for_redirect(response)
        f.write(response.text)


def get_book_html(book_id):
    response = requests.get(f"https://tululu.org/b{book_id}/", verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    return response.text


def parse_book_page(page_html):
    soup = BeautifulSoup(page_html, "lxml")
    h1 = soup.select_one("#content h1").text

    title, author = map(lambda item: item.strip(), h1.split("::"))
    path_to_image = soup.select_one("div.bookimage img").get("src")
    comment_tags = soup.select("#content .texts")
    genre_tags = soup.select("#content span.d_book a")

    return {
        "title": title,
        "author": author,
        "image": urljoin("https://tululu.org/", path_to_image),
        "comments": [comment_tag.select_one(selector=".black").text for comment_tag in comment_tags],
        "genres": [genre.text for genre in genre_tags]
    }


def check_for_redirect(response):
    if str(response.status_code).startswith("3"):
        raise requests.HTTPError


def get_category_html(category_id="l55", page=1):
    response = requests.get(f"https://tululu.org/{category_id}/{page}", verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    return response.text


def parse_category_page(page_html):
    soup = BeautifulSoup(page_html, "lxml")
    book_links = soup.select(selector="#content a[href^='/b']")
    book_ids = [book_link["href"][2:-1] for book_link in book_links]
    return book_ids


def get_last_category_page(category_id="l55"):
    category_html = get_category_html(category_id=category_id)
    soup = BeautifulSoup(category_html, "lxml")
    last_page = soup.select(selector="#content p.center a:nth-last-child(1)").text
    return int(last_page)


def save_books(
        book_ids,
        json_path="books_info.json",
        books_folder="books/",
        images_folders="images/",
        dest_folder="results/",
        skip_imgs=False,
        skip_txt=False
):
    os.makedirs(dest_folder, exist_ok=True)

    books_info_json = []
    for book_id in book_ids:

        try:
            book_info = get_book_info(book_id)
            book_filename = sanitize_filename(f"{book_info['title']}-{book_id}")

            if not skip_txt:
                download_book_text(
                    book_id=book_id,
                    book_name=book_filename,
                    folder=os.path.join(dest_folder, books_folder)
                )

            if not skip_imgs:
                book_image_file = extract_filename_from_url(book_info["image"])
                download_book_image(
                    image_url=book_info["image"],
                    image_name=f"{book_filename}{os.path.splitext(book_image_file)[1]}",
                    folder=os.path.join(dest_folder, images_folders)
                )

            books_info_json.append(book_info)
        except requests.HTTPError:
            print(f"Книга с id={book_id} отсутствует на сайте.", file=sys.stderr)
        except requests.ConnectionError:
            print(f"Ошибка соединения при обращении к книге с id={book_id}.", file=sys.stderr)

    with open(json_path, "w+", encoding="utf-8") as f:
        f.write(json.dumps(books_info_json, ensure_ascii=False))


if __name__ == "__main__":
    last_page = get_last_category_page()

    parser = argparse.ArgumentParser()
    parser.add_argument("--dest_folder", type=str, required=True)
    parser.add_argument("--skip_imgs", action="store_true", default=False)
    parser.add_argument("--skip_txt", action="store_true", default=False)
    parser.add_argument("--json_path", type=str, required=True)
    parser.add_argument("--start_page", type=int, default=1, required=False)
    parser.add_argument("--end_page", type=int, default=last_page, required=False)

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
