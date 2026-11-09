""" Model cetak dan simpan resi/struk.
    Berisi helper format harga, pembuat teks struk, dan penyimpan ke file .txt.
"""

import datetime
import os


# ============================================================
# BLOK: HELPER TAMPILAN
# ============================================================
def printLine():
    """ Mencetak garis pemisah di terminal. """
    print("-" * 30)


def formattedPrice(nilai):
    """ Mengubah angka menjadi format Rupiah tanpa desimal, contoh: Rp 1500. """
    return f"Rp {nilai:.0f}"


def timeStampNow():
    """ Mengembalikan waktu sekarang dalam format 'YYYY-MM-DD HH:MM:SS'. """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# BLOK: MEMBUAT TEKS STRUK
# ============================================================
def createReceipt(listBarang, subtotal, totalPajak, cashback, hitungTotal,
                  namaToko="SkincareinID", uangTunai=None, uangKembali=None):
    """ Menyusun teks struk pembayaran.

        Parameter:
        - listBarang  : teks daftar barang yang dibeli
        - subtotal    : total sebelum pajak
        - totalPajak  : nilai pajak
        - cashback    : nilai cashback
        - hitungTotal : total yang harus dibayar
        - namaToko    : nama toko yang tampil di struk
        - uangTunai   : uang yang dibayarkan (opsional)
        - uangKembali : uang kembalian (opsional)
    """
    timeNow = timeStampNow()

    # Bagian atas struk: nama toko, waktu, daftar barang, dan ringkasan biaya
    textDisplay = (
        "-----------------------------\n"
        f"{namaToko}\n"
        f"{timeNow}\n"
        "-----------------------------\n"
        f"{listBarang}"
        "-----------------------------\n"
        f"Total: {formattedPrice(subtotal)}\n"
        f"Pajak: {formattedPrice(totalPajak)}\n"
        f"Cashback: {formattedPrice(cashback)}\n"
        "-----------------------------\n"
        f"Bayar: {formattedPrice(hitungTotal)}\n"
    )

    # Bagian bawah: hanya ditambahkan jika uang tunai & kembalian tersedia
    if uangTunai is not None and uangKembali is not None:
        textDisplay += (
            "-----------------------------\n"
            f"Tunai: {formattedPrice(uangTunai)}\n"
            f"Kembalian: {formattedPrice(uangKembali)}\n"
        )

    return textDisplay


# ============================================================
# BLOK: MENYIMPAN STRUK KE FILE
# ============================================================
def saveReceipt(dataReceipt, filename=None):
    """ Menyimpan teks struk ke folder 'Struk-Belanja'.
        Jika filename tidak diberikan, nama file dibuat otomatis dari waktu.
    """
    folderName = "Struk-Belanja"

    # Buat folder jika belum ada
    if not os.path.exists(folderName):
        os.makedirs(folderName)

    # Nama file default: struk_YYYYmmdd_HHMMSS.txt
    if filename is None:
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"struk_{now}.txt"

    filePath = os.path.join(folderName, filename)

    # Tulis teks struk ke file
    with open(filePath, "w", encoding="utf-8") as file:
        file.write(dataReceipt)

    print(f"Bill berhasil disimpan ke {filename}")
    return filePath
