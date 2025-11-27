import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ------------------------------
# KONFIG LOGIN MULTI USER
# ------------------------------
USERS = {
    "ferri": "ferri@123",
    "alfan": "ferri@123",
    "sunhadi": "ferri@123",
    "riki": "ferri@123",
    "riaji": "ferri@123",
    "bayu": "ferri@123"
}

# ------------------------------
# FILE CSV
# ------------------------------
DATA_FILE = "data_keuangan.csv"
REQUIRED_COLUMNS = ["tanggal", "jenis", "keterangan", "jumlah", "petugas"]


# ------------------------------
# FUNGSI CEK & PERBAIKI CSV
# ------------------------------
def repair_csv():
    """Memastikan CSV punya struktur yang benar."""
    try:
        df = pd.read_csv(DATA_FILE)
        miss = [col for col in REQUIRED_COLUMNS if col not in df.columns]

        # Jika header tidak lengkap → perbaiki
        if len(miss) > 0:
            df = pd.DataFrame(columns=REQUIRED_COLUMNS)
            df.to_csv(DATA_FILE, index=False)
            return df

        # Jika CSV hanya header tanpa isi → tetap aman
        return df

    except Exception:
        # Jika file rusak atau kosong total → buat ulang
        df = pd.DataFrame(columns=REQUIRED_COLUMNS)
        df.to_csv(DATA_FILE, index=False)
        return df


def load_data():
    return repair_csv()


def save_data(row):
    df = repair_csv()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)


# ------------------------------
# LOGIN PAGE
# ------------------------------
def login_page():
    st.title("🔐 Login untuk Akses Edit")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state["user"] = username
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("Username atau password salah.")


# ------------------------------
# ADMIN PANEL
# ------------------------------
def admin_page():
    st.title("📌 Input & Manajemen Transaksi")
    st.write(f"👤 Login sebagai **{st.session_state['user']}**")

    # KAS MASUK
    st.subheader("Kas Masuk")
    with st.form("kas_masuk"):
        tgl = st.date_input("Tanggal")
        ket = st.text_input("Keterangan")
        jml = st.number_input("Jumlah (Rp)", min_value=0)
        if st.form_submit_button("Simpan Kas Masuk"):
            save_data({
                "tanggal": str(tgl),
                "jenis": "masuk",
                "keterangan": ket,
                "jumlah": jml,
                "petugas": st.session_state["user"]
            })
            st.success("Kas masuk tersimpan!")

    # KAS KELUAR
    st.subheader("Kas Keluar")
    with st.form("kas_keluar"):
        tgl = st.date_input("Tanggal", key="tgl_keluar")
        ket = st.text_input("Keterangan", key="ket_keluar")
        jml = st.number_input("Jumlah (Rp)", min_value=0, key="jml_keluar")
        if st.form_submit_button("Simpan Kas Keluar"):
            save_data({
                "tanggal": str(tgl),
                "jenis": "keluar",
                "keterangan": ket,
                "jumlah": jml,
                "petugas": st.session_state["user"]
            })
            st.success("Kas keluar tersimpan!")

    # LAPORAN
    st.subheader("📊 Laporan Keuangan")
    df = load_data()

    if df.empty:
        st.warning("Belum ada transaksi.")
    else:
        st.dataframe(df)

        total_masuk = df[df["jenis"] == "masuk"]["jumlah"].sum()
        total_keluar = df[df["jenis"] == "keluar"]["jumlah"].sum()
        saldo = total_masuk - total_keluar

        st.info(f"💰 Total Kas Masuk: Rp {total_masuk:,.0f}")
        st.info(f"📤 Total Kas Keluar: Rp {total_keluar:,.0f}")
        st.success(f"🔵 Saldo Akhir: Rp {saldo:,.0f}")

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()


# ------------------------------
# MAIN
# ------------------------------
def main():
    st.set_page_config(page_title="Aplikasi Keuangan Musholla", layout="centered")

    if "user" not in st.session_state:
        login_page()
    else:
        admin_page()


if __name__ == "__main__":
    main()
