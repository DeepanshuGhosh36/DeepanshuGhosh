from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CATALOG_PATH = DATA_DIR / "catalog.json"
EMBED_PATH = DATA_DIR / "embeddings.npy"
INDEX_PATH = DATA_DIR / "faiss.index"


def build_embeddings() -> None:
    data = json.loads(CATALOG_PATH.read_text())
    texts = [f"{d['name']} {d.get('description','')} {d.get('test_type','')} {' '.join(d.get('skills_measured',[]))}" for d in data]
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embs = model.encode(texts, normalize_embeddings=True)
    arr = np.array(embs, dtype="float32")
    np.save(EMBED_PATH, arr)
    index = faiss.IndexFlatIP(arr.shape[1])
    index.add(arr)
    faiss.write_index(index, str(INDEX_PATH))


if __name__ == "__main__":
    build_embeddings()
    print("Embeddings and FAISS index generated.")
