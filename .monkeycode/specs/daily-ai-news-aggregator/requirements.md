# 需求文档

## 引言

本工具是一个AI资讯聚合与翻译平台，从多个权威来源抓取AI相关资讯，自动翻译为中文，支持手动触发和定时抓取两种模式。平台提供数据存储、汇总分析、技术趋势图表等功能，帮助用户高效追踪AI领域动态。

## 词汇表

- **Aggregator**: 资讯聚合器，负责从多个来源抓取内容
- **Source**: 资讯来源，包括技术社区、国内媒体、学术论文等
- **Crawler**: 爬虫模块，负责从各来源获取原始内容
- **Parser**: 解析器，负责解析原始HTML/JSON为结构化数据
- **Scheduler**: 调度器，负责管理定时任务执行
- **Frontend**: 前端Web界面，展示资讯内容
- **Article**: 资讯文章，包含标题、摘要、来源、发布时间等字段
- **Daily Digest**: 每日摘要，每日期刊化的资讯合集
- **CLI**: 命令行界面，用户通过命令行触发抓取任务
- **Trend Chart**: 趋势图表，展示技术话题热度变化
- **Deduplication**: 去重机制，跨源合并相同URL的内容
- **X (Twitter)**: 社交媒体平台，用户获取实时资讯和专家观点
- **Facebook**: 社交媒体平台，支持公开页面内容获取
- **Lobsters**: 技术社区，类似HackerNews的程序员社区
- **Stack Overflow**: 开发者问答平台，技术问题讨论
- **DEV Community**: 开发者技术博客社区
- **Medium**: 在线文章发布平台，技术博客聚集地
- **Translator**: 翻译模块，负责将英文内容翻译为中文
- **RuleScorer**: 规则评分器，基于预定义规则计算文章质量分数

## 需求

### 需求1：多来源资讯抓取

**用户故事：** AS 一个开发者，我想要从多个AI资讯来源抓取内容，以便能在一个地方看到所有最新资讯。

#### Acceptance Criteria

1. WHEN 系统启动时，Aggregator SHALL 从预配置的新闻源列表中加载所有来源配置。
2. WHEN 用户执行 `horizon fetch` 命令时，Aggregator SHALL 触发所有已启用的Source进行内容抓取。
3. WHEN 抓取任务执行时，Aggregator SHALL 并发地向每个Source发起请求，超时时间设置为30秒。
4. WHEN 某Source抓取失败时，系统 SHALL 记录错误日志并继续处理其他Source，不中断整体流程。
5. IF Source返回非200状态码，系统 SHALL 重试最多3次，每次间隔10秒。
6. WHERE Source需要认证（如GitHub API），系统 SHALL 支持OAuth2/API Key两种认证方式。
7. IF 用户指定了时间窗口参数（如 `--hours 48`），系统 SHALL 仅抓取该时间范围内的内容。

### 需求2：支持的资讯来源

**用户故事：** AS 一个用户，我想要系统支持主流的AI资讯来源，以便获取全面的信息。

#### Acceptance Criteria

1. WHERE Source类型为"HackerNews"时，系统 SHALL 获取Top stories并支持获取评论。
2. WHERE Source类型为"RSS/Atom"时，系统 SHALL 解析任何标准RSS或Atom feed。
3. WHERE Source类型为"Reddit"时，系统 SHALL 支持获取subreddit的热门帖子和评论。
4. WHERE Source类型为"GitHub"时，系统 SHALL 支持获取仓库releases和用户事件。
5. WHERE Source类型为"微信公众号"时，系统 SHALL 通过第三方API（如可能）获取文章列表。
6. WHERE Source类型为"ArXiv"时，系统 SHALL 支持获取最新提交的AI/ML论文。
7. WHERE Source类型为"X (Twitter)"时，系统 SHALL 支持通过API获取指定账号的推文或关键词搜索结果。
8. WHERE Source类型为"Facebook"时，系统 SHALL 支持获取公开页面（Page）的帖子内容。
9. WHERE Source类型为"Lobsters"时，系统 SHALL 支持获取热门故事和评论。
10. WHERE Source类型为"Stack Overflow"时，系统 SHALL 支持获取指定标签的问题和答案。
11. WHERE Source类型为"DEV Community"时，系统 SHALL 支持获取热门文章和标签过滤。
12. WHERE Source类型为"Medium"时，系统 SHALL 支持获取热门文章和关键词搜索。
13. WHERE Source类型为"YouTube"时，系统 SHALL 支持获取AI相关频道的最新视频和标题。
14. WHERE Source需要认证（如X API、Reddit API），系统 SHALL 支持OAuth2/API Key两种认证方式。

### 需求3：内容解析与结构化

