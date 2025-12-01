import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import StringIO

# ======================================================
#  KONFIGURASI UTAMA
# ======================================================
DATA_UANG = "https://raw.githubusercontent.com/mushollaattaqwaklotok/laporan-keuangan/main/data/keuangan.csv"
DATA_BARANG = "https://raw.githubusercontent.com/mushollaattaqwaklotok/laporan-keuangan/main/data/barang.csv"
LOG_FILE = "data/log_aktivitas.csv"

BUKTI_FOLDER = "bukti"
os.makedirs(BUKTI_FOLDER, exist_ok=True)

# ======================================================
# LOAD DATA
# ======================================================
@st.cache_data
def load_csv(url_or_path, columns=None):
    try:
        df = pd.read_csv(url_or_path)
        if columns:
            for c in columns:
                if c not in df.columns:
                    df[c] = ""
        return df
    except:
        return pd.DataFrame(columns=columns)

df = load_csv(DATA_UANG, ["tanggal","keterangan","jenis","jumlah","bukti"])
df_barang = load_csv(DATA_BARANG, ["tanggal","nama_barang","jenis","jumlah","bukti"])

# ======================================================
# SIMPAN KE GITHUB (RAW UPDATE)
# ======================================================
def save_to_repo(df, path):
    df.to_csv(path, index=False)

# ======================================================
# TAMPILAN APLIKASI
# ======================================================
st.title("📊 Laporan Keuangan Musholla At-Taqwa RT 1 — Dusun Klotok")

menu = st.sidebar.radio("Menu", ["Input Uang", "Input Barang", "Laporan", "Log Aktivitas"])

# ======================================================
# 1. INPUT UANG
# ======================================================
if menu == "Input Uang":
    st.subheader("➕ Input Pemasukan / Pengeluaran Uang")

    tanggal = st.date_input("Tanggal")
    keterangan = st.text_input("Keterangan")
    jenis = st.selectbox("Jenis", ["Masuk", "Keluar"])
    jumlah = st.number_input("Jumlah (Rp)", min_value=0)

    bukti_file = st.file_uploader("Upload Foto Nota (optional)", type=["jpg","png","jpeg"])

    if st.button("Simpan Data Uang"):
        bukti_name = ""
        if bukti_file:
            ext = bukti_file.name.split(".")[-1]
            bukti_name = f"uang_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
            with open(os.path.join(BUKTI_FOLDER, bukti_name), "wb") as f:
                f.write(bukti_file.getbuffer())

        new_row = {
            "tanggal": tanggal,
            "keterangan": keterangan,
            "jenis": jenis,
            "jumlah": jumlah,
            "bukti": bukti_name
        }

        df.loc[len(df)] = new_row
        save_to_repo(df, "data/keuangan.csv")

        st.success("Data uang berhasil disimpan!")

# ======================================================
# 2. INPUT BARANG
# ======================================================
elif menu == "Input Barang":
    st.subheader("📦 Input Data Barang (Non-Uang)")

    tanggal = st.date_input("Tanggal")
    nama_barang = st.text_input("Nama Barang")
    jenis = st.selectbox("Status Barang", ["Masuk", "Keluar"])
    jumlah = st.number_input("Jumlah", min_value=1)

    bukti_file = st.file_uploader("Upload Foto Bukti (opsional)", type=["jpg","png","jpeg"])

    if st.button("Simpan Data Barang"):
        bukti_name = ""
        if bukti_file:
            ext = bukti_file.name.split(".")[-1]
            bukti_name = f"barang_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
            with open(os.path.join(BUKTI_FOLDER, bukti_name), "wb") as f:
                f.write(bukti_file.getbuffer())

        new_row = {
            "tanggal": tanggal,
            "nama_barang": nama_barang,
            "jenis": jenis,
            "jumlah": jumlah,
            "bukti": bukti_name
        }

        df_barang.loc[len(df_barang)] = new_row
        save_to_repo(df_barang, "data/barang.csv")

        st.success("Data barang berhasil disimpan!")

# ======================================================
# 3. LAPORAN (TAMPILAN PUBLIK)
# ======================================================
elif menu == "Laporan":
    st.subheader("📄 Laporan Keuangan Uang")

    df_display = df.copy()
    df_display["preview"] = df_display["bukti"].apply(
        lambda x: f"![bukti](bukti/{x})" if x else "-"
    )

    st.write(df_display[["tanggal","keterangan","jenis","jumlah","preview"]])

    # ======================
    st.subheader("📦 Laporan Barang")

    df_barang_display = df_barang.copy()
    df_barang_display["preview"] = df_barang_display["bukti"].apply(
        lambda x: f"![bukti](bukti/{x})" if x else "-"
    )

    st.write(df_barang_display[["tanggal","nama_barang","jenis","jumlah","preview"]])

    # Button download semua CSV
    st.subheader("⬇️ Download Semua Data")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "Download Keuangan (CSV)",
            df.to_csv(index=False),
            "keuangan.csv",
            "text/csv"
        )

    with col2:
        st.download_button(
            "Download Barang (CSV)",
            df_barang.to_csv(index=False),
            "barang.csv",
            "text/csv"
        )

# ======================================================
# 4. LOG AKTIVITAS (PALING BAWAH)
# ======================================================
elif menu == "Log Aktivitas":
    st.subheader("📝 Log Aktivitas Sistem")

    try:
        log_df = pd.read_csv(LOG_FILE)
        st.dataframe(log_df)
    except:
        st.info("Belum ada log aktivitas.")

