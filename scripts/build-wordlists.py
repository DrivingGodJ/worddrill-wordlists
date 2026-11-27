#!/usr/bin/env python3
"""从 kajweb/dict 构建 WordDrill 公开词表仓库（CET-4、CET-6、IELTS + 干扰项池）。"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / '.cache-dict'
WORDLISTS_DIR = ROOT / 'wordlists'
DICT_REPO = 'kajweb/dict'
FREQ_REPO = 'hermitdave/FrequencyWords'
FREQ_PATH = 'content/2018/en/en_50k.txt'
TODAY = datetime.now(timezone.utc).strftime('%Y-%m-%d')

BOOKS = [
    {
        'id': 'cet4',
        'name': '大学英语四级（CET-4）',
        'shortName': '四级词汇',
        'tag': '拼写',
        'catalogTag': '默认拼写',
        'description': '大学英语四级核心与高频词汇，含词性、中文释义、例句与搭配。',
        'pattern': r'.*CET4.*\.(zip)$',
        'file': 'wordlists/cet4.json',
    },
    {
        'id': 'cet6',
        'name': '大学英语六级（CET-6）',
        'shortName': '六级词汇',
        'tag': '只认',
        'catalogTag': '默认只认',
        'description': '大学英语六级核心与高频词汇，含词性、中文释义、例句与搭配。',
        'pattern': r'.*CET6.*\.(zip)$',
        'file': 'wordlists/cet6.json',
    },
    {
        'id': 'ielts',
        'name': '雅思核心词汇（IELTS）',
        'shortName': '雅思词汇',
        'tag': '拼写',
        'catalogTag': '默认拼写',
        'description': '雅思高频核心词汇，含词性、中文释义、例句与搭配。',
        'pattern': r'.*IELTS.*\.(zip)$',
        'file': 'wordlists/ielts.json',
    },
]


def gh(endpoint: str) -> str:
    p = subprocess.run(['gh', 'api', endpoint], capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'GitHub API 失败：{p.stderr.strip()[:300]}')
    return p.stdout


def chinese(text: str) -> bool:
    return bool(re.search(r'[\u4e00-\u9fff]', text or ''))


def contains_head(text: str, head: str) -> bool:
    return bool(re.search(rf'(?<![a-z]){re.escape(head)}(?![a-z])', text, re.IGNORECASE))


def complete_sentence(text: str, head: str) -> bool:
    return (
        5 <= len(text.split()) <= 35
        and len(text) <= 240
        and bool(re.match(r'^["“\(]?[A-Z]', text))
        and bool(re.search(r'[.!?]["”\)]?$', text))
        and not re.search(r'\.{2,}|…|_{2,}|<[^>]+>', text)
        and contains_head(text, head)
    )


def download_books(index_items: list[dict], pattern: str) -> list[Path]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    wanted = [it for it in index_items if re.match(pattern, it['name'], re.IGNORECASE)]
    if not wanted:
        sys.exit(f'没有匹配 {pattern} 的词书')
    paths = []
    for it in sorted(wanted, key=lambda x: x['name']):
        dest = CACHE_DIR / it['name']
        def matches(raw: bytes) -> bool:
            return hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == it['sha']
        if not dest.exists() or not matches(dest.read_bytes()):
            print(f"下载 {it['name']}...")
            blob = json.loads(gh(f"repos/{DICT_REPO}/git/blobs/{it['sha']}"))
            raw = base64.b64decode(blob['content'])
            if not matches(raw):
                sys.exit(f"校验失败：{it['name']}")
            dest.write_bytes(raw)
        paths.append(dest)
    return paths


def parse_zip(path: Path) -> list[dict]:
    rows = []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.endswith('.json'):
                for line in z.read(name).decode('utf-8').splitlines():
                    if line.strip():
                        rows.append(json.loads(line))
    return rows


def load_freq_ranks() -> dict[str, int]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / 'en-freq-50k.txt'
    if not path.exists():
        print('下载词频表 en_50k.txt...')
        blob = json.loads(gh(f'repos/{FREQ_REPO}/contents/{FREQ_PATH}'))
        path.write_bytes(base64.b64decode(blob['content']))
    ranks = {}
    for i, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        parts = line.split()
        if parts:
            w = parts[0].lower()
            if w not in ranks:
                ranks[w] = i
    return ranks


def compute_freq_and_difficulty(head: str, meaning: str, freq_ranks: dict[str, int]) -> tuple[int | None, int]:
    low = head.lower().strip()
    rank = freq_ranks.get(low)
    if rank is None and low.endswith('ly'):
        candidates = [r for r in (freq_ranks.get(low[:-2]), freq_ranks.get(low[:-3] + 'y')) if r is not None]
        if candidates:
            rank = min(candidates)
    if rank is not None:
        if rank <= 3500:
            diff = 1
        elif rank <= 10000:
            diff = 2
        elif rank <= 22000:
            diff = 3
        elif rank <= 36000:
            diff = 4
        else:
            diff = 5
        return rank, diff

    # 外词频表缺失时（多词短语或生僻词），按长度与义项复杂度做平滑分级
    letters = len(re.sub(r'[^a-z]', '', low))
    senses = len([s for s in re.split(r'[；;]', meaning) if s.strip()])
    if ' ' in low or '-' in low:
        diff = 3 if letters <= 12 else 4
    elif letters <= 6 and senses <= 2:
        diff = 3
    elif letters <= 9:
        diff = 4
    else:
        diff = 5
    return None, diff


def to_entry(raw: dict, tag: str, freq_ranks: dict[str, int]) -> tuple[int, dict] | None:
    head = (raw.get('headWord') or '').strip()
    if not head:
        return None
    wid = re.sub(r'[^a-z0-9]+', '-', head.lower()).strip('-')
    if not wid:
        return None

    c = raw.get('content', {}).get('word', {}).get('content', {})
    trans = c.get('trans') or []
    meaning = '；'.join(dict.fromkeys(
        t.get('tranCn', '').strip() for t in trans if t.get('tranCn', '').strip()
    ))
    if not chinese(meaning):
        return None

    pos = '/'.join(dict.fromkeys(
        p.strip().rstrip('.') + '.'
        for t in trans
        for p in re.split(r'&|/', t.get('pos', ''))
        if p.strip()
    ))

    sentences = c.get('sentence', {}).get('sentences', []) or []
    good_sents = [
        s for s in sentences
        if complete_sentence(s.get('sContent', '').strip(), head) and chinese(s.get('sCn', ''))
    ]
    any_sents = [
        s for s in sentences
        if s.get('sContent', '').strip() and chinese(s.get('sCn', ''))
    ]
    picked_sent = min(good_sents, key=lambda s: len(s['sContent'])) if good_sents else (
        min(any_sents, key=lambda s: len(s['sContent'])) if any_sents else None
    )

    phrases = [
        f"{p['pContent'].strip()}（{p['pCn'].strip()}）"
        for p in c.get('phrase', {}).get('phrases', []) or []
        if p.get('pContent') and chinese(p.get('pCn', '')) and contains_head(p['pContent'], head)
    ][:3]
    phonetic = (c.get('ukphone') or c.get('usphone') or '').strip()

    freq_rank, diff = compute_freq_and_difficulty(head, meaning, freq_ranks)
    entry = {
        'id': wid,
        'word': head,
        'pos': pos,
        'meaning': meaning,
        'example': picked_sent['sContent'].strip() if picked_sent else '',
        'exampleZh': picked_sent['sCn'].strip() if picked_sent else '',
        'tags': [tag],
        'difficulty': diff,
    }
    if freq_rank is not None:
        entry['freq'] = freq_rank
    if phrases:
        entry['collocations'] = phrases
    if phonetic:
        entry['phonetic'] = phonetic

    quality = (
        (10 if good_sents else (3 if any_sents else 0))
        + (2 if pos else 0)
        + min(2, len(phrases))
        + (1 if phonetic else 0)
    )
    return quality, entry


def main() -> None:
    WORDLISTS_DIR.mkdir(parents=True, exist_ok=True)
    freq_ranks = load_freq_ranks()
    index_items = json.loads(gh(f'repos/{DICT_REPO}/contents/book'))
    catalog = []
    distractor_pool = {}

    for spec in BOOKS:
        paths = download_books(index_items, spec['pattern'])
        best: dict[str, tuple[int, dict]] = {}
        for p in paths:
            for raw in parse_zip(p):
                res = to_entry(raw, spec['tag'], freq_ranks)
                if not res:
                    continue
                q, entry = res
                prev = best.get(entry['id'])
                if prev is None or q > prev[0]:
                    best[entry['id']] = (q, entry)

        words = sorted((v[1] for v in best.values()), key=lambda x: x['id'])
        out_path = ROOT / spec['file']
        payload = {
            'meta': {
                'id': spec['id'],
                'name': spec['name'],
                'shortName': spec['shortName'],
                'updated': TODAY,
                'count': len(words),
                'source': DICT_REPO,
            },
            'words': words,
        }
        out_path.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        print(f"{spec['shortName']}: {len(words)} words -> {spec['file']} ({out_path.stat().st_size // 1024} KB)")

        catalog.append({
            'id': spec['id'],
            'name': spec['name'],
            'shortName': spec['shortName'],
            'tag': spec['catalogTag'],
            'description': spec['description'],
            'count': len(words),
            'file': spec['file'],
        })

        for w in words:
            if w['pos'] and len(w['meaning']) <= 36 and w['id'] not in distractor_pool:
                distractor_pool[w['id']] = {'w': w['word'], 'pos': w['pos'], 'meaning': w['meaning']}

    # Pick balanced distractors across parts of speech (up to 900)
    by_pos: dict[str, list[dict]] = {}
    for d in distractor_pool.values():
        k = d['pos'].split('/')[0].strip()
        by_pos.setdefault(k, []).append(d)
    selected_distractors = []
    for k in ['n.', 'v.', 'vt.', 'vi.', 'adj.', 'adv.']:
        selected_distractors.extend(by_pos.get(k, [])[:200])
    seen_w = {d['w'] for d in selected_distractors}
    for d in distractor_pool.values():
        if len(selected_distractors) >= 900:
            break
        if d['w'] not in seen_w:
            selected_distractors.append(d)
            seen_w.add(d['w'])

    dist_path = WORDLISTS_DIR / 'distractors.json'
    dist_path.write_text(
        json.dumps({'words': selected_distractors[:900]}, ensure_ascii=False, separators=(',', ':')),
        encoding='utf-8',
    )
    print(f"distractors: {len(selected_distractors[:900])} entries -> wordlists/distractors.json")

    index_payload = {
        'version': 1,
        'updated': TODAY,
        'distractors': 'wordlists/distractors.json',
        'wordlists': catalog,
    }
    (ROOT / 'index.json').write_text(json.dumps(index_payload, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
