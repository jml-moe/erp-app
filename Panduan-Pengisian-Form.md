# Panduan Lengkap Pengisian Form ERP

Dokumen ini berisi panduan lengkap untuk mengisi semua form di aplikasi ERP Coffe'O.

---

## 1. Form Product (Produk)

**Lokasi**: Manufacturing → Product → Create/Edit

### Field-field Form:

#### **Name** (Wajib)
- **Maksud**: Nama produk
- **Contoh**: "Espresso Blend Coffee", "Cappuccino Cup 250ml", "Coffee Bean Arabica"

#### **Internal Reference** (Opsional)
- **Maksud**: Kode internal/SKU produk. Jika dikosongkan, akan otomatis digenerate (format: PROD-00001, PROD-00002, dst.)
- **Contoh**: "PROD-00001", "COFFEE-001", "CUP-250"
- **Catatan**: Biarkan kosong untuk auto-generate

#### **Barcode** (Opsional)
- **Maksud**: Barcode produk (EAN, UPC, atau barcode internal)
- **Contoh**: "1234567890123", "8991234567890"

#### **Description** (Opsional)
- **Maksud**: Deskripsi detail produk
- **Contoh**: "Premium Arabica coffee beans from Java, medium roast, 1kg package"

#### **Category** (Opsional)
- **Maksud**: Kategori produk untuk pengelompokan
- **Contoh**: Pilih dari dropdown, misalnya "Coffee", "Equipment", "Packaging"
- **Catatan**: Buat kategori terlebih dahulu di Settings → Categories

#### **Product Type** (Wajib)
- **Maksud**: Tipe produk menentukan bagaimana produk dikelola
- **Pilihan**:
  - **Stockable**: Produk yang ditrack stoknya (barang fisik yang masuk gudang)
    - **Contoh**: Coffee beans, cups, packaging
    - **Kapan digunakan**: Untuk produk yang perlu dikelola stoknya
  - **Consumable**: Produk yang tidak ditrack stoknya (habis pakai)
    - **Contoh**: Cleaning supplies, office supplies
    - **Kapan digunakan**: Untuk produk yang langsung habis digunakan
  - **Service**: Jasa/layanan (tidak ada stok)
    - **Contoh**: Delivery fee, consulting service
    - **Kapan digunakan**: Untuk layanan yang dijual

#### **UOM (Unit of Measure)** (Wajib)
- **Maksud**: Satuan ukur default untuk produk (untuk stok dan penjualan)
- **Contoh**: Pilih dari dropdown, misalnya "Kilogram (kg)", "Piece (pcs)", "Liter (L)"
- **Catatan**: Buat UOM terlebih dahulu di Settings → Units of Measure

#### **Purchase UOM** (Opsional)
- **Maksud**: Satuan ukur saat pembelian (jika berbeda dengan UOM default)
- **Contoh**: Jika UOM default adalah "kg" tapi beli dalam "ton", pilih "Ton (T)"
- **Catatan**: Jika kosong, akan menggunakan UOM default

#### **Cost Method** (Wajib) ⭐
- **Maksud**: Metode perhitungan harga pokok (cost) produk
- **Pilihan**:
  - **Standard Price**: Menggunakan harga standar yang ditetapkan
    - **Penjelasan**: Harga pokok tetap sesuai `standard_price` yang diinput
    - **Kapan digunakan**: Untuk produk dengan harga stabil, mudah dihitung
    - **Contoh**: Produk dengan harga tetap seperti "Coffee Cup 250ml" dengan harga standar Rp 5.000
    - **Keuntungan**: Mudah dihitung, konsisten
    - **Kekurangan**: Tidak mengikuti fluktuasi harga pasar
  
  - **Average Cost**: Rata-rata harga dari semua pembelian
    - **Penjelasan**: Sistem menghitung rata-rata harga dari semua transaksi pembelian
    - **Kapan digunakan**: Untuk produk dengan harga berfluktuasi
    - **Contoh**: Coffee beans yang harganya berubah setiap pembelian
      - Pembelian 1: 100kg @ Rp 50.000/kg = Rp 5.000.000
      - Pembelian 2: 50kg @ Rp 55.000/kg = Rp 2.750.000
      - Average Cost = (5.000.000 + 2.750.000) / 150kg = Rp 51.667/kg
    - **Keuntungan**: Mengikuti tren harga pasar
    - **Kekurangan**: Perlu tracking semua transaksi
  
  - **FIFO (First In First Out)**: Barang masuk pertama, keluar pertama
    - **Penjelasan**: Harga pokok dihitung dari stok yang paling lama masuk
    - **Kapan digunakan**: Untuk produk yang memiliki expiry date atau produk yang perlu dirotasi
    - **Contoh**: Coffee beans dengan batch berbeda
      - Batch A (masuk 1 Jan): 100kg @ Rp 50.000/kg
      - Batch B (masuk 15 Jan): 50kg @ Rp 55.000/kg
      - Saat penjualan 30kg, harga pokok = Rp 50.000/kg (dari Batch A)
    - **Keuntungan**: Cocok untuk produk dengan expiry date
    - **Kekurangan**: Perlu tracking per batch

#### **Standard Price** (Wajib)
- **Maksud**: Harga pokok standar produk (cost price)
- **Contoh**: "50000" (untuk Rp 50.000)
- **Catatan**: Digunakan jika Cost Method = Standard Price

#### **List Price** (Wajib)
- **Maksud**: Harga jual standar produk (selling price)
- **Contoh**: "75000" (untuk Rp 75.000)
- **Catatan**: Harga ini akan muncul otomatis saat membuat Sales Order/Quotation

