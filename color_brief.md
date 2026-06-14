# Brief Website Chat-First Lost & Found ITK

## 1. Ringkasan Konsep

Website ini adalah platform **Lost & Found berbasis chatbot** untuk lingkungan ITK. Fokus utama interaksi pengguna adalah melalui chatbot, bukan melalui halaman website yang kompleks.

Konsep utama:

> Pengguna mencari, melaporkan, dan mengecek status barang hilang/ditemukan melalui percakapan chatbot. UI visual hanya dipakai ketika lebih efektif daripada teks, seperti tombol pilihan cepat, card barang, upload foto, dan status klaim.

Arah desain:

- Chat-first
- Clean
- Minimal
- Friendly
- Trust-based
- Cocok untuk sistem kampus
- Menggunakan identitas warna ITK

---

## 2. Tujuan Website

Website dibuat untuk membantu civitas akademika ITK dalam:

1. Mencari barang hilang.
2. Melaporkan barang ditemukan.
3. Mencocokkan barang hilang dengan barang ditemukan.
4. Mengajukan klaim kepemilikan barang.
5. Mengecek status laporan atau klaim.
6. Membantu admin memverifikasi laporan dan klaim.

---

## 3. Prinsip Desain Utama

### 3.1 Chatbot sebagai pusat interaksi

Website tidak dibuat seperti marketplace atau katalog biasa. Chatbot menjadi elemen utama yang mengarahkan user.

Contoh pendekatan:

- User tidak langsung disuruh mengisi form panjang.
- Chatbot bertanya satu per satu.
- UI hanya muncul ketika dibutuhkan.
- Pilihan penting ditampilkan dalam bentuk tombol cepat.
- Hasil pencarian ditampilkan dalam bentuk card barang.

### 3.2 UI seminimal mungkin

UI tidak perlu terlalu banyak menu. Cukup tampilkan elemen yang penting.

Navigasi utama:

- Cari Barang
- Lapor Barang
- Cek Status

Elemen lain seperti filter, form panjang, dan tabel hanya dipakai jika benar-benar diperlukan.

### 3.3 Percakapan tetap terarah

Meskipun berbasis chatbot, percakapan harus tetap memiliki alur yang jelas. Gunakan quick reply agar user tidak bingung.

Contoh quick reply:

- Saya kehilangan barang
- Saya menemukan barang
- Lihat barang terbaru
- Cek status laporan
- Dompet
- Kunci
- HP
- Kartu identitas
- Tas
- Lainnya

---

## 4. Struktur Halaman

### 4.1 Homepage

Homepage harus sederhana dan langsung mengarahkan user ke chatbot.

Struktur rekomendasi:

```text
------------------------------------------------
Logo ITK / FindIt ITK        Cari Barang | Lapor | Status
------------------------------------------------

Temukan kembali barang hilang di lingkungan ITK
Laporkan, cari, dan klaim barang melalui chatbot.

[ Mulai Chat ]

------------------------------------------------

Chatbot Panel
Bot: Halo, saya bisa bantu kamu mencari atau melaporkan barang.

[ Saya kehilangan barang ]
[ Saya menemukan barang ]
[ Cek status laporan ]

------------------------------------------------

Barang terbaru ditemukan
[Card] [Card] [Card]

------------------------------------------------
```

Catatan:

- Chatbot harus menjadi fokus utama.
- Bagian barang terbaru hanya sebagai pendukung.
- Jangan membuat homepage terlalu ramai.

---

## 5. Layout Utama Website

Rekomendasi layout desktop:

```text
------------------------------------------------
Header: Logo + navigasi ringkas
------------------------------------------------

Kiri / Tengah:
Panel chatbot besar

Kanan / Bawah:
Area hasil berupa card barang jika dibutuhkan

------------------------------------------------
```

Rekomendasi layout mobile:

```text
------------------------------------------------
Header kecil
------------------------------------------------
Chatbot full screen
------------------------------------------------
Card barang muncul di bawah chat
------------------------------------------------
Input chat fixed di bawah
------------------------------------------------
```

---

## 6. Flow Interaksi Utama

## 6.1 Flow Cari Barang Hilang

```text
Bot:
Halo, kamu mau cari barang hilang atau melaporkan barang ditemukan?

User klik:
[Saya kehilangan barang]

Bot:
Barang apa yang kamu kehilangan?

User:
Dompet hitam

Bot:
Terakhir terlihat di mana?

Quick reply:
[Kantin] [Perpustakaan] [Parkiran] [Kelas] [Lainnya]

User klik:
Kantin

Bot:
Kapan kira-kira hilangnya?

Quick reply:
[Hari ini] [Kemarin] [Minggu ini] [Pilih tanggal]

Bot:
Saya menemukan beberapa barang yang mirip.
```

Setelah itu tampilkan card barang:

