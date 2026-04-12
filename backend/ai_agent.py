"""
LangGraph AI Agent for ITK LostFound.

Tools:
1. report_lost_item   — Laporkan barang hilang
2. report_found_item  — Laporkan barang ditemukan
3. search_items       — Cari barang berdasarkan keyword/kategori
4. list_recent_items  — Lihat laporan terbaru
5. match_items        — Cari kecocokan barang hilang & ditemukan
"""

from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
from database import SessionLocal, Item, ItemType, ItemCategory, ItemStatus, generate_unique_code
from datetime import datetime
import os
import traceback

# ── LLM Setup (Groq — Free & Fast) ────────────────────────────────

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

# ── Pydantic Schemas for Strict Tool Calling ───────────────────────

class ReportLostInput(BaseModel):
    title: str = Field(description="Nama atau judul barang yang hilang (wajib)")
    reporter_name: str = Field(description="Nama pelapor yang kehilangan barang (wajib)")
    category: str = Field(default="lainnya", description="Kategori: elektronik/pakaian/dokumen/aksesoris/tas/kunci/lainnya")
    description: str = Field(default="", description="Deskripsi detail tentang barang (warna, merk, ciri khas)")
    location: str = Field(default="", description="Lokasi detail tempat terakhir barang terlihat")
    reporter_contact: str = Field(default="", description="Kontak pelapor (No HP atau email)")

class ReportFoundInput(BaseModel):
    title: str = Field(description="Nama atau judul barang yang ditemukan (wajib)")
    reporter_name: str = Field(description="Nama penemu barang (wajib)")
    category: str = Field(default="lainnya", description="Kategori: elektronik/pakaian/dokumen/aksesoris/tas/kunci/lainnya")
    description: str = Field(default="", description="Deskripsi detail tentang barang (warna, merk, ciri khas)")
    location: str = Field(default="", description="Lokasi detail tempat barang ditemukan")
    reporter_contact: str = Field(default="", description="Kontak penemu (No HP atau email)")

class SearchItemsInput(BaseModel):
    keyword: str = Field(default="", description="Kata kunci pencarian (nama atau deskripsi barang)")
    category: str = Field(default="", description="Filter kategori: elektronik/pakaian/dokumen/aksesoris/tas/kunci/lainnya")
    type: str = Field(default="", description="Filter tipe laporan ('lost' untuk hilang, 'found' untuk ditemukan)")

class ListRecentInput(BaseModel):
    limit: int = Field(default=10, description="Jumlah maksimal laporan yang ingin ditampilkan")

class MatchItemsInput(BaseModel):
    keyword: str = Field(default="", description="Kata kunci pencarian barang untuk dicocokkan")

# ── Tools ──────────────────────────────────────────────────────────