**用户故事：** AS 一个内容创作者，我想要系统解析抓取的内容并提取关键信息，以便我能快速了解每条资讯的核心要点。

#### Acceptance Criteria

1. WHEN Crawler返回原始内容时，Parser SHALL 识别内容格式（HTML/JSON/RSS/Atom）。
2. WHEN 解析HTML内容时，Parser SHALL 提取文章标题、发布日期、来源URL、摘要和正文内容。
3. WHEN 解析RSS/Atom内容时，Parser SHALL 提取所有entry项的标题、链接、发布时间和描述。
4. WHEN 解析JSON API响应时，Parser SHALL 根据预定义的字段映射规则提取数据。
5. IF 内容包含中文，系统 SHALL 使用UTF-8编码进行解码，防止乱码。
6. IF 文章正文超过5000字，Parser SHALL 生成500字的摘要作为预览。

### 需求4：跨源去重

**用户故事：** AS 一个用户，我想要系统自动合并来自不同平台但指向相同内容的资讯，以避免信息重复。

#### Acceptance Criteria

1. WHEN Parser生成Article时，Aggregator SHALL 计算文章URL的规范形式作为去重依据。
2. IF 两篇文章的规范URL相同，系统 SHALL 仅保留发布时间最早的一篇。
3. WHERE 文章标题相似度超过85%（使用编辑距离算法），系统 SHALL 标记为潜在重复供人工确认。
4. WHEN 去重完成后，系统 SHALL 生成去重报告，包含检测到的重复对数量。

### 需求5：基于规则的质量评分

**用户故事：** AS 一个分析师，我想要系统根据预定义规则对资讯进行质量评分，以便筛选出最有价值的内容。

#### Acceptance Criteria

1. WHERE 评分因素包括来源权威性（来源权重由管理员配置）、标题关键词匹配、内容长度、发布时间新鲜度，RuleScorer SHALL 计算综合质量分数（0-10分）。
2. WHERE 来源权威性评分由管理员在配置文件中设置，系统 SHALL 使用配置的权重进行计算。
3. WHERE 标题包含"突发"、"重磅"、"首发"等关键词时，系统 SHALL 增加2分。
4. WHERE 文章正文超过1000字且少于10000字时，系统 SHALL 增加1分（内容充实但不过长）。
5. WHERE 文章发布时间在24小时内，系统 SHALL 增加2分（新鲜度高）。
6. IF 文章包含代码、技术术语、图表等专业技术元素，RuleScorer SHALL 增加1分。
7. IF 最终分数超过10分，系统 SHALL 截断为10分。

### 需求6：热度排名

**用户故事：** AS 一个内容编辑，我想要系统根据多维度指标计算文章热度，以便快速找到最热门的内容。

#### Acceptance Criteria

1. WHERE 热度计算考虑来源权威性（权重30%）、规则评分（权重30%）、发布时间（权重25%）、互动指标（权重15%），HotnessRanker SHALL 计算综合热度分数。
2. WHERE 来源权重由管理员配置，系统 SHALL 支持调整各来源的权重系数。
3. WHERE 互动指标包括评论数、点赞数、转发数，系统 SHALL 从各平台抓取这些数据（如果可用）。
4. IF 同一话题的多篇文章，系统 SHALL 合并计算话题整体热度。
5. WHEN 用户访问热度榜单时，界面 SHALL 按热度分数倒序显示文章。

### 需求7：智能排序与筛选

**用户故事：** AS 一个用户，我想要系统根据我的偏好智能排序和筛选资讯，以便快速找到感兴趣的内容。

#### Acceptance Criteria

1. WHERE 文章列表默认按热度排序，用户 SHALL 可切换为按时间、评分、来源排序。
2. IF 用户设置了偏好标签（如"LLM"、"Computer Vision"），系统 SHALL 优先展示匹配标签的文章。
3. WHERE 用户使用标签过滤器时，界面 SHALL 仅显示包含选定标签的文章。
4. IF 用户使用来源过滤器时，界面 SHALL 仅显示来自选定来源的文章。
5. WHERE 用户使用时间范围过滤器时，界面 SHALL 仅显示发布时间在范围内的文章。

### 需求8：内容翻译为中文

**用户故事：** AS 一个中文用户，我想要系统将所有资讯翻译成中文，以便无障碍阅读。

#### Acceptance Criteria

1. WHERE 原始内容为英文时，Translator SHALL 调用翻译API将其翻译为中文。
2. WHERE 翻译API支持Google Translate、DeepL、百度翻译等，系统 SHALL 支持配置切换。
3. IF 翻译API调用失败或超时（超过10秒），系统 SHALL 记录错误并保留原始英文内容。
4. IF 原始内容已经是中文，系统 SHALL 跳过翻译步骤。
5. WHERE 文章标题和正文都需要翻译，系统 SHALL 保持标题和正文的对应关系。
6. IF 用户指定 `--no-translate` 参数，翻译功能 SHALL 被禁用。
7. WHERE 翻译结果需要存储，系统 SHALL 在数据库中同时保存原文和译文。

