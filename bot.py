import feedparser
import requests
import json
import os
from datetime import datetime

# === CONFIG ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Add in GitHub Secrets
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")      # Your channel ID
RSS_FEEDS = [
    "https://hitconsultant.net/feed/",
    "https://www.fiercehealthcare.com/rss/health%20%26%20tech/xml",
    "https://medtechintelligence.com/feed/",
    "https://www.digitalhealth.net/news/feed/",
    "https://news.google.com/rss/search?q=healthcare+technology+OR+health+tech+OR+medtech+OR+%22AI+in+healthcare%22&hl=en-US&gl=US&ceid=US:en",
    # Add your PubMed RSS here
]

SEEN_FILE = "seen.json"

# Load or create seen items (to avoid duplicates)
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE) as f:
        seen = set(json.load(f))
else:
    seen = set()

def send_to_telegram(title, link, summary=""):
    message = f"📰 **{title}**\n\n{summary}\n\n🔗 {link}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

new_items = 0
for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)
    for entry in feed.entries[:10]:  # Limit per feed
        item_id = entry.get("id") or entry.link
        if item_id not in seen:
            seen.add(item_id)
            summary = entry.get("summary", "")[:300] or entry.get("description", "")[:300]
            send_to_telegram(entry.title, entry.link, summary)
            new_items += 1

# Save updated seen list
with open(SEEN_FILE, "w") as f:
    json.dump(list(seen), f)

print(f"✅ Sent {new_items} new healthcare tech updates")
