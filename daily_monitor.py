#!/usr/bin/env python3
"""HK Research Daily Monitor - 香港八校核心期刊论文每日监测"""

import argparse
import sys
from datetime import date, timedelta
from hku_monitor.fetcher import fetch_papers
from hku_monitor.mailer import build_html, send_email


def main():
    parser = argparse.ArgumentParser(description="HK Research Daily Monitor")
    parser.add_argument("--date", help="查询日期 YYYY-MM-DD (默认: 昨天)")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅打印报告到 stdout，不发送邮件")
    parser.add_argument("--days-back", type=int, default=1,
                        help="回溯天数 (默认: 1)")
    args = parser.parse_args()

    if args.date:
        query_date = args.date
    else:
        query_date = (date.today() - timedelta(days=args.days_back)).isoformat()

    print(f"[MONITOR] Fetching papers for {query_date} ...")
    data = fetch_papers(query_date)

    print(f"[MONITOR] Total: {data['total_papers']} papers, "
          f"{data['total_classified']} classified")
    for tname, papers in data["by_topic"].items():
        print(f"  {tname}: {len(papers)} 篇")

    html = build_html(data)
    subject = f"HK Research Daily - {query_date}"

    if args.dry_run:
        print("\n" + "=" * 60)
        print("HTML REPORT (first 3000 chars):")
        print(html[:3000])
        print("=" * 60)
        return

    send_email(data, html, subject)


if __name__ == "__main__":
    main()