### 需求8：数据存储

**用户故事：** AS 一个系统管理员，我想要系统将抓取的资讯持久化存储，以便后续查询和分析。

#### Acceptance Criteria

1. WHEN 首次启动时，系统 SHALL 初始化SQLite数据库文件 `data/horizon.db`。
2. WHEN Parser生成Article时，系统 SHALL 将其存储到数据库，包含标题、URL、摘要、正文、来源、发布时间、原始JSON等字段。
3. IF 数据库文件不存在，系统 SHALL 自动创建必要的表结构。
4. IF 数据库版本需要升级，系统 SHALL 执行自动迁移。
5. IF 存储空间超过10GB，系统 SHALL 在日志中记录存储警告。

### 需求9：手动触发机制

**用户故事：** AS 一个用户，我想要通过命令行手动触发抓取任务，以便按需获取最新资讯。

#### Acceptance Criteria

1. WHEN 用户执行 `horizon fetch` 命令时，系统 SHALL 立即执行一次完整的抓取流程。
2. IF 用户指定 `horizon fetch --hours 48`，系统 SHALL 抓取过去48小时内的内容。
3. IF 用户指定 `horizon fetch --sources hn,reddit`，系统 SHALL 仅抓取指定来源。
4. WHEN 抓取任务执行时，系统 SHALL 在终端输出实时进度日志。
5. WHEN 抓取任务完成时，系统 SHALL 显示汇总信息，包括抓取的文章数量、来源统计等。

### 需求10：每日摘要生成

**用户故事：** AS 一个用户，我想要系统生成每日的资讯摘要，以便快速了解当天的重要新闻。

#### Acceptance Criteria

1. WHEN 用户执行 `horizon digest` 命令时，系统 SHALL 生成当日资讯的Markdown格式摘要。
2. WHERE 生成的摘要包含中英文双语版本，系统 SHALL 合并到同一文件中。
3. IF 文章数量超过20篇，摘要 SHALL 包含"精选"栏目，挑选最重要的5篇进行详细介绍。
4. WHEN 摘要生成完成后，系统 SHALL 保存到 `data/summaries/YYYY-MM-DD.md`。
5. IF 用户指定 `horizon digest --publish`，系统 SHALL 自动部署到GitHub Pages（如果配置了）。

### 需求11：统计分析仪表板

**用户故事：** AS 一个分析师，我想要系统提供统计分析功能，以便了解资讯的分布和趋势。

#### Acceptance Criteria

1. WHEN 用户执行 `horizon stats` 命令时，系统 SHALL 生成以下统计信息：
   - 各来源文章数量分布
   - 每日文章发布数量趋势
   - 热门话题词云数据
   - 平均每日文章数量
2. WHERE 统计时间范围默认为最近7天，用户 SHALL 可通过 `--days N` 参数自定义。
3. IF 用户指定 `--format json`，系统 SHALL 输出JSON格式的统计数据。

### 需求12：技术趋势图表

**用户故事：** AS 一个研究者，我想要系统展示技术话题的趋势图表，以便追踪AI领域的技术演进。

#### Acceptance Criteria

1. WHEN 用户访问趋势页面时，Web界面 SHALL 展示以下图表：
   - 每日文章发布量折线图
   - 来源分布饼图
   - 技术话题词频趋势图
2. WHERE 图表数据源为最近30天的文章，系统 SHALL 支持按时间范围筛选。
3. IF 用户选择特定话题标签，图表 SHALL 仅显示包含该标签的文章数据。
4. WHERE 图表使用ECharts实现，系统 SHALL 支持导出PNG格式的图片。

### 需求13：Web界面展示

**用户故事：** AS 一个个人用户，我想要通过Web界面浏览和搜索资讯，以便随时查看最新AI动态。

#### Acceptance Criteria

1. WHEN 用户访问首页时，系统 SHALL 显示当日和昨日的资讯列表，按时间倒序排列。
2. WHEN 用户点击文章时，系统 SHALL 在新页面显示完整文章内容。
3. WHEN 用户使用搜索功能时，系统 SHALL 支持按关键词、来源、日期范围进行筛选。
4. WHERE 文章列表超过50条时，界面 SHALL 实现分页功能，每页最多显示50条。
5. IF 用户点击"标记已读"按钮，系统 SHALL 记录用户阅读状态并灰色显示已读文章。

### 需求14：来源管理

**用户故事：** AS 一个管理员，我想要管理系统资讯来源，以便添加、启用或禁用特定来源。

