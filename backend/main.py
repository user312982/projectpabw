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

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from ai_agent import process_chat
from database import (
    Item,
    ItemCategory,
    ItemStatus,
    ItemType,
    KlaimBarang,
    TokenBlacklist,
    User,
    UserRole,
    generate_unique_code,
    get_db,
    init_db,
)
from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from rag import rag_system
from sqlalchemy import func
from sqlalchemy.orm import Session

# ── Config ──────────────────────────────────────────────────────────

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set. Please set it in .env file.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7

ADMIN_KEY = os.getenv("ADMIN_KEY", "change-me-admin-key")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

# ── Rate Limiter (in-memory) ──────────────────────────────────────────

from collections import defaultdict, deque

_login_attempts: dict = defaultdict(list)
LOGIN_MAX_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 60


def _clean_old_attempts(ip: str):
    now = datetime.now(timezone.utc)
    _login_attempts[ip] = [
        t for t in _login_attempts[ip]
        if (now - t).total_seconds() < LOGIN_WINDOW_SECONDS
    ]


def _is_rate_limited(ip: str) -> bool:
    _clean_old_attempts(ip)
    return len(_login_attempts[ip]) >= LOGIN_MAX_ATTEMPTS


# ── App ─────────────────────────────────────────────────────────────

app = FastAPI(title="ITK LostFound", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    # Skip RAG reindex di startup (membutuhkan download model 79MB, lambat)
    # try:
    #     rag_system.reindex_all()
    #     print("RAG system initialized and reindexed successfully")
    # except Exception as e:
    #     print(f"RAG initialization warning: {e}")
    #     print("Chatbot will work with fallback search instead of RAG")


# ── Auth Helpers ────────────────────────────────────────────────────


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, token_type: str = "access", expires_delta: Optional[timedelta] = None):
    import uuid
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: int):
    return create_access_token(user_id, token_type="refresh", expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


def _is_token_blacklisted(jti: str, db: Session) -> bool:
    return db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first() is not None


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user from JWT token. Returns None if no valid token."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return None
        jti = payload.get("jti")
        if jti and _is_token_blacklisted(jti, db):
            return None
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            return None
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        return None
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None
    if not user.is_active:
        return None
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
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1)
    nim: Optional[str] = None


class RegisterPetugasRequest(BaseModel):
    admin_key: str
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1)
    nim: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
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
    reporter_name: Optional[str] = None
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
    kontak_pengklaim: Optional[str] = None


class ClaimByCodeRequest(BaseModel):
    unique_code: str
    nama_pengklaim: str
    nim_pengklaim: str
    kontak_pengklaim: Optional[str] = None


class ChatMessage(BaseModel):
    role: str  # "user" or "ai"
    text: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    response: str
    tools_used: Optional[list] = None


# ── Routes: Auth ────────────────────────────────────────────────────


@app.post("/api/auth/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=[{"loc": ["body", "username"], "msg": "Username sudah digunakan"}],
        )

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        nim=data.nim,
        role=UserRole.user.value,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return {
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }


