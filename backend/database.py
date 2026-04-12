"""
ITK LostFound — Database Models
"""

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import enum

DATABASE_URL = "sqlite:///./data/lostfound.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── Enums ───────────────────────────────────────────────────────────


class UserRole(str, enum.Enum):
    user = "user"
    petugas = "petugas"


class ItemType(str, enum.Enum):
    lost = "lost"
    found = "found"


class ItemCategory(str, enum.Enum):
    elektronik = "elektronik"
    pakaian = "pakaian"
    dokumen = "dokumen"
    aksesoris = "aksesoris"
    tas = "tas"
    kunci = "kunci"
    lainnya = "lainnya"


class ItemStatus(str, enum.Enum):
    open = "open"
    claimed = "claimed"
    closed = "closed"


# ── Models ──────────────────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    nim = Column(String(20), nullable=True)
    role = Column(String(20), nullable=False, default=UserRole.user.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    klaim_processed = relationship("KlaimBarang", back_populates="petugas")

    def __repr__(self):
        return f"<User {self.username} | {self.role}>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "nim": self.nim,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    unique_code = Column(String(50), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default=ItemCategory.lainnya.value)
    type = Column(String(10), nullable=False, default=ItemType.lost.value)
    location = Column(String(255), nullable=True)
    date_event = Column(DateTime, nullable=True)  # when lost/found
    image_url = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default=ItemStatus.open.value)
    reporter_name = Column(String(255), nullable=False)
    reporter_contact = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    klaims = relationship("KlaimBarang", back_populates="item")

    def __repr__(self):
        return f"<Item {self.title} | {self.type} | {self.status}>"

    def to_dict(self):
        return {
            "id": self.id,
            "unique_code": self.unique_code,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "type": self.type,
            "location": self.location,
            "date_event": self.date_event.isoformat() if self.date_event else None,
            "image_url": self.image_url,
            "status": self.status,
            "reporter_name": self.reporter_name,
            "reporter_contact": self.reporter_contact,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class KlaimBarang(Base):
    __tablename__ = "klaim_barang"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    nama_pengklaim = Column(String(255), nullable=False)
    nim_pengklaim = Column(String(20), nullable=False)
    kontak_pengklaim = Column(String(255), nullable=False)
    tanggal_klaim = Column(DateTime, default=datetime.utcnow)
    petugas_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    item = relationship("Item", back_populates="klaims")
    petugas = relationship("User", back_populates="klaim_processed")

    def __repr__(self):
        return f"<Klaim item={self.item_id} by {self.nama_pengklaim}>"

    def to_dict(self):
        return {
            "id": self.id,
            "item_id": self.item_id,
            "nama_pengklaim": self.nama_pengklaim,
            "nim_pengklaim": self.nim_pengklaim,
            "kontak_pengklaim": self.kontak_pengklaim,
            "tanggal_klaim": self.tanggal_klaim.isoformat() if self.tanggal_klaim else None,
            "petugas_id": self.petugas_id,
            "petugas_name": self.petugas.full_name if self.petugas else None,
            "item_title": self.item.title if self.item else None,
        }


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


def generate_unique_code(db):
    """Helper to generate a random 6-character code."""
    import string
    import random
    while True:
        code = "LF-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not db.query(Item).filter(Item.unique_code == code).first():
            return code