#### Acceptance Criteria

1. WHEN 管理员访问来源管理页面时，系统 SHALL 列表显示所有配置的Source及其状态。
2. WHERE Source状态为"禁用"时，系统 SHALL 在抓取时跳过该Source。
3. IF 管理员添加新Source，系统 SHALL 验证URL格式和可访问性。
4. WHEN Source连续失败超过10次时，系统 SHALL 自动禁用该Source并记录告警。

### 需求15：资讯分享

**用户故事：** AS 一个内容创作者，我想要快速分享感兴趣的文章，以便与我的读者分享有价值的AI资讯。

#### Acceptance Criteria

1. WHEN 用户点击文章分享按钮时，系统 SHALL 生成该文章的链接。
2. IF 用户使用"复制链接"功能，系统 SHALL 生成包含UTM参数的完整URL。
3. IF 系统部署在域名 example.com，生成的链接 SHALL BE https://example.com/article/{article_id}?utm_source=share。

### 需求16：数据序列化与往返验证

**用户故事:** AS 一个开发者，我想要系统支持数据序列化和反序列化的往返验证，以确保数据完整性。

#### Acceptance Criteria

1. WHEN Parser解析Article时，Parser SHALL 生成结构化的Article对象。
2. WHEN Article对象需要存储时，系统 SHALL 序列化为JSON格式并存储到数据库。
3. WHEN 从数据库读取Article时，系统 SHALL 反序列化为Article对象。
4. IF 序列化后再反序列化的对象与原始对象不一致，系统 SHALL 记录数据不一致错误。
5. WHERE 文章正文包含特殊字符（如HTML标签），Pretty-Printer SHALL 正确转义并还原。

### 需求17：定时调度（可选）

**用户故事:** AS 一个用户，我想要系统支持定时自动抓取，以便每天自动更新资讯。

#### Acceptance Criteria

1. IF 用户配置了 `scheduler.enabled=true`，Scheduler SHALL 在预定时间自动执行抓取任务。
2. WHERE 用户位于中国时区（UTC+8），默认抓取时间 SHALL BE 每天上午8:00。
3. IF 抓取任务执行时间超过1小时，Scheduler SHALL 记录警告日志。
4. WHEN 抓取完成后，Scheduler SHALL 生成当日抓取报告。

### 需求18：配置管理

**用户故事:** AS 一个开发者，我想要通过配置文件管理所有设置，以便快速调整系统行为。

#### Acceptance Criteria

1. WHEN 系统首次启动时，ConfigLoader SHALL 从 `data/config.json` 加载配置（如不存在则使用默认配置）。
2. WHERE 配置包含翻译API设置时，系统 SHALL 支持 Google Translate / DeepL / 百度翻译 等提供商。
3. IF 用户执行 `horizon wizard` 命令，系统 SHALL 启动交互式配置向导。
4. WHERE 配置包含过滤阈值时，文章 SHALL 仅保留规则评分高于阈值的内容。
5. IF 配置文件格式错误，系统 SHALL 输出友好的错误提示并退出。
6. WHERE 配置包含来源权重时，管理员 SHALL 可调整各来源的权威性权重。

### 需求19：定期清理与归档

**用户故事:** AS 一个系统维护者，我想要系统自动清理过期内容，以保持数据库性能。

#### Acceptance Criteria

1. WHEN 文章发布超过7天且未归档时，系统 SHALL 自动将其移动到归档表。
2. WHERE 文章发布超过30天，系统 SHALL 保留摘要但删除正文以节省空间。
3. IF 管理员触发手动清理，系统 SHALL 生成清理报告，包含删除的文章数量和释放的空间。

## 参考实现

本项目设计参考了以下开源项目：

- **Horizon** (https://github.com/Thysrael/Horizon) - 全自动AI科技新闻聚合与摘要生成器，本项目简化设计，无需AI模型
- **AI-News-Aggregator** - 基于Python的RSS新闻聚合器，支持每日摘要和Notion集成
- **ai-daily-digest** - 从90个顶级技术博客获取Hacker News内容的AI日报

## 技术选型建议

| 组件 | 推荐技术 | 说明 |
|------|----------|------|
| 后端语言 | Python 3.11+ | 生态丰富，适合数据处理和爬虫 |
| Web框架 | FastAPI | 高性能，自动API文档 |
| 前端框架 | Next.js | SSR支持，部署简单 |
| 数据库 | SQLite | 轻量级，适合个人项目 |
| 图表库 | ECharts | 丰富的图表类型 |
| 爬虫框架 | httpx + BeautifulSoup | 异步支持，解析能力强 |
| 定时任务 | APScheduler | 轻量级定时调度 |
| RSS解析 | feedparser | 成熟的RSS解析库 |
