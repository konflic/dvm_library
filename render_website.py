import json
import os
import webbrowser

from math import ceil
from more_itertools import chunked
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape


server = Server()

env = Environment(
    loader=FileSystemLoader("."), autoescape=select_autoescape(["html", "xml"])
)

template = env.get_template("templates/template.html")


def on_reload():
    with open("books_info.json", "r") as books_json:
        books = json.loads(books_json.read())
        start_from = 1
        books_in_row = 2
        books_per_page = 20
        pages = range(start_from, ceil(len(books) / books_per_page))

        for page, books in enumerate(chunked(books, books_per_page), start=start_from):
            
            chunked_books = chunked(books, books_in_row)
            rendered_page = template.render(books=chunked_books, pages=pages, current=page, prev=page-1, _next=page+1)

            os.makedirs("pages", exist_ok=True)

            with open(f"pages/index{page}.html", "w", encoding="utf-8") as file:
                file.write(rendered_page)

on_reload()

server.watch("templates/*.html", on_reload)

webbrowser.open("http://localhost:5500/pages/index1.html")

server.serve()