#### **Can Be Purchased** (Checkbox)
- **Maksud**: Centang jika produk ini dapat dibeli dari vendor
- **Contoh**: ✅ Centang untuk coffee beans, cups, dll
- **Catatan**: Jika tidak dicentang, produk tidak akan muncul di form Purchase Order

#### **Can Be Sold** (Checkbox)
- **Maksud**: Centang jika produk ini dapat dijual ke customer
- **Contoh**: ✅ Centang untuk semua produk yang dijual
- **Catatan**: Jika tidak dicentang, produk tidak akan muncul di form Sales Order

#### **Reorder Point** (Opsional)
- **Maksud**: Level stok minimum sebelum harus reorder (titik pemesanan ulang)
- **Contoh**: "100" (jika stok < 100, sistem akan alert untuk reorder)
- **Catatan**: Dalam satuan UOM produk

#### **Reorder Qty** (Opsional)
- **Maksud**: Jumlah default yang dipesan saat reorder
- **Contoh**: "500" (saat reorder, otomatis pesan 500 unit)
- **Catatan**: Dalam satuan UOM produk

#### **Is Active** (Checkbox)
- **Maksud**: Status aktif produk
- **Contoh**: ✅ Centang untuk produk yang masih aktif digunakan
- **Catatan**: Produk non-aktif tidak akan muncul di dropdown

---

## 2. Form Category (Kategori)

**Lokasi**: Settings → Categories → Create/Edit

#### **Name** (Wajib)
- **Maksud**: Nama kategori
- **Contoh**: "Coffee", "Equipment", "Packaging", "Beverages"

#### **Description** (Opsional)
- **Maksud**: Deskripsi kategori
- **Contoh**: "All coffee-related products including beans, ground coffee, and instant coffee"

#### **Parent** (Opsional)
- **Maksud**: Kategori induk (untuk membuat kategori hierarkis)
- **Contoh**: 
  - Kategori "Coffee" (parent: None)
  - Kategori "Arabica" (parent: Coffee)
  - Kategori "Robusta" (parent: Coffee)
- **Catatan**: Biarkan kosong untuk kategori utama

#### **Is Active** (Checkbox)
- **Maksud**: Status aktif kategori
- **Contoh**: ✅ Centang

---

## 3. Form Unit of Measure (Satuan Ukur)

**Lokasi**: Settings → Units of Measure → Create/Edit

#### **Name** (Wajib)
- **Maksud**: Nama satuan ukur
- **Contoh**: "Kilogram", "Gram", "Liter", "Piece", "Box"

#### **Symbol** (Wajib)
- **Maksud**: Simbol singkatan satuan
- **Contoh**: "kg", "g", "L", "pcs", "box"

#### **Category** (Wajib)
- **Maksud**: Kategori satuan ukur
- **Pilihan**:
  - **Unit**: Satuan unit (pcs, box, pack)
  - **Weight**: Satuan berat (kg, g, ton)
  - **Volume**: Satuan volume (L, mL)
  - **Length**: Satuan panjang (m, cm)
  - **Time**: Satuan waktu (hour, day)

#### **Ratio** (Wajib)
- **Maksud**: Rasio konversi ke satuan dasar dalam kategori yang sama
- **Contoh**: 
  - Jika "Kilogram" adalah base unit (ratio = 1.0)
  - "Gram" memiliki ratio = 0.001 (1 gram = 0.001 kg)
  - "Ton" memiliki ratio = 1000 (1 ton = 1000 kg)

#### **Is Base Unit** (Checkbox)
- **Maksud**: Centang jika ini adalah satuan dasar untuk kategorinya
- **Contoh**: ✅ Centang untuk "Kilogram" jika ini base unit untuk kategori Weight
- **Catatan**: Hanya satu base unit per kategori

#### **Is Active** (Checkbox)
- **Maksud**: Status aktif
- **Contoh**: ✅ Centang

---

## 4. Form Vendor (Supplier)

**Lokasi**: Buying → Vendor → Create/Edit

#### **Name** (Wajib)
- **Maksud**: Nama vendor/supplier
- **Contoh**: "PT Coffee Supplier Indonesia", "CV Biji Kopi Nusantara"

#### **Code** (Opsional)
- **Maksud**: Kode vendor. Auto-generate jika kosong (format: VND-0001)
- **Contoh**: "VND-0001", "SUP-001"

#### **Company Name** (Opsional)
- **Maksud**: Nama perusahaan legal
- **Contoh**: "PT Coffee Supplier Indonesia, Tbk"

#### **Email** (Opsional)
- **Maksud**: Email vendor
- **Contoh**: "contact@coffeesupplier.com"

#### **Phone** (Opsional)
- **Maksud**: Nomor telepon
- **Contoh**: "+62 21 12345678"

#### **Website** (Opsional)
- **Maksud**: Website vendor
- **Contoh**: "https://www.coffeesupplier.com"

#### **Street** (Opsional)
- **Maksud**: Alamat jalan
- **Contoh**: "Jl. Sudirman No. 123"

#### **Street2** (Opsional)
- **Maksud**: Alamat tambahan (apartment, suite, dll)
- **Contoh**: "Gedung ABC Lt. 5"

#### **City** (Opsional)
- **Maksud**: Kota
- **Contoh**: "Jakarta"

#### **State** (Opsional)
- **Maksud**: Provinsi
- **Contoh**: "DKI Jakarta"

#### **Zip Code** (Opsional)
- **Maksud**: Kode pos
- **Contoh**: "12190"

#### **Country** (Opsional)
- **Maksud**: Negara (default: Indonesia)
- **Contoh**: "Indonesia"

#### **Tax ID (NPWP)** (Opsional)
- **Maksud**: Nomor Pokok Wajib Pajak
- **Contoh**: "01.234.567.8-901.000"

