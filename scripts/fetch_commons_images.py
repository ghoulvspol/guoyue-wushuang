#!/usr/bin/env python3
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'app/static/photos'
OUT.mkdir(parents=True, exist_ok=True)
ATTR = ROOT / 'data/image_attributions.json'

INSTRUMENT_QUERIES = {
    'guzheng': 'guzheng musical instrument',
    'pipa': 'pipa musical instrument',
    'erhu': 'erhu musical instrument',
    'yangqin': 'yangqin musical instrument',
    'dizi': 'dizi flute musical instrument',
    'suona': 'suona musical instrument',
    'guqin': 'guqin musical instrument',
    'zhongruan': 'ruan musical instrument Chinese lute',
    'sanxian': 'sanxian musical instrument',
    'konghou': 'konghou harp musical instrument',
    'sheng': 'sheng musical instrument',
    'xiao': 'xiao flute musical instrument',
    'xun': 'xun musical instrument',
    'hulusi': 'hulusi musical instrument',
    'matouqin': 'morin khuur musical instrument',
    'bianzhong': 'bianzhong bells',
    'paigu': 'paigu Chinese drums',
    'bo': 'Chinese cymbals musical instrument',
}

API = 'https://commons.wikimedia.org/w/api.php'
UA = 'GuoyueWushuang/1.0 (local educational app; contact: local)'

def clean_html(value):
    value = value or ''
    value = re.sub(r'<[^>]*>', '', value)
    return re.sub(r'\s+', ' ', value).strip()

def api(params):
    params = {'format': 'json', 'formatversion': '2', **params}
    req = urllib.request.Request(API + '?' + urllib.parse.urlencode(params), headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))

def search_files(query):
    data = api({
        'action': 'query',
        'generator': 'search',
        'gsrsearch': f'filetype:bitmap {query}',
        'gsrnamespace': '6',
        'gsrlimit': '12',
        'prop': 'imageinfo',
        'iiprop': 'url|mime|size|extmetadata',
        'iiurlwidth': '900',
    })
    return data.get('query', {}).get('pages', [])

def choose_image(pages):
    candidates = []
    for page in pages:
        info = (page.get('imageinfo') or [{}])[0]
        mime = info.get('mime', '')
        if not mime.startswith('image/') or mime == 'image/svg+xml':
            continue
        width = info.get('width') or 0
        height = info.get('height') or 0
        thumb = info.get('thumburl') or info.get('url')
        if not thumb or width < 240 or height < 180:
            continue
        title = page.get('title', '')
        bad = ['score', 'sheet', 'map', 'logo', 'icon', 'diagram', 'notation']
        if any(word in title.lower() for word in bad):
            continue
        candidates.append((width * height, page, info))
    if not candidates:
        return None
    candidates.sort(reverse=True, key=lambda item: item[0])
    return candidates[0][1], candidates[0][2]

def extension(mime):
    return '.jpg' if mime in {'image/jpeg', 'image/jpg'} else '.png'

records = []
if ATTR.exists():
    records = json.loads(ATTR.read_text())
seen = {r['id'] for r in records}
for key, query in INSTRUMENT_QUERIES.items():
    if key in seen and Path(ROOT / records[[r['id'] for r in records].index(key)]['path'].lstrip('/')).exists():
        print(f'Skip {key}')
        continue
    print(f'Fetching {key}: {query}')
    pages = search_files(query)
    selected = choose_image(pages)
    if not selected:
        print(f'  ! no image found')
        continue
    page, info = selected
    mime = info.get('mime', 'image/jpeg')
    ext = extension(mime)
    target = OUT / f'{key}{ext}'
    image_url = info.get('thumburl') or info.get('url')
    last_error = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(image_url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=60) as response:
                target.write_bytes(response.read())
            break
        except Exception as exc:
            last_error = exc
            wait = 5 + attempt * 8
            print(f'  retry in {wait}s after {exc}')
            time.sleep(wait)
    else:
        print(f'  ! failed download: {last_error}')
        continue
    meta = info.get('extmetadata') or {}
    record = {
        'id': key,
        'path': f'/static/photos/{target.name}',
        'title': page.get('title'),
        'artist': clean_html((meta.get('Artist') or {}).get('value')) or 'Wikimedia Commons contributor',
        'license': clean_html((meta.get('LicenseShortName') or {}).get('value')) or clean_html((meta.get('UsageTerms') or {}).get('value')),
        'credit': clean_html((meta.get('Credit') or {}).get('value')),
        'source': clean_html((meta.get('ObjectName') or {}).get('value')),
        'description_url': info.get('descriptionurl'),
        'width': info.get('thumbwidth') or info.get('width'),
        'height': info.get('thumbheight') or info.get('height'),
    }
    records.append(record)
    print(f'  -> {target.name} {record["license"]} {record["description_url"]}')
    ATTR.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
    time.sleep(2.0)

ATTR.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
print(f'Wrote {len(records)} records to {ATTR}')
