# =====================================================
# app.py FINAL – Manajemen Musholla At-Taqwa
# =====================================================

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import io

# ===== PDF =====
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table,
    TableStyle, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# =====================================================
# KONFIGURASI AWAL
# =====================================================
BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_KEU = UPLOADS_DIR / "keuangan"
UPLOADS_BAR = UPLOADS_DIR / "barang"
ASSETS_DIR = BASE_DIR / "assets"

for d in [DATA_DIR, UPLOADS_DIR, UPLOADS_KEU, UPLOADS_BAR, ASSETS_DIR]:
    os.makedirs(d, exist_ok=True)

FILE_KEUANGAN = DATA_DIR / "keuangan.csv"
FILE_BARANG = DATA_DIR / "barang.csv"
FILE_LOG = DATA_DIR / "log_aktivitas.csv"

LOGO_PATH = ASSETS_DIR / "logo_attaqwa.png"

# ===== DATA PANITIA =====
NAMA_KETUA = "Ferri Kusuma"
NAMA_SEKRETARIS = "Alfan Fatichul Ichsan"
NAMA_BENDAHARA = "Sunhadi Prayitno"

# ===== AKUN =====
PANITIA = {
    "ketua": "kelas3ku",
    "sekretaris": "fatik3762",
    "bendahara 1": "hadi5028",
    "bendahara 2": "riki6522",
    "koor donasi 1": "bayu0255",
    "koor donasi 2": "roni9044"
}

# =====================================================
# INIT FILE
# =====================================================
if not FILE_KEUANGAN.exists():
    pd.DataFrame(columns=[
        "Tanggal","Keterangan","Kategori",
        "Masuk","Keluar","Saldo","bukti_url"
    ]).to_csv(FILE_KEUANGAN, index=False)

if not FILE_BARANG.exists():
    pd.DataFrame(columns=[
        "tanggal","jenis","keterangan",
        "jumlah","satuan","bukti"
    ]).to_csv(FILE_BARANG, index=False)

if not FILE_LOG.exists():
    pd.DataFrame(columns=["Waktu","User","Aktivitas"]).to_csv(FILE_LOG, index=False)

# =====================================================
# UTIL
# =====================================================
def read_csv_safe(path):
    try:
        return pd.read_csv(path)
    except:
        return pd.DataFrame()

def save_csv(df, path):
    df.to_csv(path, index=False)

# =====================================================
# PDF GENERATOR
# =====================================================
def generate_pdf_laporan(df, periode_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=36, leftMargin=36,
        topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()
    elements = []

    # ===== HEADER LOGO =====
    if LOGO_PATH.exists():
        logo = Image(str(LOGO_PATH), width=70, height=70)
        elements.append(logo)

    elements.append(Paragraph("<b>LAPORAN KEUANGAN</b>", styles["Title"]))
    elements.append(Paragraph("<b>MUSHOLLA AT-TAQWA</b>", styles["Title"]))
    elements.append(Spacer(1, 6))

    tanggal_cetak = datetime.now().strftime("%d %B %Y")
    elements.append(Paragraph(
        f"Periode: {periode_text}<br/>Tanggal Cetak: {tanggal_cetak}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 12))

    # ===== RINGKASAN =====
    total_masuk = df["Masuk"].sum()
    total_keluar = df["Keluar"].sum()
    saldo = df["Saldo"].iloc[-1] if len(df) else 0

    ringkasan = [
        ["Total Masuk", f"Rp {int(total_masuk):,}"],
        ["Total Keluar", f"Rp {int(total_keluar):,}"],
        ["Saldo Akhir", f"Rp {int(saldo):,}"]
    ]

    t_ring = Table(ringkasan, colWidths=[200, 200])
    t_ring.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)
    ]))
    elements.append(t_ring)
    elements.append(Spacer(1, 14))

    # ===== TABEL DATA =====
    data = [["Tanggal","Keterangan","Masuk","Keluar","Saldo"]]
    for _, r in df.iterrows():
        data.append([
            r["Tanggal"],
            r["Keterangan"],
            f"{int(r['Masuk']):,}",
            f"{int(r['Keluar']):,}",
            f"{int(r['Saldo']):,}"
        ])

    table = Table(data, repeatRows=1,
                  colWidths=[80, 190, 70, 70, 70])
    table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("ALIGN",(2,1),(-1,-1),"RIGHT")
    ]))
    elements.append(table)
    elements.append(Spacer(1, 36))

    # ===== TANDA TANGAN =====
    ttd = Table([
        ["Mengetahui,", "", "Menyetujui,"],
        ["Ketua", "", "Bendahara"],
        ["", "", ""],
        [f"( {NAMA_KETUA} )", "", f"( {NAMA_BENDAHARA} )"],
        ["", "", ""],
        ["Sekretaris", "", ""],
        ["", "", ""],
        [f"( {NAMA_SEKRETARIS} )", "", ""]
    ], colWidths=[200, 50, 200])

    ttd.setStyle(TableStyle([
        ("ALIGN",(0,0),(-1,-1),"CENTER")
    ]))
    elements.append(ttd)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# =====================================================
# UI – TETAP HIJAU NU (ASLI)
# =====================================================
st.set_page_config("Manajemen At-Taqwa", layout="wide")

st.markdown("""
<style>
.stApp { background-color:#f1f6f2; }
h1,h2,h3 { color:#0b6e4f; font-weight:800; }
</style>
""", unsafe_allow_html=True)

st.markdown("## Laporan Keuangan Musholla At-Taqwa")
st.markdown("**Transparansi • Amanah • Profesional**")
st.markdown("---")

# =====================================================
# LOGIN
# =====================================================
st.sidebar.header("Login")
level = st.sidebar.radio("Akses", [
    "Publik","Ketua","Sekretaris",
    "Bendahara 1","Bendahara 2",
    "Koor Donasi 1","Koor Donasi 2"
])

if level != "Publik":
    pw = st.sidebar.text_input("Password", type="password")
    if pw != PANITIA.get(level.lower(),""):
        st.warning("Password salah")
        st.stop()

menu = st.sidebar.radio("Menu", ["📄 Laporan"])

# =====================================================
# LOAD DATA
# =====================================================
df_keu = read_csv_safe(FILE_KEUANGAN)
if len(df_keu):
    df_keu[["Masuk","Keluar"]] = df_keu[["Masuk","Keluar"]].fillna(0)
    df_keu["Saldo"] = df_keu["Masuk"].cumsum() - df_keu["Keluar"].cumsum()

# =====================================================
# MENU LAPORAN (TAMBAHAN SAJA)
# =====================================================
if menu == "📄 Laporan":
    st.dataframe(df_keu, use_container_width=True)

    periode = st.text_input(
        "Periode Laporan",
        value=f"{df_keu['Tanggal'].min()} s/d {df_keu['Tanggal'].max()}"
        if len(df_keu) else "-"
    )

    if st.button("📄 Download Laporan PDF Resmi"):
        pdf = generate_pdf_laporan(df_keu, periode)
        st.download_button(
            "⬇️ Klik Download PDF",
            pdf,
            "laporan_keuangan_musholla_attaqwa.pdf",
            mime="application/pdf"
        )
