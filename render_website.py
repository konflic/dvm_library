import json
import webbrowser

from more_itertools import chunked
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape


server = Server()

env = Environment(
    loader=FileSystemLoader("."), autoescape=select_autoescape(["html", "xml"])
)


def on_reload():
    template = env.get_template("templates/template.html")

    with open("books_info.json") as books_json:
        books = json.loads(books_json.read())
        chunked_books = chunked(books, 2)
        rendered_page = template.render(books=chunked_books)

        print(chunked_books)

        with open("index.html", "w", encoding="utf8") as file:
            file.write(rendered_page)


server.watch("templates/*.html", on_reload)

webbrowser.open("http://localhost:5500")

server.serve(root="")
