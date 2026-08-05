"""A minimal in-memory vector store using numpy for similarity search.

This is intended for development and testing. For production, replace with a
persistent vector database (Milvus, Pinecone, Weaviate, etc.).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple
import logging

import numpy as np

from ai.embeddings import embed_text, embed_texts

logger = logging.getLogger(__name__)


class InMemoryVectorStore:
    """Simple vector store holding embeddings and metadata in memory.

    Usage:
        store = InMemoryVectorStore()
        store.add(["text1", "text2"], metadatas=[{"id":1}, {"id":2}])
        results = store.search("query text", top_k=3)
    """

    def __init__(self):
        self._embeddings: Optional[np.ndarray] = None
        self._metadatas: List[Dict[str, Any]] = []
        self._texts: List[str] = []

    def add(self, texts: Sequence[str], metadatas: Optional[Sequence[Dict[str, Any]]] = None) -> None:
        """Add texts and optional metadata to the store.

        `metadatas` must be the same length as `texts` if provided.
        """
        if metadatas is not None and len(metadatas) != len(texts):
            raise ValueError("metadatas length must match texts length")

        vectors = embed_texts(list(texts))
        arr = np.array(vectors, dtype=float)

        if self._embeddings is None:
            self._embeddings = arr
        else:
            self._embeddings = np.vstack([self._embeddings, arr])

        self._texts.extend(texts)
        if metadatas:
            self._metadatas.extend(metadatas)
        else:
            # Append empty metadata dicts for alignment
            self._metadatas.extend([{} for _ in texts])

    def _ensure_index(self) -> None:
        if self._embeddings is None:
            self._embeddings = np.zeros((0, 0))

    def search(self, query: str | Sequence[float], top_k: int = 5) -> List[Tuple[float, str, Dict[str, Any]]]:
        """Search the store with a text query or a vector.

        Returns a list of tuples: (score, text, metadata) ordered by descending score.
        Score is cosine similarity in [-1, 1].
        """
        self._ensure_index()

        if isinstance(query, str):
            q_vec = np.array(embed_text(query), dtype=float)
        else:
            q_vec = np.array(query, dtype=float)

        if self._embeddings.size == 0:
            return []

        # Ensure shapes
        if q_vec.ndim == 1:
            q_vec = q_vec.reshape(1, -1)

        # Compute cosine similarity: (q . x) / (||q|| * ||x||)
        try:
            emb = self._embeddings
            # If embeddings shape mismatch, try to adapt by trimming/padding (defensive)
            if q_vec.shape[1] != emb.shape[1]:
                logger.warning("Query vector size (%s) differs from store embeddings (%s)", q_vec.shape[1], emb.shape[1])
                # Attempt to broadcast-compatible comparison by trimming to min dim
                min_dim = min(q_vec.shape[1], emb.shape[1])
                q = q_vec[:, :min_dim]
                e = emb[:, :min_dim]
            else:
                q = q_vec
                e = emb

            q_norm = np.linalg.norm(q, axis=1, keepdims=True)
            e_norm = np.linalg.norm(e, axis=1, keepdims=True).T
            # Avoid division by zero
            q_norm[q_norm == 0] = 1.0
            e_norm[e_norm == 0] = 1.0

            sims = (q @ e.T) / (q_norm @ e_norm)
            sims = sims.flatten()
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Vector search failed: %s", exc)
            return []

        # Get top K indices
        idxs = np.argsort(-sims)[:top_k]
        results = []
        for i in idxs:
            score = float(sims[i])
            text = self._texts[i]
            meta = self._metadatas[i]
            results.append((score, text, meta))

        return results
