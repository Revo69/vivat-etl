# 📚 Vivat ETL

An automated ETL pipeline for collecting new book links from [vivat.com.ua](https://vivat.com.ua), storing them in SQLite, and preparing them for metadata parsing.

---

## 🚀 Features

- Daily scraping of new book URLs
- Storage in SQLite (`raw_links` table)
- Flags processed links with `processed = 1`
- Automatically sets `updated_at = CURRENT_TIMESTAMP`
- Runs on schedule or manually via GitHub Actions

---

## 🧱 Project Structure

```
vivat-etl/
├── .github/workflows/
│   └── etl.yml              # GitHub Actions workflow
├── etl/
│   └── parser.py            # Main scraping script
├── db/
│   └── books_links.sqlite3  # SQLite database
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## ⚙️ Local Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the parser:
   ```bash
   python etl/parser.py
   ```

---

## 🗃️ SQLite Table Schema

```sql
CREATE TABLE IF NOT EXISTS raw_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    processed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## 🕰️ GitHub Actions Automation

The workflow runs:

- ⏰ Daily at 6:00 AM UTC (`cron`)
- 🧑‍💻 Manually via GitHub interface (`workflow_dispatch`)

Example trigger configuration:

```yaml
on:
  schedule:
    - cron: "0 6 * * *"
  workflow_dispatch:
```

Includes auto-commit logic to push updated SQLite DB only if changes are detected.

---

## 📌 Future Plans

- Parse book metadata (author, title, ISBN, etc.)
- Upload structured data to Supabase or PostgreSQL
- Add progress tracking and visual dashboards
- Notifications for newly added books

---

## 👤 Author

Developed and maintained by [Sergey](https://github.com/Revo69) — passionate about Data Engineering and Computer Vision.

---

## 📬 Contributions

Pull requests are welcome. For major changes, please open an issue first to discuss what you’d like to change.

---

## 🛡️ License

MIT License — feel free to use, modify, and share.
```
