**简体中文** | [English](GUIDE.en.md)

# 合格单词表构建与提交指南

[返回仓库首页](../README.md)

本指南说明如何制作一份能被 WordDrill 稳定加载、并充分发挥**独立回想**、**语境填空**与**按难度智能安排每日新词**能力的标准词表。

---

## 1. 文件命名与整体结构

- 文件路径：`wordlists/<deck-id>.json`，`<deck-id>` 使用小写英文字母、数字与连字符（例如 `kaoyan.json`、`toefl-core.json`、`cs-english.json`）。
- 编码：UTF-8（无 BOM），建议使用紧凑 JSON 减小下载体积。
- 顶层对象包含 `meta` 与 `words` 两个字段：

```json
{
  "meta": {
    "id": "toefl-core",
    "name": "托福核心词汇（TOEFL）",
    "shortName": "托福词汇",
    "updated": "2026-11-27",
    "count": 3200,
    "source": "可核验的公开词源说明或仓库链接"
  },
  "words": [ /* 词条数组 */ ]
}
```

---

## 2. 词条字段规范（必填与推荐）

| 字段 | 级别 | 类型 | 规范与作用 |
| :--- | :--- | :--- | :--- |
| `id` | **必填** | `string` | 唯一稳定标识符，建议由 `word` 规范化生成：小写英文、数字和连字符（`re.sub(r'[^a-z0-9]+', '-', word.lower()).strip('-')`）。**同一词表内严禁重复**；修改已有词条 `id` 会导致用户丢失该词的学习进度。 |
| `word` | **必填** | `string` | 英文词头或短语，去除首尾空白，不夹杂音标或中文注释。 |
| `meaning` | **必填** | `string` | 清晰简洁的中文释义，多义项用全角分号 `；` 分隔（如 `"放弃；遗弃"`）。 |
| `tags` | **必填** | `string[]` | 训练要求标签，**仅填写 `["拼写"]` 或 `["只认"]`**（分别对应「认词+拼写」和「只认不拼」）。 |
| `pos` | **强烈推荐** | `string` | 词性，带句点，多词性用 `/` 拼接（如 `"v."`、`"n./v."`、`"adj."`）。WordDrill 认词题优先挑选同词性干扰项。 |
| `example` | **强烈推荐** | `string` | 英文完整例句，满足下方「语境填空质量门槛」时会自动解锁**语境填空**加练。 |
| `exampleZh` | **强烈推荐** | `string` | 与 `example` 一一对应的中文译文。 |
| `difficulty` | **推荐** | `1 \| 2 \| 3 \| 4 \| 5` | 难度等级（1 最基础，5 最难），供 WordDrill「难易搭配 / 先易后难 / 难词优先」直接调度。 |
| `freq` | **推荐** | `integer` | 词频排名（如 `en_50k.txt` 中的正整数名次，越小越常见），与 `difficulty` 联合估算 0–100 综合难度。 |
| `collocations` | 可选 | `string[]` | 1–3 条高频搭配，推荐格式 `"phrase（中文）"`。 |
| `phonetic` | 可选 | `string` | 音标字符串（不带外层斜杠，如 `"rɪˈzɪliənt"`）。 |

---

## 3. 核心质量门槛

### 语境填空例句标准
WordDrill 仅对符合完整句条件的词条开放「语境填空」：
- 词数在 `5`–`35` 词之间，字符长度不超过 `240`；
- 首字母大写，以 `.`、`!` 或 `?` 结尾；
- 不含 `...`、`…`、`__` 占位符或 HTML 标签；
- 句子中以完整单词边界包含目标词 `word`（不区分大小写）；
- 配套准确的中文翻译 `exampleZh`。

### 词频与难度分级参考
参考 `scripts/build-wordlists.py` 对 `hermitdave/FrequencyWords`（`en_50k.txt`）的统一分层：
- `difficulty = 1`：词频排名 `1 – 3,500`
- `difficulty = 2`：词频排名 `3,501 – 10,000`
- `difficulty = 3`：词频排名 `10,001 – 22,000`
- `difficulty = 4`：词频排名 `22,001 – 36,000`
- `difficulty = 5`：词频排名 `> 36,000` 或罕见长词

> 若自定义词表暂未提供 `freq`/`difficulty`，WordDrill 也会按词长、义项数与拼写负荷自动估算难度；但提供真实词频与分级能让每日新词排布明显更贴合学习梯度。

---

## 4. 在 `index.json` 中登记词表

在仓库根目录 `index.json` 的 `wordlists` 数组末尾追加一项：

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

- `tag` 建议写 `"默认拼写"` 或 `"默认只认"`，与词表内主要词条的 `tags` 保持一致。
- `count` 必须严格等于目标文件中 `words` 数组的长度。

---

## 5. 本地校验与 WordDrill 实测流程

### 第一步：运行自动校验脚本

```bash
python3 scripts/check-wordlists.py
```

脚本会逐项检查：
- `index.json` 与所有词表 JSON 语法是否合法；
- 必填字段、唯一 `id`、`tags` 合法值（仅允许 `拼写` / `只认`）、`difficulty`（1–5）与 `freq`（正整数）范围；
- `index.json` 与 `meta.count` 是否与实际词数完全一致；
- 统计并报告每个词表的有效语境填空例句覆盖率。

### 第二步：在 WordDrill 中真机实测拉取
1. 将你的修改推送到自己的 Fork 仓库（公开仓库）。
2. 打开 [WordDrill](https://drivinggodj.github.io/word-drill/) →「**词库**」→「**+ 新建本地词库**」。
3. 展开「**词表源仓库**」，将地址改为 `你的用户名/worddrill-wordlists`，点击「**重新拉取**」。
4. 勾选新词表创建本地词库，试跑一轮认词/拼写与「单词」列表，确认显示正常。

### 第三步：提交 Pull Request
在 PR 说明中写明：
- 词表名称、目标场景与词数；
- 明确的数据来源与开源/公共授权依据；
- `python3 scripts/check-wordlists.py` 通过的输出结果。
