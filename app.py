import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =====================================================================
# KONFIGURASI DIREKTORI
# =====================================================================
DATA_FILE = "data/keuangan.csv"
BARANG_FILE = "data/barang.csv"
LOG_FILE = "data/log.csv"
BUKTI_DIR = "bukti"

os.makedirs("data", exist_ok=True)
os.makedirs(BUKTI_DIR, exist_ok=True)

# =====================================================================
# USERS PANITIA
# =====================================================================
PANITIA_USERS = {
    "Ketua": "kelas3ku",
    "Sekretaris": "fatik3762",
    "Bendahara 1": "hadi5028",
    "Bendahara 2": "riki6522",
    "Koor Donasi 1": "bayu0255",
    "Koor Donasi 2": "roni9044"
}

# =====================================================================
# INISIALISASI CSV
# =====================================================================
def init_csv():
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=["Tanggal", "Keterangan", "Kategori", "Masuk", "Keluar", "Bukti"]).to_csv(DATA_FILE, index=False)

    if not os.path.exists(BARANG_FILE):
        pd.DataFrame(columns=["Tanggal", "Nama Barang", "Jumlah", "Satuan", "Bukti"]).to_csv(BARANG_FILE, index=False)

    if not os.path.exists(LOG_FILE):
        pd.DataFrame(columns=["Waktu", "Aktivitas"]).to_csv(LOG_FILE, index=False)

init_csv()

# =====================================================================
# UTILITAS
# =====================================================================
def load_df(path):
    return pd.read_csv(path)

def save_df(df, path):
    df.to_csv(path, index=False)

def preview_link(bukti):
    if bukti == "" or pd.isna(bukti):
        return "-"
    return f"[Lihat]({BUKTI_DIR}/{bukti})"

def log_activity(text):
    df = load_df(LOG_FILE)
    df.loc[len(df)] = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), text]
    save_df(df, LOG_FILE)

# =====================================================================
# LOGIN
# =====================================================================
st.title("📊 Sistem Keuangan Musholla At-Taqwa RT 1")

role = st.selectbox("Login sebagai:", ["Publik"] + list(PANITIA_USERS.keys()))

if role != "Publik":
    pwd = st.text_input("Password:", type="password")
    if pwd != PANITIA_USERS.get(role, ""):
        st.warning("Masukkan password yang benar.")
        st.stop()

st.success(f"Login sebagai {role}")

# =====================================================================
# HALAMAN
# =====================================================================
tab1, tab2, tab3, tab4 = st.tabs(["💰 Keuangan", "📦 Barang Masuk", "📄 Laporan", "🧾 Log"])

# =====================================================================
# TAB 1 — INPUT KEUANGAN (ADMIN ONLY)
# =====================================================================
with tab1:
    st.header("Input Keuangan")

    if role == "Publik":
        st.info("Hanya panitia yang dapat input data.")
    else:
        tgl = st.date_input("Tanggal", datetime.now())
        ket = st.text_input("Keterangan")
        kategori = st.selectbox("Kategori", ["Kas Masuk", "Kas Keluar"])

        if kategori == "Kas Masuk":
            masuk = st.number_input("Masuk (Rp)", min_value=0)
            keluar = 0
        else:
            masuk = 0
            keluar = st.number_input("Keluar (Rp)", min_value=0)

        bukti = st.file_uploader("Upload Bukti", type=["jpg", "png", "jpeg", "pdf"], key="keuangan_uploader")

        if st.button("Simpan"):
            df = load_df(DATA_FILE)

            bukti_name = ""
            if bukti:
                ext = bukti.name.split(".")[-1]
                bukti_name = f"k_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                with open(f"{BUKTI_DIR}/{bukti_name}", "wb") as f:
                    f.write(bukti.getbuffer())

            df.loc[len(df)] = [str(tgl), ket, kategori, masuk, keluar, bukti_name]
            save_df(df, DATA_FILE)

            log_activity(f"{role} input keuangan: {ket}")
            st.success("Data berhasil disimpan!")

# =====================================================================
# TAB 2 — INPUT BARANG MASUK
# =====================================================================
with tab2:
    st.header("Barang Masuk")

    if role == "Publik":
        st.info("Hanya panitia yang dapat input data.")
    else:
        tgl = st.date_input("Tanggal", datetime.now(), key="tgl_barang")
        nama = st.text_input("Nama Barang")
        jumlah = st.number_input("Jumlah", min_value=1)
        satuan = st.text_input("Satuan", value="unit")

        bukti_b = st.file_uploader("Upload Bukti Barang", type=["jpg", "png", "jpeg", "pdf"], key="barang_uploader")

        if st.button("Simpan Barang"):
            dfb = load_df(BARANG_FILE)

            bukti_name = ""
            if bukti_b:
                ext = bukti_b.name.split(".")[-1]
                bukti_name = f"b_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                with open(f"{BUKTI_DIR}/{bukti_name}", "wb") as f:
                    f.write(bukti_b.getbuffer())

            dfb.loc[len(dfb)] = [str(tgl), nama, jumlah, satuan, bukti_name]
            save_df(dfb, BARANG_FILE)

            log_activity(f"{role} input barang: {nama}")
            st.success("Barang berhasil disimpan!")

# =====================================================================
# TAB 3 — LAPORAN
# =====================================================================
with tab3:
    st.header("Laporan Keuangan & Barang")

    st.subheader("📘 Keuangan")
    df = load_df(DATA_FILE)
    if not df.empty:
        df["Preview"] = df["Bukti"].apply(preview_link)
        st.dataframe(df)

        st.metric("Total Masuk", f"Rp {df['Masuk'].sum():,}")
        st.metric("Total Keluar", f"Rp {df['Keluar'].sum():,}")
        st.metric("Saldo", f"Rp {(df['Masuk'].sum() - df['Keluar'].sum()):,}")
    else:
        st.info("Belum ada data keuangan.")

    st.subheader("📦 Barang Masuk")
    dfb = load_df(BARANG_FILE)
    if not dfb.empty:
        dfb["Preview"] = dfb["Bukti"].apply(preview_link)
        st.dataframe(dfb)
    else:
        st.info("Belum ada data barang.")

# =====================================================================
# TAB 4 — LOG
# =====================================================================
with tab4:
    st.header("Aktivitas Panitia")
    dfl = load_df(LOG_FILE)
    st.dataframe(dfl)
