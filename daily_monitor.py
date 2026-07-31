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

    ranked = data["ranked_papers"]
    with_if = [p for p in ranked if p.get("impact_factor") is not None]
    print(f"[MONITOR] Total: {data['total_papers']} papers, "
          f"{len(with_if)} with impact factor")
    top10 = ranked[:10]
    print("[MONITOR] Top 10 by IF:")
    for p in top10:
        print(f"  IF {p.get('impact_factor', '-'):<6} {p.get('journal',''):<40} {p['title'][:50]}")

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
