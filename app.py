import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
from io import BytesIO

# ===============================
# KONFIGURASI DASAR
# ===============================
st.set_page_config(page_title="Laporan Keuangan Musholla At-Taqwa", layout="wide")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FILE_KEU = DATA_DIR / "keuangan.csv"
FILE_BARANG = DATA_DIR / "barang_masuk.csv"

# ===============================
# WARNA HIJAU NU (AMAN)
# ===============================
st.markdown("""
<style>
body { background-color: #f5fff7; }
h1, h2, h3 { color: #0b6b3a; }
.stButton>button { background-color:#0b6b3a; color:white; }
</style>
""", unsafe_allow_html=True)

# ===============================
# DATA DEFAULT (AMAN JIKA FILE BELUM ADA)
# ===============================
if not FILE_KEU.exists():
    pd.DataFrame(columns=["Tanggal", "Keterangan", "Masuk", "Keluar", "Saldo"]).to_csv(FILE_KEU, index=False)

if not FILE_BARANG.exists():
    pd.DataFrame(columns=["Tanggal", "Nama Barang", "Jumlah", "Satuan", "Keterangan"]).to_csv(FILE_BARANG, index=False)

df_keu = pd.read_csv(FILE_KEU)
df_barang = pd.read_csv(FILE_BARANG)

# ===============================
# HEADER
# ===============================
st.title("📊 Sistem Keuangan Musholla At-Taqwa")

menu = st.sidebar.radio(
    "Menu",
    ["💰 Keuangan", "📦 Barang Masuk", "📄 Laporan"]
)

# ===============================
# MENU KEUANGAN
# ===============================
if menu == "💰 Keuangan":
    st.subheader("💰 Data Keuangan")
    st.dataframe(df_keu, use_container_width=True)

# ===============================
# MENU BARANG MASUK
# ===============================
if menu == "📦 Barang Masuk":
    st.subheader("📦 Data Barang Masuk")
    st.dataframe(df_barang, use_container_width=True)

# ===============================
# FUNGSI PDF OPSI B (TABEL RAPI)
# ===============================
def generate_pdf_laporan(df_keu, df_barang):
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    elements = []

    # ===== LOGO KREASI SEDERHANA =====
    title_style = ParagraphStyle(
        "TitleCenter",
        parent=styles["Title"],
        alignment=1,
        textColor=colors.HexColor("#0b6b3a")
    )

    elements.append(Paragraph("MUSHOLLA AT-TAQWA", title_style))
    elements.append(Paragraph("<b>LAPORAN KEUANGAN & BARANG MASUK</b>", styles["Heading2"]))
    elements.append(Paragraph(
        f"Periode: s.d. {datetime.now().strftime('%d %B %Y')}<br/>Tanggal Cetak: {datetime.now().strftime('%d %B %Y')}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 12))

    # ===== TABEL KEUANGAN =====
    elements.append(Paragraph("<b>A. Laporan Keuangan</b>", styles["Heading3"]))

    table_data = [["Tanggal", "Keterangan", "Masuk (Rp)", "Keluar (Rp)", "Saldo (Rp)"]]
    for _, r in df_keu.iterrows():
        table_data.append([
            r["Tanggal"],
            r["Keterangan"],
            f"{int(r['Masuk']):,}" if pd.notna(r["Masuk"]) else "-",
            f"{int(r['Keluar']):,}" if pd.notna(r["Keluar"]) else "-",
            f"{int(r['Saldo']):,}" if pd.notna(r["Saldo"]) else "-"
        ])

    table = Table(table_data, colWidths=[70, 180, 80, 80, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (2,1), (-1,-1), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold")
    ]))
    elements.append(table)
    elements.append(Spacer(1, 16))

    # ===== TABEL BARANG MASUK =====
    elements.append(Paragraph("<b>B. Barang Masuk</b>", styles["Heading3"]))

    table_barang = [["Tanggal", "Nama Barang", "Jumlah", "Satuan", "Keterangan"]]
    for _, r in df_barang.iterrows():
        table_barang.append([
            r["Tanggal"],
            r["Nama Barang"],
            r["Jumlah"],
            r["Satuan"],
            r["Keterangan"]
        ])

    tb = Table(table_barang, colWidths=[70, 140, 60, 60, 120])
    tb.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold")
    ]))
    elements.append(tb)
    elements.append(Spacer(1, 24))

    # ===== TTD =====
    ttd = Table([
        ["Ketua", "Sekretaris", "Bendahara"],
        ["", "", ""],
        ["Ferri Kusuma", "Alfan Fatichul Ichsan", "Sunhadi Prayitno"]
    ], colWidths=[170, 170, 170])

    ttd.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,1), (-1,1), 30),
        ("FONT", (0,2), (-1,2), "Helvetica-Bold")
    ]))

    elements.append(ttd)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ===============================
# MENU LAPORAN (TAMBAH PDF SAJA)
# ===============================
if menu == "📄 Laporan":
    st.subheader("📄 Laporan Resmi")

    st.info("Gunakan tombol di bawah untuk mengunduh laporan PDF resmi (format tabel rapi, siap cetak).")

    pdf_bytes = generate_pdf_laporan(df_keu, df_barang)

    st.download_button(
        label="📥 Download Laporan PDF Resmi",
        data=pdf_bytes,
        file_name="Laporan_Musholla_At-Taqwa.pdf",
        mime="application/pdf"
    )
