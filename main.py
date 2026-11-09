# ============================================================
# main.py - Versi CLI (Command Line) aplikasi kasir
# Jalankan di terminal dengan:  python main.py
# ============================================================

# Import fungsi dari modul lokal (folder model/)
from model.calculator import totalPrice, countTax, countDiscount, countCashback
from model.receipt import printLine, formattedPrice, createReceipt, saveReceipt


def inputAngka(prompt):
    """ Membaca input user dan memastikan nilainya bilangan bulat.
        Jika user memasukkan selain angka, program meminta ulang (tidak crash).
    """
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Masukan harus berupa angka. Coba lagi.")


def main():
    """ Alur utama aplikasi kasir versi CLI. """
    print("SkincareinID")

    # Tempat semua barang yang dibeli (keranjang belanja)
    shoppingCart = []  # Default kosong

    # --------------------------------------------------------
    # BLOK 1: INPUT BARANG
    # Diulang terus sampai user mengetik 'selesai'.
    # --------------------------------------------------------
    while True:
        namaBarang = input("Masukan nama barang (atau ketik 'selesai'): ")
        if namaBarang.lower() == 'selesai':
            break

        inputHargaBarang = inputAngka("Masukan harga barang: ")
        inputJumlahBarang = inputAngka("Masukan jumlah barang: ")

        # Hitung subtotal barang (harga satuan x jumlah)
        subtotal = totalPrice(inputHargaBarang, inputJumlahBarang)

        # Simpan barang ke keranjang
        shoppingCart.append({
            "nama": namaBarang,
            "harga": inputHargaBarang,
            "jumlah": inputJumlahBarang,
            "subtotal": subtotal
        })
        print(f"-> {namaBarang} berhasil ditambahkan")

    # --------------------------------------------------------
    # BLOK 2: VALIDASI KERANJANG
    # Jika tidak ada barang yang dibeli, program berhenti.
    # --------------------------------------------------------
    if not shoppingCart:
        print("Tidak ada barang yang di beli")
        return

    # --------------------------------------------------------
    # BLOK 3: HITUNG TOTAL SELURUH BELANJA
    # Menjumlahkan semua subtotal dan menyusun daftar barang.
    # --------------------------------------------------------
    totalSubtotal = 0
    listDaftarBarang = ""

    for item in shoppingCart:
        totalSubtotal += item['subtotal']
        listDaftarBarang += f"Barang: {item['nama']} ({item['jumlah']}x) - {formattedPrice(item['subtotal'])}\n"

    # Hitung pajak & cashback dari total belanja
    totalPajak = countTax(totalSubtotal)      # pajak 10%
    cashback = countCashback(totalSubtotal)   # cashback 5% jika >= Rp 1.000.000
    totalAll = totalSubtotal + totalPajak - cashback

    # --------------------------------------------------------
    # BLOK 4: INPUT PEMBAYARAN & HITUNG KEMBALIAN
    # Diulang sampai uang yang dibayarkan cukup.
    # --------------------------------------------------------
    while True:
        uangTunai = inputAngka("Masukan uang tunai: ")
        if uangTunai >= totalAll:
            break
        print(f"Uang kurang {formattedPrice(totalAll - uangTunai)}, total bayar {formattedPrice(totalAll)}")

    uangKembali = uangTunai - totalAll

    # --------------------------------------------------------
    # BLOK 5: BUAT, CETAK, DAN SIMPAN STRUK
    # --------------------------------------------------------
    createBill = createReceipt(
        listDaftarBarang,
        totalSubtotal,
        totalPajak,
        cashback,
        totalAll,
        uangTunai=uangTunai,
        uangKembali=uangKembali,
    )
    printLine()
    print(createBill, end="")

    saveReceipt(createBill)


# Titik masuk program: main() hanya dijalankan jika file ini dieksekusi langsung
if __name__ == "__main__":
    main()
