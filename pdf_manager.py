import os
import json
from datetime import datetime
import pymupdf

class PDFManager:
    """
    Kelas untuk menangani manipulasi dokumen PDF menggunakan PyMuPDF:
    1. Menyematkan stempel visual tanda tangan & QR Code (PDF Stamping).
    2. Menghasilkan lembar Sertifikat Keaslian Digital resmi ukuran A4.
    3. Mengekstrak sertifikat kriptografi yang tertanam di dalam PDF.
    """
    def __init__(self):
        pass

    def stamp_pdf(
        self,
        original_pdf_path: str,
        qr_image_path: str,
        creator_name: str,
        file_hash_hex: str,
        signature_b64: str,
        cert_payload: dict,
        output_pdf_path: str
    ) -> str:
        """
        Menyematkan stempel visual QR Code, detail kriptografis, dan melampirkan
        metadata sertifikat JSON ke dalam dokumen PDF asli.
        """
        try:
            with pymupdf.open(original_pdf_path) as doc:
                if len(doc) == 0:
                    raise ValueError("Dokumen PDF tidak memiliki halaman.")

                # Ambil halaman terakhir untuk menempelkan stempel segel resmi
                page = doc[-1]
                rect = page.rect

                # Ukuran dan posisi stempel (pojok kanan bawah halaman)
                stamp_width = 240
                stamp_height = 80
                margin_right = 25
                margin_bottom = 25

                x1 = rect.width - stamp_width - margin_right
                y1 = rect.height - stamp_height - margin_bottom
                x2 = rect.width - margin_right
                y2 = rect.height - margin_bottom

                # Jika halaman terlalu kecil, sesuaikan koordinat agar tidak keluar batas
                if x1 < 10:
                    x1 = 10
                    x2 = min(rect.width - 10, x1 + stamp_width)
                if y1 < 10:
                    y1 = 10
                    y2 = min(rect.height - 10, y1 + stamp_height)

                stamp_rect = pymupdf.Rect(x1, y1, x2, y2)

                # 1. Gambar latar belakang kartu stempel dengan border biru elegan
                page.draw_rect(stamp_rect, color=(0.15, 0.38, 0.78), fill=(0.97, 0.98, 1.0), width=1.2)

                # 2. Sisipkan gambar QR Code
                qr_size = 64
                qr_rect = pymupdf.Rect(x1 + 8, y1 + 8, x1 + 8 + qr_size, y1 + 8 + qr_size)
                if os.path.exists(qr_image_path):
                    page.insert_image(qr_rect, filename=qr_image_path)

                # 3. Sisipkan teks informasi stempel resmi
                text_x = x1 + 80
                page.insert_text((text_x, y1 + 20), "SEALED BY ARTISIGN", fontsize=9, fontname="helv", color=(0.1, 0.3, 0.7))
                
                # Potong nama kreator jika terlalu panjang
                display_creator = (creator_name[:20] + '..') if len(creator_name) > 20 else creator_name
                page.insert_text((text_x, y1 + 33), f"Kreator: {display_creator}", fontsize=7.5, fontname="helv", color=(0.2, 0.2, 0.2))
                
                page.insert_text((text_x, y1 + 45), "ECDSA P-256 / SHA-256", fontsize=7, fontname="helv", color=(0.05, 0.55, 0.25))
                
                hash_short = f"Hash: {file_hash_hex[:12]}..."
                page.insert_text((text_x, y1 + 56), hash_short, fontsize=6.5, fontname="helv", color=(0.4, 0.4, 0.4))
                page.insert_text((text_x, y1 + 67), "Scan QR utk verifikasi sah", fontsize=6.5, fontname="helv", color=(0.25, 0.45, 0.75))

                # 4. Tanamkan file sertifikat JSON langsung ke dalam PDF sebagai embedded file
                cert_bytes = json.dumps(cert_payload, indent=2).encode('utf-8')
                doc.embfile_add(
                    "artisign_certificate.json",
                    cert_bytes,
                    filename="artisign_certificate.json",
                    ufilename="artisign_certificate.json",
                    desc="Artisign Cryptographic Certificate"
                )

                # 5. Perbarui metadata dokumen
                doc.set_metadata({
                    "title": f"Artisign Certified - {os.path.basename(original_pdf_path)}",
                    "author": creator_name,
                    "subject": "Digital Asset Certified by Artisign (ECDSA P-256)",
                    "keywords": f"artisign,ecdsa,p256,sha256,hash:{file_hash_hex}"
                })

                # Simpan hasil akhir
                doc.save(output_pdf_path, deflate=True)
            return output_pdf_path
        except Exception as e:
            raise ValueError(f"Gagal memproses dokumen PDF: {str(e)}")

    def generate_certificate_pdf(
        self,
        asset_filename: str,
        creator_name: str,
        file_hash_hex: str,
        signature_b64: str,
        verification_url: str,
        qr_image_path: str,
        cert_payload: dict,
        output_pdf_path: str
    ) -> str:
        """
        Menghasilkan lembar Sertifikat Keaslian Digital (A4) berdesain resmi
        dan elegan untuk segala tipe aset (PDF, gambar, file 3D, dokumen, dsb).
        """
        with pymupdf.open() as doc:
            page = doc.new_page(width=595, height=842) # A4 format

            # Margin dan batas dekoratif luar
            page.draw_rect(pymupdf.Rect(30, 30, 565, 812), color=(0.2, 0.4, 0.75), width=2)
            page.draw_rect(pymupdf.Rect(35, 35, 560, 807), color=(0.7, 0.8, 0.9), width=0.8)

            # Header Banner
            page.draw_rect(pymupdf.Rect(40, 40, 555, 120), color=(0.15, 0.35, 0.7), fill=(0.95, 0.97, 1.0))
            page.insert_text((60, 80), "ARTISIGN VERIFIED", fontsize=22, fontname="helv", color=(0.1, 0.3, 0.75))
            page.insert_text((60, 102), "SERTIFIKAT KEASLIAN ASET DIGITAL (CERTIFICATE OF AUTHENTICITY)", fontsize=10, fontname="helv", color=(0.3, 0.4, 0.5))

            # Konten Utama
            y = 155
            page.insert_text((55, y), "DOKUMEN INI MENERANGKAN BAHWA ASET DIGITAL BERIKUT TELAH DIKUNCI SECARA KRIPTOGRAFIS:", fontsize=8.5, fontname="helv", color=(0.4, 0.4, 0.4))

            # Kotak Informasi Aset
            y += 20
            page.draw_rect(pymupdf.Rect(55, y, 540, y + 150), color=(0.85, 0.88, 0.92), fill=(0.98, 0.99, 1.0))
            
            info_y = y + 25
            page.insert_text((75, info_y), "Nama Aset / Berkas", fontsize=9, fontname="helv", color=(0.5, 0.5, 0.5))
            page.insert_text((200, info_y), f": {asset_filename}", fontsize=10, fontname="helv", color=(0.1, 0.1, 0.1))

            info_y += 25
            page.insert_text((75, info_y), "Pencipta / Pemilik Sah", fontsize=9, fontname="helv", color=(0.5, 0.5, 0.5))
            page.insert_text((200, info_y), f": {creator_name}", fontsize=10, fontname="helv", color=(0.1, 0.3, 0.8))

            info_y += 25
            page.insert_text((75, info_y), "Waktu Penerbitan", fontsize=9, fontname="helv", color=(0.5, 0.5, 0.5))
            now_str = datetime.now().strftime("%d %B %Y, %H:%M:%S UTC")
            page.insert_text((200, info_y), f": {now_str}", fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))

            info_y += 25
            page.insert_text((75, info_y), "Standar Kriptografi", fontsize=9, fontname="helv", color=(0.5, 0.5, 0.5))
            page.insert_text((200, info_y), ": ECDSA Curve SECP256R1 (NIST P-256) & SHA-256", fontsize=9, fontname="helv", color=(0.05, 0.55, 0.25))

            info_y += 25
            page.insert_text((75, info_y), "Status Integritas", fontsize=9, fontname="helv", color=(0.5, 0.5, 0.5))
            page.insert_text((200, info_y), ": TERVERIFIKASI & ANTI-TAMPER PROTECTED", fontsize=9, fontname="helv", color=(0.05, 0.6, 0.2))

            # Kotak Hash Kriptografi
            y += 170
            page.draw_rect(pymupdf.Rect(55, y, 540, y + 65), color=(0.85, 0.88, 0.92), fill=(1.0, 1.0, 1.0))
            page.insert_text((70, y + 20), "SHA-256 HASH (FINGERPRINT RESMI BERKAS):", fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
            page.insert_text((70, y + 42), file_hash_hex, fontsize=9.5, fontname="courier", color=(0.1, 0.1, 0.1))

            # Kotak Tanda Tangan Digital
            y += 80
            page.draw_rect(pymupdf.Rect(55, y, 540, y + 80), color=(0.85, 0.88, 0.92), fill=(1.0, 1.0, 1.0))
            page.insert_text((70, y + 20), "DIGITAL SIGNATURE (ECDSA DER ENCODED):", fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
            # Pecah signature menjadi dua baris jika panjang
            sig_line1 = signature_b64[:70]
            sig_line2 = signature_b64[70:]
            page.insert_text((70, y + 42), sig_line1, fontsize=8.5, fontname="courier", color=(0.2, 0.4, 0.6))
            if sig_line2:
                page.insert_text((70, y + 58), sig_line2, fontsize=8.5, fontname="courier", color=(0.2, 0.4, 0.6))

            # Bagian Bawah: QR Code & Instruksi Validasi
            y += 105
            qr_size = 140
            qr_rect = pymupdf.Rect(70, y, 70 + qr_size, y + qr_size)
            if os.path.exists(qr_image_path):
                page.insert_image(qr_rect, filename=qr_image_path)
                page.draw_rect(qr_rect, color=(0.8, 0.8, 0.8), width=0.8)

            text_inst_x = 230
            page.insert_text((text_inst_x, y + 25), "CARA MEMVERIFIKASI KEASLIAN:", fontsize=10, fontname="helv", color=(0.1, 0.3, 0.7))
            page.insert_text((text_inst_x, y + 48), "1. Pindai (scan) QR Code di samping menggunakan kamera smartphone.", fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
            page.insert_text((text_inst_x, y + 68), "2. Anda akan diarahkan ke portal verifikasi publik Artisign secara instan.", fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
            page.insert_text((text_inst_x, y + 88), "3. Cocokkan berkas aset untuk memastikan data belum pernah dimanipulasi.", fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
            page.insert_text((text_inst_x, y + 108), "4. Jika 1 byte data diubah, verifikasi otomatis menolak keabsahan dokumen.", fontsize=8, fontname="helv", color=(0.7, 0.2, 0.2))

            # Footer
            page.insert_text((60, 790), "Artisign Cryptographic Platform - Secured by NIST P-256 Asymmetric Cryptography", fontsize=7.5, fontname="helv", color=(0.5, 0.5, 0.5))

            # Tanamkan sertifikat JSON
            cert_bytes = json.dumps(cert_payload, indent=2).encode('utf-8')
            doc.embfile_add(
                "artisign_certificate.json",
                cert_bytes,
                filename="artisign_certificate.json",
                ufilename="artisign_certificate.json",
                desc="Artisign Cryptographic Certificate"
            )

            doc.save(output_pdf_path, deflate=True)
        return output_pdf_path

    def extract_certificate_from_pdf(self, pdf_path: str) -> dict | None:
        """
        Mengekstrak file sertifikat JSON yang tertanam di dalam dokumen PDF.
        """
        try:
            with pymupdf.open(pdf_path) as doc:
                for name in doc.embfile_names():
                    if name.endswith("certificate.json") or "artisign" in name.lower():
                        raw_data = doc.embfile_get(name)
                        return json.loads(raw_data.decode('utf-8'))
        except Exception:
            pass
        return None
