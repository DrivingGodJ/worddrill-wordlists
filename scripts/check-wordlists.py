#!/usr/bin/env python3
"""校验 WordDrill 公开词表仓库中的 index.json 与全部 wordlists/*.json。"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWED_TAGS = {"拼写", "只认"}
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def has_chinese(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text or ""))


def is_valid_fill_example(example: str, word: str) -> bool:
    if not example or not word:
        return False
    ex = example.strip()
    if not (5 <= len(ex.split()) <= 35 and len(ex) <= 240):
        return False
    if not re.search(r'[.!?]["”’\']?$', ex):
        return False
    if re.search(r"…|\.{3}|_{2,}|<[^>]+>", ex):
        return False
    return bool(re.search(rf"\b{re.escape(word)}\b", ex, re.IGNORECASE))


def main() -> int:
    errors: list[str] = []
    index_path = ROOT / "index.json"
    if not index_path.exists():
        print("ERROR: 缺少 index.json", file=sys.stderr)
        return 1

    index = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(index.get("wordlists"), list) or not index["wordlists"]:
        errors.append("index.json: wordlists 必须为非空数组")

    seen_deck_ids: set[str] = set()
    for item in index.get("wordlists", []):
        did = item.get("id")
        fpath = item.get("file")
        if not isinstance(did, str) or not ID_RE.match(did):
            errors.append(f"index.json: 非法词表 id={did!r}（仅允许小写字母、数字与连字符）")
            continue
        if did in seen_deck_ids:
            errors.append(f"index.json: 重复词表 id={did!r}")
        seen_deck_ids.add(did)

        full_path = ROOT / str(fpath or "")
        if not full_path.exists():
            errors.append(f"index.json: 词表文件不存在 {fpath}")
            continue

        payload = json.loads(full_path.read_text(encoding="utf-8"))
        words = payload.get("words")
        meta = payload.get("meta") or {}
        if not isinstance(words, list) or not words:
            errors.append(f"{fpath}: words 必须为非空数组")
            continue

        if item.get("count") != len(words):
            errors.append(f"{fpath}: index.json count={item.get('count')} 与实际词数 {len(words)} 不一致")
        if meta.get("count") is not None and meta.get("count") != len(words):
            errors.append(f"{fpath}: meta.count={meta.get('count')} 与实际词数 {len(words)} 不一致")

        seen_word_ids: set[str] = set()
        fill_ok = 0
        diff_ok = 0
        for idx, w in enumerate(words):
            if not isinstance(w, dict):
                errors.append(f"{fpath}[{idx}]: 词条不是对象")
                continue
            wid = w.get("id")
            word = w.get("word")
            meaning = w.get("meaning")
            tags = w.get("tags")
            if not isinstance(wid, str) or not wid.strip():
                errors.append(f"{fpath}[{idx}]: 缺少非空 id")
            elif wid in seen_word_ids:
                errors.append(f"{fpath}[{idx}]: 重复词条 id={wid!r}")
            else:
                seen_word_ids.add(wid)

            if not isinstance(word, str) or not word.strip():
                errors.append(f"{fpath}[{idx}]: 缺少非空 word")
            if not isinstance(meaning, str) or not has_chinese(meaning):
                errors.append(f"{fpath}[{idx}] ({wid}): meaning 必须包含中文释义")
            if not isinstance(tags, list) or not tags or not set(tags).issubset(ALLOWED_TAGS):
                errors.append(f"{fpath}[{idx}] ({wid}): tags 必须为 ['拼写'] 或 ['只认']，实际为 {tags!r}")

            if "difficulty" in w:
                d = w["difficulty"]
                if not (isinstance(d, int) and 1 <= d <= 5):
                    errors.append(f"{fpath}[{idx}] ({wid}): difficulty 须为 1-5 整数，实际为 {d!r}")
                else:
                    diff_ok += 1
            if "freq" in w:
                fr = w["freq"]
                if not (isinstance(fr, int) and fr > 0):
                    errors.append(f"{fpath}[{idx}] ({wid}): freq 须为正整数，实际为 {fr!r}")

            if is_valid_fill_example(w.get("example", ""), word or "") and has_chinese(w.get("exampleZh", "")):
                fill_ok += 1

        pct_fill = fill_ok * 100.0 / len(words)
        pct_diff = diff_ok * 100.0 / len(words)
        print(f"OK {fpath}: {len(words)} words | fill-ready={pct_fill:.1f}% | difficulty={pct_diff:.1f}%")

    dist_rel = index.get("distractors")
    if dist_rel:
        dp = ROOT / dist_rel
        if not dp.exists():
            errors.append(f"index.json: distractors 文件不存在 {dist_rel}")
        else:
            ddata = json.loads(dp.read_text(encoding="utf-8"))
            if not isinstance(ddata.get("words"), list) or not ddata["words"]:
                errors.append(f"{dist_rel}: words 必须为非空数组")
            else:
                print(f"OK {dist_rel}: {len(ddata['words'])} distractors")

    if errors:
        print(f"\n校验失败（共 {len(errors)} 项）：", file=sys.stderr)
        for e in errors[:30]:
            print("  -", e, file=sys.stderr)
        return 1

    print("\nAll wordlists passed validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