@tool(args_schema=ReportLostInput)
def report_lost_item(title: str, reporter_name: str, category: str = "lainnya", description: str = "", location: str = "", reporter_contact: str = "") -> str:
    """Simpan data laporan barang hilang ke database sistem ITK LostFound."""
    if not title.strip() or not reporter_name.strip():
        return "[ERROR] Nama barang dan nama pelapor tidak boleh kosong."

    valid_categories = [c.value for c in ItemCategory]
    if category not in valid_categories:
        category = "lainnya"

    db = SessionLocal()
    try:
        item = Item(
            unique_code=generate_unique_code(db),
            title=title,
            description=description,
            category=category,
            type=ItemType.lost.value,
            location=location,
            date_event=datetime.now(),
            status=ItemStatus.open.value,
            reporter_name=reporter_name,
            reporter_contact=reporter_contact,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return (
            f"[SUCCESS] Laporan barang hilang berhasil dibuat!\n"
            f"   Kode Unik: {item.unique_code}\n"
            f"   Barang: {title}\n"
            f"   Kategori: {category}\n"
            f"   Lokasi: {location or '-'}\n"
            f"   Pelapor: {reporter_name}\n"
        )
    finally:
        db.close()

@tool(args_schema=ReportFoundInput)
def report_found_item(title: str, reporter_name: str, category: str = "lainnya", description: str = "", location: str = "", reporter_contact: str = "") -> str:
    """Simpan data laporan barang yang ditemukan ke database sistem ITK LostFound."""
    if not title.strip() or not reporter_name.strip():
        return "[ERROR] Nama barang dan nama penemu tidak boleh kosong."

    valid_categories = [c.value for c in ItemCategory]
    if category not in valid_categories:
        category = "lainnya"

    db = SessionLocal()
    try:
        item = Item(
            unique_code=generate_unique_code(db),
            title=title,
            description=description,
            category=category,
            type=ItemType.found.value,
            location=location,
            date_event=datetime.now(),
            status=ItemStatus.open.value,
            reporter_name=reporter_name,
            reporter_contact=reporter_contact,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return (
            f"[SUCCESS] Laporan barang ditemukan berhasil dibuat!\n"
            f"   Kode Unik: {item.unique_code}\n"
            f"   Barang: {title}\n"
            f"   Kategori: {category}\n"
            f"   Lokasi: {location or '-'}\n"
            f"   Penemu: {reporter_name}\n"
        )
    finally:
        db.close()

@tool(args_schema=SearchItemsInput)
def search_items(keyword: str = "", category: str = "", type: str = "") -> str:
    """Cari daftar barang hilang atau ditemukan berdasarkan kata kunci, kategori, atau tipe."""
    db = SessionLocal()
    try:
        query = db.query(Item).order_by(Item.created_at.desc())

        if keyword:
            query = query.filter((Item.title.ilike(f"%{keyword}%")) | (Item.description.ilike(f"%{keyword}%")))
        if category:
            query = query.filter(Item.category == category)
        if type:
            query = query.filter(Item.type == type)

        items = query.limit(20).all()
        if not items:
            return "[INFO] Tidak ada barang yang cocok dengan pencarian."

        lines = ["**Hasil Pencarian:**\n"]
        for i, item in enumerate(items, 1):
            type_label = "HILANG" if item.type == "lost" else "DITEMUKAN"
            lines.append(
                f"{i}. [{type_label}] {item.title} (Kategori: {item.category}, Lokasi: {item.location or '-'})"
            )
        lines.append(f"Total: {len(items)} hasil")
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

        lines = ["**Laporan Terbaru:**\n"]
        for i, item in enumerate(items, 1):
            type_label = "HILANG" if item.type == "lost" else "DITEMUKAN"
            lines.append(f"{i}. [{type_label}] {item.title} - Lokasi: {item.location or '-'}")
        return "\n".join(lines)
    finally:
        db.close()

@tool(args_schema=MatchItemsInput)
def match_items(keyword: str = "") -> str:
    """Cari algoritma kecocokan antara laporan barang yang hilang dan barang yang ditemukan di database."""
    db = SessionLocal()
    try:
        lost_query = db.query(Item).filter(Item.type == "lost", Item.status == "open")
        found_query = db.query(Item).filter(Item.type == "found", Item.status == "open")

        if keyword:
            lost_query = lost_query.filter((Item.title.ilike(f"%{keyword}%")) | (Item.description.ilike(f"%{keyword}%")))
            found_query = found_query.filter((Item.title.ilike(f"%{keyword}%")) | (Item.description.ilike(f"%{keyword}%")))

        lost_items = lost_query.all()
        found_items = found_query.all()

        if not lost_items and not found_items:
            return "[INFO] Tidak ada data barang yang bisa dicocokkan."

        matches = []
        for lost in lost_items:
            for found in found_items:
                if lost.category == found.category:
                    score = 0
                    if lost.title.lower() in found.title.lower() or found.title.lower() in lost.title.lower():
                        score += 2
                    if lost.location and found.location and (lost.location.lower() in found.location.lower() or found.location.lower() in lost.location.lower()):
                        score += 1
                    if score > 0:
                        matches.append((lost, found, score))

        if not matches:
            return "[INFO] Tidak ditemukan kecocokan otomatis."

        matches.sort(key=lambda x: x[2], reverse=True)
        lines = ["**Kemungkinan Kecocokan:**\n"]
        for i, (lost, found, score) in enumerate(matches[:10], 1):
            lines.append(
                f"{i}. HILANG: '{lost.title}' dengan DITEMUKAN: '{found.title}'\n"
                f"   Skor kecocokan: {score}/3 | Kontak pemilik: {lost.reporter_name} | Kontak penemu: {found.reporter_name}"
            )
        return "\n".join(lines)
    finally:
        db.close()

# ── Agent Setup (Manual Tool Calling Loop) ─────────────────────────

tools = [report_lost_item, report_found_item, search_items, list_recent_items, match_items]

SYSTEM_PROMPT = """Kamu adalah asisten penjaga ITK LostFound, platform pencarian barang hilang dan ditemukan di kampus ITK.

PANDUAN SANGAT PENTING (BACA DENGAN TELITI):
1. BEDAKAN ANTARA "MENCARI" DAN "MELAPOR":
   - Jika pengguna berkata "saya mau cari barang", "carikan", atau "apakah ada", GUNAKAN `search_items`. 
   - JANGAN PERNAH menggunakan `report_lost_item` atau `report_found_item` jika pengguna hanya ingin mencari.
2. JANGAN BERHALUSINASI (MENGARANG DATA):
   - Jika pengguna ingin membuat laporan (hilang/ditemukan), kamu TIDAK BOLEH mengarang nama pelapor, judul barang, lokasi, dsb.
   - Jika data *title* atau *reporter_name* belum diberikan oleh pengguna, KAMU WAJIB BERTANYA terlebih dahulu sebelum memanggil tool pelaporan.
   - Jika ragu apakah pengguna ingin mencari atau melapor, BERTANYALAH untuk mengklarifikasi ("Apakah Anda ingin mencari barang ini di data kami, atau membuat laporan baru?").
3. RESPON INTERAKTIF:
   - Jika kamu selesai menggunakan `search_items` dan data ditemukan, bilang "Ini hasilnya di panel sebelah kiri. Apakah ada ciri spesifik yang ingin Anda tambahkan?". 
   - JANGAN sebutkan ulang isi laporan/data di layar chat. Cukup katakan "Data telah disinkronkan, silakan periksa di tabel sebelah kiri layar Anda."
4. ATURAN TOOL:
   - JIKA kamu memanggil tool, DILARANG KERAS menyertakan narasi/teks pengantar sebelum tool terpanggil. Langsung gunakan output JSON dari tool!
"""

llm_with_tools = llm.bind_tools(tools)

async def process_chat(message: str, chat_history: list = None) -> tuple[str, list]:
    """Process a user chat message with an explicit, deterministic 2-step tool calling loop."""
    from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=message)
    ]

    try:
        # Panggilan 1: Biarkan LLM memutuskan ingin memanggil tool atau langsung merespons
        response = await llm_with_tools.ainvoke(messages)
        messages.append(response)

        # Jika LLM memutuskan untuk memanggil tool
        if hasattr(response, "tool_calls") and response.tool_calls:
            tools_used = []
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call.get("args", {})
                tool_id = tool_call["id"]
                
                tools_used.append({"name": tool_name, "args": tool_args})
                
                tool_result = "[ERROR] Alat tidak ditemukan"
                # Cari dan jalankan tool yang sesuai
                for t in tools:
                    if t.name == tool_name:
                        try:
                            tool_result = t.invoke(tool_args)
                        except Exception as e:
                            tool_result = f"[ERROR] Gagal mengeksekusi tool: {str(e)}"
                        break
                
                # Masukkan hasil tool ke dalam riwayat pesan
                messages.append(ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_id,
                    name=tool_name
                ))
            
            # Panggilan 2: LLM memberikan jawaban akhir berdasarkan hasil tool
            final_response = await llm_with_tools.ainvoke(messages)
            return final_response.content, tools_used
        
        # Jika tidak memanggil tool, langsung return pesan
        return response.content, []

    except Exception as e:
        import traceback
        traceback.print_exc()
        error_str = str(e)
        if "tool_use_failed" in error_str.lower():
            return "Maaf, ada kendala teknis saat memproses alat (tool_use_failed). Coba ubah sedikit struktur kalimat Anda."
        if "rate limit" in error_str.lower():
            return "Server AI sedang sibuk (Rate Limit). Mohon tunggu beberapa detik sebelum mencoba lagi."
        return f"[INFO] Sistem sedang kelebihan beban. Mohon dicoba beberapa saat lagi. Detail: {error_str}"
