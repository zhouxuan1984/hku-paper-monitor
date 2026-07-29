import os
import smtplib
import email.utils
from datetime import date as Date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import INSTITUTIONS, TOPICS


def _get_hk_insts(p):
    hk = p.get("hk_institutions")
    if hk:
        return sorted(hk)
    r2n = {v["ror"]: k for k, v in INSTITUTIONS.items()}
    found = set()
    for s in p.get("institutions", []):
        for ror, cname in r2n.items():
            if ror in s:
                found.add(cname)
    return sorted(found)


def _count_papers_by_uni(all_papers):
    counts = {name: 0 for name in INSTITUTIONS}
    for p in all_papers:
        for cname in _get_hk_insts(p):
            counts[cname] = counts.get(cname, 0) + 1
    return [(k, v) for k, v in counts.items() if v > 0]


def build_html(data):
    date_str = data["date"]
    total = data["total_papers"]
    by_topic = data["by_topic"]
    all_papers = data["all_papers"]

    topic_order = [t["name"] for t in TOPICS]

    uni_counts = _count_papers_by_uni(all_papers)
    uni_summary = " · ".join(f"{name} {n}篇" for name, n in uni_counts)

    rows = []
    for tname in topic_order:
        papers = by_topic.get(tname)
        if not papers:
            continue
        paper_rows = ""
        for i, p in enumerate(papers[:10], 1):
            insts = _get_hk_insts(p)
            insts_str = " · ".join(insts) if insts else ", ".join(p.get("institutions", [])[:2])
            source_tag = f'<span style="background:#e8f0fe;padding:1px 6px;border-radius:3px;font-size:11px;color:#0366d6;">{p.get("source","")}</span>'
            abstract = (p.get("abstract") or "")[:300]
            if len(p.get("abstract", "")) > 300:
                abstract += "..."

            doi = p.get("doi", "")
            doi_link = ""
            if doi:
                doi_link = f'<a href="https://doi.org/{doi}" style="color:#0366d6;">doi:{doi}</a>'

            cites = p.get("citation_count")
            pctl = p.get("citation_percentile")
            cite_html = ""
            if cites is not None:
                cite_html += f'被引 {cites}'
                if pctl:
                    cite_html += f' · 百分位 {pctl}%'
                cite_html = f'<br><span style="color:#888;font-size:11px;">{cite_html}</span>'

            paper_url = p.get("url", "")
            direct_link = ""
            if paper_url and paper_url.startswith("http"):
                direct_link = f' · <a href="{paper_url}" style="color:#0366d6;">🔗 原文</a>'
            elif doi:
                direct_link = f' · <a href="https://doi.org/{doi}" style="color:#0366d6;">🔗 原文</a>'

            paper_rows += f"""
            <tr>
              <td style="padding:8px 12px;border-bottom:1px solid #eee;">{i}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #eee;">
                <strong>{p['title']}</strong> {source_tag}<br>
                <span style="color:#666;font-size:12px;">
                  {p.get("publication_date","")} · {p.get("primary_location","")} · {doi_link}{direct_link}
                </span>{cite_html}<br>
                <span style="color:#888;font-size:12px;">{insts_str}</span>
              </td>
              <td style="padding:8px 12px;border-bottom:1px solid #eee;font-size:13px;color:#555;max-width:500px;">
                {abstract}
              </td>
            </tr>"""

        rows.append(f"""
        <h3 style="background:#f6f8fa;padding:10px 16px;border-radius:6px;margin:24px 0 12px;font-size:16px;">
          {tname}
          <span style="font-weight:normal;font-size:13px;color:#666;margin-left:8px;">共 {len(papers)} 篇</span>
        </h3>
        <table style="width:100%;border-collapse:collapse;font-size:14px;">
          <thead>
            <tr style="background:#f1f1f1;">
              <th style="padding:6px 12px;text-align:left;width:32px;">#</th>
              <th style="padding:6px 12px;text-align:left;">论文</th>
              <th style="padding:6px 12px;text-align:left;">摘要</th>
            </tr>
          </thead>
          <tbody>
            {paper_rows}
          </tbody>
        </table>""")

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,'Segoe UI',Arial,sans-serif;background:#fff;padding:20px;max-width:960px;margin:0 auto;">

<div style="border-bottom:2px solid #0366d6;padding-bottom:12px;margin-bottom:20px;">
  <h1 style="font-size:22px;margin:0 0 4px;">HK Research Daily</h1>
  <div style="color:#666;font-size:14px;">
    香港八校核心期刊论文监测 · {date_str} · 共 <b>{total}</b> 篇匹配
  </div>
  <div style="color:#888;font-size:13px;margin-top:4px;">
    {uni_summary}
  </div>
</div>

{''.join(rows)}

<div style="border-top:1px solid #ddd;margin-top:30px;padding-top:12px;font-size:12px;color:#999;">
  <p>由 HK Research Daily Monitor 自动生成 · 数据来源: OpenAlex + PubMed + arXiv + Semantic Scholar</p>
  <p>覆盖领域: {' · '.join(topic_order)}</p>
  <p>覆盖院校: {' · '.join(INSTITUTIONS.keys())}</p>
</div>

</body>
</html>"""

    return html


def build_plain_text(data):
    date_str = data["date"]
    total = data["total_papers"]
    by_topic = data["by_topic"]

    lines = [f"HK Research Daily - {date_str}", f"共 {total} 篇匹配\n"]
    for tname, papers in by_topic.items():
        lines.append(f"【{tname}】({len(papers)}篇)")
        for i, p in enumerate(papers[:5], 1):
            src = p.get("source", "")
            insts = " · ".join(_get_hk_insts(p))
            doi = p.get("doi", "")
            lines.append(f"  {i}. [{src}] {p['title']}")
            if insts:
                lines.append(f"     {insts}")
            if doi:
                lines.append(f"     https://doi.org/{doi}")
        lines.append("")
    return "\n".join(lines)


def send_email(data, html_content, subject):
    smtp_host = os.environ.get("SMTP_HOST", "smtp.qq.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))
    email_addr = os.environ.get("EMAIL_ADDRESS", "")
    auth_code = os.environ.get("EMAIL_AUTH_CODE", "")
    raw_recipients = os.environ.get("RECIPIENT_EMAIL", email_addr)
    recipients = [r.strip() for r in raw_recipients.replace(";", ",").split(",") if r.strip()]

    if not email_addr or not auth_code:
        print("[EMAIL] EMAIL_ADDRESS or EMAIL_AUTH_CODE not set, skipping send")
        for r in recipients:
            print("[EMAIL] Would send to:", r)
        print("[EMAIL] Subject:", subject)
        return

    success, failed = 0, 0
    for recipient in recipients:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = email_addr
        msg["To"] = recipient
        msg["Date"] = email.utils.formatdate(localtime=True)
        msg.attach(MIMEText(build_plain_text(data), "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as s:
                s.login(email_addr, auth_code)
                s.sendmail(email_addr, [recipient], msg.as_string())
            print(f"[EMAIL] Sent to {recipient}")
            success += 1
        except Exception as e:
            print(f"[EMAIL] Failed to send to {recipient}: {e}")
            failed += 1

    print(f"[EMAIL] Done: {success} sent, {failed} failed")
