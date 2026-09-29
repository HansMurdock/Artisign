import os
import tempfile
import pytest
from cryptography.exceptions import InvalidTag

from crypto_core import DigitalSignatureApp
import key_manager


crypto = DigitalSignatureApp()

PASSWORD = b"test_password_123"


def create_dummy_file(content: bytes, folder: str = None) -> str:
    """
    Membuat file dummy untuk pengujian.
    Jika folder diberikan, file dibuat di dalam folder tersebut agar
    otomatis dibersihkan saat TemporaryDirectory selesai.
    """
    if folder:
        path = os.path.join(folder, f"dummy_{os.urandom(4).hex()}.bin")
        with open(path, "wb") as f:
            f.write(content)
        return path

    file = tempfile.NamedTemporaryFile(delete=False)
    file.write(content)
    file.close()
    return file.name


# =====================================================================
# 1. Test Pembangkitan Kunci (Key Generation)
# =====================================================================
def test_key_generation():
    with tempfile.TemporaryDirectory() as folder:
        crypto.generate_keys(PASSWORD, folder)

        assert os.path.exists(os.path.join(folder, "private_key.pem"))
        assert os.path.exists(os.path.join(folder, "public_key.pem"))


# =====================================================================
# 2. Test Hashing SHA-256 (Konsistensi & Ukuran 256-bit)
# =====================================================================
def test_hash_sha256():
    with tempfile.TemporaryDirectory() as folder:
        file = create_dummy_file(b"Artisign Asset", folder)

        result1 = crypto.hash_file(file)
        result2 = crypto.hash_file(file)

        assert len(result1) == 32
        assert result1 == result2


# =====================================================================
# 3. Test Tanda Tangan & Verifikasi Normal
# =====================================================================
def test_valid_signature():
    with tempfile.TemporaryDirectory() as folder:
        crypto.generate_keys(PASSWORD, folder)
        file = create_dummy_file(b"Original Asset", folder)

        priv_key = os.path.join(folder, "private_key.pem")
        pub_key = os.path.join(folder, "public_key.pem")

        signature = crypto.sign_document(file, priv_key, PASSWORD)
        result = crypto.verify_signature(file, signature, pub_key)

        assert result is True


# =====================================================================
# 4. Test Deteksi Manipulasi / Uji Tamper
# =====================================================================
def test_document_tampered():
    with tempfile.TemporaryDirectory() as folder:
        crypto.generate_keys(PASSWORD, folder)
        file = create_dummy_file(b"Original", folder)

        priv_key = os.path.join(folder, "private_key.pem")
        pub_key = os.path.join(folder, "public_key.pem")

        signature = crypto.sign_document(file, priv_key, PASSWORD)

        # Ubah isi file secara ilegal
        with open(file, "wb") as f:
            f.write(b"Modified")

        result = crypto.verify_signature(file, signature, pub_key)
        assert result is False


# =====================================================================
# 5. Test Penolakan Kunci Publik yang Salah (Wrong Public Key)
# =====================================================================
def test_wrong_public_key():
    with tempfile.TemporaryDirectory() as folder1:
        with tempfile.TemporaryDirectory() as folder2:
            crypto.generate_keys(PASSWORD, folder1)
            crypto.generate_keys(PASSWORD, folder2)

            file = create_dummy_file(b"Asset", folder1)

            priv_key1 = os.path.join(folder1, "private_key.pem")
            pub_key2 = os.path.join(folder2, "public_key.pem")

            signature = crypto.sign_document(file, priv_key1, PASSWORD)
            result = crypto.verify_signature(file, signature, pub_key2)

            assert result is False


# =====================================================================
# 6. Test Penolakan Password Kunci Privat yang Salah
# =====================================================================
def test_wrong_private_key_password():
    with tempfile.TemporaryDirectory() as folder:
        crypto.generate_keys(PASSWORD, folder)
        file = create_dummy_file(b"Secret Asset", folder)
        priv_key = os.path.join(folder, "private_key.pem")

        with pytest.raises(Exception):
            crypto.sign_document(file, priv_key, b"wrong_password")


# =====================================================================
# 7. Test Enkripsi Kunci Privat (Harus Terproteksi PKCS8)
# =====================================================================
def test_private_key_encrypted():
    with tempfile.TemporaryDirectory() as folder:
        crypto.generate_keys(PASSWORD, folder)

        with open(os.path.join(folder, "private_key.pem"), "rb") as f:
            key_content = f.read()

        assert b"ENCRYPTED" in key_content