#### **Payment Term** (Wajib)
- **Maksud**: Termin pembayaran
- **Pilihan**:
  - **Cash on Delivery (COD)**: Bayar saat barang diterima
  - **Net 7 Days**: Bayar dalam 7 hari setelah invoice
  - **Net 14 Days**: Bayar dalam 14 hari setelah invoice
  - **Net 30 Days**: Bayar dalam 30 hari setelah invoice (paling umum)
  - **Net 60 Days**: Bayar dalam 60 hari setelah invoice

#### **Rating** (Wajib)
- **Maksud**: Rating vendor (1-5)
- **Pilihan**: 1 (Poor) sampai 5 (Excellent)
- **Contoh**: Pilih "5 - Excellent" untuk vendor terpercaya

#### **Notes** (Opsional)
- **Maksud**: Catatan tambahan tentang vendor
- **Contoh**: "Vendor utama untuk coffee beans, delivery cepat"

#### **Is Active** (Checkbox)
- **Maksud**: Status aktif vendor
- **Contoh**: ✅ Centang

---

## 5. Form Customer (Pelanggan)

**Lokasi**: Selling → Customer → Create/Edit

#### **Name** (Wajib)
- **Maksud**: Nama customer
- **Contoh**: "John Doe", "PT Retail Coffee"

#### **Customer Type** (Wajib)
- **Maksud**: Tipe customer
- **Pilihan**:
  - **Individual**: Perorangan
  - **Company**: Perusahaan

#### **Email** (Opsional)
- **Maksud**: Email customer
- **Contoh**: "john@example.com"

#### **Phone** (Opsional)
- **Maksud**: Nomor telepon
- **Contoh**: "+62 812 3456 7890"

#### **Mobile** (Opsional)
- **Maksud**: Nomor handphone
- **Contoh**: "+62 812 3456 7890"

#### **Address** (Opsional)
- **Maksud**: Alamat lengkap
- **Contoh**: "Jl. Merdeka No. 45, Jakarta Pusat"

#### **City** (Opsional)
- **Maksud**: Kota
- **Contoh**: "Jakarta"

#### **Company Name** (Opsional)
- **Maksud**: Nama perusahaan (jika Customer Type = Company)
- **Contoh**: "PT Retail Coffee Indonesia"

#### **Tax ID (NPWP)** (Opsional)
- **Maksud**: Nomor Pokok Wajib Pajak
- **Contoh**: "01.234.567.8-901.000"

#### **Notes** (Opsional)
- **Maksud**: Catatan tentang customer
- **Contoh**: "Customer VIP, diskon 10%"

#### **Is Active** (Checkbox)
- **Maksud**: Status aktif
- **Contoh**: ✅ Centang

---

## 6. Form Request for Quotation (RFQ)

**Lokasi**: Buying → Request for Quotation → Create

#### **Vendor** (Wajib)
- **Maksud**: Vendor yang diminta quotation
- **Contoh**: Pilih dari dropdown vendor aktif

#### **Deadline** (Opsional)
- **Maksud**: Batas waktu vendor memberikan quotation
- **Contoh**: Pilih tanggal, misalnya "2024-12-31"

#### **Notes** (Opsional)
- **Maksud**: Catatan untuk vendor
- **Contoh**: "Mohon quotation untuk 100kg coffee beans"

**Setelah membuat RFQ, tambahkan line items:**
- **Product**: Pilih produk yang diminta quotation
- **Description**: Deskripsi (auto-filled dari product)
- **Quantity**: Jumlah yang diminta
- **Unit Price**: Harga per unit (diisi vendor saat memberikan quotation)

---

## 7. Form Purchase Order (PO)

**Lokasi**: Buying → Purchase Order → Create

#### **Vendor** (Wajib)
- **Maksud**: Vendor yang dipesan
- **Contoh**: Pilih dari dropdown vendor aktif

#### **Expected Date** (Opsional)
- **Maksud**: Tanggal diharapkan barang diterima
- **Contoh**: Pilih tanggal, misalnya "2024-12-15"

#### **Delivery Location** (Opsional)
- **Maksud**: Lokasi gudang tujuan penerimaan barang
- **Contoh**: Pilih dari dropdown location (internal location)

#### **Notes** (Opsional)
- **Maksud**: Catatan untuk PO
- **Contoh**: "Mohon kirim dengan packaging yang baik"

**Setelah membuat PO, tambahkan line items:**
- **Product**: Pilih produk yang dipesan
- **Description**: Deskripsi (auto-filled)
- **Quantity**: Jumlah yang dipesan
- **Unit Price**: Harga per unit dari vendor

---

## 8. Form Sales Quotation

**Lokasi**: Selling → Request for Quotation → Create

#### **Customer** (Wajib)
- **Maksud**: Customer yang diberikan quotation
- **Contoh**: Pilih dari dropdown customer aktif

#### **Validity Date** (Opsional)
- **Maksud**: Tanggal berlaku quotation (expiry date)
- **Contoh**: Pilih tanggal, misalnya "2024-12-31"

#### **Discount Amount** (Opsional)
- **Maksud**: Jumlah diskon total (dalam rupiah)
- **Contoh**: "100000" (untuk diskon Rp 100.000)

#### **Notes** (Opsional)
- **Maksud**: Catatan untuk quotation
- **Contoh**: "Harga berlaku sampai akhir tahun"

**Setelah membuat Quotation, tambahkan line items:**
- **Product**: Pilih produk yang ditawarkan
- **Description**: Deskripsi (auto-filled)
- **Quantity**: Jumlah yang ditawarkan
- **Unit Price**: Harga per unit
- **Discount Percent**: Persentase diskon per item (0-100)

---

