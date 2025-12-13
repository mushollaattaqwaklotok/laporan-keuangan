# sistem-keuangan-attaqwa

Repo siap pakai untuk aplikasi Streamlit manajemen keuangan Musholla At-Taqwa.

## Struktur
```
/sistem-keuangan-attaqwa
  app.py
  /data
    keuangan.csv
    barang.csv
    log_aktivitas.csv
  /uploads
  .gitignore
  README.md
```

## Cara pakai (singkat)
1. Pastikan Python 3.8+ terinstall.
2. Install dependencies:
```
pip install streamlit pandas
```
3. Jalankan:
```
streamlit run app.py
```
4. Aplikasi akan berjalan di localhost, upload file bukti akan disimpan di folder `uploads/`.

## Warna tema
Tema default diatur ke warna *emas* (emas/krem). Untuk mengganti ke warna hijau NU, ubah CSS di bagian atas `app.py`.

## Catatan
- Pastikan folder `data/` dan `uploads/` memiliki izin tulis saat dideploy.
- Jika menggunakan Streamlit Cloud, gunakan external storage untuk menyimpan file jika ingin persistensi jangka panjang.
