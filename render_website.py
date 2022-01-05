import json
import webbrowser

from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader("."), autoescape=select_autoescape(["html", "xml"])
)

template = env.get_template("templates/template.html")

with open("books_info.json") as books_json:
    books = json.loads(books_json.read())

    rendered_page = template.render(books=books)

    with open("index.html", "w", encoding="utf8") as file:
        file.write(rendered_page)

webbrowser.open("http://localhost:8000")

server = HTTPServer(("0.0.0.0", 8000), SimpleHTTPRequestHandler)
server.serve_forever()
