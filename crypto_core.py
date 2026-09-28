import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.exceptions import InvalidSignature

class DigitalSignatureApp:
    def __init__(self):
        # Menggunakan ECDSA P-256 sesuai spesifikasi wajib
        self.curve = ec.SECP256R1()
        self.hash_algorithm = hashes.SHA256()

    def generate_keys(self, password: bytes, save_path: str = "./"):
        """
        Membangkitkan pasangan kunci ECDSA P-256.
        Kunci privat diekspor dengan enkripsi menggunakan password.
        """
        private_key = ec.generate_private_key(self.curve)
        public_key = private_key.public_key()

        # Menyimpan Private Key TERENKRIPSI (Wajib untuk keamanan)
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password)
        )
        
        # Menyimpan Public Key
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        with open(os.path.join(save_path, "private_key.pem"), "wb") as f:
            f.write(pem_private)
        
        with open(os.path.join(save_path, "public_key.pem"), "wb") as f:
            f.write(pem_public)
            
        return "Pasangan kunci berhasil dibuat dan diamankan."

    def hash_file(self, file_path: str) -> bytes:
        """
        Menghasilkan nilai hash SHA-256 dari sebuah berkas.
        Membaca dalam bentuk chunks agar kuat memproses file besar (misal: aset Unreal Engine).
        """
        digest = hashes.Hash(self.hash_algorithm)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                digest.update(chunk)
        return digest.finalize()

    def sign_document(self, file_path: str, private_key_path: str, password: bytes) -> bytes:
        """
        Menandatangani hash dokumen.
        """
        # 1. Baca dan dekripsi private key
        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=password,
            )
            
        # 2. Hash file
        file_hash = self.hash_file(file_path)
        
        # 3. Buat tanda tangan digital
        signature = private_key.sign(
            file_hash,
            ec.ECDSA(Prehashed(self.hash_algorithm))
        )
        return signature

    def verify_signature(self, file_path: str, signature: bytes, public_key_path: str) -> bool:
        """
        Memverifikasi keaslian dokumen dan menolak jika file diubah.
        """
        with open(public_key_path, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())
            
        file_hash = self.hash_file(file_path)
        
        try:
            public_key.verify(
                signature,
                file_hash,
                ec.ECDSA(Prehashed(self.hash_algorithm))
            )
            return True
        except (InvalidSignature, ValueError, TypeError):
            return False

# =====================================================================
# Fungsi Mandiri (Level-Modul untuk Kompatibilitas & Pengujian Otomatis)
# =====================================================================

def generate_keys():
    """
    Membangkitkan pasangan kunci privat dan publik ECDSA SECP256R1 (P-256).
    Mengembalikan tuple (private_key, public_key).
    """
    private_key = ec.generate_private_key(ec.SECP256R1())
    return private_key, private_key.public_key()

def hash_document(data: bytes | str) -> bytes:
    """
    Menghasilkan nilai hash SHA-256 dari data mentah (32 bytes).
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data)
    return digest.finalize()

def sign_data(doc_hash: bytes, private_key) -> bytes:
    """
    Menandatangani digest hash menggunakan kunci privat ECDSA P-256.
    """
    return private_key.sign(
        doc_hash,
        ec.ECDSA(Prehashed(hashes.SHA256()))
    )

def verify_signature(doc_hash: bytes, signature: bytes, public_key) -> bool:
    """
    Memverifikasi tanda tangan digital terhadap digest hash menggunakan kunci publik.
    """
    try:
        public_key.verify(
            signature,
            doc_hash,
            ec.ECDSA(Prehashed(hashes.SHA256()))
        )
        return True
    except (InvalidSignature, ValueError, TypeError, Exception):
        return False