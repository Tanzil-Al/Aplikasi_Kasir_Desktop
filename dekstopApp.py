# ============================================================
# BLOK: IMPORT LIBRARY
# ============================================================
import tkinter as tk                     # Library GUI Python
from tkinter import ttk, messagebox      # ttk = widget modern, messagebox = dialog
import os                                # Operasi file & folder (struk)
import re                                # Regular expression untuk bersihkan angka

# Import dari modul lokal (logika bisnis ada di folder model/)
from model.calculator import totalPrice, countTax, countCashback
from model.receipt import formattedPrice, createReceipt, saveReceipt, timeStampNow

# ============================================================
# BLOK: KELAS UTAMA APLIKASI GUI
# ============================================================
class DesktopApp:
    """ Kelas utama yang membangun seluruh tampilan dan logika aplikasi kasir. """

    def __init__(self, root):
        """ Inisialisasi jendela utama, state aplikasi, dan seluruh komponen UI. """
        # --- Konfigurasi jendela utama ---
        self.root = root
        self.root.title("Sistem Kasir - SkincareinID")
        self.root.geometry("980x680")
        self.root.minsize(850, 600)
        self.root.configure(bg="#f8fafc")

        # --- State / data aplikasi ---
        self.shoppingCart = []   # Daftar barang di keranjang
        self.totalSubtotal = 0   # Total sebelum pajak & cashback
        self.totalPajak = 0      # Nilai pajak
        self.cashback = 0        # Nilai cashback
        self.strukAkhir = None   # Teks struk terakhir
        self.fileStruk = None    # Path file struk terakhir

        # --- Membangun tampilan ---
        self._setup_style()          # Atur style tabel
        self._header_create()        # Header + jam realtime
        self._main_content_create()  # Area input, keranjang, ringkasan
        self._summary_update()       # Hitung & tampilkan ringkasan awal

    def _setup_style(self):
        """ Mengatur tema dan style tampilan tabel (Treeview). """
        style = ttk.Style()
        style.theme_use("clam")

        # Style untuk judul kolom tabel
        style.configure(
            "Treeview.Heading",
            font = ("Segoe UI", 10, "bold"),
            background = "#e2e8f0",
            foreground = "#1e293b",
            relief = "flat",
            padding = 6,
        )

        # Style untuk baris tabel
        style.configure(
            "Treeview",
            font = ("Segoe UI", 10),
            rowheight = 28,
            background = "#ffffff",
            fieldbackground = "#ffffff",
            foreground = "#1e293b"
        )

        # Warna saat baris tabel dipilih
        style.map(
            "Treeview",
            background = [("selected", "#3b82f6")],
            foreground = [("selected", "#ffffff")],
        )


    def _header_create(self):
        """ Membuat header aplikasi: judul toko dan jam realtime. """
        # Frame header berwarna biru tua di bagian atas
        frame_header = tk.Frame(self.root, bg="#1e3a8a", padx=20, pady=12)
        frame_header.pack(side=tk.TOP, fill=tk.X)

        # Judul aplikasi di kiri
        label_title = tk.Label(
            frame_header,
            text = "Sistem Kasir - SkincareinID",
            font = ("Segoe UI", 16, "bold"),
            bg = "#1e3a8a",
            fg = "#ffffff",
        )
        label_title.pack(side=tk.LEFT)

        # Label jam di kanan
        self.label_time = tk.Label(
            frame_header,
            text = timeStampNow(),
            font = ("Segoe UI", 10),
            bg = "#1e3a8a",
            fg = "#93c5fd",
        )
        self.label_time.pack(side=tk.RIGHT)

        # Mulai update jam setiap detik
        self._time_update()

    def _time_update(self):
        """ Memperbarui label jam setiap 1 detik. """
        self.label_time.config(text=timeStampNow())
        self.root.after(1000, self._time_update)

    def _main_content_create(self):
        """ Membangun area utama: kolom kiri (input & keranjang) dan
            kolom kanan (ringkasan pembayaran).
        """
        # Container utama, dibagi menjadi 2 kolom
        container = tk.Frame(self.root, bg="#f8fafc", padx=15, pady=12)
        container.pack(fill=tk.BOTH, expand=True)

        # Kolom kiri (lebar fleksibel): input barang + tabel keranjang
        left_coll = tk.Frame(container, bg="#f8fafc")
        left_coll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Kolom kanan (lebar tetap 340px): ringkasan & pembayaran
        right_coll = tk.Frame(container, bg="#f8fafc", width=340)
        right_coll.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_coll.pack_propagate(False)

        # ====================================================
        # BAGIAN KIRI - CARD INPUT BARANG
        # ====================================================
        # Card (kotak berjudul) untuk form input barang
        card_input = tk.LabelFrame(
            left_coll,
            text = "Input List Daftar Barang",
            font = ("Segoe UI", 11, "bold"),
            bg = "#ffffff",
            fg = "#1e293b",
            padx = 14,
            pady = 10,
            relief = tk.GROOVE,
        )
        card_input.pack(fill=tk.X, pady=(0, 10))

        # Baris 1: input nama barang
        row_1 = tk.Frame(card_input, bg="#ffffff")
        row_1.pack(fill=tk.X, pady=4)

        tk.Label(
            row_1,
            text = "Nama Barang",
            font = ("Segoe UI", 10),
            bg = "#ffffff",
            fg = "#475569",
            width = 12,
            anchor = "w",
        ).pack(side=tk.LEFT)
        self.input_nama = tk.Entry(row_1, font=("Segoe UI", 10))
        self.input_nama.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_nama.focus()

        # Baris 2: input harga satuan & jumlah (qty)
        row_2 = tk.Frame(card_input, bg="#ffffff")
        row_2.pack(fill=tk.X, pady=4)

        tk.Label(
            row_2,
            text = "Harga (Rp): ",
            font = ("Segoe UI", 10),
            bg = "#ffffff",
            fg = "#475569",
            width = 12,
            anchor = "w",
        ).pack(side=tk.LEFT)
        self.input_harga = ttk.Entry(row_2, font=("Segoe UI", 10), width=18)
        self.input_harga.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(
            row_2,
            text = "Jumlah (Qty): ",
            font = ("Segoe UI", 10),
            bg = "#ffffff",
            fg = "#475569",
        ).pack(side=tk.LEFT, padx=(0, 6))
        self.input_qty = ttk.Spinbox(
            row_2, from_=1, to=9999, font=("Segoe UI", 10), width=8
        )
        self.input_qty.set(1)
        self.input_qty.pack(side=tk.LEFT)

        # Baris 3: tombol tambah ke keranjang & tombol reset input
        row_3 = tk.Frame(card_input, bg="#ffffff")
        row_3.pack(fill=tk.X, pady=(8, 2))

        # Tombol untuk menambahkan barang ke keranjang
        btn_add = tk.Button(
            row_3,
            text = "Tambahkan ke Keranjang",
            font = ("Segoe UI", 10, "bold"),
            bg = "#2563eb",
            fg = "#ffffff",
            activebackground = "#1d4ed8",
            activeforeground = "#ffffff",
            relief = tk.FLAT,
            padx = 14,
            pady = 5,
            cursor = "hand2",
            command = self.tambah_barang,
        )
        btn_add.pack(side=tk.LEFT, padx=(0, 8))

        btn_clear_input = tk.Button(
            row_3,
            text = "Hapus input",
            font = ("Segoe UI", 9),
            bg = "#e2e8f0",
            fg = "#334155",
            relief = tk.FLAT,
            padx = 10,
            pady = 5,
            cursor = "hand2",
            command = self._clear_input_fields,
        )
        btn_clear_input.pack(side=tk.LEFT)

        # Shortcut keyboard: Enter memindahkan fokus ke field berikutnya,
        # dan Enter di field qty langsung menambahkan barang.
        self.input_nama.bind("<Return>", lambda e: self.input_harga.focus())
        self.input_harga.bind("<Return>", lambda e: self.input_qty.focus())
        self.input_qty.bind("<Return>", lambda e: self.tambah_barang())

        # ====================================================
        # BAGIAN KIRI - TABEL KERANJANG BELANJA
        # ====================================================
        shopcart_card = tk.LabelFrame(
            left_coll,
            text = "Keranjang Belanja",
            font = ("Segoe UI", 11, "bold"),
            bg = "#ffffff",
            fg = "#1e293b",
            padx = 10,
            pady = 8,
            relief = tk.GROOVE,
        )
        shopcart_card.pack(fill=tk.BOTH, expand=True)

        # Definisikan kolom tabel
        columns = ("no", "nama", "harga", "qty", "subtotal")
        self.tree = ttk.Treeview(
            shopcart_card, columns=columns, show="headings", selectmode="browse"
        )
        # Atur judul tiap kolom
        self.tree.heading("no", text="No")
        self.tree.heading("nama", text="Nama Barang")
        self.tree.heading("harga", text="Harga Satuan")
        self.tree.heading("qty", text="Qty")
        self.tree.heading("subtotal", text="Subtotal")

        # Atur lebar dan perataan tiap kolom
        self.tree.column("no", width=40, anchor="center")
        self.tree.column("nama", width=220, anchor="w")
        self.tree.column("harga", width=110, anchor="e")
        self.tree.column("qty", width=60, anchor="center")
        self.tree.column("subtotal", width=120, anchor="e")

        # Scrollbar vertikal untuk tabel
        scrollbar = ttk.Scrollbar(
            shopcart_card, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ====================================================
        # BAGIAN KIRI - TOMBOL AKSI TABEL
        # ====================================================
        btn_table_frame = tk.Frame(left_coll, bg="#f8fafc", pady=6)
        btn_table_frame.pack(fill=tk.X)

        # Tombol hapus barang yang dipilih di tabel
        delete_btn = tk.Button(
            btn_table_frame,
            text = "Hapus Terpilih",
            font = ("Segoe UI", 9),
            bg = "#fee2e2",
            fg = "#b91c1c",
            activebackground = "#fecaca",
            relief = tk.FLAT,
            padx = 10,
            pady = 4,
            cursor = "hand2",
            command = self.hapus_barang_terpilih,
        )
        delete_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Tombol kosongkan seluruh keranjang
        emptycart_btn = tk.Button(
            btn_table_frame,
            text = "Kosongkan keranjang",
            font = ("Segoe UI", 9),
            bg = "#f1f5f9",
            fg = "#64748b",
            relief = tk.FLAT,
            padx = 10,
            pady = 4,
            cursor = "hand2",
            command = self.kosongkan_keranjang,
        )
        emptycart_btn.pack(side=tk.LEFT)

        # ====================================================
        # BAGIAN KANAN - RINGKASAN PEMBAYARAN
        # ====================================================
        card_summary = tk.LabelFrame(
            right_coll,
            text = "Rincian Pembayaran",
            font = ("Segoe UI", 11, "bold"),
            bg = "#ffffff",
            fg = "#1e293b",
            padx = 14,
            pady = 12,
            relief = tk.GROOVE,
        )
        card_summary.pack(fill=tk.BOTH, expand=True)

        # Baris ringkasan: subtotal, pajak, dan cashback
        self._row_summary(card_summary, "Subtotal", "lbl_subtotal")
        self._row_summary(card_summary, "Pajak (10%)", "lbl_pajak")
        self._row_summary(
            card_summary, "Cashback (5%)", "lbl_cashback", val_color="#16a34a"
        )

        # Garis pemisah
        tk.Frame(card_summary, height=1, bg="#cbd5e1").pack(fill=tk.X, pady=(12, 12))

        # Label total akhir yang harus dibayar (huruf besar)
        self.lbl_total_akhir = tk.Label(
            card_summary,
            text = "Rp 0",
            font = ("Segoe UI", 18, "bold"),
            bg = "#ffffff",
            fg = "#1e3a8a",
            anchor = "w",
        )
        self.lbl_total_akhir.pack(fill=tk.X, pady=(0, 14))

        tk.Frame(card_summary, height=1, bg="#cbd5e1").pack(fill=tk.X, pady=(0, 12))

        # Label + input uang yang diterima dari pembeli
        tk.Label(
            card_summary,
            text = "Uang Diterima (Rp): ",
            font = ("Segoe UI", 10, "bold"),
            bg = "#ffffff",
            fg = "#1e293b",
            anchor = "w",
        ).pack(fill=tk.X, pady=(0,4))

        # Input uang bayar; kembalian dihitung otomatis setiap kali mengetik
        self.entry_bayar = ttk.Entry(card_summary, font=("Segoe UI", 11))
        self.entry_bayar.pack(fill=tk.X, pady=(0, 8))
        self.entry_bayar.bind("<KeyRelease>", self._on_bayar_change)
        self.entry_bayar.bind("<Return>", lambda e: self.proses_transaksi())

        # Baris kembalian (otomatis dari uang diterima - total)
        self._row_summary(
            card_summary, "Kembalian", "lbl_kembalian", val_color="#0284c7"
        )

        # Tombol untuk memproses pembayaran, menyimpan, dan mencetak struk
        btn_bayar = tk.Button(
            card_summary,
            text = "Bayar dan Cetak struk",
            font = ("Segoe UI", 11, "bold"),
            bg = "#16a34a",
            fg = "#ffffff",
            activebackground = "#15803d",
            activeforeground = "#ffffff",
            relief = tk.FLAT,
            pady = 10,
            cursor = "hand2",
            command = self.proses_transaksi,
        )
        btn_bayar.pack(fill=tk.X, pady=(16, 6))

        # Tombol untuk mereset keranjang dan memulai transaksi baru
        btn_transaksi_baru = tk.Button(
            card_summary,
            text = "Masukan Transaksi Baru",
            font = ("Segoe UI", 10),
            bg = "#f1f5f9",
            fg = "#334155",
            activebackground = "#e2e8f0",
            relief = tk.FLAT,
            pady = 6,
            cursor = "hand2",
            command = self.transaksi_baru,
        )
        btn_transaksi_baru.pack(fill=tk.X, pady=(0, 6))

        # Tombol untuk membuka preview struk terakhir
        self.btn_open_struk = tk.Button(
            card_summary,
            text = "Lihat Struk",
            font = ("Segoe UI", 9),
            bg = "#ffffff",
            fg = "#64748b",
            relief = tk.GROOVE,
            pady = 4,
            cursor = "hand2",
            command = self.open_struk_modalview,
        )
        self.btn_open_struk.pack(fill=tk.X)

    def _row_summary(self, parent, title, attr_name, val_color="#1e293b"):
        """ Membuat satu baris ringkasan (judul di kiri, nilai di kanan).
            Nilai disimpan sebagai atribut `attr_name` agar bisa diupdate nanti.
        """
        row = tk.Frame(parent, bg="#ffffff")
        row.pack(fill=tk.X, pady=3)

        tk.Label(
            row,
            text = title,
            font = ("Segoe UI", 10),
            bg="#ffffff",
            fg = "#64748b",
            anchor = "w",
        ).pack(side=tk.LEFT)

        lbl = tk.Label(
            row,
            text = "Rp 0",
            font = ("Segoe UI", 10, "bold")
        )
        lbl.pack(side=tk.RIGHT)
        setattr(self, attr_name, lbl)

    def _parse_angka(self, text):
        """ Mengubah teks (misal '1.500' atau '1,500') menjadi integer 1500.
            Karakter selain angka dibuang. Jika kosong, hasilnya 0.
        """
        clean = re.sub(r"[^\d]", "", str(text))
        return int(clean) if clean else 0

    def _clear_input_fields(self):
        """ Mengosongkan form input dan mengembalikan fokus ke nama barang. """
        self.input_nama.delete(0, tk.END)
        self.input_harga.delete(0, tk.END)
        self.input_qty.set(1)
        self.input_nama.focus()

    def tambah_barang(self):
        """ Membaca form input, memvalidasi, lalu menambah barang ke keranjang. """
        nama = self.input_nama.get().strip()
        harga_raw = self.input_harga.get().strip()
        qty_raw = self.input_qty.get().strip()

        # Validasi nama barang tidak boleh kosong
        if not nama:
            messagebox.showwarning("Peringatan", "Nama barang tidak boleh kosong")
            self.input_nama.focus()
            return

        # Validasi harga harus angka > 0
        try:
            harga = self._parse_angka(harga_raw)
            if harga <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Peringatan", "Harga harus berupa angka lebih besar dari 0")
            self.input_harga.focus()
            return

        # Validasi jumlah minimal 1
        try:
            qty = int(qty_raw)
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Peringatan", "Jumlah harus minimal 1")
            self.input_qty.focus()
            return

        # Hitung subtotal barang (harga x qty) memakai model calculator.py
        subtotal = totalPrice(harga, qty)

        # Jika barang dengan nama & harga sama sudah ada, cukup tambah qty-nya
        item_search = False
        for item in self.shoppingCart:
            if item["nama"].lower() == nama.lower() and item["harga"] == harga:
                item["jumlah"] += qty
                item["subtotal"] += subtotal
                item_search = True
                break

        # Jika belum ada, tambahkan sebagai baris baru di keranjang
        if not item_search:
            self.shoppingCart.append(
                {
                    "nama": nama,
                    "harga": harga,
                    "jumlah": qty,
                    "subtotal": subtotal,
                }
            )

        # Perbarui tampilan tabel & ringkasan, lalu kosongkan form
        self._refresh_table()
        self._summary_update()
        self._clear_input_fields()


    def hapus_barang_terpilih(self):
        """ Menghapus barang yang sedang dipilih di tabel keranjang. """
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Pilih barang yang anda ingin hapus dari keranjang")
            return

        item_idx = self.tree.index(selected[0])
        del self.shoppingCart[item_idx]

        self._refresh_table()
        self._summary_update()


    def kosongkan_keranjang(self):
        """ Mengosongkan seluruh isi keranjang setelah konfirmasi user. """
        if not self.shoppingCart:
            return

        confirm = messagebox.askyesno(
            "Konfirmasi",
            "Apakah anda ingin menghapus isi keranjang?",
        )

        if confirm:
            self.shoppingCart.clear()
            self._refresh_table()
            self._summary_update()

    def _refresh_table(self):
        """ Menampilkan ulang isi shoppingCart ke tabel Treeview. """
        # Bersihkan tabel Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Masukan ulang seluruh barang dari shoppingCart
        for i, item in enumerate(self.shoppingCart, start=1):
            self.tree.insert(
                "",
                tk.END,
                values=(
                    i,
                    item["nama"],
                    formattedPrice(item["harga"]),
                    item["jumlah"],
                    formattedPrice(item["subtotal"]),
                ),
            )

    def _summary_update(self):
        """ Menghitung ulang subtotal, pajak, cashback, dan total akhir,
            lalu memperbarui label di panel kanan.
        """
        # Jumlahkan subtotal seluruh barang
        self.totalSubtotal = sum(item["subtotal"] for item in self.shoppingCart)

        # Hitung pajak & cashback memakai model calculator
        self.totalPajak = countTax(self.totalSubtotal)
        self.cashback = countCashback(self.totalSubtotal)
        self.totalAll = self.totalSubtotal + self.totalPajak - self.cashback

        # Perbarui teks label ringkasan
        self.lbl_subtotal.config(text=formattedPrice(self.totalSubtotal))
        self.lbl_pajak.config(text=formattedPrice(self.totalPajak))
        self.lbl_cashback.config(text = f" - {formattedPrice(self.cashback)}" if self.cashback > 0 else "Rp 0")

        self.lbl_total_akhir.config(text=formattedPrice(self.totalAll))

        # Hitung ulang kembalian berdasarkan uang yang sudah diinput
        self._on_bayar_change()

    def _on_bayar_change(self, event=None):
        """ Dipanggil setiap kali isi kolom uang bayar berubah.
            Menampilkan kembalian (hijau) atau kekurangan (merah).
        """
        payment = self._parse_angka(self.entry_bayar.get())
        if payment > 0 and self.totalAll > 0:
            paymentChange = payment - self.totalAll
            if paymentChange >= 0:
                self.lbl_kembalian.config(
                    text = formattedPrice(paymentChange), fg="#16a34a"
                )
            else:
                self.lbl_kembalian.config(
                    text = f" Kurang {formattedPrice(abs(paymentChange))}", fg="#dc2626"
                )
        else:
            self.lbl_kembalian.config(text="Rp 0", fg="#0284c7")

    def proses_transaksi(self):
        """ Memvalidasi pembayaran, membuat struk, menyimpannya,
            lalu menampilkan preview struk.
        """
        # Pastikan keranjang tidak kosong
        if not self.shoppingCart:
            messagebox.showwarning("Keranjang kosong", "belum ada barang di dalam keranjang belanja")
            return

        # Ambil uang bayar dan pastikan cukup
        payment = self._parse_angka(self.entry_bayar.get())
        if payment < self.totalAll:
            kurang = self.totalAll - payment
            messagebox.showwarning(
                "Uang tidak cukup",
                f"Uang yang di bayarkan kurang {formattedPrice(kurang)}!\n"
                f"Total bayar: {formattedPrice(self.totalAll)}\n"
                f"Uang diterima: {formattedPrice(payment)}",
            )
            self.entry_bayar.focus()
            return

        # Hitung kembalian
        kembalian = payment - self.totalAll

        # Susun teks daftar barang sesuai format struk
        text_daftar_barang = ""
        for item in self.shoppingCart:
            text_daftar_barang += f"Barang: {item['nama']} ({item['jumlah']}x) - {formattedPrice(item['subtotal'])}\n"

        # Buat teks struk lengkap
        dataReceipt = createReceipt(
            listBarang = text_daftar_barang,
            subtotal = self.totalSubtotal,
            totalPajak = self.totalPajak,
            cashback = self.cashback,
            hitungTotal = self.totalAll,
            namaToko="SkincareinID",
            uangTunai = payment,
            uangKembali = kembalian,
        )

        # Simpan struk ke file .txt di folder Struk-Belanja
        filename = saveReceipt(dataReceipt)

        # Simpan referensi struk terakhir untuk tombol "Lihat Struk"
        self.strukAkhir = dataReceipt
        self.fileStruk = filename
        self.btn_open_struk.config(state=tk.NORMAL)

        # Tampilkan pop-up preview struk
        self.open_struk_modalview(
            success = f"Transaksi Berhasil! \n Struk telah disimpan ke: \n {filename}"
        )

    def open_struk_modalview(self, success=None):
        """ Menampilkan jendela pop-up berisi preview struk.
            `success` diisi pesan sukses setelah transaksi (opsional).
        """
        if not self.strukAkhir:
            return

        # Buat jendela modal (tidak bisa ditutup sebelum ditutup manual)
        modal = tk.Toplevel(self.root)
        modal.title("Struk pembayaran")
        modal.geometry("420x540")
        modal.transient(self.root)
        modal.grab_set()

        # Tampilkan banner sukses jika ada pesan
        if success:
            lbl_info = tk.Label(
                modal,
                text = "✅ " + success,
                font = ("Segoe UI", 9),
                bg = "#dcfce7",
                fg = "#166534",
                pady = 8,
                padx = 10,
                justify = tk.CENTER,
            )
            lbl_info.pack(fill=tk.X)

        # Kotak teks read-only untuk menampilkan isi struk
        text_box = tk.Text(
            modal,
            font=("Consolas", 10),
            bg="#fdfefe",
            fg="#0f172a",
            padx=15,
            pady=12,
            relief=tk.FLAT,
        )
        text_box.insert(tk.END, self.strukAkhir)
        text_box.config(state=tk.DISABLED)
        text_box.pack(fill=tk.BOTH, expand=True)

        # Tombol untuk menutup pop-up
        btn_close = tk.Button(
            modal,
            text="Tutup",
            font=("Segoe UI", 10, "bold"),
            bg="#1e3a8a",
            fg="#ffffff",
            relief=tk.FLAT,
            pady=6,
            command=modal.destroy,
        )
        btn_close.pack(fill=tk.X, padx=12, pady=8)

    def transaksi_baru(self):
        """ Mereset keranjang & form untuk memulai transaksi baru. """
        # Minta konfirmasi jika masih ada barang di keranjang
        if self.shoppingCart:
            ask = messagebox.askyesno(
                "Transaksi Baru",
                "Mulai transaksi baru? Keranjang dan input pembayaran saat ini akan direset.",
            )
            if not ask:
                return

        # Kosongkan semua state transaksi
        self.shoppingCart.clear()
        self._refresh_table()
        self.entry_bayar.delete(0, tk.END)
        self._clear_input_fields()
        self._summary_update()
        self.input_nama.focus()


# ============================================================
# BLOK: TITIK MASUK PROGRAM
# ============================================================
def main():
    """ Membuat jendela Tkinter dan menjalankan aplikasi. """
    root = tk.Tk()
    app = DesktopApp(root)
    root.mainloop()


# main() hanya dijalankan jika file ini dieksekusi langsung
if __name__ == "__main__":
    main()
