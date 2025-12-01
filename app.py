import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

# ======================================================
#  KONFIGURASI UTAMA
# ======================================================
DATA_DIR = "data"
BUKTI_DIR = "data/bukti"
PENERIMAAN_DIR = "data/penerimaan"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BUKTI_DIR, exist_ok=True)
os.makedirs(PENERIMAAN_DIR, exist_ok=True)

FILE_KEUANGAN = "data/keuangan.csv"
FILE_BARANG = "data/barang.csv"
FILE_LOG = "data/log_aktivitas.csv"

TZ = timezone(timedelta(hours=7))

# LOGIN PANITIA
PANITIA_USERS = {
    "Ketua": "kelas3ku",
    "Sekretaris": "fatik3762",
    "Bendahara 1": "hadi5028",
    "Bendahara 2": "riki6522",
    "Koor Donasi 1": "bayu0255",
    "Koor Donasi 2": "roni9044"
}

PUBLIK_MODE = "PUBLIK"
PANITIA_MODE = "PANITIA"

# ======================================================
#  LOAD / SAVE CSV DENGAN PERLINDUNGAN KOLUMNYA
# ======================================================
def load_csv(file, cols):
    if not os.path.exists(file):
        df = pd.DataFrame(columns=cols)
        df.to_csv(file, index=False)
        return df

    df = pd.read_csv(file)

    # Pastikan semua kolom tersedia
    for c in cols:
        if c not in df.columns:
            df[c] = ""

    # Kembalikan sesuai urutan kolom template
    return df[cols]


def save_csv(file, df):
    df.to_csv(file, index=False)


# ======================================================
#  TEMPLATE KOLOM
# ======================================================
COL_KEUANGAN = ["Tanggal", "Keterangan", "Masuk", "Keluar", "Saldo", "Bukti"]
COL_BARANG = ["Tanggal", "Nama Barang", "Jumlah", "Keterangan", "Bukti"]
COL_LOG = ["Waktu", "Pengguna", "Aksi", "Detail"]

# ======================================================
#  LOGGING AKTIVITAS
# ======================================================
def save_log(user, aksi, detail=""):
    df = load_csv(FILE_LOG, COL_LOG)
    new_row = {
        "Waktu": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "Pengguna": user,
        "Aksi": aksi,
        "Detail": detail
    }
    df.loc[len(df)] = new_row
    save_csv(FILE_LOG, df)


# ======================================================
#  THEME STYLE NU
# ======================================================
st.markdown("""
    <style>
        body { background-color: #ffffff; }
        .main { background-color: #ffffff; }
        .stApp { background-color: #ffffff; }
        h1, h2, h3 { color: #0b6e4f; font-weight: 800; }
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
        .stTextInput input, .stNumberInput input {
            border: 1px solid #0b6e4f !important;
        }
    </style>
""", unsafe_allow_html=True)


# ======================================================
#  PILIH MODE
# ======================================================
st.sidebar.header("📌 Pilih Mode")
mode = st.sidebar.radio("Mode", [PUBLIK_MODE, PANITIA_MODE])


# ======================================================
#  MODE PUBLIK
# ======================================================
if mode == PUBLIK_MODE:
    st.title("💒 Musholla At-Taqwa RT.1 Dusun Klotok – PUBLIK")

    df_uang = load_csv(FILE_KEUANGAN, COL_KEUANGAN)
    df_barang = load_csv(FILE_BARANG, COL_BARANG)

    # ----------------- TABEL KEUANGAN -----------------
    st.subheader("📄 Laporan Keuangan Uang")
    st.dataframe(df_uang, use_container_width=True)

    st.download_button(
        "⬇️ Download CSV Keuangan",
        df_uang.to_csv(index=False).encode("utf-8"),
        "laporan_keuangan.csv",
        "text/csv",
    )

    # ----------------- TABEL BARANG -----------------
    st.subheader("📦 Daftar Barang Masuk")
    st.dataframe(df_barang, use_container_width=True)

    st.download_button(
        "⬇️ Download CSV Barang",
        df_barang.to_csv(index=False).encode("utf-8"),
        "laporan_barang.csv",
        "text/csv",
    )


