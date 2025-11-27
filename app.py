import streamlit as st
import pandas as pd
import datetime
import os
from io import BytesIO
from hashlib import sha256
from PIL import Image

# ============================
# KONFIGURASI DASAR
# ============================

DATA_FILE = "data/transaksi.csv"
LOG_FILE = "logs/activity_log.csv"
BUKTI_FOLDER = "bukti"

os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs(BUKTI_FOLDER, exist_ok=True)

# ============================
# AKUN LOGIN
# ============================

USERS = {
    "ferri": "ferri@123",
    "alfan": "alfan@123",
    "sunhadi": "sunhadi@123",
    "riki": "riki@123",
    "riaji": "riaji@123",
    "bayu": "bayu@123"
}

def verify(username, password):
    return username in USERS and USERS[username] == password

# ============================
# LOG AKTIVITAS
# ============================

def log_activity(username, aktivitas, detail=""):
    df_log = pd.DataFrame([{
        "waktu": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": username,
        "aktivitas": aktivitas,
        "detail": detail
    }])
    df_log.to_csv(LOG_FILE, mode="a", header=not os.path.exists(LOG_FILE), index=False)

# ============================
# LOAD DATA
# ============================

def load_transaksi():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["tanggal", "jenis", "keterangan", "jumlah", "bukti"])
    return pd.read_csv(DATA_FILE)

def save_transaksi(df):
    df.to_csv(DATA_FILE, index=False)

# ============================
# FITUR 1 – UPLOAD BUKTI
# ============================

def simpan_bukti(uploaded_file):
    if uploaded_file is None:
        return ""
    img = Image.open(uploaded_file)
    filename = f"{datetime.datetime.now().timestamp()}_{uploaded_file.name}"
    path = os.path.join(BUKTI_FOLDER, filename)
    img.save(path)
    return filename

# ============================
# FITUR 4 – DOWNLOAD LAPORAN
# ============================

def download_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Keuangan")
    return output.getvalue()

def download_pdf(df):
    text = df.to_string()
    return text.encode()

# ============================
# FITUR 5 – MODE PUBLIK
# ============================

def public_page():
    st.header("📢 Laporan Keuangan Musholla At Taqwa (Publik)")

    df = load_transaksi()
    if df.empty:
        st.warning("Belum ada data")
        return

    df["tanggal"] = pd.to_datetime(df["tanggal"])

    total_masuk = df[df["jenis"] == "masuk"]["jumlah"].sum()
    total_keluar = df[df["jenis"] == "keluar"]["jumlah"].sum()
    saldo = total_masuk - total_keluar

    st.subheader("💰 Ringkasan Keuangan")
    st.write(f"**Total Masuk:** Rp {total_masuk:,.0f}")
    st.write(f"**Total Keluar:** Rp {total_keluar:,.0f}")
    st.write(f"**Saldo Akhir:** Rp {saldo:,.0f}")

    st.subheader("📄 Semua Transaksi")
    st.dataframe(df)

    st.info("Untuk input transaksi, harap login sebagai panitia.")

# ============================
# HALAMAN ADMIN
# ============================

def admin_page(username):

    st.success(f"Login sebagai {username}")

    df = load_transaksi()

    st.subheader("📌 Input & Manajemen Transaksi")

    tab_masuk, tab_keluar, tab_log, tab_laporan = st.tabs(
        ["Kas Masuk", "Kas Keluar", "Log Aktivitas", "Download Laporan"]
    )

    # ========================
    # KAS MASUK
    # ========================
    with tab_masuk:
        tgl = st.date_input("Tanggal", datetime.date.today())
        ket = st.text_input("Keterangan")
        jml = st.number_input("Jumlah (Rp)", min_value=0)
        bukti_file = st.file_uploader("Upload Bukti (opsional)", type=["jpg", "png", "jpeg"])

        if st.button("Simpan Kas Masuk"):
            bukti_name = simpan_bukti(bukti_file)
            df.loc[len(df)] = [tgl, "masuk", ket, jml, bukti_name]
            save_transaksi(df)
            log_activity(username, "Input Kas Masuk", ket)
            st.success("Kas masuk berhasil disimpan!")

    # ========================
    # KAS KELUAR
    # ========================
    with tab_keluar:
        tgl = st.date_input("Tanggal", datetime.date.today(), key="keluar")
        ket = st.text_input("Keterangan", key="ket_keluar")
        jml = st.number_input("Jumlah (Rp)", key="jml_keluar", min_value=0)
        bukti_file = st.file_uploader("Upload Bukti (opsional)", type=["jpg", "png", "jpeg"], key="bukti_keluar")

        if st.button("Simpan Kas Keluar"):
            bukti_name = simpan_bukti(bukti_file)
            df.loc[len(df)] = [tgl, "keluar", ket, jml, bukti_name]
            save_transaksi(df)
            log_activity(username, "Input Kas Keluar", ket)
            st.success("Kas keluar berhasil disimpan!")

    # ========================
    # LOG AKTIVITAS
    # ========================
    with tab_log:
        if os.path.exists(LOG_FILE):
            log_df = pd.read_csv(LOG_FILE)
            st.dataframe(log_df)
        else:
            st.info("Belum ada log aktivitas.")

    # ========================
    # DOWNLOAD LAPORAN
    # ========================
    with tab_laporan:
        st.subheader("📥 Download Laporan")

        df = load_transaksi()

        st.download_button("Download CSV", df.to_csv(index=False), "laporan.csv")

        st.download_button(
            "Download Excel (.xlsx)", 
            download_excel(df), 
            "laporan.xlsx"
        )

        st.download_button(
            "Download PDF (.txt)", 
            download_pdf(df),
            "laporan.txt"
        )

# ============================
# MAIN APP
# ============================

def main():
    st.title("Aplikasi Keuangan — Musholla At Taqwa RT.1 Dusun Klotok")

    mode = st.sidebar.selectbox("Mode Aplikasi", ["Publik", "Login (Panitia)"])

    # ======================
    # MODE PUBLIK
    # ======================
    if mode == "Publik":
        public_page()
        return

    # ======================
    # MODE LOGIN
    # ======================
    st.sidebar.subheader("Login untuk Akses Panitia")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if verify(username, password):
            admin_page(username)
        else:
            st.sidebar.error("Username atau password salah!")

if __name__ == "__main__":
    main()
