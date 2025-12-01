import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ======================================================
#  FOLDER SETUP AMAN
# ======================================================
DATA_DIR = "data"
BUKTI_DIR = "data/bukti"
PENERIMAAN_DIR = "data/penerimaan"

def safe_makedirs(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.rename(path, path + "_backup")
    else:
        os.makedirs(path, exist_ok=True)

for folder in [DATA_DIR, BUKTI_DIR, PENERIMAAN_DIR]:
    safe_makedirs(folder)

# ======================================================
# CSV FILES
# ======================================================
KEUANGAN_CSV = "data/keuangan.csv"
BARANG_CSV = "data/barang.csv"
LOG_CSV = "data/log_aktivitas.csv"

# ======================================================
#  SINKRONISASI KOLOM
# ======================================================
def sync_columns(df, required):
    """Menambah kolom yang hilang dan mengurutkan kolom agar sesuai template."""
    for col in required:
        if col not in df.columns:
            df[col] = ""
    return df[required]

def ensure_csv(path, cols):
    if not os.path.exists(path):
        pd.DataFrame(columns=cols).to_csv(path, index=False)

# Template kolom
KEUANGAN_COLS = ["Tanggal", "Keterangan", "Kategori", "Masuk", "Keluar", "Bukti"]
BARANG_COLS   = ["Tanggal", "Nama Barang", "Jumlah", "Satuan", "Keterangan", "Bukti"]
LOG_COLS      = ["Waktu", "User", "Aksi"]

ensure_csv(KEUANGAN_CSV, KEUANGAN_COLS)
ensure_csv(BARANG_CSV, BARANG_COLS)
ensure_csv(LOG_CSV, LOG_COLS)

# ======================================================
# LOGIN SYSTEM
# ======================================================
st.title("Sistem Keuangan Musholla At-Taqwa RT 1")

USERS = {
    "Ketua": "kelas3ku",
    "Sekretaris": "fatik3762",
    "Bendahara 1": "hadi5028",
    "Bendahara 2": "riki6522",
    "Koor Donasi 1": "bayu0255",
    "Koor Donasi 2": "roni9044",
    "Publik": "",  # publik tanpa password
}

user = st.sidebar.selectbox("Login sebagai:", USERS.keys())

password = ""
if user != "Publik":
    password = st.sidebar.text_input("Password:", type="password")

login = (user == "Publik") or (password == USERS[user])

if not login:
    st.warning("Masukkan password untuk melanjutkan.")
    st.stop()

st.success(f"Login sebagai {user}")

# ======================================================
# LOGGING
# ======================================================
def log_aktivitas(user, aksi):
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.read_csv(LOG_CSV)
    df = sync_columns(df, LOG_COLS)
    df.loc[len(df)] = [waktu, user, aksi]
    df.to_csv(LOG_CSV, index=False)

# ======================================================
# INPUT DATA (PANITIA SAJA)
# ======================================================
if user != "Publik":
    st.header("Input Keuangan")
    tab1, tab2 = st.tabs(["💰 Keuangan", "📦 Barang Masuk"])

    # --------------------------------------------------
    # TAB KEUANGAN
    # --------------------------------------------------
    with tab1:
        tgl = st.date_input("Tanggal")
        ket = st.text_input("Keterangan")
        kategori = st.selectbox("Kategori", ["Kas Masuk", "Kas Keluar", "Donasi", "Operasional"])
        masuk = st.number_input("Masuk (Rp)", min_value=0)
        keluar = st.number_input("Keluar (Rp)", min_value=0)

        bukti = st.file_uploader("Upload Bukti", type=["jpg","png","jpeg","pdf"])

        if st.button("Simpan Keuangan"):
            bukti_name = ""
            if bukti:
                ts = datetime.now().strftime("%Y%m%d%H%M%S")
                bukti_name = f"{ts}_{bukti.name}"
                with open(f"{BUKTI_DIR}/{bukti_name}", "wb") as f:
                    f.write(bukti.getbuffer())

            df = pd.read_csv(KEUANGAN_CSV)
            df = sync_columns(df, KEUANGAN_COLS)

            df.loc[len(df)] = [str(tgl), ket, kategori, masuk, keluar, bukti_name]
            df.to_csv(KEUANGAN_CSV, index=False)

            log_aktivitas(user, f"Input keuangan: {ket}")
            st.success("Data keuangan disimpan.")

    # --------------------------------------------------
    # TAB BARANG MASUK
    # --------------------------------------------------
    with tab2:
        tglb = st.date_input("Tanggal Barang")
        namab = st.text_input("Nama Barang")
        jumlah = st.number_input("Jumlah", min_value=1)
        satuan = st.text_input("Satuan")
        ketb = st.text_area("Keterangan")
        bukti_b = st.file_uploader("Upload Bukti", type=["jpg","png","jpeg","pdf"])

        if st.button("Simpan Barang Masuk"):
            bukti_name = ""
            if bukti_b:
                ts = datetime.now().strftime("%Y%m%d%H%M%S")
                bukti_name = f"{ts}_{bukti_b.name}"
                with open(f"{PENERIMAAN_DIR}/{bukti_name}", "wb") as f:
                    f.write(bukti_b.getbuffer())

            dfb = pd.read_csv(BARANG_CSV)
            dfb = sync_columns(dfb, BARANG_COLS)

            dfb.loc[len(dfb)] = [str(tglb), namab, jumlah, satuan, ketb, bukti_name]
            dfb.to_csv(BARANG_CSV, index=False)

            log_aktivitas(user, f"Input barang: {namab}")
            st.success("Data barang masuk disimpan.")

# ======================================================
# LAPORAN KEUANGAN
# ======================================================
st.header("📊 Laporan Keuangan")

df_lap = sync_columns(pd.read_csv(KEUANGAN_CSV), KEUANGAN_COLS)

def preview_link(x):
    if not x:
        return ""
    path = f"{BUKTI_DIR}/{x}"
    return f"[Lihat Bukti]({path})" if os.path.exists(path) else ""

df_lap["Preview"] = df_lap["Bukti"].apply(preview_link)
st.dataframe(df_lap)

# ======================================================
# LAPORAN BARANG
# ======================================================
st.header("📦 Daftar Barang Masuk")

df_barang = sync_columns(pd.read_csv(BARANG_CSV), BARANG_COLS)

def preview_brg(x):
    if not x:
        return ""
    path = f"{PENERIMAAN_DIR}/{x}"
    return f"[Lihat]({path})" if os.path.exists(path) else ""

df_barang["Preview"] = df_barang["Bukti"].apply(preview_brg)

st.dataframe(df_barang)

# ======================================================
# LOG (PANITIA SAJA)
# ======================================================
if user != "Publik":
    st.header("📝 Log Aktivitas")
    df_log = sync_columns(pd.read_csv(LOG_CSV), LOG_COLS)
    st.dataframe(df_log)

# ======================================================
# DOWNLOAD
# ======================================================
st.header("📥 Download Semua Data")

st.download_button("Download Keuangan (CSV)", df_lap.to_csv(index=False), "keuangan.csv")
st.download_button("Download Barang (CSV)", df_barang.to_csv(index=False), "barang.csv")

if user != "Publik":
    st.download_button("Download Log (CSV)", df_log.to_csv(index=False), "log.csv")
