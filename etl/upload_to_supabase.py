import os
import time
import logging
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from config import DB_PATH

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Logging setup
LOG_PATH = os.path.join("logs", "upload.log")
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def upload_book(record):
    payload = {
        "author": record["author"],
        "title": record["title"],
        "seria": record["seria"],
        "publisher": record["publisher"],
        "pages_count": record["pages_count"],
        "cover_type": record["cover_type"],
        "publication_year": record["publication_year"],
        "translator": record["translator"],
        "book_language": record["book_language"],
        "isbn": record["isbn"]
    }
    try:
        supabase.table("book_data").upsert(payload, on_conflict=["isbn"]).execute()
        return True
    except Exception as e:
        logging.error("❌ Failed to upload ISBN %s: %s", record["isbn"], e)
        return False

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM raw_books WHERE uploaded = 0")
    books = cur.fetchall()
    logging.info("Found %d books to upload", len(books))

    for book in books:
        logging.info("📤 Uploading: %s", book["title"])
        success = upload_book(book)
        if success:
            cur.execute("UPDATE raw_books SET uploaded = 1 WHERE id = ?", (book["id"],))
            conn.commit()
            logging.info("✅ Uploaded: %s", book["title"])
        else:
            logging.warning("⚠️ Skipped: %s", book["title"])
        time.sleep(0.5)

    conn.close()
    logging.info("🎉 Done. All books uploaded.")

if __name__ == "__main__":
    main()

