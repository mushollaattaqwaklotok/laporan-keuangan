# === APLIKASI KEUANGAN MUSHOLLA AT-TAQWA RT 1 ===
# Dibuat oleh ChatGPT untuk Ferri Kusuma

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# ==============================
# KONFIGURASI AWAL
# ==============================

USERS = {
    "ferri": "ferri@123",
    "riki": "ferri@123",
    "bayu": "ferri@123",
}

DATA_FILE = "data.csv"
LOG_FILE = "log.csv"
BUKTI_FOLDER = "bukti"
BACKUP_FOLDER = "backup"

# Buat folder jika belum ada
os.makedirs(BUKTI_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# ==============================
# FUNGSI DATABASE
# ==============================

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["tanggal", "jenis", "keterangan", "jumlah", "panitia", "bukti"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)
    backup_name = f"{BACKUP_FOLDER}/backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
    df.to_csv(backup_name, index=False)

def load_log():
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE)
    else:
        return pd.DataFrame(columns=["waktu", "panitia", "aksi"])

def log_action(panitia, aksi):
    log_df = load_log()
    new_log = pd.DataFrame({
        "waktu": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "panitia": [panitia],
        "aksi": [aksi]
    })
    log_df = pd.concat([log_df, new_log], ignore_index=True)
    log_df.to_csv(LOG_FILE, index=False)

# ==============================
# DOWNLOAD CSV
# ==============================

def download_csv(df):
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output

# ==============================
# HALAMAN LOGIN
# ==============================

def login_page():
    st.title("Aplikasi Keuangan — Musholla At Taqwa RT.1 Dusun Klotok")

    st.subheader("Login (Panitia)")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and password == USERS[username]:
            st.session_state["user"] = username
            st.success(f"Login berhasil sebagai: {username}")
            st.rerun()
        else:
            st.error("Username atau password salah")

# ==============================
# HALAMAN ADMIN
# ==============================

def admin_page(user):

    st.title(f"🤝 Selamat Datang, {user}")

    df = load_data()

    menu = st.sidebar.radio(
        "Menu",
        ["Kas Masuk", "Kas Keluar", "Log Aktivitas",
         "Edit / Hapus Transaksi", "Download Laporan", "Dashboard"]
    )

    # ============================
    # KAS MASUK
    # ============================
    if menu == "Kas Masuk":

        st.subheader("📌 Input Kas Masuk")

        tgl = st.date_input("Tanggal", datetime.now())
        ket = st.text_input("Keterangan")
        jumlah = st.number_input("Jumlah (Rp)", min_value=0)
        bukti = st.file_uploader("Upload Bukti (opsional)", type=["jpg", "png", "jpeg"])

        if st.button("Simpan Kas Masuk"):
            filename = ""

            if bukti:
                filename = f"{BUKTI_FOLDER}/{datetime.now().strftime('%Y%m%d%H%M%S')} - {bukti.name}"
                with open(filename, "wb") as f:
                    f.write(bukti.read())

            new_row = pd.DataFrame({
                "tanggal": [str(tgl)],
                "jenis": ["masuk"],
                "keterangan": [ket],
                "jumlah": [jumlah],
                "panitia": [user],
                "bukti": [filename],
            })

            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)

            log_action(user, f"Menambah kas masuk Rp {jumlah} ({ket})")

            st.success("Kas masuk disimpan!")
            st.rerun()

    # ============================
    # KAS KELUAR
    # ============================
    if menu == "Kas Keluar":

        st.subheader("📌 Input Kas Keluar")

        tgl = st.date_input("Tanggal", datetime.now())
        ket = st.text_input("Keterangan")
        jumlah = st.number_input("Jumlah (Rp)", min_value=0)
        bukti = st.file_uploader("Upload Bukti (opsional)", type=["jpg", "png", "jpeg"])

        if st.button("Simpan Kas Keluar"):
            filename = ""

            if bukti:
                filename = f"{BUKTI_FOLDER}/{datetime.now().strftime('%Y%m%d%H%M%S')} - {bukti.name}"
                with open(filename, "wb") as f:
                    f.write(bukti.read())

            new_row = pd.DataFrame({
                "tanggal": [str(tgl)],
                "jenis": ["keluar"],
                "keterangan": [ket],
                "jumlah": [jumlah],
                "panitia": [user],
                "bukti": [filename],
            })

            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)

            log_action(user, f"Menambah kas keluar Rp {jumlah} ({ket})")

            st.success("Kas keluar disimpan!")
            st.rerun()

    # ============================
    # LOG AKTIVITAS
    # ============================
    if menu == "Log Aktivitas":
        st.subheader("📜 Log Aktivitas Panitia")
        st.dataframe(load_log())

    # ============================
    # EDIT / HAPUS TRANSAKSI
    # ============================
    if menu == "Edit / Hapus Transaksi":

        st.subheader("✏ Edit / Hapus Transaksi")

        if len(df) == 0:
            st.info("Belum ada data.")
        else:
            idx = st.number_input("ID Data (index)", min_value=0, max_value=len(df)-1)
            row = df.loc[idx]

            st.write("📄 Data saat ini:")
            st.json(row.to_dict())

            new_ket = st.text_input("Edit Keterangan", row["keterangan"])
            new_jml = st.number_input("Edit Jumlah", min_value=0, value=int(row["jumlah"]))

            if st.button("Simpan Perubahan"):
                df.at[idx, "keterangan"] = new_ket
                df.at[idx, "jumlah"] = new_jml
                save_data(df)
                log_action(user, f"Edit transaksi ID {idx}")
                st.success("Berhasil diperbarui!")
                st.rerun()

            if st.button("Hapus Data"):
                df = df.drop(idx).reset_index(drop=True)
                save_data(df)
                log_action(user, f"Hapus transaksi ID {idx}")
                st.success("Data dihapus!")
                st.rerun()

    # ============================
    # DOWNLOAD LAPORAN
    # ============================
    if menu == "Download Laporan":
        st.subheader("📥 Download Laporan Keuangan (CSV)")

        st.download_button(
            "Download Laporan (CSV)",
            download_csv(df),
            "laporan-keuangan.csv",
            mime="text/csv",
        )

    # ============================
    # DASHBOARD
    # ============================
    if menu == "Dashboard":

        st.subheader("📊 Ringkasan Keuangan")

        total_masuk = df[df["jenis"] == "masuk"]["jumlah"].sum()
        total_keluar = df[df["jenis"] == "keluar"]["jumlah"].sum()
        saldo = total_masuk - total_keluar

        st.metric("Total Kas Masuk", f"Rp {total_masuk:,.0f}")
        st.metric("Total Kas Keluar", f"Rp {total_keluar:,.0f}")
        st.metric("Saldo Akhir", f"Rp {saldo:,.0f}")

        st.subheader("📅 Grafik Harian")

        if len(df) > 0:
            chart_df = df.copy()
            chart_df["tanggal"] = pd.to_datetime(chart_df["tanggal"])
            st.line_chart(chart_df, x="tanggal", y="jumlah")

# ==============================
# MAIN
# ==============================

def main():
    if "user" not in st.session_state:
        login_page()
    else:
        admin_page(st.session_state["user"])

main()
