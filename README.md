# Ilost&Found AI

> Menemukan barang hilang secara cepat dan mudah

Aplikasi wweb ini dilengkapi AI Assistant untuk mengelola barang hilang dan barang ditemukan melalui perintah bahasa Indonesia. Sehingga pengguna dipermudah dalam menemukan barang yang hilang.

## Tech Stack

- **Frontend**: Vue.js 3 + Vite
- **Backend**: FastAPI (Python)
- **AI Engine**: LangChain + OpenAI GPT-4o-mini
- **Database**: SQLite
- **Container**: Docker + Docker Compose

## Quick Start

### Dengan Docker (Recommended)

```bash
# 1. Clone dan masuk ke directory project
cd projectpabw

# 2. Copy dan isi API key
cp .env.example .env
# Edit .env dan isi OPENAI_API_KEY

# 3. Build dan jalankan
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Development (Tanpa Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
# Set environment variable
export OPENAI_API_KEY=sk-your-key-here
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## AI Commands

### Dashboard
| Fitur | Contoh | Contoh |
|----------|--------|--------|
| Dashboard + Search | Cari data di dashboard | *"Cari barang hilang dengan kata kunci dompet hitam"*|
| Dashboard + Search (opsional) | Tampilkan ringkasan dashboard | *"Tampilkan statistik barang hilang dan temuan hari ini"*|
| Dashboard + Search | Cari data di dashboard | *"Cari barang hilang dengan kata kunci dompet hitam"*|

### GET: Barang Hilang
| Fitur | Contoh | Contoh |
|----------|--------|--------|
| Get Barang Hilang | Lihat semua barang hilang | *"Tampilkan semua barang hilang"*|
| Get Barang Hilang | Filter barang hilang | *"Tampilkan barang hilang kategori elektronik"*|

### GET: Barang Temuan
| Fitur | Contoh | Contoh |
|----------|--------|--------|
| Get Barang Temuan | Lihat semua barang temuan | *"Tampilkan semua barang temuan"*|
| Get Barang Temuan | Filter barang temuan | *"Tampilkan barang temuan kategori aksesoris"*|

### POST: Barang Hilang
| Fitur | Contoh | Contoh |
|----------|--------|--------|
| Post Barang Hilang | Tambah barang Hilang | *"Laporkan barang hilang berupa HP di parkiran"*|
| Post Barang Hilang | Tambah lokasi | *"Tambahkan lokasi terakhir kemungkinan di gedung A"*|
| Post Barang Hilang (opsional) | Tambah Foto Barang | *"Tambahkan foto barang yang ditemukan"*|
| Post Barang Hilang | Tambah Keterangan Tambahan | *"Tambahkan keterangan tambahan untuk barang ini, yaitu barang berwarna pink dan kategorinya berharga"*|

### POST: Barang Temuan
| Fitur | Contoh | Contoh |
|----------|--------|--------|
| Post Barang Temuan | Tambah barang Temuan | *"Laporkan barang temuan berupa HP di parkiran"*|
| Post Barang Temuan | Tambah lokasi | *"Tambahkan lokasi ditemukan di gedung A"*|
| Post Barang Temuan | Tambah waktu | *"Tambahkan waktu ditemukan di hari Senin 7 Februari 2026"*|
| Post Barang Temuan | Tambah Foto Barang | *"Tambahkan foto barang yang ditemukan"*|
| Post Barang Temuan | Tambah Keterangan Tambahan | *"Tambahkan keterangan tambahan untuk barang ini, yaitu barang berwarna pink dan kategorinya berharga"*|

### Petugas Panel
| Fitur | Contoh | Contoh |
|----------|--------|--------|
| Verifikasi Barang | Verifikasi laporan | *"Verifikasi laporan barang hilang ID 123"*|
| Post Barang Temuan | Tambah lokasi | *"Tambahkan lokasi ditemukan di gedung A"*|
| Post Barang Temuan | Tambah waktu | *"Tambahkan waktu ditemukan di hari Senin 7 Februari 2026"*|

## Project Structure

```
projectpabw/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── main.py          # FastAPI app + routes
│   ├── database.py      # SQLAlchemy models
│   ├── ai_agent.py      # LangChain agent + 6 tools
│   └── Dockerfile
└── frontend/
    ├── src/
    │   ├── App.vue
    │   ├── components/
    |   |   ├── Login.vue
    |   |   ├── Register.vue
    |   |   ├── AdminDashboard.vue
    │   │   ├── Dashboard.vue
    |   |   ├── ProductLostPost.vue
    |   |   ├── ProductFoundPost.vue
    │   │   ├── ProductLostList.vue
    │   │   └── ProductFoundList.vue
    │   └── services/api.js
    ├── nginx.conf
    └── Dockerfile
```
