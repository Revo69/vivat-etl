# 📚 Vivat ETL

An automated ETL pipeline for collecting book links and metadata from [vivat.com.ua](https://vivat.com.ua), storing them in SQLite, and uploading structured data to Supabase.

---

## 🚀 Features

- Daily scraping of new book URLs
- Metadata extraction (title, author, ISBN, etc.)
- Storage in SQLite (`raw_links`, `raw_books`)
- Upload to Supabase via secure API
- GitHub Actions automation with logging and artifact export
- Secrets managed via GitHub for security

---

## 🧱 Project Structure

```
vivat-etl/
├── .github/workflows/
│   └── etl.yml              # GitHub Actions workflow
├── etl/
│   ├── parser.py            # Collects book links
│   ├── parse_books.py       # Extracts book metadata
│   ├── upload_to_supabase.py# Uploads data to Supabase
│   ├── config.py            # Centralized paths and settings
├── db/
│   └── books_links.sqlite3  # SQLite database
├── logs/
│   ├── parser.log           # Link scraping logs
│   ├── parse_books.log      # Metadata parsing logs
│   └── upload.log           # Supabase upload logs
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## ⚙️ Local Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create `.env` file in project root:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-service-role-key
   ```

3. Run the pipeline manually:
   ```bash
   python etl/parser.py
   python etl/parse_books.py
   python etl/upload_to_supabase.py
   ```

---

## 🗃️ SQLite Table Schemas

### `raw_links`

```sql
CREATE TABLE IF NOT EXISTS raw_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    processed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

### `raw_books`

```sql
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
);
```

---

## 🕰️ GitHub Actions Automation

The workflow runs:

- ⏰ Daily at 6:00 AM UTC (`cron`)
- 🧑‍💻 Manually via GitHub interface (`workflow_dispatch`)

It performs:

- Link scraping (`parser.py`)
- Metadata parsing (`parse_books.py`)
- Upload to Supabase (`upload_to_supabase.py`)
- Commits updated SQLite DB
- Uploads logs as artifacts for inspection

### Secrets used:

- `SUPABASE_URL`
- `SUPABASE_KEY`

Stored securely via **Settings → Secrets → Actions**.

---

## 📎 Logs & Artifacts

After each run, logs from `logs/` are uploaded as artifacts:

- `parser.log`
- `parse_books.log`
- `upload.log`

You can download them from the **Artifacts** section of each workflow run.

---

## 📌 Future Plans

- Add data quality checks before upload
- Enable concurrent backfills for historical data
- Visualize upload progress and metrics
- Integrate with dashboards or BI tools

---

## 👤 Author

Developed and maintained by [Serghei](https://github.com/Revo69) — passionate about Data Engineering, Computer Vision, and clean architecture.

---

## 🛡️ License

MIT License — feel free to use, modify, and share.
