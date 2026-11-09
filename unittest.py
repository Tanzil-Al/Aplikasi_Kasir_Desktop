"""
Unit test sederhana untuk Admin Kasir App.
Jalankan dengan:  python unittest.py

Catatan:
File ini sengaja TIDAK meng-import modul `unittest` bawaan Python, karena
nama file `unittest.py` akan menimpa (shadow) modul standar tersebut sehingga
`import unittest` malah memuat file ini sendiri. Test dijalankan dengan runner
sederhana di bagian bawah file.
"""

# ============================================================
# BLOK: IMPORT
# ============================================================
import builtins
import os
import tempfile

from main import inputAngka
from model.calculator import totalPrice, countTax, countDiscount, countCashback
from model.receipt import formattedPrice, createReceipt, saveReceipt


# ============================================================
# BLOK: TEST UNTUK model/calculator.py
# ============================================================
class TestCalculator:
    """ Menguji semua fungsi perhitungan (harga, pajak, diskon, cashback). """

    def test_total_price(self):
        assert totalPrice(1000, 3) == 3000

    def test_total_price_zero_qty(self):
        assert totalPrice(1000, 0) == 0

    def test_tax_default_10_percent(self):
        assert countTax(1000) == 100

    def test_tax_custom_percent(self):
        assert countTax(1000, 5) == 50

    def test_tax_zero(self):
        assert countTax(0) == 0

    def test_discount(self):
        assert countDiscount(1000, 200) == 800

    def test_cashback_below_threshold(self):
        assert countCashback(999_999) == 0

    def test_cashback_at_threshold(self):
        assert countCashback(1_000_000) == 50_000

    def test_cashback_above_threshold(self):
        assert countCashback(2_000_000) == 100_000


# ============================================================
# BLOK: TEST UNTUK model/receipt.py
# ============================================================
class TestReceipt:
    """ Menguji format harga, isi struk, dan penyimpanan struk ke file. """

    def test_formatted_price(self):
        assert formattedPrice(1500) == "Rp 1500"
        assert formattedPrice(1500.6) == "Rp 1501"

    def test_create_receipt_content(self):
        # Struk tanpa pembayaran: baris Tunai/Kembalian tidak boleh muncul
        receipt = createReceipt(
            listBarang="Barang: Sabun (2x) - Rp 2000\n",
            subtotal=2000,
            totalPajak=200,
            cashback=0,
            hitungTotal=2200,
        )
        assert "SkincareinID" in receipt
        assert "Barang: Sabun (2x) - Rp 2000" in receipt
        assert "Total: Rp 2000" in receipt
        assert "Pajak: Rp 200" in receipt
        assert "Bayar: Rp 2200" in receipt
        assert "Tunai:" not in receipt
        assert "Kembalian:" not in receipt

    def test_create_receipt_with_payment(self):
        # Struk dengan pembayaran: baris Tunai & Kembalian harus muncul
        receipt = createReceipt(
            listBarang="Barang: Sabun (1x) - Rp 1000\n",
            subtotal=1000,
            totalPajak=100,
            cashback=0,
            hitungTotal=1100,
            uangTunai=5000,
            uangKembali=3900,
        )
        assert "Tunai: Rp 5000" in receipt
        assert "Kembalian: Rp 3900" in receipt

    def test_save_receipt(self):
        # Gunakan folder sementara agar tidak mengotori folder Struk-Belanja asli
        old_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            os.chdir(tmp)
            try:
                path = saveReceipt("isi struk", filename="struk_test.txt")
                assert os.path.exists(path)
                with open(path, "r", encoding="utf-8") as file:
                    assert file.read() == "isi struk"
            finally:
                os.chdir(old_cwd)


# ============================================================
# BLOK: TEST UNTUK main.py (validasi input angka)
# ============================================================
class TestMain:
    """ Menguji helper inputAngka agar aman dari input bukan angka. """

    def test_input_angka_valid(self):
        original = builtins.input
        answers = iter(["123"])
        builtins.input = lambda prompt="": next(answers)
        try:
            assert inputAngka("> ") == 123
        finally:
            builtins.input = original

    def test_input_angka_retry(self):
        # Input pertama salah ("abc"), lalu benar ("456")
        original = builtins.input
        answers = iter(["abc", "456"])
        builtins.input = lambda prompt="": next(answers)
        try:
            assert inputAngka("> ") == 456
        finally:
            builtins.input = original


# ============================================================
# BLOK: RUNNER SEDERHANA
# Menjalankan semua method yang namanya diawali "test_".
# ============================================================
def run_tests():
    test_classes = [TestCalculator, TestReceipt, TestMain]
    total = 0
    passed = 0
    failed = []

    for cls in test_classes:
        instance = cls()
        for name in sorted(dir(instance)):
            if not name.startswith("test_"):
                continue
            total += 1
            try:
                getattr(instance, name)()
            except Exception as error:  # noqa: BLE001
                failed.append((cls.__name__, name, error))
                print(f"FAIL  {cls.__name__}.{name} -> {error!r}")
            else:
                passed += 1
                print(f"OK    {cls.__name__}.{name}")

    print("-" * 50)
    print(f"Total: {total} | Lulus: {passed} | Gagal: {len(failed)}")
    return 1 if failed else 0


# Titik masuk: jalankan test hanya jika file ini dieksekusi langsung
if __name__ == "__main__":
    raise SystemExit(run_tests())
