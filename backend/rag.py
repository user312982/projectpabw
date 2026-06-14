"""
RAG (Retrieval-Augmented Generation) untuk ITK LostFound.
Menggunakan ChromaDB sebagai vector store untuk semantic search
dengan embedding dari sentence-transformers.
"""

import logging
import os
from typing import Dict, List, Optional

from database import Item, SessionLocal

logger = logging.getLogger(__name__)

# ── Feature flag untuk RAG ChromaDB ──
# Default OFF agar startup cepat dan ringan.
HAS_CHROMADB = os.getenv("ENABLE_RAG", "false").lower() in ("1", "true", "yes", "on")
if HAS_CHROMADB:
    logger.info("RAG ChromaDB diaktifkan via ENABLE_RAG=true")
else:
    logger.warning("RAG ChromaDB dinonaktifkan (ENABLE_RAG=false)")

# ── Fallback: TF-IDF based search for when chromadb is not available ──
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logger.warning(
        "scikit-learn tidak tersedia, fallback RAG tidak akan berfungsi optimal"
    )


class LostFoundRAG:
    """
    RAG Engine untuk ITK LostFound.

    Menggunakan ChromaDB untuk semantic search berdasarkan item database.
    Jika ChromaDB tidak tersedia, menggunakan TF-IDF sebagai fallback.
    """

    def __init__(self):
        self.initialized = False
        self.collection = None
        self._init_chromadb()

    def _init_chromadb(self):
        """Initialize ChromaDB collection."""
        if not HAS_CHROMADB:
            logger.info("ChromaDB tidak tersedia, menggunakan fallback RAG")
            return

        try:
            # Use persistent client untuk menyimpan embeddings
            persist_dir = os.path.join(
                os.path.dirname(__file__), "..", "data", "chromadb"
            )
            os.makedirs(persist_dir, exist_ok=True)

            self.client = chromadb.PersistentClient(path=persist_dir)

            # Use default embedding function (all-MiniLM-L6-v2 via ONNX)
            self.collection = self.client.get_or_create_collection(
                name="lostfound_items", metadata={"hnsw:space": "cosine"}
            )

            self.initialized = True
            logger.info("ChromaDB RAG berhasil diinisialisasi")
        except Exception as e:
            logger.error(f"Gagal menginisialisasi ChromaDB: {e}")
            self.initialized = False

    def _format_item_text(self, item) -> str:
        """Format item data menjadi teks untuk embedding."""
        type_label = "Barang Hilang" if item.type == "lost" else "Barang Ditemukan"
        parts = [
            f"Judul: {item.title}",
            f"Tipe: {type_label}",
            f"Kategori: {item.category}",
            f"Deskripsi: {item.description or 'tidak ada deskripsi'}",
            f"Lokasi: {item.location or 'tidak disebutkan'}",
        ]
        return ". ".join(parts)

    def reindex_all(self):
        """Re-index semua item dari database ke ChromaDB."""
        if not self.initialized:
            return

        db = SessionLocal()
        try:
            items = db.query(Item).all()
            if not items:
                logger.info("RAG: Tidak ada item untuk di-index")
                return

            ids = []
            documents = []
            metadatas = []

            for item in items:
                ids.append(str(item.id))
                documents.append(self._format_item_text(item))
                metadatas.append(
                    {
                        "item_id": item.id,
                        "type": item.type,
                        "category": item.category,
                        "title": item.title,
                        "status": item.status,
                        "location": item.location or "",
                    }
                )

            # Hapus data lama dan re-add
            try:
                existing_ids = self.collection.get()["ids"]
                if existing_ids:
                    self.collection.delete(ids=existing_ids)
            except Exception:
                pass

            # Add in batches untuk menghindari overload
            batch_size = 50
            for i in range(0, len(ids), batch_size):
                batch_end = min(i + batch_size, len(ids))
                self.collection.add(
                    documents=documents[i:batch_end],
                    metadatas=metadatas[i:batch_end],
                    ids=ids[i:batch_end],
                )

            logger.info(f"RAG: Berhasil meng-index {len(items)} item")
        except Exception as e:
            logger.error(f"RAG: Gagal reindex: {e}")
        finally:
            db.close()

    def retrieve(
        self, query: str, n_results: int = 5, type_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve item relevan berdasarkan semantic similarity.

        Args:
            query: Teks query dari user
            n_results: Jumlah maksimal hasil
            type_filter: Filter tipe ('lost', 'found', atau None untuk semua)

        Returns:
            List of dict dengan item yang relevan
        """
        if self.initialized:
            return self._chromadb_retrieve(query, n_results, type_filter)
        else:
            return self._fallback_retrieve(query, n_results, type_filter)

    def _chromadb_retrieve(
        self, query: str, n_results: int = 5, type_filter: Optional[str] = None
    ) -> List[Dict]:
        """Retrieve menggunakan ChromaDB vector search."""
        try:
            where_filter = {}
            if type_filter:
                where_filter["type"] = type_filter

            # Query chromadb dengan filter
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results * 2 if type_filter else n_results,
                where=where_filter if where_filter else None,
            )

            if not results["ids"][0]:
                return []

            retrieved = []
            for i in range(len(results["ids"][0])):
                meta = results["metadatas"][0][i]
                doc = results["documents"][0][i]
                distance = results["distances"][0][i] if "distances" in results else 0
                relevance = 1 - distance  # Konversi jarak ke skor relevansi

                retrieved.append(
                    {
                        "id": results["ids"][0][i],
                        "title": meta.get("title", ""),
                        "type": meta.get("type", ""),
                        "category": meta.get("category", ""),
                        "status": meta.get("status", ""),
                        "location": meta.get("location", ""),
                        "content": doc,
                        "relevance_score": round(relevance, 4),
                    }
                )

            # Filter dan sort
            if type_filter:
                retrieved = [r for r in retrieved if r["type"] == type_filter]

            retrieved.sort(key=lambda x: x["relevance_score"], reverse=True)
            return retrieved[:n_results]

        except Exception as e:
            logger.error(f"RAG ChromaDB error: {e}")
            return self._fallback_retrieve(query, n_results, type_filter)

    def _fallback_retrieve(
        self, query: str, n_results: int = 5, type_filter: Optional[str] = None
    ) -> List[Dict]:
        """Fallback: Gunakan SQL LIKE search jika vector DB tidak tersedia."""
        db = SessionLocal()
        try:
            query_obj = db.query(Item).order_by(Item.created_at.desc())

            # Simple keyword search
            keywords = query.lower().split()
            for kw in keywords:
                query_obj = query_obj.filter(
                    (Item.title.ilike(f"%{kw}%"))
                    | (Item.description.ilike(f"%{kw}%"))
                    | (Item.location.ilike(f"%{kw}%"))
                )

            if type_filter:
                query_obj = query_obj.filter(Item.type == type_filter)

            items = query_obj.limit(n_results).all()

            return [
                {
                    "id": str(item.id),
                    "title": item.title,
                    "type": item.type,
                    "category": item.category,
                    "status": item.status,
                    "location": item.location or "",
                    "content": self._format_item_text(item),
                    "relevance_score": 1.0,
                }
                for item in items
            ]

        except Exception as e:
            logger.error(f"RAG Fallback error: {e}")
            return []
        finally:
            db.close()

    def add_item(self, item) -> bool:
        """Add single item to index."""
        if not self.initialized:
            return False
        try:
            self.collection.add(
                documents=[self._format_item_text(item)],
                metadatas=[
                    {
                        "item_id": item.id,
                        "type": item.type,
                        "category": item.category,
                        "title": item.title,
                        "status": item.status,
                        "location": item.location or "",
                    }
                ],
                ids=[str(item.id)],
            )
            return True
        except Exception as e:
            logger.error(f"RAG add_item error: {e}")
            return False

    def update_item(self, item) -> bool:
        """Update item di index."""
        if not self.initialized:
            return False
        try:
            self.collection.update(
                documents=[self._format_item_text(item)],
                metadatas=[
                    {
                        "item_id": item.id,
                        "type": item.type,
                        "category": item.category,
                        "title": item.title,
                        "status": item.status,
                        "location": item.location or "",
                    }
                ],
                ids=[str(item.id)],
            )
            return True
        except Exception as e:
            logger.error(f"RAG update_item error: {e}")
            return False

    def delete_item(self, item_id: int) -> bool:
        """Remove item dari index."""
        if not self.initialized:
            return False
        try:
            self.collection.delete(ids=[str(item_id)])
            return True
        except Exception as e:
            logger.error(f"RAG delete_item error: {e}")
            return False


# Singleton instance
rag_system = LostFoundRAG()
