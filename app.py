import os
import time
import uuid
from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename

from crypto_core import DigitalSignatureApp
from file_qr_manager import FileQRManager

app = Flask(__name__)

# Konfigurasi folder penyimpanan
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'documents')
app.config['OUTPUT_FOLDER'] = os.path.join(BASE_DIR, 'hasil_enkripsi')
app.config['KEYS_FOLDER'] = os.path.join(BASE_DIR, 'keys')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['KEYS_FOLDER'], exist_ok=True)

# Inisialisasi engine kriptografi dan pengelola berkas
crypto_app = DigitalSignatureApp()
qr_manager = FileQRManager(crypto_app)

# Batas maksimal ukuran unggah berkas: 100 MB (aman untuk shared hosting/cloud free tier)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

def get_key_paths():
    priv_path = os.path.join(app.config['KEYS_FOLDER'], "private_key.pem")
    pub_path = os.path.join(app.config['KEYS_FOLDER'], "public_key.pem")
    return priv_path, pub_path

@app.route('/')
def index():
    """Halaman Landing Page Utama Artisign"""
    return render_template('landing.html')

@app.route('/creator')
def creator_page():
    """Halaman khusus Ruang Kreator (Penerbitan Sertifikat & Tanda Tangan)"""
    return render_template('creator.html')

@app.route('/validator')
def validator_page():
    """Halaman khusus validator berkas digital"""
    return render_template('validator.html')

@app.route('/sign', methods=['POST'])
def sign_file():
    """Menangani proses penandatanganan berkas dari form Ruang Kreator"""
    # 1. Validasi keberadaan file
    if 'file_upload' not in request.files:
        return render_template('result.html', type='error', title='Gagal', message='Tidak ada file yang diunggah.')
        
    file = request.files['file_upload']
    creator_name = (request.form.get('creator_name') or '').strip()
    raw_password = request.form.get('password')

    if file.filename == '':
        return render_template('result.html', type='error', title='Gagal', message='File tidak valid atau kosong.')

    if not creator_name:
        return render_template('result.html', type='error', title='Gagal', message='Nama kreator wajib diisi.')

    if not raw_password:
        return render_template('result.html', type='error', title='Gagal', message='Password private key wajib diisi.')

    password = raw_password.encode('utf-8')

    # 2. Simpan file yang diunggah dengan sanitasi nama yang aman
    raw_filename = secure_filename(file.filename)
    filename = raw_filename if raw_filename else f"dokumen_{int(time.time())}.bin"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    priv_key_path, pub_key_path = get_key_paths()

    # Pastikan kunci privat tersedia
    if not os.path.exists(priv_key_path):
        return render_template('result.html', 
                               type='error', 
                               title='Kunci Privat Tidak Ditemukan', 
                               message='Berkas private_key.pem belum dibuat di server. Jalankan generate_keys terlebih dahulu.')

    try:
        # 3. Proses Kriptografi, Pembuatan Sertifikat & QR Code
        base_name = os.path.splitext(filename)[0]
        creator_metadata = {
            "name": creator_name,
            "role": "Creator"
        }

        # Menggunakan alamat host yang dinamis untuk verification_url
        verification_url_base = request.host_url.rstrip('/') + '/verify'

        result = qr_manager.create_verification_qr(
            file_path=filepath,
            private_key_path=priv_key_path,
            password=password,
            creator_metadata=creator_metadata,
            output_dir=app.config['OUTPUT_FOLDER'],
            verification_url_base=verification_url_base,
            qr_filename=f"{base_name}_qr.png"
        )

        # Nama file untuk keperluan download & preview
        bundle_name = os.path.basename(result.get('bundle_file', ''))
        cert_name = os.path.basename(result.get('certificate_file', ''))
        qr_name = os.path.basename(result.get('qr_code_path', ''))
        cert_pdf_name = os.path.basename(result.get('certificate_pdf', '')) if result.get('certificate_pdf') else None
        stamped_pdf_name = os.path.basename(result.get('stamped_pdf', '')) if result.get('stamped_pdf') else None

        # 4. Tampilkan halaman sukses dengan pratinjau dan opsi download
        return render_template('result.html', 
                               type='success', 
                               title='Sertifikat Berhasil Diterbitkan!',
                               message=f'Aset digital "{filename}" atas nama {creator_name} telah berhasil diamankan secara kriptografis.',
                               file_url=f'/download/{bundle_name}',
                               bundle_url=f'/download/{bundle_name}',
                               cert_url=f'/download/{cert_name}',
                               qr_download_url=f'/download/{qr_name}',
                               qr_preview_url=f'/preview/{qr_name}',
                               cert_pdf_url=f'/download/{cert_pdf_name}' if cert_pdf_name else None,
                               stamped_pdf_url=f'/download/{stamped_pdf_name}' if stamped_pdf_name else None,
                               details={
                                   "filename": filename,
                                   "creator": creator_name,
                                   "hash": result['file_hash'],
                                   "verification_url": result['verification_url']
                               })
                               
    except Exception as e:
        error_text = str(e)
        if "Incorrect password" in error_text or "Bad decrypt" in error_text:
            error_msg = "Password salah! Sistem menolak mendekripsi kunci privat."
        else:
            error_msg = f"Terjadi kesalahan saat memproses dokumen: {error_text}"

        return render_template('result.html', 
                               type='error', 
                               title='Akses Ditolak / Penandatanganan Gagal',
                               message=error_msg)

