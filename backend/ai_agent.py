"""
LangGraph AI Agent untuk ITK LostFound dengan RAG.

Tools:
1. report_lost_item   — Laporkan barang hilang (wajib: nama & lokasi)
2. report_found_item  — Laporkan barang ditemukan (wajib: nama & lokasi)
3. search_items       — Cari barang berdasarkan kata kunci/kategori
4. list_recent_items  — Lihat laporan terbaru
5. match_items        — Cari kecocokan barang hilang & ditemukan
6. update_item_tool   — Perbarui data laporan
7. delete_item_tool   — Hapus laporan

Fitur:
- RAG (Retrieval-Augmented Generation) untuk semantic search
- Chat history / konteks percakapan
- Deteksi kebingungan dan respons yang sesuai
- Wajib nama & lokasi untuk laporan
- Tidak keluar konteks
"""

import os
import re
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# ── Rate Limiter ──────────────────────────────────────────────────
# Simple rate limiter: max 10 requests per minute
_last_request_time = 0
_min_interval = 10.0  # seconds between requests (6 per minute = 10s each)

from database import (
    Item,
    ItemCategory,
    ItemStatus,
    ItemType,
    SessionLocal,
    generate_unique_code,
)
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from pydantic import BaseModel, Field
from rag import rag_system

# ── LLM Setup (DeepSeek V4) ────────────────────────────────

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.2,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    max_tokens=1000,
)

# ── Pydantic Schemas for Strict Tool Calling ───────────────────────


class ReportLostInput(BaseModel):
    title: str = Field(description="NAMA atau judul barang yang hilang (WAJIB diisi)")
    reporter_name: Optional[str] = Field(
        default=None, description="NAMA pelapor yang kehilangan barang (opsional, isi jika disebutkan)"
    )
    category: str = Field(
        default="lainnya",
        description="Kategori: elektronik/pakaian/dokumen/aksesoris/tas/kunci/lainnya",
    )
    description: str = Field(
        default="",
        description="Deskripsi detail tentang barang: warna, merk, ciri khas",
    )
    location: str = Field(description="LOKASI terakhir barang terlihat (WAJIB diisi)")
    reporter_contact: str = Field(
        default="", description="Kontak pelapor: No HP atau email"
    )
    force_create: bool = Field(
        default=False,
        description="JANGAN ISI FIELD INI. Hanya gunakan jika user sudah konfirmasi ingin melanjutkan laporan meskipun ada barang serupa.",
    )


class ReportFoundInput(BaseModel):
    title: str = Field(
        description="NAMA atau judul barang yang ditemukan (WAJIB diisi)"
    )
    reporter_name: Optional[str] = Field(
        default=None, description="NAMA penemu barang (opsional, isi jika disebutkan)"
    )
    category: str = Field(
        default="lainnya",
        description="Kategori: elektronik/pakaian/dokumen/aksesoris/tas/kunci/lainnya",
    )
    description: str = Field(
        default="",
        description="Deskripsi detail tentang barang: warna, merk, ciri khas",
    )
    location: str = Field(
        description="LOKASI detail tempat barang ditemukan (WAJIB diisi)"
    )
    reporter_contact: str = Field(
        default="", description="Kontak penemu: No HP atau email"
    )
    force_create: bool = Field(
        default=False,
        description="JANGAN ISI FIELD INI. Hanya gunakan jika user sudah konfirmasi ingin melanjutkan laporan meskipun ada barang serupa.",
    )


class SearchItemsInput(BaseModel):
    keyword: str = Field(
        default="", description="Kata kunci pencarian (nama atau deskripsi barang)"
    )
    category: str = Field(
        default="",
        description="Filter kategori: elektronik/pakaian/dokumen/aksesoris/tas/kunci/lainnya",
    )
    type: str = Field(
        default="",
        description="Filter tipe laporan ('lost' untuk hilang, 'found' untuk ditemukan)",
    )


class ListRecentInput(BaseModel):
    limit: int = Field(
        default=10, description="Jumlah maksimal laporan yang ingin ditampilkan"
    )


class MatchItemsInput(BaseModel):
    keyword: str = Field(
        default="", description="Kata kunci pencarian barang untuk dicocokkan"
    )


