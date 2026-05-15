from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.shl.com/solutions/products/product-catalog/"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "catalog.json"


def _get(url: str, retries: int = 3, timeout: int = 20) -> str:
    for i in range(retries):
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(1.5 * (i + 1))
    return ""


def scrape_catalog() -> List[Dict]:
    # NOTE: page selectors may evolve; keep parser defensive.
    html = _get(BASE_URL)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("a[href*='/products/']")
    items: List[Dict] = []
    seen = set()
    for c in cards:
        name = c.get_text(" ", strip=True)
        href = c.get("href", "")
        if not name or not href:
            continue
        full_url = href if href.startswith("http") else f"https://www.shl.com{href}"
        key = (name.lower(), full_url)
        if key in seen:
            continue
        seen.add(key)
        # conservative filter to avoid pre-packaged job solutions
        if "job solution" in name.lower() or "pre-packaged" in name.lower():
            continue
        items.append(
            {
                "name": name,
                "url": full_url,
                "description": "",
                "category": "Individual Test Solutions",
                "test_type": "Unknown",
                "skills_measured": [],
            }
        )

    OUT_PATH.write_text(json.dumps(items, indent=2))
    return items


if __name__ == "__main__":
    results = scrape_catalog()
    print(f"Saved {len(results)} entries to {OUT_PATH}")
