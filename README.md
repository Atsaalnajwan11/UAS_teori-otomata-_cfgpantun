# Implementasi Context-Free Grammar (CFG) untuk Validasi Struktur Pantun Berbasis Web

Proyek UAS **Teori Bahasa dan Otomata** — aplikasi web berbasis **Python
Flask** yang memvalidasi struktur pantun menggunakan **Context-Free Grammar
(CFG)** dan **Recursive Descent Parser (Top-Down Parser)**, tanpa
mengandalkan regex sebagai metode validasi utama.

---

## Daftar Isi

- [Fitur](#fitur)
- [Grammar CFG](#grammar-cfg)
- [Struktur Folder](#struktur-folder)
- [Instalasi & Menjalankan Secara Lokal](#instalasi--menjalankan-secara-lokal)
- [Deployment ke Railway](#deployment-ke-railway)
- [Deployment ke VPS (Domain .my.id)](#deployment-ke-vps-domain-myid)
- [Cara Kerja Parser](#cara-kerja-parser)
- [Lisensi](#lisensi)

---

## Fitur

| Halaman | Deskripsi |
|---|---|
| **Home** | Landing page berisi penjelasan singkat proyek dan CFG. |
| **Validasi Pantun** | Form input pantun, tombol Validasi & Reset, contoh pantun, serta hasil validasi lengkap (status, jumlah baris/kata, aturan grammar, trace parsing, alasan). |
| **Grammar CFG** | Menampilkan seluruh aturan produksi CFG beserta penjelasannya. |
| **Riwayat Validasi** | Menampilkan histori validasi yang tersimpan di SQLite, dengan opsi hapus riwayat. |
| **About** | Penjelasan latar belakang, metodologi, dan teknologi proyek. |

---

## Grammar CFG

```
Pantun    -> Sampiran Isi
Sampiran  -> Baris Baris
Isi       -> Baris Baris
Baris     -> Kalimat
Kalimat   -> Kata Kalimat | Kata
```

Aturan semantik tambahan:

- Jumlah baris pantun **harus tepat 4**.
- Setiap baris memiliki **4–12 kata**.
- Baris 1–2 = **Sampiran**, Baris 3–4 = **Isi**.

Grammar didefinisikan di `grammar.py` (terpisah dari logika parser) agar
mudah dikembangkan, misalnya menambah aturan rima atau jumlah suku kata.

---

## Struktur Folder

```
project/
│
├── app.py                 # Entry point Flask, routing, & database
├── cfg_parser.py            # Recursive Descent Parser (implementasi CFG)
├── grammar.py               # Definisi aturan produksi CFG
├── requirements.txt
├── Procfile                 # Untuk deployment Railway/Heroku-style
├── railway.json              # Konfigurasi Railway (Nixpacks + Gunicorn)
├── README.md
├── database.db               # SQLite (dibuat otomatis saat app dijalankan)
├── static/
│   ├── css/style.css
│   └── js/script.js
└── templates/
    ├── base.html
    ├── index.html
    ├── validate.html
    ├── grammar.html
    ├── history.html
    └── about.html
```

---

## Instalasi & Menjalankan Secara Lokal

```bash
# 1. Buat virtual environment (opsional tapi disarankan)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependensi
pip install -r requirements.txt

# 3. Jalankan aplikasi (mode development)
python app.py
```

Buka browser ke `http://localhost:5000`.

Untuk menjalankan mirip mode produksi (menggunakan Gunicorn):

```bash
gunicorn app:app --bind 0.0.0.0:5000
```

Database SQLite (`database.db`) akan otomatis dibuat pada saat aplikasi
pertama kali dijalankan (lihat fungsi `init_db()` pada `app.py`).

---

## Deployment ke Railway

1. Push proyek ini ke repository GitHub.
2. Buat project baru di [Railway](https://railway.app) dan hubungkan ke
   repository tersebut.
3. Railway akan otomatis mendeteksi `requirements.txt` dan `Procfile`
   (builder **Nixpacks**), lalu menjalankan perintah start:
   ```
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```
4. Setelah deploy berhasil, arahkan domain `.my.id` Anda:
   - Tambahkan domain kustom pada pengaturan project di Railway.
   - Buat **CNAME record** pada penyedia domain `.my.id` yang mengarah ke
     domain Railway (`xxxx.up.railway.app`).
5. Tunggu propagasi DNS, lalu akses website melalui domain `.my.id` Anda.

---

## Deployment ke VPS (Domain .my.id)

1. **Siapkan VPS** (Ubuntu 22.04 direkomendasikan) dan install Python 3,
   pip, serta Nginx:
   ```bash
   sudo apt update && sudo apt install python3-pip python3-venv nginx -y
   ```
2. **Clone proyek** ke VPS dan install dependensi:
   ```bash
   git clone <url-repo-anda> pantun-cfg
   cd pantun-cfg
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Jalankan dengan Gunicorn** (disarankan menggunakan `systemd` agar
   otomatis restart):
   ```ini
   # /etc/systemd/system/pantun-cfg.service
   [Unit]
   Description=Gunicorn instance for CFG Pantun Validator
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/pantun-cfg
   Environment="PATH=/path/to/pantun-cfg/venv/bin"
   ExecStart=/path/to/pantun-cfg/venv/bin/gunicorn app:app --bind unix:pantun-cfg.sock

   [Install]
   WantedBy=multi-user.target
   ```
   ```bash
   sudo systemctl start pantun-cfg
   sudo systemctl enable pantun-cfg
   ```
4. **Konfigurasi Nginx** sebagai reverse proxy dan arahkan domain `.my.id`
   Anda ke IP VPS melalui **A record** pada pengaturan DNS domain.
5. (Opsional) Amankan dengan **SSL** menggunakan Let's Encrypt (`certbot`).

---

## Cara Kerja Parser

Parser (`cfg_parser.py`) mengimplementasikan **Recursive Descent Parser**
yang meniru langsung struktur grammar:

1. `parse()` — titik masuk, merepresentasikan simbol awal `Pantun`.
2. `parse_sampiran()` / `parse_isi()` — masing-masing menurunkan dua
   `Baris`.
3. `parse_baris()` — menurunkan satu `Baris` menjadi `Kalimat`, sekaligus
   memeriksa batas jumlah kata (4–12).
4. `parse_kalimat()` — fungsi **rekursif** yang meniru aturan
   `Kalimat -> Kata Kalimat | Kata`: mengambil satu kata di depan, lalu
   memanggil dirinya sendiri untuk sisa token, hingga tersisa satu kata
   (basis rekursi).

Setiap tahap mencatat langkah (`trace`) yang kemudian ditampilkan di
halaman **Validasi Pantun** sebagai bukti transparansi proses parsing —
bukan sekadar hasil `True/False` dari regex.

---

## Lisensi

Proyek ini dibuat untuk keperluan akademik (UAS Teori Bahasa dan Otomata)
dan bebas digunakan/dikembangkan lebih lanjut untuk keperluan riset,
jurnal, maupun portofolio.
