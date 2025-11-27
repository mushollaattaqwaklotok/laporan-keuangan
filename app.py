import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================================
#   KONFIGURASI
# ================================
DATA_FILE = "data/keuangan.csv"
PANITIA_PASS = "kelas3ku"   # Password panitia (contoh)
PUBLIK_MODE = "PUBLIK"
PANITIA_MODE = "PANITIA"

# Buat folder data jika belum ada
os.makedirs("data", exist_ok=True)

# ================================
#   FUNGSI BACA & SIMPAN DATA
# ================================
def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["Tanggal", "Keterangan", "Masuk", "Keluar", "Saldo"])
        df.to_csv(DATA_FILE, index=False)
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)


# ================================
#   TEMA WARNA NU
# ================================
st.markdown("""
    <style>
        body { background-color: #ffffff; }
        .main { background-color: #ffffff; }
        .stApp { background-color: #ffffff; }
        h1, h2, h3 { color: #0b6e4f; font-weight: 800; }
        
        /* Tombol hijau */
        .stButton>button {
            background-color: #0b6e4f;
            color: white;
            font-weight: bold;
            border-radius: 6px;
            padding: 6px 16px;
        }
        .stButton>button:hover {
            background-color: #0d8a64;
            color: white;
        }

        /* Input border hijau */
        .stTextInput>div>div>input,
        .stNumberInput>div>div>input {
            border: 1px solid #0b6e4f !important;
        }
    </style>
""", unsafe_allow_html=True)


# ================================
#   MODE APLIKASI
# ================================
st.sidebar.header("📌 Pilih Mode")
mode = st.sidebar.radio("Mode Aplikasi", [PUBLIK_MODE, PANITIA_MODE])

# ================================
#   MODE PUBLIK
# ================================
if mode == PUBLIK_MODE:
    st.title("💒 Keuangan Musholla At-Taqwa RT 1 – Publik")

    df = load_data()

    if df.empty:
        st.info("Belum ada data keuangan.")
    else:
        st.subheader("📄 Tabel Keuangan")
        st.dataframe(df, use_container_width=True)

        # Tombol download CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Data CSV",
            csv,
            "keuangan_musholla.csv",
            "text/csv",
        )


# ================================
#   MODE PANITIA (LOGIN)
# ================================
else:
    st.title("🕌 Panel Panitia – Kelola Keuangan Musholla")

    password = st.sidebar.text_input("Password Panitia", type="password")

    if password != PANITIA_PASS:
        st.warning("Masukkan password panitia.")
        st.stop()

    st.success("Login berhasil ✔️")

    df = load_data()

    # ============================
    #  FORM INPUT
    # ============================
    st.subheader("➕ Tambah Data Baru")

    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal", datetime.now())
        keterangan = st.text_input("Keterangan")
    with col2:
        masuk = st.number_input("Uang Masuk", min_value=0, step=1000)
        keluar = st.number_input("Uang Keluar", min_value=0, step=1000)

    if st.button("Simpan Data"):
        saldo_akhir = df["Saldo"].iloc[-1] if not df.empty else 0
        saldo_baru = saldo_akhir + masuk - keluar

        new_row = {
            "Tanggal": str(tanggal),
            "Keterangan": keterangan,
            "Masuk": masuk,
            "Keluar": keluar,
            "Saldo": saldo_baru
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)
        st.success("Data berhasil disimpan!")


    # ============================
    #  TABEL
    # ============================
    st.subheader("📄 Tabel Keuangan")
    st.dataframe(df, use_container_width=True)

    # ============================
    #  HAPUS DATA
    # ============================
    st.subheader("🗑 Hapus Baris Data")

    if not df.empty:
        index_to_delete = st.number_input("Pilih nomor baris (0 - {}):".format(len(df)-1), min_value=0, max_value=len(df)-1, step=1)

        if st.button("Hapus Baris Ini"):
            df = df.drop(index_to_delete).reset_index(drop=True)
            save_data(df)
            st.success("Baris berhasil dihapus!")


    # ============================
    #  DOWNLOAD CSV
    # ============================
    st.subheader("⬇️ Download Data")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV",
        csv,
        "keuangan_musholla.csv",
        "text/csv",
    )
