import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =========================
# CONFIG APLIKASI
# =========================
st.set_page_config(
    page_title="Aplikasi Keuangan Musholla At Taqwa",
    layout="wide"
)

ADMIN_USER = "admin"
ADMIN_PASS = "musholla123"

DATA_FOLDER = "data"

# =========================
# FUNGSI MEMUAT DATA
# =========================
def load_csv(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()

    df = pd.read_csv(file_path)

    # Normalisasi nama kolom
    df.columns = df.columns.str.strip().str.title()

    # Buat kolom Jumlah jika belum ada
    if "Jumlah" not in df.columns:
        df["Jumlah"] = 0

    # Validasi tipe numerik
    df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0)

    # Buat kolom tanggal jika belum ada
    if "Tanggal" in df.columns:
        df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")

    return df


# =========================
# FUNGSI SIMPAN DATA
# =========================
def save_csv(df, file_path):
    df.to_csv(file_path, index=False)


# =========================
# LOGIN
# =========================
def login():
    st.subheader("Login untuk Akses Edit")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == ADMIN_USER and pwd == ADMIN_PASS:
            st.session_state["logged_in"] = True
            st.success("Login berhasil!")
        else:
            st.error("Username / password salah!")

    return st.session_state.get("logged_in", False)


# =========================
# RINGKASAN KEUANGAN
# =========================
def display_financial_summary(df_masuk, df_keluar):

    total_masuk = df_masuk["Jumlah"].sum()
    total_keluar = df_keluar["Jumlah"].sum()
    saldo = total_masuk - total_keluar

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Pemasukan", f"Rp {total_masuk:,.0f}")

    with col2:
        st.metric("Total Pengeluaran", f"Rp {total_keluar:,.0f}")

    with col3:
        st.metric("Saldo Akhir", f"Rp {saldo:,.0f}")

    st.write("---")


# =========================
# INPUT TRANSAKSI ADMIN
# =========================
def admin_page():
    st.header("📌 Input & Manajemen Transaksi")

    tab1, tab2 = st.tabs(["Kas Masuk", "Kas Keluar"])

    # -----------------------
    # TAB KAS MASUK
    # -----------------------
    with tab1:

        file_path = f"{DATA_FOLDER}/kas_masuk.csv"
        df = load_csv(file_path)

        st.subheader("Tambah Kas Masuk")
        tgl = st.date_input("Tanggal")
        uraian = st.text_input("Uraian")
        jumlah = st.number_input("Jumlah (Rp)", min_value=0)

        if st.button("Simpan Kas Masuk"):
            new_row = {
                "Tanggal": datetime.combine(tgl, datetime.min.time()),
                "Uraian": uraian,
                "Jumlah": jumlah
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_csv(df, file_path)
            st.success("Tersimpan!")

        st.write("### Data Kas Masuk")
        st.dataframe(df)

    # -----------------------
    # TAB KAS KELUAR
    # -----------------------
    with tab2:

        file_path = f"{DATA_FOLDER}/kas_keluar.csv"
        df = load_csv(file_path)

        st.subheader("Tambah Kas Keluar")
        tgl = st.date_input("Tanggal", key="keluar_tgl")
        uraian = st.text_input("Uraian", key="keluar_uraian")
        jumlah = st.number_input("Jumlah (Rp)", min_value=0, key="keluar_jumlah")

        if st.button("Simpan Kas Keluar"):
            new_row = {
                "Tanggal": datetime.combine(tgl, datetime.min.time()),
                "Uraian": uraian,
                "Jumlah": jumlah
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_csv(df, file_path)
            st.success("Tersimpan!")

        st.write("### Data Kas Keluar")
        st.dataframe(df)


# =========================
# HALAMAN LAPORAN PUBLIK
# =========================
def public_report():
    st.header("📊 Laporan Keuangan Musholla At-Taqwa")

    df_masuk = load_csv(f"{DATA_FOLDER}/kas_masuk.csv")
    df_keluar = load_csv(f"{DATA_FOLDER}/kas_keluar.csv")

    # Ringkasan
    display_financial_summary(df_masuk, df_keluar)

    st.subheader("📥 Rincian Kas Masuk")
    st.dataframe(df_masuk)

    st.subheader("📤 Rincian Kas Keluar")
    st.dataframe(df_keluar)


# =========================
# MAIN APP
# =========================
def main():
    st.title("Aplikasi Keuangan — Musholla At Taqwa RT.1 Dusun Klotok")
    st.caption("Aplikasi sederhana untuk pencatatan dan pelaporan keuangan pembangunan musholla.")

    st.write("## Akses Laporan")
    if st.button("📄 Lihat Laporan Publik"):
        public_report()

    st.write("---")

    st.write("## Login untuk Akses Edit")
    if login():
        admin_page()


if __name__ == "__main__":
    main()
