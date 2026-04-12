# BizLedger AI

> 💼 Pencatatan Keuangan Bisnis dengan AI Assistant

Aplikasi web pencatatan keuangan bisnis yang dilengkapi AI Assistant untuk mengelola **stok barang** dan **faktur** melalui perintah bahasa Indonesia.

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

# 2. Copy dan isi konfigurasi environment
cp .env.example .env
# Edit file .env dan isi variabel yang dibutuhkan (seperti GROQ_API_KEY)

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

| Perintah | Contoh |
|----------|--------|
| Tambah produk | *"Tambah produk Kopi Arabica harga 75000 stok 100"* |
| Lihat produk | *"Lihat semua produk"* |
| Buat faktur | *"Buatkan faktur untuk Toko Makmur: 10 Kopi Arabica"* |
| Lihat faktur | *"Lihat semua faktur"* |
| Total penjualan | *"Berapa total penjualan hari ini?"* |
| Stok menipis | *"Produk apa yang stoknya menipis?"* |

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
    │   │   ├── AiChat.vue
    │   │   ├── DashboardCards.vue
    │   │   ├── ProductList.vue
    │   │   └── InvoiceList.vue
    │   └── services/api.js
    ├── nginx.conf
    └── Dockerfile
```
