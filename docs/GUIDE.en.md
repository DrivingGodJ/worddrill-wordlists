[简体中文](GUIDE.zh-CN.md) | **English**

# Authoring & Submitting Qualified Wordlists

[Back to repository README](../README.en.md)

This guide explains how to build a clean wordlist JSON that loads reliably in WordDrill and unlocks **Independent Recall**, **Context Fill**, and **Difficulty-Aware Daily New Word Selection**.

---

## 1. File Naming & Top-Level Structure

- Path: `wordlists/<deck-id>.json`, where `<deck-id>` uses lowercase ASCII letters, digits, and hyphens (e.g. `toefl-core.json`, `gre-essential.json`, `cs-english.json`).
- Encoding: UTF-8 without BOM (minified JSON recommended to keep downloads fast).
- Top-level object requires `meta` and `words`:

```json
{
  "meta": {
    "id": "toefl-core",
    "name": "托福核心词汇（TOEFL）",
    "shortName": "托福词汇",
    "updated": "2026-11-27",
    "count": 3200,
    "source": "Verifiable open/public source name or repository URL"
  },
  "words": [ /* entry objects */ ]
}
```

---

## 2. Entry Schema (Required & Recommended)

| Field | Requirement | Type | Rules & Purpose |
| :--- | :--- | :--- | :--- |
| `id` | **Required** | `string` | Stable unique slug (`re.sub(r'[^a-z0-9]+', '-', word.lower()).strip('-')`). **No duplicates within a file.** Never rename existing IDs, as WordDrill ties user progress to `id`. |
| `word` | **Required** | `string` | Trimmed English headword or phrase without phonetics or notes. |
| `meaning` | **Required** | `string` | Concise Chinese meaning; separate multiple senses with `；`. |
| `tags` | **Required** | `string[]` | Training mode tag: **strictly `["拼写"]`** (recognition + spelling) or **`["只认"]`** (recognition only). |
| `pos` | **Strongly recommended** | `string` | Part of speech with trailing dot, joined by `/` (e.g. `"v."`, `"n./v."`, `"adj."`). Used to pick same-POS distractors. |
| `example` | **Strongly recommended** | `string` | Complete English sentence; unlocks **Context Fill** when quality gates pass. |
| `exampleZh` | **Strongly recommended** | `string` | Accurate Chinese translation matching `example`. |
| `difficulty` | **Recommended** | `1 \| 2 \| 3 \| 4 \| 5` | Difficulty tier (`1` easiest → `5` hardest) used by WordDrill's Balanced / Easy-First / Hard-First daily new-word selector. |
| `freq` | **Recommended** | `integer` | Positive frequency rank (lower = more common, e.g. from `en_50k.txt`), combined with `difficulty` into a 0–100 score. |
| `collocations` | Optional | `string[]` | 1–3 common collocations, e.g. `"phrase（中文）"`. |
| `phonetic` | Optional | `string` | IPA transcription without outer slashes (e.g. `"rɪˈzɪliənt"`). |

---

## 3. Quality Gates

### Context-Fill Example Rules
WordDrill enables **Context Fill** only for entries with clean, complete sentences:
- `5`–`35` words, total length ≤ `240` characters;
- Starts with a capital letter and ends with `.`, `!`, or `?`;
- No `...`, `…`, `__` blanks, or HTML tags;
- Contains `word` on whole-word boundaries (case-insensitive);
- Accompanied by a matching `exampleZh`.

### Frequency & Difficulty Tiers
Aligned with `scripts/build-wordlists.py` using `hermitdave/FrequencyWords` (`en_50k.txt`):
- `difficulty = 1`: rank `1 – 3,500`
- `difficulty = 2`: rank `3,501 – 10,000`
- `difficulty = 3`: rank `10,001 – 22,000`
- `difficulty = 4`: rank `22,001 – 36,000`
- `difficulty = 5`: rank `> 36,000` or rare/complex words

> Decks without `freq`/`difficulty` still work via WordDrill's shape-based fallback estimator, but supplying true rankings noticeably improves daily difficulty balance.

---

## 4. Registering in `index.json`

Append an entry to `wordlists` in root `index.json`:

```json
{
  "id": "toefl-core",
  "name": "托福核心词汇（TOEFL）",
  "shortName": "托福词汇",
  "tag": "默认拼写",
  "description": "托福高频核心词汇，含词性、中文释义、例句与难度分级。",
  "count": 3200,
  "file": "wordlists/toefl-core.json"
}
```

- Keep `tag` aligned with the deck's entries (`"默认拼写"` or `"默认只认"`).
- `count` must match `words.length` exactly.

---

## 5. Validation, Live Testing & PR Checklist

### 1. Run the Automated Validator

```bash
python3 scripts/check-wordlists.py
```

The validator checks JSON syntax, required fields, unique IDs, valid `tags`, `difficulty`/`freq` bounds, exact `count` consistency across `index.json` and `meta.count`, and reports context-fill example coverage.

### 2. Test Live Inside WordDrill
1. Push your branch to your public fork.
2. Open [WordDrill](https://drivinggodj.github.io/word-drill/) → **Wordbooks** → **+ Create Local Wordbook**.
3. Expand **Source Repository**, enter `your-username/worddrill-wordlists`, and click **Reload**.
4. Select your new deck, create a local wordbook, and test a short session plus the Word Library view.

### 3. Open a Pull Request
Include in your PR description:
- Deck name, target audience, and word count;
- Verifiable open/public source and license rationale;
- Passing output of `python3 scripts/check-wordlists.py`.