## 9. Form Sales Order (SO)

**Lokasi**: Selling → Sales Order → Create

#### **Customer** (Wajib)
- **Maksud**: Customer yang memesan
- **Contoh**: Pilih dari dropdown customer aktif

#### **Expected Date** (Opsional)
- **Maksud**: Tanggal diharapkan pengiriman/pickup
- **Contoh**: Pilih tanggal, misalnya "2024-12-20"

#### **Source Location** (Opsional)
- **Maksud**: Lokasi gudang sumber untuk pengambilan barang
- **Contoh**: Pilih dari dropdown location (internal location)

#### **Discount Amount** (Opsional)
- **Maksud**: Jumlah diskon total (dalam rupiah)
- **Contoh**: "50000" (untuk diskon Rp 50.000)

#### **Notes** (Opsional)
- **Maksud**: Catatan untuk sales order
- **Contoh**: "Mohon packing dengan baik"

**Setelah membuat SO, tambahkan line items:**
- **Product**: Pilih produk yang dipesan
- **Description**: Deskripsi (auto-filled)
- **Quantity**: Jumlah yang dipesan
- **Unit Price**: Harga per unit
- **Discount Percent**: Persentase diskon per item (0-100)

---

## 10. Form Sales Invoice

**Lokasi**: Selling → Sales Invoice → Create

#### **Customer** (Wajib)
- **Maksud**: Customer yang diinvoice
- **Contoh**: Pilih dari dropdown customer aktif

#### **Sales Order** (Opsional)
- **Maksud**: Sales Order yang diinvoice (jika invoice dibuat dari SO)
- **Contoh**: Pilih dari dropdown sales order

#### **Due Date** (Opsional)
- **Maksud**: Tanggal jatuh tempo pembayaran
- **Contoh**: Pilih tanggal, misalnya "2024-12-30"

#### **Discount Amount** (Opsional)
- **Maksud**: Jumlah diskon total
- **Contoh**: "25000" (untuk diskon Rp 25.000)

#### **Notes** (Opsional)
- **Maksud**: Catatan untuk invoice
- **Contoh**: "Mohon transfer ke rekening BCA 1234567890"

**Setelah membuat Invoice, tambahkan line items:**
- **Product**: Pilih produk yang diinvoice
- **Description**: Deskripsi
- **Quantity**: Jumlah
- **Unit Price**: Harga per unit
- **Discount Percent**: Persentase diskon per item

**Form Pembayaran (Payment Form):**
- **Amount**: Jumlah yang dibayar
- **Payment Method**: Metode pembayaran (Cash, Bank Transfer, Credit Card, Debit Card, E-Wallet, QRIS)
- **Payment Reference**: Nomor referensi pembayaran (opsional)

---

## 11. Form Warehouse (Gudang)

**Lokasi**: Inventory → Warehouses → Create/Edit

#### **Name** (Wajib)
- **Maksud**: Nama gudang
- **Contoh**: "Gudang Utama Jakarta", "Gudang Bandung"

#### **Code** (Wajib)
- **Maksud**: Kode gudang (singkat)
- **Contoh**: "WH01", "WH-JKT", "WH-BDG"

#### **Address** (Opsional)
- **Maksud**: Alamat gudang
- **Contoh**: "Jl. Industri No. 123, Jakarta Utara"

#### **Is Active** (Checkbox)
- **Maksud**: Status aktif gudang
- **Contoh**: ✅ Centang

---

## 12. Form Location (Lokasi)

**Lokasi**: Inventory → Locations → Create/Edit

#### **Name** (Wajib)
- **Maksud**: Nama lokasi
- **Contoh**: "Rak A1", "Area Pendingin", "Lantai 2"

#### **Code** (Wajib)
- **Maksud**: Kode lokasi
- **Contoh**: "A1", "COLD-01", "L2-01"

#### **Warehouse** (Opsional)
- **Maksud**: Gudang tempat lokasi berada
- **Contoh**: Pilih dari dropdown warehouse

#### **Parent** (Opsional)
- **Maksud**: Lokasi induk (untuk struktur hierarkis)
- **Contoh**: 
  - Lokasi "Rak A" (parent: None)
  - Lokasi "Rak A1" (parent: Rak A)
  - Lokasi "Rak A2" (parent: Rak A)

#### **Location Type** (Wajib)
- **Maksud**: Tipe lokasi
- **Pilihan**:
  - **Internal Location**: Lokasi internal gudang (untuk stok)
  - **Supplier Location**: Lokasi supplier (untuk incoming goods)
  - **Customer Location**: Lokasi customer (untuk outgoing goods)
  - **Inventory Loss**: Lokasi untuk barang rusak/hilang
  - **Production**: Lokasi untuk produksi
  - **Transit Location**: Lokasi transit

#### **Is Default** (Checkbox)
- **Maksud**: Centang jika ini lokasi default untuk warehouse
- **Contoh**: ✅ Centang untuk lokasi utama

#### **Is Scrap** (Checkbox)
- **Maksud**: Centang jika ini lokasi untuk barang rusak/scrap
- **Contoh**: ✅ Centang untuk lokasi khusus scrap

#### **Is Active** (Checkbox)
- **Maksud**: Status aktif
- **Contoh**: ✅ Centang

---

## 13. Form Bill of Materials (BOM)

**Lokasi**: Manufacturing → Bill of Materials → Create/Edit

#### **Product** (Wajib)
- **Maksud**: Produk yang akan diproduksi (finished product)
- **Contoh**: Pilih produk yang `can_be_sold = True`, misalnya "Espresso Blend 1kg"

#### **Reference** (Opsional)
- **Maksud**: Referensi BOM. Auto-generate jika kosong
- **Contoh**: "BOM-ESPRESSO-001"

