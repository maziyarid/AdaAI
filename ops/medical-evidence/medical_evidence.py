#!/usr/bin/env python3
"""Deterministic medical evidence retrieval + independent claim verification.

This worker sits between Stage C (candidate claims) and Stage D (drafting).
It retrieves real records from public medical/scholarly APIs, stores an auditable
packet in factory.sqlite3, then asks an independent provider to judge each claim
against only the retrieved evidence. Mistral is never used as the verifier.

The worker fails closed: no authoritative source -> no approved claim.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path("/srv/maziyar-wp-mcp")
DB = Path(os.environ.get("MZ_FACTORY_DB", str(ROOT / "state/factory.sqlite3")))
AI_CLI = str(ROOT / ".venv/bin/mzmcp-ai")
USER_AGENT = "MaziyarMedicalEvidence/1.0 (evidence-retrieval; contact=maziyarid.com)"
MAX_CLAIMS = 6
MAX_EVIDENCE_PER_CLAIM = 7
MAX_EXCERPT = 1000
APPROVABLE_PROVIDERS = {"pubmed", "europe_pmc", "openfda", "dailymed"}


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS medical_evidence_runs (
          run_id TEXT PRIMARY KEY,
          chain_id TEXT NOT NULL,
          status TEXT NOT NULL,
          claim_count INTEGER NOT NULL DEFAULT 0,
          source_count INTEGER NOT NULL DEFAULT 0,
          approved_count INTEGER NOT NULL DEFAULT 0,
          rejected_count INTEGER NOT NULL DEFAULT 0,
          verifier_job_id TEXT,
          provider_status_json TEXT NOT NULL DEFAULT '{}',
          packet_json TEXT NOT NULL DEFAULT '{}',
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_medical_evidence_runs_chain
          ON medical_evidence_runs(chain_id, updated_at);
        CREATE TABLE IF NOT EXISTS medical_evidence_sources (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          run_id TEXT NOT NULL,
          chain_id TEXT NOT NULL,
          claim_key TEXT NOT NULL,
          source_id TEXT NOT NULL,
          provider TEXT NOT NULL,
          title TEXT NOT NULL,
          url TEXT,
          doi TEXT,
          pmid TEXT,
          publication_date TEXT,
          source_type TEXT,
          authority_tier TEXT NOT NULL,
          excerpt TEXT,
          metadata_json TEXT NOT NULL DEFAULT '{}',
          retrieved_at TEXT NOT NULL,
          UNIQUE(run_id, claim_key, source_id),
          FOREIGN KEY(run_id) REFERENCES medical_evidence_runs(run_id)
        );
        CREATE INDEX IF NOT EXISTS idx_medical_evidence_sources_chain
          ON medical_evidence_sources(chain_id, claim_key, provider);
        CREATE TABLE IF NOT EXISTS medical_claim_verdicts (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          run_id TEXT NOT NULL,
          chain_id TEXT NOT NULL,
          claim_id TEXT,
          claim_key TEXT NOT NULL,
          candidate_wording TEXT NOT NULL,
          allowed_wording TEXT,
          verdict TEXT NOT NULL,
          evidence_strength TEXT,
          medical_risk TEXT,
          source_ids_json TEXT NOT NULL DEFAULT '[]',
          rationale TEXT,
          uncertainty TEXT,
          created_at TEXT NOT NULL,
          UNIQUE(run_id, claim_key),
          FOREIGN KEY(run_id) REFERENCES medical_evidence_runs(run_id)
        );
        """
    )


