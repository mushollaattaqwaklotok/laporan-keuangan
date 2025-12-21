# =====================================================
#  app.py - FINAL VERSION
#  Manajemen Keuangan Musholla At-Taqwa
# =====================================================

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import io

# ===== PDF LIBRARY =====
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

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

# ===== DATA PANITIA RESMI =====
NAMA_KETUA = "Ferri Kusuma"
NAMA_SEKRETARIS = "Alfan Fatichul Ichsan"
NAMA_BENDAHARA = "Sunhadi Prayitno"

# ===== AKUN PANITIA =====
PANITIA = {
    "ketua": "kelas3ku",
    "sekretaris": "fatik3762",
    "bendahara 1": "hadi5028",
    "bendahara 2": "riki6522",
    "koor donasi 1": "bayu0255",
    "koor donasi 2": "roni9044"
}

# =====================================================
#  INIT FILE
# =====================================================
if not FILE_KEUANGAN.exists():
    pd.DataFrame(columns=["Tanggal","Keterangan","Kategori","Masuk","Keluar","Saldo","bukti_url"]).to_csv(FILE_KEUANGAN, index=False)

if not FILE_BARANG.exists():
    pd.DataFrame(columns=["tanggal","jenis","keterangan","jumlah","satuan","bukti"]).to_csv(FILE_BARANG, index=False)

if not FILE_LOG.exists():
    pd.DataFrame(columns=["Waktu","User","Aktivitas"]).to_csv(FILE_LOG, index=False)

# =====================================================
#  UTIL
# =====================================================
def read_csv(path):
    try:
        return pd.read_csv(path)
    except:
        return pd.DataFrame()

def save_csv(df, path):
    df.to_csv(path, index=False)

def log_activity(user, activity):
    df = read_csv(FILE_LOG)
    df = pd.concat([df, pd.DataFrame([{
        "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "User": user,
        "Aktivitas": activity
    }])], ignore_index=True)
    save_csv(df, FILE_LOG)

def save_uploaded_file(uploaded, folder):
    if uploaded is None:
        return ""
    path = folder / uploaded.name
    if path.exists():
        path = folder / f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded.name}"
    with open(path, "wb") as f:
        f.write(uploaded.getbuffer())
    return str(path)

# =====================================================
#  PDF GENERATOR
# =====================================================
def generate_pdf_laporan(df, periode):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>LAPORAN KEUANGAN</b>", styles["Title"]))
    elements.append(Paragraph("<b>MUSHOLLA AT-TAQWA</b>", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Periode: {periode}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    total_masuk = df["Masuk"].sum()
    total_keluar = df["Keluar"].sum()
    saldo = df["Saldo"].iloc[-1] if len(df) else 0

    ringkasan = [
        ["Total Masuk", f"Rp {int(total_masuk):,}"],
        ["Total Keluar", f"Rp {int(total_keluar):,}"],
        ["Saldo Akhir", f"Rp {int(saldo):,}"]
    ]

    table_ring = Table(ringkasan, colWidths=[200,200])
    table_ring.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,colors.black),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)
    ]))
    elements.append(table_ring)
    elements.append(Spacer(1, 16))

    data = [["Tanggal","Keterangan","Masuk","Keluar","Saldo"]]
    for _, r in df.iterrows():
        data.append([
            r["Tanggal"], r["Keterangan"],
            f"{int(r['Masuk']):,}",
            f"{int(r['Keluar']):,}",
            f"{int(r['Saldo']):,}"
        ])

    table = Table(data, repeatRows=1, colWidths=[80,200,70,70,70])
    table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("ALIGN",(2,1),(-1,-1),"RIGHT")
    ]))
    elements.append(table)
    elements.append(Spacer(1, 40))

    ttd = Table([
        ["Mengetahui,", "", "Menyetujui,"],
        ["Ketua", "", "Bendahara"],
        ["", "", ""],
        [f"( {NAMA_KETUA} )", "", f"( {NAMA_BENDAHARA} )"],
        ["", "", ""],
        ["Sekretaris", "", ""],
        ["", "", ""],
        [f"( {NAMA_SEKRETARIS} )", "", ""]
    ], colWidths=[200,50,200])

    ttd.setStyle(TableStyle([
        ("ALIGN",(0,0),(-1,-1),"CENTER")
    ]))

    elements.append(ttd)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# =====================================================
#  UI
# =====================================================
st.set_page_config("Manajemen At-Taqwa", layout="wide")

st.markdown("""
<h2 style='color:#0b6e4f'>Laporan Keuangan Musholla At-Taqwa</h2>
<p><b>Transparansi • Amanah • Profesional</b></p>
<hr>
""", unsafe_allow_html=True)

# =====================================================
#  LOGIN
# =====================================================
st.sidebar.header("Login")
level = st.sidebar.radio("Akses:", [
    "Publik","Ketua","Sekretaris",
    "Bendahara 1","Bendahara 2",
    "Koor Donasi 1","Koor Donasi 2"
])

if level != "Publik":
    pw = st.sidebar.text_input("Password", type="password")
    if pw != PANITIA.get(level.lower(),""):
        st.warning("Password salah")
        st.stop()

menu = st.sidebar.radio("Menu", ["💰 Keuangan","📄 Laporan"])

# =====================================================
#  LOAD DATA
# =====================================================
df_keu = read_csv(FILE_KEUANGAN)
df_keu[["Masuk","Keluar"]] = df_keu[["Masuk","Keluar"]].fillna(0)
df_keu["Saldo"] = df_keu["Masuk"].cumsum() - df_keu["Keluar"].cumsum()

# =====================================================
#  MENU LAPORAN
# =====================================================
if menu == "📄 Laporan":
    st.subheader("📄 Laporan Keuangan Resmi")
    st.dataframe(df_keu, use_container_width=True)

    periode = st.text_input(
        "Periode Laporan",
        value=f"{df_keu['Tanggal'].min()} s/d {df_keu['Tanggal'].max()}"
    )

    if st.button("📄 Download Laporan PDF Resmi"):
        pdf = generate_pdf_laporan(df_keu, periode)
        st.download_button(
            "⬇️ Klik Download PDF",
            pdf,
            "laporan_keuangan_musholla_attaqwa.pdf",
            mime="application/pdf"
        )
