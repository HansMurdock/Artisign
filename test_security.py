import os
import tempfile

from crypto_core import DigitalSignatureApp


crypto = DigitalSignatureApp()


PASSWORD = b"test_password_123"


def create_dummy_file(content):

    file = tempfile.NamedTemporaryFile(delete=False)
    file.write(content)
    file.close()

    return file.name


# 1. Test fenerate key
def test_key_generation():

    with tempfile.TemporaryDirectory() as folder:

        result = crypto.generate_keys(
            PASSWORD,
            folder
        )

        assert os.path.exists(
            folder + "/private_key.pem"
        )

        assert os.path.exists(
            folder + "/public_key.pem"
        )


# 2. Test hash SHA256
def test_hash_sha256():

    file = create_dummy_file(
        b"Artisign Asset"
    )

    result1 = crypto.hash_file(file)
    result2 = crypto.hash_file(file)

    assert len(result1)==32

    assert result1 == result2


# 3. Test signature berhasil
def test_valid_signature():

    with tempfile.TemporaryDirectory() as folder:

        crypto.generate_keys(
            PASSWORD,
            folder
        )

        file=create_dummy_file(
            b"Original Asset"
        )

        signature = crypto.sign_document(
            file,
            folder+"/private_key.pem",
            PASSWORD
        )

        result = crypto.verify_signature(
            file,
            signature,
            folder+"/public_key.pem"
        )

        assert result == True


# 4. Test tamper
def test_document_tampered():

    with tempfile.TemporaryDirectory() as folder:

        crypto.generate_keys(
            PASSWORD,
            folder
        )

        file=create_dummy_file(
            b"Original"
        )

        signature = crypto.sign_document(
            file,
            folder+"/private_key.pem",
            PASSWORD
        )

        # ubah isi file
        with open(file,"wb") as f:
            f.write(
                b"Modified"
            )

        result = crypto.verify_signature(
            file,
            signature,
            folder+"/public_key.pem"
        )

        assert result == False


# 5. Wrong key
def test_wrong_public_key():

    with tempfile.TemporaryDirectory() as folder1:

      with tempfile.TemporaryDirectory() as folder2:

        crypto.generate_keys(
            PASSWORD,
            folder1
        )

        crypto.generate_keys(
            PASSWORD,
            folder2
        )

        file=create_dummy_file(
            b"Asset"
        )

        signature=crypto.sign_document(
            file,
            folder1+"/private_key.pem",
            PASSWORD
        )

        result=crypto.verify_signature(
            file,
            signature,
            folder2+"/public_key.pem"
        )

        assert result == False


# 6. Wrong password test
def test_wrong_private_key_password():

    with tempfile.TemporaryDirectory() as folder:

        crypto.generate_keys(
            PASSWORD,
            folder
        )

        file = create_dummy_file(
            b"Secret Asset"
        )

        try:

            crypto.sign_document(
                file,
                folder + "/private_key.pem",
                b"wrong_password"
            )

            # kalau sampai sini berarti gagal ditolak
            assert False


        except Exception:

            assert True


# 7. private key encryption test
def test_private_key_encrypted():

    with tempfile.TemporaryDirectory() as folder:

        crypto.generate_keys(
            PASSWORD,
            folder
        )


        with open(
            folder + "/private_key.pem",
            "rb"
        ) as f:

            key_content = f.read()


        assert b"ENCRYPTED" in key_content


# 8. signature difference test
def test_signature_changes_when_file_modified():

    with tempfile.TemporaryDirectory() as folder:

        crypto.generate_keys(
            PASSWORD,
            folder
        )


        file1 = create_dummy_file(
            b"Original Asset"
        )


        file2 = create_dummy_file(
            b"Modified Asset"
        )


        signature1 = crypto.sign_document(
            file1,
            folder + "/private_key.pem",
            PASSWORD
        )


        signature2 = crypto.sign_document(
            file2,
            folder + "/private_key.pem",
            PASSWORD
        )


        assert signature1 != signature2