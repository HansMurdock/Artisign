import os
import json
import base64
import qrcode
from crypto_core import DigitalSignatureApp

class FileQRManager:
    """
    Kelas untuk mengelola hashing file, penandatanganan digital,
    dan penyimpanan hasil keluaran ke dalam folder tersendiri.
    """
    def __init__(self, crypto_app: DigitalSignatureApp = None):
        self.crypto_app = crypto_app or DigitalSignatureApp()

    def create_verification_qr(
        self,
        file_path: str,
        private_key_path: str,
        password: bytes,
        creator_metadata: dict,
        output_dir: str = "./output_results",
        verification_url_base: str = "https://example.com/verify",
        qr_filename: str = "qr_sertifikat.png"
    ) -> dict:
        """
        1. Membuat folder keluaran secara otomatis jika belum ada.
        2. Menghitung hash dari file.
        3. Menandatangani hash dengan private key.
        4. Menyimpan signature dan metadata sertifikat ke dalam folder keluaran.
        5. Menghasilkan QR Code di dalam folder keluaran.
        """
        # 1. Pastikan folder keluaran tersedia
        os.makedirs(output_dir, exist_ok=True)

        # 2. Hitung hash file
        file_hash_bytes = self.crypto_app.hash_file(file_path)
        file_hash_hex = file_hash_bytes.hex()

        # 3. Tandatangani hash dengan private key
        signature_bytes = self.crypto_app.sign_document(file_path, private_key_path, password)
        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')

        # 4. Buat URL Verifikasi & Payload
        verification_url = (
            f"{verification_url_base}?"
            f"hash={file_hash_hex}&"
            f"signature={signature_b64}"
        )

        qr_payload = {
            "creator": creator_metadata,
            "hash": file_hash_hex,
            "signature": signature_b64,
            "verification_url": verification_url
        }

        # 5. Simpan berkas signature terpisah (*.sig) di folder output
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        sig_file_path = os.path.join(output_dir, f"{base_name}.sig")
        with open(sig_file_path, "wb") as f:
            f.write(signature_bytes)

        # 6. Simpan berkas sertifikat JSON di folder output
        cert_file_path = os.path.join(output_dir, f"{base_name}_certificate.json")
        with open(cert_file_path, "w", encoding="utf-8") as f:
            json.dump(qr_payload, f, indent=4)

        # 7. Generate dan Simpan Gambar QR Code ke folder output
        qr_output_path = os.path.join(output_dir, qr_filename)
        qr_content = json.dumps(qr_payload, indent=2)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(qr_output_path)

        return {
            "file_hash": file_hash_hex,
            "signature": signature_b64,
            "verification_url": verification_url,
            "signature_file": sig_file_path,
            "certificate_file": cert_file_path,
            "qr_code_path": qr_output_path
        }