# =====================================================================
# 8. Test Perbedaan Signature Jika Dokumen Berbeda
# =====================================================================
def test_signature_changes_when_file_modified():
    with tempfile.TemporaryDirectory() as folder:
        crypto.generate_keys(PASSWORD, folder)
        priv_key = os.path.join(folder, "private_key.pem")

        file1 = create_dummy_file(b"Original Asset", folder)
        file2 = create_dummy_file(b"Modified Asset", folder)

        signature1 = crypto.sign_document(file1, priv_key, PASSWORD)
        signature2 = crypto.sign_document(file2, priv_key, PASSWORD)

        assert signature1 != signature2


# =====================================================================
# 9. Test key_manager: Enkripsi & Dekripsi AES-256-GCM Roundtrip
# =====================================================================
def test_key_manager_roundtrip():
    test_key_pem = b"-----BEGIN EC PRIVATE KEY-----\nTEST_KEY_DATA\n-----END EC PRIVATE KEY-----"
    master_pass = b"super_secure_master_password_999"

    # Enkripsi
    encrypted = key_manager.encrypt_private_key(test_key_pem, master_pass)
    # Overhead: salt (16) + iv (12) + tag (16) = 44 bytes
    assert len(encrypted) == len(test_key_pem) + 44

    # Dekripsi
    decrypted = key_manager.decrypt_private_key(encrypted, master_pass)
    assert decrypted == test_key_pem


# =====================================================================
# 10. Test key_manager: Penolakan Password Master yang Salah
# =====================================================================
def test_key_manager_wrong_password():
    test_key_pem = b"PRIVATE_KEY_BYTES"
    master_pass = b"correct_password"
    wrong_pass = b"incorrect_password"

    encrypted = key_manager.encrypt_private_key(test_key_pem, master_pass)

    with pytest.raises(InvalidTag):
        key_manager.decrypt_private_key(encrypted, wrong_pass)


# =====================================================================
# 11. Test key_manager: Deteksi Manipulasi Ciphertext (Tampering)
# =====================================================================
def test_key_manager_tampered_ciphertext():
    test_key_pem = b"HIGH_SECURITY_ASSET_KEY"
    master_pass = b"master_pass_123"

    encrypted = bytearray(key_manager.encrypt_private_key(test_key_pem, master_pass))

    # Rusak 1 byte di bagian ciphertext / tag
    encrypted[-1] ^= 0xFF

    with pytest.raises(InvalidTag):
        key_manager.decrypt_private_key(bytes(encrypted), master_pass)


# =====================================================================
# 12. Test key_manager: Validasi Input Kosong & Data Terpotong
# =====================================================================
def test_key_manager_invalid_inputs():
    master_pass = b"valid_password"

    # Input kosong harus melempar ValueError
    with pytest.raises(ValueError):
        key_manager.encrypt_private_key(b"", master_pass)

    with pytest.raises(ValueError):
        key_manager.encrypt_private_key(b"some_key", b"")

    with pytest.raises(ValueError):
        key_manager.decrypt_private_key(b"", master_pass)

    # Data terlalu pendek (< 44 bytes)
    with pytest.raises(ValueError):
        key_manager.decrypt_private_key(b"too_short_data", master_pass)


# =====================================================================
# 13. Test key_manager: Simpan & Muat File Terenkripsi (save/load)
# =====================================================================
def test_key_manager_save_and_load_file():
    with tempfile.TemporaryDirectory() as folder:
        target_path = os.path.join(folder, "keys", "private_key.enc")
        test_key_pem = b"SECRET_PEM_CONTENT_STORED_TO_DISK"
        master_pass = "string_password_supported"

        saved_path = key_manager.save_encrypted_key(test_key_pem, master_pass, target_path)
        assert os.path.exists(saved_path)

        loaded_key = key_manager.load_encrypted_key(saved_path, master_pass)
        assert loaded_key == test_key_pem


if __name__ == '__main__':
    print("=" * 60)
    print("Menjalankan Artisign Security Test Suite...")
    print("=" * 60)
    import sys
    ret = pytest.main([__file__, "-v"])
    sys.exit(ret)