@app.route('/verify', methods=['GET', 'POST'])
def verify_file():
    """
    Menangani verifikasi dokumen:
    - POST: Verifikasi file sertifikat (.json/.sig/.zip/.pdf) dengan file aset asli (Tamper Test).
    - GET : Menampilkan halaman informasi verifikasi atau mendeteksi parameter QR Code (?hash=...&signature=...).
    """
    priv_key_path, pub_key_path = get_key_paths()

    if request.method == 'GET':
        query_hash = request.args.get('hash')
        query_sig = request.args.get('signature')

        if query_hash:
            # Jika pengguna membuka tautan langsung dari hasil scan QR Code
            return render_template('validator.html', 
                                   prefilled_hash=query_hash, 
                                   prefilled_sig=query_sig)
        return render_template('validator.html')

    # POST: Memproses berkas yang diunggah
    if 'cert_file' not in request.files or 'asset_file' not in request.files:
        return render_template('result.html', 
                               type='error', 
                               title='File Tidak Lengkap', 
                               message='Harap unggah kedua file: Berkas Sertifikat (.json/.sig/.zip/.pdf) dan Berkas Aset Asli.')

    cert_file = request.files['cert_file']
    asset_file = request.files['asset_file']

    if cert_file.filename == '' or asset_file.filename == '':
        return render_template('result.html', 
                               type='error', 
                               title='File Kosong', 
                               message='Salah satu atau kedua file yang dipilih tidak valid.')

    if not os.path.exists(pub_key_path):
        return render_template('result.html', 
                               type='error', 
                               title='Kunci Publik Tidak Ditemukan', 
                               message='Kunci publik verifikator (public_key.pem) belum tersedia di server.')

    temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_verify')
    os.makedirs(temp_dir, exist_ok=True)

    uid = uuid.uuid4().hex[:8]
    raw_cert_name = secure_filename(cert_file.filename) or "cert.dat"
    raw_asset_name = secure_filename(asset_file.filename) or "asset.dat"

    cert_path = os.path.join(temp_dir, f"{uid}_{raw_cert_name}")
    asset_path = os.path.join(temp_dir, f"{uid}_{raw_asset_name}")

    try:
        cert_file.save(cert_path)
        asset_file.save(asset_path)

        # Jalankan mesin verifikasi
        verification = qr_manager.verify_certificate_file(cert_path, asset_path, pub_key_path)

        if verification.get('valid'):
            creator = verification.get('creator') or {}
            creator_name = creator.get('name', 'Terdaftar')
            return render_template('result.html',
                                   type='success',
                                   title='Dokumen 100% Asli & Terverifikasi!',
                                   message=f'Integritas dokumen terbukti sah secara kriptografis atas nama {creator_name}. Tidak ada perubahan atau pemalsuan data pada file ini.',
                                   details={
                                       "filename": raw_asset_name,
                                       "creator": creator_name,
                                       "hash": verification.get('calculated_hash'),
                                       "status": "ASLI (UNTOUCHED)"
                                   })
        else:
            tampered = verification.get('tampered', False)
            title = 'Peringatan: Dokumen Telah Diubah (Tampered)!' if tampered else 'Verifikasi Gagal'
            return render_template('result.html',
                                   type='error',
                                   title=title,
                                   message=verification.get('message', 'Dokumen gagal diverifikasi.'),
                                   details={
                                       "filename": raw_asset_name,
                                       "expected_hash": verification.get('expected_hash', 'N/A'),
                                       "calculated_hash": verification.get('calculated_hash', 'N/A'),
                                       "status": "PALSU / TIDAK VALID"
                                   })

    except Exception as e:
        return render_template('result.html',
                               type='error',
                               title='Kesalahan Sistem Verifikasi',
                               message=f'Gagal memverifikasi dokumen: {str(e)}')
    finally:
        # Pembersihan berkas sementara dengan jaminan eksekusi
        for p in [cert_path, asset_path]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

