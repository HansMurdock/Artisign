# Artisign — Cryptographic Digital Asset Provenance & Authentication

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Security Standard](https://img.shields.io/badge/NIST-ECDSA%20P--256-orange.svg)](https://csrc.nist.gov/)
[![Tests](https://img.shields.io/badge/tests-23%20passed-brightgreen.svg)]()

> **Proyek Ujian Tengah Semester (UTS) Mata Kuliah Aplikasi Kriptografi**  
> **Dosen Pengampu:** Ir. Alam Rahmatulloh, S.T., M.T., MCE., IPM.  
> **Program Studi Informatika — Fakultas Teknik — Universitas Siliwangi (2026)**

---

## 👥 Tim Pengembang (Kelompok 3)

| Nama Anggota | NPM | Peran & Tanggung Jawab Utama |
| :--- | :---: | :--- |
| **Khansa Rasendriya Aji** | `247006111132` | Logika Bisnis, QR Code Manager & Stempel Dokumen PDF |
| **Muhammad Zaki Zaidan Binawan** | `247006111134` | Desain Antarmuka (Frontend UI/UX) & Integrasi Web Flask |
| **Rafa Ahza Naufal** | `247006111135` | Engine Inti Kriptografi (ECDSA & SHA-256), Keamanan Kunci & Benchmarking |

---

## 📌 Deskripsi Proyek

**Artisign** adalah platform verifikasi dan sertifikasi keaslian aset digital (*Digital Asset Provenance*) berbasis kriptografi kunci asimetris modern. Aplikasi ini dirancang khusus untuk melindungi aset industri kreatif—seperti model 3D game, karya seni generatif AI, audio, dan dokumen kontrak digital—dari pembajakan, klaim sepihak (*false attribution*), serta pemalsuan data (*tampering*).

### Fitur Kunci:
1. **Tanda Tangan Digital ECDSA P-256**: Menggunakan kurva eliptik SECP256R1 standar NIST FIPS 186-4 yang menjamin prinsip *non-repudiation* (anti-penyangkalan).
2. **Deteksi Manipulasi Bit (SHA-256)**: Perubahan 1 bit atau 1 karakter pada file secara otomatis akan menolak keabsahan dokumen (akurasi 100%).
3. **Brankas Kunci Terautentikasi (AES-256-GCM + PBKDF2)**: Kunci privat kreator disimpan terenkripsi menggunakan AES-GCM 256-bit dengan derivasi kunci master PBKDF2-HMAC-SHA256 (480.000 iterasi) sesuai standar OWASP 2023.
4. **Stempel Vektor PDF & Sertifikat Fisik A4**: Menyematkan stempel QR Code interaktif ke kuadran dokumen PDF via PyMuPDF dan menerbitkan lembar resmi *Certificate of Authenticity* ukuran A4.
5. **Validator Publik dengan Scanner Kamera**: Pindai QR code langsung melalui kamera ponsel/laptop tanpa perlu mengunduh aplikasi tambahan.
6. **Client-Side Hashing Multi-GB**: Mendukung verifikasi berkas raksasa (ukuran gigabyte) secara instan di sisi peramban web (*Web Crypto API*) tanpa menghabiskan bandwidth peladen.

---

## ⚙️ Spesifikasi Standar Kriptografi

Sesuai dengan ketentuan umum teknis:
* **Algoritma Asimetris**: ECDSA kurva SECP256R1 (NIST P-256).
* **Fungsi Hash**: SHA-256 (FIPS 180-4).
* **Enkripsi Kunci Simetris**: AES-256-GCM (NIST SP 800-38D).
* **Pembangkit Acak**: CSPRNG sistem operasi (`os.urandom` / RFC 6979 deterministik).
* **Bebas Algoritma Usang**: Sama sekali tidak menggunakan ECB mode, MD5, SHA-1, DES, atau RC4.

---

## 🚀 Panduan Instalasi

### 1. Prasyarat Sistem
* Python versi 3.10, 3.11, 3.12, atau 3.14.
* Pip (Python Package Manager).
* Git.

### 2. Kloning Repositori
```bash
git clone https://github.com/username/artisign.git
cd artisign
```

### 3. Buat dan Aktifkan Virtual Environment
* **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

---

## 🖥️ Cara Menjalankan Aplikasi

1. **Jalankan Web Server Lokal:**
   ```bash
   python app.py
   ```
2. **Buka di Peramban Web:**
   Kunjungi tautan: **`http://127.0.0.1:5000`**

---

## 📖 Contoh Penggunaan

### A. Alur Penerbitan Sertifikat (Ruang Kreator):
1. Buka menu **Ruang Kreator** (`http://127.0.0.1:5000/creator`).
2. Masukkan nama kreator (misal: *Rafa Ahza Naufal*).
3. Masukkan password pengaman kunci privat (default pengujian: `super_secret_password_123`).
4. Tarik dan letakkan (*drag & drop*) berkas aset yang ingin dilindungi (misal file PDF atau ZIP).
5. Klik tombol **"Tandatangani Dokumen & Terbitkan Sertifikat"**.
6. Sistem akan mengunduh paket bundel ZIP berisi berkas asli, stempel QR, sertifikat JSON, dan berkas tanda tangan `.sig`.

### B. Alur Verifikasi Integritas (Validator Publik):
1. Buka menu **Validator Publik** (`http://127.0.0.1:5000/validator`).
2. **Opsi 1 (Kamera):** Klik tombol **"Pindai QR via Kamera / Webcam"** lalu arahkan kamera ke stempel QR sertifikat.
3. **Opsi 2 (Unggah Berkas):** Masukkan berkas sertifikat JSON / ZIP dan berkas aset yang ingin diuji keasliannya.
4. Klik **"Jalankan Verifikasi Keaslian"**.
5. Sistem akan menampilkan status hijau jika dokumen **ASLI & SAH**, atau status merah jika dokumen **TELAH DIMODIFIKASI / PALSU**.

---

## 🧪 Pengujian Unit & Benchmarking (Testing)

Proyek ini dilengkapi dengan **23 unit test otomatis** untuk memverifikasi fungsionalitas dan ketahanan sistem terhadap serangan manipulasi:

### 1. Menjalankan Seluruh Unit Test (Pytest)
```bash
pytest -v
```
*(Hasil: 23 passed 100%)*

### 2. Menjalankan Khusus Uji Kriptografi & Keamanan
```bash
python test_security.py
```

### 3. Menjalankan Uji Performa Empiris (Benchmarking 30 Iterasi)
```bash
python performance_test.py
```
Hasil pengujian performa akan tercatat secara otomatis pada file **`security_performance_result.csv`** dan rekapitulasi Excel **`security_performance_result.xlsx`**.

### Ringkasan Rata-Rata Kinerja:
* **Waktu Penandatanganan (*Signing*)**: ~0.0018 detik (1.83 ms)
* **Waktu Verifikasi (*Verification*)**: ~0.0006 detik (0.65 ms)
* **Ukuran Tanda Tangan**: 70 – 72 byte
* **Akurasi Uji Manipulasi Data (*Tamper*)**: 100% Berhasil Ditolak

---

## 📂 Struktur Direktori Proyek

```
Artisign/
├── app.py                             # Pengontrol utama aplikasi Flask & routing web
├── crypto_core.py                     # Mesin kriptografi inti (ECDSA SECP256R1 & SHA-256)
├── key_manager.py                     # Brankas kunci privat terenkripsi (AES-256-GCM + PBKDF2)
├── file_qr_manager.py                 # Pengelola QR code, sertifikat JSON & bundel ZIP
├── pdf_manager.py                     # Stempel visual vektor PDF & Certificate of Authenticity A4
├── performance_test.py                # Skrip benchmarking performa 30 kali iterasi
├── test_security.py                   # 13 unit test keamanan & integritas kriptografi
├── test_app_integration.py            # 10 unit test integrasi endpoint web Flask
├── security_performance_result.xlsx   # Rekapitulasi data hasil uji kinerja dalam format Excel
├── requirements.txt                   # Daftar dependensi pustaka Python
├── LAPORAN_PROYEK_UTS_ARTISIGN.md     # Naskah laporan teknis lengkap proyek UTS
├── templates/                         # Berkas template antarmuka HTML
│   ├── landing.html                   # Landing page utama Artisign
│   ├── creator.html                   # Halaman khusus formulir Ruang Kreator
│   ├── validator.html                 # Halaman khusus Validator Publik & Camera Scanner
│   └── result.html                    # Halaman visualisasi status hasil verifikasi
└── keys/                              # Direktori penyimpanan kunci terproteksi .gitignore
```

---

## 🔒 Kebijakan Keamanan Kunci

Sesuai aturan keamanan kriptografi:
* Direktori `keys/` dan berkas biner kunci (`*.pem`, `*.key`, `*.enc`, `*.p12`) telah dieksekusi dalam `.gitignore` sehingga **tidak akan pernah terunggah ke repositori GitHub publik**.
* Kunci privat dienkripsi pada disk dengan mode AES-256-GCM sebelum disimpan.

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).
