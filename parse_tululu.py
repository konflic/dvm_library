import json
import os
import sys
import requests
import argparse

from urllib.parse import urljoin, urlsplit, unquote
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def download_book(url, folder):
    """Функция для скачивания книг.
    :param url (str): Ссылка на текст, который хочется скачать.
    :param folder (str): Папка, куда сохранять.
    :return: (str) Путь до файла, куда сохранён текст или None
    """
    response = requests.get(url, verify=False, allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)

    book_id = urlsplit(url).query.split("=")[-1]
    book_html = get_book_html(book_id)
    book_info = parse_book_page(book_html)

    book_filename = sanitize_filename(f"{book_info['title']}-{book_id}")
    book_image_file = extract_filename_from_url(book_info["image"])

    download_image(book_info["image"], f"{book_filename}{os.path.splitext(book_image_file)[1]}")

    path_for_book = os.path.join(folder, f"{book_filename}.txt")

    with open(path_for_book, "w+") as f:
        f.write(response.text)

    return book_info


def extract_filename_from_url(file_url):
    unquoted_url = unquote(file_url)
    return os.path.split(urlsplit(unquoted_url).path)[1]


def download_image(image_url, image_name, folder="images/"):
    save_as = os.path.join(folder, image_name)

    with open(save_as, "wb+") as f:
        response = requests.get(image_url, verify=False)
        response.raise_for_status()

        f.write(response.content)


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


def save_books(book_ids, books_folder="books", images_folders="images"):
    os.makedirs(books_folder, exist_ok=True)
    os.makedirs(images_folders, exist_ok=True)

    book_info_json = []
    for book_id in book_ids:
        book_url = f"https://tululu.org/txt.php?id={book_id}"

        try:
            book_info = download_book(book_url, books_folder)
            book_info_json.append(book_info)
        except requests.HTTPError:
            print(f"{book_url} отсутствует на сайте!", file=sys.stderr)
        except requests.ConnectionError:
            print(f"Ошибка соединения при обращении к {book_url}!", file=sys.stderr)

    with open("books_info.json", "w+", encoding="utf-8") as f:
        f.write(json.dumps(book_info_json, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_id", type=int, default=1, required=False)
    parser.add_argument("--end_id", type=int, default=10, required=False)

    args = parser.parse_args()

    save_books(range(args.start_id, args.end_id))
