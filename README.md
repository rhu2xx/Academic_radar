# 🎯 Academic Radar：面向“未知的未知”的科研侦察员

作为研究者，我们常常会困在自己的领域泡泡里。我们阅读相同的期刊，引用相同的作者，也用和本领域其他人相同的方式解决问题。但很多时候，你最棘手的问题其实已经在某个你从未关注过的领域中被解决了。

**Academic Radar** 是一个用于弥合这种鸿沟的 AI 科研工具。它不只是寻找“你研究什么”，而是进一步分析“你如何研究”，从而帮助你发现其他领域中具有相似方法结构的论文。

**“同构搜索”的核心思想**：假设你正在构建一个模型来预测股票市场趋势，但遇到了高噪声数据带来的瓶颈。Academic Radar 会分析你的问题，并发现从数学结构上看，“高噪声股票数据”和心脏病学中的“不规则心电信号”非常相似。于是，它可能会推荐一篇关于 ECG 信号去噪的医学论文。虽然这篇论文讨论的是心脏信号，但其中的方法工具可能正好能解决股票预测中的噪声问题。

这就是 **Isomorphic Search（同构搜索）**：在不同研究领域中寻找具有相同数学结构、建模方式或方法路径的问题与解法。

## ✨ 核心功能

Academic Radar 主要提供以下功能：

1. **研究兴趣画像生成**
   - 从用户上传的论文中提取研究主题、方法偏好、常用技术路线和潜在研究约束。
   - 自动生成个性化 research profile，用于后续论文推荐。

2. **跨领域同构检索**
   - 不只根据关键词搜索论文，而是根据问题结构、数学形式和方法相似性进行跨领域检索。
   - 帮助用户发现其他学科中可迁移的方法或工具。

3. **OpenAlex 论文搜索**
   - 对接 OpenAlex 数据源，支持在大规模学术论文库中搜索相关论文。
   - 可根据时间范围、查询数量和目标论文数量进行配置。

4. **方法相关性评分**
   - 使用 AI Analyst 对候选论文进行分析，并给出 0–1 的方法相关性评分。
   - 重点评估论文中的方法是否能迁移到用户当前研究问题中。

5. **每周邮件推送**
   - 可通过 GitHub Actions 自动运行搜索流程。
   - 每周将新的论文发现结果发送到指定邮箱。

6. **去重与历史记录管理**
   - 自动记录已经发送过的论文 ID 和标题。
   - 避免重复推荐相同论文，提高每周推送质量。

7. **可配置搜索参数**
   - 支持配置分析论文数量、搜索时间范围、最低相关性分数、每个查询返回数量等参数。
   - 用户可以根据自己的研究需求调整推荐强度和覆盖范围。

## 🏗️ 工作原理

Academic Radar 由 5 个 AI Agent 协同工作：

1. **Profiler**
   - 从你的论文中学习研究兴趣、领域背景和方法偏好。

2. **Abstractor**
   - 将你的研究问题抽象为可跨领域迁移的搜索查询。

3. **Scout**
   - 在 OpenAlex 上搜索大规模学术论文。

4. **Analyst**
   - 评估候选论文与用户研究问题之间的方法相关性，并给出 0–1 的评分。

5. **Publisher**
   - 将每周发现的高价值论文整理后发送到你的邮箱。

## 🚀 快速开始

### 1. 安装

```bash
git clone git@github.com:rhu2xx/Academic_radar.git
cd Academic_radar
pip install -r requirements.txt
```

### 2. 配置

创建 `.env` 文件：

```bash
# 必填
LLM_PROVIDER=deepseek                    # 也可以使用 openai/anthropic
DEEPSEEK_API_KEY=your_key_here
OPENALEX_EMAIL=your@email.com            # 用于获得更快的 OpenAlex API 访问速度

# 邮件配置（可选；每周自动化邮件需要）
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASS=your_app_password
RECIPIENT_EMAIL=your@email.com
```

<details>
<summary><b>📖 如何获取 API Key</b></summary>

#### 🤖 DeepSeek API Key（推荐，成本较低）

