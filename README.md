# Horizon - AI News Aggregator & Translator

AI资讯聚合与翻译平台，自动获取每日最新AI资讯并翻译为中文。

## 特性

- **多源聚合**：支持 HackerNews、Reddit、ArXiv、GitHub、Lobsters、YouTube、RSS/Atom 等来源
- **智能去重**：基于URL规范化和内容相似度的跨源去重
- **规则评分**：基于来源权威性、关键词、内容长度、新鲜度等规则计算质量分数
- **热度排名**：多维度指标计算，支持时间衰减算法
- **自动翻译**：集成 Google Translate，自动将内容翻译为中文
- **定时任务**：支持每日自动抓取
- **CLI工具**：丰富的命令行工具，方便管理

## 支持的来源

| 来源 | 类型 | 描述 |
|------|------|------|
| HackerNews | 技术社区 | Top stories |
| Reddit | 社区 | Subreddit 热门帖子 |
| ArXiv | 学术 | 最新 AI/ML 论文 |
| GitHub | 代码平台 | 仓库 Releases |
| Lobsters | 技术社区 | 热门故事 |
| YouTube | 视频 | AI 相关频道 |
| RSS/Atom | 通用 | 任何 RSS/Atom 源 |

## 安装

### 前置要求

- Python 3.11+
- pip 或 uv

### 安装步骤

```bash
# 克隆项目
git clone https://github.com/jiang237832960/daily-ai-news-aggregator.git
cd daily-ai-news-aggregator

# 安装后端依赖
cd horizon
pip install -e .

# 或者使用 uv
uv sync
```

## 使用

### 初始化配置

首次运行时会自动创建默认配置文件 `data/config.json`。

### 获取新闻

```bash
# 获取最近24小时的新闻
horizon fetch

# 获取最近48小时的新闻
horizon fetch --hours 48

# 只获取指定来源
horizon fetch --sources hn,reddit

# 禁用翻译
horizon fetch --no-translate
```

### 查看来源

```bash
horizon list-sources
```

### 生成日报

```bash
# 生成今日日报
horizon digest

# 生成指定日期的日报
horizon digest --date 2026-03-28
```

### 查看统计

```bash
# 查看最近7天的统计
horizon stats

# 查看最近30天的统计
horizon stats --days 30

# JSON格式输出
horizon stats --format json
```

### 配置向导

```bash
horizon wizard
```

## 配置

配置文件位于 `data/config.json`。

```json
{
  "version": 1,
  "translation": {
    "provider": "google",
    "enabled": true,
    "timeout": 10
  },
  "sources": [
    {
      "name": "HackerNews",
      "type": "hackernews",
      "enabled": true,
      "weight": 8.0,
      "timeout": 30
    }
  ],
  "scoring": {
    "keywords": {
      "突发": 2, "重磅": 2, "首发": 2
    },
    "length_bonus": {
      "min": 1000, "max": 10000, "score": 1
    },
    "freshness_hours": 24,
    "freshness_bonus": 2
  },
  "scheduler": {
    "enabled": false,
    "cron": "0 8 * * *",
    "timezone": "Asia/Shanghai"
  }
}
```

## 项目结构

```
horizon/
├── __init__.py
├── main.py              # CLI入口
├── models.py            # 数据模型
├── config.py            # 配置加载
├── database.py          # 数据库
├── aggregator.py        # 聚合器
├── parser.py            # 解析器
├── translator.py         # 翻译器
├── scorer.py            # 规则评分
├── ranker.py            # 热度排名
├── deduplicator.py      # 去重器
└── crawlers/            # 爬虫模块
    ├── __init__.py
    ├── base.py          # 基类
    ├── hackernews.py
    ├── rss.py
    ├── reddit.py
    ├── arxiv.py
    ├── github.py
    ├── lobsters.py
    └── youtube.py
```

## 评分算法

### 质量评分 (RuleScorer)

| 因素 | 权重/加分 | 说明 |
|------|----------|------|
| 来源权威性 | 来源配置 | 管理员配置 |
| 关键词匹配 | +2分/关键词 | 突发、重磅、首发等 |
| 内容长度 | +1分 | 1000-10000字 |
| 新鲜度 | +2分 | 24小时内 |
| 技术元素 | +1分 | 包含代码、API等 |

### 热度计算 (HotnessRanker)

| 因素 | 权重 | 说明 |
|------|------|------|
| 来源权威性 | 30% | 配置的来源权重 |
| 规则评分 | 30% | RuleScorer得分 |
| 发布时间 | 25% | 含时间衰减 |
| 互动指标 | 15% | 评论、点赞、分享 |

**时间衰减**：每24小时降低10%

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
ruff check .
```

## 许可证

MIT License

## 参考项目

- [Horizon](https://github.com/Thysrael/Horizon) - 全自动AI科技新闻聚合与摘要生成器
- [/last30days](https://github.com/mvanhorn/last30days-skill) - AI agent skill，多源话题研究
