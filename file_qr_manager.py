import os
import json
import base64
import zipfile
import qrcode
from crypto_core import DigitalSignatureApp
from pdf_manager import PDFManager

class FileQRManager:
    """
    Kelas untuk mengelola hashing file, penandatanganan digital,
    pembuatan sertifikat & QR Code, verifikasi, serta penyimpanan bundel hasil.
    """
    def __init__(self, crypto_app: DigitalSignatureApp = None, pdf_mgr: PDFManager = None):
        self.crypto_app = crypto_app or DigitalSignatureApp()
        self.pdf_mgr = pdf_mgr or PDFManager()

    def create_verification_qr(
        self,
        file_path: str,
        private_key_path: str,
        password: bytes,
        creator_metadata: dict,
        output_dir: str = "./hasil_enkripsi",
        verification_url_base: str = "https://example.com/verify",
        qr_filename: str = "qr_sertifikat.png"
    ) -> dict:
        """
        1. Membuat folder keluaran secara otomatis jika belum ada.
        2. Menghitung hash dari file.
        3. Menandatangani hash dengan private key.
        4. Menyimpan signature dan metadata sertifikat ke dalam folder keluaran.
        5. Menghasilkan QR Code di dalam folder keluaran.
        6. Mengemas semuanya ke dalam file ZIP bundel.
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

        # 8. Buat Lembar Sertifikat Keaslian Digital A4 (.pdf)
        cert_pdf_path = os.path.join(output_dir, f"{base_name}_certificate.pdf")
        try:
            self.pdf_mgr.generate_certificate_pdf(
                asset_filename=os.path.basename(file_path),
                creator_name=creator_metadata.get("name", "Creator"),
                file_hash_hex=file_hash_hex,
                signature_b64=signature_b64,
                verification_url=verification_url,
                qr_image_path=qr_output_path,
                cert_payload=qr_payload,
                output_pdf_path=cert_pdf_path
            )
        except Exception:
            cert_pdf_path = None

        # 9. Jika berkas asli adalah PDF valid, buat versi Berstempel Segel Digital (_stamped.pdf)
        stamped_pdf_path = None
        if file_path.lower().endswith(".pdf"):
            candidate_stamped = os.path.join(output_dir, f"{base_name}_stamped.pdf")
            try:
                stamped_pdf_path = self.pdf_mgr.stamp_pdf(
                    original_pdf_path=file_path,
                    qr_image_path=qr_output_path,
                    creator_name=creator_metadata.get("name", "Creator"),
                    file_hash_hex=file_hash_hex,
                    signature_b64=signature_b64,
                    cert_payload=qr_payload,
                    output_pdf_path=candidate_stamped
                )
            except Exception:
                stamped_pdf_path = None

        # 10. Simpan paket ZIP bundel lengkap
        bundle_file_path = os.path.join(output_dir, f"{base_name}_bundle.zip")
        with zipfile.ZipFile(bundle_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(sig_file_path, arcname=os.path.basename(sig_file_path))
            zipf.write(cert_file_path, arcname=os.path.basename(cert_file_path))
            zipf.write(qr_output_path, arcname=os.path.basename(qr_output_path))
            if cert_pdf_path and os.path.exists(cert_pdf_path):
                zipf.write(cert_pdf_path, arcname=os.path.basename(cert_pdf_path))
            if stamped_pdf_path and os.path.exists(stamped_pdf_path):
                zipf.write(stamped_pdf_path, arcname=os.path.basename(stamped_pdf_path))

        return {
            "file_hash": file_hash_hex,
            "signature": signature_b64,
            "verification_url": verification_url,
            "signature_file": sig_file_path,
            "certificate_file": cert_file_path,
            "qr_code_path": qr_output_path,
            "certificate_pdf": cert_pdf_path,
            "stamped_pdf": stamped_pdf_path,
            "bundle_file": bundle_file_path
        }

    def generate_certificate(
        self,
        creator_name: str,
        file_hash: bytes,
        signature: bytes,
        output_dir: str = "./hasil_enkripsi",
        base_name: str = "dokumen",
        verification_url_base: str = "https://example.com/verify"
    ) -> str:
        """
        Fungsi pembantu (kompatibilitas) untuk membuat sertifikat langsung
        dari nilai hash dan signature yang sudah ada.
        Mengembalikan path file sertifikat JSON.
        """
        os.makedirs(output_dir, exist_ok=True)
        file_hash_hex = file_hash.hex() if isinstance(file_hash, bytes) else str(file_hash)
        signature_b64 = base64.b64encode(signature).decode('utf-8') if isinstance(signature, bytes) else str(signature)

        verification_url = f"{verification_url_base}?hash={file_hash_hex}&signature={signature_b64}"
        qr_payload = {
            "creator": {"name": creator_name, "role": "Creator"},
            "hash": file_hash_hex,
            "signature": signature_b64,
            "verification_url": verification_url
        }

        cert_file_path = os.path.join(output_dir, f"{base_name}_certificate.json")
        with open(cert_file_path, "w", encoding="utf-8") as f:
            json.dump(qr_payload, f, indent=4)

        qr_output_path = os.path.join(output_dir, f"{base_name}_qr.png")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(qr_payload, indent=2))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(qr_output_path)

        bundle_path = os.path.join(output_dir, f"{base_name}_bundle.zip")
        with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(cert_file_path, arcname=os.path.basename(cert_file_path))
            zipf.write(qr_output_path, arcname=os.path.basename(qr_output_path))

        return cert_file_path

    def verify_certificate_file(self, cert_file_path: str, asset_file_path: str, public_key_path: str) -> dict:
        """
        Memverifikasi integritas berkas aset berdasarkan berkas sertifikat (.json, .sig, atau .zip).
        Mengecek kecocokan hash (Tamper Detection) dan validitas tanda tangan ECDSA.
        """
        if not os.path.exists(cert_file_path):
            return {"valid": False, "tampered": True, "message": "File sertifikat tidak ditemukan."}
        if not os.path.exists(asset_file_path):
            return {"valid": False, "tampered": True, "message": "File aset asli tidak ditemukan."}
        if not os.path.exists(public_key_path):
            return {"valid": False, "tampered": True, "message": "Kunci publik verifikator tidak ditemukan di server."}

        current_hash_hex = self.crypto_app.hash_file(asset_file_path).hex()
        creator_info = None
        signature_bytes = None
        expected_hash_hex = None

        ext = os.path.splitext(cert_file_path)[1].lower()

        # Kasus 1: File ZIP (bundel)
        if ext == ".zip":
            try:
                with zipfile.ZipFile(cert_file_path, 'r') as zf:
                    cert_json_name = next((name for name in zf.namelist() if name.endswith('_certificate.json')), None)
                    if cert_json_name:
                        with zf.open(cert_json_name) as jf:
                            cert_data = json.load(jf)
                            expected_hash_hex = cert_data.get("hash")
                            sig_b64 = cert_data.get("signature")
                            creator_info = cert_data.get("creator")
                            if sig_b64:
                                signature_bytes = base64.b64decode(sig_b64)
                    else:
                        sig_name = next((name for name in zf.namelist() if name.endswith('.sig')), None)
                        if sig_name:
                            with zf.open(sig_name) as sf:
                                signature_bytes = sf.read()
            except Exception as e:
                return {
                    "valid": False,
                    "tampered": True,
                    "message": f"Berkas arsip ZIP rusak atau tidak valid: {str(e)}"
                }

        # Kasus 2: File JSON Sertifikat
        elif ext == ".json":
            try:
                with open(cert_file_path, "r", encoding="utf-8") as f:
                    cert_data = json.load(f)
                    expected_hash_hex = cert_data.get("hash")
                    sig_b64 = cert_data.get("signature")
                    creator_info = cert_data.get("creator")
                    if sig_b64:
                        signature_bytes = base64.b64decode(sig_b64)
            except Exception as e:
                return {
                    "valid": False,
                    "tampered": True,
                    "message": f"Format file sertifikat JSON rusak atau tidak valid: {str(e)}"
                }

        # Kasus 3: File .sig biner tanda tangan
        elif ext == ".sig":
            try:
                with open(cert_file_path, "rb") as f:
                    signature_bytes = f.read()
            except Exception as e:
                return {
                    "valid": False,
                    "tampered": True,
                    "message": f"Gagal membaca berkas tanda tangan: {str(e)}"
                }

        # Kasus 4: File PDF (Certified PDF atau Sertifikat PDF dengan sertifikat tertanam)
        elif ext == ".pdf":
            extracted_cert = self.pdf_mgr.extract_certificate_from_pdf(cert_file_path)
            if extracted_cert:
                expected_hash_hex = extracted_cert.get("hash")
                sig_b64 = extracted_cert.get("signature")
                creator_info = extracted_cert.get("creator")
                if sig_b64:
                    signature_bytes = base64.b64decode(sig_b64)
            else:
                return {
                    "valid": False,
                    "tampered": True,
                    "message": "Dokumen PDF ini tidak memiliki sertifikat digital Artisign tertanam."
                }

        else:
            return {
                "valid": False,
                "tampered": True,
                "message": "Format sertifikat tidak didukung. Harap unggah file .json, .sig, .zip, atau .pdf."
            }

        if not signature_bytes:
            return {
                "valid": False,
                "tampered": True,
                "message": "Tanda tangan digital tidak ditemukan di dalam berkas sertifikat."
            }

        # 1. Uji Tamper Hash (jika hash tercatat di sertifikat)
        hash_matched = True
        if expected_hash_hex:
            hash_matched = (current_hash_hex.lower() == expected_hash_hex.lower())
            if not hash_matched:
                return {
                    "valid": False,
                    "tampered": True,
                    "hash_matched": False,
                    "expected_hash": expected_hash_hex,
                    "calculated_hash": current_hash_hex,
                    "creator": creator_info,
                    "message": "Peringatan! Sidik jari dokumen tidak cocok. File aset telah diubah/dimanipulasi (Tampered)!"
                }

        # 2. Uji Keabsahan Tanda Tangan Kriptografis ECDSA P-256
        sig_valid = self.crypto_app.verify_signature(asset_file_path, signature_bytes, public_key_path)

        if sig_valid and hash_matched:
            return {
                "valid": True,
                "tampered": False,
                "hash_matched": True,
                "signature_valid": True,
                "calculated_hash": current_hash_hex,
                "creator": creator_info,
                "message": "Dokumen terbukti ASLI dan belum pernah dimanipulasi sama sekali."
            }
        else:
            return {
                "valid": False,
                "tampered": True,
                "hash_matched": hash_matched,
                "signature_valid": False,
                "calculated_hash": current_hash_hex,
                "creator": creator_info,
                "message": "Tanda tangan digital tidak valid atau kunci publik tidak cocok."
            }