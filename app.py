import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# ======================================================
# KONFIGURASI UTAMA
# ======================================================
DATA_DIR = "data"
BUKTI_DIR = "data/bukti"
PENERIMAAN_DIR = "data/penerimaan"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BUKTI_DIR, exist_ok=True)
os.makedirs(PENERIMAAN_DIR, exist_ok=True)

FILE_UANG = f"{DATA_DIR}/keuangan.csv"
FILE_BARANG = f"{DATA_DIR}/barang.csv"
FILE_LOG = f"{DATA_DIR}/log_aktivitas.csv"

# ======================================================
# MULTI-USER LOGIN (PANITIA)
# ======================================================
PANITIA_USERS = {
    "Ketua": "kelas3ku",
    "Sekretaris": "fatik3762",
    "Bendahara 1": "hadi5028",
    "Bendahara 2": "riki6522",
    "Koor Donasi 1": "bayu0255",
    "Koor Donasi 2": "roni9044"
}

PUBLIK_PASSWORD = "musholla2025"

# ======================================================
# FUNGSI UTILITAS
# ======================================================
def load_csv(file, cols):
    if not os.path.exists(file):
        df = pd.DataFrame(columns=cols)
        df.to_csv(file, index=False)
    return pd.read_csv(file)

def save_csv(df, file):
    df.to_csv(file, index=False)

def log_aktivitas(user, pesan):
    log_df = load_csv(FILE_LOG, ["Waktu", "Pengguna", "Aksi"])
    new = {"Waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
           "Pengguna": user,
           "Aksi": pesan}
    log_df = pd.concat([log_df, pd.DataFrame([new])], ignore_index=True)
    save_csv(log_df, FILE_LOG)

# ======================================================
# HALAMAN LOGIN
# ======================================================
st.title("📊 Sistem Keuangan Pembangunan Musholla At Taqwa")

menu = st.sidebar.selectbox("Pilih Mode Akses", ["Publik", "Panitia"])

if menu == "Publik":
    pwd = st.sidebar.text_input("Password Publik", type="password")
    if pwd != PUBLIK_PASSWORD:
        st.warning("Masukkan password publik.")
        st.stop()
    akses_panitia = False
else:
    user = st.sidebar.selectbox("Login Sebagai", PANITIA_USERS.keys())
    pwd = st.sidebar.text_input("Password Panitia", type="password")
    if pwd != PANITIA_USERS[user]:
        st.warning("Password salah.")
        st.stop()
    akses_panitia = True

# ======================================================
# LOAD DATA
# ======================================================
df_uang = load_csv(FILE_UANG,
                   ["Tanggal", "Kategori", "Keterangan", "Jumlah", "Bukti"])
df_barang = load_csv(FILE_BARANG,
                     ["Tanggal", "Nama Barang", "Jumlah", "Satuan", "Pemberi", "Bukti"])
df_log = load_csv(FILE_LOG, ["Waktu", "Pengguna", "Aksi"])

# ======================================================
# INPUT KHUSUS PANITIA
# ======================================================
if akses_panitia:
    st.header("🧾 Input Transaksi Keuangan")

    with st.form("form_uang"):
        tanggal = st.date_input("Tanggal")
        kategori = st.selectbox("Kategori", ["Masuk", "Keluar"])
        ket = st.text_input("Keterangan")
        jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=1000)
        bukti = st.file_uploader("Upload Foto Nota (Opsional)", type=["jpg", "png", "jpeg"])
        submit = st.form_submit_button("Simpan")

    if submit:
        bukti_name = ""
        if bukti:
            bukti_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{bukti.name}"
            bukti_path = os.path.join(BUKTI_DIR, bukti_name)
            with open(bukti_path, "wb") as f:
                f.write(bukti.read())

        new = {
            "Tanggal": tanggal.strftime("%Y-%m-%d"),
            "Kategori": kategori,
            "Keterangan": ket,
            "Jumlah": jumlah,
            "Bukti": bukti_name
        }
        df_uang = pd.concat([df_uang, pd.DataFrame([new])], ignore_index=True)
        save_csv(df_uang, FILE_UANG)
        log_aktivitas(user, f"Input transaksi {kategori}: {ket}")

        st.success("Transaksi berhasil disimpan!")

    st.header("📦 Input Data Barang Masuk")

    with st.form("form_barang"):
        tgl_brg = st.date_input("Tanggal Barang Masuk")
        nama_brg = st.text_input("Nama Barang")
        jml_brg = st.number_input("Jumlah Barang", min_value=0)
        satuan = st.text_input("Satuan (unit/kg/lainnya)")
        pemberi = st.text_input("Nama Penyumbang")
        bukti_brg = st.file_uploader("Upload Foto Bukti (Opsional)", type=["jpg", "png", "jpeg"])
        submit_brg = st.form_submit_button("Simpan Barang")

    if submit_brg:
        bukti_name = ""
        if bukti_brg:
            bukti_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{bukti_brg.name}"
            bukti_path = os.path.join(PENERIMAAN_DIR, bukti_name)
            with open(bukti_path, "wb") as f:
                f.write(bukti_brg.read())

        new_brg = {
            "Tanggal": tgl_brg.strftime("%Y-%m-%d"),
            "Nama Barang": nama_brg,
            "Jumlah": jml_brg,
            "Satuan": satuan,
            "Pemberi": pemberi,
            "Bukti": bukti_name
        }

        df_barang = pd.concat([df_barang, pd.DataFrame([new_brg])], ignore_index=True)
        save_csv(df_barang, FILE_BARANG)
        log_aktivitas(user, f"Input barang masuk: {nama_brg}")

        st.success("Barang masuk berhasil disimpan!")

# ======================================================
# TAMPILAN LAPORAN UMUM
# ======================================================
st.header("📄 Laporan Keuangan")

df_tampil = df_uang.copy()
df_tampil["Preview"] = df_tampil["Bukti"].apply(
    lambda x: f"[Lihat Bukti](data/bukti/{x})" if x else ""
)

st.dataframe(df_tampil)

# Daftar Barang Publik
st.header("📦 Daftar Barang Masuk")

df_brg_tampil = df_barang.copy()
df_brg_tampil["Preview"] = df_brg_tampil["Bukti"].apply(
    lambda x: f"[Lihat Bukti](data/penerimaan/{x})" if x else ""
)

st.dataframe(df_brg_tampil)

# ======================================================
# DOWNLOAD DATA
# ======================================================
st.subheader("⬇️ Download Data (CSV)")

col1, col2 = st.columns(2)

with col1:
    st.download_button("Download Data Uang",
                       df_uang.to_csv(index=False),
                       "keuangan.csv")

with col2:
    st.download_button("Download Data Barang",
                       df_barang.to_csv(index=False),
                       "barang.csv")

# ======================================================
# LOG AKTIVITAS (PALING BAWAH)
# ======================================================
if akses_panitia:
    st.header("📜 Log Aktivitas Panitia")
    st.dataframe(df_log)
