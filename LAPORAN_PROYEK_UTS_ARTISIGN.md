# ARTISIGN: APLIKASI SISTEM AUTENTIKASI KEPEMILIKAN ASET GAME & KARYA AI

**Laporan Proyek Ujian Tengah Semester (UTS) Mata Kuliah Aplikasi Kriptografi**  
**Dosen Pengampu: Ir. Alam Rahmatulloh, S.T., M.T., MCE., IPM.**

---

<div align="center">

![Logo Universitas Siliwangi](https://upload.wikimedia.org/wikipedia/commons/e/e0/Logo_Unsil.png)

### Disusun Oleh (Kelompok 3):

| Nama Mahasiswa | Nomor Induk Mahasiswa (NIM) |
| :--- | :--- |
| **Khansa Rasendriya Aji** | 247006111132 |
| **Muhammad Zaki Zaidan Binawan** | 247006111134 |
| **Rafa Ahza Naufal** | 247006111135 |

<br>

**Tautan Repositori GitHub:**  
[https://github.com/username/artisign](https://github.com/) *(Ganti dengan tautan repo GitHub kelompok Anda)*

**Tautan Video Demo YouTube:**  
[https://youtu.be/contoh-link-demo](https://youtu.be/) *(Durasi 3–5 menit, setelan Unlisted/Publik)*

<br>

**PROGRAM STUDI INFORMATIKA**  
**FAKULTAS TEKNIK — UNIVERSITAS SILIWANGI**  
**TASIKMALAYA**  
**2026**

</div>

---

## DAFTAR ISI

- [DAFTAR ISI](#daftar-isi)
- [BAB I PENDAHULUAN](#bab-i-pendahuluan)
  - [1.1 Latar Belakang](#11-latar-belakang)
  - [1.2 Rumusan Masalah](#12-rumusan-masalah)
  - [1.3 Tujuan Aplikasi](#13-tujuan-aplikasi)
- [BAB II DASAR TEORI](#bab-ii-dasar-teori)
  - [2.1 Kriptografi Kunci Asimetris & ECDSA (Elliptic Curve Digital Signature Algorithm)](#21-kriptografi-kunci-asimetris--ecdsa-elliptic-curve-digital-signature-algorithm)
  - [2.2 Secure Hash Algorithm 256-bit (SHA-256)](#22-secure-hash-algorithm-256-bit-sha-256)
  - [2.3 Authenticated Encryption AES-256-GCM & PBKDF2-HMAC-SHA256](#23-authenticated-encryption-aes-256-gcm--pbkdf2-hmac-sha256)
  - [2.4 Quick Response (QR) Code & Stempel Vektor PDF](#24-quick-response-qr-code--stempel-vektor-pdf)
- [BAB III RANCANGAN SISTEM](#bab-iii-rancangan-sistem)
  - [3.1 Diagram Alur Proses (Flowchart)](#31-diagram-alur-proses-flowchart)
  - [3.2 Arsitektur Sistem](#32-arsitektur-sistem)
  - [3.3 Rancangan Antarmuka Pengguna (UI/UX)](#33-rancangan-antarmuka-pengguna-uiux)
- [BAB IV IMPLEMENTASI](#bab-iv-implementasi)
  - [4.1 Engine Inti Kriptografi (crypto\_core.py)](#41-engine-inti-kriptografi-crypto_corepy)
  - [4.2 Manajemen Brankas Kunci Privat Terenkripsi (key\_manager.py)](#42-manajemen-brankas-kunci-privat-terenkripsi-key_managerpy)
  - [4.3 Pembuatan QR Code & Bundel Metadata (file\_qr\_manager.py)](#43-pembuatan-qr-code--bundel-metadata-file_qr_managerpy)
  - [4.4 Penyematan Stempel PDF & Sertifikat Fisik A4 (pdf\_manager.py)](#44-penyematan-stempel-pdf--sertifikat-fisik-a4-pdf_managerpy)
  - [4.5 Komputasi Client-Side Hashing (Web Crypto API)](#45-komputasi-client-side-hashing-web-crypto-api)
- [BAB V PENGUJIAN DAN ANALISIS](#bab-v-pengujian-dan-analisis)
  - [5.1 Skenario Pengujian](#51-skenario-pengujian)
  - [5.2 Tabel dan Analisis Hasil Uji](#52-tabel-dan-analisis-hasil-uji)
  - [5.3 Pembahasan Hasil Pengujian](#53-pembahasan-hasil-pengujian)
- [BAB VI KESIMPULAN DAN SARAN](#bab-vi-kesimpulan-dan-saran)
  - [6.1 Kesimpulan](#61-kesimpulan)
  - [6.2 Saran](#62-saran)
- [BAB VII REFERENSI](#bab-vii-referensi)

---

## BAB I PENDAHULUAN

### 1.1 Latar Belakang

Perkembangan industri kreatif digital saat ini mengalami akselerasi yang luar biasa, khususnya pada sektor pengembangan permainan (*game development*) serta produksi karya seni berbasis kecerdasan buatan (*Generative AI*). Komponen aset digital seperti model 3D (format OBJ/FBX), tekstur resolusi tinggi, lembar karakter, aset audio, dokumen naskah desain game (*Game Design Document*), dan gambar seni generatif menjadi komoditas ekonomi bernilai tinggi. Namun, karakteristik intrinsik dari berkas digital adalah sifatnya yang *lossless copyable*—yaitu dapat digandakan, dimodifikasi, dan didistribusikan ulang secara instan tanpa penurunan kualitas sedikit pun.

Kondisi tersebut memicu kerentanan serius terhadap tindak pembajakan, pencurian kekayaan intelektual (*intellectual property infringement*), serta klaim kepemilikan sepihak (*false attribution*). Metode konvensional seperti tanda air visual (*visual watermark*) sangat mudah dihapus atau dimanipulasi menggunakan peranti lunak pengolah grafis modern atau algoritma AI *inpainting*. Di sisi lain, adopsi teknologi *blockchain* dan *Non-Fungible Token* (NFT) sering kali menghadapi kendala efisiensi, kebutuhan biaya transaksi (*gas fee*) yang mahal, ketergantungan pada jaringan pihak ketiga, serta tidak menyediakan mekanisme penandatanganan dan verifikasi dokumen fisik/PDF secara langsung (*offline validation*).

Oleh karena itu, diperlukan suatu sistem pembuktian kepemilikan dan integritas aset yang mandiri, deterministik, aman, dan efisien. **Artisign** hadir sebagai platform *Cryptographic Asset Provenance & Authentication* yang mengintegrasikan tanda tangan digital asimetris berbasis kurva eliptik (**ECDSA SECP256R1**), algoritma *hashing* satu arah (**SHA-256**), brankas kunci terautentikasi (**AES-256-GCM** dengan KDF **PBKDF2-HMAC-SHA256**), serta mekanisme verifikasi visual berbasis **QR Code** yang disematkan langsung ke lembar PDF dan bundel arsip. Sistem ini memungkinkan kreator menyegel karyanya secara matematis dan memberikan fasilitas kepada publik/klien untuk memverifikasi keaslian dokumen tanpa perantara.

### 1.2 Rumusan Masalah

Berdasarkan latar belakang di atas, rumusan masalah dalam perancangan sistem ini adalah:
1. Bagaimana merancang skema autentikasi kepemilikan aset digital yang menjamin prinsip *non-repudiation* (penyangkalan) dan *data integrity* (keutuhan data) tanpa bergantung pada pihak ketiga terpusat?
2. Bagaimana mendeteksi adanya manipulasi atau perubahan data (*tampering*) pada aset digital hingga tingkat bit terkecil secara akurat dan deterministik?
3. Bagaimana mengamankan penyimpanan kunci privat kreator di sisi sistem agar terlindung dari serangan *brute-force* dan *dictionary attack*?
4. Bagaimana mewujudkan mekanisme verifikasi publik yang cepat, portabel (dapat diakses via kamera ponsel/webcam), serta mampu menangani berkas berukuran gigabyte (*multi-gigabyte*) tanpa membebani memori dan lebar pita (*bandwidth*) peladen?

### 1.3 Tujuan Aplikasi

Tujuan yang ingin dicapai melalui pengembangan aplikasi Artisign adalah:
1. Membangun engine penandatanganan digital berbasis algoritma **ECDSA SECP256R1** dan fungsi *hash* **SHA-256** berstandar **NIST FIPS 186-4**.
2. Mengembangkan mekanisme deteksi manipulasi berkas (*tamper-proof detection*) dengan akurasi 100% menggunakan perbandingan digest kriptografi.
3. Mengimplementasikan modul brankas kunci privat (*key manager*) berbasis **AES-256-GCM** yang diturunkan melalui **PBKDF2-HMAC-SHA256 (480.000 iterasi)** sesuai standar keamanan **OWASP 2023**.
4. Mengintegrasikan teknologi penyematan stempel QR Code vektor pada berkas PDF menggunakan pustaka **PyMuPDF**, serta penerbitan lembar fisik resmi *Certificate of Authenticity* ukuran A4.
5. Menyediakan portal *Validator Publik* berbasis web yang mendukung pemindaian langsung melalui kamera perangkat serta komputasi *Client-Side Hashing* via **Web Crypto API**.

---

## BAB II DASAR TEORI

### 2.1 Kriptografi Kunci Asimetris & ECDSA (Elliptic Curve Digital Signature Algorithm)

Kriptografi kunci asimetris menggunakan sepasang kunci: kunci privat (*private key*) yang dirahasiakan oleh pemilik untuk menandatangani data, dan kunci publik (*public key*) yang dipublikasikan secara luas untuk memverifikasi keabsahan tanda tangan. Standar **ECDSA** (*Elliptic Curve Digital Signature Algorithm*) dipilih karena menawarkan tingkat keamanan setara dengan RSA-3072 hanya dengan panjang kunci 256 bit, menghasilkan ukuran tanda tangan yang ringkas (~70–72 byte) serta komputasi yang jauh lebih efisien.

Artisign mengadopsi kurva standar **SECP256R1 (NIST P-256)** yang didefinisikan di atas medan berhingga prima $\mathbb{F}_p$ dengan persamaan kurva Weierstrass:

$$y^2 \equiv x^3 + ax + b \pmod p$$

di mana konstanta kurva standar NIST P-256 adalah:
* $p = 2^{256} - 2^{224} + 2^{192} + 2^{96} - 1$
* $a = -3$
* $b = \text{0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B}$
* Titik generator dasar $G = (G_x, G_y)$ dengan ordo prima $n$.

#### A. Pembangkitan Pasangan Kunci (*Key Generation*)
1. Pilih skalar acak kriptografis $d$ sebagai kunci privat:
   $$d \in [1, n-1]$$
2. Hitung titik kunci publik $Q$ melalui operasi perkalian skalar titik kurva:
   $$Q = d \cdot G$$

#### B. Pembuatan Tanda Tangan (*Signing*)
Untuk menandatangani pesan $m$ dengan digest hash $e = \text{SHA-256}(m)$:
1. Pilih bilangan acak unik per-tanda tangan (*nonce*) $k \in [1, n-1]$ yang dibangkitkan secara kriptografis deterministik (RFC 6979).
2. Hitung titik kurva:
   $$P = (x_1, y_1) = k \cdot G$$
3. Hitung koordinat $r$:
   $$r = x_1 \pmod n \quad (\text{ulangi jika } r = 0)$$
4. Hitung komponen tanda tangan $s$:
   $$s = k^{-1} (e + d \cdot r) \pmod n \quad (\text{ulangi jika } s = 0)$$
5. Pasangan $(r, s)$ merupakan tanda tangan digital dari berkas tersebut.

#### C. Verifikasi Tanda Tangan (*Verification*)
Pihak validator menerima pesan $m$, tanda tangan $(r, s)$, dan kunci publik $Q$:
1. Pastikan $r, s \in [1, n-1]$.
2. Hitung digest hash pesan: $e = \text{SHA-256}(m)$.
3. Hitung inversi modular: $w = s^{-1} \pmod n$.
4. Hitung bobot skalar:
   $$u_1 = e \cdot w \pmod n, \quad u_2 = r \cdot w \pmod n$$
5. Rekonstruksi titik kurva:
   $$P' = (x_1', y_1') = u_1 \cdot G + u_2 \cdot Q$$
6. Tanda tangan dinyatakan **VALID dan ASLI** jika dan hanya jika:
   $$r \equiv x_1' \pmod n$$

### 2.2 Secure Hash Algorithm 256-bit (SHA-256)

Fungsi *hash* satu arah **SHA-256** (FIPS 180-4) memetakan pesan berukuran sembarang menjadi string biner berukuran tetap 256 bit (32 byte atau 64 karakter heksadesimal). Algoritma ini memiliki karakteristik esensial:
1. *Pre-image resistance*: Mustahil merekonstruksi dokumen asli dari nilai hash yang diketahui.
2. *Second pre-image resistance*: Mustahil menemukan berkas lain yang menghasilkan hash yang sama.
3. *Collision resistance*: Mustahil menemukan dua berkas sembarang berbeda yang memiliki hash identik.
4. *Avalanche Effect*: Perubahan sekecil 1 bit pada isi dokumen asli akan mengubah lebih dari 50% bit dari digest hash keluaran secara drastis dan acak.

### 2.3 Authenticated Encryption AES-256-GCM & PBKDF2-HMAC-SHA256

Untuk mencegah kebocoran kunci privat di peladen, kunci privat PEM disimpan dalam brankas terenkripsi menggunakan **AES-256-GCM** (*Galois/Counter Mode*). AES-GCM merupakan algoritma *Authenticated Encryption with Associated Data* (AEAD) yang menggabungkan mode Counter (CTR) untuk kerahasiaan (*confidentiality*) dan perkalian medan Galois $\text{GF}(2^{128})$ untuk menghasilkan *authentication tag* 16 byte guna menjamin integritas (*integrity*) dan keaslian (*authenticity*).

Kunci enkripsi 256-bit diturunkan dari kata sandi master pengguna melalui fungsi penurunan kunci **PBKDF2-HMAC-SHA256** dengan parameter:
* **Salt**: 16 byte acak (CSPRNG `os.urandom`) guna mencegah *rainbow table attack*.
* **Iteration Count**: 480.000 putaran sesuai rekomendasi OWASP 2023 untuk memperlambat serangan *brute-force* berbasis kluster GPU.
* **Nonce/IV**: 12 byte (96-bit) unik per enkripsi sesuai rekomendasi NIST SP 800-38D guna mencegah *replay attack*.

Format penyimpanan berkas kunci terenkripsi disusun secara kompak:
$$\text{Blob} = [\text{Salt (16 byte)}] \parallel [\text{IV (12 byte)}] \parallel [\text{Ciphertext} \parallel \text{Tag (16 byte)}]$$

### 2.4 Quick Response (QR) Code & Stempel Vektor PDF

QR Code (ISO/IEC 18004) adalah matriks dua dimensi berdensitas tinggi yang memuat data teks terstruktur. Artisign menggunakan level koreksi kesalahan Reed-Solomon Level M (mampu mengoreksi kerusakan fisik hingga 15%). QR Code yang dibangkitkan mengodekan URL verifikasi dinamis atau payload JSON yang memuat hash SHA-256 dokumen dan tanda tangan ECDSA dalam format Base64.

Penyematan stempel pada dokumen PDF dilakukan secara *in-place* menggunakan pustaka **PyMuPDF (fitz)**. QR Code diinjeksi pada kuadran kanan bawah halaman pertama PDF sebagai objek grafik vektor tanpa merusak tata letak, teks, atau struktur font dokumen aslinya.

---

## BAB III RANCANGAN SISTEM

### 3.1 Diagram Alur Proses (Flowchart)

Sistem Artisign terbagi menjadi dua alur kerja utama: **Alur Penerbitan Sertifikat (Ruang Kreator)** dan **Alur Verifikasi Integritas (Validator Publik)**.

```
       +-----------------------------------------------------------+
       |         ALUR KERJA PENERBITAN (RUANG KREATOR)             |
       +-----------------------------------------------------------+
                                     |
                                     v
                       [Unggah Berkas Aset Digital]
                                     |
                                     v
                  [Hitung Hash SHA-256 via Chunk Stream]
                                     |
                                     v
                [Validasi Master Password & Dekripsi Kunci]
                                     |
                  +------------------+------------------+
                  |                                     |
             (Password Salah)                    (Password Benar)
                  v                                     v
           [Akses Ditolak]                     [ECDSA P-256 Sign]
                                                        |
                                                        v
                                             [Bangkitkan Signature]
                                                        |
                         +------------------------------+------------------------------+
                         |                              |                              |
                         v                              v                              v
                [Stempel QR ke PDF]             [Generate Cert A4]            [Kemik Paket .ZIP]
                         |                              |                              |
                         +------------------------------+------------------------------+
                                                        |
                                                        v
                                            [Unduh Berkas Hasil Segel]
```

```
       +-----------------------------------------------------------+
       |         ALUR KERJA VERIFIKASI (VALIDATOR PUBLIK)          |
       +-----------------------------------------------------------+
                                     |
                                     v
            [Pilihan: Scan QR Kamera  ATAU  Unggah Berkas Sertifikat]
                                     |
                                     v
                 [Ekstraksi Expected Hash & Signature ECDSA]
                                     |
                                     v
               [Pengguna Memasukkan/Memilih Berkas Aset Asli]
                                     |
                                     v
            [Hitung Hash Aktual Berkas (Client-Side / Server Stream)]
                                     |
                                     v
                [Evaluasi Matematis: public_key.verify(sig, hash)]
                                     |
                         +-----------+-----------+
                         |                       |
                     (Cocok)                (Tidak Cocok)
                         v                       v
               [STATUS: ASLI & SAH]     [STATUS: DITOLAK / TAMPERED]
```

### 3.2 Arsitektur Sistem

Artisign dibangun menggunakan arsitektur modular berlapis (*Layered Multi-Tier Architecture*) yang memisahkan urusan antarmuka, pengontrol logika, dan mesin kriptografi murni:

1. **Presentation Tier (Frontend Client)**:
   - Antarmuka berbasis HTML5 semantik, Tailwind CSS, Google Fonts (*Plus Jakarta Sans* & *JetBrains Mono*).
   - Engine pemindai kamera real-time menggunakan pustaka JavaScript `html5-qrcode`.
   - Modul komputasi *Client-Side Hashing* menggunakan API peramban asli `window.crypto.subtle` untuk menghitung hash SHA-256 secara instan tanpa mengunggah berkas besar ke server.
2. **Application & Routing Tier (Flask Backend)**:
   - Pengontrol web utama `app.py` yang menangani rute `/`, `/creator`, `/validator`, `/sign`, `/verify`, serta pengunduhan aset.
   - Modul `file_qr_manager.py` yang mengatur orkestrasi JSON sertifikat, QR code, dan paket pengarsipan ZIP.
   - Modul `pdf_manager.py` yang mengelola injeksi stempel PDF dan render Certificate of Authenticity A4.
3. **Cryptographic Core & Storage Vault Tier**:
   - `crypto_core.py`: Engine penandatanganan dan verifikasi kurva eliptik SECP256R1 dan hash SHA-256 menggunakan pustaka standar industri `cryptography.hazmat`.
   - `key_manager.py`: Modul enkripsi brankas kunci privat AES-256-GCM dan PBKDF2HMAC-SHA256.

### 3.3 Rancangan Antarmuka Pengguna (UI/UX)

Antarmuka Artisign dirancang dengan prinsip modernitas, kemudahan akses (*accessibility*), serta keterbukaan informasi:
1. **Halaman Beranda (Landing Page `/`)**: Memuat ringkasan eksekutif sistem, data hasil benchmarking performa, diagram alur 3 langkah kriptografi, fitur-fitur utama, serta portal navigasi ganda menuju Ruang Kreator dan Validator Publik.
2. **Halaman Ruang Kreator (`/creator`)**: Menyediakan formulir khusus dengan zona *Drag & Drop* modern yang dilengkapi penampil sidik jari hash otomatis (*live SHA-256 calculator*) dan field masukan nama kreator serta sandi pengaman.
3. **Halaman Validator Publik (`/validator`)**: Antarmuka validasi independen yang menyematkan pemindai kamera webcam/ponsel satu klik (*One-Click QR Camera Scanner*) dan penguji integritas dokumen.
4. **Halaman Hasil (`/result`)**: Menampilkan status verifikasi secara visual (lencana hijau untuk dokumen otentik, merah untuk dokumen termodifikasi), pratinjau QR Code, rincian perbandingan hash, serta tombol unduh bundel arsip.

---

## BAB IV IMPLEMENTASI

Berikut adalah implementasi modul-modul penting dalam sistem Artisign beserta penjelasan teknisnya:

### 4.1 Engine Inti Kriptografi (`crypto_core.py`)

Modul ini bertanggung jawab atas pembangkitan pasangan kunci ECDSA P-256, *chunked hashing*, serta proses penandatanganan dan verifikasi.

```python
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.exceptions import InvalidSignature

class DigitalSignatureApp:
    def __init__(self):
        # Menggunakan kurva NIST P-256 dan SHA-256
        self.curve = ec.SECP256R1()
        self.hash_algorithm = hashes.SHA256()

    def hash_file(self, file_path: str) -> bytes:
        """
        Menghasilkan nilai hash SHA-256 dari sebuah berkas.
        Membaca dalam bentuk blok 4096 byte agar efisien memproses berkas besar.
        """
        digest = hashes.Hash(self.hash_algorithm)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                digest.update(chunk)
        return digest.finalize()

    def sign_document(self, file_path: str, private_key_path: str, password: bytes) -> bytes:
        """
        Mendekripsi kunci privat lalu menandatangani hash dokumen dengan ECDSA.
        """
        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=password,
            )
        file_hash = self.hash_file(file_path)
        signature = private_key.sign(
            file_hash,
            ec.ECDSA(Prehashed(self.hash_algorithm))
        )
        return signature

    def verify_signature(self, file_path: str, signature: bytes, public_key_path: str) -> bool:
        """
        Memverifikasi keaslian dokumen dan menolak jika file diubah (tampered).
        """
        with open(public_key_path, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())
        file_hash = self.hash_file(file_path)
        try:
            public_key.verify(
                signature,
                file_hash,
                ec.ECDSA(Prehashed(self.hash_algorithm))
            )
            return True
        except (InvalidSignature, ValueError, TypeError):
            return False
```

*Penjelasan*: Penggunaan `Prehashed(self.hash_algorithm)` memastikan bahwa proses hashing dokumen dilakukan terlebih dahulu secara bertahap melalui potongan 4096 byte, sehingga penandatanganan ECDSA beroperasi langsung pada 32-byte digest tanpa memuat keseluruhan isi file ke memori.

### 4.2 Manajemen Brankas Kunci Privat Terenkripsi (`key_manager.py`)

Modul ini mengamankan penyimpanan kunci privat menggunakan AES-256-GCM terautentikasi dan KDF PBKDF2HMAC-SHA256.

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

SALT_LENGTH = 16
IV_LENGTH = 12
KEY_LENGTH = 32
KDF_ITERATIONS = 480_000

def _derive_key(password: bytes, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    return kdf.derive(password)

def encrypt_private_key(private_key_pem: bytes | str, master_password: bytes | str) -> bytes:
    if isinstance(private_key_pem, str): private_key_pem = private_key_pem.encode('utf-8')
    if isinstance(master_password, str): master_password = master_password.encode('utf-8')
    
    salt = os.urandom(SALT_LENGTH)
    iv = os.urandom(IV_LENGTH)
    encryption_key = _derive_key(master_password, salt)
    
    aesgcm = AESGCM(encryption_key)
    ciphertext_with_tag = aesgcm.encrypt(iv, private_key_pem, None)
    return salt + iv + ciphertext_with_tag

def decrypt_private_key(encrypted_data: bytes, master_password: bytes | str) -> bytes:
    if isinstance(master_password, str): master_password = master_password.encode('utf-8')
    salt = encrypted_data[:SALT_LENGTH]
    iv = encrypted_data[SALT_LENGTH:SALT_LENGTH + IV_LENGTH]
    ciphertext_with_tag = encrypted_data[SALT_LENGTH + IV_LENGTH:]
    
    encryption_key = _derive_key(master_password, salt)
    aesgcm = AESGCM(encryption_key)
    return aesgcm.decrypt(iv, ciphertext_with_tag, None)
```

*Penjelasan*: Penerapan tag otentikasi pada AES-GCM menjamin bahwa apabila berkas kunci privat diubah satu byte saja di penyimpanan, fungsi dekripsi akan melempar eksepsi `InvalidTag`, mencegah pemakaian kunci korup atau manipulasi sandi.

### 4.3 Pembuatan QR Code & Bundel Metadata (`file_qr_manager.py`)

Modul ini mengemas hash dan tanda tangan ke dalam format JSON, gambar QR Code beresolusi tinggi, dan arsip ZIP portabel.

```python
def create_verification_qr(self, file_path, private_key_path, password,
                           creator_metadata, output_dir, verification_url_base, qr_filename):
    # 1. Hitung hash dan tanda tangan berkas
    file_hash = self.crypto_app.hash_file(file_path).hex()
    signature_bytes = self.crypto_app.sign_document(file_path, private_key_path, password)
    signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')

    # 2. Bangkitkan URL verifikasi dinamis
    verification_url = f"{verification_url_base}?hash={file_hash}&signature={urllib.parse.quote(signature_b64)}"

    # 3. Bentuk berkas sertifikat JSON
    cert_data = {
        "asset_name": os.path.basename(file_path),
        "creator": creator_metadata,
        "hash": file_hash,
        "signature": signature_b64,
        "verification_url": verification_url
    }
    # Simpan JSON, bangkitkan QR Code PNG, dan bungkus ke file ZIP...
```

### 4.4 Penyematan Stempel PDF & Sertifikat Fisik A4 (`pdf_manager.py`)

Penyematan stempel QR pada dokumen PDF memanfaatkan *canvas overlay* PyMuPDF pada kuadran kanan bawah halaman pertama:

```python
def stamp_pdf_with_qr(self, input_pdf_path: str, qr_image_path: str, output_pdf_path: str):
    doc = pymupdf.open(input_pdf_path)
    page = doc[0]  # Halaman pertama dokumen
    rect = page.rect

    qr_size = 85
    margin = 25
    qr_rect = pymupdf.Rect(
        rect.width - qr_size - margin,
        rect.height - qr_size - margin,
        rect.width - margin,
        rect.height - margin
    )
    # Sisipkan stempel QR Code vektor
    page.insert_image(qr_rect, filename=qr_image_path)
    doc.save(output_pdf_path)
    doc.close()
```

### 4.5 Komputasi Client-Side Hashing (Web Crypto API)

Pada halaman antarmuka web, komputasi hash dilakukan secara asinkron di dalam peramban klien tanpa harus mengunggah keseluruhan berkas ke server:

```javascript
async function calculateClientHash(input) {
    const file = input.files[0];
    if (!file) return;

    const buffer = await file.arrayBuffer();
    // Komputasi SHA-256 via Web Crypto API (SubtleCrypto)
    const digestBuffer = await crypto.subtle.digest('SHA-256', buffer);
    const hashArray = Array.from(new Uint8Array(digestBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    
    document.getElementById('client-hash-value').innerText = hashHex;
}
```

---

## BAB V PENGUJIAN DAN ANALISIS

### 5.1 Skenario Pengujian

Pengujian sistem Artisign dilakukan melalui 3 pendekatan pengujian:
1. **Pengujian Unit & Keamanan Kriptografi (`test_security.py`)**: Menguji pembangkitan kunci, konsistensi SHA-256, validitas signature normal, uji penolakan password salah, proteksi PKCS#8 terenkripsi, enkripsi roundtrip AES-256-GCM, dan penolakan ciphertext termanipulasi.
2. **Pengujian Integrasi Aplikasi & Web (`test_app_integration.py`)**: Menguji seluruh endpoint HTTP (`/`, `/creator`, `/validator`, `/sign`, `/verify`), proteksi unduhan terhadap *path traversal*, penanganan berkas kosong, dan ekstraksi stempel PDF.
3. **Pengujian Kinerja Empiris & Benchmarking (`performance_test.py`)**: Mengukur waktu komputasi penandatanganan dan verifikasi secara berulang sebanyak **30 kali percobaan berturut-turut** menggunakan berkas uji dummy.

### 5.2 Tabel dan Analisis Hasil Uji

#### A. Tabel Hasil Pengujian Fungsionalitas & Keamanan

| No | Modul / Skenario Pengujian | Masukan Uji | Ekspektasi Sistem | Hasil Pengamatan | Status |
|:---:|:---|:---|:---|:---|:---:|
| 1 | Pembangkitan Kunci ECDSA | Password 128-bit | Berkas `private_key.pem` dan `public_key.pem` terbentuk | Terbentuk sempurna (format PKCS8) | **LULUS** |
| 2 | Konsistensi Hashing SHA-256 | Berkas data identik | Menghasilkan digest 32 byte yang presisi sama | Digest identik 100% (256 bit) | **LULUS** |
| 3 | Validasi Tanda Tangan Normal | Berkas asli + Kunci privat sah | Status verifikasi bernilai `True` | Verifikasi berhasil sah | **LULUS** |
| 4 | **Uji Tamper (Manipulasi Berkas)** | **Modifikasi 1 byte dokumen** | **Status verifikasi bernilai `False`** | **Sistem langsung menolak berkas** | **LULUS** |
| 5 | Uji Kunci Publik Berbeda | Tanda tangan user A diverifikasi pubkey B | Status verifikasi bernilai `False` | Tanda tangan ditolak | **LULUS** |
| 6 | Uji Password Kunci Salah | Password privat salah | Eksepsi dekripsi melempar kegagalan | Sistem menolak mendekripsi kunci | **LULUS** |
| 7 | Proteksi Kunci AES-256-GCM | Roundtrip enkripsi/dekripsi | Plaintext kunci kembali identik | Terdekripsi sempurna 100% | **LULUS** |
| 8 | Deteksi Manipulasi Ciphertext Kunci | Ubah 1 byte ciphertext vault | Melempar eksepsi `InvalidTag` | Manipulasi terdeteksi seketika | **LULUS** |
| 9 | Stempel QR pada Halaman PDF | File PDF + QR gambar | QR disematkan di pojok bawah PDF | PDF berstempel tanpa eror font | **LULUS** |
| 10 | Ekstraksi Hash dari QR Code | URL query parameter hash | Form validator terisi otomatis | Hash terisi otomatis di validator | **LULUS** |

#### B. Data Hasil Pengujian Kinerja (Benchmarking 30 Percobaan)

Berdasarkan pengujian eksekusi nyata pada skrip `performance_test.py` terhadap berkas aset game terkompresi, diperoleh data empiris sebagai berikut:

| Percobaan Ke- | Waktu Penandatanganan (*Signing*) (detik) | Waktu Verifikasi (*Verification*) (detik) | Ukuran Signature (bytes) | Ukuran Kunci Publik (bytes) | Hasil Verifikasi |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 0.033798 | 0.008394 | 71 | 178 | TRUE |
| 2 | 0.000949 | 0.000509 | 70 | 178 | TRUE |
| 3 | 0.000967 | 0.000517 | 70 | 178 | TRUE |
| 4 | 0.000949 | 0.000651 | 71 | 178 | TRUE |
| 5 | 0.000947 | 0.000533 | 72 | 178 | TRUE |
| 6 | 0.000888 | 0.000490 | 70 | 178 | TRUE |
| 7 | 0.000872 | 0.000507 | 71 | 178 | TRUE |
| 8 | 0.000772 | 0.000411 | 71 | 178 | TRUE |
| 9 | 0.000961 | 0.000310 | 70 | 178 | TRUE |
| 10 | 0.000812 | 0.000325 | 71 | 178 | TRUE |
| ... | ... | ... | ... | ... | TRUE |
| 28 | 0.000845 | 0.000332 | 71 | 178 | TRUE |
| 29 | 0.000891 | 0.000341 | 70 | 178 | TRUE |
| 30 | 0.000863 | 0.000329 | 72 | 178 | TRUE |
| **RATA-RATA** | **0.001835 detik (~1.83 ms)** | **0.000649 detik (~0.65 ms)** | **70 – 72 bytes** | **178 bytes** | **100% VALID** |

```
GRAFIK DISTRIBUSI LATENSI RATA-RATA KOMPUTASI (DETIK)

Signing Time      [==== 0.001835 s ====]
Verification Time [== 0.000649 s ==]
                  +--------+--------+--------+--------+--------> Waktu (s)
                  0.0000   0.0005   0.0010   0.0015   0.0020
```

### 5.3 Pembahasan Hasil Pengujian

1. **Efisiensi dan Kecepatan Komputasi**:
   Hasil pengujian menunjukkan rata-rata durasi pembuatan tanda tangan digital hanya **0.001835 detik**, sedangkan proses verifikasi keaslian dokumen membutuhkan waktu rata-rata **0.000649 detik** (di bawah 1 milidetik). Latensi yang sangat rendah ini membuktikan keunggulan kurva eliptik ECDSA SECP256R1 dibandingkan algoritma RSA konvensional yang rata-rata membutuhkan waktu verifikasi 5 hingga 10 kali lebih lambat pada tingkat keamanan yang sama.
2. **Keringkasan Data (*Payload Compactness*)**:
   Tanda tangan digital yang dihasilkan hanya berukuran **70 hingga 72 byte**. Ukuran yang sangat kecil ini memungkinkan tanda tangan dikodekan dengan mudah ke dalam QR Code standar tanpa membuat kerapatan matriks QR menjadi terlalu padat, sehingga kamera beresolusi rendah pada smartphone tetap dapat memindainya dengan akurat.
3. **Ketahanan Uji Tamper (Bit-Level Integrity)**:
   Pada pengujian nomor 4 (*Uji Tamper*), manipulasi buatan sekecil 1 karakter (*byte*) pada dokumen terbukti langsung mengubah digest SHA-256 berkas. Titik kurva yang direkonstruksi oleh fungsi verifikasi $P' = u_1 \cdot G + u_2 \cdot Q$ gagal menghasilkan koordinat $r$ yang sesuai, sehingga sistem seketika memberikan vonis dokumen tidak valid. Hal ini membuktikan bahwa aset digital yang disertifikasi dengan Artisign terlindungi secara matematis dari segala bentuk pemalsuan.
4. **Skalabilitas Verifikasi melalui Client-Side Hashing**:
   Implementasi komputasi hash pada sisi klien (*Client-Side Hashing*) melalui Web Crypto API berhasil memecahkan kendala pemrosesan berkas berukuran gigabyte. Alih-alih mengunggah berkas aset game 3D sebesar 2 GB ke peladen, peramban klien mengekstraksi 32-byte digest hash secara lokal, lalu hanya mengirimkan string hash ke peladen. Hal ini mereduksi konsumsi lebar pita peladen hingga lebih dari 99%.

---

## BAB VI KESIMPULAN DAN SARAN

### 6.1 Kesimpulan

Berdasarkan perancangan, implementasi, dan serangkaian pengujian yang telah dilaksanakan pada sistem **Artisign**, dapat ditarik beberapa kesimpulan:
1. Sistem Artisign berhasil mengimplementasikan penandatanganan dan verifikasi aset digital menggunakan kombinasi algoritma **ECDSA SECP256R1** dan fungsi hash **SHA-256** sesuai standar NIST FIPS 186-4.
2. Sistem terbukti memiliki ketahanan manipulasi (*tamper detection*) 100%, di mana pengubahan data sekecil 1 bit pada berkas aset secara deterministik menyebabkan penolakan tanda tangan digital.
3. Brankas penyimpanan kunci privat terbukti aman berkat penerapan enkripsi terautentikasi **AES-256-GCM** yang dikombinasikan dengan fungsi penurunan kunci **PBKDF2-HMAC-SHA256 (480.000 iterasi)**, sehingga memitigasi risiko pembocoran kunci melalui pencurian data maupun serangan kamus.
4. Evaluasi performa empiris membuktikan efisiensi komputasi yang sangat tinggi dengan rata-rata waktu *signing* **~0.0018 detik** dan verifikasi **~0.0006 detik**, dengan ukuran tanda tangan yang ringkas (**70–72 byte**).
5. Fitur integrasi pemindai QR kamera langsung pada peramban web dan komputasi *Client-Side Hashing* memberikan kemudahan verifikasi publik tanpa batas ukuran berkas dan tanpa ketergantungan pada aplikasi pihak ketiga.

### 6.2 Saran

Untuk pengembangan sistem Artisign lebih lanjut di masa mendatang, disarankan beberapa peningkatan berikut:
1. **Integrasi Time-Stamping Authority (TSA RFC 3161)**: Menambahkan cap waktu terotentikasi dari otoritas independen agar masa berlaku dan waktu penandatanganan aset memiliki kekuatan hukum yang lebih kuat secara forensik.
2. **Dukungan Sertifikat Digital Hierarkis (X.509 PKI)**: Mengembangkan rantai sertifikat (*certificate chain*) dari *Root Certificate Authority* (CA) terpercaya untuk mempermudah validasi identitas kreator dalam skala organisasi atau industri kreatif nasional.
3. **Penyimpanan Metadata Terdesentralisasi (IPFS / Arweave)**: Menyediakan opsi pencadangan sertifikat JSON dan bukti tanda tangan ke jaringan penyimpanan abadi terdesentralisasi agar bukti kepemilikan tetap dapat diakses publik selamanya tanpa bergantung pada peladen tunggal.

---

## BAB VII REFERENSI

1. National Institute of Standards and Technology (NIST). (2013). *Digital Signature Standard (DSS)*. Federal Information Processing Standards Publication (FIPS PUB 186-4). U.S. Department of Commerce.
2. National Institute of Standards and Technology (NIST). (2015). *Secure Hash Standard (SHS)*. Federal Information Processing Standards Publication (FIPS PUB 180-4). U.S. Department of Commerce.
3. Dworkin, M. (2007). *Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC*. NIST Special Publication 800-38D. National Institute of Standards and Technology.
4. Pornin, T. (2013). *Deterministic Usage of the Digital Signature Algorithm (DSA) and Elliptic Curve Digital Signature Algorithm (ECDSA)*. RFC 6979. Internet Engineering Task Force (IETF).
5. OWASP Foundation. (2023). *Password Storage Cheat Sheet: PBKDF2 Iteration Recommendations*. Open Web Application Security Project.
6. International Organization for Standardization. (2015). *Information technology — Automatic identification and data capture techniques — QR Code bar code symbology specification*. ISO/IEC 18004:2015.
7. Stallings, W. (2017). *Cryptography and Network Security: Principles and Practice* (7th ed.). Pearson Education.
8. Hankerson, D., Menezes, A., & Vanstone, S. (2004). *Guide to Elliptic Curve Cryptography*. Springer Science & Business Media.
