import os
import requests

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
        book_data = extract_book_data(book_id=url.split("=")[-1])
        path_for_book = os.path.join(folder, sanitize_filename(f"{book_data['title']}.txt"))

        print(book_data)

        download_image(book_data["image"])

        with open(path_for_book, "w+") as f:
            f.write(response.text)

    return path_for_book


def download_image(image_url, folder="images/"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    save_as = os.path.join(folder, image_url.split("/")[-1])

    with open(save_as, "wb+") as f:
        f.write(requests.get(image_url, verify=False).content)


def extract_book_data(book_id):
    response = requests.get(f"https://tululu.org/b{book_id}/", verify=False)

    soup = BeautifulSoup(response.text, "lxml")
    h1 = soup.find(id="content").find("h1").text

    title, author = map(lambda item: item.strip(), h1.split("::"))
    image = soup.find("div", class_="bookimage").find("img").get("src")
    comments = soup.find(id="content").find_all(class_="texts")

    return {
        "title": title,
        "author": author,
        "image": urljoin("https://tululu.org", image),
        "comments": list(map(lambda item: item.find(class_="black").text, comments))
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
    save_books(range(1, 11))
