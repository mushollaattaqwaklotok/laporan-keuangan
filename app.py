# =====================================================
#  APP.PY FINAL – MUSHOLLA AT-TAQWA
#  Hijau NU | Login Aman | PDF Resmi | Data Bersih
# =====================================================

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from io import BytesIO

# =====================================================
#  KONFIGURASI DIREKTORI
# =====================================================
BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_KEU = UPLOADS_DIR / "keuangan"
UPLOADS_BAR = UPLOADS_DIR / "barang"

for d in [DATA_DIR, UPLOADS_DIR, UPLOADS_KEU, UPLOADS_BAR]:
    os.makedirs(d, exist_ok=True)

FILE_KEUANGAN = DATA_DIR / "keuangan.csv"
FILE_BARANG = DATA_DIR / "barang.csv"
FILE_LOG = DATA_DIR / "log_aktivitas.csv"

# =====================================================
#  INISIAL FILE JIKA BELUM ADA
# =====================================================
if not FILE_KEUANGAN.exists():
    pd.DataFrame(columns=[
        "Tanggal","Keterangan","Kategori","Masuk","Keluar","Saldo","bukti_url"
    ]).to_csv(FILE_KEUANGAN, index=False)

if not FILE_BARANG.exists():
    pd.DataFrame(columns=[
        "tanggal","jenis","keterangan","jumlah","satuan","bukti","bukti_penerimaan"
    ]).to_csv(FILE_BARANG, index=False)

if not FILE_LOG.exists():
    pd.DataFrame(columns=["Waktu","User","Aktivitas"]).to_csv(FILE_LOG, index=False)

# =====================================================
#  AKUN PANITIA
# =====================================================
PANITIA = {
    "ketua": "kelas3ku",
    "sekretaris": "fatik3762",
    "bendahara 1": "hadi5028",
    "bendahara 2": "riki6522",
    "koor donasi 1": "bayu0255",
    "koor donasi 2": "roni9044"
}

# =====================================================
#  TEMA HIJAU NU
# =====================================================
st.set_page_config(page_title="Manajemen Musholla At-Taqwa", layout="wide")