@app.route('/download/<filename>')
def download_file(filename):
    """Menangani pengunduhan berkas hasil tanda tangan dan sertifikat dengan proteksi direktori"""
    safe_name = secure_filename(filename)
    if not safe_name:
        return render_template('result.html', type='error', title='File Tidak Valid', message='Nama berkas tidak valid.'), 400

    output_dir = os.path.abspath(app.config['OUTPUT_FOLDER'])
    file_path = os.path.abspath(os.path.join(output_dir, safe_name))

    if not file_path.startswith(output_dir) or not os.path.exists(file_path):
        return render_template('result.html', 
                               type='error', 
                               title='File Tidak Ditemukan', 
                               message=f'Berkas "{safe_name}" tidak ditemukan di server.'), 404
        
    return send_file(file_path, as_attachment=True)

@app.route('/preview/<filename>')
def preview_file(filename):
    """Menangani pratinjau gambar QR Code secara langsung di browser dengan proteksi direktori"""
    safe_name = secure_filename(filename)
    if not safe_name:
        return "File tidak valid", 400

    output_dir = os.path.abspath(app.config['OUTPUT_FOLDER'])
    file_path = os.path.abspath(os.path.join(output_dir, safe_name))

    if not file_path.startswith(output_dir) or not os.path.exists(file_path):
        return "File tidak ditemukan", 404
        
    return send_file(file_path, as_attachment=False)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('result.html', type='error', title='404 - Halaman Tidak Ditemukan', message='Halaman atau berkas yang Anda cari tidak tersedia.'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('result.html', type='error', title='500 - Kesalahan Server Internal', message='Terjadi kendala teknis pada sistem. Silakan coba kembali beberapa saat lagi.'), 500

@app.errorhandler(413)
def request_entity_too_large(e):
    return render_template('result.html', type='error', title='413 - Ukuran Berkas Terlalu Besar', 
                           message='Ukuran berkas melebihi batas maksimal 100 MB. Untuk berkas berukuran gigabyte, Anda dapat menggunakan halaman Validator dengan fitur Client-Side Hashing tanpa perlu mengunggah file.'), 413


if __name__ == '__main__':
    # Port dinamis mendukung local running maupun platform cloud (Render/Railway/Heroku)
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(host='0.0.0.0', port=port, debug=debug_mode)