```text
[Foto Barang]
Dompet hitam
Lokasi ditemukan: Kantin lantai 1
Tanggal ditemukan: 24 Mei 2026
Status: Belum diklaim

[Lihat Detail] [Ini mungkin milik saya]
```

Chatbot lanjut mengarahkan:

```text
Bot:
Apakah salah satu barang ini terlihat cocok dengan barang milikmu?
```

---

## 6.2 Flow Lapor Barang Ditemukan

```text
Bot:
Barang apa yang kamu temukan?

User:
Kartu mahasiswa

Bot:
Di mana kamu menemukannya?

Quick reply:
[Kantin] [Perpustakaan] [Lobby] [Toilet] [Parkiran] [Lainnya]

Bot:
Kapan barang ditemukan?

Quick reply:
[Baru saja] [Hari ini] [Kemarin] [Pilih tanggal]

Bot:
Boleh unggah foto barangnya?

UI:
[Upload Foto]

Bot:
Tambahkan ciri khusus yang aman untuk ditampilkan publik.
```

Untuk barang sensitif seperti kartu identitas, chatbot harus memberi peringatan:

```text
Bot:
Untuk keamanan, detail seperti nama lengkap, NIM, dan nomor identitas tidak akan ditampilkan publik.
```

---

## 6.3 Flow Klaim Barang

```text
User klik:
[Ini mungkin milik saya]

Bot:
Untuk memastikan barang ini benar milikmu, jawab beberapa pertanyaan verifikasi.

Bot:
Sebutkan ciri khusus barang tersebut.

User:
Di dalam dompet ada kartu ATM biru dan struk belanja.

Bot:
Terima kasih. Klaim kamu akan diperiksa oleh admin.
```

Status yang ditampilkan:

```text
Status klaim: Menunggu verifikasi

[Cek Status] [Hubungi Petugas]
```

---

## 6.4 Flow Cek Status Laporan

```text
Bot:
Masukkan kode laporan atau pilih laporan terakhir kamu.

User:
ITK-LF-2026-0012

Bot:
Status laporan kamu saat ini:

Barang: Dompet hitam
Status: Menunggu verifikasi admin
Update terakhir: 24 Mei 2026

[Detail Laporan] [Hubungi Admin]
```

---

## 7. Komponen UI yang Dibutuhkan

Karena website harus minim UI, gunakan komponen berikut saja.

| Komponen | Fungsi |
|---|---|
| Chat panel | Area utama interaksi user dengan chatbot |
| Message bubble | Menampilkan pesan user dan bot |
| Quick reply button | Pilihan cepat untuk mengurangi input manual |
| Suggestion chip | Pilihan kategori, lokasi, waktu, status |
| Item card | Menampilkan hasil barang hilang/ditemukan |
| Upload photo | Mengunggah foto barang |
| Status badge | Menampilkan status laporan atau klaim |
| Mini form | Hanya untuk data yang harus terstruktur |
| Admin table | Khusus admin untuk verifikasi laporan |

---

## 8. Komponen yang Sebaiknya Dihindari

Hindari elemen yang membuat website terasa seperti marketplace atau dashboard rumit.

Jangan terlalu dominan memakai:

- Sidebar besar
- Banyak menu
- Filter kompleks di homepage
- Form panjang di awal
- Banyak tab
- Banyak warna status tanpa label teks
- Hero section terlalu besar
- Animasi berlebihan
- Ilustrasi yang terlalu ramai

---

## 9. Palet Warna ITK

Warna utama mengacu pada identitas visual ITK:

- Biru utama: RGB 11, 97, 170
- Oranye/kuning aksen: RGB 245, 183, 90

Konversi HEX:

```css
--itk-blue: #0B61AA;
--itk-orange: #F5B75A;
```

Biru digunakan sebagai warna utama karena memberi kesan:

- Terpercaya
- Stabil
- Akademik
- Teknologis
- Cocok untuk institusi kampus

Oranye/kuning digunakan sebagai aksen karena memberi kesan:

- Ramah
- Optimis
- Hangat
- Menarik perhatian untuk aksi penting

---

## 10. Skema Warna Final

Gunakan palet berikut sebagai design token.

```css
:root {
  --primary: #0B61AA;
  --primary-dark: #073B6D;
  --accent: #F5B75A;

  --background: #F7F9FC;
  --surface: #FFFFFF;
  --surface-soft: #EEF6FF;
  --warm-surface: #FFF7E8;

  --text: #1F2937;
  --muted: #6B7280;
  --border: #E5E7EB;

  --success: #16A34A;
  --warning: #F59E0B;
  --danger: #DC2626;
  --info: #6366F1;
}
```

---

## 11. Pembagian Warna UI

### 11.1 Background halaman

```css
background: #F7F9FC;
```

