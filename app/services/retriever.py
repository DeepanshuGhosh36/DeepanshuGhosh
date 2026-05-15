from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import faiss
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CATALOG_PATH = DATA_DIR / "catalog.json"
EMBED_PATH = DATA_DIR / "embeddings.npy"
INDEX_PATH = DATA_DIR / "faiss.index"

CATALOG: List[Dict[str, Any]] = []
INDEX = None
EMBEDDINGS = None


def load_catalog() -> List[Dict[str, Any]]:
    global CATALOG
    if CATALOG:
        return CATALOG
    if not CATALOG_PATH.exists():
        CATALOG = []
        return CATALOG
    CATALOG = json.loads(CATALOG_PATH.read_text())
    return CATALOG


def load_index() -> None:
    global INDEX, EMBEDDINGS
    if INDEX is not None:
        return
    if INDEX_PATH.exists() and EMBED_PATH.exists():
        INDEX = faiss.read_index(str(INDEX_PATH))
        EMBEDDINGS = np.load(EMBED_PATH)


def _keyword_score(item: Dict[str, Any], query: str) -> int:
    text = " ".join([item.get("name", ""), item.get("description", ""), " ".join(item.get("skills_measured", []))]).lower()
    return sum(1 for tok in query.lower().split() if tok in text)


def retrieve_assessments(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    catalog = load_catalog()
    if not catalog:
        return []
    # cheap keyword-first fallback; semantic score optional when index available
    ranked = sorted(catalog, key=lambda x: _keyword_score(x, query), reverse=True)
    results = ranked[: max(1, min(top_k, 10))]
    return [
        {
            "name": r["name"],
            "url": r["url"],
            "test_type": r.get("test_type", "Unknown"),
            "description": r.get("description", ""),
        }
        for r in results
        if r.get("url")
    ]
