**简体中文** | [English](README.en.md)

# WordDrill 公开单词表仓库

为 [WordDrill · 背单词](https://drivinggodj.github.io/word-drill/) 提供开箱即用的标准单词表，在应用内「**词库 → 新建本地词库**」即可单选或多选合并拉取，也欢迎社区通过 Pull Request 提交更多高质量词表。

[打开 WordDrill 拉取词表](https://drivinggodj.github.io/word-drill/) · [词表构建与提交指南](docs/GUIDE.zh-CN.md) · [主应用仓库](https://github.com/DrivingGodJ/word-drill)

## 已收录词表

| 词表 | 文件路径 | 默认训练标签 | 词数 | 说明 |
| :--- | :--- | :--- | ---: | :--- |
| 大学英语四级（CET-4） | `wordlists/cet4.json` | 默认拼写 | 4,544 | 四级核心与高频词，含音标、释义、例句、搭配、词频与难度 |
| 大学英语六级（CET-6） | `wordlists/cet6.json` | 默认只认 | 3,992 | 六级核心与高频词，默认专注认词（应用内可自由切换拼写模式） |
| 雅思核心词汇（IELTS） | `wordlists/ielts.json` | 默认拼写 | 5,275 | 雅思高频核心词，含完整例句、搭配、词频与难度分级 |

仓库同时维护 `wordlists/distractors.json`（认词题词库外干扰释义池）与 `index.json`（WordDrill 拉取的目录索引）。多选合并词表时，WordDrill 会按词条 `id` 自动去重，若同一词在任一词表标为 `拼写`，合并后保留拼写要求。

## 提交你的新单词表（3 步）

欢迎提交考研、托福、GRE、专四专八、计算机英语或其他合法开源来源的词表：

1. **构建词表 JSON**：在 `wordlists/<id>.json` 放入 UTF-8 编码的词表文件。每条词条必须具备唯一稳定的 `id`、`word`、`meaning` 与 `tags`（仅填 `["拼写"]` 或 `["只认"]`）；强烈建议补齐 `pos`、完整英文 `example`/`exampleZh`、`difficulty`（1–5）与 `freq`（词频排名），以完整启用 WordDrill 的**语境填空**与**按难度智能排新词**。
2. **登记目录索引**：在 `index.json` 的 `wordlists` 数组中新增一项，确保 `id`、`file` 与实际文件路径一致，`count` 等于 `words` 数组长度。
3. **本地校验并实测后提 PR**：运行内置校验脚本确认零报错，并在 WordDrill「新建本地词库 → 词表源仓库」填入你自己的 `用户名/worddrill-wordlists` 实测拉取正常后提交 Pull Request。

```bash
python3 scripts/check-wordlists.py
```

## 词条结构速览

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

## 进一步了解

| 想了解什么 | 去哪里看 |
| :--- | :--- |
| 完整字段规范、例句门槛、难度分级与 PR 验收清单 | [词表构建与提交指南](docs/GUIDE.zh-CN.md) |
| 从开源词书与词频表自动构建词表 | [build-wordlists.py](scripts/build-wordlists.py) |
| 一键校验 `index.json` 与所有词表文件 | [check-wordlists.py](scripts/check-wordlists.py) |
| 主应用与学习规则说明 | [WordDrill 仓库](https://github.com/DrivingGodJ/word-drill) |
| 问题反馈或词表需求 | [Issues](https://github.com/DrivingGodJ/worddrill-wordlists/issues) |

**来源与版权说明**：现有四级、六级与雅思词表数据整理自开源词书 [kajweb/dict](https://github.com/kajweb/dict)，词频分级参考 [hermitdave/FrequencyWords](https://github.com/hermitdave/FrequencyWords)。提交新词表时请务必注明清晰可核验的合法开源/公共来源，切勿上传未经授权的商业教材或受版权保护的私有词库。
