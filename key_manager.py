"""
key_manager.py — Modul Keamanan Penyimpanan Kunci Privat

Modul ini bertanggung jawab untuk:
1. Mengenkripsi private key PEM menggunakan AES-256-GCM sebelum disimpan.
2. Mendekripsi private key PEM dari bentuk terenkripsi saat dibutuhkan.
3. Menggunakan PBKDF2-HMAC-SHA256 sebagai KDF untuk menurunkan encryption key
   dari master password pengguna.
4. Menghasilkan salt dan IV (nonce) acak setiap kali enkripsi dilakukan
   untuk mencegah serangan replay.

Format penyimpanan (binary):
  [salt 16 byte][iv 12 byte][tag 16 byte][ciphertext ...]

Anggota 3 — Keamanan & Unit Test
"""

import os
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


# Konstanta kriptografi
SALT_LENGTH = 16       # 128-bit salt (NIST recommendation)
IV_LENGTH = 12         # 96-bit nonce untuk AES-GCM (NIST SP 800-38D)
KEY_LENGTH = 32        # 256-bit key untuk AES-256
KDF_ITERATIONS = 480_000  # Iterasi PBKDF2 (OWASP 2023 recommendation)


def _derive_key(password: bytes, salt: bytes) -> bytes:
    """
    Menurunkan encryption key 256-bit dari password menggunakan PBKDF2-HMAC-SHA256.

    Mengapa PBKDF2?
    - Memperlambat brute-force attack terhadap password lemah.
    - Salt mencegah rainbow table attack.
    - 480.000 iterasi sesuai rekomendasi OWASP 2023.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    return kdf.derive(password)


def encrypt_private_key(private_key_pem: bytes, master_password: bytes) -> bytes:
    """
    Mengenkripsi private key PEM menggunakan AES-256-GCM.

    Args:
        private_key_pem: Bytes dari private key dalam format PEM.
        master_password: Password master dari pengguna (dalam bytes).

    Returns:
        Bytes berformat: salt (16) + iv (12) + tag (16) + ciphertext
        Total overhead = 44 byte di atas ukuran plaintext.

    Raises:
        ValueError: Jika private_key_pem atau master_password kosong.
    """
    if not private_key_pem:
        raise ValueError("Private key PEM tidak boleh kosong.")
    if not master_password:
        raise ValueError("Master password tidak boleh kosong.")

    # 1. Generate salt dan IV secara acak (CSPRNG)
    salt = os.urandom(SALT_LENGTH)
    iv = os.urandom(IV_LENGTH)

    # 2. Derive encryption key dari password + salt
    encryption_key = _derive_key(master_password, salt)

    # 3. Enkripsi menggunakan AES-256-GCM (authenticated encryption)
    aesgcm = AESGCM(encryption_key)
    # AES-GCM secara otomatis menghasilkan authentication tag 16 byte
    # yang ditempel di akhir ciphertext
    ciphertext_with_tag = aesgcm.encrypt(iv, private_key_pem, None)

    # 4. Gabungkan: salt + iv + ciphertext_with_tag
    return salt + iv + ciphertext_with_tag


def decrypt_private_key(encrypted_data: bytes, master_password: bytes) -> bytes:
    """
    Mendekripsi private key PEM dari bentuk terenkripsi AES-256-GCM.

    Args:
        encrypted_data: Bytes berformat salt + iv + ciphertext_with_tag.
        master_password: Password master dari pengguna (dalam bytes).

    Returns:
        Bytes dari private key dalam format PEM (plaintext).

    Raises:
        ValueError: Jika data terlalu pendek atau password salah.
        cryptography.exceptions.InvalidTag: Jika password salah
            atau data telah dimodifikasi (integritas gagal).
    """
    min_length = SALT_LENGTH + IV_LENGTH + 16  # 16 = minimum tag size
    if len(encrypted_data) < min_length:
        raise ValueError(
            f"Data terenkripsi terlalu pendek (min {min_length} byte, "
            f"diterima {len(encrypted_data)} byte)."
        )

    # 1. Pisahkan komponen dari binary blob
    salt = encrypted_data[:SALT_LENGTH]
    iv = encrypted_data[SALT_LENGTH:SALT_LENGTH + IV_LENGTH]
    ciphertext_with_tag = encrypted_data[SALT_LENGTH + IV_LENGTH:]

    # 2. Derive key yang sama dari password + salt
    encryption_key = _derive_key(master_password, salt)

    # 3. Dekripsi dan verifikasi integritas (AES-GCM authenticated decryption)
    aesgcm = AESGCM(encryption_key)
    plaintext = aesgcm.decrypt(iv, ciphertext_with_tag, None)

    return plaintext


def save_encrypted_key(private_key_pem: bytes, master_password: bytes,
                       output_path: str) -> str:
    """
    Mengenkripsi private key lalu menyimpannya ke file.

    Args:
        private_key_pem: Bytes dari private key PEM.
        master_password: Password master pengguna.
        output_path: Path file tujuan (misal: './keys/private_key.enc').

    Returns:
        Path file yang disimpan.
    """
    encrypted = encrypt_private_key(private_key_pem, master_password)

    # Pastikan direktori ada
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(encrypted)

    return output_path


def load_encrypted_key(encrypted_path: str, master_password: bytes) -> bytes:
    """
    Membaca file private key terenkripsi lalu mendekripsinya.

    Args:
        encrypted_path: Path file terenkripsi.
        master_password: Password master pengguna.

    Returns:
        Bytes private key PEM (plaintext).

    Raises:
        FileNotFoundError: Jika file tidak ditemukan.
        cryptography.exceptions.InvalidTag: Jika password salah.
    """
    with open(encrypted_path, "rb") as f:
        encrypted_data = f.read()

    return decrypt_private_key(encrypted_data, master_password)