@app.post("/api/auth/login", response_model=LoginResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login and get JWT token."""
    client_ip = request.client.host if request.client else "unknown"
    if _is_rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Terlalu banyak percobaan login. Coba lagi nanti.",
        )

    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        _login_attempts[client_ip].append(datetime.now(timezone.utc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[{"loc": ["body", "password"], "msg": "Kredensial tidak valid"}],
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=[{"loc": ["body", "username"], "msg": "Akun dinonaktifkan. Hubungi petugas."}],
        )

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return {
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }


@app.post("/api/auth/register-petugas", status_code=201)
def register_petugas(data: RegisterPetugasRequest, db: Session = Depends(get_db)):
    """Register a new petugas/admin account. Requires ADMIN_KEY."""
    if data.admin_key != ADMIN_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kunci admin tidak valid",
        )

    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=[{"loc": ["body", "username"], "msg": "Username sudah digunakan"}],
        )

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        nim=data.nim,
        role=UserRole.petugas.value,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return {
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }


@app.post("/api/auth/refresh")
def refresh_token_endpoint(
    data: RefreshRequest,
    db: Session = Depends(get_db),
):
    """Refresh access token using a valid refresh token."""
    try:
        payload = jwt.decode(data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token bukan refresh token")
        jti = payload.get("jti")
        if jti and _is_token_blacklisted(jti, db):
            raise HTTPException(status_code=401, detail="Token telah dibatalkan")
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(status_code=401, detail="Token tidak valid")
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Token tidak valid atau kadaluarsa")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="Akun tidak ditemukan atau dinonaktifkan")

    # Blacklist the old refresh token
    old_jti = payload.get("jti")
    if old_jti:
        exp = payload.get("exp")
        expire_dt = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else None
        blacklisted = TokenBlacklist(
            jti=old_jti,
            token_type="refresh",
            user_id=user_id,
            expires_at=expire_dt,
        )
        db.add(blacklisted)
        db.commit()

    new_access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@app.post("/api/auth/logout")
def logout(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Logout: blacklist current access token so it cannot be reused."""
    if not token:
        return {"detail": "Tidak ada token"}
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        user_id_str = payload.get("sub")
        exp = payload.get("exp")
        if jti and user_id_str:
            expire_dt = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else None
            blacklisted = TokenBlacklist(
                jti=jti,
                token_type="access",
                user_id=int(user_id_str),
                expires_at=expire_dt,
            )
            db.add(blacklisted)
            db.commit()
    except JWTError:
        pass
    return {"detail": "Logout berhasil"}


@app.get("/api/auth/me")
def get_me(user: User = Depends(require_user)):
    """Get current user info."""
    return user.to_dict()


# ── Routes: AI Chat ─────────────────────────────────────────────────


@app.post("/api/ai/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: User = Depends(require_user),
):
    """Kirim perintah ke AI assistant dengan dukungan riwayat chat dan RAG."""
    history_list = []
    if request.history:
        history_list = [{"role": h.role, "text": h.text} for h in request.history]

    result = await process_chat(
        request.message,
        chat_history=history_list,
        user_id=user.id,
        user_role=user.role,
    )
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
            (Item.title.ilike(f"%{search}%")) | (Item.description.ilike(f"%{search}%"))
        )

    items = query.limit(100).all()
    return [item.to_dict() for item in items]


@app.get("/api/items/by-code/{unique_code}")
def get_item_by_code(unique_code: str, db: Session = Depends(get_db)):
    """Get a single item by unique code."""
    item = db.query(Item).filter(Item.unique_code == unique_code.upper()).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")
    return item.to_dict()


@app.get("/api/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item by ID."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")
    return item.to_dict()


@app.post("/api/items", status_code=201)
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
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
        uploader_id=user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item.to_dict()


@app.put("/api/items/{item_id}")
def update_item(
    item_id: int,
    data: ItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    """Update an existing item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")

    if item.uploader_id != user.id and user.role != UserRole.petugas.value:
        raise HTTPException(
            status_code=403, detail="Tidak memiliki akses untuk mengubah item ini"
        )

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
    item_id: int,
    data: StatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    """Update item status (open, claimed, closed). Hanya pembuat laporan atau petugas."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")

    if item.uploader_id != user.id and user.role != UserRole.petugas.value:
        raise HTTPException(
            status_code=403, detail="Tidak memiliki akses untuk mengubah item ini"
        )

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
    user: User = Depends(require_user),
):
    """Delete an item (petugas or owner only)."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")

    if item.uploader_id != user.id and user.role != UserRole.petugas.value:
        raise HTTPException(
            status_code=403, detail="Tidak memiliki akses untuk menghapus item ini"
        )

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
        raise HTTPException(
            status_code=404, detail="Item tidak ditemukan dengan kode tersebut"
        )

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