#### **Quantity** (Wajib)
- **Maksud**: Jumlah produk yang dihasilkan dari BOM ini
- **Contoh**: "1" (1kg espresso blend), "100" (100 cup cappuccino)

#### **BOM Type** (Wajib)
- **Maksud**: Tipe BOM
- **Pilihan**:
  - **Manufacture this product**: BOM untuk memproduksi produk (normal)
  - **Kit / Package**: BOM untuk packaging/kit (gabungan beberapa produk)

#### **Ready Time** (Wajib)
- **Maksud**: Waktu produksi dalam menit
- **Contoh**: "60" (1 jam), "120" (2 jam), "30" (30 menit)

#### **Is Active** (Checkbox)
- **Maksud**: Status aktif BOM
- **Contoh**: ✅ Centang

#### **Notes** (Opsional)
- **Maksud**: Catatan tentang BOM
- **Contoh**: "Resep standar untuk espresso blend premium"

**Setelah membuat BOM, tambahkan BOM Lines (komponen):**
- **Product**: Pilih produk komponen (raw material)
- **Quantity**: Jumlah komponen yang dibutuhkan
- **UOM**: Satuan ukur (opsional, default dari product)
- **Notes**: Catatan untuk komponen

**Contoh BOM:**
- **Product**: Espresso Blend 1kg
- **Komponen**:
  - Arabica Coffee Beans: 0.7 kg
  - Robusta Coffee Beans: 0.3 kg
  - Packaging Bag: 1 pcs

---

## 14. Form Manufacturing Order (MO)

**Lokasi**: Manufacturing → Manufacturing Order → Create/Edit

#### **Product** (Wajib)
- **Maksud**: Produk yang akan diproduksi
- **Contoh**: Pilih produk yang `can_be_sold = True`

#### **BOM** (Opsional)
- **Maksud**: Bill of Materials yang digunakan
- **Contoh**: Pilih BOM yang sesuai dengan product
- **Catatan**: Jika kosong, bisa input manual komponen

#### **Quantity** (Wajib)
- **Maksud**: Jumlah produk yang akan diproduksi
- **Contoh**: "100" (produksi 100 unit)

#### **Source Location** (Opsional)
- **Maksud**: Lokasi sumber untuk mengambil komponen/raw materials
- **Contoh**: Pilih internal location yang menyimpan raw materials

#### **Destination Location** (Opsional)
- **Maksud**: Lokasi tujuan untuk menyimpan produk jadi
- **Contoh**: Pilih internal location untuk finished goods

#### **Scheduled Date** (Opsional)
- **Maksud**: Tanggal dan waktu terjadwal untuk produksi
- **Contoh**: "2024-12-15 08:00"

#### **Priority** (Wajib)
- **Maksud**: Prioritas produksi
- **Pilihan**:
  - **Not Urgent**: Tidak urgent
  - **Normal**: Normal (default)
  - **Urgent**: Urgent
  - **Very Urgent**: Sangat urgent

#### **Origin** (Opsional)
- **Maksud**: Referensi dokumen sumber (misalnya dari Sales Order)
- **Contoh**: "SO-00001", "ORDER-123"

#### **Notes** (Opsional)
- **Maksud**: Catatan untuk manufacturing order
- **Contoh**: "Produksi untuk order customer VIP"

---

## 15. Form Employee (Karyawan)

**Lokasi**: HR → Employees → Create/Edit

#### **Actor** (Opsional)
- **Maksud**: Link ke user account (untuk login sistem)
- **Contoh**: Pilih dari dropdown user yang belum punya employee profile

#### **Full Name** (Wajib)
- **Maksud**: Nama lengkap karyawan
- **Contoh**: "Ahmad Fauzi", "Siti Nurhaliza"

#### **Date of Birth** (Wajib)
- **Maksud**: Tanggal lahir
- **Contoh**: Pilih tanggal, misalnya "1990-01-15"

#### **Email** (Opsional)
- **Maksud**: Email karyawan
- **Contoh**: "ahmad@coffeeo.com"

#### **Phone** (Opsional)
- **Maksud**: Nomor telepon
- **Contoh**: "+62 812 3456 7890"

#### **Street** (Opsional)
- **Maksud**: Alamat jalan
- **Contoh**: "Jl. Merdeka No. 45"

#### **City** (Opsional)
- **Maksud**: Kota
- **Contoh**: "Jakarta"

#### **State** (Opsional)
- **Maksud**: Provinsi
- **Contoh**: "DKI Jakarta"

#### **Zip Code** (Opsional)
- **Maksud**: Kode pos
- **Contoh**: "10110"

#### **Country** (Opsional)
- **Maksud**: Negara (default: Indonesia)
- **Contoh**: "Indonesia"

#### **Job Title** (Wajib)
- **Maksud**: Jabatan
- **Contoh**: "Manager", "Staff Produksi", "Kasir"

#### **Department** (Wajib)
- **Maksud**: Departemen
- **Pilihan**:
  - Human Resources
  - Finance & Accounting
  - Information Technology
  - Sales & Marketing
  - Operations
  - Manufacturing
  - Purchasing
  - Warehouse
  - General

#### **Employment Type** (Wajib)
- **Maksud**: Tipe pekerjaan
- **Pilihan**:
  - **Full Time**: Pekerja penuh waktu
  - **Part Time**: Pekerja paruh waktu
  - **Contract**: Kontrak
  - **Intern**: Magang

#### **Start Date** (Wajib)
- **Maksud**: Tanggal mulai bekerja
- **Contoh**: Pilih tanggal, misalnya "2024-01-01"

#### **End Date** (Opsional)
- **Maksud**: Tanggal berakhir bekerja (untuk kontrak/resign)
- **Contoh**: Pilih tanggal jika ada

