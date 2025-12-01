import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ======================================================
# KONFIGURASI UTAMA
# ======================================================
DATA_URL = "https://raw.githubusercontent.com/mushollaattaqwaklotok/laporan-keuangan/main/data/keuangan.csv"
BARANG_URL = "https://raw.githubusercontent.com/mushollaattaqwaklotok/laporan-keuangan/main/data/barang.csv"
LOG_URL = "https://raw.githubusercontent.com/mushollaattaqwaklotok/laporan-keuangan/main/data/log_aktivitas.csv"

LOCAL_DIR = "data"
BUKTI_DIR = "bukti"

os.makedirs(LOCAL_DIR, exist_ok=True)
os.makedirs(BUKTI_DIR, exist_ok=True)

KEUANGAN_CSV = f"{LOCAL_DIR}/keuangan.csv"
BARANG_CSV = f"{LOCAL_DIR}/barang.csv"
LOG_CSV = f"{LOCAL_DIR}/log_aktivitas.csv"


# ======================================================
# FUNGSI LOAD DATA
# ======================================================
def load_csv(url, local_path, columns):
    try:
        df = pd.read_csv(url)
    except:
        df = pd.DataFrame(columns=columns)
    df.to_csv(local_path, index=False)
    return df


keuangan = load_csv(DATA_URL, KEUANGAN_CSV, ["tanggal", "keterangan", "kategori", "jenis", "jumlah", "bukti"])
barang = load_csv(BARANG_URL, BARANG_CSV, ["tanggal", "nama_barang", "jumlah", "jenis", "keterangan"])
log = load_csv(LOG_URL, LOG_CSV, ["waktu", "aktivitas"])


# ======================================================
# TAMPILAN UTAMA
# ======================================================
st.title("📊 Laporan Keuangan Musholla At-Taqwa")

menu = st.sidebar.radio("Menu", ["Input Uang", "Input Barang", "Laporan Keuangan", "Laporan Barang", "Semua Bukti", "Download Laporan"])


# ======================================================
# INPUT UANG
# ======================================================
if menu == "Input Uang":
    st.header("🧾 Input Keuangan (Uang Masuk/Keluar)")

    tanggal = st.date_input("Tanggal")
    keterangan = st.text_input("Keterangan")
    kategori = st.selectbox("Kategori", ["Infak", "Pembangunan", "Operasional", "Lainnya"])
    jenis = st.radio("Jenis Transaksi", ["Masuk", "Keluar"])
    jumlah = st.number_input("Jumlah (Rp)", min_value=0)

    bukti_file = st.file_uploader("Upload Bukti (Foto/Nota)", type=["jpg", "jpeg", "png", "pdf"])

    if st.button("Simpan Data"):
        bukti_filename = ""

        # simpan bukti
        if bukti_file:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            ext = os.path.splitext(bukti_file.name)[1]
            bukti_filename = f"{timestamp}{ext}"
            with open(os.path.join(BUKTI_DIR, bukti_filename), "wb") as f:
                f.write(bukti_file.read())

        # simpan keuangan
        new_row = {
            "tanggal": tanggal,
            "keterangan": keterangan,
            "kategori": kategori,
            "jenis": jenis,
            "jumlah": jumlah,
            "bukti": bukti_filename
        }
        keuangan = pd.concat([keuangan, pd.DataFrame([new_row])], ignore_index=True)
        keuangan.to_csv(KEUANGAN_CSV, index=False)

        # simpan log
        log_entry = {
            "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "aktivitas": f"Input uang: {keterangan} ({jenis}) Rp{jumlah}"
        }
        log = pd.concat([log, pd.DataFrame([log_entry])], ignore_index=True)
        log.to_csv(LOG_CSV, index=False)

        st.success("Data keuangan berhasil disimpan!")



# ======================================================
# INPUT BARANG
# ======================================================
elif menu == "Input Barang":
    st.header("📦 Input Barang Masuk/Keluar")

    tgl = st.date_input("Tanggal")
    nama_barang = st.text_input("Nama Barang")
    jumlah_barang = st.number_input("Jumlah", min_value=1)
    jenis_barang = st.radio("Jenis Barang", ["Masuk", "Keluar"])
    ket_br = st.text_input("Keterangan")

    if st.button("Simpan Barang"):
        new_row = {
            "tanggal": tgl,
            "nama_barang": nama_barang,
            "jumlah": jumlah_barang,
            "jenis": jenis_barang,
            "keterangan": ket_br
        }

        barang = pd.concat([barang, pd.DataFrame([new_row])], ignore_index=True)
        barang.to_csv(BARANG_CSV, index=False)

        log_entry = {
            "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "aktivitas": f"Input barang: {nama_barang} ({jenis_barang}) x{jumlah_barang}"
        }
        log = pd.concat([log, pd.DataFrame([log_entry])], ignore_index=True)
        log.to_csv(LOG_CSV, index=False)

        st.success("Data barang berhasil disimpan!")



# ======================================================
# LAPORAN UANG
# ======================================================
elif menu == "Laporan Keuangan":
    st.header("📊 Laporan Keuangan")

    st.dataframe(keuangan)

    # preview bukti
    for idx, row in keuangan.iterrows():
        if row["bukti"] != "":
            st.image(f"{BUKTI_DIR}/{row['bukti']}", width=300, caption=row["keterangan"])



# ======================================================
# LAPORAN BARANG
# ======================================================
elif menu == "Laporan Barang":
    st.header("📦 Laporan Barang Masuk & Keluar")

    st.dataframe(barang)



# ======================================================
# SEMUA BUKTI
# ======================================================
elif menu == "Semua Bukti":
    st.header("📁 Semua Bukti Nota / Foto")

    bukti_files = os.listdir(BUKTI_DIR)

    for b in bukti_files:
        st.image(os.path.join(BUKTI_DIR, b), width=300)
        st.write(b)
        st.divider()



# ======================================================
# DOWNLOAD LAPORAN (3 file CSV)
# ======================================================
elif menu == "Download Laporan":
    st.header("⬇️ Download Semua Laporan (CSV Terpisah)")

    st.download_button("Download Keuangan (CSV)", keuangan.to_csv(index=False), "keuangan.csv")
    st.download_button("Download Barang (CSV)", barang.to_csv(index=False), "barang.csv")
    st.download_button("Download Log Aktivitas (CSV)", log.to_csv(index=False), "log_aktivitas.csv")



# ======================================================
# LOG AKTIVITAS — POSISI PALING BAWAH
# ======================================================
st.divider()
st.subheader("📝 Log Aktivitas Sistem")

st.dataframe(log)