class UpdateItemInput(BaseModel):
    unique_code: str = Field(
        description="KODE UNIK laporan barang (wajib, contoh: LF-ABCD12)"
    )
    title: Optional[str] = Field(
        default=None, description="Nama barang baru (jika ingin diubah)"
    )
    description: Optional[str] = Field(
        default=None, description="Deskripsi baru (jika ingin diubah)"
    )
    location: Optional[str] = Field(
        default=None, description="Lokasi baru (jika ingin diubah)"
    )
    reporter_name: Optional[str] = Field(
        default=None, description="Nama pelapor/penemu baru (jika ingin diubah)"
    )
    reporter_contact: Optional[str] = Field(
        default=None, description="Kontak pelapor/penemu baru (jika ingin diubah)"
    )
    status: Optional[str] = Field(
        default=None, description="Status laporan: open/claimed/closed"
    )


class DeleteItemInput(BaseModel):
    unique_code: str = Field(
        description="KODE UNIK laporan barang yang ingin dihapus (wajib, contoh: LF-ABCD12)"
    )


# ── Tools ──────────────────────────────────────────────────────────


@tool(args_schema=ReportLostInput)
def report_lost_item(
    title: str,
    reporter_name: Optional[str] = None,
    category: str = "lainnya",
    description: str = "",
    location: str = "",
    reporter_contact: str = "",
    force_create: bool = False,
) -> str:
    """Simpan data laporan barang hilang ke database sistem ITK LostFound.
    WAJIB: title (nama barang) dan location (lokasi terakhir) harus diisi. reporter_name (nama pelapor) opsional.
    SEBELUM melaporkan, sistem akan mencari barang serupa di database (berdasarkan NAMA BARANG saja)."""
    if not title or not title.strip():
        return "[ERROR] Nama barang tidak boleh kosong! Mohon beri tahu nama barang yang hilang."
    if not location or not location.strip():
        return "[ERROR] Lokasi terakhir barang tidak boleh kosong! Mohon beri tahu di mana terakhir kali barang terlihat."

    # Validasi kategori
    valid_categories = [c.value for c in ItemCategory]
    if category and category not in valid_categories:
        return f"[ERROR] Kategori '{category}' tidak valid. Pilih: {', '.join(valid_categories)}"

    # 🔍 CARI BARANG SERUPA (BERDASARKAN NAMA SAJA) - kecuali force_create=True
    db = SessionLocal()
    try:
        if not force_create:
            # Cari barang ditemukan yang mungkin cocok (HANYA berdasarkan nama/title)
            found_items = db.query(Item).filter(
                Item.type == "found",
                Item.status == "open"
            ).all()
            
            similar_items = []
            title_lower = title.lower()
            
            for found in found_items:
                found_title_lower = found.title.lower()
                # Cek apakah nama barang mirip (hanya berdasarkan nama, bukan lokasi)
                # Menggunakan fuzzy matching sederhana - cek setiap kata dalam title
                title_words = [w for w in title_lower.split() if len(w) > 2]
                found_words = [w for w in found_title_lower.split() if len(w) > 2]
                
                # Cek jika ada kata yang sama
                matching_words = set(title_words) & set(found_words)
                
                # Juga cek jika salah satu title merupakan bagian dari title lainnya
                is_similar = (
                    len(matching_words) >= 1 or  # Ada minimal 1 kata yang sama
                    title_lower in found_title_lower or  # Title user bagian dari title di DB
                    found_title_lower in title_lower  # Title di DB bagian dari title user
                )
                
                if is_similar:
                    similar_items.append(found)
            
            # Jika ada yang cocok, beri tahu user
            if similar_items:
                lines = ["[PERHATIAN] Ditemukan barang serupa di database (berdasarkan nama):"]
                for found in similar_items[:3]:  # Max 3 hasil
                    lines.append(
                        f"\n- {found.title} (Ditemukan)\n"
                        f"  Lokasi: {found.location}\n"
                        f"  Kategori: {found.category}\n"
                        f"  Penemu: {found.reporter_name or 'Anonim'}\n"
                        f"  Kontak: {found.reporter_contact or '-'}\n"
                        f"  Kode: {found.unique_code}"
                    )
                lines.append("\nApakah ini barang yang Anda maksud? Jika ya, Anda bisa menghubungi penemu langsung.")
                lines.append("Jika ingin tetap membuat laporan baru, konfirmasi dengan jelas.")
                return "\n".join(lines)
        
        # Jika tidak ada yang cocok ATAU force_create=True, lanjutkan buat laporan
        item = Item(
            unique_code=generate_unique_code(db),
            title=title.strip(),
            description=description.strip() if description else "",
            category=category if category in valid_categories else "lainnya",
            type=ItemType.lost.value,
            location=location.strip(),
            date_event=datetime.now(),
            status=ItemStatus.open.value,
            reporter_name=(reporter_name.strip() if reporter_name else "Anonim"),
            reporter_contact=reporter_contact.strip() if reporter_contact else "",
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        # Add to RAG index
        rag_system.add_item(item)

        return (
            f"[SUCCESS] Laporan barang hilang berhasil dibuat!\n"
            f"   Kode Unik: {item.unique_code}\n"
            f"   Barang: {title}\n"
            f"   Kategori: {category}\n"
            f"   Lokasi terakhir: {location}\n"
            f"   Pelapor: {reporter_name.strip() if reporter_name else 'Anonim'}\n"
        )
    finally:
        db.close()


@tool(args_schema=ReportFoundInput)
def report_found_item(
    title: str,
    reporter_name: Optional[str] = None,
    category: str = "lainnya",
    description: str = "",
    location: str = "",
    reporter_contact: str = "",
    force_create: bool = False,
) -> str:
    """Simpan data laporan barang ditemukan ke database sistem ITK LostFound.
    WAJIB: title (nama barang) dan location (lokasi ditemukan) harus diisi. reporter_name (nama penemu) opsional.
    SEBELUM melaporkan, sistem akan mencari barang hilang yang mungkin cocok (berdasarkan NAMA BARANG saja)."""
    if not title or not title.strip():
        return "[ERROR] Nama barang tidak boleh kosong! Mohon beri tahu nama barang yang ditemukan."
    if not location or not location.strip():
        return "[ERROR] Lokasi ditemukan tidak boleh kosong! Mohon beri tahu di mana barang ditemukan."

    valid_categories = [c.value for c in ItemCategory]
    if category and category not in valid_categories:
        return f"[ERROR] Kategori '{category}' tidak valid. Pilih: {', '.join(valid_categories)}"

    # 🔍 CARI BARANG HILANG YANG SERUPA (BERDASARKAN NAMA SAJA) - kecuali force_create=True
    db = SessionLocal()
    try:
        if not force_create:
            # Cari barang hilang yang mungkin cocok (HANYA berdasarkan nama/title)
            lost_items = db.query(Item).filter(
                Item.type == "lost",
                Item.status == "open"
            ).all()
            
            similar_items = []
            title_lower = title.lower()
            
            for lost in lost_items:
                lost_title_lower = lost.title.lower()
                # Cek apakah nama barang mirip (hanya berdasarkan nama, bukan lokasi)
                # Menggunakan fuzzy matching sederhana - cek setiap kata dalam title
                title_words = [w for w in title_lower.split() if len(w) > 2]
                lost_words = [w for w in lost_title_lower.split() if len(w) > 2]
                
                # Cek jika ada kata yang sama
                matching_words = set(title_words) & set(lost_words)
                
                # Juga cek jika salah satu title merupakan bagian dari title lainnya
                is_similar = (
                    len(matching_words) >= 1 or  # Ada minimal 1 kata yang sama
                    title_lower in lost_title_lower or  # Title user bagian dari title di DB
                    lost_title_lower in title_lower  # Title di DB bagian dari title user
                )
                
                if is_similar:
                    similar_items.append(lost)
            
            # Jika ada yang cocok, beri tahu user
            if similar_items:
                lines = ["[PERHATIAN] Ditemukan barang hilang yang serupa (berdasarkan nama):"]
                for lost in similar_items[:3]:  # Max 3 hasil
                    lines.append(
                        f"\n- {lost.title} (Hilang)\n"
                        f"  Lokasi: {lost.location}\n"
                        f"  Kategori: {lost.category}\n"
                        f"  Pelapor: {lost.reporter_name or 'Anonim'}\n"
                        f"  Kontak: {lost.reporter_contact or '-'}\n"
                        f"  Kode: {lost.unique_code}"
                    )
                lines.append("\nApakah ini barang yang Anda maksud? Jika ya, Anda bisa menghubungi pemilik langsung.")
                lines.append("Jika ingin tetap membuat laporan baru, konfirmasi dengan jelas.")
                return "\n".join(lines)
        
        # Jika tidak ada yang cocok ATAU force_create=True, lanjutkan buat laporan
        item = Item(
            unique_code=generate_unique_code(db),
            title=title.strip(),
            description=description.strip() if description else "",
            category=category if category in valid_categories else "lainnya",
            type=ItemType.found.value,
            location=location.strip(),
            date_event=datetime.now(),
            status=ItemStatus.open.value,
            reporter_name=(reporter_name.strip() if reporter_name else "Anonim"),
            reporter_contact=reporter_contact.strip() if reporter_contact else "",
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        # Add to RAG index
        rag_system.add_item(item)

        return (
            f"[SUCCESS] Laporan barang ditemukan berhasil dibuat!\n"
            f"   Kode Unik: {item.unique_code}\n"
            f"   Barang: {title}\n"
            f"   Kategori: {category}\n"
            f"   Lokasi ditemukan: {location}\n"
            f"   Penemu: {reporter_name.strip() if reporter_name else 'Anonim'}\n"
        )
    finally:
        db.close()


@tool(args_schema=SearchItemsInput)
def search_items(keyword: str = "", category: str = "", type: str = "") -> str:
    """Cari daftar barang hilang atau ditemukan berdasarkan kata kunci, kategori, atau tipe.
    Gunakan RAG untuk semantic search yang lebih akurat."""
    db = SessionLocal()
    try:
        # Gunakan RAG untuk semantic search jika ada keyword
        if keyword:
            type_filter = type if type else None
            rag_results = rag_system.retrieve(
                keyword, n_results=10, type_filter=type_filter
            )
            if rag_results:
                lines = ["**Hasil Pencarian (RAG - Semantic Search):**\n"]
                for i, r in enumerate(rag_results, 1):
                    type_label = "HILANG 🔴" if r["type"] == "lost" else "DITEMUKAN 🟢"
                    lines.append(
                        f"{i}. [{type_label}] {r['title']}\n"
                        f"   Kategori: {r['category']}, Lokasi: {r['location'] or '-'}\n"
                        f"   Skor Relevansi: {r['relevance_score']:.2f}"
                    )
                lines.append(f"\nTotal: {len(rag_results)} hasil ditemukan")
                return "\n".join(lines)

        # Fallback ke SQL search
        query = db.query(Item).order_by(Item.created_at.desc())

        if keyword:
            kw = f"%{keyword}%"
            query = query.filter(
                (Item.title.ilike(kw))
                | (Item.description.ilike(kw))
                | (Item.location.ilike(kw))
            )
        if category:
            query = query.filter(Item.category == category)
        if type:
            query = query.filter(Item.type == type)

        items = query.limit(20).all()
        if not items:
            return "[INFO] Tidak ada barang yang cocok dengan pencarian. Coba gunakan kata kunci yang berbeda."

        lines = ["**Hasil Pencarian:**\n"]
        for i, item in enumerate(items, 1):
            type_label = "HILANG 🔴" if item.type == "lost" else "DITEMUKAN 🟢"
            lines.append(
                f"{i}. [{type_label}] {item.title}\n"
                f"   Kategori: {item.category}, Lokasi: {item.location or '-'}"
            )
        lines.append(f"\nTotal: {len(items)} hasil")
        return "\n".join(lines)
    finally:
        db.close()


@tool(args_schema=ListRecentInput)
def list_recent_items(limit: int = 10) -> str:
    """Lihat daftar laporan barang terbaru secara umum."""
    db = SessionLocal()
    try:
        items = db.query(Item).order_by(Item.created_at.desc()).limit(limit).all()
        if not items:
            return "[INFO] Belum ada laporan barang."

        lines = ["**📋 Laporan Terbaru:**\n"]
        for i, item in enumerate(items, 1):
            type_label = "HILANG 🔴" if item.type == "lost" else "DITEMUKAN 🟢"
            lines.append(
                f"{i}. [{type_label}] {item.title}\n"
                f"   Kategori: {item.category}, Lokasi: {item.location or '-'}, Status: {item.status}"
            )
        return "\n".join(lines)
    finally:
        db.close()


@tool(args_schema=MatchItemsInput)
def match_items(keyword: str = "") -> str:
    """Cari kecocokan antara laporan barang yang hilang dan barang yang ditemukan di database."""
    db = SessionLocal()
    try:
        lost_query = db.query(Item).filter(Item.type == "lost", Item.status == "open")
        found_query = db.query(Item).filter(Item.type == "found", Item.status == "open")

        if keyword:
            kw = f"%{keyword}%"
            lost_query = lost_query.filter(
                (Item.title.ilike(kw)) | (Item.description.ilike(kw))
            )
            found_query = found_query.filter(
                (Item.title.ilike(kw)) | (Item.description.ilike(kw))
            )

        lost_items = lost_query.all()
        found_items = found_query.all()

        if not lost_items and not found_items:
            return "[INFO] Tidak ada data barang yang bisa dicocokkan."

        matches = []
        for lost in lost_items:
            for found in found_items:
                score = 0
                # Cek kecocokan berdasarkan kategori
                if lost.category == found.category:
                    score += 1
                # Cek judul yang mirip
                if (
                    lost.title.lower() in found.title.lower()
                    or found.title.lower() in lost.title.lower()
                ):
                    score += 2
                # Cek lokasi yang mirip
                if (
                    lost.location
                    and found.location
                    and (
                        lost.location.lower() in found.location.lower()
                        or found.location.lower() in lost.location.lower()
                    )
                ):
                    score += 1
                if score > 0:
                    matches.append((lost, found, score))

        if not matches:
            return "[INFO] Tidak ditemukan kecocokan otomatis saat ini."

        matches.sort(key=lambda x: x[2], reverse=True)
        lines = ["**🔗 Kemungkinan Kecocokan:**\n"]
        for i, (lost, found, score) in enumerate(matches[:10], 1):
            lines.append(
                f"{i}. HILANG: '{lost.title}' ↔ DITEMUKAN: '{found.title}'\n"
                f"   Skor kecocokan: {score}/4 | Pelapor: {lost.reporter_name or 'Anonim'} | Penemu: {found.reporter_name or 'Anonim'}"
            )
        return "\n".join(lines)
    finally:
        db.close()


@tool(args_schema=UpdateItemInput)
def update_item_tool(
    unique_code: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    reporter_name: Optional[str] = None,
    reporter_contact: Optional[str] = None,
    status: Optional[str] = None,
) -> str:
    """Perbarui (update) data atau status laporan barang berdasarkan kode unik. Bisa mengubah nama pelapor/penemu dan kontak juga."""
    if not unique_code or not unique_code.strip():
        return "[ERROR] Kode unik tidak boleh kosong!"

    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.unique_code == unique_code).first()
        if not item:
            return f"[ERROR] Barang dengan kode unik {unique_code} tidak ditemukan."

        if title:
            item.title = title.strip()
        if description:
            item.description = description.strip()
        if location:
            item.location = location.strip()
        if reporter_name:
            item.reporter_name = reporter_name.strip()
        if reporter_contact:
            item.reporter_contact = reporter_contact.strip()
        if status:
            valid_statuses = [s.value for s in ItemStatus]
            if status in valid_statuses:
                item.status = status
            else:
                return (
                    f"[ERROR] Status tidak valid. Gunakan: {', '.join(valid_statuses)}"
                )

        db.commit()

        # Update RAG index
        rag_system.update_item(item)

        return f"[SUCCESS] ✅ Laporan barang ({unique_code}) berhasil diperbarui!"
    except Exception as e:
        return f"[ERROR] Gagal memperbarui barang: {str(e)}"
    finally:
        db.close()


@tool(args_schema=DeleteItemInput)
def delete_item_tool(unique_code: str) -> str:
    """Hapus laporan barang dari sistem berdasarkan kode unik."""
    if not unique_code or not unique_code.strip():
        return "[ERROR] Kode unik tidak boleh kosong!"

    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.unique_code == unique_code).first()
        if not item:
            return f"[ERROR] Barang dengan kode unik {unique_code} tidak ditemukan."

        item_id = item.id
        db.delete(item)
        db.commit()

        # Remove from RAG index
        rag_system.delete_item(item_id)

        return f"[SUCCESS] ✅ Laporan barang ({unique_code}) berhasil dihapus!"
    except Exception as e:
        return f"[ERROR] Gagal menghapus barang: {str(e)}"
    finally:
        db.close()


