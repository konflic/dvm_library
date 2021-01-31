import os
import requests


def save_book(book_name, book_id, folder="books"):
    r = requests.get(f"https://tululu.org/txt.php?id={book_id}", verify=False)

    if not os.path.isdir(folder):
        os.mkdir(folder)

    with open(f"books/{book_name}.txt", "w+") as f:
        f.write(r.text)


if __name__ == "__main__":
    save_book("Пески Марса", 32168)
