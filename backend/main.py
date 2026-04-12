"""
ITK LostFound — FastAPI Backend
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env BEFORE importing ai_agent (which needs GROQ_API_KEY at module level)
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    env_parent = Path(__file__).parent.parent / ".env"
    if env_parent.exists():
        load_dotenv(env_parent)
    else:
        load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from database import (
    init_db,
    get_db,
    generate_unique_code,
    User,
    UserRole,
    Item,
    ItemType,
    ItemCategory,
    ItemStatus,
    KlaimBarang,
)
from ai_agent import process_chat

# ── Config ──────────────────────────────────────────────────────────

SECRET_KEY = os.getenv("SECRET_KEY", "itk-lostfound-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

# ── App ─────────────────────────────────────────────────────────────

app = FastAPI(title="ITK LostFound", version="1.0.0")

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


# ── Auth Helpers ────────────────────────────────────────────────────


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user from JWT token. Returns None if no token."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    user = db.query(User).filter(User.username == username).first()
    return user


async def require_user(
    user: Optional[User] = Depends(get_current_user),
) -> User:
    """Require authenticated user."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login diperlukan",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_petugas(
    user: User = Depends(require_user),
) -> User:
    """Require authenticated petugas."""
    if user.role != UserRole.petugas.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya petugas yang bisa mengakses fitur ini",
        )
    return user


# ── Schemas ─────────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str
    nim: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "lainnya"
    type: str = "lost"
    location: Optional[str] = None
    date_event: Optional[str] = None
    image_url: Optional[str] = None
    reporter_name: str
    reporter_contact: Optional[str] = None


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    date_event: Optional[str] = None
    image_url: Optional[str] = None
    reporter_name: Optional[str] = None
    reporter_contact: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str


class KlaimCreate(BaseModel):
    nama_pengklaim: str
    nim_pengklaim: str
    kontak_pengklaim: str


class ClaimByCodeRequest(BaseModel):
    unique_code: str
    nama_pengklaim: str
    nim_pengklaim: str
    kontak_pengklaim: str


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    tools_used: Optional[list] = None


# ── Routes: Auth ────────────────────────────────────────────────────


