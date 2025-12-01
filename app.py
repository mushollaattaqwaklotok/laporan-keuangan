import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ======================================================
#  KONFIGURASI
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
def load_csv(url, expected_cols):
    try:
        df = pd.read_csv(url)
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""
        return df
    except:
        return pd.DataFrame(columns=expected_cols)

df = load_csv(DATA_UANG, ["tanggal","keterangan","jenis","jumlah","bukti"])
df_barang = load_csv(DATA_BARANG, ["tanggal","nama_barang","jenis","jumlah","bukti"])

# ======================================================
# SAVE TO REPO
# ======================================================
def save_local(df, path):
    df.to_csv(path, index=False)

# ======================================================
# TAMPILAN UTAMA
# ======================================================
st.title("📊 Laporan Keuangan Musholla At-Taqwa RT 1 — Dusun Klotok")

menu = st.sidebar.radio("Menu", ["Input Uang", "Input Barang", "Laporan", "Log Aktivitas"])

# ======================================================
# INPUT UANG
# ======================================================
if menu == "Input Uang":
    st.subheader("➕ Input Data Keuangan")

    tgl = st.date_input("Tanggal")
    ket = st.text_input("Keterangan")
    jenis = st.selectbox("Jenis", ["Masuk", "Keluar"])
    jumlah = st.number_input("Jumlah (Rp)", min_value=0)

    bukti_file = st.file_uploader("Upload Bukti (Opsional)", type=["jpg","jpeg","png"])

    if st.button("Simpan"):
        bukti_name = ""
        if bukti_file:
            ext = bukti_file.name.split(".")[-1]
            bukti_name = f"uang_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
            with open(os.path.join(BUKTI_FOLDER, bukti_name), "wb") as f:
                f.write(bukti_file.getbuffer())

        df.loc[len(df)] = [tgl, ket, jenis, jumlah, bukti_name]
        save_local(df, "data/keuangan.csv")

        st.success("Data berhasil disimpan!")

# ======================================================
# INPUT BARANG
# ======================================================
elif menu == "Input Barang":
    st.subheader("📦 Input Data Barang")

    tgl = st.date_input("Tanggal")
    nama = st.text_input("Nama Barang")
    jenis = st.selectbox("Jenis Barang", ["Masuk", "Keluar"])
    jumlah = st.number_input("Jumlah", min_value=1)

    bukti_file = st.file_uploader("Upload Bukti (Opsional)", type=["jpg","jpeg","png"])

    if st.button("Simpan"):
        bukti_name = ""
        if bukti_file:
            ext = bukti_file.name.split(".")[-1]
            bukti_name = f"barang_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
            with open(os.path.join(BUKTI_FOLDER, bukti_name), "wb") as f:
                f.write(bukti_file.getbuffer())

        df_barang.loc[len[df_barang]] = [tgl, nama, jenis, jumlah, bukti_name]
        save_local(df_barang, "data/barang.csv")

        st.success("Data barang berhasil disimpan!")

# ======================================================
# LAPORAN
# ======================================================
elif menu == "Laporan":
    st.subheader("📄 Laporan Keuangan (Uang)")

    df_show = df.copy()
    df_show["preview_bukti"] = df_show["bukti"].apply(
        lambda x: f"![bukti](bukti/{x})" if x else "-"
    )

    st.write(df_show[["tanggal","keterangan","jenis","jumlah","preview_bukti"]])

    # ======================================================
    # TAMBAHAN PENTING: LAPORAN BARANG
    # ======================================================
    st.subheader("📦 Laporan Barang (Non-Uang)")

    df_barang_show = df_barang.copy()
    df_barang_show["preview_bukti"] = df_barang_show["bukti"].apply(
        lambda x: f"![bukti](bukti/{x})" if x else "-"
    )

    st.write(df_barang_show[["tanggal","nama_barang","jenis","jumlah","preview_bukti"]])

# ======================================================
# LOG AKTIVITAS
# ======================================================
elif menu == "Log Aktivitas":
    st.subheader("📝 Log Aktivitas")

    try:
        log_df = pd.read_csv(LOG_FILE)
        st.dataframe(log_df)
    except:
        st.info("Belum ada log aktivitas.")
