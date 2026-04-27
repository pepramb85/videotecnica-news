#!/usr/bin/env python3
"""
fetch_news.py - Scarica RSS da DDay.it e HDblog.it, li unisce in news.json
Per: La VIDEOTECNICA - Portale Interno
"""

import feedparser
import json
import sys
import re
from datetime import datetime, timezone
from html import unescape

# Fonti RSS da aggregare
SOURCES = [
    {
        "name": "DDay.it",
        "url": "https://www.dday.it/rss",
        "color": "#E63946",
    },
    {
        "name": "HDblog.it",
        "url": "https://www.hdblog.it/feed/",
        "color": "#0066CC",
    },
]

MAX_PER_SOURCE = 10  # massimo articoli per fonte
MAX_TOTAL = 30       # massimo articoli totali nel JSON
EXCERPT_LEN = 180    # lunghezza riassunto in caratteri


def clean_html(text):
    """Rimuove tag HTML e decodifica entità."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def truncate(text, max_len):
    if len(text) <= max_len:
        return text
    cut = text[:max_len].rsplit(' ', 1)[0]
    return cut + '…'


def extract_image(entry):
    """Cerca un'immagine principale nell'entry RSS."""
    # 1. media:thumbnail / media:content
    if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
        url = entry.media_thumbnail[0].get('url')
        if url:
            return url
    if hasattr(entry, 'media_content') and entry.media_content:
        url = entry.media_content[0].get('url')
        if url:
            return url
    # 2. enclosure
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            t = enc.get('type', '')
            if t.startswith('image/'):
                return enc.get('href') or enc.get('url')
    # 3. <img> nel contenuto
    content = ''
    if hasattr(entry, 'content') and entry.content:
        content = entry.content[0].get('value', '')
    elif hasattr(entry, 'summary'):
        content = entry.summary
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    if m:
        return m.group(1)
    return None


def parse_feed(source):
    """Scarica e parsa un singolo feed."""
    print(f"→ Scarico {source['name']} da {source['url']}", flush=True)
    try:
        d = feedparser.parse(source['url'])
        if d.bozo and not d.entries:
            print(f"  ⚠ Errore parsing: {d.bozo_exception}", flush=True)
            return []
        items = []
        for entry in d.entries[:MAX_PER_SOURCE]:
            title = clean_html(entry.get('title', '')).strip()
            link = entry.get('link', '').strip()
            if not title or not link:
                continue
            # Data pubblicazione
            pub_struct = entry.get('published_parsed') or entry.get('updated_parsed')
            if pub_struct:
                pub_dt = datetime(*pub_struct[:6], tzinfo=timezone.utc)
                pub_iso = pub_dt.isoformat()
            else:
                pub_iso = datetime.now(timezone.utc).isoformat()
            # Riassunto
            summary_raw = entry.get('summary', '')
            excerpt = truncate(clean_html(summary_raw), EXCERPT_LEN)
            # Immagine
            image = extract_image(entry)
            items.append({
                'title': title,
                'link': link,
                'excerpt': excerpt,
                'image': image,
                'publishedAt': pub_iso,
                'source': source['name'],
                'sourceColor': source['color'],
            })
        print(f"  ✓ {len(items)} articoli", flush=True)
        return items
    except Exception as e:
        print(f"  ✗ Errore: {e}", flush=True)
        return []


def main():
    all_items = []
    for src in SOURCES:
        all_items.extend(parse_feed(src))

    # Ordina per data, dal più recente
    all_items.sort(key=lambda x: x['publishedAt'], reverse=True)
    all_items = all_items[:MAX_TOTAL]

    output = {
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'count': len(all_items),
        'items': all_items,
    }

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ news.json scritto: {len(all_items)} articoli totali", flush=True)
    if not all_items:
        print("⚠ Nessun articolo. Esco con codice 1.", flush=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
