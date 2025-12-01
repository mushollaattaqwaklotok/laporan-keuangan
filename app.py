import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta, timezone
import requests
import base64
import io

# ======================================================
#  KONFIGURASI UTAMA
# ======================================================
# (lokal fallback)
DATA_FILE = "data/keuangan.csv"
LOG_FILE = "data/log_aktivitas.csv"

# Zona waktu GMT+7
TZ = timezone(timedelta(hours=7))

# Multi-password untuk panitia
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

# Pastikan folder data ada (untuk fallback lokal)
os.makedirs("data", exist_ok=True)

# ======================================================
#  KONFIGURASI GITHUB (ambil dari st.secrets jika ada)
# ======================================================
# Streamlit Secrets yang dianjurkan:
# GITHUB_TOKEN, GITHUB_REPO, (opsional) GITHUB_DATA_PATH, GITHUB_LOG_PATH
GITHUB_TOKEN = None
GITHUB_REPO = None
GITHUB_DATA_PATH = None
GITHUB_LOG_PATH = None

if "GITHUB_TOKEN" in st.secrets:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
if "GITHUB_REPO" in st.secrets:
    GITHUB_REPO = st.secrets["GITHUB_REPO"]
if "GITHUB_DATA_PATH" in st.secrets:
    GITHUB_DATA_PATH = st.secrets["GITHUB_DATA_PATH"]
if "GITHUB_LOG_PATH" in st.secrets:
    GITHUB_LOG_PATH = st.secrets["GITHUB_LOG_PATH"]

# defaults
if not GITHUB_DATA_PATH:
    GITHUB_DATA_PATH = "data/keuangan.csv"
if not GITHUB_LOG_PATH:
    GITHUB_LOG_PATH = "data/log_aktivitas.csv"

# Helper: raw URL (untuk membaca cepat)
def github_raw_url(repo, path, branch="main"):
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"

# ======================================================
#  GITHUB HELPERS (GET content, PUT update)
# ======================================================
def github_get_file(repo, path):
    """
    Mengambil file content & sha via GitHub API.
    Returns (content_text, sha) or (None, None) jika tidak ditemukan / error.
    """
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return None, None

    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        j = r.json()
        content_b64 = j.get("content", "")
        sha = j.get("sha", None)
        # decode
        try:
            content = base64.b64decode(content_b64).decode("utf-8")
        except Exception:
            content = None
        return content, sha
    else:
        # not found or access denied
        return None, None

