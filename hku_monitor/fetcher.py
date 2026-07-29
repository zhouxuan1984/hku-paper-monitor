import re
import ssl
import json
import urllib.request
from datetime import date as Date
from .config import INSTITUTIONS, TOPICS

_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE

_UA = "HKU-Paper-Monitor/1.0 (mailto:hku-monitor@example.com)"


def _req(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    return urllib.request.urlopen(req, timeout=timeout, context=_CTX)


def decode_abstract(inverted_index):
    if not inverted_index:
        return ""
    words = {}
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word
    return " ".join(words[i] for i in sorted(words.keys()))


def parse_paper(work):
    authorships = work.get("authorships", [])
    inst_names = set()
    for auth in authorships:
        for inst in auth.get("institutions", []):
            name = inst.get("display_name", "")
            ror = inst.get("ror", "")
            if name:
                inst_names.add(f"{name}" + (f" ({ror})" if ror else ""))

    concepts = work.get("concepts", [])
    concept_ids = {c["id"] for c in concepts if c.get("id")}

    return {
        "id": work.get("id", ""),
        "title": work.get("title", ""),
        "doi": (work.get("doi") or "").replace("https://doi.org/", ""),
        "publication_date": work.get("publication_date", ""),
        "abstract": decode_abstract(work.get("abstract_inverted_index")),
        "authorships": authorships,
        "institutions": sorted(inst_names),
        "concept_ids": concept_ids,
        "concepts": [c["display_name"] for c in concepts if c.get("display_name")],
        "cited_by_count": work.get("cited_by_count", 0),
        "primary_location": (
            ((work.get("primary_location") or {}).get("source") or {})
            .get("display_name", "")
        ),
        "url": work.get("doi", work.get("id", "")),
    }


def classify_paper(paper):
    matched = []
    title = paper["title"] or ""
    abstract = paper["abstract"] or ""

    for topic in TOPICS:
        score = 0

        if topic["concept_id"] and topic["concept_id"] in paper["concept_ids"]:
            score += 2

        for kw in topic["keywords"]:
            pattern = re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE)
            if pattern.search(title):
                score += 3
            elif pattern.search(abstract):
                score += 1

        if score >= 2:
            matched.append(topic["name"])

    return matched


def fetch_papers(target_date=None):
    if target_date is None:
        target_date = Date.today().isoformat()

    date_str = target_date if isinstance(target_date, str) else target_date.isoformat()
    inst_list = [v["openalex"] for v in INSTITUTIONS.values()]
    inst_filter = "institutions.id:" + "|".join(inst_list)
    filter_str = f"{inst_filter},from_publication_date:{date_str},to_publication_date:{date_str}"

    all_papers = []
    cursor = "*"
    base = "https://api.openalex.org/works"

    while cursor:
        url = (f"{base}?filter={filter_str}&sort=publication_date:desc"
               f"&per_page=200&cursor={cursor}")
        try:
            resp = _req(url)
            data = json.loads(resp.read().decode())
        except Exception as e:
            print(f"  [WARN] OpenAlex API error: {e}")
            break

        for work in data.get("results", []):
            all_papers.append(parse_paper(work))

        cursor = data.get("meta", {}).get("next_cursor")

    for p in all_papers:
        p["topics"] = classify_paper(p)

    by_topic = {}
    for topic in TOPICS:
        tname = topic["name"]
        matched = [p for p in all_papers if tname in p["topics"]]
        if matched:
            by_topic[tname] = matched

    return {
        "date": date_str,
        "total_papers": len(all_papers),
        "total_classified": sum(len(v) for v in by_topic.values()),
        "by_topic": by_topic,
        "all_papers": all_papers,
    }