# ── System Prompt yang Ketat ───────────────────────────────────────

MAIN_SYSTEM_PROMPT = """Kamu adalah asisten ITK LostFound, platform resmi untuk melaporkan dan mencari barang hilang & ditemukan di kampus Institut Teknologi Kalimantan (ITK).

## TUJUAN UTAMA
Membantu mahasiswa, dosen, dan staf ITK dalam:
1. Melaporkan barang hilang atau ditemukan
2. Mencari barang berdasarkan deskripsi
3. Mencocokkan barang hilang dengan barang ditemukan
4. Melihat laporan terbaru

## ATURAN WAJIB

### 1. DATA WAJIB UNTUK LAPORAN:
Untuk MELAPORKAN BARANG HILANG, WAJIB menanyakan dan mengisi:
- ✅ NAMA BARANG (WAJIB)
- ✅ LOKASI TERAKHIR (WAJIB)
- NAMA PELAPOR (opsional, jika disebutkan baru diisi)
- Kategori, Deskripsi, Kontak (opsional)

Untuk MELAPORKAN BARANG DITEMUKAN, WAJIB menanyakan dan mengisi:
- ✅ NAMA BARANG (WAJIB)
- ✅ LOKASI DITEMUKAN (WAJIB)
- NAMA PENEMU (opsional, jika disebutkan baru diisi)
- Kategori, Deskripsi, Kontak (opsional)

### 2. JANGAN PERNAH MENGARANG DATA:
- Jika user belum memberikan title (nama barang) atau location, KAMU WAJIB BERTANYA.
- Nama pelapor/penemu bersifat OPSIONAL. Jika user tidak menyebutkan namanya, jangan tanya lagi, langsung buat laporan dengan nama "Anonim".
- UNTUK UPDATE/DELETE: Tanyakan KODE UNIK (contoh: LF-ABCD12).
- JANGAN mengarang kode unik!

### 3. BEDAKAN INTENSI USER:
- "saya mau cari", "carikan", "apakah ada" → GUNAKAN `search_items`
- "saya mau lapor", "saya kehilangan", "saya menemukan" → GUNAKAN `report_lost_item` / `report_found_item`
- "saya mau ubah", "perbarui", "update" → GUNAKAN `update_item_tool`
- "saya mau hapus", "hapus" → GUNAKAN `delete_item_tool`
- "cocokkan", "match", "kecocokan" → GUNAKAN `match_items`
- "laporan terbaru", "lihat semua", "tampilkan" → GUNAKAN `list_recent_items`

### 3a. PERHATIAN: EDIT/HAPUS HANYA UNTUK PEMBUAT LAPORAN:
- `update_item_tool` dan `delete_item_tool` akan otomatis ditolak jika user bukan pembuat laporan (atau petugas).
- Jika sistem mengembalikan error izin, beri tahu user bahwa mereka tidak bisa mengubah/menghapus laporan orang lain.

### 4. JIKA BINGUNG ATAU TIDAK PAHAM:
- Jika tidak mengerti pertanyaan user, KATAKAN: "Maaf, saya kurang memahami maksud Anda. Bisa dijelaskan dengan lebih detail? Saya bisa membantu melaporkan barang hilang/ditemukan atau mencari barang."
- Jika user bicara di luar topik barang hilang/ditemukan, arahkan kembali ke topik.
- JANGAN menjawab pertanyaan yang tidak terkait dengan sistem LostFound.

### 5. KONTEKS PERCAKAPAN:
- Ingat konteks chat sebelumnya! Jika user baru saja menyebutkan suatu barang, gunakan informasi itu.
- Jika user bilang "itu", "tersebut", atau "dia", pahami apa yang dimaksud dari chat sebelumnya.

### 6. AUTO-MATCH SEBELUM LAPORAN:
- `report_lost_item` dan `report_found_item` akan otomatis mencari barang serupa (berdasarkan NAMA BARANG saja) SEBELUM membuat laporan.
- Jika ada kecocokan, sistem akan mengembalikan daftar barang serupa dan LAPORAN TIDAK JADI DIBUAT.
- Jika ada kecocokan, informasikan ke user: "Saya menemukan X barang serupa di database. Apakah ini barang yang Anda maksud?"
- Jika user konfirmasi "iya", "ya", "benar", "itu", "yang itu" (artinya ini barang yang dimaksud), arahkan ke kontak pelapor/penemu.
- JIKA USER INGIN MELANJUTKAN / MEMBUAT LAPORAN BARU (bilang: "lanjutkan", "iya lanjut", "ya lanjut", "ya tetap", "bukan", "tetap buat", "tetap lanjut", "continue", "skip", "abaikan", atau menyatakan ingin membuat laporan baru), MAKA:
  - Panggil tool `report_lost_item` atau `report_found_item` lagi DENGAN parameter `force_create: true`
  - Ini akan membuat laporan baru tanpa mengecek kecocokan lagi
- Tool akan otomatis mencari kecocokan saat pertama kali dipanggil, jadi cukup panggil tool dengan `force_create: true` saat user ingin melanjutkan.

### 7. FORMAT RESPON:
- JANGAN gunakan emoji sama sekali dalam respon
- Jika `search_items` mengembalikan hasil, TIDAK perlu sebutkan detail barang satu per satu. Cukup bilang:
  - "Saya menemukan X barang yang cocok. Silakan lihat di daftar kiri untuk detailnya."
  - Atau "Tidak ada barang yang cocok dengan deskripsi tersebut."
- Jika berhasil membuat/update/delete laporan, berikan kode uniknya saja
- Gunakan bahasa Indonesia yang sederhana dan jelas

## 🔧 TOOLS YANG TERSEDIA:
- `report_lost_item` - Untuk melaporkan barang hilang
- `report_found_item` - Untuk melaporkan barang ditemukan
- `search_items` - Untuk mencari barang (gunakan RAG semantic search)
- `list_recent_items` - Untuk melihat laporan terbaru
- `match_items` - Untuk mencocokkan barang hilang & ditemukan
- `update_item_tool` - Untuk memperbarui data laporan
- `delete_item_tool` - Untuk menghapus laporan
"""

