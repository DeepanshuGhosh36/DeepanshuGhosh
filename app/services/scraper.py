from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.shl.com/solutions/products/product-catalog/"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "catalog.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SHL-Catalog-Scraper/1.0)"}


def _get(url: str, retries: int = 4, timeout: int = 30) -> str:
    last_error: Optional[Exception] = None
    for i in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(1.2 * (i + 1))
    raise RuntimeError(f"Failed fetching {url}: {last_error}")


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _extract_skills(text: str) -> List[str]:
    lexicon = [
        "numerical", "verbal", "logical", "critical thinking", "problem solving", "leadership",
        "communication", "personality", "cognitive", "situational judgement", "stakeholder management",
        "attention to detail", "coding", "java", "python", "sales", "customer service",
    ]
    low = text.lower()
    return sorted({s for s in lexicon if s in low})


def _find_product_links(soup: BeautifulSoup) -> List[str]:
    links: List[str] = []
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        if "/products/" not in href:
            continue
        full = urljoin("https://www.shl.com", href)
        if "/products/product-catalog/" in full:
            continue
        links.append(full.split("#")[0])
    return sorted(set(links))


def _parse_product_page(url: str) -> Optional[Dict[str, Any]]:
    html = _get(url)
    soup = BeautifulSoup(html, "html.parser")

    name = _normalize_text((soup.find("h1") or soup.title).get_text(" ", strip=True) if (soup.find("h1") or soup.title) else "")
    if not name:
        return None
    if "job focused" in name.lower() or "solution" in name.lower() and "test" not in name.lower():
        return None

    desc_node = soup.select_one("meta[name='description']")
    description = _normalize_text(desc_node.get("content", "") if desc_node else "")

    body_text = _normalize_text(soup.get_text(" ", strip=True))
    test_type = "Unknown"
    for t in ["Ability & Aptitude", "Personality & Behavior", "Situational Judgement", "Knowledge & Skills", "Biodata & Experience"]:
        if t.lower() in body_text.lower():
            test_type = t
            break

    # guard: keep only individual tests, exclude pre-packaged job solutions
    if "pre-packaged job solution" in body_text.lower() or "job-focused assessment" in body_text.lower():
        return None

    return {
        "name": name,
        "url": url,
        "description": description,
        "category": "Individual Test Solutions",
        "test_type": test_type,
        "skills_measured": _extract_skills(f"{name} {description} {body_text[:3000]}"),
    }


def scrape_catalog() -> List[Dict[str, Any]]:
    landing_html = _get(BASE_URL)
    landing = BeautifulSoup(landing_html, "html.parser")
    urls = _find_product_links(landing)

    records: List[Dict[str, Any]] = []
    seen = set()
    for url in urls:
        try:
            record = _parse_product_page(url)
        except Exception:
            continue
        if not record:
            continue
        key = (record["name"].lower(), record["url"])
        if key in seen:
            continue
        seen.add(key)
        records.append(record)

    records = sorted(records, key=lambda x: x["name"].lower())
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(records, indent=2, ensure_ascii=False))
    return records


if __name__ == "__main__":
    items = scrape_catalog()
    print(f"Saved {len(items)} entries to {OUT_PATH}")
