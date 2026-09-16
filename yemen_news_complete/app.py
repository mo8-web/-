# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
from scraper import scrape_latest_news
import sqlite3
import threading
import time

app = Flask(__name__)
DATABASE = "news.db"

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            published_at TEXT,
            image_url TEXT,
            source_url TEXT NOT NULL UNIQUE,
            category TEXT,
            source_name TEXT DEFAULT 'المصدر',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    db.close()

def get_news(limit=40, category=None):
    db = get_db()
    if category:
        rows = db.execute("SELECT * FROM news WHERE category = ? ORDER BY id DESC LIMIT ?", (category, limit)).fetchall()
    else:
        rows = db.execute("SELECT * FROM news ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    db.close()
    return rows

def refresh_news():
    try:
        scrape_latest_news()
    except Exception as e:
        print("خطأ في التحديث:", e)

def automatic_updater():
    while True:
        time.sleep(120)  # تحديث دوري فوري كل دقيقتين لمقاطعة الأخبار القديمة
        refresh_news()

@app.route("/")
def home():
    news = get_news(40)
    return render_template("index.html", news=news, slider=news[:5], breaking=news[:8], active_category=None)

@app.route("/category/<category>")
def category_page(category):
    news = get_news(40, category)
    return render_template("index.html", news=news, slider=news[:5], breaking=get_news(8), active_category=category)

@app.route("/article/<int:article_id>")
def article(article_id):
    db = get_db()
    item = db.execute("SELECT * FROM news WHERE id = ?", (article_id,)).fetchone()
    db.close()
    if item is None: return "الخبر غير موجود", 404

    from urllib.parse import quote
    base_url = request.host_url.rstrip('/')
    local_article_url = f"{base_url}/article/{article_id}"
    
    share_links = {
        "whatsapp": f"https://whatsapp.com{quote(item['title'])}%20{quote(local_article_url)}",
        "twitter": f"https://twitter.com{quote(item['title'])}&url={quote(local_article_url)}"
    }
    return render_template("article.html", article=item, latest=get_news(8), share_links=share_links, local_url=local_article_url)

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query: return render_template("search.html", results=[], query="")
    db = get_db()
    results = db.execute("SELECT * FROM news WHERE title LIKE ? OR content LIKE ? ORDER BY id DESC LIMIT 50", (f"%{query}%", f"%{query}%")).fetchall()
    db.close()
    return render_template("search.html", results=results, query=query)

@app.route("/refresh")
def manual_refresh():
    refresh_news()
    return '<html dir="rtl"><meta charset="utf-8"><body style="font-family:Arial;text-align:center;padding:60px"><h2>جاري السحب الفوري المحدث بالعربية...</h2><a href="/">العودة للرئيسية</a></body></html>'

if __name__ == "__main__":
    init_db()
    threading.Thread(target=refresh_news).start()
    threading.Thread(target=automatic_updater, daemon=True).start()
    app.run(debug=True)