#### **Salary** (Wajib)
- **Maksud**: Gaji bulanan
- **Contoh**: "5000000" (untuk Rp 5.000.000)

#### **Is Active** (Checkbox)
- **Maksud**: Status aktif karyawan
- **Contoh**: ✅ Centang

#### **Notes** (Opsional)
- **Maksud**: Catatan tentang karyawan
- **Contoh**: "Karyawan teladan bulan ini"

---

## 16. Form Payroll

**Lokasi**: HR → Payroll → Create/Edit

#### **Employee** (Wajib)
- **Maksud**: Karyawan yang di-payroll
- **Contoh**: Pilih dari dropdown employee aktif

#### **Month** (Wajib)
- **Maksud**: Bulan payroll (pilih tanggal di bulan tersebut)
- **Contoh**: Pilih "2024-12-01" untuk payroll Desember 2024

#### **Gross Salary** (Wajib)
- **Maksud**: Gaji kotor (sebelum potongan)
- **Contoh**: "5000000" (untuk Rp 5.000.000)
- **Catatan**: Auto-filled dari employee.salary jika kosong

#### **Tax Deduction** (Wajib)
- **Maksud**: Potongan pajak
- **Contoh**: "500000" (untuk Rp 500.000)

#### **Insurance Deduction** (Wajib)
- **Maksud**: Potongan asuransi (BPJS, dll)
- **Contoh**: "200000" (untuk Rp 200.000)

#### **Other Deduction** (Wajib)
- **Maksud**: Potongan lainnya
- **Contoh**: "100000" (untuk Rp 100.000)

#### **Net Pay** (Otomatis)
- **Maksud**: Gaji bersih (dihitung otomatis)
- **Rumus**: Gross Salary - (Tax + Insurance + Other Deduction)
- **Contoh**: 5.000.000 - (500.000 + 200.000 + 100.000) = 4.200.000

#### **Status** (Wajib)
- **Maksud**: Status payroll
- **Pilihan**:
  - **Draft**: Draft
  - **Pending**: Pending
  - **Processing**: Sedang diproses
  - **Paid**: Sudah dibayar
  - **Cancelled**: Dibatalkan

#### **Payment Date** (Opsional)
- **Maksud**: Tanggal pembayaran (auto-filled saat status = Paid)
- **Contoh**: Pilih tanggal pembayaran

#### **Notes** (Opsional)
- **Maksud**: Catatan payroll
- **Contoh**: "Bonus akhir tahun included"

---

## Tips Pengisian Form

1. **Field Wajib**: Pastikan semua field wajib diisi sebelum submit
2. **Auto-generate**: Field seperti `internal_reference`, `code` akan auto-generate jika dikosongkan
3. **Dropdown**: Pastikan data master (Category, UOM, Vendor, dll) sudah dibuat terlebih dahulu
4. **Decimal**: Gunakan titik (.) untuk desimal, contoh: "50.5" bukan "50,5"
5. **Date**: Format tanggal: YYYY-MM-DD (contoh: 2024-12-15)
6. **Checkbox**: Centang untuk aktif/true, kosongkan untuk non-aktif/false
7. **Cost Method**: Pilih sesuai kebutuhan bisnis:
   - Standard: Harga stabil
   - Average: Harga berfluktuasi
   - FIFO: Ada expiry date/batch
8. **Product Type**: 
   - Stockable: Barang fisik yang ditrack stok
   - Consumable: Barang habis pakai
   - Service: Jasa/layanan

---

## Contoh Skenario Lengkap

### Skenario 1: Membuat Produk Coffee Beans

1. **Buat Category** (jika belum ada):
   - Name: "Coffee"
   - Description: "Coffee products"
   - Parent: (kosongkan)
   - Is Active: ✅

2. **Buat UOM** (jika belum ada):
   - Name: "Kilogram"
   - Symbol: "kg"
   - Category: Weight
   - Ratio: 1.0
   - Is Base Unit: ✅

3. **Buat Product**:
   - Name: "Arabica Coffee Beans Premium"
   - Internal Reference: (kosongkan, auto-generate)
   - Barcode: "8991234567890"
   - Description: "Premium Arabica coffee beans from Java, medium roast"
   - Category: Coffee
   - Product Type: Stockable
   - UOM: Kilogram (kg)
   - Purchase UOM: (kosongkan)
   - Cost Method: Average Cost
   - Standard Price: 50000
   - List Price: 75000
   - Can Be Purchased: ✅
   - Can Be Sold: ✅
   - Reorder Point: 100
   - Reorder Qty: 500
   - Is Active: ✅

### Skenario 2: Membuat Purchase Order

1. **Buat Vendor** (jika belum ada):
   - Name: "PT Coffee Supplier"
   - Code: (auto-generate)
   - Payment Term: Net 30 Days
   - Rating: 5 - Excellent
   - Is Active: ✅

2. **Buat Purchase Order**:
   - Vendor: PT Coffee Supplier
   - Expected Date: 2024-12-20
   - Delivery Location: Gudang Utama / Lokasi A1
   - Notes: "Mohon kirim dengan packaging yang baik"

3. **Tambah Line Items**:
   - Product: Arabica Coffee Beans Premium
   - Quantity: 500
   - Unit Price: 50000

### Skenario 3: Membuat BOM untuk Espresso Blend

1. **Buat BOM**:
   - Product: Espresso Blend 1kg
   - Quantity: 1
   - BOM Type: Manufacture this product
   - Ready Time: 60 (menit)