Gunakan abu sangat muda agar tampilan bersih dan tidak melelahkan mata.

### 11.2 Header

```css
background: #FFFFFF;
border-bottom: 1px solid #E5E7EB;
color: #1F2937;
```

Logo atau brand name dapat menggunakan biru ITK.

### 11.3 Tombol utama

Untuk aksi utama seperti:

- Mulai Chat
- Cari Barang
- Lapor Barang
- Klaim Barang

```css
background: #0B61AA;
color: #FFFFFF;
hover: #073B6D;
```

### 11.4 Tombol sekunder

Untuk aksi seperti:

- Upload Foto
- Lihat Detail
- Cek Status

```css
background: #F5B75A;
color: #1F2937;
hover: #E6A94D;
```

Catatan:

- Jangan terlalu banyak memakai warna oranye.
- Oranye cukup sebagai aksen agar tidak terlihat ramai.

### 11.5 Bubble chatbot dari bot

```css
background: #EEF6FF;
color: #1F2937;
border: 1px solid #D8EAFE;
```

### 11.6 Bubble chatbot dari user

```css
background: #0B61AA;
color: #FFFFFF;
```

### 11.7 Quick reply button

Default:

```css
background: #FFFFFF;
color: #0B61AA;
border: 1px solid #0B61AA;
```

Hover atau selected:

```css
background: #0B61AA;
color: #FFFFFF;
```

### 11.8 Card barang

```css
background: #FFFFFF;
border: 1px solid #E5E7EB;
border-radius: 16px;
box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
```

---

## 12. Warna Status

| Status | Warna | HEX | Catatan |
|---|---|---|---|
| Hilang | Biru | `#0B61AA` | Status barang yang dilaporkan hilang |
| Ditemukan | Hijau | `#16A34A` | Barang sudah ditemukan |
| Menunggu Verifikasi | Oranye | `#F59E0B` | Klaim/laporan sedang dicek admin |
| Dalam Proses Klaim | Indigo | `#6366F1` | Klaim sedang berjalan |
| Selesai | Abu gelap | `#374151` | Kasus selesai |
| Ditolak / Bermasalah | Merah | `#DC2626` | Klaim gagal atau perlu perhatian |

Penting:

- Jangan hanya mengandalkan warna.
- Selalu tampilkan label teks status.
- Contoh: `Menunggu Verifikasi`, `Ditemukan`, `Selesai`.

---

## 13. Rekomendasi Tipografi

Gunakan font sans-serif modern.

Rekomendasi:

- Inter
- Plus Jakarta Sans
- Poppins
- DM Sans

Prioritas:

- Mudah dibaca
- Tidak terlalu dekoratif
- Cocok untuk UI kampus dan teknologi

Ukuran rekomendasi:

```css
--text-xs: 12px;
--text-sm: 14px;
--text-base: 16px;
--text-lg: 18px;
--text-xl: 20px;
--text-2xl: 24px;
--text-3xl: 32px;
```

---

## 14. Gaya Visual

Gunakan gaya visual berikut:

- Rounded corner besar tapi tetap profesional
- Banyak whitespace
- Shadow halus
- Border tipis
- Icon sederhana
- Background netral
- Warna ITK sebagai identitas, bukan dekorasi berlebihan

Contoh karakter UI:

```text
Clean campus tech
Friendly assistant
Reliable public service
Minimal but helpful
```

---

## 15. Rekomendasi Struktur Data Barang

Gunakan struktur data berikut untuk item lost & found.

```ts
type LostFoundItem = {
  id: string;
  title: string;
  category: string;
  type: 'lost' | 'found';
  description: string;
  publicDescription: string;
  privateClues?: string;
  location: string;
  date: string;
  imageUrl?: string;
  status: 'lost' | 'found' | 'pending_verification' | 'claiming' | 'resolved' | 'rejected';
  reporterName?: string;
  reporterContact?: string;
  createdAt: string;
  updatedAt: string;
};
```

Catatan keamanan:

- `publicDescription` ditampilkan ke publik.
- `privateClues` hanya digunakan untuk verifikasi admin.
- Jangan tampilkan data sensitif seperti NIM lengkap, nomor identitas, nomor kartu, atau kontak pribadi di listing publik.

---

## 16. Rekomendasi Intent Chatbot

Chatbot minimal harus mendukung intent berikut:

```ts
type ChatIntent =
  | 'search_lost_item'
  | 'report_found_item'
  | 'report_lost_item'
  | 'claim_item'
  | 'check_report_status'
  | 'contact_admin'
  | 'faq';
```

---

## 17. Contoh Respons Chatbot

### Sapaan awal

```text
Halo! Saya bisa bantu kamu mencari atau melaporkan barang hilang di lingkungan ITK.

Apa yang ingin kamu lakukan?
```

Quick replies:

