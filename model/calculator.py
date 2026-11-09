""" Model untuk perhitungan aplikasi kasir.
    Semua rumus perhitungan (harga, pajak, diskon, cashback) dikumpulkan di sini
    agar mudah diuji dan dipakai ulang oleh versi CLI maupun GUI.
"""

# ============================================================
# BLOK: HITUNG TOTAL BELANJA
# ============================================================
def totalPrice(harga, jumlah):
    """ Mengembalikan subtotal = harga satuan x jumlah barang. """
    return harga * jumlah


# ============================================================
# BLOK: HITUNG PAJAK
# ============================================================
def countTax(total, persen=10):  # default pajak 10%
    """ Mengembalikan nilai pajak dari total belanja.
        persen=10 berarti 10%, sehingga dibagi 100.
    """
    return total * (persen / 100)


# ============================================================
# BLOK: HITUNG DISKON
# ============================================================
def countDiscount(total, potongan):
    """ Mengembalikan total setelah dikurangi potongan/diskon. """
    return total - potongan


# ============================================================
# BLOK: HITUNG CASHBACK
# ============================================================
def countCashback(total, persen=5):
    """ Cashback 5% hanya diberikan jika total belanja minimal Rp 1.000.000.
        Di bawah nilai itu, cashback = 0.
    """
    if total >= 1000000:
        return total * (persen / 100)
    else:
        return 0
