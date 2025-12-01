import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ======================================================
#  KONFIGURASI UTAMA
# ======================================================

DATA_DIR = "data"
BUKTI_DIR = "bukti"

KEUANGAN_FILE = f"{DATA_DIR}/keuangan.csv"
BARANG_FILE = f"{DATA_DIR}/barang.csv"
LOG_FILE = f"{DATA_DIR}/log_aktivitas.csv"

GITHUB_RAW_KEUANGAN = "https://raw.githubusercontent.com/mushollaattaqwaklotok/laporan-keuangan/refs/heads/main/data/keuangan.csv"
GITHUB_RAW_BARANG = "https://raw.githubusercontent.com/mushollaattaqwaklotok/laporan-keuangan/refs/heads/main/data/barang.csv"

ADMIN_PASSWORD = "attaqwa"
PUBLIK_MODE = "Publik"
ADMIN_MODE = "Admin"

# ------------------------------------------------------
#  Pastikan folder ada
# ------------------------------------------------------
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BUKTI_DIR, exist_ok=True)

# ======================================================
#  FUNGSI UTILITAS
# ======================================================

def load_csv(local_path, github_url):
    """Load CSV dari lokal, jika gagal ambil dari GitHub"""
    try:
        if os.path.exists(local_path):
            return pd.read_csv(local_path)
        return pd.read_csv(github_url)
    except:
        return pd.DataFrame()

def save_csv(df, path):
    try:
        df.to_csv(path, index=False)
    except:
        pass

def log_aktivitas(teks):
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = pd.DataFrame({"Waktu": [waktu], "Aktivitas": [teks]})

    if os.path.exists(LOG_FILE):
        lama = pd.read_csv(LOG_FILE)
        baru = pd.concat([lama, entry], ignore_index=True)
    else:
        baru = entry

    baru.to_csv(LOG_FILE, index=False)

def upload_bukti(file):
    if file is None:
        return ""
    ext = file.name.split(".")[-1].lower()
    new_name = datetime.now().strftime("%Y%m%d%H%M%S") + "." + ext
    save_path = f"{BUKTI_DIR}/{new_name}"
    with open(save_path, "wb") as f:
        f.write(file.read())
    return save_path


# ======================================================
#  LOAD DATABASE
# ======================================================
def load_keuangan():
    return load_csv(KEUANGAN_FILE, GITHUB_RAW_KEUANGAN)

def load_barang():
    return load_csv(BARANG_FILE, GITHUB_RAW_BARANG)


# ======================================================
#  STREAMLIT APP
# ======================================================
st.set_page_config(page_title="Laporan Keuangan Musholla At-Taqwa", layout="wide")
st.title("📊 Laporan Keuangan Musholla At-Taqwa - RT 1 Dusun Klotok")

# ======================================================
#  MODE SELEKSI (ADMIN / PUBLIK)
# ======================================================
mode = st.sidebar.selectbox("Mode Aplikasi", [PUBLIK_MODE, ADMIN_MODE])

if mode == ADMIN_MODE:
    password = st.sidebar.text_input("Password Admin", type="password")
    if password != ADMIN_PASSWORD:
        st.warning("Masukkan password admin untuk melanjutkan")
        st.stop()