# ======================================================
#  MODE PANITIA
# ======================================================
else:

    st.title("🕌 Panel PANITIA – Kelola Keuangan Musholla")

    username = st.sidebar.selectbox("Pilih Nama Panitia", ["-"] + list(PANITIA_USERS.keys()))
    password = st.sidebar.text_input("Password", type="password")

    if username == "-" or password != PANITIA_USERS.get(username):
        st.warning("Masukkan username & password panitia.")
        st.stop()

    st.success(f"Login berhasil ✔️ (Panitia: {username})")
    save_log(username, "Login", "Masuk ke panel panitia")

    df_uang = load_csv(FILE_KEUANGAN, COL_KEUANGAN)
    df_barang = load_csv(FILE_BARANG, COL_BARANG)

    # ======================================================
    #   INPUT KEUANGAN
    # ======================================================
    st.subheader("➕ Tambah Data Keuangan")

    col1, col2 = st.columns(2)
    with col1:
        tgl = st.date_input("Tanggal", datetime.now(TZ))
        ket = st.text_input("Keterangan")
    with col2:
        masuk = st.number_input("Uang Masuk", min_value=0, step=1000)
        keluar = st.number_input("Uang Keluar", min_value=0, step=1000)

    bukti_file = st.file_uploader("Upload Nota/Kwitansi (Opsional)", type=["jpg", "jpeg", "png"])

    if st.button("Simpan Data Keuangan"):
        saldo_akhir = df_uang["Saldo"].iloc[-1] if not df_uang.empty else 0
        saldo_baru = saldo_akhir + masuk - keluar

        bukti_nama = ""
        if bukti_file:
            bukti_nama = f"{datetime.now(TZ).strftime('%Y%m%d-%H%M%S')}_{bukti_file.name}"
            with open(os.path.join(BUKTI_DIR, bukti_nama), "wb") as f:
                f.write(bukti_file.getbuffer())

        new_row = {
            "Tanggal": str(tgl),
            "Keterangan": ket,
            "Masuk": masuk,
            "Keluar": keluar,
            "Saldo": saldo_baru,
            "Bukti": bukti_nama
        }

        df_uang.loc[len(df_uang)] = new_row
        save_csv(FILE_KEUANGAN, df_uang)
        save_log(username, "Tambah Keuangan", f"{ket} | +{masuk} / -{keluar}")

        st.success("Data keuangan berhasil disimpan!")

    # ======================================================
    #   INPUT BARANG MASUK
    # ======================================================
    st.subheader("📦 Tambah Data Barang Masuk")

    colA, colB = st.columns(2)
    with colA:
        tglb = st.date_input("Tanggal Barang", datetime.now(TZ), key="tglb")
        nama_barang = st.text_input("Nama Barang")
    with colB:
        jumlah = st.number_input("Jumlah Barang", min_value=1, step=1)
        ketb = st.text_input("Keterangan Barang")

    bukti_barang_file = st.file_uploader("Upload Foto Barang (Opsional)", type=["jpg", "jpeg", "png"], key="barang")

    if st.button("Simpan Data Barang"):
        bukti_brg = ""
        if bukti_barang_file:
            bukti_brg = f"BRG_{datetime.now(TZ).strftime('%Y%m%d-%H%M%S')}_{bukti_barang_file.name}"
            with open(os.path.join(PENERIMAAN_DIR, bukti_brg), "wb") as f:
                f.write(bukti_barang_file.getbuffer())

        new_barang = {
            "Tanggal": str(tglb),
            "Nama Barang": nama_barang,
            "Jumlah": jumlah,
            "Keterangan": ketb,
            "Bukti": bukti_brg
        }

        df_barang.loc[len(df_barang)] = new_barang
        save_csv(FILE_BARANG, df_barang)
        save_log(username, "Tambah Barang", f"{nama_barang} ({jumlah})")

        st.success("Data barang berhasil ditambahkan!")

    # ======================================================
    #  TABEL KEUANGAN
    # ======================================================
    st.subheader("📄 Tabel Keuangan")
    st.dataframe(df_uang, use_container_width=True)

    # ======================================================
    #  TABEL BARANG
    # ======================================================
    st.subheader("📦 Tabel Barang Masuk")
    st.dataframe(df_barang, use_container_width=True)

    # ======================================================
    #  HAPUS DATA BARANG
    # ======================================================
    if not df_barang.empty:
        st.subheader("🗑 Hapus Data Barang")
        idxb = st.number_input(
            f"Pilih baris (0 — {len(df_barang)-1})",
            min_value=0, max_value=len(df_barang)-1, step=1
        )
        if st.button("Hapus Baris Barang"):
            deleted = df_barang.iloc[idxb].to_dict()
            df_barang = df_barang.drop(idxb).reset_index(drop=True)
            save_csv(FILE_BARANG, df_barang)
            save_log(username, "Hapus Barang", str(deleted))
            st.success("Baris barang berhasil dihapus!")

    # ======================================================
    #  DOWNLOAD LAPORAN
    # ======================================================
    st.subheader("⬇️ Download Semua Data")

    colD1, colD2 = st.columns(2)
    with colD1:
        st.download_button(
            "Download CSV Keuangan",
            df_uang.to_csv(index=False).encode("utf-8"),
            "laporan_keuangan.csv",
            "text/csv"
        )
    with colD2:
        st.download_button(
            "Download CSV Barang",
            df_barang.to_csv(index=False).encode("utf-8"),
            "laporan_barang.csv",
            "text/csv"
        )

    # ======================================================
    #  LOG AKTIVITAS (PALING BAWAH)
    # ======================================================
    st.subheader("📘 Log Aktivitas Panitia (Ketua Only)")

    df_log = load_csv(FILE_LOG, COL_LOG)
    st.dataframe(df_log, use_container_width=True)

    if username == "Ketua":
        if st.button("Hapus Semua Log"):
            save_csv(FILE_LOG, pd.DataFrame(columns=COL_LOG))
            save_log("Ketua", "Reset Log", "Semua log dihapus")
            st.success("Log berhasil dihapus!")

