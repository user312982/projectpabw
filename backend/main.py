"""
BizLedger AI — FastAPI Backend
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env BEFORE importing ai_agent (which needs GROQ_API_KEY at module level)
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Also check parent directory (when running from project root)
    env_parent = Path(__file__).parent.parent / ".env"
    if env_parent.exists():
        load_dotenv(env_parent)
    else:
        load_dotenv()

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from database import init_db, get_db, Product, Invoice
from ai_agent import process_chat

# ── App ─────────────────────────────────────────────────────────────

app = FastAPI(title="BizLedger AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


# ── Schemas ─────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


# ── Routes: AI Chat ─────────────────────────────────────────────────


@app.post("/api/ai/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Kirim perintah ke AI assistant."""
    response = await process_chat(request.message)
    return ChatResponse(response=response)


# ── Routes: Products (read-only) ────────────────────────────────────


@app.get("/api/products")
def get_products(db: Session = Depends(get_db)):
    """Get all active products."""
    products = db.query(Product).filter(Product.is_active == True).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "sell_price": p.sell_price,
            "stock_qty": p.stock_qty,
            "min_stock": p.min_stock,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in products
    ]


# ── Routes: Invoices (read-only) ────────────────────────────────────


@app.get("/api/invoices")
def get_invoices(db: Session = Depends(get_db)):
    """Get all invoices, most recent first."""
    invoices = (
        db.query(Invoice).order_by(Invoice.created_at.desc()).limit(50).all()
    )
    return [
        {
            "id": inv.id,
            "invoice_no": inv.invoice_no,
            "customer_name": inv.customer_name,
            "total": inv.total,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
            "items": [
                {
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "subtotal": item.subtotal,
                }
                for item in inv.items
            ],
        }
        for inv in invoices
    ]


# ── Routes: Dashboard ───────────────────────────────────────────────


@app.get("/api/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary data."""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    total_products = db.query(Product).filter(Product.is_active == True).count()
    low_stock = (
        db.query(Product)
        .filter(Product.is_active == True, Product.stock_qty <= Product.min_stock)
        .count()
    )
    invoices_today = db.query(Invoice).filter(Invoice.created_at >= today_start).all()
    total_sales_today = sum(inv.total for inv in invoices_today)

    return {
        "total_products": total_products,
        "low_stock_count": low_stock,
        "invoices_today": len(invoices_today),
        "total_sales_today": total_sales_today,
    }
