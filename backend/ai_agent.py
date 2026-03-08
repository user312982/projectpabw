"""
LangChain AI Agent with 6 tools for BizLedger AI.

Tools:
1. add_product       — Tambah produk baru
2. list_products     — Lihat semua produk
3. create_invoice    — Buat faktur baru (otomatis kurangi stok)
4. list_invoices     — Lihat semua faktur
5. get_sales_today   — Total penjualan hari ini
6. get_low_stock     — Produk dengan stok menipis
"""

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from database import SessionLocal, Product, Invoice, InvoiceItem
from datetime import datetime, timedelta
import json
import os
import traceback

# ── LLM Setup (Groq — Free & Fast) ────────────────────────────────

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

# ── Tools ──────────────────────────────────────────────────────────


@tool
def add_product(name: str, sell_price: float, stock_qty: int, min_stock: int = 10) -> str:
    """Tambah produk baru ke database.
    Gunakan tool ini ketika user ingin menambahkan produk/barang baru.

    Args:
        name: Nama produk
        sell_price: Harga jual produk
        stock_qty: Jumlah stok awal
        min_stock: Batas minimum stok (default 10)
    """
    db = SessionLocal()
    try:
        # Check if product already exists
        existing = db.query(Product).filter(
            Product.name.ilike(name), Product.is_active == True
        ).first()
        if existing:
            return f"[ERROR] Produk '{name}' sudah ada. Stok saat ini: {existing.stock_qty}"

        product = Product(
            name=name,
            sell_price=sell_price,
            stock_qty=stock_qty,
            min_stock=min_stock,
        )
        db.add(product)
        db.commit()
        return f"[SUCCESS] Produk '{name}' berhasil ditambahkan!\n   Harga jual: Rp{sell_price:,.0f}\n   Stok: {stock_qty}\n   Min stok: {min_stock}"
    finally:
        db.close()


@tool
def list_products() -> str:
    """Lihat daftar semua produk yang aktif.
    Gunakan tool ini ketika user ingin melihat semua produk/barang/stok.
    """
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.is_active == True).all()
        if not products:
            return "[INFO] Belum ada produk. Silakan tambahkan produk terlebih dahulu."

        lines = ["**Daftar Produk:**\n"]
        lines.append(f"{'No':<4} {'Nama':<25} {'Harga Jual':<15} {'Stok':<8} {'Min':<5}")
        lines.append("-" * 60)
        for i, p in enumerate(products, 1):
            alert = " (!)" if p.stock_qty <= p.min_stock else ""
            lines.append(
                f"{i:<4} {p.name:<25} Rp{p.sell_price:<13,.0f} {p.stock_qty:<8} {p.min_stock:<5}{alert}"
            )
        lines.append(f"\nTotal: {len(products)} produk")
        return "\n".join(lines)
    finally:
        db.close()


@tool
def create_invoice(customer_name: str, items: list[dict]) -> str:
    """Buat faktur baru dan otomatis kurangi stok produk.
    Gunakan tool ini ketika user ingin membuat faktur/invoice.

    Args:
        customer_name: Nama pelanggan
        items: List of items, each with 'product_name' and 'quantity'.
               Example: [{"product_name": "Kopi Arabica", "quantity": 10}]
    """
    db = SessionLocal()
    try:
        # Generate invoice number
        today = datetime.now().strftime("%Y%m%d")
        count = db.query(Invoice).filter(
            Invoice.invoice_no.like(f"INV-{today}%")
        ).count()
        invoice_no = f"INV-{today}-{count + 1:03d}"

        invoice_items = []
        total = 0
        errors = []

        for item_data in items:
            product_name = item_data.get("product_name", "")
            quantity = item_data.get("quantity", 0)

            # Find product
            product = db.query(Product).filter(
                Product.name.ilike(f"%{product_name}%"),
                Product.is_active == True
            ).first()

            if not product:
                errors.append(f"Produk '{product_name}' tidak ditemukan")
                continue

            if product.stock_qty < quantity:
                errors.append(
                    f"Stok '{product.name}' tidak cukup (tersisa: {product.stock_qty})"
                )
                continue

            subtotal = product.sell_price * quantity
            total += subtotal

            invoice_items.append(
                InvoiceItem(
                    product_id=product.id,
                    product_name=product.name,
                    quantity=quantity,
                    unit_price=product.sell_price,
                    subtotal=subtotal,
                )
            )

            # Reduce stock
            product.stock_qty -= quantity

        if errors:
            return "[ERROR] Gagal membuat faktur:\n" + "\n".join(f"  - {e}" for e in errors)

        if not invoice_items:
            return "[ERROR] Tidak ada item valid untuk faktur."

        invoice = Invoice(
            invoice_no=invoice_no,
            customer_name=customer_name,
            total=total,
        )
        db.add(invoice)
        db.flush()

        for inv_item in invoice_items:
            inv_item.invoice_id = invoice.id
            db.add(inv_item)

        db.commit()

        # Build response
        lines = [f"[SUCCESS] Faktur {invoice_no} berhasil dibuat!\n"]
        lines.append(f"Pelanggan: {customer_name}")
        lines.append(f"{'Produk':<25} {'Qty':<6} {'Harga':<15} {'Subtotal':<15}")
        lines.append("-" * 65)
        for inv_item in invoice_items:
            lines.append(
                f"{inv_item.product_name:<25} {inv_item.quantity:<6} "
                f"Rp{inv_item.unit_price:<13,.0f} Rp{inv_item.subtotal:,.0f}"
            )
        lines.append("-" * 65)
        lines.append(f"{'TOTAL':<47} Rp{total:,.0f}")
        return "\n".join(lines)
    finally:
        db.close()