2. **Tambah BOM Lines**:
   - Line 1:
     - Product: Arabica Coffee Beans Premium
     - Quantity: 0.7
     - UOM: kg
   - Line 2:
     - Product: Robusta Coffee Beans
     - Quantity: 0.3
     - UOM: kg
   - Line 3:
     - Product: Packaging Bag 1kg
     - Quantity: 1
     - UOM: pcs

---

## 17. Form Vendor Contact (Kontak Vendor)

**Lokasi**: Buying → Vendor → Detail → Tambah Contact

#### **Name** (Wajib)
- **Maksud**: Nama kontak vendor
- **Contoh**: "Budi Santoso", "Siti Nurhaliza"

#### **Title** (Opsional)
- **Maksud**: Jabatan kontak
- **Contoh**: "Sales Manager", "Procurement Officer"

#### **Email** (Opsional)
- **Maksud**: Email kontak
- **Contoh**: "budi@coffeesupplier.com"

#### **Phone** (Opsional)
- **Maksud**: Nomor telepon
- **Contoh**: "+62 21 12345678"

#### **Mobile** (Opsional)
- **Maksud**: Nomor handphone
- **Contoh**: "+62 812 3456 7890"

#### **Is Primary** (Checkbox)
- **Maksud**: Centang jika ini kontak utama vendor
- **Contoh**: ✅ Centang untuk kontak utama
- **Catatan**: Hanya satu kontak utama per vendor

#### **Notes** (Opsional)
- **Maksud**: Catatan tentang kontak
- **Contoh**: "Kontak untuk urgent order"

---

## 18. Form Vendor Product (Produk Vendor)

**Lokasi**: Buying → Vendor → Detail → Tambah Product

#### **Product** (Wajib)
- **Maksud**: Produk yang disediakan vendor
- **Contoh**: Pilih dari dropdown produk yang `can_be_purchased = True`

#### **Vendor Product Code** (Opsional)
- **Maksud**: Kode produk sesuai vendor
- **Contoh**: "SUP-001", "ABC-123"

#### **Vendor Product Name** (Opsional)
- **Maksud**: Nama produk sesuai vendor
- **Contoh**: "Premium Arabica Beans"

#### **Price** (Wajib)
- **Maksud**: Harga dari vendor ini
- **Contoh**: "50000" (untuk Rp 50.000)

#### **Currency** (Wajib)
- **Maksud**: Mata uang
- **Contoh**: "IDR" (default)

#### **Min Qty** (Wajib)
- **Maksud**: Minimum order quantity
- **Contoh**: "100" (minimum order 100 unit)

#### **Lead Time Days** (Wajib)
- **Maksud**: Waktu pengiriman dalam hari
- **Contoh**: "7" (7 hari), "14" (14 hari)

#### **Is Preferred** (Checkbox)
- **Maksud**: Centang jika ini vendor preferred untuk produk ini
- **Contoh**: ✅ Centang
- **Catatan**: Hanya satu preferred vendor per produk

#### **Is Active** (Checkbox)
- **Maksud**: Status aktif
- **Contoh**: ✅ Centang

---

## 19. Form Stock Picking (Pengiriman/Penerimaan Barang)

**Lokasi**: Inventory → (via Purchase Order/Sales Order)

#### **Picking Type** (Wajib)
- **Maksud**: Tipe picking
- **Pilihan**:
  - **Receipt**: Penerimaan barang (dari vendor)
  - **Delivery**: Pengiriman barang (ke customer)
  - **Internal Transfer**: Transfer internal antar lokasi

#### **Location Source** (Opsional)
- **Maksud**: Lokasi sumber
- **Contoh**: Pilih dari dropdown location

#### **Location Destination** (Opsional)
- **Maksud**: Lokasi tujuan
- **Contoh**: Pilih dari dropdown location

#### **Scheduled Date** (Opsional)
- **Maksud**: Tanggal terjadwal
- **Contoh**: "2024-12-15 08:00"

#### **Origin** (Opsional)
- **Maksud**: Referensi dokumen sumber
- **Contoh**: "PO-00001", "SO-00001"

#### **Notes** (Opsional)
- **Maksud**: Catatan
- **Contoh**: "Mohon handle with care"

**Setelah membuat Stock Picking, tambahkan line items:**
- **Product**: Pilih produk
- **Quantity**: Jumlah yang dipindahkan

---

## 20. Form Stock Adjustment (Penyesuaian Stok)

**Lokasi**: Inventory → Stock Adjustments → Create

#### **Name** (Wajib)
- **Maksud**: Nama penyesuaian
- **Contoh**: "Monthly Inventory Count", "Stock Opname Desember 2024"

#### **Location** (Wajib)
- **Maksud**: Lokasi yang disesuaikan
- **Contoh**: Pilih internal location

#### **Notes** (Opsional)
- **Maksud**: Catatan
- **Contoh**: "Stock opname akhir bulan"

**Setelah membuat Stock Adjustment, tambahkan line items:**
- **Product**: Pilih produk yang dihitung ulang
- **Counted Qty**: Jumlah yang dihitung secara fisik
- **Catatan**: Sistem akan otomatis menghitung selisih (difference) dengan stok sistem

---

## 21. Form Receive Products (Penerimaan Barang dari PO)

**Lokasi**: Buying → Purchase Order → Detail → Receive

Form ini muncul otomatis saat menerima barang dari Purchase Order.

- **Field dinamis**: Setiap line PO yang belum diterima akan muncul sebagai field
- **Label**: Nama produk
- **Value**: Jumlah yang diterima (default: sisa yang belum diterima)
- **Contoh**: 
  - Arabica Coffee Beans: 500 (dari PO 500, sudah diterima 0)
  - Jika sudah diterima 300, field akan menampilkan 200 (sisa)

---

## 22. Form Convert RFQ to PO (Konversi RFQ ke PO)

