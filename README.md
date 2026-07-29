# HK Research Daily Monitor

每日自动监测香港八所大学在 22 个前沿科技领域的全球核心期刊论文发表情况，生成中文报告并推送到指定邮箱。

## 覆盖院校

香港大学、香港中文大学、香港科技大学、香港城市大学、香港理工大学、香港浸会大学、香港岭南大学、香港教育大学

## 覆盖领域

集成电路、航空航天、生物医药、低空经济、新型储能、智能机器人、量子科技、生物制造、氢能、脑机接口、具身智能、6G、新一代信息技术、生物技术、新能源、新材料、高端装备、新能源汽车、绿色环保、海洋装备、人工智能

## 数据来源

[OpenAlex](https://openalex.org/) — 免费开放学术图谱，聚合 Scopus、PubMed、Crossref 等 2.5 亿+论文元数据。

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

- Actions 会在 **每天北京时间 09:00** 自动运行
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
- 按领域分组的论文列表（标题、期刊、DOI、短摘要、作者单位）
- 每个领域标注 "共 N 篇"

## 项目结构

```
hku-paper-monitor/
├── .github/workflows/daily_monitor.yml   # GitHub Actions 定时任务
├── hku_monitor/
│   ├── config.py     # 院校 + 领域配置
│   ├── fetcher.py    # OpenAlex API 查询 + 论文分类
│   └── mailer.py     # HTML 报告生成 + 邮件发送
├── daily_monitor.py  # 入口脚本
├── requirements.txt  # 无外部依赖（纯 Python 标准库）
└── README.md
```

## 许可

MIT
