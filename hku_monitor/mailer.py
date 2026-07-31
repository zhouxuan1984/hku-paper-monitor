import os
import smtplib
import email.utils
from datetime import date as Date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import INSTITUTIONS


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
    ranked = data["ranked_papers"]
    all_papers = data["all_papers"]

    uni_counts = _count_papers_by_uni(all_papers)
    uni_summary = " · ".join(f"{name} {n}篇" for name, n in uni_counts)

    if len(ranked) > 150:
        ranked = ranked[:150]
        trunc_note = f'<div style="color:#c0392b;font-size:13px;margin:8px 0;">⚠ 论文较多，仅展示前 150 篇（按影响因子排序）</div>'
    else:
        trunc_note = ""

    paper_rows = ""
    for i, p in enumerate(ranked, 1):
        insts = _get_hk_insts(p)
        insts_str = " · ".join(insts) if insts else ", ".join(p.get("institutions", [])[:2])
        source_tag = f'<span style="background:#e8f0fe;padding:1px 6px;border-radius:3px;font-size:11px;color:#0366d6;">{p.get("source","")}</span>'
        abstract = (p.get("abstract") or "")

        doi = p.get("doi", "")
        doi_link = ""
        if doi:
            doi_link = f'<a href="https://doi.org/{doi}" style="color:#0366d6;">doi:{doi}</a>'

        if_val = p.get("impact_factor")
        if if_val is not None:
            if_html = f'<span style="background:#fff3cd;padding:1px 6px;border-radius:3px;font-size:12px;color:#8a6d3b;font-weight:bold;">IF {if_val}</span> '
        else:
            if_html = '<span style="background:#eee;padding:1px 6px;border-radius:3px;font-size:12px;color:#999;">IF —</span> '

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
              {if_html}{p.get("publication_date","")} · {p.get("journal","")} · {doi_link}{direct_link}
            </span>{cite_html}<br>
            <span style="color:#888;font-size:12px;">{insts_str}</span>
          </td>
          <td style="padding:8px 12px;border-bottom:1px solid #eee;font-size:13px;color:#555;">
            {abstract}
          </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,'Segoe UI',Arial,sans-serif;background:#fff;padding:20px;max-width:960px;margin:0 auto;">

<div style="border-bottom:2px solid #0366d6;padding-bottom:12px;margin-bottom:20px;">
  <h1 style="font-size:22px;margin:0 0 4px;">HK Research Daily</h1>
  <div style="color:#666;font-size:14px;">
    香港八校论文监测（按期刊影响因子排名） · {date_str} · 共 <b>{total}</b> 篇
  </div>
  <div style="color:#888;font-size:13px;margin-top:4px;">
    {uni_summary}
  </div>
</div>

{trunc_note}

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
</table>

<div style="border-top:1px solid #ddd;margin-top:30px;padding-top:12px;font-size:12px;color:#999;">
  <p>由 HK Research Daily Monitor 自动生成 · 数据来源: OpenAlex + PubMed + arXiv + Semantic Scholar</p>
  <p>影响因子来源: 2024 JCR (Clarivate) · 覆盖院校: {' · '.join(INSTITUTIONS.keys())}</p>
</div>

</body>
</html>"""

    return html


def build_plain_text(data):
    date_str = data["date"]
    total = data["total_papers"]
    ranked = data["ranked_papers"]

    lines = [f"HK Research Daily (按影响因子排名) - {date_str}", f"共 {total} 篇\n"]
    for i, p in enumerate(ranked[:150], 1):
        if_val = p.get("impact_factor")
        if_label = f"IF {if_val}" if if_val is not None else "IF —"
        src = p.get("source", "")
        insts = " · ".join(_get_hk_insts(p))
        doi = p.get("doi", "")
        lines.append(f"{i}. [{if_label}] {p['title']}")
        lines.append(f"     {p.get('journal','')} · {p.get('publication_date','')} · {src}")
        if insts:
            lines.append(f"     {insts}")
        if doi:
            lines.append(f"     https://doi.org/{doi}")
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
