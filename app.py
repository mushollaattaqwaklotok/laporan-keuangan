import streamlit as st
import pandas as pd
import os
from datetime import datetime
from github import Github

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

# GITHUB PAT

# =====================================================

GITHUB_PAT = "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"
REPO_NAME = "mushollaattaqwaklotok/laporan-keuangan"
g = Github(GITHUB_PAT)
repo = g.get_repo(REPO_NAME)

# =====================================================

# UI PREMIUM – Hanya Tampilan

# =====================================================

st.markdown("""

<style>
.stApp { background-color: #f4f7f5 !important; }
h1,h2,h3,h4 { color:#0b6e4f !important; font-weight:800; }
.header-box { background: linear-gradient(90deg,#0b6e4f,#18a36d); padding:22px 26px; border-radius:14px; color:white !important; margin-bottom:16px; }
.header-title { font-size:30px; font-weight:900; }
.header-sub { opacity:.85; margin-top:-6px; }
section[data-testid="stSidebar"] { background:#0b6e4f; padding:20px; }
section[data-testid="stSidebar"] * { color:white !important; }
.stButton>button { background: linear-gradient(90deg,#0b6e4f,#18a36d); color:white !important; font-weight:700; padding:8px 22px; border-radius:10px; }
.stButton>button:hover { background: linear-gradient(90deg,#18a36d,#0b6e4f); transform:scale(1.03); }
input, textarea, select { border-radius:10px !important; border:1px solid #0b6e4f !important; }
.infocard { background:white; border-radius:14px; padding:18px; text-align:center; border:1px solid #d9e9dd; margin-bottom:15px; }
.infocard h3 { margin:4px 0; font-size:20px; }
.infocard p { margin:0; font-weight:700; font-size:18px; }
.dataframe th { background:#0b6e4f !important; color:white !important; padding:8px !important; }
.dataframe td { padding:6px !important; border:1px solid #c8e6d3 !important; }
</style>

""", unsafe_allow_html=True)

# =====================================================

# FUNGSI UTILITAS

# =====================================================

def load_csv_safe(local_file, github_url, columns):
if os.path.exists(local_file):
try:
return pd.read_csv(local_file)
except Exception:
return pd.DataFrame(columns=columns)
try:
return pd.read_csv(github_url)
except Exception:
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
except Exception:
repo.create_file(f"data/{file_name}", commit_msg, content)

# =====================================================

# LOAD DATA

# =====================================================

df_keu = load_csv_safe(FILE_KEUANGAN, GITHUB_KEUANGAN, ["Tanggal","Keterangan","Kategori","Masuk","Keluar","Saldo","bukti_url"])
df_barang = load_csv_safe(FILE_BARANG, GITHUB_BARANG, ["tanggal","jenis","keterangan","jumlah","satuan","bukti","bukti_penerimaan"])

# =====================================================

# HEADER UI

# =====================================================

st.markdown("""

<div class="header-box">
    <div class="header-title">Laporan Keuangan Musholla At-Taqwa</div>
    <div class="header-sub">Transparansi • Amanah • Profesional</div>
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
        st.markdown(f"<div class='infocard'><h3>Total Masuk</h3><p>Rp {df_keu['Masuk'].sum():,}</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='infocard'><h3>Total Keluar</h3><p>Rp {df_keu['Keluar'].sum():,}</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='infocard'><h3>Saldo Akhir</h3><p>Rp {df_keu['Saldo'].iloc[-1]:,}</p></div>", unsafe_allow_html=True)

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
                st.success("✅ Data berhasil disimpan!")
            except Exception as e:
                st.error(f"❌ Gagal menyimpan data: {e}")

# Tabel Laporan + Download CSV
if len(df_keu) > 0:
    df_show = df_keu.copy()
    df_show["Bukti"] = df_show["bukti_url"].apply(preview_link)
    st.write(df_show.to_html(escape=False), unsafe_allow_html=True)
    st.subheader("Download CSV")
    csv_data = df_keu.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", csv_data, file_name="laporan_keuangan.csv", mime="text/csv")
```

# =====================================================

# BARANG MASUK

# =====================================================

elif menu == "📦 Barang Masuk":
st.header("📦 Barang Masuk")

```
if level.lower() == "publik":
    st.info("🔒 Hanya panitia yang dapat input data.")
else:
    tgl_b = st.date_input("Tanggal Barang")
    jenis_b = st.text_input("Jenis Barang")
    ket_b = st.text_input("Keterangan")
    jml_b = st.number_input("Jumlah", min_value=0)
    satuan_b = st.text_input("Satuan")
    bukti_b = st.file_uploader("Upload Bukti Penerimaan")

    if st.button("Simpan Barang"):
        if jenis_b.strip() == "" or ket_b.strip() == "":
            st.error("❌ Jenis dan Keterangan barang harus diisi!")
        else:
            try:
                bukti_url = ""
                if bukti_b:
                    bukti_url = f"{UPLOADS_DIR}/{bukti_b.name}"
                    with open(bukti_url, "wb") as f:
                        f.write(bukti_b.read())

                new_b = {
                    "tanggal": str(tgl_b),
                    "jenis": jenis_b,
                    "keterangan": ket_b,
                    "jumlah": jml_b,
                    "satuan": satuan_b,
                    "bukti": bukti_url,
                    "bukti_penerimaan": bukti_url
                }
                df_barang = pd.concat([df_barang, pd.DataFrame([new_b])], ignore_index=True)
                save_csv(df_barang, FILE_BARANG)
                github_upload(FILE_BARANG, commit_msg=f"Update barang {tgl_b}")
                st.success("✅ Data barang berhasil disimpan!")
            except Exception as e:
                st.error(f"❌ Gagal menyimpan data barang: {e}")

if len(df_barang) > 0:
    st.write(df_barang)
```

# =====================================================

# LAPORAN

# =====================================================

elif menu == "📄 Laporan":
st.header("📄 Laporan Keuangan")
if len(df_keu) > 0:
df_show = df_keu.copy()
df_show["Bukti"] = df_show["bukti_url"].apply(preview_link)
st.write(df_show.to_html(escape=False), unsafe_allow_html=True)
else:
st.info("Belum ada data.")

# =====================================================

# LOG (Placeholder)

# =====================================================

elif menu == "🧾 Log":
st.header("🧾 Log Aktivitas")
st.info("Fitur log akan dibuat jika dibutuhkan.")
