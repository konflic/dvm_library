import json
import os
import webbrowser

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

        for page, books in enumerate(chunked(books, 20), start=1):
            
            chunked_books = chunked(books, 2)
            rendered_page = template.render(books=chunked_books)

            os.makedirs("pages", exist_ok=True)

            with open(f"pages/index{page}.html", "w", encoding="utf-8") as file:
                file.write(rendered_page)


server.watch("templates/*.html", on_reload)
server.watch("books_info.json", on_reload)

webbrowser.open("http://localhost:5500/pages/index1.html")

server.serve()
