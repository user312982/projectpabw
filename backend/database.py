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
    Boolean,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone
import enum
import random
import string

DATABASE_URL = "sqlite:///./data/lostfound.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    nim = Column(String(20), nullable=True)
    role = Column(String(20), nullable=False, default=UserRole.user.value)
    is_active = Column(Boolean, nullable=False, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    klaim_processed = relationship("KlaimBarang", back_populates="petugas")
    items = relationship("Item", back_populates="uploader")

    def __repr__(self):
        return f"<User {self.username} | {self.role}>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "nim": self.nim,
            "role": self.role,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
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
    date_event = Column(DateTime, nullable=True)
    image_url = Column(String(500), nullable=True)
    image_mime = Column(String(100), nullable=True)
    image_size = Column(Integer, nullable=True)
    image_hash = Column(String(64), nullable=True)
    image_uploaded_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default=ItemStatus.open.value)
    reporter_name = Column(String(255), nullable=True)
    reporter_contact = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    klaims = relationship("KlaimBarang", back_populates="item")
    uploader = relationship("User", back_populates="items")

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
            "image_mime": self.image_mime,
            "image_size": self.image_size,
            "image_hash": self.image_hash,
            "image_uploaded_at": self.image_uploaded_at.isoformat() if self.image_uploaded_at else None,
            "status": self.status,
            "reporter_name": self.reporter_name,
            "reporter_contact": self.reporter_contact,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "uploader_id": self.uploader_id,
            "uploader_name": self.uploader.full_name if self.uploader else None,
        }


class KlaimBarang(Base):
    __tablename__ = "klaim_barang"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    nama_pengklaim = Column(String(255), nullable=False)
    nim_pengklaim = Column(String(20), nullable=False)
    kontak_pengklaim = Column(String(255), nullable=True)
    tanggal_klaim = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    petugas_id = Column(Integer, ForeignKey("users.id"), nullable=False)

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


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    jti = Column(String(255), unique=True, nullable=False, index=True)
    token_type = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    import os

    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)

    _migrate_reporter_name_nullable()
    _migrate_user_new_columns()
    _migrate_kontak_nullable()
    _migrate_item_photo_columns()


def _migrate_reporter_name_nullable():
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    if "items" not in inspector.get_table_names():
        return
    columns = {col["name"]: col for col in inspector.get_columns("items")}
    if "reporter_name" in columns and not columns["reporter_name"]["nullable"]:
        with engine.begin() as conn:
            conn.execute(text("PRAGMA foreign_keys=OFF"))
            conn.execute(text(
                "CREATE TABLE items_new ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "unique_code VARCHAR(50) NOT NULL UNIQUE, "
                "title VARCHAR(255) NOT NULL, "
                "description TEXT, "
                "category VARCHAR(50) NOT NULL DEFAULT 'lainnya', "
                "type VARCHAR(10) NOT NULL DEFAULT 'lost', "
                "location VARCHAR(255), "
                "date_event DATETIME, "
                "image_url VARCHAR(500), "
                "status VARCHAR(20) NOT NULL DEFAULT 'open', "
                "reporter_name VARCHAR(255), "
                "reporter_contact VARCHAR(255), "
                "created_at DATETIME, "
                "uploader_id INTEGER, "
                "FOREIGN KEY(uploader_id) REFERENCES users(id))"
            ))
            conn.execute(text("INSERT INTO items_new SELECT * FROM items"))
            conn.execute(text("DROP TABLE items"))
            conn.execute(text("ALTER TABLE items_new RENAME TO items"))
            conn.execute(text("CREATE UNIQUE INDEX ix_items_unique_code ON items(unique_code)"))
            conn.execute(text("CREATE INDEX ix_items_id ON items(id)"))
            conn.execute(text("PRAGMA foreign_keys=ON"))


def _migrate_user_new_columns():
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    columns = {col["name"]: col for col in inspector.get_columns("users")}
    with engine.begin() as conn:
        if "is_active" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1"))
        if "last_login" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN last_login DATETIME"))


def _migrate_kontak_nullable():
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    if "klaim_barang" not in inspector.get_table_names():
        return

    columns = {col["name"]: col for col in inspector.get_columns("klaim_barang")}
    if "kontak_pengklaim" in columns and not columns["kontak_pengklaim"]["nullable"]:
        with engine.begin() as conn:
            conn.execute(text("PRAGMA foreign_keys=OFF"))
            conn.execute(text(
                "CREATE TABLE klaim_barang_new ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "item_id INTEGER NOT NULL, "
                "nama_pengklaim VARCHAR(255) NOT NULL, "
                "nim_pengklaim VARCHAR(20) NOT NULL, "
                "kontak_pengklaim VARCHAR(255), "
                "tanggal_klaim DATETIME, "
                "petugas_id INTEGER NOT NULL, "
                "FOREIGN KEY(item_id) REFERENCES items(id), "
                "FOREIGN KEY(petugas_id) REFERENCES users(id))"
            ))
            conn.execute(text("INSERT INTO klaim_barang_new SELECT * FROM klaim_barang"))
            conn.execute(text("DROP TABLE klaim_barang"))
            conn.execute(text("ALTER TABLE klaim_barang_new RENAME TO klaim_barang"))
            conn.execute(text("CREATE INDEX ix_klaim_barang_id ON klaim_barang(id)"))
            conn.execute(text("PRAGMA foreign_keys=ON"))


def _migrate_item_photo_columns():
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    if "items" not in inspector.get_table_names():
        return

    columns = {col["name"]: col for col in inspector.get_columns("items")}
    statements = []
    if "image_mime" not in columns:
        statements.append("ALTER TABLE items ADD COLUMN image_mime VARCHAR(100)")
    if "image_size" not in columns:
        statements.append("ALTER TABLE items ADD COLUMN image_size INTEGER")
    if "image_hash" not in columns:
        statements.append("ALTER TABLE items ADD COLUMN image_hash VARCHAR(64)")
    if "image_uploaded_at" not in columns:
        statements.append("ALTER TABLE items ADD COLUMN image_uploaded_at DATETIME")

    if statements:
        with engine.begin() as conn:
            for stmt in statements:
                conn.execute(text(stmt))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_unique_code(db, prefix: str = "LF", length: int = 6) -> str:
    """Generate unique item code like LF-ABC123."""
    while True:
        random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
        code = f"{prefix}-{random_part}"
        exists = db.query(Item).filter(Item.unique_code == code).first()
        if not exists:
            return code