@tool
def list_invoices() -> str:
    """Lihat daftar semua faktur.
    Gunakan tool ini ketika user ingin melihat semua faktur/invoice.
    """
    db = SessionLocal()
    try:
        invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).limit(20).all()
        if not invoices:
            return "[INFO] Belum ada faktur."

        lines = ["**Daftar Faktur (20 terakhir):**\n"]
        lines.append(f"{'No Faktur':<20} {'Pelanggan':<25} {'Total':<15} {'Tanggal':<12}")
        lines.append("-" * 75)
        for inv in invoices:
            date_str = inv.created_at.strftime("%d/%m/%Y")
            lines.append(
                f"{inv.invoice_no:<20} {inv.customer_name:<25} Rp{inv.total:<13,.0f} {date_str}"
            )
        return "\n".join(lines)
    finally:
        db.close()


@tool
def get_sales_today() -> str:
    """Hitung total penjualan hari ini.
    Gunakan tool ini ketika user bertanya berapa total penjualan / pendapatan hari ini.
    """
    db = SessionLocal()
    try:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        invoices = db.query(Invoice).filter(Invoice.created_at >= today_start).all()

        if not invoices:
            return "[INFO] Belum ada penjualan hari ini."

        total = sum(inv.total for inv in invoices)
        return (
            f"**Penjualan Hari Ini:**\n"
            f"   Jumlah faktur: {len(invoices)}\n"
            f"   Total penjualan: Rp{total:,.0f}"
        )
    finally:
        db.close()


@tool
def get_low_stock() -> str:
    """Cek produk yang stoknya menipis (di bawah batas minimum).
    Gunakan tool ini ketika user bertanya produk apa yang stoknya hampir habis / menipis.
    """
    db = SessionLocal()
    try:
        products = (
            db.query(Product)
            .filter(Product.is_active == True, Product.stock_qty <= Product.min_stock)
            .all()
        )

        if not products:
            return "[SUCCESS] Semua produk memiliki stok yang cukup!"

        lines = ["**Produk Stok Menipis:**\n"]
        for p in products:
            lines.append(
                f"  - {p.name}: {p.stock_qty} tersisa (minimum: {p.min_stock})"
            )
        return "\n".join(lines)
    finally:
        db.close()


# ── Agent Setup ────────────────────────────────────────────────────

tools = [add_product, list_products, create_invoice, list_invoices, get_sales_today, get_low_stock]

REACT_PROMPT = """Kamu adalah asisten AI untuk aplikasi BizLedger, sebuah sistem pencatatan keuangan bisnis.
Kamu membantu pengguna mengelola stok produk dan faktur melalui percakapan bahasa Indonesia.

ATURAN PENTING:
- Selalu jawab dalam bahasa Indonesia
- JANGAN gunakan emoji apapun
- Format angka uang dengan Rp dan pemisah ribuan
- Jika user meminta sesuatu di luar kemampuanmu, jelaskan bahwa fitur tersebut belum tersedia
- Jika informasi kurang (misal harga atau jumlah), tanyakan ke pengguna

Kamu memiliki akses ke tools berikut:

{tools}

Gunakan format berikut:

Question: pertanyaan input dari user
Thought: kamu harus selalu berpikir tentang apa yang harus dilakukan
Action: nama tool yang akan digunakan, harus salah satu dari [{tool_names}]
Action Input: input untuk tool tersebut (gunakan format JSON, contoh: {{"name": "Kopi"}}, untuk tool tanpa input gunakan: {{}})
Observation: hasil dari tool
... (langkah Thought/Action/Action Input/Observation ini bisa diulang beberapa kali)
Thought: Aku sudah tahu jawaban akhirnya
Final Answer: jawaban akhir untuk pertanyaan user

Mulai!

Question: {input}
Thought:{agent_scratchpad}"""

react_prompt = PromptTemplate.from_template(REACT_PROMPT)

agent = create_react_agent(llm, tools, react_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors="Terjadi error parsing. Coba format ulang Action Input dalam JSON yang valid.",
    max_iterations=5,
)


async def process_chat(message: str, chat_history: list = None) -> str:
    """Process a user chat message through the AI agent."""
    max_retries = 2
    last_error = None

    for attempt in range(max_retries):
        try:
            result = await agent_executor.ainvoke({
                "input": message,
            })
            return result["output"]
        except Exception as e:
            last_error = e
            print(f"[RETRY {attempt + 1}/{max_retries}] Error in agent: {e}")
            traceback.print_exc()
            if attempt < max_retries - 1:
                continue

    return f"[ERROR] Gagal memproses perintah. Silakan coba lagi. Detail: {str(last_error)}"
