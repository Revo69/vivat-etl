from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import sqlite3
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


base_url = "https://vivat.com.ua/category/khudozhni-knyhy/?sort=-pubdate"
all_links = set()
max_pages = 10

options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)

try:
    for page in range(1, max_pages + 1):
        # Корректно обновляем/добавляем параметр page в query-string
        parsed = urlparse(base_url)
        q = dict(parse_qsl(parsed.query))
        if page == 1:
            q.pop('page', None)  # первая страница — без page
        else:
            q['page'] = str(page)
        new_query = urlencode(q, doseq=True)
        url = urlunparse(parsed._replace(query=new_query))

        logging.info(f"Parsing page {page}: {url}")
        driver.get(url)
        time.sleep(1.0)  # Даем время на загрузку JS

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        link_elements = soup.find_all('a', class_='sc-d48af2da-1 ilVlZU title')

        if not link_elements:
            logging.warning("No more links found on page %s", page)
            break

        for link in link_elements:
            href = link.get('href')
            if not href:
                continue
            href = href.split('?')[0]  # Remove query parameters
            if href.startswith('/'):
                full_link = "https://vivat.com.ua" + href
            elif href.startswith('http'):
                full_link = href
            else:
                full_link = "https://vivat.com.ua/" + href
            all_links.add(full_link)

        time.sleep(2)  # Delay to avoid rate limiting
finally:
    driver.quit()

def save_links_to_db(links, db_path='books_links.sqlite3'):
    """Сохраняет список ссылок в SQLite.
    Перед вставкой проверяет наличие URL и вставляет только новые.
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                processed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        conn.commit()

        # Считаем текущее количество записей
        cur.execute("SELECT COUNT(*) FROM raw_links")
        before = cur.fetchone()[0]

        # Вставка с игнорированием дубликатов (если кто-то добавил параллельно)
        cur.executemany("INSERT OR IGNORE INTO raw_links (url) VALUES (?)", ((u,) for u in links))
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM raw_links")
        after = cur.fetchone()[0]

        logging.info("Saved %d new links to %s (total %d)", after - before, db_path, after)

    except Exception as e:
        logging.error("Error saving links to DB: %s", e)

    finally:
        conn.close()

# Сохраняем собранные ссылки
save_links_to_db(sorted(all_links))


