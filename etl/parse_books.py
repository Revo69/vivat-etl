import os
import time
import logging
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from config import DB_PATH, LOG_PARSE_BOOKS, HEADERS, FIELDS

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_PARSE_BOOKS, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def init_raw_books_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            author TEXT DEFAULT '',
            seria TEXT DEFAULT '',
            publisher TEXT DEFAULT '',
            pages_count INTEGER DEFAULT 0,
            cover_type TEXT DEFAULT '',
            publication_year INTEGER DEFAULT 0,
            translator TEXT DEFAULT '',
            book_language TEXT DEFAULT '',
            isbn TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            uploaded BOOLEAN DEFAULT 0,
            FOREIGN KEY (link_id) REFERENCES raw_links(id)
        )
    """)
    conn.commit()

def parse_book(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
    except Exception as e:
        logging.error("❌ Failed to load %s: %s", url, e)
        return {}

    book_info = {}

    characteristics = soup.find('div', id='characteristics')
    if characteristics:
        rows = characteristics.find_all('div', class_='sc-eea45014-5 iqJpaS')
        for row in rows:
            label = row.find('div', class_='sc-eea45014-6 jdAhdS')
            value = row.find('div', class_='sc-eea45014-12 kJabMY') or row.find('span', class_='sc-eea45014-8 gWXAeK')
            if label and value:
                label_text = label.text.strip()
                value_text = value.text.strip()
                for key, field in FIELDS.items():
                    if label_text.lower() == key.lower():
                        book_info[field] = value_text

    title = soup.find('h1', class_='sc-72ae4fce-1 euXUYE')
    if title:
        book_info['title'] = title.text.strip()

    for field in FIELDS.values():
        book_info.setdefault(field, '')

    return book_info

def main():
    conn = sqlite3.connect(DB_PATH)
    init_raw_books_table(conn)
    cur = conn.cursor()

    cur.execute("SELECT id, url FROM raw_links WHERE processed = 0")
    links = cur.fetchall()
    logging.info("Found %d unprocessed links", len(links))

    for link_id, url in links:
        logging.info("🔗 Processing: %s", url)
        book_data = parse_book(url)

        if not book_data or not book_data.get('isbn') or not book_data.get('title'):
            logging.warning("⚠️ Skipped: missing required fields for %s", url)
            continue

        try:
            cur.execute("""
                INSERT INTO raw_books (
                    link_id, title, author, seria, publisher,
                    pages_count, cover_type, publication_year,
                    translator, book_language, isbn
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(isbn) DO UPDATE SET
                    link_id = excluded.link_id,
                    title = excluded.title,
                    author = excluded.author,
                    seria = excluded.seria,
                    publisher = excluded.publisher,
                    pages_count = excluded.pages_count,
                    cover_type = excluded.cover_type,
                    publication_year = excluded.publication_year,
                    translator = excluded.translator,
                    book_language = excluded.book_language
            """, (
                link_id,
                book_data['title'],
                book_data['author'],
                book_data['seria'],
                book_data['publisher'],
                int(book_data['pages_count']) if book_data['pages_count'].isdigit() else 0,
                book_data['cover_type'],
                int(book_data['publication_year']) if book_data['publication_year'].isdigit() else 0,
                book_data['translator'],
                book_data['book_language'],
                book_data['isbn']
            ))
        
            cur.execute("""
                UPDATE raw_links SET processed = 1, updated_at = ? WHERE id = ?
            """, (datetime.now(), link_id))
        
            conn.commit()
            logging.info("✅ Upserted: %s", book_data['title'])
        
        except Exception as e:
            logging.error("❌ Error while saving to database: %s", e)


        time.sleep(0.5)

    conn.close()
    logging.info("🎉 Done. All links have been processed.")

if __name__ == "__main__":
    main()

