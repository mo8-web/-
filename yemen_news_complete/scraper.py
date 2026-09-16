# -*- coding: utf-8 -*-
"""
برنامج سحب الأخبار الشامل والمكثف - مخصص لأخبار اليمن فقط.
المصادر: وكالة سبأ الشرعية، سبتمبر نت، والصحوة نت (تم تحديث الرابط الجديد).
"""

import json
import re
import sqlite3
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

DATABASE = "news.db"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "ar,en;q=0.8",
}

# المصادر والروابط الدقيقة للأقسام الجديدة - مع تحديث رابط الصحوة نت الجديد ليعمل بنجاح
YEMEN_SOURCES = {
    "وكالة سبأ الشرعية": {
        "سياسة": "https://sabanew.net",
        "اقتصاد": "https://sabanew.net",
        "رياضة": "https://sabanew.net"
    },
    "سبتمبر نت": {
        "سياسة": "https://26sepnews.net",
        "اقتصاد": "https://26sepnews.net",
        "رياضة": "https://26sepnews.net"
    },
    "الصحوة نت": {
        "سياسة": "https://alsahwa-yemen.net/album-67",
        "اقتصاد": "https://alsahwa-yemen.net/album-115",
        "رياضة": "https://alsahwa-yemen.net/album-115"
    }
}

def clean_text(text):
    if not text: return ""
    return re.sub(r"\s+", " ", text).strip()

def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"⚠️ تعذر الاتصال بالرابط {url}: {e}")
        return None

def is_strictly_yemen(title, content):
    """نظام الفلترة لضمان بقاء المحتوى ضمن الشأن اليمني."""
    yemen_keywords = ["اليمن", "يمني", "صنعاء", "عدن", "تعز", "مأرب", "حضرموت", "الحديدة", "شبوة", "أبين", "لحج", "الضالع", "الشرعية", "الحكومة", "الجيش"]
    text_to_check = (title + " " + content).lower()
    return any(keyword in text_to_check for keyword in yemen_keywords)

def extract_article_details(url, source_name, category):
    soup = get_soup(url)
    if not soup: return None
    
    title_tag = soup.find("h1") or soup.find("meta", attrs={"property": "og:title"})
    title = title_tag.get_text() if title_tag and not title_tag.get("content") else (title_tag.get("content") if title_tag else "")
    title = clean_text(title)
    
    if not title: return None
    
    img_tag = soup.find("meta", attrs={"property": "og:image"}) or soup.find("article img")
    image_url = img_tag.get("content") if img_tag and img_tag.get("content") else (img_tag.get("src") if img_tag else "")
    if image_url:
        image_url = urljoin(url, image_url)
    
    paragraphs = soup.select("article p, .entry-content p, .post-content p, .view-content p, .text-post p")
    content_text = "\n\n".join([clean_text(p.get_text()) for p in paragraphs if len(p.get_text()) > 15])
    
    if not is_strictly_yemen(title, content_text):
        return None
        
    return {
        "title": title,
        "content": content_text,
        "published_at": "",
        "image_url": image_url,
        "source_url": url,
        "category": category,
        "source_name": source_name
    }

def save_article(article):
    """حفظ مشروط يمنع التكرار نهائياً."""
    if not article: return False
    db = sqlite3.connect(DATABASE)
    try:
        db.execute("""
            INSERT OR IGNORE INTO news (title, content, published_at, image_url, source_url, category, source_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (article["title"], article["content"], article["published_at"], article["image_url"], article["source_url"], article["category"], article["source_name"]))
        inserted = db.total_changes > 0
        db.commit()
        return inserted
    except Exception as e:
        print(f"❌ خطأ في الحفظ: {e}")
        return False
    finally:
        db.close()

def scrape_latest_news():
    print("🚀 بدء سحب شامل ومكثف لجميع الأخبار اليمنية الجديدة...")
    added_count = 0
    
    for source_name, categories in YEMEN_SOURCES.items():
        for category_name, cat_url in categories.items():
            print(f"🔄 جلب [{category_name}] من موقع [{source_name}]...")
            soup = get_soup(cat_url)
            if not soup: continue
            
            links = set()
            for anchor in soup.select("a[href]"):
                href = anchor.get("href", "").strip()
                full_url = urljoin(cat_url, href)
                
                if urlparse(full_url).netloc == urlparse(cat_url).netloc and len(href) > 12:
                    links.add(full_url)
            
            # فحص وتجميع حتى 20 رابطاً من كل قسم لضمان سحب كل المحتوى
            for link in list(links)[:20]:
                try:
                    article = extract_article_details(link, source_name, category_name)
                    if article and save_article(article):
                        added_count += 1
                        print(f"✅ تم حفظ خبر جديد: {article['title']}")
                except Exception:
                    pass
                    
    print(f"🏁 انتهى السحب الشامل. إجمالي الأخبار المضافة حالياً: {added_count}")
    return added_count