**Lokasi**: Buying → Request for Quotation → Detail → Convert to PO

#### **Delivery Location** (Wajib)
- **Maksud**: Lokasi tujuan penerimaan barang
- **Contoh**: Pilih internal location

**Catatan**: Form ini akan membuat Purchase Order baru dari RFQ yang sudah diterima quotation dari vendor.

---

## 23. Form PO Billing (Tagihan Vendor)

**Lokasi**: Buying → Purchase Order → Detail → Mark Billed

#### **Bill Reference** (Wajib)
- **Maksud**: Nomor invoice/tagihan dari vendor
- **Contoh**: "INV-VENDOR-001", "BILL-2024-12-001"

#### **Bill Date** (Wajib)
- **Maksud**: Tanggal invoice vendor
- **Contoh**: Pilih tanggal, misalnya "2024-12-15"

#### **Bill Amount** (Wajib)
- **Maksud**: Jumlah yang ditagih vendor
- **Contoh**: "5500000" (untuk Rp 5.500.000)

---

## 24. Form PO Payment (Pembayaran ke Vendor)

**Lokasi**: Buying → Purchase Order → Detail → Record Payment

#### **Payment Date** (Wajib)
- **Maksud**: Tanggal pembayaran
- **Contoh**: Pilih tanggal, misalnya "2024-12-20"

#### **Payment Reference** (Opsional)
- **Maksud**: Nomor referensi pembayaran
- **Contoh**: "TRF-123456", "CHQ-001"

---

## 25. Form Produce (Pencatatan Produksi)

**Lokasi**: Manufacturing → Manufacturing Order → Detail → Produce

#### **Quantity** (Wajib)
- **Maksud**: Jumlah produk yang diproduksi
- **Contoh**: "100" (memproduksi 100 unit)
- **Catatan**: Tidak boleh melebihi quantity yang direncanakan di MO

**Catatan**: Form ini untuk mencatat hasil produksi. Sistem akan:
- Mengurangi stok komponen dari source location
- Menambah stok produk jadi ke destination location

---

## 26. Form Payment (Pembayaran Invoice)

**Lokasi**: Selling → Sales Invoice → Detail → Pay

#### **Amount** (Wajib)
- **Maksud**: Jumlah yang dibayar
- **Contoh**: "7500000" (untuk Rp 7.500.000)
- **Catatan**: Bisa partial payment (pembayaran sebagian)

#### **Payment Method** (Wajib)
- **Maksud**: Metode pembayaran
- **Pilihan**:
  - **Cash**: Tunai
  - **Bank Transfer**: Transfer bank
  - **Credit Card**: Kartu kredit
  - **Debit Card**: Kartu debit
  - **E-Wallet**: E-wallet (GoPay, OVO, dll)
  - **QRIS**: QRIS

#### **Payment Reference** (Opsional)
- **Maksud**: Nomor referensi pembayaran
- **Contoh**: "TRF-123456", "CHQ-001", "QRIS-789"

---

## Ringkasan Field-field Penting

### Cost Method (Metode Harga Pokok) ⭐

**Standard Price**:
- Harga pokok tetap sesuai standard_price
- Cocok: Produk dengan harga stabil
- Contoh: Cup, packaging dengan harga tetap

**Average Cost**:
- Rata-rata harga dari semua pembelian
- Cocok: Produk dengan harga berfluktuasi
- Contoh: Coffee beans yang harganya berubah-ubah
- Perhitungan: (Total pembelian) / (Total quantity)

**FIFO (First In First Out)**:
- Barang masuk pertama, keluar pertama
- Cocok: Produk dengan expiry date atau batch
- Contoh: Coffee beans dengan batch berbeda
- Perhitungan: Harga dari batch paling lama

### Product Type (Tipe Produk)

**Stockable**: 
- Ditrack stoknya
- Contoh: Coffee beans, cups, equipment

**Consumable**:
- Tidak ditrack stok
- Contoh: Cleaning supplies, office supplies

**Service**:
- Jasa/layanan
- Contoh: Delivery fee, consulting

### Payment Terms (Termin Pembayaran)

**COD (Cash on Delivery)**: Bayar saat terima barang
**Net 7/14/30/60 Days**: Bayar dalam X hari setelah invoice

---

## Checklist Sebelum Mengisi Form

### Untuk Form Product:
- [ ] Category sudah dibuat
- [ ] UOM sudah dibuat
- [ ] Tentukan Product Type (Stockable/Consumable/Service)
- [ ] Pilih Cost Method sesuai kebutuhan
- [ ] Isi Standard Price dan List Price
- [ ] Centang Can Be Purchased jika bisa dibeli
- [ ] Centang Can Be Sold jika bisa dijual

### Untuk Form Purchase Order:
- [ ] Vendor sudah dibuat dan aktif
- [ ] Product sudah dibuat dan `can_be_purchased = True`
- [ ] Location sudah dibuat untuk delivery

### Untuk Form Sales Order:
- [ ] Customer sudah dibuat dan aktif
- [ ] Product sudah dibuat dan `can_be_sold = True`
- [ ] Location sudah dibuat untuk source

### Untuk Form BOM:
- [ ] Product finished goods sudah dibuat
- [ ] Product komponen (raw materials) sudah dibuat
- [ ] UOM untuk komponen sudah dibuat

### Untuk Form Manufacturing Order:
- [ ] BOM sudah dibuat untuk product
- [ ] Source location sudah dibuat (untuk raw materials)
- [ ] Destination location sudah dibuat (untuk finished goods)

---

**Catatan**: Dokumen ini akan terus diupdate sesuai perkembangan aplikasi.

**Versi**: 1.0
**Terakhir Update**: Desember 2024