```text
[Saya kehilangan barang]
[Saya menemukan barang]
[Cek status laporan]
[Lihat barang terbaru]
```

### Saat hasil ditemukan

```text
Saya menemukan beberapa barang yang mirip dengan deskripsi kamu. Coba cek apakah salah satunya cocok.
```

### Saat tidak ada hasil

```text
Saya belum menemukan barang yang cocok. Kamu bisa membuat laporan kehilangan agar admin dapat membantu mencocokkan jika ada barang ditemukan nanti.
```

### Saat klaim diajukan

```text
Klaim kamu sudah dikirim. Admin akan memeriksa kecocokan data terlebih dahulu sebelum barang dapat diambil.
```

---

## 18. Fitur MVP

Fitur minimum yang harus ada:

1. Chatbot utama.
2. Quick reply untuk alur utama.
3. Form lapor barang hilang.
4. Form lapor barang ditemukan.
5. Upload foto barang.
6. Daftar card barang yang cocok.
7. Detail barang.
8. Klaim barang.
9. Cek status laporan.
10. Admin verifikasi laporan dan klaim.

---

## 19. Fitur Lanjutan

Fitur yang bisa dibuat setelah MVP:

1. Matching otomatis antara laporan hilang dan barang ditemukan.
2. Notifikasi email atau WhatsApp.
3. Login SSO kampus.
4. QR code untuk kode laporan.
5. Riwayat laporan user.
6. Statistik barang hilang/ditemukan.
7. Auto-hide data sensitif dengan AI.
8. Multi-language Indonesia/English.

---

## 20. Admin Dashboard

Admin dashboard tidak harus chat-first. Untuk admin, tabel lebih efisien.

Fitur admin:

- Melihat semua laporan.
- Memfilter berdasarkan status.
- Melihat detail barang.
- Memverifikasi klaim.
- Mengubah status barang.
- Menghubungi pelapor.
- Menandai barang selesai.

Struktur admin:

```text
Dashboard Admin

[Total Laporan] [Menunggu Verifikasi] [Dalam Klaim] [Selesai]

Tabel laporan:
- Kode laporan
- Nama barang
- Jenis: Hilang/Ditemukan
- Lokasi
- Tanggal
- Status
- Aksi
```

---

## 21. Prioritas Implementasi UI

Urutan implementasi yang disarankan:

1. Buat layout dasar homepage.
2. Buat chat panel.
3. Buat message bubble.
4. Buat quick reply button.
5. Buat flow chatbot statis.
6. Buat item card.
7. Buat form upload/lapor barang.
8. Buat status tracking.
9. Buat admin dashboard sederhana.
10. Integrasikan database dan backend.

---

## 22. Catatan untuk Codex

Bangun UI dengan arah berikut:

- Chatbot harus menjadi fokus utama halaman.
- Jangan membuat UI terlalu ramai.
- Gunakan warna biru ITK sebagai primary color.
- Gunakan oranye ITK sebagai aksen terbatas.
- Gunakan banyak putih, abu muda, dan biru muda.
- User biasa tidak perlu melihat dashboard kompleks.
- Admin boleh menggunakan tabel karena lebih efisien.
- Semua alur user sebaiknya dimulai dari chatbot.
- Gunakan card hanya untuk menampilkan barang atau status.
- Gunakan quick reply untuk pilihan yang sering muncul.
- Jangan tampilkan data sensitif di listing publik.

---

## 23. Contoh Prompt Implementasi untuk Codex

```text
Buat website Lost & Found ITK berbasis chat-first conversational UI.

Gunakan React/Next.js dan Tailwind CSS.

Fokus utama halaman adalah panel chatbot besar di tengah. UI lain dibuat minimal dan hanya muncul jika dibutuhkan.

Gunakan palet warna:
- primary: #0B61AA
- primary-dark: #073B6D
- accent: #F5B75A
- background: #F7F9FC
- surface: #FFFFFF
- bot-bubble: #EEF6FF
- text: #1F2937
- muted: #6B7280
- border: #E5E7EB

Buat komponen:
- Header sederhana
- ChatPanel
- MessageBubble
- QuickReplyButton
- ItemCard
- StatusBadge
- UploadPhotoButton
- ReportStatusCard
- AdminDashboard sederhana

Buat flow chatbot:
1. Cari barang hilang
2. Lapor barang ditemukan
3. Ajukan klaim barang
4. Cek status laporan

Desain harus clean, modern, friendly, dan cocok untuk sistem kampus ITK.
```

---

## 24. Sumber Identitas Warna

Warna identitas visual ITK yang dipakai dalam brief ini:

- Biru: RGB 11, 97, 170 / HEX #0B61AA
- Oranye/kuning: RGB 245, 183, 90 / HEX #F5B75A

Sumber: Pedoman Visual Institut Teknologi Kalimantan / Brand Guidelines ITK.