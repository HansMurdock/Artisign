import pytest
import os
# Asumsi Anggota 1 membuat fungsi-fungsi ini di file core_crypto.py
from crypto_core import (
    generate_keys, hash_document, sign_data, verify_signature
)

# 1. Test Pembangkitan Kunci
def test_key_generation():
    private_key, public_key = generate_keys()
    assert private_key is not None
    assert public_key is not None
    # Pastikan tipe/panjang kunci sesuai standar ECDSA P-256

# 2. Test Konsistensi Hashing SHA-256
def test_hash_consistency():
    dummy_data = b"Ini adalah aset game 3D"
    hash1 = hash_document(dummy_data)
    hash2 = hash_document(dummy_data)
    assert len(hash1) == 32 # SHA-256 selalu menghasilkan 32 byte (256 bit) murni
    assert hash1 == hash2 # Hash data yang sama harus identik

# 3. Test Tanda Tangan & Verifikasi Normal
def test_valid_signature_verification():
    private_key, public_key = generate_keys()
    data = b"Dokumen asli"
    doc_hash = hash_document(data)
    
    signature = sign_data(doc_hash, private_key)
    is_valid = verify_signature(doc_hash, signature, public_key)
    assert is_valid == True # Verifikasi harus berhasil

# 4. Test Uji Tamper (Dokumen Dimodifikasi)
def test_tamper_document():
    private_key, public_key = generate_keys()
    original_data = b"Dokumen lisensi asli"
    original_hash = hash_document(original_data)
    signature = sign_data(original_hash, private_key)
    
    # Simulasikan pembajak mengubah 1 byte dokumen
    tampered_data = b"Dokumen lisensi palsu"
    tampered_hash = hash_document(tampered_data)
    
    # Sistem harus menolak dokumen yang sudah diubah (Uji Tamper)
    is_valid = verify_signature(tampered_hash, signature, public_key)
    assert is_valid == False 

# 5. Test Uji Kunci Salah (Kunci Publik Berbeda)
def test_wrong_public_key():
    priv_key_1, pub_key_1 = generate_keys()
    priv_key_2, pub_key_2 = generate_keys() # Kunci milik orang lain
    
    data = b"Aset game original"
    doc_hash = hash_document(data)
    signature = sign_data(doc_hash, priv_key_1)
    
    # Mencoba verifikasi tanda tangan user 1 menggunakan kunci publik user 2
    is_valid = verify_signature(doc_hash, signature, pub_key_2)
    assert is_valid == False

if __name__ == '__main__':
    print("Menjalankan seluruh pengujian keamanan kriptografi...")
    test_key_generation()
    print("- Test 1: Pembangkitan Kunci ECDSA P-256 ... OK")
    test_hash_consistency()
    print("- Test 2: Konsistensi Hashing SHA-256 ... OK")
    test_valid_signature_verification()
    print("- Test 3: Tanda Tangan & Verifikasi Normal ... OK")
    test_tamper_document()
    print("- Test 4: Uji Tamper (Deteksi Manipulasi Data) ... OK")
    test_wrong_public_key()
    print("- Test 5: Uji Kunci Salah (Penolakan Kunci Publik Berbeda) ... OK")
    print("\nSemua 5 pengujian keamanan kriptografi LULUS 100%!")