# ======================================================
#  MODE PUBLIK — HANYA VIEW
# ======================================================
if mode == PUBLIK_MODE:

    st.header("💰 Laporan Keuangan")

    df = load_keuangan()

    if df.empty:
        st.info("Belum ada data keuangan.")
    else:
        st.dataframe(df, use_container_width=True)

        # ====== PREVIEW BUKTI KEUANGAN ======
        st.subheader("🧾 Bukti Keuangan (Nota / Kwitansi)")
        for i, row in df.iterrows():
            bukti = str(row.get("Bukti", "")).strip()
            if bukti:
                with st.expander(f"[{i}] {row['Tanggal']} — {row['Keterangan']}"):
                    try:
                        if bukti.startswith("http"):
                            if bukti.lower().endswith((".jpg", ".jpeg", ".png")):
                                st.image(bukti)
                            else:
                                st.markdown(f"[Lihat File]({bukti})")
                        else:
                            st.image(open(bukti, "rb").read())
                    except:
                        st.markdown(f"[Buka File]({bukti})")

    # ======================================================
    #   TAMPILAN BARANG (PUBLIK)
    # ======================================================
    st.header("📦 Laporan Barang Masuk / Keluar")

    df_b = load_barang()

    if df_b.empty:
        st.info("Belum ada data barang.")
    else:
        st.dataframe(
            df_b.drop(columns=["Bukti"]) if "Bukti" in df_b.columns else df_b,
            use_container_width=True
        )

        # ====== PREVIEW FOTO BARANG ======
        st.subheader("📸 Bukti Foto Barang")
        for i, row in df_b.iterrows():
            bukti = str(row.get("Bukti", "")).strip()
            if bukti:
                with st.expander(f"[{i}] {row['Tanggal']} — {row['Jenis']} – {row['Keterangan']}"):
                    try:
                        if bukti.startswith("http"):
                            st.image(bukti)
                        else:
                            st.image(open(bukti, "rb").read())
                    except:
                        st.markdown(f"[Buka File]({bukti})")

    # ====== DOWNLOAD LAPORAN ======
    st.subheader("📥 Download Laporan")
    st.download_button("Download CSV Keuangan", df.to_csv(index=False), file_name="keuangan.csv")
    st.download_button("Download CSV Barang", df_b.to_csv(index=False), file_name="barang.csv")

    st.stop()

# ======================================================
#  MODE ADMIN
# ======================================================
st.header("🔐 Panel Admin")

# ======================================================
#  INPUT KEUANGAN
# ======================================================
st.subheader("➕ Input Keuangan")

df = load_keuangan()

col1, col2 = st.columns(2)
with col1:
    tanggal = st.date_input("Tanggal", datetime.now())
    keterangan = st.text_input("Keterangan")
with col2:
    masuk = st.number_input("Masuk (Rp)", 0)
    keluar = st.number_input("Keluar (Rp)", 0)

bukti = st.file_uploader("Upload Bukti (Opsional)", type=["jpg", "jpeg", "png", "pdf"])

if st.button("Simpan Keuangan"):
    bukti_path = upload_bukti(bukti)

    saldo_lama = df["Saldo"].iloc[-1] if not df.empty else 0
    saldo_baru = saldo_lama + masuk - keluar

    new = pd.DataFrame({
        "Tanggal": [str(tanggal)],
        "Keterangan": [keterangan],
        "Masuk": [masuk],
        "Keluar": [keluar],
        "Saldo": [saldo_baru],
        "Bukti": [bukti_path]
    })

    df = pd.concat([df, new], ignore_index=True)
    save_csv(df, KEUANGAN_FILE)
    log_aktivitas(f"Input keuangan: {keterangan} ({masuk}/{keluar})")

    st.success("Data keuangan berhasil disimpan!")

# ======================================================
#  INPUT BARANG
# ======================================================
st.subheader("📦 Input Barang Masuk / Keluar")

df_b = load_barang()

col1, col2 = st.columns(2)
with col1:
    tgl_b = st.date_input("Tanggal Barang", datetime.now(), key="tglbarang")
    jenis = st.selectbox("Jenis", ["Masuk", "Keluar"])
with col2:
    jumlah = st.number_input("Jumlah", 0)
    ket_b = st.text_input("Keterangan Barang")

bukti_b = st.file_uploader("Upload Bukti Barang (Opsional)", type=["jpg","jpeg","png","pdf"], key="buktibarang")

if st.button("Simpan Barang"):
    bukti_path_b = upload_bukti(bukti_b)

    new_b = pd.DataFrame({
        "Tanggal": [str(tgl_b)],
        "Jenis": [jenis],
        "Jumlah": [jumlah],
        "Keterangan": [ket_b],
        "Bukti": [bukti_path_b]
    })

    df_b = pd.concat([df_b, new_b], ignore_index=True)
    save_csv(df_b, BARANG_FILE)
    log_aktivitas(f"Input barang: {jenis} {jumlah} ({ket_b})")

    st.success("Data barang berhasil disimpan!")

# ======================================================
#  LOG AKTIVITAS (PALING BAWAH)
# ======================================================
st.subheader("📜 Log Aktivitas Admin")

if os.path.exists(LOG_FILE):
    st.dataframe(pd.read_csv(LOG_FILE), use_container_width=True)
else:
    st.info("Belum ada aktivitas.")
