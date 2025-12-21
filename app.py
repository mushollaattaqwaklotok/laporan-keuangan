# app.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from io import BytesIO

# =====================================================
#  KONFIGURASI AWAL
# =====================================================
BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_KEU = UPLOADS_DIR / "keuangan"
UPLOADS_BAR = UPLOADS_DIR / "barang"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(UPLOADS_KEU, exist_ok=True)
os.makedirs(UPLOADS_BAR, exist_ok=True)

FILE_KEUANGAN = DATA_DIR / "keuangan.csv"
FILE_BARANG = DATA_DIR / "barang.csv"
FILE_LOG = DATA_DIR / "log_aktivitas.csv"

if not FILE_KEUANGAN.exists():
    pd.DataFrame(columns=["Tanggal","Keterangan","Kategori","Masuk","Keluar","Saldo","bukti_url"]).to_csv(FILE_KEUANGAN, index=False)
if not FILE_BARANG.exists():
    pd.DataFrame(columns=["tanggal","jenis","keterangan","jumlah","satuan","bukti","bukti_penerimaan"]).to_csv(FILE_BARANG, index=False)
if not FILE_LOG.exists():
    pd.DataFrame(columns=["Waktu","User","Aktivitas"]).to_csv(FILE_LOG, index=False)

PANITIA = {
    "ketua": "kelas3ku",
    "sekretaris": "fatik3762",
    "bendahara 1": "hadi5028",
    "bendahara 2": "riki6522",
    "koor donasi 1": "bayu0255",
    "koor donasi 2": "roni9044"
}

# =====================================================
#  UI – TEMA HIJAU NU
# =====================================================
st.set_page_config(page_title="Manajemen At-Taqwa", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #f1f6f2 !important; }
h1,h2,h3,h4 { color:#0b6e4f !important; font-weight:800; }
.header-box {
    background: linear-gradient(90deg,#0b6e4f,#18a36d);
    padding:22px; border-radius:14px;
    color:white; margin-bottom:16px;
}
section[data-testid="stSidebar"] { background:#0b6e4f; }
section[data-testid="stSidebar"] * { color:white !important; }
.stButton>button {
    background: linear-gradient(90deg,#0b6e4f,#18a36d);
    color:white !important;
    font-weight:700;
    border-radius:10px;
}
.infocard {
    background:white;
    border-radius:14px;
    padding:18px;
    text-align:center;
    border:1px solid #d9e9dd;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
#  UTIL
# =====================================================
def read_csv_safe(path):
    try:
        return pd.read_csv(path) if path.exists() else pd.DataFrame()
    except:
        return pd.DataFrame()

def save_csv(df, path):
    df.to_csv(path, index=False)

def preview_link(url):
    if pd.isna(url) or url == "":
        return "-"
    return f"<a href='{url}' target='_blank'>Lihat Bukti</a>"

def log_activity(user, activity):
    df = read_csv_safe(FILE_LOG)
    df.loc[len(df)] = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user, activity]
    save_csv(df, FILE_LOG)

# =====================================================
#  GENERATE PDF (OPSIONAL B – AMAN)
# =====================================================
def generate_pdf_laporan(df_keu, df_barang):
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    el = []

    el.append(Paragraph("<b>MUSHOLLA AT-TAQWA</b>", styles["Title"]))
    el.append(Paragraph("Laporan Keuangan & Barang Masuk", styles["Heading2"]))
    el.append(Paragraph(f"Tanggal Cetak: {datetime.now().strftime('%d %B %Y')}", styles["Normal"]))
    el.append(Spacer(1, 12))

    data_keu = [["Tanggal","Keterangan","Masuk","Keluar","Saldo"]]
    for _, r in df_keu.iterrows():
        data_keu.append([r["Tanggal"], r["Keterangan"], int(r["Masuk"]), int(r["Keluar"]), int(r["Saldo"])])

    tbl = Table(data_keu)
    tbl.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)
    ]))
    el.append(tbl)
    el.append(Spacer(1, 20))

    el.append(Paragraph("Ketua: Ferri Kusuma<br/>Sekretaris: Alfan Fatichul Ichsan<br/>Bendahara: Sunhadi Prayitno", styles["Normal"]))

    doc.build(el)
    buffer.seek(0)
    return buffer

# =====================================================
#  LOAD DATA
# =====================================================
df_keu = read_csv_safe(FILE_KEUANGAN)
df_barang = read_csv_safe(FILE_BARANG)

if len(df_keu) > 0:
    df_keu["Masuk"] = pd.to_numeric(df_keu["Masuk"], errors="coerce").fillna(0)
    df_keu["Keluar"] = pd.to_numeric(df_keu["Keluar"], errors="coerce").fillna(0)
    df_keu["Saldo"] = df_keu["Masuk"].cumsum() - df_keu["Keluar"].cumsum()

# =====================================================
#  HEADER
# =====================================================
st.markdown("""
<div class="header-box">
<h2>Laporan Keuangan Musholla At-Taqwa</h2>
Transparansi • Amanah • Profesional
</div>
""", unsafe_allow_html=True)

# =====================================================
#  LOGIN
# =====================================================
st.sidebar.header("Login")
level = st.sidebar.radio("", ["Publik","Ketua","Sekretaris","Bendahara 1","Bendahara 2","Koor Donasi 1","Koor Donasi 2"])

if level != "Publik":
    pw = st.sidebar.text_input("Password", type="password")
    if PANITIA.get(level.lower()) != pw:
        st.warning("Password salah")
        st.stop()

menu = st.sidebar.radio("Menu", ["💰 Keuangan","📦 Barang Masuk","📄 Laporan","🧾 Log"])

# =====================================================
#  MENU LAPORAN (PDF DI SINI)
# =====================================================
if menu == "📄 Laporan":
    st.header("📄 Laporan")
    if len(df_keu) > 0:
        df_show = df_keu.copy()
        df_show["Bukti"] = df_show["bukti_url"].apply(preview_link)
        st.markdown(df_show.to_html(escape=False), unsafe_allow_html=True)

        pdf = generate_pdf_laporan(df_keu, df_barang)
        st.download_button(
            "📥 Download Laporan PDF Resmi",
            data=pdf,
            file_name="Laporan_Musholla_At-Taqwa.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Belum ada data.")
