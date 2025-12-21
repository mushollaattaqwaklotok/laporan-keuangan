import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path

# ===============================
# PDF
# ===============================
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

# ===============================
# KONFIGURASI
# ===============================
BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

FILE_KEU = DATA_DIR / "keuangan.csv"
FILE_BARANG = DATA_DIR / "barang_masuk.csv"

# ===============================
# WARNA NU (TETAP)
# ===============================
st.set_page_config(page_title="Sistem Keuangan Musholla", layout="wide")
st.markdown(
    """
    <style>
    .stApp {
        background-color: #e9f5ee;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===============================
# HEADER
# ===============================
st.title("📊 Sistem Keuangan Musholla At-Taqwa")

menu = st.sidebar.selectbox(
    "📌 Menu",
    ["🏠 Beranda", "💰 Keuangan", "📦 Barang Masuk", "📄 Laporan"]
)

# ===============================
# LOAD DATA
# ===============================
def load_csv(file, columns):
    if file.exists():
        return pd.read_csv(file)
    else:
        return pd.DataFrame(columns=columns)

df_keu = load_csv(FILE_KEU, ["Tanggal", "Uraian", "Masuk", "Keluar"])
df_barang = load_csv(FILE_BARANG, ["Tanggal", "Nama Barang", "Jumlah", "Keterangan"])

# ===============================
# SIMPAN CSV
# ===============================
def save_csv(df, file):
    df.to_csv(file, index=False)

# ===============================
# MENU BERANDA
# ===============================
if menu == "🏠 Beranda":
    st.success("Selamat datang di Sistem Keuangan Musholla At-Taqwa")
    st.info("Aplikasi transparansi dan amanah keuangan musholla")

# ===============================
# MENU KEUANGAN
# ===============================
elif menu == "💰 Keuangan":
    st.subheader("💰 Input Keuangan")

    with st.form("form_keuangan"):
        tgl = st.date_input("Tanggal", datetime.now())
        uraian = st.text_input("Uraian")
        masuk = st.number_input("Uang Masuk", min_value=0, value=0)
        keluar = st.number_input("Uang Keluar", min_value=0, value=0)
        simpan = st.form_submit_button("💾 Simpan")

    if simpan:
        df_keu.loc[len(df_keu)] = [
            tgl.strftime("%Y-%m-%d"),
            uraian,
            masuk,
            keluar
        ]
        save_csv(df_keu, FILE_KEU)
        st.success("Data keuangan tersimpan")

    st.dataframe(df_keu, use_container_width=True)

# ===============================
# MENU BARANG MASUK
# ===============================
elif menu == "📦 Barang Masuk":
    st.subheader("📦 Barang Masuk")

    with st.form("form_barang"):
        tgl = st.date_input("Tanggal", datetime.now())
        nama = st.text_input("Nama Barang")
        jumlah = st.number_input("Jumlah", min_value=1, value=1)
        ket = st.text_input("Keterangan")
        simpan = st.form_submit_button("💾 Simpan")

    if simpan:
        df_barang.loc[len(df_barang)] = [
            tgl.strftime("%Y-%m-%d"),
            nama,
            jumlah,
            ket
        ]
        save_csv(df_barang, FILE_BARANG)
        st.success("Data barang masuk tersimpan")

    st.dataframe(df_barang, use_container_width=True)

# ===============================
# FUNGSI PDF
# ===============================
def generate_pdf(df_keu, df_barang):
    file_pdf = "Laporan_Keuangan_Musholla_At_Taqwa.pdf"
    c = canvas.Canvas(file_pdf, pagesize=A4)
    width, height = A4

    # Logo (kreasi sederhana)
    c.setFillColor(colors.darkgreen)
    c.circle(2*cm, height-2*cm, 1*cm, fill=1)

    # Header
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(4*cm, height-2*cm, "MUSHOLLA AT-TAQWA")

    c.setFont("Helvetica", 10)
    c.drawString(4*cm, height-2.7*cm, "Laporan Keuangan & Barang Masuk")

    # Tanggal cetak
    c.setFont("Helvetica-Oblique", 9)
    c.drawRightString(
        width-2*cm,
        height-2.7*cm,
        f"Tanggal Cetak: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
    )

    y = height - 4*cm

    # ===== TABEL KEUANGAN =====
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y, "A. Laporan Keuangan")
    y -= 0.7*cm

    data_keu = [df_keu.columns.tolist()] + df_keu.values.tolist()
    table_keu = Table(data_keu, colWidths=[3*cm, 6*cm, 3*cm, 3*cm])
    table_keu.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgreen),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("ALIGN", (2,1), (-1,-1), "RIGHT"),
    ]))
    table_keu.wrapOn(c, width, height)
    table_keu.drawOn(c, 2*cm, y - len(data_keu)*0.45*cm)

    y -= (len(data_keu)+2)*0.45*cm

    # ===== TABEL BARANG =====
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y, "B. Barang Masuk")
    y -= 0.7*cm

    data_barang = [df_barang.columns.tolist()] + df_barang.values.tolist()
    table_barang = Table(data_barang, colWidths=[3*cm, 6*cm, 2*cm, 4*cm])
    table_barang.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgreen),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
    ]))
    table_barang.wrapOn(c, width, height)
    table_barang.drawOn(c, 2*cm, y - len(data_barang)*0.45*cm)

    # ===== TTD =====
    y -= (len(data_barang)+4)*0.45*cm

    c.drawString(2*cm, y, "Ketua")
    c.drawString(8*cm, y, "Sekretaris")
    c.drawString(14*cm, y, "Bendahara")

    y -= 2*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, y, "Ferri Kusuma")
    c.drawString(8*cm, y, "Alfan Fatichul Ichsan")
    c.drawString(14*cm, y, "Sunhadi Prayitno")

    c.showPage()
    c.save()

    return file_pdf

# ===============================
# MENU LAPORAN
# ===============================
elif menu == "📄 Laporan":
    st.subheader("📄 Laporan Keuangan & Barang Masuk")

    st.dataframe(df_keu, use_container_width=True)
    st.dataframe(df_barang, use_container_width=True)

    # CSV tetap ada
    st.download_button(
        "⬇️ Download CSV Keuangan",
        df_keu.to_csv(index=False),
        file_name="keuangan.csv",
        mime="text/csv"
    )

    # === TAMBAHAN PDF (SAJA INI) ===
    if st.button("📄 Download Laporan PDF Resmi"):
        pdf_file = generate_pdf(df_keu, df_barang)
        with open(pdf_file, "rb") as f:
            st.download_button(
                "⬇️ Klik untuk Download PDF",
                f,
                file_name=pdf_file,
                mime="application/pdf"
            )