@app.post("/api/auth/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check duplicate username
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Username sudah digunakan",
        )

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        nim=data.nim,
        role=UserRole.user.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Auto-login after register
    token = create_access_token(data={"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }


@app.post("/api/auth/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get JWT token."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }


@app.get("/api/auth/me")
def get_me(user: User = Depends(require_user)):
    """Get current user info."""
    return user.to_dict()


# ── Routes: AI Chat ─────────────────────────────────────────────────


@app.post("/api/ai/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Kirim perintah ke AI assistant."""
    result = await process_chat(request.message)
    if isinstance(result, tuple):
        return ChatResponse(response=result[0], tools_used=result[1])
    return ChatResponse(response=result)


# ── Routes: Items CRUD ──────────────────────────────────────────────


@app.get("/api/items")
def get_items(
    type: Optional[str] = Query(None, description="Filter by type: lost or found"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by title/description"),
    db: Session = Depends(get_db),
):
    """Get all items with optional filters."""
    query = db.query(Item).order_by(Item.created_at.desc())

    if type:
        query = query.filter(Item.type == type)
    if category:
        query = query.filter(Item.category == category)
    if status:
        query = query.filter(Item.status == status)
    if search:
        query = query.filter(
            (Item.title.ilike(f"%{search}%"))
            | (Item.description.ilike(f"%{search}%"))
        )

    items = query.limit(100).all()
    return [item.to_dict() for item in items]


@app.get("/api/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item by ID."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")
    return item.to_dict()


@app.post("/api/items", status_code=201)
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    """Create a new lost or found item report."""
    date_event = None
    if data.date_event:
        try:
            date_event = datetime.fromisoformat(data.date_event)
        except ValueError:
            raise HTTPException(status_code=400, detail="Format tanggal tidak valid")

    item = Item(
        unique_code=generate_unique_code(db),
        title=data.title,
        description=data.description,
        category=data.category,
        type=data.type,
        location=data.location,
        date_event=date_event,
        image_url=data.image_url,
        status=ItemStatus.open.value,
        reporter_name=data.reporter_name,
        reporter_contact=data.reporter_contact,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item.to_dict()


@app.put("/api/items/{item_id}")
def update_item(item_id: int, data: ItemUpdate, db: Session = Depends(get_db)):
    """Update an existing item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")

    update_data = data.model_dump(exclude_unset=True)
    if "date_event" in update_data and update_data["date_event"]:
        try:
            update_data["date_event"] = datetime.fromisoformat(
                update_data["date_event"]
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Format tanggal tidak valid")

    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item.to_dict()


@app.patch("/api/items/{item_id}/status")
def update_item_status(
    item_id: int, data: StatusUpdate, db: Session = Depends(get_db)
):
    """Update item status (open, claimed, closed)."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")

    if data.status not in [s.value for s in ItemStatus]:
        raise HTTPException(
            status_code=400,
            detail=f"Status tidak valid. Gunakan: {[s.value for s in ItemStatus]}",
        )

    item.status = data.status
    db.commit()
    db.refresh(item)
    return item.to_dict()


@app.delete("/api/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_petugas),
):
    """Delete an item (petugas only)."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")

    db.delete(item)
    db.commit()
    return {"detail": "Item berhasil dihapus"}


# ── Routes: Klaim Barang ────────────────────────────────────────────


@app.post("/api/items/claim-by-code", status_code=201)
def claim_item_by_code(
    data: ClaimByCodeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_petugas),
):
    """Process a claim for an item using its unique code (petugas only)."""
    item = db.query(Item).filter(Item.unique_code == data.unique_code).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan dengan kode tersebut")

    if item.status == ItemStatus.claimed.value:
        raise HTTPException(status_code=400, detail="Item sudah diklaim sebelumnya")

    # Create klaim record
    klaim = KlaimBarang(
        item_id=item.id,
        nama_pengklaim=data.nama_pengklaim,
        nim_pengklaim=data.nim_pengklaim,
        kontak_pengklaim=data.kontak_pengklaim,
        petugas_id=user.id,
    )
    db.add(klaim)

    # Update item status to claimed
    item.status = ItemStatus.claimed.value
    db.commit()
    db.refresh(klaim)

    return klaim.to_dict()


@app.post("/api/items/{item_id}/claim", status_code=201)
def claim_item(
    item_id: int,
    data: KlaimCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_petugas),
):
    """Process a claim for an item (petugas only)."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")

    if item.status == ItemStatus.claimed.value:
        raise HTTPException(status_code=400, detail="Item sudah diklaim")

    # Create klaim record
    klaim = KlaimBarang(
        item_id=item_id,
        nama_pengklaim=data.nama_pengklaim,
        nim_pengklaim=data.nim_pengklaim,
        kontak_pengklaim=data.kontak_pengklaim,
        petugas_id=user.id,
    )
    db.add(klaim)

    # Update item status to claimed
    item.status = ItemStatus.claimed.value
    db.commit()
    db.refresh(klaim)

    return klaim.to_dict()


@app.get("/api/items/{item_id}/claims")
def get_item_claims(item_id: int, db: Session = Depends(get_db)):
    """Get claim history for an item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")

    klaims = (
        db.query(KlaimBarang)
        .filter(KlaimBarang.item_id == item_id)
        .order_by(KlaimBarang.tanggal_klaim.desc())
        .all()
    )
    return [k.to_dict() for k in klaims]


@app.get("/api/claims")
def get_all_claims(
    db: Session = Depends(get_db),
    user: User = Depends(require_petugas),
):
    """Get all claims (petugas only)."""
    klaims = (
        db.query(KlaimBarang)
        .order_by(KlaimBarang.tanggal_klaim.desc())
        .limit(100)
        .all()
    )
    return [k.to_dict() for k in klaims]


# ── Routes: Dashboard ───────────────────────────────────────────────


@app.get("/api/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary data."""
    total_lost = db.query(Item).filter(Item.type == "lost").count()
    total_found = db.query(Item).filter(Item.type == "found").count()
    total_open = db.query(Item).filter(Item.status == "open").count()
    total_claimed = db.query(Item).filter(Item.status == "claimed").count()
    total_closed = db.query(Item).filter(Item.status == "closed").count()

    return {
        "total_lost": total_lost,
        "total_found": total_found,
        "total_open": total_open,
        "total_claimed": total_claimed,
        "total_closed": total_closed,
    }