st.markdown("""
<style>
.stApp { background-color:#f1f6f2; }
h1,h2,h3,h4 { color:#0b6e4f; font-weight:800; }
.header-box {
    background:linear-gradient(90deg,#0b6e4f,#18a36d);
    padding:22px; border-radius:14px;
    color:white; margin-bottom:18px;
}
section[data-testid="stSidebar"] { background:#0b6e4f; }
section[data-testid="stSidebar"] * { color:white !important; }
.stButton>button {
    background:linear-gradient(90deg,#0b6e4f,#18a36d);
    color:white; font-weight:700; border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
#  UTIL
# =====================================================
def read_csv_safe(path):
    try:
        return pd.read_csv(path)
    except:
        return pd.DataFrame()

def save_csv(df, path):
    df.to_csv(path, index=False)

def log_activity(user, aktivitas):
    df = read_csv_safe(FILE_LOG)
    df.loc[len(df)] = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user,
        aktivitas
    ]
    save_csv(df, FILE_LOG)

# =====================================================
#  LOAD & NORMALISASI DATA KEUANGAN (KUNCI UTAMA)
# =====================================================
df_keu = read_csv_safe(FILE_KEUANGAN)

if not df_keu.empty:
    # Normalisasi kategori
    df_keu["Kategori"] = (
        df_keu["Kategori"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df_keu.loc[df_keu["Kategori"].isin(["kas masuk","kas_masuk"]), "Kategori"] = "Kas_Masuk"
    df_keu.loc[df_keu["Kategori"].isin(["kas keluar","kas_keluar"]), "Kategori"] = "Kas_Keluar"

    # Pastikan angka
    df_keu["Masuk"] = pd.to_numeric(df_keu["Masuk"], errors="coerce").fillna(0)
    df_keu["Keluar"] = pd.to_numeric(df_keu["Keluar"], errors="coerce").fillna(0)

    # Hitung saldo ulang (AMAN)
    df_keu["Saldo"] = (df_keu["Masuk"] - df_keu["Keluar"]).cumsum()

df_barang = read_csv_safe(FILE_BARANG)

# =====================================================
#  HEADER
# =====================================================
st.markdown("""
<div class="header-box">
<h2>📊 Laporan Keuangan Musholla At-Taqwa</h2>
Transparansi • Amanah • Profesional
</div>
""", unsafe_allow_html=True)

# =====================================================
#  LOGIN
# =====================================================
st.sidebar.header("🔐 Login")
level = st.sidebar.radio(
    "",
    ["Publik","Ketua","Sekretaris","Bendahara 1","Bendahara 2","Koor Donasi 1","Koor Donasi 2"]
)

user_login = level

if level != "Publik":
    pw = st.sidebar.text_input("Password", type="password")
    if PANITIA.get(level.lower()) != pw:
        st.warning("❌ Password salah")
        st.stop()

menu = st.sidebar.radio(
    "📂 Menu",
    ["💰 Keuangan","📦 Barang Masuk","📄 Laporan","🧾 Log"]
)

# =====================================================
#  MENU KEUANGAN
# =====================================================
if menu == "💰 Keuangan":
    st.subheader("💰 Data Keuangan")

    if df_keu.empty:
        st.info("Belum ada data keuangan.")
    else:
        st.dataframe(df_keu, use_container_width=True)

        total_masuk = df_keu["Masuk"].sum()
        total_keluar = df_keu["Keluar"].sum()
        saldo = df_keu["Saldo"].iloc[-1]

        col1,col2,col3 = st.columns(3)
        col1.metric("Total Masuk", f"Rp {total_masuk:,.0f}")
        col2.metric("Total Keluar", f"Rp {total_keluar:,.0f}")
        col3.metric("Saldo Akhir", f"Rp {saldo:,.0f}")

# =====================================================
#  MENU BARANG
# =====================================================
elif menu == "📦 Barang Masuk":
    st.subheader("📦 Barang Masuk")
    if df_barang.empty:
        st.info("Belum ada data barang.")
    else:
        st.dataframe(df_barang, use_container_width=True)

# =====================================================
#  PDF LAPORAN
# =====================================================
def generate_pdf(df):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    el = []

    el.append(Paragraph("<b>MUSHOLLA AT-TAQWA</b>", styles["Title"]))
    el.append(Paragraph("LAPORAN KEUANGAN RESMI", styles["Heading2"]))
    el.append(Paragraph(
        f"Tanggal Cetak: {datetime.now().strftime('%d %B %Y')}",
        styles["Normal"]
    ))
    el.append(Spacer(1,12))

    data = [["Tanggal","Keterangan","Masuk","Keluar","Saldo"]]
    for _,r in df.iterrows():
        data.append([
            r["Tanggal"], r["Keterangan"],
            f"{r['Masuk']:,.0f}",
            f"{r['Keluar']:,.0f}",
            f"{r['Saldo']:,.0f}"
        ])

    tbl = Table(data, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("ALIGN",(2,1),(-1,-1),"RIGHT")
    ]))
    el.append(tbl)
    el.append(Spacer(1,20))

    el.append(Paragraph(
        "Ketua: Ferri Kusuma<br/>"
        "Sekretaris: Alfan Fatichul Ichsan<br/>"
        "Bendahara: Sunhadi Prayitno",
        styles["Normal"]
    ))

    doc.build(el)
    buffer.seek(0)
    return buffer

# =====================================================
#  MENU LAPORAN
# =====================================================
elif menu == "📄 Laporan":
    st.subheader("📄 Laporan Resmi")

    if df_keu.empty:
        st.info("Belum ada data.")
    else:
        st.dataframe(df_keu, use_container_width=True)

        pdf = generate_pdf(df_keu)
        st.download_button(
            "📥 Download Laporan PDF Resmi",
            data=pdf,
            file_name="Laporan_Musholla_At-Taqwa.pdf",
            mime="application/pdf"
        )

# =====================================================
#  LOG AKTIVITAS
# =====================================================
elif menu == "🧾 Log":
    st.subheader("🧾 Log Aktivitas")
    df_log = read_csv_safe(FILE_LOG)
    if df_log.empty:
        st.info("Belum ada log.")
    else:
        st.dataframe(df_log, use_container_width=True)
