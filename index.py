import os
import requests


def save_book(books_id, folder="books"):
    if not os.path.isdir(folder):
        os.mkdir(folder)

    if isinstance(books_id, list):

        for book in books_id:
            r = requests.get(f"https://tululu.org/txt.php?id={book}", verify=False)

            with open(f"books/id{book}.txt", "w+") as f:
                f.write(r.text)


if __name__ == "__main__":
    save_book([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
