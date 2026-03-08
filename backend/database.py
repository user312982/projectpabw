from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./data/bizledger.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── Models ──────────────────────────────────────────────────────────


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    sell_price = Column(Float, nullable=False, default=0)
    stock_qty = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, nullable=False, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Product {self.name} | Stok: {self.stock_qty} | Harga: Rp{self.sell_price:,.0f}>"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_no = Column(String(20), unique=True, nullable=False)
    customer_name = Column(String(255), nullable=False)
    total = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("InvoiceItem", back_populates="invoice")

    def __repr__(self):
        return f"<Invoice {self.invoice_no} | {self.customer_name} | Rp{self.total:,.0f}>"


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    invoice = relationship("Invoice", back_populates="items")


# ── Helpers ─────────────────────────────────────────────────────────


def init_db():
    """Create all tables if they don't exist."""
    import os

    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency: yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
