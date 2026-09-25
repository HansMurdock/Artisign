from crypto_core import DigitalSignatureApp

app = DigitalSignatureApp()
password_rahasia = b"super_secret_password_123"

# 1. Generate Kunci
app.generate_keys(password_rahasia)
print("Kunci berhasil dibuat.")

# 2. Buat file dummy PDF untuk diuji
with open("dokumen_penting.pdf", "w") as f:
    f.write("Ini adalah isi sertifikat aset game.")

# 3. Proses Penandatanganan
signature = app.sign_document("dokumen_penting.pdf", "private_key.pem", password_rahasia)
print(f"Dokumen ditandatangani. Ukuran signature: {len(signature)} bytes")

# 4. Verifikasi Normal
is_valid = app.verify_signature("dokumen_penting.pdf", signature, "public_key.pem")
print(f"Status Verifikasi Asli: {is_valid}")

# 5. Uji Tamper (Mengubah satu byte dokumen)
with open("dokumen_penting.pdf", "a") as f:
    f.write("x") # Menambahkan 1 karakter ilegal
    
is_valid_tampered = app.verify_signature("dokumen_penting.pdf", signature, "public_key.pem")
print(f"Status Verifikasi Setelah Diubah: {is_valid_tampered}")