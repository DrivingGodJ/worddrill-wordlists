[简体中文](README.md) | **English**

# WordDrill Public Wordlists

Ready-to-use vocabulary decks for [WordDrill](https://drivinggodj.github.io/word-drill/). Select one or merge multiple decks directly inside WordDrill (**Wordbooks → Create Local Wordbook**), or submit new community decks via Pull Request.

[Open WordDrill](https://drivinggodj.github.io/word-drill/) · [Authoring & Contribution Guide](docs/GUIDE.en.md) · [Main App Repo](https://github.com/DrivingGodJ/word-drill)

## Included Wordlists

| Deck | File | Default Tag | Words | Notes |
| :--- | :--- | :--- | ---: | :--- |
| CET-4 (`大学英语四级`) | `wordlists/cet4.json` | Default Spelling | 4,544 | Core & high-frequency CET-4 words with phonetics, examples, collocations, freq & difficulty |
| CET-6 (`大学英语六级`) | `wordlists/cet6.json` | Default Recognize | 3,992 | Core CET-6 reading vocabulary (spelling mode remains customizable in WordDrill) |
| IELTS (`雅思核心词汇`) | `wordlists/ielts.json` | Default Spelling | 5,275 | High-frequency IELTS words with complete examples, collocations, freq & difficulty |

This repository also ships `wordlists/distractors.json` (out-of-deck distractor pool for recognition quizzes) and `index.json` (catalog manifest fetched by WordDrill). When merging multiple decks, WordDrill deduplicates by `id` and preserves spelling requirements if any selected deck marks a word as `拼写`.

## Submit a New Wordlist in 3 Steps

Pull Requests for TOEFL, GRE, Postgraduate English, CS/Technical English, or other openly licensed decks are welcome:

1. **Prepare the deck JSON**: Save a UTF-8 JSON file at `wordlists/<id>.json`. Every entry requires a stable unique `id`, `word`, `meaning`, and `tags` (`["拼写"]` or `["只认"]`). Include `pos`, complete `example`/`exampleZh`, `difficulty` (`1`–`5`), and `freq` rank so WordDrill's **Context Fill** and **Difficulty-Aware New Words** work at full accuracy.
2. **Register in `index.json`**: Add a catalog entry under `wordlists` with matching `id`, `file`, and exact `count` equal to `words.length`.
3. **Validate, test, and open a PR**: Run the bundled validator below, test loading your fork inside WordDrill (**Create Local Wordbook → Source Repository** set to `your-user/worddrill-wordlists`), then submit a Pull Request.

```bash
python3 scripts/check-wordlists.py
```

## Entry Format Snapshot

```json
{
  "meta": {
    "id": "cet4",
    "name": "大学英语四级（CET-4）",
    "shortName": "四级词汇",
    "updated": "2026-11-27",
    "count": 4544,
    "source": "kajweb/dict"
  },
  "words": [
    {
      "id": "abandon",
      "word": "abandon",
      "pos": "v.",
      "meaning": "丢弃；放弃，抛弃",
      "example": "How could she abandon her own child?",
      "exampleZh": "她怎么能抛弃自己的孩子？",
      "tags": ["拼写"],
      "difficulty": 2,
      "freq": 4036,
      "collocations": ["with abandon（恣意地，放纵地）"],
      "phonetic": "ə'bænd(ə)n"
    }
  ]
}
```

## Explore Further

| Topic | Link |
| :--- | :--- |
| Full schema rules, example quality gates, difficulty tiers & PR checklist | [Authoring & Contribution Guide](docs/GUIDE.en.md) |
| Automated deck builder from open dictionaries & frequency lists | [build-wordlists.py](scripts/build-wordlists.py) |
| One-command validator for `index.json` and all decks | [check-wordlists.py](scripts/check-wordlists.py) |
| Main WordDrill trainer & learning algorithm | [WordDrill Repository](https://github.com/DrivingGodJ/word-drill) |
| Deck requests & bug reports | [Issues](https://github.com/DrivingGodJ/worddrill-wordlists/issues) |

**Sources & Licensing**: Current CET-4, CET-6, and IELTS entries are compiled from [kajweb/dict](https://github.com/kajweb/dict), with frequency rankings derived from [hermitdave/FrequencyWords](https://github.com/hermitdave/FrequencyWords). Contributors must cite verifiable open/public sources and must not upload copyrighted commercial books without permission.
