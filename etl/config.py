import os

# Пути
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "books_links.sqlite3")
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Лог-файлы
LOG_PARSE_BOOKS = os.path.join(LOG_DIR, "parse_books.log")

# Настройки парсинга
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# Поля для метаданных
FIELDS = {
    'Назва': 'title',
    'Автор': 'author',
    'Серія': 'seria',
    'Видавництво': 'publisher',
    'Кількість сторінок': 'pages_count',
    'Обкладинка': 'cover_type',
    'Рік видання': 'publication_year',
    'Перекладач': 'translator',
    'Мова': 'book_language',
    'ISBN': 'isbn',
}
