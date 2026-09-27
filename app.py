import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

# Mengimpor modul inti buatanmu dan rekanmu
from crypto_core import DigitalSignatureApp
from file_qr_manager import FileQRManager

app = Flask(__name__)

# Konfigurasi folder penyimpanan file sementara
app.config['UPLOAD_FOLDER'] = './documents'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inisialisasi kelas kriptografi dan pengelola dokumen
crypto_app = DigitalSignatureApp()
qr_manager = FileQRManager(crypto_app)

@app.route('/')
def index():
    """Menampilkan halaman dashboard utama (Ruang Kreator & Validator)"""
    return render_template('index.html')

@app.route('/sign', methods=['POST'])
def sign_file():
    """Menangani proses penandatanganan dari form Ruang Kreator"""
    # 1. Validasi input dari form web
    if 'file_upload' not in request.files:
        return render_template('result.html', type='error', title='Gagal', message='Tidak ada file yang diunggah.')
        
    file = request.files['file_upload']
    creator_name = request.form.get('creator_name')
    
    if file.filename == '':
        return render_template('result.html', type='error', title='Gagal', message='File tidak valid atau kosong.')

    # Mengambil password dari form web dan mengubahnya menjadi bytes
    password = request.form.get('password').encode()
    
    # 2. Simpan file yang diunggah ke folder sementara
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # 3. Proses Kriptografi (Core Logic)
        file_hash = crypto_app.hash_file(filepath)
        
        # Pastikan private_key.pem milikmu sudah ada di dalam folder ./keys/
        signature = crypto_app.sign_document(filepath, "./keys/private_key.pem", password)
        
        # 4. Pembuatan Sertifikat & QR Code (Module rekanmu)
        file_cert_path = qr_manager.generate_certificate(creator_name, file_hash, signature)
        
        # 5. Ambil nama file hasil akhir untuk dikirim ke tombol download di UI
        cert_filename = os.path.basename(file_cert_path)
        
        # 6. Tampilkan halaman sukses!
        return render_template('result.html', 
                               type='success', 
                               title='Sertifikat Berhasil Dibuat!',
                               message=f'Aset digital atas nama {creator_name} telah diamankan secara kriptografis.',
                               file_url=f'/download/{cert_filename}')
                               
    except Exception as e:
        # Menangani error jika password salah atau file rusak
        error_msg = "Password salah, sistem menolak mendekripsi kunci privat." if "Incorrect password" in str(e) else str(e)
        return render_template('result.html', 
                               type='error', 
                               title='Akses Ditolak / Gagal',
                               message=error_msg)

@app.route('/verify', methods=['POST'])
def verify_file():
    """Menangani proses verifikasi dari form Validator Publik (Tamper Test)"""
    # Fitur ini akan kita kerjakan di fase selanjutnya. 
    # Untuk sementara, ini akan menampilkan pesan informatif di UI agar web tidak error.
    return render_template('result.html', 
                           type='error', 
                           title='Fitur Sedang Dibangun',
                           message='Modul verifikasi untuk mendeteksi uji tamper sedang dalam tahap pengembangan.')

@app.route('/download/<filename>')
def download_file(filename):
    """Menangani tombol unduh (download) sertifikat di halaman hasil"""
    # Mengarahkan pencarian file ke folder hasil buatan rekanmu
    folder_hasil = "./hasil_enkripsi" 
    file_path = os.path.join(folder_hasil, filename)
    
    # as_attachment=True membuat browser otomatis mengunduh file tersebut
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    # Menjalankan server lokal di port 5000
    app.run(debug=True)