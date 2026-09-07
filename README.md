# HK Research Daily Monitor

每日自动监测香港八所大学在全球期刊的论文发表情况，按期刊影响因子（JCR 2024）排序，生成中文报告并推送到指定邮箱。

## 覆盖院校

香港大学、香港中文大学、香港科技大学、香港城市大学、香港理工大学、香港浸会大学、香港岭南大学、香港教育大学

## 数据来源

- [OpenAlex](https://openalex.org/) — 免费开放学术图谱，聚合 Scopus、PubMed、Crossref 等 2.5 亿+论文元数据。
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/) — 生物医学文献数据库。
- [arXiv](https://arxiv.org/) — 预印本平台（物理、数学、计算机科学等）。
- [Semantic Scholar](https://www.semanticscholar.org/) — 引用计数等补充信息。
- 影响因子数据来自 2024 年 JCR（Clarivate），本地映射表 `data/jcr_if.json`（21,527 本期刊）。

## 快速开始

### 1. 推送到 GitHub 仓库

```bash
# 创建新仓库（在 GitHub 上创建后）
cd hku-paper-monitor
git init
git add .
git commit -m "init: HK Research Daily Monitor"
git remote add origin https://github.com/<你的用户名>/hku-paper-monitor.git
git push -u origin main
```

### 2. 配置 GitHub Secrets

在仓库 Settings → Secrets and variables → Actions → New repository secret 中添加：

| Secret | 说明 |
|--------|------|
| `EMAIL_ADDRESS` | QQ 邮箱地址 (如 `123456789@qq.com`) |
| `EMAIL_AUTH_CODE` | QQ 邮箱 SMTP 授权码 (见下方获取方式) |
| `RECIPIENT_EMAIL` | 收件邮箱 (可与发送邮箱相同) |
| `SMTP_HOST` | SMTP 服务器 (默认 `smtp.qq.com`，可不填) |
| `SMTP_PORT` | SMTP 端口 (默认 `465`，可不填) |

### 3. 获取 QQ 邮箱 SMTP 授权码

1. 登录 QQ 邮箱 → 设置 → 账户
2. 找到 "POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
3. 开启 "SMTP服务"
4. 点击 "生成授权码" → 复制 16 位授权码
5. 将该授权码填入 GitHub Secrets 的 `EMAIL_AUTH_CODE`

### 4. 验证部署

- Actions 会在 **每天北京时间 0:30** 自动运行
- 也可以在 GitHub Actions 页面手动触发 `workflow_dispatch`

## 本地测试

```bash
# 查看前一天的数据（不发送邮件）
python3 daily_monitor.py --dry-run

# 查看指定日期
python3 daily_monitor.py --date 2026-07-20 --dry-run

# 查看多天前
python3 daily_monitor.py --days-back 3 --dry-run

# 实际发送（需设置环境变量）
export EMAIL_ADDRESS=your@qq.com
export EMAIL_AUTH_CODE=your_auth_code
export RECIPIENT_EMAIL=your@qq.com
python3 daily_monitor.py
```

## 输出示例

邮件包含：
- 顶部概要：日期、总论文数、各院校发文数
- 按期刊影响因子降序排列的论文列表（标题、期刊、IF 徽标、DOI、短摘要、作者单位、引用数、百分位）
- 最多展示前 150 篇，完整列表见文章内链接

## 项目结构

```
hku-paper-monitor/
├── .github/workflows/daily_monitor.yml   # GitHub Actions 定时任务
├── data/
│   └── jcr_if.json                       # 期刊影响因子映射表 (JCR 2024)
├── hku_monitor/
│   ├── config.py     # 院校 + 关键词配置
│   ├── fetcher.py    # 多数据源 API 查询 + 院校匹配 + IF 排名
│   └── mailer.py     # HTML 报告生成 + 邮件发送
├── daily_monitor.py  # 入口脚本
├── requirements.txt  # 无外部依赖（纯 Python 标准库）
└── README.md
```

## 许可

MIT
