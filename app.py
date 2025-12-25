# =====================================================
#  APP.PY FINAL – MUSHOLLA AT-TAQWA
#  KEUANGAN + BARANG MASUK | HIJAU NU | PDF SEMI FORMAL
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
#  INISIAL FILE
# =====================================================
if not FILE_KEUANGAN.exists():
    pd.DataFrame(columns=["Tanggal","Keterangan","Kategori","Masuk","Keluar","Saldo","bukti_url"])\
        .to_csv(FILE_KEUANGAN, index=False)

if not FILE_BARANG.exists():
    pd.DataFrame(columns=["tanggal","jenis","keterangan","jumlah","satuan","bukti"])\
        .to_csv(FILE_BARANG, index=False)

if not FILE_LOG.exists():
    pd.DataFrame(columns=["Waktu","User","Aktivitas"])\
        .to_csv(FILE_LOG, index=False)

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
#  STREAMLIT & TEMA HIJAU NU
# =====================================================
st.set_page_config("Manajemen Musholla At-Taqwa", layout="wide")
st.markdown("""
<style>
.stApp { background:#f1f6f2; }
h1,h2,h3,h4 { color:#D4AF37; font-weight:800; }
.header-box {
   background:linear-gradient(90deg,#064635,#0b6e4f);
   padding:22px;border-radius:14px;color:white;margin-bottom:16px;
}
section[data-testid="stSidebar"] { background:#0b6e4f; }
section[data-testid="stSidebar"] * { color:white!important; }
.stButton>button {
    background:linear-gradient(90deg,#0b6e4f,#18a36d);
    color:white;font-weight:700;border-radius:10px;
}
.infocard {
    background:white;border-radius:14px;padding:18px;
    border:1px solid #d9e9dd;text-align:center;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
#  UTIL
# =====================================================
def read_csv_safe(p):
    try:
        return pd.read_csv(p)
    except:
        return pd.DataFrame()

def save_log(user, aktivitas):
    df = read_csv_safe(FILE_LOG)
    df = pd.concat([df, pd.DataFrame([{
        "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "User": user,
        "Aktivitas": aktivitas
    }])])
    df.to_csv(FILE_LOG, index=False)

# =====================================================
#  LOAD DATA
# =====================================================
df_keu = read_csv_safe(FILE_KEUANGAN)
df_barang = read_csv_safe(FILE_BARANG)

if not df_keu.empty:
    df_keu["Masuk"] = pd.to_numeric(df_keu["Masuk"], errors="coerce").fillna(0)
    df_keu["Keluar"] = pd.to_numeric(df_keu["Keluar"], errors="coerce").fillna(0)
    df_keu["Saldo"] = (df_keu["Masuk"] - df_keu["Keluar"]).cumsum()

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
level = st.sidebar.radio("", [
    "Publik","Ketua","Sekretaris",
    "Bendahara 1","Bendahara 2",
    "Koor Donasi 1","Koor Donasi 2"
])
is_admin = level != "Publik"

if is_admin:
    pw = st.sidebar.text_input("Password", type="password")
    if PANITIA.get(level.lower()) != pw:
        st.warning("❌ Password salah")
        st.stop()

menu = st.sidebar.radio("📂 Menu", ["💰 Keuangan","📦 Barang Masuk","📄 Laporan","🧾 Log"])

# =====================================================
#  MENU KEUANGAN
# =====================================================
if menu == "💰 Keuangan":
    st.subheader("💰 Ringkasan Keuangan")

    if not df_keu.empty:
        c1,c2,c3 = st.columns(3)
        c1.markdown(f"<div class='infocard'><h4>Total Masuk</h4><h3>Rp {df_keu['Masuk'].sum():,.0f}</h3></div>", True)
        c2.markdown(f"<div class='infocard'><h4>Total Keluar</h4><h3>Rp {df_keu['Keluar'].sum():,.0f}</h3></div>", True)
        c3.markdown(f"<div class='infocard'><h4>Saldo Akhir</h4><h3>Rp {df_keu['Saldo'].iloc[-1]:,.0f}</h3></div>", True)

        st.dataframe(df_keu, use_container_width=True)
        st.download_button("📥 Download Transaksi CSV", df_keu.to_csv(index=False),
                           "transaksi_keuangan.csv","text/csv")

    if is_admin:
        st.markdown("### ➕ Tambah Transaksi")
        with st.form("keu"):
            tgl = st.date_input("Tanggal")
            ket = st.text_input("Keterangan")
            masuk = st.number_input("Masuk",0)
            keluar = st.number_input("Keluar",0)
            if st.form_submit_button("💾 Simpan"):
                df = pd.concat([df_keu, pd.DataFrame([{
                    "Tanggal":tgl.strftime("%Y-%m-%d"),
                    "Keterangan":ket,"Kategori":"",
                    "Masuk":masuk,"Keluar":keluar,
                    "Saldo":0,"bukti_url":""
                }])])
                df["Saldo"] = (df["Masuk"]-df["Keluar"]).cumsum()
                df.to_csv(FILE_KEUANGAN,index=False)
                save_log(level,"Tambah transaksi")
                st.rerun()

# =====================================================
#  MENU BARANG MASUK
# =====================================================
elif menu == "📦 Barang Masuk":
    st.subheader("📦 Barang Masuk")

    if not df_barang.empty:
        st.dataframe(df_barang, use_container_width=True)
        st.download_button("📥 Download Barang CSV",
            df_barang.to_csv(index=False),"barang_masuk.csv","text/csv")
    else:
        st.info("Belum ada data barang.")

    if is_admin:
        st.markdown("### ➕ Tambah Barang")
        with st.form("barang"):
            tgl = st.date_input("Tanggal")
            jenis = st.text_input("Jenis Barang")
            ket = st.text_input("Keterangan")
            jumlah = st.number_input("Jumlah",1)
            satuan = st.text_input("Satuan")
            if st.form_submit_button("💾 Simpan"):
                df = pd.concat([df_barang, pd.DataFrame([{
                    "tanggal":tgl.strftime("%Y-%m-%d"),
                    "jenis":jenis,"keterangan":ket,
                    "jumlah":jumlah,"satuan":satuan,"bukti":""
                }])])
                df.to_csv(FILE_BARANG,index=False)
                save_log(level,"Tambah barang masuk")
                st.rerun()

# =====================================================
#  MENU LAPORAN – PDF DIPERINDAH (SAJA)
# =====================================================
elif menu == "📄 Laporan":
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=36,leftMargin=36,topMargin=36,bottomMargin=36
    )

    styles = getSampleStyleSheet()
    styles["Title"].textColor = colors.HexColor("#064635")
    styles["Title"].alignment = 1
    styles["Normal"].spaceAfter = 6

    el = []

    el.append(Paragraph("<b>MUSHOLLA AT-TAQWA</b>", styles["Title"]))
    el.append(Paragraph("Laporan Keuangan & Barang Masuk", styles["Normal"]))
    el.append(Paragraph(
        f"Per tanggal: {datetime.now().strftime('%d %B %Y')}",
        styles["Normal"]
    ))
    el.append(Spacer(1,12))

    # ---------- TABEL KEUANGAN ----------
    data_keu = [["Tanggal","Keterangan","Masuk","Keluar","Saldo"]]
    for _,r in df_keu.iterrows():
        data_keu.append([
            r["Tanggal"], r["Keterangan"],
            f"{int(r['Masuk']):,}",
            f"{int(r['Keluar']):,}",
            f"{int(r['Saldo']):,}"
        ])

    tbl_keu = Table(data_keu, repeatRows=1, colWidths=[70,150,70,70,70])
    tbl_keu.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#064635")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("ALIGN",(2,1),(-1,-1),"RIGHT"),
        ("FONT",(0,0),(-1,0),"Helvetica-Bold")
    ]))

    el.append(tbl_keu)
    el.append(Spacer(1,16))

    # ---------- TABEL BARANG ----------
    if not df_barang.empty:
        data_bar = [["Tanggal","Jenis","Keterangan","Jumlah","Satuan"]]
        for _,r in df_barang.iterrows():
            data_bar.append([
                r["tanggal"], r["jenis"],
                r["keterangan"], r["jumlah"], r["satuan"]
            ])

        tbl_bar = Table(data_bar, repeatRows=1, colWidths=[70,100,150,50,50])
        tbl_bar.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#064635")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("GRID",(0,0),(-1,-1),0.5,colors.grey),
            ("FONT",(0,0),(-1,0),"Helvetica-Bold")
        ]))

        el.append(tbl_bar)

    doc.build(el)
    buffer.seek(0)

    st.download_button(
        "📥 Download Laporan PDF",
        buffer,
        "Laporan_Musholla_At-Taqwa.pdf",
        "application/pdf"
    )

# =====================================================
#  MENU LOG
# =====================================================
elif menu == "🧾 Log":
    df_log = read_csv_safe(FILE_LOG)
    st.dataframe(df_log, use_container_width=True)
    st.download_button("📥 Download Log CSV",
        df_log.to_csv(index=False),"log_aktivitas.csv","text/csv")
