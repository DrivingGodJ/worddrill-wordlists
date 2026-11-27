# WordDrill 公开单词表仓库

用于 [WordDrill](https://github.com/DrivingGodJ/word-drill) 在创建**本地词库**时直接拉取标准单词表（支持单选或多选合并）。

## 目录结构

- `index.json`：词表目录索引，记录词表名称、标签、词数与文件路径。
- `wordlists/cet4.json`：大学英语四级（CET-4）词汇。
- `wordlists/cet6.json`：大学英语六级（CET-6）词汇。
- `wordlists/ielts.json`：雅思核心词汇（IELTS）。
- `wordlists/distractors.json`：认词题干扰释义池。
- `scripts/build-wordlists.py`：从开源词书构建上述 JSON 词表的脚本。

## 词条格式

每个词表文件均为标准 WordDrill 词库 JSON：

```json
{
  "meta": {
    "id": "cet4",
    "name": "大学英语四级（CET-4）",
    "shortName": "四级词汇",
    "updated": "2026-11-27",
    "count": 4000,
    "source": "kajweb/dict"
  },
  "words": [
    {
      "id": "abandon",
      "word": "abandon",
      "pos": "vt.",
      "meaning": "放弃，遗弃",
      "example": "...",
      "exampleZh": "...",
      "tags": ["CET4"]
    }
  ]
}
```

## 来源与致谢

词汇、音标、释义与例句数据整理自开源词书项目 [kajweb/dict](https://github.com/kajweb/dict)。