1. 访问 [platform.deepseek.com](https://platform.deepseek.com)
2. 注册并验证邮箱
3. 进入 **API Keys** 页面
4. 点击 **Create API Key**
5. 复制 key，通常以 `sk-...` 开头
6. 费用约为 `$0.14 / 百万 tokens`

#### 🔍 OpenAlex Email

1. 使用任意有效邮箱地址
2. 在 `.env` 中添加：

```bash
OPENALEX_EMAIL=your@email.com
```

3. 配置邮箱后可以获得更快的 API 访问速度
4. 可选：在 [openalex.org/account](https://openalex.org/account) 获取高级 API key

#### 📧 Gmail SMTP 密码

1. 访问 [myaccount.google.com](https://myaccount.google.com)
2. 启用 **两步验证**
3. 在设置中搜索 **App Passwords**
4. 选择 **Mail** 和你的设备
5. 点击 **Generate**，复制 16 位字符密码
6. 在 `.env` 中使用该密码，而不是 Gmail 登录密码

#### 其他 LLM 提供商

**OpenAI：**

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

**Anthropic Claude：**

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-...
```

</details>

### 3. 创建研究画像

```bash
# 将你的论文放入 data/user_papers/
mkdir -p data/user_papers
cp your_papers/*.pdf data/user_papers/

# 提取研究画像，只需执行一次
python main.py --mode profile
```

### 4. 搜索论文

```bash
# 手动搜索
python main.py --mode search

# 完整流程：profile + search + email
python main.py --mode full
```

## 🤖 使用 GitHub Actions 自动化

你可以使用 GitHub Actions 每周自动运行 Academic Radar，并将论文发现结果发送到邮箱，无需手动执行。

### 前置条件

- 已完成安装、配置和研究画像创建
- 拥有 GitHub 账号
- 已将该项目推送到 GitHub 仓库

### Step 1：准备仓库

```bash
# 1. 确保 profile 已生成
python main.py --mode profile

# 2. 提交必要文件
git add cache/profile.json
git add .github/workflows/weekly_radar.yml
git commit -m "Setup automated radar workflow"
git push
```

### Step 2：添加 GitHub Secrets

进入 GitHub 仓库：

```text
Settings → Secrets and variables → Actions → New repository secret
```

添加以下 secrets：

| Secret 名称 | 值 | 示例 | 是否必需 |
|-------------|----|------|----------|
| `DEEPSEEK_API_KEY` | DeepSeek API key | `sk-abc123...` | ✅ 是 |
| `OPENALEX_EMAIL` | OpenAlex 邮箱 | `you@email.com` | ✅ 是 |
| `OPENALEX_API_KEY` | OpenAlex 高级 key | `abc123...` | ⚠️ 可选 |
| `SMTP_USER` | Gmail 地址 | `you@gmail.com` | ✅ 是 |
| `SMTP_PASS` | Gmail app password | `abcd efgh ijkl mnop` | ✅ 是 |
| `RECIPIENT_EMAIL` | 接收报告的邮箱 | `you@email.com` | ✅ 是 |
| `LLM_MODEL` | 使用的 LLM 模型 | `deepseek-reasoner` | 可选 |

> 注意：`MAX_PAPERS_TO_ANALYZE`、`SEARCH_DAYS_BACK` 等搜索参数不是 secrets，应该直接在 `.github/workflows/weekly_radar.yml` 中修改。

### Step 3：自定义搜索参数

编辑 `.github/workflows/weekly_radar.yml`：

```yaml
MAX_PAPERS_TO_ANALYZE: 10          # 要分析的论文数量
SEARCH_DAYS_BACK: 600              # 搜索最近多少天的论文
MIN_BORROWABILITY_SCORE: 0.5       # 最低相关性分数
MAX_RESULTS_PER_QUERY: 20          # 每个查询返回的论文数量
TARGET_NEW_PAPERS: 10              # 每次搜索的目标新论文数量
MAX_PAGES_TO_SCAN: 5               # 最大扫描页数
PAPER_HISTORY_DAYS: 365            # 已发送论文记录保留天数
LLM_TEMPERATURE: 0.7               # LLM 创造性，范围 0.0–1.0
```

修改后提交：

```bash
git add .github/workflows/weekly_radar.yml
git commit -m "Adjust search parameters"
git push
```

### Step 4：启用 GitHub Actions

1. 进入仓库的 **Actions** 标签页
2. 如果出现提示，点击 **I understand my workflows, go ahead and enable them**
3. 确认可以看到 **Weekly Academic Radar Scan** workflow

### Step 5：手动测试 Workflow

1. 进入 **Actions** 标签页
2. 点击 **Weekly Academic Radar Scan**
3. 点击右侧 **Run workflow**
4. 选择 `mode: search`
5. 点击绿色 **Run workflow** 按钮

运行完成后可以检查：

- workflow 是否成功运行
- 邮箱是否收到论文推荐
- `cache/sent_papers.json` 是否更新

## 📅 自定义运行时间

编辑 `.github/workflows/weekly_radar.yml`：

```yaml
on:
  schedule:
    - cron: '0 9 * * 1'  # 每周一 UTC 时间上午 9 点
```

常见配置：

```text
'0 9 * * 1'      每周一上午 9 点
'0 9 * * 1,4'    每周一和周四上午 9 点
'0 9 1,15 * *'   每月 1 日和 15 日上午 9 点
'0 9 * * *'      每天上午 9 点
```

## ⚙️ 关键配置项

可以在 `.env` 或 workflow 文件中调整以下参数：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `MAX_PAPERS_TO_ANALYZE` | 5 | 每次运行分析的论文数量 |
| `SEARCH_DAYS_BACK` | 7 | 向前搜索多少天 |
| `MIN_BORROWABILITY_SCORE` | 0.5 | 最低方法相关性分数 |
| `MAX_RESULTS_PER_QUERY` | 20 | 每个查询获取的论文数量 |

## 📊 输出示例

邮件标题示例：

```text
🎯 Academic Radar: 3 Discoveries This Week
```

邮件内容示例：

```text
📄 Efficient Tensor Decomposition for Video Streaming
   Computer Vision • Score: 0.89

   💡 这篇论文使用 Tucker decomposition 将内存占用降低 73%，
   可以直接对应你在交通预测模型中遇到的 OOM 问题。

   🔗 可尝试将低秩张量近似方法应用到你的时空交通数据中。
```

## 🔧 高级特性

- **避免重复推荐**：通过论文 ID 和标题记录已发送论文。
- **智能排序**：综合相关性、引用数和新近度进行排序。
- **英文论文过滤**：自动过滤非英文论文。
- **成本优化**：在调用 LLM 分析前先进行去重。
- **移动端兼容**：邮件样式兼容 iOS 等常见设备。

## 📁 项目结构

```text
academic-radar/
├── src/agents/          # 5 个 AI Agent
├── src/core/            # 状态管理
├── src/tools/           # OpenAlex、PDF 解析
├── main.py              # 入口文件
└── .github/workflows/   # GitHub Actions 自动化配置
```

## 🤝 贡献方向

欢迎贡献代码或文档。可以考虑以下方向：

- 添加 Semantic Scholar 或 PubMed 支持
- 改进 prompt engineering
- 增加 Web UI
- 优化论文去重逻辑
- 增强邮件报告模板

## 📄 许可证

MIT License