# ── Tools List ─────────────────────────────────────────────────────

tools = [
    report_lost_item,
    report_found_item,
    search_items,
    list_recent_items,
    match_items,
    update_item_tool,
    delete_item_tool,
]

llm_with_tools = llm.bind_tools(tools)

# ── History Manager ────────────────────────────────────────────────

CHAT_HISTORY_MAX = 20  # Maksimal pesan dalam riwayat


def truncate_history(messages: list) -> list:
    """Potong riwayat chat agar tidak terlalu panjang."""
    if len(messages) > CHAT_HISTORY_MAX:
        # Simpan system prompt + CHAT_HISTORY_MAX pesan terakhir
        return [messages[0]] + messages[-(CHAT_HISTORY_MAX - 1) :]
    return messages


async def process_chat(message: str, chat_history: list = None, user_id: int = None, user_role: str = None) -> tuple:
    """
    Process a user chat message with RAG context, tool calling, and chat history.

    Args:
        message: Pesan dari user
        chat_history: Riwayat percakapan (list of dict: {"role": "user"/"ai", "text": "..."})
        user_id: ID user yang sedang login (untuk validasi kepemilikan)
        user_role: Role user (user/petugas) untuk pengecekan akses

    Returns:
        Tuple (response_text, tools_used)
    """
    global _last_request_time
    
    # Rate limiting: wait if request too frequent
    current_time = time.time()
    elapsed = current_time - _last_request_time
    if elapsed < _min_interval:
        wait_time = _min_interval - elapsed
        time.sleep(wait_time)
    _last_request_time = time.time()
    
    # Initialize messages with system prompt
    messages = [SystemMessage(content=MAIN_SYSTEM_PROMPT)]

    # Add chat history if available
    if chat_history:
        for msg in chat_history[-8:]:  # Ambil 8 pesan terakhir untuk konteks
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("text", "")))
            elif msg.get("role") == "ai":
                messages.append(AIMessage(content=msg.get("text", "")))

    # Add RAG context if message seems like a search query
    rag_context = ""
    search_keywords = [
        "cari",
        "carikan",
        "apakah ada",
        "gimana cara",
        "bagaimana",
        "tahu",
        "liat",
        "lihat",
        "cek",
        "periksa",
        "screen",
    ]
    is_search_query = any(kw in message.lower() for kw in search_keywords)

    if is_search_query:
        rag_results = rag_system.retrieve(message, n_results=3)
        if rag_results:
            rag_parts = []
            for r in rag_results:
                type_label = "HILANG" if r["type"] == "lost" else "DITEMUKAN"
                rag_parts.append(
                    f"- [{type_label}] {r['title']} (Lokasi: {r['location'] or '-'})"
                )
            rag_context = (
                "\n\n[INFO TAMBAHAN DARI DATABASE - Gunakan informasi ini jika relevan]:\n"
                + "\n".join(rag_parts)
            )

    # Add user message with RAG context
    user_msg = message + rag_context
    messages.append(HumanMessage(content=user_msg))

    try:
        # First call: LLM decides whether to call a tool
        response = await llm_with_tools.ainvoke(messages)
        messages.append(response)

        tools_used = []

        # If LLM decided to call tools
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call.get("args", {})
                tool_id = tool_call["id"]

                tool_info = {"name": tool_name, "args": tool_args}
                tools_used.append(tool_info)

                tool_result = "[ERROR] Tool tidak ditemukan"

                # Ownership check for update/delete tools
                if tool_name in ("update_item_tool", "delete_item_tool") and user_id is not None:
                    unique_code = tool_args.get("unique_code", "")
                    if unique_code:
                        db = SessionLocal()
                        try:
                            item = db.query(Item).filter(Item.unique_code == unique_code).first()
                            if not item:
                                # Item tidak ditemukan - biarkan tool memberikan pesan error
                                pass
                            elif item.uploader_id is None:
                                # Item dibuat via AI (tanpa login), hanya petugas yang bisa edit
                                if user_role != "petugas":
                                    tool_result = "[ERROR] ❌ Laporan ini dibuat tanpa akun, hanya petugas yang bisa mengedit."
                                    messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_id, name=tool_name))
                                    continue
                            elif item.uploader_id != user_id and user_role != "petugas":
                                # Bukan pemilik dan bukan petugas
                                tool_result = "[ERROR] ❌ Anda tidak memiliki izin untuk mengubah atau menghapus laporan ini. Hanya pembuat laporan atau petugas yang bisa."
                                messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_id, name=tool_name))
                                continue
                            # Kalau pemiliknya atau petugas, biarkan tool berjalan
                        finally:
                            db.close()

                for t in tools:
                    if t.name == tool_name:
                        try:
                            tool_result = t.invoke(tool_args)
                        except Exception as e:
                            tool_result = f"[ERROR] Gagal mengeksekusi tool: {str(e)}"
                        break

                messages.append(
                    ToolMessage(
                        content=str(tool_result), tool_call_id=tool_id, name=tool_name
                    )
                )

            # Second call: LLM provides final answer based on tool results
            final_response = await llm_with_tools.ainvoke(messages)
            return final_response.content, tools_used

        # If no tool called, return directly
        return response.content, []

    except Exception as e:
        traceback.print_exc()
        error_str = str(e).lower()

        if "tool_use_failed" in error_str:
            return (
                "Maaf, ada kendala teknis saat memproses. "
                "Coba ubah sedikit cara Anda bertanya ya 😊",
                [],
            )
        if "rate limit" in error_str:
            return (
                "Server AI sedang sibuk (Rate Limit). "
                "Mohon tunggu beberapa saat sebelum mencoba lagi ⏳",
                [],
            )
        return (
            "Maaf, sistem sedang kelebihan beban. Mohon dicoba beberapa saat lagi 🙏",
            [],
        )
