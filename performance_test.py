import os
import time
import csv
import tempfile

from crypto_core import DigitalSignatureApp

# ==================================
# KONFIGURASI
# ==================================

ITERATIONS = 30
PASSWORD = b"performance_test_password"

crypto = DigitalSignatureApp()

# ==================================
# Membuat file dummy asset
# ==================================

def create_test_file(path):

    with open(path, "wb") as f:
        f.write(
            b"Artisign Performance Testing Asset" * 1000
        )


# ==================================
# Performance Testing
# ==================================

def run_test():

    with tempfile.TemporaryDirectory() as folder:

        # Generate key
        crypto.generate_keys(
            PASSWORD,
            folder
        )

        private_key = os.path.join(
            folder,
            "private_key.pem"
        )

        public_key = os.path.join(
            folder,
            "public_key.pem"
        )

        # Buat file aset dummy
        asset_file = os.path.join(
            folder,
            "asset_test.zip"
        )

        create_test_file(
            asset_file
        )

        results = []

        print("Mulai performance test...")

        for i in range(1, ITERATIONS + 1):

            # ==========================
            # SIGNING TEST
            # ==========================

            start = time.perf_counter()

            signature = crypto.sign_document(
                asset_file,
                private_key,
                PASSWORD
            )

            end = time.perf_counter()

            signing_time = (
                end - start
            )

            # ==========================
            # VERIFY TEST
            # ==========================

            start = time.perf_counter()

            result = crypto.verify_signature(
                asset_file,
                signature,
                public_key
            )

            end = time.perf_counter()

            verify_time = (
                end - start
            )

            results.append(
                {
                    "Percobaan": i,
                    "Signing Time (s)": signing_time,
                    "Verification Time (s)": verify_time,
                    "Signature Size (bytes)": len(signature),
                    "Public Key Size (bytes)": os.path.getsize(public_key),
                    "Verification Result": result
                }
            )

            print(
                f"Test {i}/30 selesai"
            )

        # ==========================
        # Simpan CSV
        # ==========================

        with open(
            "security_performance_result.csv",
            "w",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=results[0].keys()
            )

            writer.writeheader()

            writer.writerows(results)

        # ==========================
        # Statistik
        # ==========================

        avg_sign = sum(
            x["Signing Time (s)"]
            for x in results
        ) / ITERATIONS

        avg_verify = sum(
            x["Verification Time (s)"]
            for x in results
        ) / ITERATIONS

        print("\n===== HASIL =====")

        print(
            "Rata-rata Signing:",
            avg_sign,
            "detik"
        )

        print(
            "Rata-rata Verification:",
            avg_verify,
            "detik"
        )

        print(
            "Signature Size:",
            results[0]["Signature Size (bytes)"],
            "bytes"
        )

        print(
            "Public Key Size:",
            results[0]["Public Key Size (bytes)"],
            "bytes"
        )

        print(
            "\nFile hasil:"
            " security_performance_result.csv"
        )

if __name__ == "__main__":

    run_test()