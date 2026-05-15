from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import faiss
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CATALOG_PATH = DATA_DIR / "catalog.json"
EMBED_PATH = DATA_DIR / "embeddings.npy"
INDEX_PATH = DATA_DIR / "faiss.index"

CATALOG: List[Dict[str, Any]] = []
INDEX: faiss.Index | None = None
EMBEDDINGS: np.ndarray | None = None


def load_catalog() -> List[Dict[str, Any]]:
    global CATALOG
    if CATALOG:
        return CATALOG
    if not CATALOG_PATH.exists():
        CATALOG = []
        return CATALOG
    raw = json.loads(CATALOG_PATH.read_text())
    CATALOG = [r for r in raw if isinstance(r, dict) and r.get("name") and r.get("url")]
    return CATALOG


def load_index() -> None:
    global INDEX, EMBEDDINGS
    if INDEX is not None:
        return
    if INDEX_PATH.exists() and EMBED_PATH.exists():
        INDEX = faiss.read_index(str(INDEX_PATH))
        EMBEDDINGS = np.load(EMBED_PATH)


def _keyword_score(item: Dict[str, Any], query: str) -> float:
    text = " ".join(
        [item.get("name", ""), item.get("description", ""), item.get("test_type", ""), " ".join(item.get("skills_measured", []))]
    ).lower()
    q_tokens = [t for t in query.lower().split() if len(t) > 1]
    if not q_tokens:
        return 0.0
    return sum(1.0 for tok in q_tokens if tok in text) / len(q_tokens)


def _semantic_candidates(query: str, top_k: int) -> List[Tuple[int, float]]:
    if INDEX is None or EMBEDDINGS is None or EMBEDDINGS.shape[0] == 0:
        return []
    # lightweight query projection via token overlap with catalog fields (no runtime transformer)
    # use average of top matching vectors by keyword score as pseudo-query vector
    catalog = load_catalog()
    scored = sorted(((i, _keyword_score(c, query)) for i, c in enumerate(catalog)), key=lambda x: x[1], reverse=True)[: min(20, len(catalog))]
    if not scored or scored[0][1] == 0:
        return []
    vecs = np.array([EMBEDDINGS[i] for i, s in scored if s > 0], dtype="float32")
    if vecs.size == 0:
        return []
    qvec = vecs.mean(axis=0, keepdims=True).astype("float32")
    faiss.normalize_L2(qvec)
    dists, idxs = INDEX.search(qvec, min(top_k * 2, len(catalog)))
    return [(int(i), float(s)) for i, s in zip(idxs[0], dists[0]) if i >= 0]


def retrieve_assessments(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    catalog = load_catalog()
    if not catalog:
        return []

    k = max(1, min(top_k, 10))
    kw = {i: _keyword_score(item, query) for i, item in enumerate(catalog)}
    sem = dict(_semantic_candidates(query, k))

    ranked = []
    for i, item in enumerate(catalog):
        score = 0.65 * kw.get(i, 0.0) + 0.35 * sem.get(i, 0.0)
        ranked.append((score, i, item))

    ranked.sort(key=lambda x: x[0], reverse=True)
    picked = [r[2] for r in ranked[:k] if r[2].get("url")]

    return [{"name": r["name"], "url": r["url"], "test_type": r.get("test_type", "Unknown"), "description": r.get("description", "")} for r in picked]