def github_put_file(repo, path, content_text, commit_message="Update via Streamlit", sha=None):
    """
    Membuat atau memperbarui file di repo GitHub.
    Jika sha diberikan -> update, jika tidak -> create.
    Returns True jika berhasil.
    """
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return False

    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    encoded = base64.b64encode(content_text.encode()).decode()
    payload = {
        "message": commit_message,
        "content": encoded
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(url, headers=headers, json=payload)
    return r.status_code in (200, 201)

# ======================================================
#  FUNGSI DATA (men-support GitHub atau fallback lokal)
# ======================================================
def ensure_local_file(path, columns):
    """
    Pastikan file lokal ada. Jika belum, buat dengan header.
    """
    if not os.path.exists(path):
        df = pd.DataFrame(columns=columns)
        df.to_csv(path, index=False)

def load_data():
    # Jika konfigurasi GitHub tersedia, coba ambil dari raw URL (cepat)
    if GITHUB_TOKEN and GITHUB_REPO:
        raw = github_raw_url(GITHUB_REPO, GITHUB_DATA_PATH)
        try:
            df = pd.read_csv(raw)
            return df
        except Exception:
            # jika raw gagal (mungkin file belum ada), coba lewat API
            content, sha = github_get_file(GITHUB_REPO, GITHUB_DATA_PATH)
            if content:
                try:
                    df = pd.read_csv(io.StringIO(content))
                    return df
                except Exception:
                    pass
            # kalau tidak ada, fallback ke lokal (dan pastikan file lokal ada)
    # fallback lokal
    ensure_local_file(DATA_FILE, ["Tanggal", "Keterangan", "Masuk", "Keluar", "Saldo"])
    return pd.read_csv(DATA_FILE)

def save_data(df):
    # jika GitHub tersedia -> upload via API (replace/overwrite)
    csv_text = df.to_csv(index=False)
    if GITHUB_TOKEN and GITHUB_REPO:
        # ambil sha bila ada
        _, sha = github_get_file(GITHUB_REPO, GITHUB_DATA_PATH)
        ok = github_put_file(GITHUB_REPO, GITHUB_DATA_PATH, csv_text, commit_message="Update keuangan.csv via Streamlit", sha=sha)
        if ok:
            return True
        else:
            # jika gagal, juga tulis lokal agar tidak hilang
            df.to_csv(DATA_FILE, index=False)
            return False
    else:
        # fallback lokal
        df.to_csv(DATA_FILE, index=False)
        return True

# ======================================================
#  FUNGSI LOG (pakai GitHub juga jika tersedia)
# ======================================================
def ensure_remote_log_exists():
    # create empty log in repo if not exist
    if GITHUB_TOKEN and GITHUB_REPO:
        content, sha = github_get_file(GITHUB_REPO, GITHUB_LOG_PATH)
        if content is None:
            # buat file kosong dengan header
            header_df = pd.DataFrame(columns=["Waktu", "Pengguna", "Aksi", "Detail"])
            github_put_file(GITHUB_REPO, GITHUB_LOG_PATH, header_df.to_csv(index=False), commit_message="Create log_aktivitas.csv via Streamlit")

def load_log():
    if GITHUB_TOKEN and GITHUB_REPO:
        raw = github_raw_url(GITHUB_REPO, GITHUB_LOG_PATH)
        try:
            df = pd.read_csv(raw)
            return df
        except Exception:
            content, sha = github_get_file(GITHUB_REPO, GITHUB_LOG_PATH)
            if content:
                try:
                    df = pd.read_csv(io.StringIO(content))
                    return df
                except Exception:
                    pass
    ensure_local_file(LOG_FILE, ["Waktu", "Pengguna", "Aksi", "Detail"])
    return pd.read_csv(LOG_FILE)

def save_log(user, aksi, detail=""):
    waktu = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    new_row = {"Waktu": waktu, "Pengguna": user, "Aksi": aksi, "Detail": detail}

    if GITHUB_TOKEN and GITHUB_REPO:
        # ambil existing content, append, dan tulis kembali
        content, sha = github_get_file(GITHUB_REPO, GITHUB_LOG_PATH)
        if content:
            try:
                df = pd.read_csv(io.StringIO(content))
            except Exception:
                df = pd.DataFrame(columns=["Waktu", "Pengguna", "Aksi", "Detail"])
        else:
            df = pd.DataFrame(columns=["Waktu", "Pengguna", "Aksi", "Detail"])

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        ok = github_put_file(GITHUB_REPO, GITHUB_LOG_PATH, df.to_csv(index=False), commit_message="Update log_aktivitas.csv via Streamlit", sha=sha)
        if ok:
            return True
        else:
            # fallback lokal
            df.to_csv(LOG_FILE, index=False)
            return False
    else:
        # fallback lokal
        df = load_log()
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(LOG_FILE, index=False)
        return True

def clear_log():
    # clear local + remote
    df = pd.DataFrame(columns=["Waktu", "Pengguna", "Aksi", "Detail"])
    if GITHUB_TOKEN and GITHUB_REPO:
        _, sha = github_get_file(GITHUB_REPO, GITHUB_LOG_PATH)
        github_put_file(GITHUB_REPO, GITHUB_LOG_PATH, df.to_csv(index=False), commit_message="Reset log_aktivitas.csv via Streamlit", sha=sha)
    df.to_csv(LOG_FILE, index=False)

# ======================================================
#  Pastikan file remote ada (saat app start)
# ======================================================
if GITHUB_TOKEN and GITHUB_REPO:
    # Jika remote belum ada, buat file minimal agar tidak error
    # Data file
    content, sha = github_get_file(GITHUB_REPO, GITHUB_DATA_PATH)
    if content is None:
        # buat file data dengan header & saldo awal 0
        df0 = pd.DataFrame([{"Tanggal": datetime.now(TZ).strftime("%Y-%m-%d"),
                             "Keterangan": "Saldo Awal",
                             "Masuk": 0,
                             "Keluar": 0,
                             "Saldo": 0}])
        github_put_file(GITHUB_REPO, GITHUB_DATA_PATH, df0.to_csv(index=False), commit_message="Create keuangan.csv via Streamlit")

    # Log file
    ensure_remote_log_exists()

# ======================================================
#  TEMA WARNA NU (tidak diubah)
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
    st.title("💒 Musholla At-Taqwa RT.1 Dusun Klotok– PUBLIK")

    df = load_data()

    if df.empty:
        st.info("Belum ada data keuangan.")
    else:
        st.subheader("📄 Laporan Keuangan")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Data CSV",
            csv,
            "keuangan_musholla.csv",
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

    # Log login
    save_log(username, "Login", "Masuk ke panel panitia")

    df = load_data()

    # -------------------------
    # FORM TAMBAH DATA
    # -------------------------
    st.subheader("➕ Tambah Data Baru")

    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal", datetime.now(TZ))
        keterangan = st.text_input("Keterangan")
    with col2:
        masuk = st.number_input("Uang Masuk", min_value=0, step=1000)
        keluar = st.number_input("Uang Keluar", min_value=0, step=1000)

    if st.button("Simpan Data"):
        # recalc saldo: ambil saldo terakhir dari sumber (remote jika ada)
        df = load_data()
        saldo_akhir = df["Saldo"].iloc[-1] if not df.empty else 0
        saldo_baru = saldo_akhir + masuk - keluar

        new_row = {
            "Tanggal": str(tanggal),
            "Keterangan": keterangan,
            "Masuk": masuk,
            "Keluar": keluar,
            "Saldo": saldo_baru
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        ok = save_data(df)
        save_log(username, "Tambah Data", f"{keterangan} | +{masuk} / -{keluar}")

        if ok:
            st.success("Data berhasil disimpan!")
        else:
            st.warning("Data disimpan lokal karena gagal menyimpan ke GitHub.")

    # -------------------------
    # TABEL KEUANGAN
    # -------------------------
    st.subheader("📄 Tabel Keuangan")
    df = load_data()
    st.dataframe(df, use_container_width=True)

    # -------------------------
    # HAPUS DATA
    # -------------------------
    st.subheader("🗑 Hapus Baris Data")

    if not df.empty:
        idx = st.number_input(
            f"Pilih nomor baris (0 - {len(df)-1})",
            min_value=0, max_value=len(df)-1, step=1
        )

        if st.button("Hapus Baris"):
            deleted = df.iloc[idx].to_dict()
            df = df.drop(idx).reset_index(drop=True)
            ok = save_data(df)
            save_log(username, "Hapus Data", str(deleted))

            if ok:
                st.success("Baris berhasil dihapus!")
            else:
                st.warning("Perubahan disimpan lokal karena gagal menyimpan ke GitHub.")

    # -------------------------
    # DOWNLOAD CSV
    # -------------------------
    st.subheader("⬇️ Download Data")

    csv = df.to_csv(index=False).encode("utf-8")
    if st.download_button("Download CSV", csv, "keuangan_musholla.csv", "text/csv"):
        save_log(username, "Download CSV", "Mengunduh data keuangan")

    # -------------------------
    # LOG AKTIVITAS
    # -------------------------
    st.subheader("📘 Log Aktivitas Panitia")

    log_df = load_log()
    st.dataframe(log_df, use_container_width=True)

    # -------------------------
    # HAPUS LOG (KHUSUS KETUA)
    # -------------------------
    if username == "Ketua":
        st.warning("⚠️ Fitur Khusus Ketua")
        if st.button("Hapus Semua Log"):
            clear_log()
            save_log("Ketua", "Hapus Semua Log", "Log aktivitas direset ketua")
            st.success("Semua log aktivitas berhasil dihapus!")
