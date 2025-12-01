import streamlit as st
import pandas as pd
import os
from datetime import datetime
from github import Github, GithubException

# =====================================================

# KONFIGURASI AWAL

# =====================================================

DATA_DIR = "data"
UPLOADS_DIR = "uploads"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

FILE_KEUANGAN = f"{DATA_DIR}/keuangan.csv"
FILE_BARANG = f"{DATA_DIR}/barang.csv"

GITHUB_KEUANGAN = "[https://raw.githubusercontent.com/mushollaattaqwaklotok/laporan-keuangan/refs/heads/main/data/keuangan.csv](https://raw.githubusercontent.com/mushollaattaqwaklotok/laporan-keuangan/refs/heads/main/data/keuangan.csv)"
GITHUB_BARANG = "[https://raw.githubusercontent.com/mushollaattaqwaklotok/laporan-keuangan/refs/heads/main/data/barang.csv](https://raw.githubusercontent.com/mushollaattaqwaklotok/laporan-keuangan/refs/heads/main/data/barang.csv)"

PANITIA = {
"ketua": "kelas3ku",
"sekretaris": "fatik3762",
"bendahara 1": "hadi5028",
"bendahara 2": "riki6522",
"koor donasi 1": "bayu0255",
"koor donasi 2": "roni9044"
}

# =====================================================

# GITHUB PAT (letakkan token fine-grained di sini)

# =====================================================

GITHUB_PAT = "PASTE_YOUR_FINE_GRAINED_TOKEN_HERE"
REPO_NAME = "mushollaattaqwaklotok/laporan-keuangan"

try:
g = Github(GITHUB_PAT)
repo = g.get_repo(REPO_NAME)
st.sidebar.success("✅ GitHub token valid")
except GithubException as e:
st.sidebar.error(f"❌ Token invalid atau repo tidak ditemukan: {e}")
st.stop()

# =====================================================

# UTILITAS

# =====================================================

def load_csv_safe(local_file, github_url, columns):
if os.path.exists(local_file):
try:
return pd.read_csv(local_file)
except:
return pd.DataFrame(columns=columns)
try:
return pd.read_csv(github_url)
except:
return pd.DataFrame(columns=columns)

def save_csv(df, file):
df.to_csv(file, index=False)

def preview_link(url):
if pd.isna(url) or url == "":
return "-"
return f"[Lihat Bukti]({url})"

def github_upload(file_path, commit_msg="Update CSV"):
file_name = os.path.basename(file_path)
with open(file_path, "r", encoding="utf-8") as f:
content = f.read()
try:
contents = repo.get_contents(f"data/{file_name}")
repo.update_file(contents.path, commit_msg, content, contents.sha)
st.success(f"✅ Berhasil push {file_name} ke GitHub")
except Exception:
repo.create_file(f"data/{file_name}", commit_msg, content)
st.success(f"✅ File {file_name} dibuat di GitHub")

# =====================================================

# LOAD DATA

# =====================================================

df_keu = load_csv_safe(FILE_KEUANGAN, GITHUB_KEUANGAN, ["Tanggal","Keterangan","Kategori","Masuk","Keluar","Saldo","bukti_url"])
df_barang = load_csv_safe(FILE_BARANG, GITHUB_BARANG, ["tanggal","jenis","keterangan","jumlah","satuan","bukti","bukti_penerimaan"])

# =====================================================

# HEADER UI

# =====================================================

st.markdown("""

<div style="background: linear-gradient(90deg,#0b6e4f,#18a36d); padding:20px; border-radius:12px; color:white;">
<h2>Laporan Keuangan Musholla At-Taqwa</h2>
<p>Transparansi • Amanah • Profesional</p>
</div>
""", unsafe_allow_html=True)

# =====================================================

# LOGIN

# =====================================================

st.sidebar.header("Login sebagai:")
level = st.sidebar.radio("", ["Publik"] + [k.title() for k in PANITIA.keys()])

if level.lower() != "publik":
password = st.sidebar.text_input("Password:", type="password")
if level.lower() not in PANITIA or password != PANITIA[level.lower()]:
st.warning("🔒 Masukkan password yang benar.")
st.stop()

# =====================================================

# MENU UTAMA

# =====================================================

menu = st.sidebar.radio("Menu:", ["💰 Keuangan", "📦 Barang Masuk", "📄 Laporan", "🧾 Log"])

# =====================================================

# DASHBOARD KEUANGAN

# =====================================================

if menu == "💰 Keuangan":
st.header("💰 Keuangan")

```
# Info Card
if len(df_keu) > 0:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div style='background:white;padding:15px;border-radius:10px;text-align:center;'>Total Masuk<br><b>Rp {df_keu['Masuk'].sum():,}</b></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='background:white;padding:15px;border-radius:10px;text-align:center;'>Total Keluar<br><b>Rp {df_keu['Keluar'].sum():,}</b></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='background:white;padding:15px;border-radius:10px;text-align:center;'>Saldo Akhir<br><b>Rp {df_keu['Saldo'].iloc[-1]:,}</b></div>", unsafe_allow_html=True)

# Input Keuangan
st.subheader("Input Keuangan")
if level.lower() == "publik":
    st.info("🔒 Hanya panitia yang dapat input data.")
else:
    tgl = st.date_input("Tanggal")
    ket = st.text_input("Keterangan")
    kategori = st.selectbox("Kategori", ["Kas Masuk", "Kas Keluar"])
    masuk = st.number_input("Masuk (Rp)", min_value=0)
    keluar = st.number_input("Keluar (Rp)", min_value=0)
    bukti = st.file_uploader("Upload Bukti")

    if st.button("Simpan Data"):
        if ket.strip() == "":
            st.error("❌ Keterangan harus diisi!")
        else:
            try:
                bukti_url = ""
                if bukti:
                    bukti_url = f"{UPLOADS_DIR}/{bukti.name}"
                    with open(bukti_url, "wb") as f:
                        f.write(bukti.read())
                saldo_akhir = (df_keu["Saldo"].iloc[-1] if len(df_keu) else 0) + masuk - keluar
                new_row = {
                    "Tanggal": str(tgl),
                    "Keterangan": ket,
                    "Kategori": kategori,
                    "Masuk": masuk,
                    "Keluar": keluar,
                    "Saldo": saldo_akhir,
                    "bukti_url": bukti_url
                }
                df_keu = pd.concat([df_keu, pd.DataFrame([new_row])], ignore_index=True)
                save_csv(df_keu, FILE_KEUANGAN)
                github_upload(FILE_KEUANGAN, commit_msg=f"Update keuangan {tgl}")
            except Exception as e:
                st.error(f"❌ Gagal menyimpan data: {e}")

# Tabel Laporan + Download CSV
if len(df_keu) > 0:
    df_show = df_keu.copy()
    df_show["Bukti"] = df_show["bukti_url"].apply(preview_link)
    st.write(df_show.to_html(escape=False), unsafe_allow_html=True)
    st.download_button("📥 Download CSV", df_keu.to_csv(index=False).encode("utf-8"), file_name="laporan_keuangan.csv", mime="text/csv")
```
