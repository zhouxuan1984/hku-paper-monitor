import os
import re
import ssl
import json
import time
import xml.etree.ElementTree as ET
import urllib.request
from datetime import date as Date, timedelta
from .config import INSTITUTIONS, INSTITUTION_KEYWORDS

_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE

_UA = "HKU-Paper-Monitor/1.0 (mailto:hku-monitor@example.com)"

_IF_CACHE = None
_IF_STRIPPED_CACHE = None


def _load_impact_factors():
    global _IF_CACHE, _IF_STRIPPED_CACHE
    if _IF_CACHE is not None:
        return _IF_CACHE, _IF_STRIPPED_CACHE
    path = os.path.join(os.path.dirname(__file__), "..", "data", "jcr_if.json")
    try:
        with open(os.path.normpath(path), encoding="utf-8") as f:
            _IF_CACHE = json.load(f)
    except Exception:
        _IF_CACHE = {}
    stripped = {}
    for name, if_val in _IF_CACHE.items():
        s = re.sub(r"\s*\([^)]*\)\s*", " ", name).strip()
        if s:
            stripped.setdefault(s, if_val)
    _IF_STRIPPED_CACHE = stripped
    return _IF_CACHE, _IF_STRIPPED_CACHE


def get_impact_factor(journal):
    if not journal:
        return None
    mapping, stripped = _load_impact_factors()
    j = journal.strip().lower()
    if j in mapping:
        return mapping[j]
    j = re.split(r"\s*[:=|]\s*", j)[0].strip()
    j = re.sub(r"\s*\([^)]*\)\s*", " ", j).strip()
    if j in mapping:
        return mapping[j]
    if j in stripped:
        return stripped[j]
    return None


