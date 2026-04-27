#!/usr/bin/env python3
"""
fetch_news.py - Scarica RSS da DDay.it, HDblog.it, Tom's Hardware Italia
e li unisce in news.json
Per: La VIDEOTECNICA - Portale Interno

Per ogni fonte si tentano più URL candidati: il primo che risponde con
articoli viene usato. Lo script logga quali URL funzionano per facilitare
il debug.
"""

import feedparser
import json
import sys
import re
from datetime import datetime, timezone
from html import unescape

# Fonti RSS — per ogni fonte si possono mettere più URL candidati,
# il primo che risponde con articoli viene usato.
SOURCES = [
    {
        "name": "DDay.it",
        "color": "#E63946",
        "candidates": [
            "https://www.dday.it/rss",
            "https://www.dday.it/feed",
            "https://www.dday.it/rss.xml",
            "https://www.dday.it/feed.xml",
        ],
    },
    {
        "name": "HDblog.it",
        "color": "#0066CC",
        "candidates": [
            "https://www.hdblog.it/feed/",
            "https://www.hdblog.it/feed",
        ],
    },
    {
        "name": "Tom's Hardware",
        "color": "#9B2D2D",
        "candidates": [
            "https://www.tomshw.it/feed",
            "https://www.tomshw.it/feed/",
            "https://www.tomshw.it/rss_news.xml",
            "https://www.tomshw.it/feed-rss",
        ],
    },
]

MAX_PER_SOURCE = 10  # massimo articoli per fonte
MAX_TOTAL = 30       # massimo articoli totali nel JSON
EXCERPT_LEN = 180    # lunghezza riassunto in caratteri
USER_AGENT = "Mozilla/5.0 (compatible; VideotecnicaNewsBot/1.0; +https://lavideotecnica-af7de.web.app)"


def clean_html(text):
    """Rimuove tag HTML e decodifica entita'."""
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
    if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
        url = entry.media_thumbnail[0].get('url')
        if url:
            return url
    if hasattr(entry, 'media_content') and entry.media_content:
        url = entry.media_content[0].get('url')
        if url:
            return url
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            t = enc.get('type', '')
            if t.startswith('image/'):
                return enc.get('href') or enc.get('url')
    content = ''
    if hasattr(entry, 'content') and entry.content:
        content = entry.content[0].get('value', '')
    elif hasattr(entry, 'summary'):
        content = entry.summary
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    if m:
        return m.group(1)
    return None


def try_url(url):
    """Prova un singolo URL e restituisce (entries, error_str)."""
    try:
        d = feedparser.parse(url, agent=USER_AGENT, request_headers={'User-Agent': USER_AGENT})
        status = getattr(d, 'status', None)
        if status and status >= 400:
            return [], f"HTTP {status}"
        entries = d.entries or []
        if not entries:
            err = ""
            if d.bozo and d.bozo_exception:
                err = f"parse error: {d.bozo_exception}"
            else:
                err = "nessun articolo"
            return [], err
        return entries, None
    except Exception as e:
        return [], f"eccezione: {e}"


def parse_feed(source):
    """Per una fonte, prova i suoi URL candidati e parsa il primo che risponde."""
    print(f"\n-> Fonte: {source['name']}", flush=True)
    chosen_entries = None
    chosen_url = None
    for url in source['candidates']:
        print(f"   prova: {url}", flush=True)
        entries, err = try_url(url)
        if entries:
            chosen_entries = entries
            chosen_url = url
            print(f"   OK funzionante ({len(entries)} articoli grezzi)", flush=True)
            break
        else:
            print(f"   X scartato ({err})", flush=True)

    if not chosen_entries:
        print(f"   ! nessun URL ha risposto per {source['name']}, salto la fonte", flush=True)
        return []

    items = []
    for entry in chosen_entries[:MAX_PER_SOURCE]:
        title = clean_html(entry.get('title', '')).strip()
        link = entry.get('link', '').strip()
        if not title or not link:
            continue
        pub_struct = entry.get('published_parsed') or entry.get('updated_parsed')
        if pub_struct:
            pub_dt = datetime(*pub_struct[:6], tzinfo=timezone.utc)
            pub_iso = pub_dt.isoformat()
        else:
            pub_iso = datetime.now(timezone.utc).isoformat()
        summary_raw = entry.get('summary', '')
        excerpt = truncate(clean_html(summary_raw), EXCERPT_LEN)
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
    print(f"   -> {len(items)} articoli validi (URL usato: {chosen_url})", flush=True)
    return items


def main():
    all_items = []
    sources_ok = 0
    for src in SOURCES:
        items = parse_feed(src)
        if items:
            sources_ok += 1
            all_items.extend(items)

    all_items.sort(key=lambda x: x['publishedAt'], reverse=True)
    all_items = all_items[:MAX_TOTAL]

    output = {
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'count': len(all_items),
        'sourcesOk': sources_ok,
        'sourcesTotal': len(SOURCES),
        'items': all_items,
    }

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}", flush=True)
    print(f"news.json scritto", flush=True)
    print(f"  Articoli totali: {len(all_items)}", flush=True)
    print(f"  Fonti funzionanti: {sources_ok}/{len(SOURCES)}", flush=True)

    if not all_items:
        print("Nessun articolo da nessuna fonte. Esco con codice 1.", flush=True)
        sys.exit(1)

    if sources_ok < len(SOURCES):
        print(f"Alcune fonti non hanno risposto, ma {sources_ok} si. Continuo.", flush=True)


if __name__ == '__main__':
    main()
