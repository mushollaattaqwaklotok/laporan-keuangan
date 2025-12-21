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
#  UI (Hijau NU)
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
section[data-testid="stSidebar"] { background:#0b6e4f; padding:20px; }
section[data-testid="stSidebar"] * { color:white !important; }
.stButton>button {
    background: linear-gradient(90deg,#0b6e4f,#18a36d);
    color:white; font-weight:700;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
#  UTIL
# =====================================================
def read_csv_safe(path):
    try:
        return pd.read_csv(path) if path.exists() else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def save_csv(df, path):
    df.to_csv(path, index=False)

def preview_link(url):
    if pd.isna(url) or url == "":
        return "-"
    return f"<a href='{url}' target='_blank'>Lihat Bukti</a>"

def save_uploaded_file(uploaded, dest):
    if not uploaded:
        return ""
    path = dest / uploaded.name
    with open(path, "wb") as f:
        f.write(uploaded.getbuffer())
    return str(path)

# =====================================================
#  PDF GENERATOR (AMAN)
# =====================================================
def generate_pdf(df_keu, df_barang):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception:
        return None

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    y = h - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(w/2, y, "MUSHOLLA AT-TAQWA")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawCentredString(w/2, y, "LAPORAN KEUANGAN & BARANG MASUK")
    y -= 15
    c.drawCentredString(w/2, y, f"Tanggal Cetak: {datetime.now().strftime('%d %B %Y')}")
    y -= 30

    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, "LAPORAN KEUANGAN")
    y -= 15
    c.setFont("Helvetica", 9)

    for _, r in df_keu.iterrows():
        c.drawString(40, y, f"{r['Tanggal']} | {r['Keterangan']} | +{int(r['Masuk'])} | -{int(r['Keluar'])} | {int(r['Saldo'])}")
        y -= 12
        if y < 100:
            c.showPage()
            y = h - 50

    y -= 20
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, "BARANG MASUK")
    y -= 15
    c.setFont("Helvetica", 9)

    for _, r in df_barang.iterrows():
        c.drawString(40, y, f"{r['tanggal']} | {r['jenis']} | {r['jumlah']} {r['satuan']}")
        y -= 12
        if y < 100:
            c.showPage()
            y = h - 50

    y = 120
    c.drawString(40, y, "Ketua")
    c.drawString(220, y, "Sekretaris")
    c.drawString(400, y, "Bendahara")
    y -= 40
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Ferri Kusuma")
    c.drawString(220, y, "Alfan Fatichul Ichsan")
    c.drawString(400, y, "Sunhadi Prayitno")

    c.save()
    buffer.seek(0)
    return buffer

# =====================================================
#  LOAD DATA
# =====================================================
df_keu = read_csv_safe(FILE_KEUANGAN)
df_barang = read_csv_safe(FILE_BARANG)
df_log = read_csv_safe(FILE_LOG)

# =====================================================
#  HEADER
# =====================================================
st.markdown("""
<div class="header-box">
<h2>Laporan Keuangan Musholla At-Taqwa</h2>
<p>Transparansi • Amanah • Profesional</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
#  LOGIN
# =====================================================
level = st.sidebar.radio("Login sebagai:", ["Publik","Ketua","Sekretaris","Bendahara 1","Bendahara 2","Koor Donasi 1","Koor Donasi 2"])

if level != "Publik":
    pw = st.sidebar.text_input("Password", type="password")
    if level.lower() not in PANITIA or pw != PANITIA[level.lower()]:
        st.stop()

menu = st.sidebar.radio("Menu", ["💰 Keuangan","📦 Barang Masuk","📄 Laporan","🧾 Log"])

# =====================================================
#  MENU LAPORAN (PDF ADA DI SINI)
# =====================================================
if menu == "📄 Laporan":
    st.header("📄 Laporan Resmi")

    if not df_keu.empty:
        df_show = df_keu.copy()
        df_show["Bukti"] = df_show["bukti_url"].apply(preview_link)
        st.markdown(df_show.to_html(escape=False), unsafe_allow_html=True)

        st.markdown("### 📥 Unduh Laporan PDF")
        pdf = generate_pdf(df_keu, df_barang)
        if pdf:
            st.download_button(
                "⬇️ Download Laporan PDF Resmi",
                data=pdf,
                file_name="Laporan_Musholla_At-Taqwa.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("PDF belum aktif (library belum tersedia di server).")
    else:
        st.info("Belum ada data.")