def _req(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    return urllib.request.urlopen(req, timeout=timeout, context=_CTX)


def _match_hk_institution(text):
    for cname, kws in INSTITUTION_KEYWORDS.items():
        for kw in kws:
            if re.search(r"\b" + re.escape(kw) + r"\b", text, re.IGNORECASE):
                return cname
    for cname, info in INSTITUTIONS.items():
        ror = info.get("ror")
        if ror and ror in text:
            return cname
    return None


def classify_paper(paper):
    matched = []
    title = paper["title"] or ""
    abstract = paper["abstract"] or ""
    for topic in TOPICS:
        score = 0
        if topic["concept_id"] and topic["concept_id"] in paper.get("concept_ids", set()):
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


def _deduplicate(papers):
    seen_dois = set()
    seen_titles = set()
    unique = []
    for p in papers:
        doi = (p.get("doi") or "").strip().lower()
        if doi and doi not in seen_dois:
            seen_dois.add(doi)
            unique.append(p)
            continue
        title = ((p.get("title") or "").strip().lower()
                 .replace(" ", "").replace("-", "").replace(":", ""))
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique.append(p)
            continue
        if not doi and not title:
            unique.append(p)
    return unique


def _make_paper(source, source_id, title="", doi="", abstract="",
                publication_date="", journal="", url="", authors=None,
                institutions=None, concept_ids=None,
                citation_count=None, citation_percentile=None):
    if authors is None:
        authors = []
    if institutions is None:
        institutions = []
    if concept_ids is None:
        concept_ids = set()
    hk_insts = []
    for inst in institutions:
        m = _match_hk_institution(inst)
        if m:
            hk_insts.append(m)
    for auth in authors:
        m = _match_hk_institution(auth)
        if m and m not in hk_insts:
            hk_insts.append(m)
    return {
        "source": source,
        "source_id": source_id,
        "title": title,
        "doi": doi.replace("https://doi.org/", ""),
        "abstract": abstract,
        "publication_date": publication_date,
        "primary_location": journal,
        "journal": journal,
        "impact_factor": get_impact_factor(journal),
        "url": url,
        "authors": authors,
        "institutions": sorted(set(institutions)),
        "hk_institutions": hk_insts,
        "concept_ids": concept_ids,
        "citation_count": citation_count,
        "citation_percentile": citation_percentile,
        "topics": [],
    }


# ── OpenAlex ────────────────────────────────────────────────────────

def _decode_abstract(inverted_index):
    if not inverted_index:
        return ""
    words = {}
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word
    return " ".join(words[i] for i in sorted(words.keys()))


def _fetch_openalex(date_str):
    inst_list = [v["openalex"] for v in INSTITUTIONS.values()]
    inst_filter = "institutions.id:" + "|".join(inst_list)
    filter_str = f"{inst_filter},from_publication_date:{date_str},to_publication_date:{date_str}"

    papers = []
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
            authorships = work.get("authorships", [])
            inst_names = set()
            author_names = []
            for auth in authorships:
                aname = (auth.get("author") or {}).get("display_name", "")
                if aname:
                    author_names.append(aname)
                for inst in auth.get("institutions", []):
                    name = inst.get("display_name", "")
                    ror = inst.get("ror", "")
                    if name:
                        inst_names.add(f"{name}" + (f" ({ror})" if ror else ""))

            concepts = work.get("concepts", [])
            concept_ids = {c["id"] for c in concepts if c.get("id")}
            journal = (
                ((work.get("primary_location") or {}).get("source") or {})
                .get("display_name", "")
            )

            cby = work.get("cited_by_count")
            cby_pctl = work.get("cited_by_percentile_year")
            cby_pctl_str = None
            if cby_pctl and isinstance(cby_pctl, dict):
                lo = cby_pctl.get("min")
                hi = cby_pctl.get("max")
                if lo is not None and hi is not None:
                    cby_pctl_str = f"{lo}-{hi}"

            p = _make_paper(
                source="OpenAlex",
                source_id=work.get("id", ""),
                title=work.get("title", ""),
                doi=(work.get("doi") or "").replace("https://doi.org/", ""),
                abstract=_decode_abstract(work.get("abstract_inverted_index")),
                publication_date=work.get("publication_date", ""),
                journal=journal,
                url=work.get("doi", work.get("id", "")),
                authors=author_names,
                institutions=list(inst_names),
                concept_ids=concept_ids,
                citation_count=cby,
                citation_percentile=cby_pctl_str,
            )
            papers.append(p)

        cursor = data.get("meta", {}).get("next_cursor")

    print(f"  [OpenAlex] {len(papers)} papers")
    return papers


# ── PubMed ──────────────────────────────────────────────────────────

def _fetch_pubmed(date_str):
    date_fmt = date_str.replace("-", "/")
    affil_parts = []
    for cname, kws in INSTITUTION_KEYWORDS.items():
        for kw in kws:
            affil_parts.append(f'"{kw}"[Affiliation]')
    affil_query = " OR ".join(affil_parts)
    query = urllib.request.quote(
        f"({affil_query}) AND ({date_fmt}[Date - Publication] : {date_fmt}[Date - Publication])"
    )
    esearch_url = (f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                   f"?db=pubmed&term={query}&retmax=200&retmode=json&sort=pub+date")

    try:
        resp = _req(esearch_url)
        data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"  [WARN] PubMed esearch error: {e}")
        return []

    id_list = data.get("esearchresult", {}).get("idlist", [])
    if not id_list:
        return []

    ids = ",".join(id_list)
    efetch_url = (f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                  f"?db=pubmed&id={ids}&retmode=xml")

    try:
        resp = _req(efetch_url)
        xml_data = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [WARN] PubMed efetch error: {e}")
        return []

    papers = []
    root = ET.fromstring(xml_data)
    for article_elem in root.findall(".//PubmedArticle"):
        try:
            medline = article_elem.find(".//MedlineCitation")
            article = medline.find(".//Article")
            if article is None:
                continue

            pmid = medline.findtext("PMID", "")
            title = article.findtext("ArticleTitle", "")
            abstract_parts = []
            for ab in article.findall(".//AbstractText"):
                label = ab.get("Label", "")
                text = "".join(ab.itertext())
                if label:
                    text = f"{label}: {text}"
                abstract_parts.append(text)
            abstract = "\n".join(abstract_parts)

            journal_elem = article.find("Journal")
            journal = ""
            if journal_elem is not None:
                journal = journal_elem.findtext("Title", "")

            pub_date = ""
            ji = article.find("Journal")
            if ji is not None:
                jid = ji.find("JournalIssue")
                if jid is not None:
                    pd = jid.find("PubDate")
                    if pd is not None:
                        year = pd.findtext("Year", "")
                        month = pd.findtext("Month", "")
                        day = pd.findtext("Day", "")
                        if year:
                            pub_date = year
                            if month:
                                months = {
                                    "Jan":"01","Feb":"02","Mar":"03","Apr":"04",
                                    "May":"05","Jun":"06","Jul":"07","Aug":"08",
                                    "Sep":"09","Oct":"10","Nov":"11","Dec":"12",
                                }
                                m = months.get(month[:3], month)
                                pub_date += f"-{m}"
                                if day:
                                    pub_date += f"-{day.zfill(2)}"

            authors = []
            institutions = []
            for author_elem in article.findall(".//Author"):
                last = author_elem.findtext("LastName", "")
                fore = author_elem.findtext("ForeName", "")
                if last or fore:
                    authors.append(f"{fore} {last}".strip())
                for aff in author_elem.findall("AffiliationInfo/Affiliation"):
                    if aff.text:
                        institutions.append(aff.text)

            doi = ""
            for eid in medline.findall(".//ArticleIdList/ArticleId"):
                if eid.get("IdType") == "doi":
                    doi = eid.text or ""
                    break
            if not doi:
                for eid in medline.findall(".//ArticleIdList/ArticleId"):
                    if eid.get("IdType") == "doi" or "doi" in (eid.text or "").lower():
                        doi = eid.text or ""
                        break

            p = _make_paper(
                source="PubMed",
                source_id=pmid,
                title=title,
                doi=doi,
                abstract=abstract,
                publication_date=pub_date,
                journal=journal,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                authors=authors,
                institutions=institutions,
            )
            papers.append(p)
        except Exception as e:
            continue

    print(f"  [PubMed] {len(papers)} papers")
    return papers


