import streamlit as st
import pandas as pd
from datetime import datetime

# ================================
# KONFIGURASI FILE CSV GITHUB
# ================================
KEUANGAN_URL = "https://raw.githubusercontent.com/mushollaattaqwaklotok/laporan-keuangan/refs/heads/main/data/keuangan.csv"
BARANG_URL   = "https://raw.githubusercontent.com/mushollaattaqwaklotok/laporan-keuangan/refs/heads/main/data/barang.csv"

# Username & Password sederhana
PANITIA_PASSWORD = "panitia123"
KETUA_PASSWORD   = "ketua123"
PUBLIK_PASSWORD  = "publik"

# ================================
# FUNGSI AMAN LOAD DATA CSV ONLINE
# ================================
@st.cache_data
def load_csv(url, columns):
    try:
        df = pd.read_csv(url)
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        return df
    except:
        return pd.DataFrame(columns=columns)

# Struktur final CSV
KEUANGAN_COLUMNS = ["Tanggal","Keterangan","Kategori","Masuk","Keluar","Saldo","bukti_url"]
BARANG_COLUMNS   = ["tanggal","jenis","keterangan","jumlah","satuan","bukti","bukti_penerimaan"]

# Load data
df_keu = load_csv(KEUANGAN_URL, KEUANGAN_COLUMNS)
df_bar = load_csv(BARANG_URL, BARANG_COLUMNS)

# ================================
# LOGIN
# ================================
st.title("📊 Sistem Keuangan Musholla At-Taqwa RT 1")

role = st.selectbox("Login sebagai:", ["Publik", "Panitia", "Ketua"])
pwd = st.text_input("Password:", type="password")

if role == "Publik":
    if pwd != PUBLIK_PASSWORD:
        st.warning("Masukkan password publik.")
        st.stop()
elif role == "Panitia":
    if pwd != PANITIA_PASSWORD:
        st.warning("Password salah untuk panitia.")
        st.stop()
elif role == "Ketua":
    if pwd != KETUA_PASSWORD:
        st.warning("Password salah untuk ketua.")
        st.stop()

st.success(f"Login sebagai {role}")

# ======================================================
# MENU NAVIGASI
# ======================================================
menu = st.sidebar.radio(
    "Menu",
    ["💰 Keuangan", "📦 Barang Masuk", "📄 Laporan", "🧾 Log"]
)

# ======================================================
# 1. KEUANGAN
# ======================================================
if menu == "💰 Keuangan":
    st.header("💰 Keuangan")

    st.subheader("Data Keuangan Saat Ini")
    st.dataframe(df_keu, use_container_width=True)

    if role == "Publik":
        st.info("Hanya panitia/ketua yang dapat input data.")
        st.stop()

    st.subheader("Input Data Keuangan")

    tgl = st.date_input("Tanggal", datetime.now())
    ket = st.text_input("Keterangan")
    kategori = st.selectbox("Kategori", ["Kas Masuk", "Kas Keluar"])
    masuk = st.number_input("Masuk (Rp)", min_value=0)
    keluar = st.number_input("Keluar (Rp)", min_value=0)

    bukti = st.file_uploader("Upload Bukti", type=["jpg","png","jpeg","pdf"], key="bukti_keu")

    if st.button("Simpan Keuangan"):
        new_row = {
            "Tanggal": str(tgl),
            "Keterangan": ket,
            "Kategori": kategori,
            "Masuk": masuk,
            "Keluar": keluar,
            "Saldo": "",
            "bukti_url": ""
        }

        st.warning("Mode ini hanya membaca CSV dari GitHub. Penyimpanan ke GitHub belum aktif.")
        st.json(new_row)

# ======================================================
# 2. BARANG
# ======================================================
elif menu == "📦 Barang Masuk":
    st.header("📦 Barang Masuk")

    st.subheader("Data Barang Masuk")
    st.dataframe(df_bar, use_container_width=True)

    if role == "Publik":
        st.info("Publik tidak dapat input data.")
        st.stop()

    st.subheader("Input Barang Masuk")

    tgl = st.date_input("Tanggal Barang", datetime.now())
    jenis = st.text_input("Jenis Barang")
    ket = st.text_input("Keterangan")
    jumlah = st.number_input("Jumlah", min_value=0.0)
    satuan = st.text_input("Satuan (bh, unit, box, dll)")

    bukti_b = st.file_uploader("Upload Bukti Pengambilan", type=["jpg","png","jpeg","pdf"], key="bukti_barang")
    bukti_p = st.file_uploader("Upload Bukti Penerimaan", type=["jpg","png","jpeg","pdf"], key="bukti_terima")

    if st.button("Simpan Barang"):
        new_row = {
            "tanggal": str(tgl),
            "jenis": jenis,
            "keterangan": ket,
            "jumlah": jumlah,
            "satuan": satuan,
            "bukti": "",
            "bukti_penerimaan": ""
        }

        st.warning("Mode ini hanya membaca CSV dari GitHub. Penyimpanan ke GitHub belum aktif.")
        st.json(new_row)

# ======================================================
# 3. LAPORAN
# ======================================================
elif menu == "📄 Laporan":
    st.header("📄 Laporan Lengkap")

    st.subheader("Keuangan")
    st.dataframe(df_keu)

    st.subheader("Barang Masuk")
    st.dataframe(df_bar)

# ======================================================
# 4. LOG
# ======================================================
elif menu == "🧾 Log":
    st.header("🧾 Log Aktivitas")

    st.info("Log belum aktif karena penyimpanan GitHub belum diaktifkan.")
