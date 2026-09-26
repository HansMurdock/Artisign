import os
from crypto_core import DigitalSignatureApp
from file_qr_manager import FileQRManager

# Inisialisasi
crypto_app = DigitalSignatureApp()
qr_manager = FileQRManager(crypto_app)
password_rahasia = b"super_secret_password_123"

# 1. Pastikan folder-folder penampung sudah dibuat
os.makedirs("./keys", exist_ok=True)
os.makedirs("./documents", exist_ok=True)

# 2. Buat file dummy di dalam folder 'documents'
file_test = "./documents/dokumen_penting.pdf"
with open(file_test, "w") as f:
    f.write("Ini adalah isi sertifikat aset digital.")

# 3. Generate Kunci
crypto_app.generate_keys(password_rahasia, save_path="./keys")

# 4. Metadata Kreator
creator_metadata = {
    "name": "Rafa Ahza Naufal",
    "role": "Creator",
    "email": "creator@example.com"
}


result = qr_manager.create_verification_qr(
    file_path=file_test,
    private_key_path="./keys/private_key.pem",
    password=password_rahasia,
    creator_metadata=creator_metadata,
    output_dir="./hasil_enkripsi",
    verification_url_base="https://verifikasi-aset.com/verify",
    qr_filename="qr_sertifikat.png"
)

print("=== Hasil Pengolahan ===")
print(f"Hash File         : {result['file_hash']}")
print(f"File Signature    : {result['signature_file']}")
print(f"File Certificate  : {result['certificate_file']}")
print(f"File QR Code      : {result['qr_code_path']}")