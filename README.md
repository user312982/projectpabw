# 1. Clone repository dan masuk ke directory project
git clone <URL_REPOSITORY>  # Ganti dengan URL repository yang sesuai
cd projectpabw

# 2. Copy dan isi konfigurasi environment
cp .env.example .env
# Edit file .env dan isi variabel yang dibutuhkan (seperti GROQ_API_KEY)

# 3. Build dan jalankan di background (Detached mode)
docker compose up -d --build

# 4. Berhenti dan menghapus container (jika sudah selesai)
# docker compose down

# 5. Melihat log dari container yang berjalan
# docker compose logs -f