# ── arXiv ───────────────────────────────────────────────────────────

ARXIV_CATEGORIES = [
    "cs.AI", "cs.LG", "cs.CV", "cs.RO", "cs.CL", "cs.NE",
    "cs.NI", "cs.IT", "cs.SY", "cs.SE", "cs.AR", "cs.ET",
    "cs.MM", "cs.HC", "cs.CR", "cs.DC",
    "quant-ph", "quant-ph",
    "physics.optics", "physics.app-ph", "physics.ins-det",
    "physics.space-ph", "physics.med-ph",
    "eess.SP", "eess.AS", "eess.SY",
    "math.OC", "math.IT", "math.NA",
    "stat.ML", "stat.ME",
    "q-bio.BM", "q-bio.GN", "q-bio.QM",
    "cond-mat.mtrl-sci", "cond-mat.mes-hall",
]


def _fetch_arxiv(date_str):
    date_fmt = date_str.replace("-", "")
    cat_query = "+OR+".join(f"cat:{c}" for c in ARXIV_CATEGORIES)
    query = f"({cat_query})+AND+submittedDate:[{date_fmt}0000+TO+{date_fmt}2359]"
    url = (f"https://export.arxiv.org/api/query?search_query={query}"
           f"&max_results=200&sortBy=submittedDate&sortOrder=descending")

    try:
        resp = _req(url, timeout=60)
        xml_data = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [WARN] arXiv API error: {e}")
        return []

    papers = []
    ns = {"a": "http://www.w3.org/2005/Atom",
          "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(xml_data)

    for entry in root.findall("a:entry", ns):
        try:
            title = (entry.findtext("a:title", "", ns)
                     .replace("\n", " ").strip())
            summary = (entry.findtext("a:summary", "", ns)
                       .replace("\n", " ").strip())
            published = entry.findtext("a:published", "", ns)[:10]

            arxiv_id = ""
            for link in entry.findall("a:link", ns):
                if link.get("rel") == "alternate":
                    arxiv_id = link.get("href", "")
                    break
            if not arxiv_id:
                arxiv_id = entry.findtext("a:id", "", ns)

            doi = ""
            for link in entry.findall("a:link", ns):
                href = link.get("href", "")
                if "doi.org" in href:
                    doi = href.split("doi.org/")[-1]
                    break

            authors = []
            institutions = []
            for author_elem in entry.findall("a:author", ns):
                name = author_elem.findtext("a:name", "", ns)
                if name:
                    authors.append(name)
                aff = author_elem.findtext("arxiv:affiliation", "", ns)
                if aff:
                    institutions.append(aff)

            journal = "arXiv"

            p = _make_paper(
                source="arXiv",
                source_id=arxiv_id,
                title=title,
                doi=doi,
                abstract=summary,
                publication_date=published,
                journal=journal,
                url=arxiv_id,
                authors=authors,
                institutions=institutions,
            )
            if p["hk_institutions"]:
                papers.append(p)
        except Exception as e:
            continue

    print(f"  [arXiv] {len(papers)} papers")
    return papers


# ── Semantic Scholar ────────────────────────────────────────────────


def _fetch_semantic_scholar(date_str):
    year = date_str[:4]
    papers = []
    queries = [
        "artificial intelligence machine learning Hong Kong",
        "engineering robotics semiconductor Hong Kong",
        "biomedical quantum materials Hong Kong",
    ]

    for q in queries:
        time.sleep(3)
        query = urllib.request.quote(q)
        url = (f"https://api.semanticscholar.org/graph/v1/paper/search"
               f"?query={query}&year={year}&limit=100&fields=title,abstract,"
               f"externalIds,authors,publicationDate,journal,url,citationCount")

        try:
            resp = _req(url, timeout=30)
            data = json.loads(resp.read().decode())
        except Exception as e:
            print(f"  [WARN] Semantic Scholar API error: {e}")
            if "429" in str(e):
                print(f"  [WARN] Rate limited, skipping")
            break

        for hit in data.get("data", []):
            authors = []
            for a in hit.get("authors", []):
                aname = a.get("name", "")
                if aname:
                    authors.append(aname)

            ext_ids = hit.get("externalIds", {}) or {}
            doi = ext_ids.get("DOI", "")

            if not any(_match_hk_institution(a) for a in authors):
                continue

            pdate = hit.get("publicationDate", "") or ""
            journal_info = hit.get("journal", {}) or {}
            jname = journal_info.get("name", "") if isinstance(journal_info, dict) else ""

            p = _make_paper(
                source="Semantic Scholar",
                source_id=hit.get("paperId", ""),
                title=hit.get("title", ""),
                doi=doi,
                abstract=hit.get("abstract", ""),
                publication_date=pdate,
                journal=jname,
                url=hit.get("url", f"https://api.semanticscholar.org/{hit.get('paperId','')}"),
                authors=authors,
                institutions=[],
                citation_count=hit.get("citationCount"),
            )
            papers.append(p)

    print(f"  [Semantic Scholar] {len(papers)} papers")
    return papers


# ── Entry Point ─────────────────────────────────────────────────────

def fetch_papers(target_date=None):
    if target_date is None:
        target_date = Date.today().isoformat()
    date_str = target_date if isinstance(target_date, str) else target_date.isoformat()

    all_papers = []
    print(f"  Fetching OpenAlex...")
    all_papers.extend(_fetch_openalex(date_str))
    print(f"  Fetching PubMed...")
    all_papers.extend(_fetch_pubmed(date_str))
    time.sleep(0.5)
    print(f"  Fetching arXiv...")
    all_papers.extend(_fetch_arxiv(date_str))
    time.sleep(0.5)
    print(f"  Fetching Semantic Scholar...")
    all_papers.extend(_fetch_semantic_scholar(date_str))

    before = len(all_papers)
    all_papers = _deduplicate(all_papers)
    dupes = before - len(all_papers)
    if dupes:
        print(f"  [Dedup] removed {dupes} duplicates")

    for p in all_papers:
        p["topics"] = []

    with_if = [p for p in all_papers if p.get("impact_factor") is not None]
    without_if = [p for p in all_papers if p.get("impact_factor") is None]
    without_if.sort(key=lambda p: (p.get("publication_date") or "", p.get("title") or ""))
    ranked = sorted(with_if, key=lambda p: -p["impact_factor"]) + without_if

    return {
        "date": date_str,
        "total_papers": len(all_papers),
        "ranked_papers": ranked,
        "all_papers": all_papers,
    }
