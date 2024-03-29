# Парсер книг с сайта tululu.org

Проект скачивает текстовые версии книг и обложки с сайта https://tululu.org вместе с обложками. Из загруженных данных можно сгенерировать html представление библиотеки.

### Пример html представления

![Screenshot](example.png)

https://konflic.github.io/dvm_library/pages/ 

### Как установить

Для запуска нужно воспользоваться версией python > 3.6.

Библиотеки установить в виртуальное окружение из файла requirements.txt.

MacOS и Linux
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell)
```
python -m venv venv
source .\venv\Scripts\activate.ps1
pip install -r requirements.txt
```

### Использование

Скрипт принимает следующие аргументы.

```
dest_folder — путь к каталогу с результатами парсинга: картинкам, книгам, JSON.
skip_imgs — не скачивать картинки
skip_txt — не скачивать книги
json_path — указать свой путь к *.json файлу с результатами
start_page - начальная страница раздела фантастики (по умолчнаию 1)
end_page - последняя страница раздела фантастики (по умолчанию 701)
```

Скрипт скачает книги в указанном диапазоне начиная с первого значения и заканчивая правым в папку ```dest_folder``` которая будет создана автоматически. 

Если какого-то из id на сайте не представлено, то ничего страшного, скрипт отказоустойчив. 

```bash
python parse_tululu_category.py --start_page 10 --end_page 15 --json_path info.json --dest_folder results
```

В результате такого запроса будут обработаны страницы раздела с 10 по 15.

### Как сгенерировать html представление

Для генерации библиотеки нужно выполнить команду:

```bash
python render_website.py
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
