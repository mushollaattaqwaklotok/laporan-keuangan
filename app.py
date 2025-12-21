# =====================================================
#  APP.PY FINAL – MUSHOLLA AT-TAQWA
#  TAMPILAN KEMBALI SEPERTI AWAL | HIJAU NU | PDF LENGKAP
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
os.makedirs(DATA_DIR, exist_ok=True)

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
        "tanggal","jenis","keterangan","jumlah","satuan","bukti"
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
#  SETTING STREAMLIT & TEMA HIJAU NU
# =====================================================
st.set_page_config(page_title="Manajemen Musholla At-Taqwa", layout="wide")

st.markdown("""
<style>
.stApp { background-color:#f1f6f2; }
h1,h2,h3,h4 { color:#0b6e4f; font-weight:800; }
.header-box {
    background:linear-gradient(90deg,#0b6e4f,#18a36d);
    padding:22px;
    border-radius:14px;
    color:white;
    margin-bottom:18px;
}
section[data-testid="stSidebar"] { background:#0b6e4f; }
section[data-testid="stSidebar"] * { color:white !important; }
.stButton>button {
    background:linear-gradient(90deg,#0b6e4f,#18a36d);
    color:white;
    font-weight:700;
    border-radius:10px;
}
.infocard {
    background:white;
    border-radius:14px;
    padding:18px;
    border:1px solid #d9e9dd;
    text-align:center;
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

# =====================================================
#  LOAD & NORMALISASI DATA
# =====================================================
df_keu = read_csv_safe(FILE_KEUANGAN)
df_barang = read_csv_safe(FILE_BARANG)

if not df_keu.empty:
    df_keu["Kategori"] = df_keu["Kategori"].astype(str).str.strip().str.lower()
    df_keu.loc[df_keu["Kategori"].isin(["kas masuk","kas_masuk"]), "Kategori"] = "Kas_Masuk"
    df_keu.loc[df_keu["Kategori"].isin(["kas keluar","kas_keluar"]), "Kategori"] = "Kas_Keluar"

    df_keu["Masuk"] = pd.to_numeric(df_keu["Masuk"], errors="coerce").fillna(0)
    df_keu["Keluar"] = pd.to_numeric(df_keu["Keluar"], errors="coerce").fillna(0)
    df_keu["Saldo"] = (df_keu["Masuk"] - df_keu["Keluar"]).cumsum()

# =====================================================
#  FUNGSI PDF (KEUANGAN + BARANG)
# =====================================================
def generate_pdf(df_keu, df_barang):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    el = []

    el.append(Paragraph("<b>MUSHOLLA AT-TAQWA</b>", styles["Title"]))
    el.append(Paragraph("LAPORAN KEUANGAN & BARANG MASUK", styles["Heading2"]))
    el.append(Paragraph(f"Tanggal Cetak: {datetime.now().strftime('%d %B %Y')}", styles["Normal"]))
    el.append(Spacer(1,12))

    # --- TABEL KEUANGAN ---
    el.append(Paragraph("<b>Laporan Keuangan</b>", styles["Heading3"]))
    data_keu = [["Tanggal","Keterangan","Masuk","Keluar","Saldo"]]
    for _, r in df_keu.iterrows():
        data_keu.append([
            r["Tanggal"], r["Keterangan"],
            f"{r['Masuk']:,.0f}",
            f"{r['Keluar']:,.0f}",
            f"{r['Saldo']:,.0f}"
        ])

    tbl_keu = Table(data_keu, repeatRows=1)
    tbl_keu.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("ALIGN",(2,1),(-1,-1),"RIGHT")
    ]))
    el.append(tbl_keu)
    el.append(Spacer(1,16))

    # --- TABEL BARANG ---
    if not df_barang.empty:
        el.append(Paragraph("<b>Laporan Barang Masuk</b>", styles["Heading3"]))
        data_bar = [["Tanggal","Jenis","Keterangan","Jumlah","Satuan"]]
        for _, r in df_barang.iterrows():
            data_bar.append([
                r.get("tanggal",""),
                r.get("jenis",""),
                r.get("keterangan",""),
                r.get("jumlah",""),
                r.get("satuan","")
            ])

        tbl_bar = Table(data_bar, repeatRows=1)
        tbl_bar.setStyle(TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,colors.grey),
            ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)
        ]))
        el.append(tbl_bar)

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
level = st.sidebar.radio("", ["Publik","Ketua","Sekretaris","Bendahara 1","Bendahara 2","Koor Donasi 1","Koor Donasi 2"])

if level != "Publik":
    pw = st.sidebar.text_input("Password", type="password")
    if PANITIA.get(level.lower()) != pw:
        st.warning("❌ Password salah")
        st.stop()

menu = st.sidebar.radio("📂 Menu", ["💰 Keuangan","📦 Barang Masuk","📄 Laporan","🧾 Log"])

# =====================================================
#  MENU KEUANGAN (RINGKASAN DI ATAS – SEPERTI AWAL)
# =====================================================
if menu == "💰 Keuangan":
    st.subheader("💰 Ringkasan Keuangan")

    if not df_keu.empty:
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"<div class='infocard'><h4>Total Masuk</h4><h3>Rp {df_keu['Masuk'].sum():,.0f}</h3></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='infocard'><h4>Total Keluar</h4><h3>Rp {df_keu['Keluar'].sum():,.0f}</h3></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='infocard'><h4>Saldo Akhir</h4><h3>Rp {df_keu['Saldo'].iloc[-1]:,.0f}</h3></div>", unsafe_allow_html=True)

        st.markdown("### 📄 Detail Transaksi")
        st.dataframe(df_keu, use_container_width=True)
    else:
        st.info("Belum ada data keuangan.")

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
#  MENU LAPORAN (KEU + BARANG + PDF)
# =====================================================
elif menu == "📄 Laporan":
    st.subheader("📄 Laporan Resmi")

    st.markdown("### 💰 Laporan Keuangan")
    st.dataframe(df_keu, use_container_width=True)

    st.markdown("### 📦 Laporan Barang Masuk")
    if df_barang.empty:
        st.info("Belum ada data barang.")
    else:
        st.dataframe(df_barang, use_container_width=True)

    pdf = generate_pdf(df_keu, df_barang)
    st.download_button(
        "📥 Download Laporan PDF Resmi",
        data=pdf,
        file_name="Laporan_Musholla_At-Taqwa.pdf",
        mime="application/pdf"
    )

# =====================================================
#  MENU LOG
# =====================================================
elif menu == "🧾 Log":
    df_log = read_csv_safe(FILE_LOG)
    st.subheader("🧾 Log Aktivitas")
    if df_log.empty:
        st.info("Belum ada log.")
    else:
        st.dataframe(df_log, use_container_width=True)
