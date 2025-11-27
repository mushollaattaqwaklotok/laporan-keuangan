import streamlit as st
import pandas as pd
import io
from datetime import datetime

# ==============================
#  TEMA PUTIH – HIJAU NU
# ==============================
def apply_nu_theme():
    st.markdown("""
    <style>
        body {
            background-color: #ffffff;
        }
        .main, .block-container {
            background-color: #ffffff;
        }
        /* Judul NU Hijau */
        h1, h2, h3, h4 {
            color: #0f5e3d;
            font-weight: 700;
        }
        .stButton>button {
            background-color: #0f5e3d !important;
            color: white !important;
            border-radius: 6px;
            padding: 0.5rem 1rem;
        }
        .stButton>button:hover {
            background-color: #0c4b31 !important;
        }
        /* Input box */
        .stTextInput>div>div>input, textarea {
            border-radius: 6px !important;
            border: 1px solid #0f5e3d55 !important;
        }
        .stSelectbox, .stDateInput {
            border-radius: 6px !important;
        }
        /* Card putih border hijau */
        .nu-card {
            padding: 1rem;
            border-radius: 10px;
            border: 2px solid #0f5e3d;
            background: #ffffff;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)


# ==============================
# DATABASE SEDERHANA (CSV)
# ==============================
FILE_DATA = "data_transaksi.csv"
FILE_LOG = "log_aktivitas.csv"

def init_database():
    try:
        pd.read_csv(FILE_DATA)
    except:
        df = pd.DataFrame(columns=["tanggal", "jenis", "keterangan", "jumlah", "bukti"])
        df.to_csv(FILE_DATA, index=False)

    try:
        pd.read_csv(FILE_LOG)
    except:
        df = pd.DataFrame(columns=["waktu", "aksi"])
        df.to_csv(FILE_LOG, index=False)


def save_transaksi(tgl, jenis, ket, jumlah, bukti_name):
    df = pd.read_csv(FILE_DATA)
    df.loc[len(df)] = [tgl, jenis, ket, jumlah, bukti_name]
    df.to_csv(FILE_DATA, index=False)


def save_log(aksi):
    df = pd.read_csv(FILE_LOG)
    df.loc[len(df)] = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), aksi]
    df.to_csv(FILE_LOG, index=False)


def download_excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Laporan")
    return buffer


# ==============================
# LOGIN PANITIA
# ==============================
USERNAME = "ferri"
PASSWORD = "kelas3ku"

def login_page():
    st.title("🔐 Login Panitia")
    st.markdown("Masukkan username dan password untuk masuk ke sistem.")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == USERNAME and p == PASSWORD:
            st.session_state["login"] = True
            st.session_state["username"] = u
            save_log(f"Login oleh {u}")
            st.success("Login berhasil!")
        else:
            st.error("Username atau password salah.")


# ==============================
# HALAMAN ADMIN
# ==============================
def admin_page():
    st.title("💹 Aplikasi Keuangan — Musholla At-Taqwa RT.1 Klotok")

    df = pd.read_csv(FILE_DATA)

    menu = st.sidebar.radio(
        "Menu",
        ["Kas Masuk", "Kas Keluar", "Rekap Transaksi", "Log Aktivitas", "Logout"]
    )

    # -------------------- KAS MASUK --------------------
    if menu == "Kas Masuk":
        st.subheader("📥 Input Kas Masuk")
        with st.container():
            st.markdown("<div class='nu-card'>", unsafe_allow_html=True)

            tgl = st.date_input("Tanggal")
            ket = st.text_input("Keterangan")
            jumlah = st.number_input("Jumlah (Rp)", min_value=0)
            bukti = st.file_uploader("Upload Bukti", type=["jpg", "png", "jpeg"])

            st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Simpan Kas Masuk"):
            bukti_name = ""
            if bukti:
                bukti_name = f"bukti_{datetime.now().timestamp()}_{bukti.name}"
                with open(bukti_name, "wb") as f:
                    f.write(bukti.getbuffer())

            save_transaksi(str(tgl), "Masuk", ket, jumlah, bukti_name)
            save_log(f"Tambah kas masuk: {jumlah}")
            st.success("Kas Masuk berhasil disimpan!")

    # -------------------- KAS KELUAR --------------------
    if menu == "Kas Keluar":
        st.subheader("📤 Input Kas Keluar")
        with st.container():
            st.markdown("<div class='nu-card'>", unsafe_allow_html=True)

            tgl = st.date_input("Tanggal")
            ket = st.text_input("Keterangan")
            jumlah = st.number_input("Jumlah (Rp)", min_value=0)
            bukti = st.file_uploader("Upload Bukti", type=["jpg", "png", "jpeg"])

            st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Simpan Kas Keluar"):
            bukti_name = ""
            if bukti:
                bukti_name = f"bukti_{datetime.now().timestamp()}_{bukti.name}"
                with open(bukti_name, "wb") as f:
                    f.write(bukti.getbuffer())

            save_transaksi(str(tgl), "Keluar", ket, jumlah, bukti_name)
            save_log(f"Tambah kas keluar: {jumlah}")
            st.success("Kas Keluar berhasil disimpan!")

    # -------------------- REKAP DATA --------------------
    if menu == "Rekap Transaksi":
        st.subheader("📊 Rekap Keuangan")
        st.dataframe(df)

        total_masuk = df[df["jenis"] == "Masuk"]["jumlah"].sum()
        total_keluar = df[df["jenis"] == "Keluar"]["jumlah"].sum()
        saldo = total_masuk - total_keluar

        st.info(f"💰 **Total Masuk:** Rp {total_masuk:,}")
        st.warning(f"💸 **Total Keluar:** Rp {total_keluar:,}")
        st.success(f"📦 **Saldo Akhir:** Rp {saldo:,}")

        if st.download_button("📥 Download Laporan Excel", download_excel(df),
                              file_name="laporan_keuangan.xlsx"):
            save_log("Download laporan excel")

    # -------------------- LOG AKTIVITAS --------------------
    if menu == "Log Aktivitas":
        st.subheader("📃 Log Aktivitas Sistem")
        log = pd.read_csv(FILE_LOG)
        st.dataframe(log)

    if menu == "Logout":
        st.session_state["login"] = False
        save_log("Logout")
        st.rerun()


# ==============================
# MAIN APP
# ==============================
def main():
    apply_nu_theme()
    init_database()

    if "login" not in st.session_state:
        st.session_state["login"] = False

    if not st.session_state["login"]:
        login_page()
    else:
        admin_page()


if __name__ == "__main__":
    main()
