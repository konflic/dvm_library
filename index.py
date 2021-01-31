import os
import requests
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
        title, author = extract_book_data(url.split("=")[-1])
        path_for_book = os.path.join(folder, sanitize_filename(f"{title}.txt"))

        with open(path_for_book, "w+") as f:
            f.write(response.text)

    return path_for_book


def extract_book_data(book_id):
    """
    :param response: Response from book page
    :return: (title, author)
    """
    response = requests.get(f"https://tululu.org/b{book_id}/", verify=False)
    soup = BeautifulSoup(response.text, "lxml")
    h1 = soup.find(id="content").find("h1").text

    return map(lambda item: item.strip(), h1.split("::"))


def check_for_redirect(response):
    if str(response.status_code).startswith("3"):
        raise requests.HTTPError


def save_books(books_id, folder="books"):
    if not os.path.isdir(folder):
        os.mkdir(folder)

    for book in books_id:
        download_txt(f"https://tululu.org/txt.php?id={book}", folder)


if __name__ == "__main__":
    save_books(range(1, 11))
