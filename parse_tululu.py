import os
import requests
import argparse

from urllib.parse import urljoin
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def download_txt(url, folder):
    """Функция для скачивания книг.
    :param url (str): Ссылка на текст, который хочется скачать.
    :param folder (str): Папка, куда сохранять.
    :return: (str) Путь до файла, куда сохранён текст или None
    """
    response = requests.get(url, verify=False, allow_redirects=False)

    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return None
    else:
        book_data = parse_book_page(get_book_html(book_id=url.split("=")[-1]))

        download_image(book_data["image"])

        path_for_book = os.path.join(folder, sanitize_filename(f"{book_data['title']}.txt"))

        with open(path_for_book, "w+") as f:
            f.write(response.text)

    return path_for_book


def download_image(image_url, folder="images/"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    save_as = os.path.join(folder, image_url.split("/")[-1])

    with open(save_as, "wb+") as f:
        f.write(requests.get(image_url, verify=False).content)


def get_book_html(book_id):
    return requests.get(f"https://tululu.org/b{book_id}/", verify=False).text


def parse_book_page(page_html):
    soup = BeautifulSoup(page_html, "lxml")
    h1 = soup.find(id="content").find("h1").text

    title, author = map(lambda item: item.strip(), h1.split("::"))
    image = soup.find("div", class_="bookimage").find("img").get("src")
    comments = soup.find(id="content").find_all(class_="texts")
    genres = soup.find(id="content").find("span", class_="d_book").find_all("a")

    return {
        "title": title,
        "author": author,
        "image": urljoin("https://tululu.org", image),
        "comments": [comment.find(class_="black").text for comment in comments],
        "genres": [genre.text for genre in genres]
    }


def check_for_redirect(response):
    if str(response.status_code).startswith("3"):
        raise requests.HTTPError


def save_books(books_id, folder="books/"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    for book_id in books_id:
        download_txt(f"https://tululu.org/txt.php?id={book_id}", folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("start_id", type=int, default=1)
    parser.add_argument("end_id", type=int, default=10)

    args = parser.parse_args()

    save_books(range(args.start_id, args.end_id))