def http_get_json(url: str, timeout: int = 25) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def http_get_text(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/xml,text/xml,text/plain,*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def clean_text(value: Any, limit: int | None = None) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        value = " ".join(str(x) for x in value if x is not None)
    text = html.unescape(re.sub(r"\s+", " ", str(value))).strip()
    if limit and len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


def recover_json_object(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else None
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            value = json.loads(text[start : end + 1])
            return value if isinstance(value, dict) else None
        except Exception:
            return None
    return None


def recover_candidate_claims(raw: str, limit: int = MAX_CLAIMS) -> list[dict[str, Any]]:
    parsed = recover_json_object(raw)
    if isinstance(parsed, dict) and isinstance(parsed.get("candidate_claims"), list):
        return [x for x in parsed["candidate_claims"] if isinstance(x, dict)][:limit]
    text = raw or ""
    marker = text.find('"candidate_claims"')
    if marker < 0:
        return []
    array_start = text.find("[", marker)
    if array_start < 0:
        return []
    claims: list[dict[str, Any]] = []
    i = array_start + 1
    while i < len(text) and len(claims) < limit:
        while i < len(text) and text[i] not in "{]":
            i += 1
        if i >= len(text) or text[i] == "]":
            break
        start = i
        depth = 0
        in_string = False
        escaped = False
        while i < len(text):
            ch = text[i]
            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
            else:
                if ch == '"':
                    in_string = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        piece = text[start : i + 1]
                        try:
                            item = json.loads(piece)
                            if isinstance(item, dict):
                                claims.append(item)
                        except Exception:
                            pass
                        i += 1
                        break
            i += 1
        else:
            break
    return claims


def load_chain(chain_id: str) -> tuple[sqlite3.Row, dict[str, Any]]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM content_ladder WHERE chain_id=?", (chain_id,)).fetchone()
    if row is None:
        raise RuntimeError(f"unknown chain: {chain_id}")
    try:
        state = json.loads(row["state_json"] or "{}")
    except json.JSONDecodeError:
        state = {}
    return row, state if isinstance(state, dict) else {}


def candidate_claims_from_state(state: dict[str, Any]) -> list[dict[str, Any]]:
    stage_c = ((state.get("stages") or {}).get("C") or {})
    parsed = stage_c.get("parsed") if isinstance(stage_c, dict) else None
    if isinstance(parsed, dict) and isinstance(parsed.get("candidate_claims"), list):
        claims = [x for x in parsed["candidate_claims"] if isinstance(x, dict)]
    else:
        claims = recover_candidate_claims(str(stage_c.get("text") or ""))
    clean: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(claims[:MAX_CLAIMS], start=1):
        key = clean_text(item.get("claim_key")) or f"claim_{index}"
        wording = clean_text(item.get("exact_candidate_wording") or item.get("claim_text"), 1800)
        if not wording or key in seen:
            continue
        seen.add(key)
        risk = clean_text(item.get("medical_risk") or item.get("proposed_medical_risk") or "M2").upper()
        if risk not in {"M0", "M1", "M2", "M3", "M4"}:
            risk = "M2"
        clean.append({
            "claim_key": key,
            "candidate_wording": wording,
            "population_context": clean_text(item.get("population/context") or item.get("population") or item.get("context"), 800),
            "uncertainty": clean_text(item.get("uncertainty"), 800),
            "contradiction_questions": item.get("contradiction_questions") if isinstance(item.get("contradiction_questions"), list) else [],
            "source_urls_or_ids": item.get("source_urls_or_ids") if isinstance(item.get("source_urls_or_ids"), list) else [],
            "medical_risk": risk,
        })
    return clean


def query_terms(worker_id: str, claim: dict[str, Any], state: dict[str, Any] | None = None) -> str:
    key = claim["claim_key"].lower().replace("-", "_")
    if worker_id in {"DRB-MED", "DRB-GSC"}:
        owner = str((state or {}).get("existing_landing_page") or "").lower()
        service_bases = {
            "hump-removal": ["rhinoplasty", "dorsal hump"],
            "rhinoplasty-primary": ["rhinoplasty"],
            "rhinoplasty-revision": ["revision rhinoplasty"],
            "rhinoplasty-bony": ["rhinoplasty", "bony nose", "dorsal hump"],
            "rhinoplasty-natural": ["rhinoplasty", "patient reported outcomes"],
            "septoplasty": ["septoplasty", "deviated nasal septum"],
            "turbinoplasty": ["turbinoplasty", "inferior turbinate reduction"],
            "sinus-endoscopy": ["functional endoscopic sinus surgery", "chronic rhinosinusitis"],
        }
        base = ["rhinoplasty"]
        for service_slug, terms in service_bases.items():
            if service_slug in owner:
                base = terms
                break
    elif worker_id == "RD-MED":
        base = ["dentistry", "dental"]
    else:
        base = ["medical"]

    vocab = {
        "anatomy": ["nasal dorsum anatomy"],
        "dorsum": ["nasal dorsum"],
        "hump": ["dorsal hump"],
        "bony_nose": ["nasal bony pyramid anatomy", "dorsal hump anatomy"],
        "cartilaginous": ["cartilaginous nasal dorsum", "upper lateral cartilage", "dorsal hump anatomy"],
        "clinical_evaluation": ["rhinoplasty preoperative evaluation", "nasal examination", "dorsal hump assessment"],
        "evaluation_criteria": ["rhinoplasty preoperative evaluation", "nasal examination", "dorsal hump assessment"],
        "contour_assessment": ["rhinoplasty postoperative dorsal contour", "dorsal irregularity"],
        "post_op_contour": ["rhinoplasty postoperative dorsal contour", "dorsal irregularity"],
        "misconception": ["rhinoplasty dorsal hump patient education"],
        "piezosurgery": ["piezoelectric", "osteotomy"],
        "piezo": ["piezoelectric", "osteotomy"],
        "preservation": ["dorsal preservation"],
        "osteotomy": ["osteotomy"],
        "traditional": ["dorsal hump reduction", "osteotomy"],
        "walk": ["postoperative", "walking", "physical activity"],
        "exercise": ["postoperative", "exercise", "physical activity"],
        "sport": ["postoperative", "sports", "exercise"],
        "heavy": ["postoperative", "strenuous exercise", "weight lifting"],
        "strength": ["postoperative", "strength training", "weight lifting"],
        "contact": ["postoperative", "contact sports", "nasal trauma"],
        "swim": ["postoperative", "swimming", "water exposure"],
        "pool": ["postoperative", "swimming", "pool"],
        "sauna": ["postoperative", "sauna", "heat"],
        "yoga": ["postoperative", "yoga", "bending"],
        "bleed": ["postoperative", "bleeding", "hemorrhage"],
        "swelling": ["postoperative", "edema", "swelling"],
        "oedema": ["postoperative", "edema", "swelling"],
        "edema": ["postoperative", "edema", "swelling"],
        "pain": ["postoperative", "pain"],
        "antibiotic": ["postoperative", "antibiotic"],
        "steroid": ["postoperative", "steroid"],
        "spray": ["postoperative", "nasal spray"],
        "saline": ["postoperative", "saline irrigation"],
    }
    added: list[str] = []
    for needle, words in vocab.items():
        if needle in key:
            added.extend(words)
    if not added:
        tokens = [t for t in re.split(r"[_\W]+", key) if len(t) > 3 and not t.isdigit()]
        added.extend(tokens[:4])
    if worker_id in {"DRB-MED", "DRB-GSC"} and not added:
        added.extend(["nasal anatomy", "rhinoplasty"])
    return clean_text(" ".join(dict.fromkeys(base + added)), 500)


def article_type_tier(types: list[str]) -> tuple[str, str]:
    joined = " ".join(types).lower()
    if any(term in joined for term in ("systematic review", "meta-analysis", "practice guideline", "guideline")):
        return "TIER_1_SYNTHESIS_OR_GUIDELINE", "systematic_review_or_guideline"
    if any(term in joined for term in ("randomized controlled trial", "clinical trial")):
        return "TIER_2_PRIMARY_STUDY", "clinical_trial"
    return "TIER_2_PRIMARY_OR_INDEXED_STUDY", "journal_article"


def pubmed_search(query: str, retmax: int = 5) -> list[dict[str, Any]]:
    params = {"db": "pubmed", "term": query, "retmax": str(retmax), "retmode": "json", "sort": "relevance"}
    api_key = os.environ.get("NCBI_API_KEY", "").strip()
    if api_key:
        params["api_key"] = api_key
    data = http_get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(params))
    ids = list((data.get("esearchresult") or {}).get("idlist") or [])
    if not ids:
        return []
    fetch_params = {"db": "pubmed", "id": ",".join(ids), "retmode": "xml"}
    if api_key:
        fetch_params["api_key"] = api_key
    root = ET.fromstring(http_get_text("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urllib.parse.urlencode(fetch_params)))
    out: list[dict[str, Any]] = []
    for article in root.findall(".//PubmedArticle"):
        pmid = clean_text(article.findtext(".//MedlineCitation/PMID"))
        title_node = article.find(".//Article/ArticleTitle")
        title = clean_text("".join(title_node.itertext()) if title_node is not None else "")
        abstracts = []
        for node in article.findall(".//Article/Abstract/AbstractText"):
            label = node.attrib.get("Label") or ""
            text = clean_text("".join(node.itertext()))
            abstracts.append((label + ": " if label else "") + text)
        abstract = clean_text(" ".join(abstracts), MAX_EXCERPT)
        types = [clean_text(x.text) for x in article.findall(".//Article/PublicationTypeList/PublicationType") if x.text]
        tier, source_type = article_type_tier(types)
        doi = ""
        for aid in article.findall(".//PubmedData/ArticleIdList/ArticleId"):
            if aid.attrib.get("IdType") == "doi":
                doi = clean_text(aid.text)
                break
        year = clean_text(article.findtext(".//Article/Journal/JournalIssue/PubDate/Year"))
        medline = clean_text(article.findtext(".//Article/Journal/JournalIssue/PubDate/MedlineDate"))
        out.append({
            "source_id": f"SRC-PM-{pmid}" if pmid else "SRC-PM-" + hashlib.sha1(title.encode()).hexdigest()[:12],
            "provider": "pubmed", "title": title,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "", "doi": doi, "pmid": pmid,
            "publication_date": year or medline, "source_type": source_type, "authority_tier": tier,
            "excerpt": abstract or title, "metadata": {"publication_types": types},
        })
    return out


def europe_pmc_search(query: str, page_size: int = 4) -> list[dict[str, Any]]:
    params = {"query": query, "format": "json", "pageSize": str(page_size), "resultType": "core"}
    data = http_get_json("https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(params))
    out: list[dict[str, Any]] = []
    for item in ((data.get("resultList") or {}).get("result") or []):
        pmid, doi, title = clean_text(item.get("pmid")), clean_text(item.get("doi")), clean_text(item.get("title"))
        pub_types = item.get("pubTypeList") or {}
        types = pub_types.get("pubType") if isinstance(pub_types, dict) else []
        types = types if isinstance(types, list) else [types]
        tier, source_type = article_type_tier([clean_text(x) for x in types])
        source_id = f"SRC-PM-{pmid}" if pmid else ("SRC-EPMC-" + hashlib.sha1((doi or title).encode()).hexdigest()[:12])
        out.append({
            "source_id": source_id, "provider": "europe_pmc", "title": title,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "https://europepmc.org/article/MED/" + clean_text(item.get("id")),
            "doi": doi, "pmid": pmid, "publication_date": clean_text(item.get("firstPublicationDate") or item.get("pubYear")),
            "source_type": source_type, "authority_tier": tier,
            "excerpt": clean_text(item.get("abstractText"), MAX_EXCERPT) or title,
            "metadata": {"journal": clean_text(item.get("journalTitle")), "cited_by": item.get("citedByCount")},
        })
    return out


def inverted_abstract(value: Any) -> str:
    if not isinstance(value, dict):
        return ""
    positions: list[tuple[int, str]] = []
    for word, indexes in value.items():
        if isinstance(indexes, list):
            positions.extend((index, word) for index in indexes if isinstance(index, int))
    return clean_text(" ".join(word for _, word in sorted(positions)), MAX_EXCERPT)


def openalex_search(query: str, page_size: int = 4) -> list[dict[str, Any]]:
    params: dict[str, str] = {"search": query, "per-page": str(page_size)}
    mailto = os.environ.get("OPENALEX_MAILTO", "").strip()
    if mailto:
        params["mailto"] = mailto
    data = http_get_json("https://api.openalex.org/works?" + urllib.parse.urlencode(params))
    out = []
    for item in data.get("results") or []:
        oid = clean_text(item.get("id")).rsplit("/", 1)[-1]
        title = clean_text(item.get("display_name") or item.get("title"))
        doi = clean_text(item.get("doi")).replace("https://doi.org/", "")
        out.append({
            "source_id": f"SRC-OA-{oid}" if oid else "SRC-OA-" + hashlib.sha1(title.encode()).hexdigest()[:12],
            "provider": "openalex", "title": title, "url": clean_text(item.get("id")), "doi": doi, "pmid": "",
            "publication_date": clean_text(item.get("publication_date") or item.get("publication_year")),
            "source_type": "scholarly_discovery_record", "authority_tier": "TIER_3_DISCOVERY_METADATA",
            "excerpt": inverted_abstract(item.get("abstract_inverted_index")) or title,
            "metadata": {"type": clean_text(item.get("type")), "cited_by": item.get("cited_by_count")},
        })
    return out


def crossref_search(query: str, rows: int = 3) -> list[dict[str, Any]]:
    params = {"query.bibliographic": query, "rows": str(rows)}
    mailto = os.environ.get("CROSSREF_MAILTO", "").strip()
    if mailto:
        params["mailto"] = mailto
    data = http_get_json("https://api.crossref.org/works?" + urllib.parse.urlencode(params))
    out = []
    for item in ((data.get("message") or {}).get("items") or []):
        doi = clean_text(item.get("DOI")); title_raw = item.get("title") or []
        title = clean_text(title_raw[0] if isinstance(title_raw, list) and title_raw else title_raw)
        date_parts = (((item.get("published") or {}).get("date-parts") or [[None]])[0])
        out.append({
            "source_id": "SRC-CR-" + hashlib.sha1((doi or title).encode()).hexdigest()[:12],
            "provider": "crossref", "title": title, "url": ("https://doi.org/" + doi) if doi else clean_text(item.get("URL")),
            "doi": doi, "pmid": "", "publication_date": "-".join(str(x) for x in date_parts if x is not None),
            "source_type": clean_text(item.get("type")) or "crossref_metadata", "authority_tier": "TIER_3_DISCOVERY_METADATA",
            "excerpt": title, "metadata": {"container_title": clean_text((item.get("container-title") or [""])[0])},
        })
    return out


def clinical_trials_search(query: str, page_size: int = 3) -> list[dict[str, Any]]:
    data = http_get_json("https://clinicaltrials.gov/api/v2/studies?" + urllib.parse.urlencode({"query.term": query, "pageSize": str(page_size), "format": "json"}))
    out = []
    for study in data.get("studies") or []:
        proto = study.get("protocolSection") or {}; identification = proto.get("identificationModule") or {}
        status = proto.get("statusModule") or {}; description = proto.get("descriptionModule") or {}
        nct = clean_text(identification.get("nctId")); title = clean_text(identification.get("briefTitle") or identification.get("officialTitle"))
        out.append({
            "source_id": f"SRC-CT-{nct}" if nct else "SRC-CT-" + hashlib.sha1(title.encode()).hexdigest()[:12],
            "provider": "clinical_trials", "title": title, "url": f"https://clinicaltrials.gov/study/{nct}" if nct else "",
            "doi": "", "pmid": "", "publication_date": clean_text((status.get("studyFirstPostDateStruct") or {}).get("date")),
            "source_type": "clinical_trial_registry", "authority_tier": "TIER_2_REGISTRY_CONTEXT",
            "excerpt": clean_text(description.get("briefSummary"), MAX_EXCERPT) or title,
            "metadata": {"nct_id": nct, "overall_status": clean_text(status.get("overallStatus"))},
        })
    return out


def likely_drug_term(claim: dict[str, Any]) -> str:
    key = claim["claim_key"].lower()
    markers = ("drug", "medication", "antibiotic", "steroid", "aspirin", "ibuprofen", "acetaminophen", "paracetamol", "saline", "spray")
    for marker in markers:
        if marker in key:
            return marker
    return ""


def rxnorm_lookup(term: str) -> list[dict[str, Any]]:
    if not term:
        return []
    data = http_get_json("https://rxnav.nlm.nih.gov/REST/approximateTerm.json?" + urllib.parse.urlencode({"term": term, "maxEntries": "3"}))
    out = []
    for item in ((data.get("approximateGroup") or {}).get("candidate") or []):
        rxcui = clean_text(item.get("rxcui")); name = clean_text(item.get("name") or term)
        out.append({
            "source_id": f"SRC-RX-{rxcui}" if rxcui else "SRC-RX-" + hashlib.sha1(name.encode()).hexdigest()[:12],
            "provider": "rxnorm", "title": name, "url": f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}.json" if rxcui else "",
            "doi": "", "pmid": "", "publication_date": "", "source_type": "medication_terminology",
            "authority_tier": "TIER_1_OFFICIAL_TERMINOLOGY_NOT_EFFICACY",
            "excerpt": f"RxNorm normalised medication concept: {name} (RxCUI {rxcui}).", "metadata": {"rxcui": rxcui, "score": item.get("score")},
        })
    return out


def dailymed_lookup(term: str) -> list[dict[str, Any]]:
    if not term:
        return []
    data = http_get_json("https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?" + urllib.parse.urlencode({"drug_name": term, "pagesize": "3", "page": "1"}))
    out = []
    for item in data.get("data") or []:
        setid = clean_text(item.get("setid")); title = clean_text(item.get("title"))
        out.append({
            "source_id": f"SRC-DM-{setid}" if setid else "SRC-DM-" + hashlib.sha1(title.encode()).hexdigest()[:12],
            "provider": "dailymed", "title": title,
            "url": f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={setid}" if setid else "",
            "doi": "", "pmid": "", "publication_date": clean_text(item.get("published_date")),
            "source_type": "official_us_structured_product_label", "authority_tier": "TIER_1_OFFICIAL_LABEL",
            "excerpt": title, "metadata": {"setid": setid},
        })
    return out


def openfda_lookup(term: str) -> list[dict[str, Any]]:
    if not term:
        return []
    params = {"search": f'openfda.generic_name:"{term}"', "limit": "3"}
    api_key = os.environ.get("OPENFDA_API_KEY", "").strip()
    if api_key:
        params["api_key"] = api_key
    data = http_get_json("https://api.fda.gov/drug/label.json?" + urllib.parse.urlencode(params))
    out = []
    for item in data.get("results") or []:
        ofda = item.get("openfda") or {}; setid = clean_text(item.get("set_id")); names = ofda.get("generic_name") or ofda.get("brand_name") or [term]
        title = clean_text(names[0] if isinstance(names, list) and names else names); sections = []
        for key in ("indications_and_usage", "contraindications", "warnings", "dosage_and_administration"):
            value = item.get(key)
            if isinstance(value, list) and value:
                sections.append(clean_text(value[0], 400))
        out.append({
            "source_id": "SRC-FDA-" + (setid or hashlib.sha1(title.encode()).hexdigest()[:12]), "provider": "openfda",
            "title": title, "url": "https://api.fda.gov/drug/label.json", "doi": "", "pmid": "",
            "publication_date": clean_text(item.get("effective_time")), "source_type": "official_us_drug_label_data",
            "authority_tier": "TIER_1_REGULATOR_LABEL", "excerpt": clean_text(" ".join(sections), MAX_EXCERPT) or title,
            "metadata": {"set_id": setid, "application_number": ofda.get("application_number")},
        })
    return out


def semantic_scholar_search(query: str, limit: int = 3) -> list[dict[str, Any]]:
    params = {"query": query, "limit": str(limit), "fields": "title,year,abstract,url,externalIds,publicationTypes,journal"}
    req = urllib.request.Request("https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(params), headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "").strip()
    if key:
        req.add_header("x-api-key", key)
    with urllib.request.urlopen(req, timeout=25) as response:
        data = json.loads(response.read().decode("utf-8", errors="replace"))
    out = []
    for item in data.get("data") or []:
        ext = item.get("externalIds") or {}; pmid = clean_text(ext.get("PubMed")); doi = clean_text(ext.get("DOI")); sid = clean_text(item.get("paperId")); title = clean_text(item.get("title"))
        out.append({
            "source_id": f"SRC-PM-{pmid}" if pmid else ("SRC-SS-" + (sid or hashlib.sha1(title.encode()).hexdigest()[:12])),
            "provider": "semantic_scholar", "title": title, "url": clean_text(item.get("url")), "doi": doi, "pmid": pmid,
            "publication_date": clean_text(item.get("year")), "source_type": "scholarly_discovery_record",
            "authority_tier": "TIER_3_DISCOVERY_METADATA", "excerpt": clean_text(item.get("abstract"), MAX_EXCERPT) or title,
            "metadata": {"publication_types": item.get("publicationTypes") or []},
        })
    return out


def source_rank(source: dict[str, Any]) -> tuple[int, int]:
    provider = source.get("provider"); tier = str(source.get("authority_tier") or "")
    if provider in {"openfda", "dailymed"}: return (0, 0)
    if "TIER_1" in tier: return (1, 0)
    if provider in {"pubmed", "europe_pmc"}: return (2, 0)
    if provider == "clinical_trials": return (3, 0)
    if provider == "rxnorm": return (4, 0)
    return (5, 0)


def dedupe_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set(); out = []
    for source in sorted(sources, key=source_rank):
        pmid = clean_text(source.get("pmid")); doi = clean_text(source.get("doi")).lower(); title = clean_text(source.get("title")).lower()
        key = ("pmid:" + pmid) if pmid else (("doi:" + doi) if doi else ("title:" + title))
        if not key or key in seen: continue
        seen.add(key); out.append(source)
    return out


def retrieve_for_claim(claim: dict[str, Any], worker_id: str, state: dict[str, Any] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    query = query_terms(worker_id, claim, state); sources: list[dict[str, Any]] = []; status: dict[str, Any] = {"query": query}
    def run_provider(name: str, fn) -> None:
        started = time.monotonic()
        try:
            result = fn(); sources.extend(result)
            status[name] = {"status": "PASS", "count": len(result), "latency_ms": round((time.monotonic() - started) * 1000)}
        except urllib.error.HTTPError as exc:
            status[name] = {"status": "HTTP_ERROR", "http": exc.code, "latency_ms": round((time.monotonic() - started) * 1000)}
        except Exception as exc:
            status[name] = {"status": "ERROR", "error": type(exc).__name__, "latency_ms": round((time.monotonic() - started) * 1000)}
    run_provider("pubmed", lambda: pubmed_search(query, 5))
    run_provider("europe_pmc", lambda: europe_pmc_search(query, 4))
    run_provider("clinical_trials", lambda: clinical_trials_search(query, 2))
    run_provider("openalex", lambda: openalex_search(query, 3))
    run_provider("crossref", lambda: crossref_search(query, 2))
    drug = likely_drug_term(claim)
    if drug:
        run_provider("rxnorm", lambda: rxnorm_lookup(drug)); run_provider("dailymed", lambda: dailymed_lookup(drug)); run_provider("openfda", lambda: openfda_lookup(drug))
    else:
        status["rxnorm"] = {"status": "NOT_APPLICABLE", "count": 0}; status["dailymed"] = {"status": "NOT_APPLICABLE", "count": 0}; status["openfda"] = {"status": "NOT_APPLICABLE", "count": 0}
    ranked = dedupe_sources(sources); authoritative = [x for x in ranked if x.get("provider") in APPROVABLE_PROVIDERS]
    if len(authoritative) < 2:
        run_provider("semantic_scholar", lambda: semantic_scholar_search(query, 3)); ranked = dedupe_sources(sources)
    else:
        status["semantic_scholar"] = {"status": "SKIPPED_SUFFICIENT_PRIMARY_DISCOVERY", "count": 0}
    return ranked[:MAX_EVIDENCE_PER_CLAIM], status


def numeric_tokens(text: str) -> set[str]:
    trans = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩٫", "01234567890123456789.")
    return set(re.findall(r"\b\d+(?:\.\d+)?%?\b", (text or "").translate(trans)))


def verifier_prompt(chain_id: str, claims: list[dict[str, Any]], evidence_by_claim: dict[str, list[dict[str, Any]]]) -> str:
    compact_claims = []
    for claim in claims:
        refs = [{"source_id": s["source_id"], "provider": s["provider"], "authority_tier": s["authority_tier"], "title": s["title"], "publication_date": s.get("publication_date") or "", "pmid": s.get("pmid") or "", "doi": s.get("doi") or "", "excerpt": clean_text(s.get("excerpt"), MAX_EXCERPT)} for s in evidence_by_claim.get(claim["claim_key"], [])]
        compact_claims.append({**claim, "retrieved_evidence": refs})
    payload = json.dumps(compact_claims, ensure_ascii=False, separators=(",", ":"))
    return (
        "You are an INDEPENDENT medical evidence verifier. You are not the drafter. Judge each Persian candidate claim ONLY against the retrieved source metadata/excerpts supplied below. "
        "Do not use memory, hidden knowledge, browsing, or unstated facts. Discovery-only records (OpenAlex, Crossref, Semantic Scholar) may help locate literature but cannot alone authorise a medical claim. "
        "ClinicalTrials.gov is registry context, not proof of efficacy. RxNorm is terminology only. Official FDA/DailyMed labels can authorise label-native medication facts only. "
        "For each claim return verdict SUPPORTED, SUPPORTED_WITH_LIMITATIONS, INSUFFICIENT_EVIDENCE, or CONTRADICTED. SUPPORTED requires direct support from at least one authoritative retrieved source. "
        "If wording is broader/more certain/more specific than evidence, use SUPPORTED_WITH_LIMITATIONS and rewrite allowed_wording conservatively in Persian. Never add a number, time interval, dose, outcome, warning, or causal mechanism unless it appears in the supplied evidence. "
        "If a precise postoperative timeline is not directly supported, remove the precise timeline. For unsupported claims, allowed_wording must be an empty string. Preserve uncertainty and population limits. "
        "Return strict JSON only with schema: {overall_decision:string,claims:[{claim_key:string,verdict:string,allowed_wording:string,evidence_strength:string,source_ids:[string],rationale:string,uncertainty:string,medical_risk:string}]}. "
        f"Chain: {chain_id}. Candidate/evidence packet: {payload}"
    )


class VerifierError(RuntimeError):
    def __init__(self, code: str, job_id: str | None = None):
        self.code = code
        self.job_id = job_id
        super().__init__(code)


def queue_and_run_verifier(site_key: str, chain_id: str, prompt: str) -> tuple[str, dict[str, Any]]:
    job_id = None
    try:
        queue = [AI_CLI, "queue", "--site", site_key, "--task-type", "medical_evidence_verify", "--risk", "L3", "--prompt", prompt, "--format", "json", "--provider", "gemini_a", "--max-output-tokens", "4096", "--source-ref", f"medical-evidence:{chain_id}"]
        proc = subprocess.run(queue, capture_output=True, text=True, timeout=60, env=os.environ.copy())
        if proc.returncode != 0:
            raise VerifierError("VERIFIER_QUEUE_FAILED")
        queued_id = json.loads(proc.stdout).get("job_id")
        if not isinstance(queued_id, str) or not queued_id.strip():
            raise VerifierError("VERIFIER_JOB_ID_MISSING")
        job_id = queued_id.strip()
        run = subprocess.run([AI_CLI, "run", job_id], capture_output=True, text=True, timeout=240, env=os.environ.copy())
        if run.returncode != 0:
            raise VerifierError("VERIFIER_RUN_FAILED", job_id)
        run_data = json.loads(run.stdout)
        if run_data.get("status") != "candidate_ready":
            raise VerifierError("VERIFIER_CANDIDATE_NOT_READY", job_id)
        with connect() as conn:
            result = conn.execute("SELECT parsed_json,raw_text,provider,model FROM ai_results WHERE job_id=? ORDER BY created_at DESC LIMIT 1", (job_id,)).fetchone()
        if result is None:
            raise VerifierError("VERIFIER_RESULT_MISSING", job_id)
        parsed = json.loads(result["parsed_json"]) if result["parsed_json"] else recover_json_object(result["raw_text"] or "")
        if not isinstance(parsed, dict):
            raise VerifierError("VERIFIER_OUTPUT_INVALID", job_id)
        parsed["_verifier_provider"] = result["provider"]
        parsed["_verifier_model"] = result["model"]
        return job_id, parsed
    except VerifierError:
        raise
    except Exception as exc:
        raise VerifierError("VERIFIER_EXECUTION_FAILED", job_id) from exc


RESET_CONDITION = "verifier dependency repaired and explicit bounded retry authorised"


def record_verifier_failure(row, run_id, code, verifier_job_id):
    """Use the existing pd_outbox owner; never create a second replay queue."""
    key = "medical-verifier:" + hashlib.sha256(
        (str(row["chain_id"]) + "|" + code).encode()
    ).hexdigest()
    payload = {"chain_id": row["chain_id"], "verifier_job_id": verifier_job_id,
               "failure_class": code}
    argv = [
        sys.executable, str(ROOT / "deploy/run_ledger_outbox.py"), "persist-failure",
        "--worker", str(row["worker_id"]), "--run-id", run_id,
        "--site", str(row["site_key"]), "--event-type", "medical_verifier_failure",
        "--replay-state", "parked", "--final-state", "PARKED_BLOCKER",
        "--failure-class", code, "--reason", code,
        "--stable-id", key, "--idempotency-key", key,
        "--factory-task-id", str(row["chain_id"]),
        "--reset-condition", RESET_CONDITION,
        "--payload-json", json.dumps(payload, separators=(",", ":")),
    ]
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=30)
        obj = json.loads(proc.stdout) if proc.returncode == 0 else {}
        if obj.get("status") == "PERSISTED" and obj.get("replay") == "parked":
            return {"replay": "parked", "stable_id": key}
    except Exception:
        pass
    return {"replay": "UNAVAILABLE", "reason": "FAILURE_LEDGER_UNAVAILABLE"}


def deterministic_verdicts(chain_id: str, claims: list[dict[str, Any]], evidence_by_claim: dict[str, list[dict[str, Any]]], verifier: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidate_map = {c["claim_key"]: c for c in claims}; raw_verdicts = verifier.get("claims") if isinstance(verifier.get("claims"), list) else []
    verifier_map = {clean_text(v.get("claim_key")): v for v in raw_verdicts if isinstance(v, dict)}; approved = []; rejected = []
    for key, candidate in candidate_map.items():
        v = verifier_map.get(key) or {}; verdict = clean_text(v.get("verdict")).upper()
        selected_ids = [clean_text(x) for x in (v.get("source_ids") or []) if clean_text(x)] if isinstance(v.get("source_ids"), list) else []
        available = {str(s["source_id"]): s for s in evidence_by_claim.get(key, [])}; selected_ids = [sid for sid in selected_ids if sid in available]
        selected_sources = [available[sid] for sid in selected_ids]; authoritative_selected = [s for s in selected_sources if s.get("provider") in APPROVABLE_PROVIDERS]
        allowed_wording = clean_text(v.get("allowed_wording"), 1800); reason = clean_text(v.get("rationale"), 1200)
        uncertainty = clean_text(v.get("uncertainty"), 900) or candidate.get("uncertainty") or ""; strength = clean_text(v.get("evidence_strength") or "UNRATED").upper()
        risk = clean_text(v.get("medical_risk") or candidate.get("medical_risk") or "M2").upper(); risk = risk if risk in {"M0","M1","M2","M3","M4"} else candidate.get("medical_risk") or "M2"
        gate_errors = []
        if verdict not in {"SUPPORTED", "SUPPORTED_WITH_LIMITATIONS"}: gate_errors.append("verifier_not_supportive")
        if not allowed_wording: gate_errors.append("missing_allowed_wording")
        if not authoritative_selected: gate_errors.append("no_authoritative_selected_source")
        nums = numeric_tokens(allowed_wording)
        if nums:
            evidence_text = " ".join(clean_text(s.get("title")) + " " + clean_text(s.get("excerpt")) for s in authoritative_selected)
            missing_nums = sorted(nums - numeric_tokens(evidence_text))
            if missing_nums: gate_errors.append("numbers_not_present_in_evidence:" + ",".join(missing_nums))
        if risk == "M4": gate_errors.append("m4_not_automatable")
        claim_id = "CLM-AUTO-" + hashlib.sha1((chain_id + "|" + key + "|" + allowed_wording).encode()).hexdigest()[:14].upper()
        record = {"claim_id": claim_id if not gate_errors else "", "claim_key": key, "candidate_wording": candidate["candidate_wording"], "allowed_wording": allowed_wording if not gate_errors else "", "verdict": verdict if not gate_errors else "INSUFFICIENT_EVIDENCE", "evidence_strength": strength, "medical_risk": risk, "source_ids": selected_ids, "rationale": reason + ((" | deterministic_gate=" + ";".join(gate_errors)) if gate_errors else ""), "uncertainty": uncertainty}
        (rejected if gate_errors else approved).append(record)
    return approved, rejected


def save_evidence_run(row: sqlite3.Row, state: dict[str, Any], run_id: str, claims: list[dict[str, Any]], evidence_by_claim: dict[str, list[dict[str, Any]]], provider_status: dict[str, Any], verifier_job_id: str | None, verifier_result: dict[str, Any] | None, approved: list[dict[str, Any]], rejected: list[dict[str, Any]], status: str) -> None:
    packet = {"run_id": run_id, "chain_id": row["chain_id"], "created_at": utcnow(), "claims": claims, "evidence_by_claim": evidence_by_claim, "provider_status": provider_status, "verifier_job_id": verifier_job_id, "verifier_provider": (verifier_result or {}).get("_verifier_provider"), "verifier_model": (verifier_result or {}).get("_verifier_model"), "approved_claims": approved, "rejected_claims": rejected, "status": status}
    source_rows = [(claim_key, s) for claim_key, values in evidence_by_claim.items() for s in values]; ts = utcnow()
    with connect() as conn:
        ensure_schema(conn)
        conn.execute("INSERT OR REPLACE INTO medical_evidence_runs(run_id,chain_id,status,claim_count,source_count,approved_count,rejected_count,verifier_job_id,provider_status_json,packet_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (run_id,row["chain_id"],status,len(claims),len(source_rows),len(approved),len(rejected),verifier_job_id,json.dumps(provider_status,ensure_ascii=False,separators=(",",":")),json.dumps(packet,ensure_ascii=False,separators=(",",":")),ts,ts))
        for claim_key, source in source_rows:
            conn.execute("INSERT OR IGNORE INTO medical_evidence_sources(run_id,chain_id,claim_key,source_id,provider,title,url,doi,pmid,publication_date,source_type,authority_tier,excerpt,metadata_json,retrieved_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (run_id,row["chain_id"],claim_key,source["source_id"],source["provider"],source["title"],source.get("url") or "",source.get("doi") or "",source.get("pmid") or "",source.get("publication_date") or "",source.get("source_type") or "",source["authority_tier"],source.get("excerpt") or "",json.dumps(source.get("metadata") or {},ensure_ascii=False),ts))
        for verdict in approved + rejected:
            conn.execute("INSERT OR REPLACE INTO medical_claim_verdicts(run_id,chain_id,claim_id,claim_key,candidate_wording,allowed_wording,verdict,evidence_strength,medical_risk,source_ids_json,rationale,uncertainty,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (run_id,row["chain_id"],verdict.get("claim_id") or "",verdict["claim_key"],verdict["candidate_wording"],verdict.get("allowed_wording") or "",verdict["verdict"],verdict.get("evidence_strength") or "",verdict.get("medical_risk") or "",json.dumps(verdict.get("source_ids") or [],ensure_ascii=False),verdict.get("rationale") or "",verdict.get("uncertainty") or "",ts))
        fresh = conn.execute("SELECT state_json,stage FROM content_ladder WHERE chain_id=?", (row["chain_id"],)).fetchone(); fresh_state = json.loads(fresh["state_json"] or "{}") if fresh else state
        fresh_state["evidence_run_id"] = run_id; fresh_state["evidence_packet"] = packet
        fresh_state["approved_claims"] = [{"claim_id":v["claim_id"],"claim_key":v["claim_key"],"allowed_wording":v["allowed_wording"],"evidence_strength":v.get("evidence_strength") or "","source_ids":v.get("source_ids") or [],"uncertainty":v.get("uncertainty") or "","medical_risk":v.get("medical_risk") or "M2"} for v in approved]
        fresh_state["verification_status"] = "APPROVED" if approved else "INSUFFICIENT_EVIDENCE"; new_status = "ready" if approved else "awaiting_claim_approval"
        risk_order = {"M0":0,"M1":1,"M2":2,"M3":3,"M4":4}; max_risk = max([fresh_state.get("medical_risk") or "M1"] + [x.get("medical_risk") or "M1" for x in approved], key=lambda x: risk_order.get(x,2)); fresh_state["medical_risk"] = max_risk
        current_review = str(fresh_state.get("human_review_status") or "").upper()
        if max_risk == "M4":
            fresh_state["human_review_status"] = "BLOCKED"
            new_status = "blocked_m4"
        elif max_risk == "M3":
            if current_review != "APPROVED":
                fresh_state["human_review_status"] = "PENDING"
        else:
            fresh_state["human_review_status"] = "NOT_REQUIRED"
        if status == "VERIFIER_FAILED":
            # Deterministic verifier-contract failures need a repaired dependency
            # and explicit retry; the hourly seed loop must not replay them.
            new_status = "blocked_verifier"
            fresh_state["verification_status"] = "VERIFIER_FAILED"
            fresh_state["verifier_reset_condition"] = RESET_CONDITION
        # Evidence belongs to the stage observed at bootstrap. A concurrent
        # worker or human may already have advanced or changed that stage.
        updated = conn.execute(
            "UPDATE content_ladder SET status=?,state_json=?,updated_at=? "
            "WHERE chain_id=? AND stage=? AND state_json=? "
            "AND status IN ('awaiting_claim_approval','ready')",
            (new_status, json.dumps(fresh_state,ensure_ascii=False,separators=(",",":")),
             ts, row["chain_id"], row["stage"], fresh["state_json"] if fresh else "{}"),
        )
        if updated.rowcount == 0:
            return  # Keep the evidence receipt; preserve the newer chain state.
        conn.execute("INSERT INTO content_ladder_events(chain_id,stage,event_type,detail_json,created_at) VALUES(?,?,?,?,?)", (row["chain_id"],fresh["stage"] if fresh else row["stage"],"medical_evidence_verified",json.dumps({"run_id":run_id,"approved":len(approved),"rejected":len(rejected),"status":new_status},ensure_ascii=False),ts))


def process_chain(chain_id: str) -> dict[str, Any]:
    row, state = load_chain(chain_id)
    if row["factory_lane"] != "medical": return {"chain_id":chain_id,"status":"SKIPPED_NOT_MEDICAL"}
    if row["stage"] != "D" or row["status"] not in {"awaiting_claim_approval","ready"}: return {"chain_id":chain_id,"status":"SKIPPED_NOT_AT_EVIDENCE_GATE","stage":row["stage"],"chain_status":row["status"]}
    if state.get("verification_status") == "APPROVED" and state.get("approved_claims"): return {"chain_id":chain_id,"status":"ALREADY_APPROVED","approved":len(state.get("approved_claims") or [])}
    claims = candidate_claims_from_state(state); run_id = "EVD-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex.upper()
    if not claims:
        save_evidence_run(row,state,run_id,[],{}, {"candidate_parser":{"status":"NO_COMPLETE_CLAIMS"}},None,None,[],[],"NO_CANDIDATE_CLAIMS")
        return {"chain_id":chain_id,"run_id":run_id,"status":"NO_CANDIDATE_CLAIMS","approved":0}
    evidence_by_claim = {}; provider_status = {}
    for claim in claims:
        sources,statuses = retrieve_for_claim(claim,row["worker_id"],state)
        evidence_by_claim[claim["claim_key"]] = sources; provider_status[claim["claim_key"]] = statuses
    verifier_job_id = None; verifier_result = None; approved = []; rejected = []
    try:
        verifier_job_id,verifier_result = queue_and_run_verifier(row["site_key"],chain_id,verifier_prompt(chain_id,claims,evidence_by_claim)); approved,rejected = deterministic_verdicts(chain_id,claims,evidence_by_claim,verifier_result); status = "APPROVED" if approved else "INSUFFICIENT_EVIDENCE"
    except Exception as exc:
        status = "VERIFIER_FAILED"
        verifier_job_id = getattr(exc, "job_id", None) or verifier_job_id
        failure_code = getattr(exc, "code", "VERIFIER_VALIDATION_FAILED")
        provider_status["verifier"] = {"status": "ERROR", "error": failure_code}

        rejected = [{"claim_id":"","claim_key":c["claim_key"],"candidate_wording":c["candidate_wording"],"allowed_wording":"","verdict":"INSUFFICIENT_EVIDENCE","evidence_strength":"UNVERIFIED","medical_risk":c["medical_risk"],"source_ids":[],"rationale":"Independent verifier failed; fail closed.","uncertainty":c.get("uncertainty") or ""} for c in claims]
    save_evidence_run(row,state,run_id,claims,evidence_by_claim,provider_status,verifier_job_id,verifier_result,approved,rejected,status)
    recovery = record_verifier_failure(row, run_id, failure_code, verifier_job_id) if status == "VERIFIER_FAILED" else {}
    return {**recovery, "chain_id":chain_id,"run_id":run_id,"status":status,"claims":len(claims),"approved":len(approved),"rejected":len(rejected),"source_count":sum(len(v) for v in evidence_by_claim.values()),"verifier_job_id":verifier_job_id,"provider_status":provider_status}


def pending_chain_ids(limit: int) -> list[str]:
    with connect() as conn:
        rows = conn.execute("SELECT chain_id FROM content_ladder WHERE factory_lane='medical' AND stage='D' AND status='awaiting_claim_approval' ORDER BY updated_at ASC LIMIT ?", (max(1,min(int(limit),20)),)).fetchall()
    return [str(r["chain_id"]) for r in rows]


def run_pending(limit: int) -> list[dict[str, Any]]:
    return [process_chain(chain_id) for chain_id in pending_chain_ids(limit)]


def latest(chain_id: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
    with connect() as conn:
        ensure_schema(conn)
        if chain_id:
            rows = conn.execute("SELECT run_id,chain_id,status,claim_count,source_count,approved_count,rejected_count,verifier_job_id,created_at,updated_at FROM medical_evidence_runs WHERE chain_id=? ORDER BY updated_at DESC LIMIT ?", (chain_id,int(limit))).fetchall()
        else:
            rows = conn.execute("SELECT run_id,chain_id,status,claim_count,source_count,approved_count,rejected_count,verifier_job_id,created_at,updated_at FROM medical_evidence_runs ORDER BY updated_at DESC LIMIT ?", (int(limit),)).fetchall()
    return [dict(r) for r in rows]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Retrieve real medical evidence and independently verify Stage-C claims"); sub = p.add_subparsers(dest="cmd",required=True)
    one = sub.add_parser("run"); one.add_argument("chain_id")
    pending = sub.add_parser("run-pending"); pending.add_argument("--limit",type=int,default=8)
    latest_p = sub.add_parser("latest"); latest_p.add_argument("--chain-id"); latest_p.add_argument("--limit",type=int,default=20)
    sub.add_parser("init"); return p


def main() -> int:
    args = build_parser().parse_args()
    with connect() as conn: ensure_schema(conn)
    if args.cmd == "init": print(json.dumps({"status":"ok","db":str(DB)},ensure_ascii=False)); return 0
    if args.cmd == "run":
        result = process_chain(args.chain_id)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 1 if result.get("status") == "VERIFIER_FAILED" else 0
    if args.cmd == "run-pending":
        results = run_pending(args.limit)
        print(json.dumps({"processed":len(results),"results":results},ensure_ascii=False,indent=2))
        return 1 if any(r.get("status") == "VERIFIER_FAILED" for r in results) else 0
    if args.cmd == "latest": print(json.dumps(latest(args.chain_id,args.limit),ensure_ascii=False,indent=2)); return 0
    return 2


if __name__ == "__main__": sys.exit(main())
