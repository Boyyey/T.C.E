from __future__ import annotations

from typing import List, Dict, Any, Tuple, Optional
import time
import os
import numpy as np

try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover
    faiss = None

# Lazy import moved into _ensure_embedder
# from sentence_transformers import SentenceTransformer
import pyarrow as pa
import pyarrow.parquet as pq
from ..types import Thought


class LongTermMemory:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", storage_dir: Optional[str] = None) -> None:
        self.episodes: List[Dict[str, Any]] = []
        self.tags_index: Dict[str, List[int]] = {}
        self._embedder = None
        self.model_name = model_name
        self.dim = None
        self.index = None
        self._embeddings: List[np.ndarray] = []
        if faiss is not None:
            # Will instantiate after we know dim, but allow empty index for load()
            self.index = None
        self.storage_dir = storage_dir
        if self.storage_dir:
            os.makedirs(self.storage_dir, exist_ok=True)

    def _ensure_embedder(self) -> None:
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer(self.model_name)
            self.dim = self._embedder.get_sentence_embedding_dimension()
            if faiss is not None and self.index is None and self._embeddings:
                self.index = faiss.IndexFlatIP(self.dim)
                self.index.add(np.stack(self._embeddings, axis=0).astype(np.float32))

    def _embed(self, text: str) -> np.ndarray:
        self._ensure_embedder()
        vec = self._embedder.encode([text], convert_to_numpy=True, normalize_embeddings=True)[0]
        return vec.astype(np.float32)

    def record_episode(self, query: str, response: str, thought: Thought, tags: List[str] | None = None) -> None:
        entry = {
            "ts": float(time.time()),
            "query": query,
            "response": response,
            "thought": thought.model_dump(),
            "tags": tags or [],
        }
        idx = len(self.episodes)
        self.episodes.append(entry)
        text = f"Q: {query}\nA: {response}\nWhy: {thought.rationale}"
        emb = self._embed(text)
        self._embeddings.append(emb)
        if faiss is not None:
            if self.index is None:
                # Initialize index now that we know dim
                self.index = faiss.IndexFlatIP(int(emb.shape[0]))
            self.index.add(emb.reshape(1, -1))
        for t in entry["tags"]:
            self.tags_index.setdefault(t, []).append(idx)

    def recent(self, k: int = 5) -> List[Dict[str, Any]]:
        return self.episodes[-k:]

    def search(self, query: str, top_k: int = 5, required_tags: List[str] | None = None) -> List[Tuple[int, float]]:
        if not self.episodes:
            return []
        q = self._embed(query)
        if self.index is not None:
            D, I = self.index.search(q.reshape(1, -1), min(top_k, len(self.episodes)))
            candidates = [(int(i), float(d)) for i, d in zip(I[0], D[0]) if i != -1]
        else:
            sims = np.array([float(np.dot(q, e)) for e in self._embeddings])
            order = np.argsort(-sims)[:top_k]
            candidates = [(int(i), float(sims[int(i)])) for i in order]
        if required_tags:
            allowed = set.intersection(*(set(self.tags_index.get(t, [])) for t in required_tags)) if required_tags else set()
            candidates = [(i, s) for i, s in candidates if i in allowed]
        return candidates

    def get_episodes(self, indices: List[int]) -> List[Dict[str, Any]]:
        return [self.episodes[i] for i in indices if 0 <= i < len(self.episodes)]

    # Persistence APIs
    def save(self, directory: Optional[str] = None) -> None:
        dir_path = directory or self.storage_dir
        if not dir_path:
            return
        os.makedirs(dir_path, exist_ok=True)
        rows = []
        for e in self.episodes:
            rows.append(
                {
                    "ts": e["ts"],
                    "query": e["query"],
                    "response": e["response"],
                    "thought": str(e["thought"]),
                    "tags": ",".join(e.get("tags", [])),
                }
            )
        table = pa.Table.from_pylist(rows)
        pq.write_table(table, os.path.join(dir_path, "episodes.parquet"))
        if self._embeddings:
            embs = np.stack(self._embeddings, axis=0)
            np.save(os.path.join(dir_path, "embeddings.npy"), embs)
        if faiss is not None and self.index is not None:
            faiss.write_index(self.index, os.path.join(dir_path, "index.faiss"))
        np.save(os.path.join(dir_path, "tags_index.npy"), self._serialize_tags_index())

    def load(self, directory: Optional[str] = None) -> None:
        dir_path = directory or self.storage_dir
        if not dir_path or not os.path.exists(dir_path):
            return
        eps_path = os.path.join(dir_path, "episodes.parquet")
        if os.path.exists(eps_path):
            table = pq.read_table(eps_path)
            self.episodes = []
            for r in table.to_pylist():
                self.episodes.append(
                    {
                        "ts": float(r["ts"]),
                        "query": r["query"],
                        "response": r["response"],
                        "thought": self._safe_eval_thought(r["thought"]),
                        "tags": r["tags"].split(",") if r["tags"] else [],
                    }
                )
        emb_path = os.path.join(dir_path, "embeddings.npy")
        if os.path.exists(emb_path):
            embs = np.load(emb_path)
            self._embeddings = [embs[i] for i in range(embs.shape[0])]
            if faiss is not None:
                # Initialize index later when embedder is ensured (dim may be None now)
                self.index = faiss.IndexFlatIP(int(embs.shape[1]))
                self.index.add(embs.astype(np.float32))
        tags_path = os.path.join(dir_path, "tags_index.npy")
        if os.path.exists(tags_path):
            self.tags_index = self._deserialize_tags_index(np.load(tags_path, allow_pickle=True).item())

    def _serialize_tags_index(self) -> Dict[str, np.ndarray]:
        return {k: np.array(v, dtype=np.int64) for k, v in self.tags_index.items()}

    def _deserialize_tags_index(self, data: Dict[str, Any]) -> Dict[str, List[int]]:
        return {k: list(map(int, list(v))) for k, v in data.items()}

    def _safe_eval_thought(self, s: str) -> Dict[str, Any]:
        try:
            import json
            return json.loads(s.replace("'", '"'))
        except Exception:
            return {"raw": s}
