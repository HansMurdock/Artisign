import io
import os
import json
import zipfile
import unittest
from app import app, crypto_app, qr_manager

class ArtisignPhase1TestCase(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        # Bersihkan file uji coba yang dihasilkan selama pengetesan dari output dan upload folder
        prefixes = ['test_kontrak', 'dokumen_asli', 'real_test_doc', 'test_doc']
        for target_dir in [app.config['OUTPUT_FOLDER'], app.config['UPLOAD_FOLDER']]:
            if os.path.exists(target_dir):
                for fname in os.listdir(target_dir):
                    if any(fname.startswith(p) for p in prefixes):
                        try:
                            os.remove(os.path.join(target_dir, fname))
                        except Exception:
                            pass

    def setUp(self):
        self.client = app.test_client()
        self.password = "super_secret_password_123"
        self.dummy_content = b"Dokumen Rahasia Negara Versi Asli."
        self.tampered_content = b"Dokumen Rahasia Negara Versi Palsu."

    def test_01_index_and_validator_pages(self):
        """Uji akses halaman / dan /validator"""
        res_index = self.client.get('/')
        self.assertEqual(res_index.status_code, 200)
        self.assertIn(b"Artisign", res_index.data)
        self.assertIn(b"Penerbitan Sertifikat", res_index.data)

        res_validator = self.client.get('/validator')
        self.assertEqual(res_validator.status_code, 200)
        self.assertIn(b"Validator Keaslian", res_validator.data)

    def test_02_sign_wrong_password(self):
        """Uji penolakan jika password salah saat menandatangani"""
        data = {
            'file_upload': (io.BytesIO(self.dummy_content), 'test_doc.pdf'),
            'creator_name': 'Budi Santoso',
            'password': 'wrong_password_xyz'
        }
        res = self.client.post('/sign', data=data, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Password salah", res.data)

    def test_03_sign_success_and_downloads(self):
        """Uji penandatanganan sukses dan pengunduhan bundel"""
        data = {
            'file_upload': (io.BytesIO(self.dummy_content), 'test_kontrak.pdf'),
            'creator_name': 'Rafa Ahza Naufal',
            'password': self.password
        }
        res = self.client.post('/sign', data=data, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Sertifikat Berhasil Diterbitkan", res.data)
        self.assertIn(b"test_kontrak_bundle.zip", res.data)

        # Uji unduh bundle zip
        with self.client.get('/download/test_kontrak_bundle.zip') as res_dl:
            self.assertEqual(res_dl.status_code, 200)
            self.assertIn(res_dl.content_type, ['application/zip', 'application/x-zip-compressed'])
            zf = zipfile.ZipFile(io.BytesIO(res_dl.data))
            file_list = zf.namelist()
            self.assertIn('test_kontrak.sig', file_list)
            self.assertIn('test_kontrak_certificate.json', file_list)
            self.assertIn('test_kontrak_qr.png', file_list)

        # Uji preview qr code
        with self.client.get('/preview/test_kontrak_qr.png') as res_prev:
            self.assertEqual(res_prev.status_code, 200)
            self.assertEqual(res_prev.content_type, 'image/png')

    def test_04_verify_original_success(self):
        """Uji verifikasi file asli menghasilkan status ASLI / SAH"""
        # 1. Tandatangani dulu
        sign_data = {
            'file_upload': (io.BytesIO(self.dummy_content), 'dokumen_asli.pdf'),
            'creator_name': 'Siti Rahma',
            'password': self.password
        }
        self.client.post('/sign', data=sign_data, content_type='multipart/form-data')

        # 2. Ambil file sertifikat JSON hasil sign
        cert_path = os.path.join(app.config['OUTPUT_FOLDER'], 'dokumen_asli_certificate.json')
        with open(cert_path, 'rb') as f:
            cert_bytes = f.read()

        # 3. Verifikasi dengan aset asli
        verify_data = {
            'cert_file': (io.BytesIO(cert_bytes), 'dokumen_asli_certificate.json'),
            'asset_file': (io.BytesIO(self.dummy_content), 'dokumen_asli.pdf')
        }
        res_ver = self.client.post('/verify', data=verify_data, content_type='multipart/form-data')
        self.assertEqual(res_ver.status_code, 200)
        self.assertIn(b"Dokumen 100% Asli", res_ver.data)
        self.assertIn(b"Siti Rahma", res_ver.data)

    def test_05_verify_tampered_fails(self):
        """Uji tamper: dokumen yang diubah walau sedikit harus ditolak"""
        cert_path = os.path.join(app.config['OUTPUT_FOLDER'], 'dokumen_asli_certificate.json')
        with open(cert_path, 'rb') as f:
            cert_bytes = f.read()

        # Gunakan konten palsu/berubah
        verify_data = {
            'cert_file': (io.BytesIO(cert_bytes), 'dokumen_asli_certificate.json'),
            'asset_file': (io.BytesIO(self.tampered_content), 'dokumen_asli.pdf')
        }
        res_ver = self.client.post('/verify', data=verify_data, content_type='multipart/form-data')
        self.assertEqual(res_ver.status_code, 200)
        self.assertIn(b"Peringatan: Dokumen Telah Diubah", res_ver.data)

    def test_06_verify_get_qr_scan(self):
        """Uji scan QR code membuka URL verifikasi dengan prefilled hash"""
        dummy_hash = "71337c1072298d3c8f93534764fcd45f8bf0f04736bfb70093d7267b3f14b4de"
        res = self.client.get(f'/verify?hash={dummy_hash}')
        self.assertEqual(res.status_code, 200)
        self.assertIn(dummy_hash.encode(), res.data)
        self.assertIn(b"Sertifikat Terdeteksi dari QR Code", res.data)

    def test_07_pdf_stamping_and_embedded_cert(self):
        """Uji stamping visual pada PDF dan verifikasi dari sertifikat tertanam di PDF"""
        import pymupdf

        # 1. Buat PDF asli valid
        doc = pymupdf.open()
        p = doc.new_page()
        p.insert_text((50, 50), "Dokumen Ijazah Digital Resmi.")
        pdf_bytes = doc.tobytes()
        doc.close()

        # 2. Kirim ke /sign
        data = {
            'file_upload': (io.BytesIO(pdf_bytes), 'real_test_doc.pdf'),
            'creator_name': 'Universitas Indonesia',
            'password': self.password
        }
        res_sign = self.client.post('/sign', data=data, content_type='multipart/form-data')
        self.assertEqual(res_sign.status_code, 200)
        self.assertIn(b"real_test_doc_stamped.pdf", res_sign.data)
        self.assertIn(b"real_test_doc_certificate.pdf", res_sign.data)

        # 3. Pastikan PDF berstempel dan sertifikat PDF terbentuk di folder output
        stamped_path = os.path.join(app.config['OUTPUT_FOLDER'], 'real_test_doc_stamped.pdf')
        cert_pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], 'real_test_doc_certificate.pdf')
        self.assertTrue(os.path.exists(stamped_path))
        self.assertTrue(os.path.exists(cert_pdf_path))

        # 4. Uji verifikasi langsung menggunakan file PDF sebagai cert_file
        with open(stamped_path, 'rb') as f:
            stamped_bytes = f.read()

        verify_data = {
            'cert_file': (io.BytesIO(stamped_bytes), 'real_test_doc_stamped.pdf'),
            'asset_file': (io.BytesIO(pdf_bytes), 'real_test_doc.pdf')
        }
        res_ver = self.client.post('/verify', data=verify_data, content_type='multipart/form-data')
        self.assertEqual(res_ver.status_code, 200)
        self.assertIn(b"Dokumen 100% Asli", res_ver.data)
        self.assertIn(b"Universitas Indonesia", res_ver.data)

    def test_08_empty_fields_handling(self):
        """Uji pengiriman form kosong pada /sign dan /verify"""
        # Form /sign tanpa nama
        res_sign = self.client.post('/sign', data={'file_upload': (io.BytesIO(b'abc'), 'test.txt'), 'creator_name': '', 'password': self.password}, content_type='multipart/form-data')
        self.assertIn(b"Nama kreator wajib diisi", res_sign.data)

        # Form /sign tanpa password
        res_sign2 = self.client.post('/sign', data={'file_upload': (io.BytesIO(b'abc'), 'test.txt'), 'creator_name': 'Budi', 'password': ''}, content_type='multipart/form-data')
        self.assertIn(b"Password private key wajib diisi", res_sign2.data)

        # Form /verify tanpa file
        res_ver = self.client.post('/verify', data={}, content_type='multipart/form-data')
        self.assertIn(b"File Tidak Lengkap", res_ver.data)

    def test_09_corrupted_and_unsupported_formats(self):
        """Uji sertifikat korup dan format yang tidak didukung"""
        # Sertifikat JSON korup
        data = {
            'cert_file': (io.BytesIO(b"ini bukan json {{{"), 'bad.json'),
            'asset_file': (io.BytesIO(b"konten asli"), 'asli.txt')
        }
        res = self.client.post('/verify', data=data, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Format file sertifikat JSON rusak", res.data)

        # Format tidak didukung (.exe)
        data2 = {
            'cert_file': (io.BytesIO(b"fake cert"), 'bad.exe'),
            'asset_file': (io.BytesIO(b"konten asli"), 'asli.txt')
        }
        res2 = self.client.post('/verify', data=data2, content_type='multipart/form-data')
        self.assertEqual(res2.status_code, 200)
        self.assertIn(b"Format sertifikat tidak didukung", res2.data)

    def test_10_download_and_preview_security(self):
        """Uji keamanan download dan penanganan 404"""
        # File tidak ditemukan
        res = self.client.get('/download/file_yang_pasti_tidak_ada.zip')
        self.assertEqual(res.status_code, 404)
        self.assertIn(b"tidak ditemukan", res.data)

        # Preview file tidak ada
        res_prev = self.client.get('/preview/file_tidak_ada.png')
        self.assertEqual(res_prev.status_code, 404)

        # Halaman 404 umum
        res_404 = self.client.get('/halaman_ngawur_123')
        self.assertEqual(res_404.status_code, 404)

if __name__ == '__main__':
    unittest.main()
