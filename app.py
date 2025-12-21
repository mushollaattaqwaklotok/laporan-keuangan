import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# ===============================
# KONFIGURASI
# ===============================
BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

FILE_KEU = DATA_DIR / "keuangan.csv"
FILE_BARANG = DATA_DIR / "barang_masuk.csv"

# ===============================
# TAMPILAN HIJAU NU
# ===============================
st.set_page_config("Sistem Keuangan Musholla", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #e9f5ee; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Sistem Keuangan Musholla At-Taqwa")

menu = st.sidebar.selectbox(
    "📌 Menu",
    ["🏠 Beranda", "💰 Keuangan", "📦 Barang Masuk", "📄 Laporan"]
)

# ===============================
# LOAD DATA
# ===============================
def load_csv(file, cols):
    return pd.read_csv(file) if file.exists() else pd.DataFrame(columns=cols)

df_keu = load_csv(FILE_KEU, ["Tanggal", "Uraian", "Masuk", "Keluar"])
df_barang = load_csv(FILE_BARANG, ["Tanggal", "Nama Barang", "Jumlah", "Keterangan"])

def save_csv(df, file):
    df.to_csv(file, index=False)

# ===============================
# MENU BERANDA
# ===============================
if menu == "🏠 Beranda":
    st.success("Selamat datang di Sistem Keuangan Musholla At-Taqwa")

# ===============================
# MENU KEUANGAN
# ===============================
elif menu == "💰 Keuangan":
    st.subheader("💰 Input Keuangan")

    with st.form("form_keu"):
        tgl = st.date_input("Tanggal", datetime.now())
        uraian = st.text_input("Uraian")
        masuk = st.number_input("Masuk", 0)
        keluar = st.number_input("Keluar", 0)
        simpan = st.form_submit_button("💾 Simpan")

    if simpan:
        df_keu.loc[len(df_keu)] = [
            tgl.strftime("%Y-%m-%d"), uraian, masuk, keluar
        ]
        save_csv(df_keu, FILE_KEU)
        st.success("Data tersimpan")

    st.dataframe(df_keu, use_container_width=True)

# ===============================
# MENU BARANG MASUK
# ===============================
elif menu == "📦 Barang Masuk":
    st.subheader("📦 Barang Masuk")

    with st.form("form_barang"):
        tgl = st.date_input("Tanggal", datetime.now())
        nama = st.text_input("Nama Barang")
        jumlah = st.number_input("Jumlah", 1)
        ket = st.text_input("Keterangan")
        simpan = st.form_submit_button("💾 Simpan")

    if simpan:
        df_barang.loc[len(df_barang)] = [
            tgl.strftime("%Y-%m-%d"), nama, jumlah, ket
        ]
        save_csv(df_barang, FILE_BARANG)
        st.success("Barang tersimpan")

    st.dataframe(df_barang, use_container_width=True)

# ===============================
# PDF
# ===============================
def generate_pdf():
    file = "Laporan_Musholla_At_Taqwa.pdf"
    c = canvas.Canvas(file, pagesize=A4)
    w, h = A4

    c.setFillColor(colors.darkgreen)
    c.circle(2*cm, h-2*cm, 1*cm, fill=1)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(4*cm, h-2*cm, "MUSHOLLA AT-TAQWA")

    c.setFont("Helvetica", 9)
    c.drawRightString(
        w-2*cm, h-2.7*cm,
        f"Tanggal Cetak: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
    )

    y = h - 4*cm

    def draw_table(title, df, colw):
        nonlocal y
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, y, title)
        y -= 0.7*cm

        data = [df.columns.tolist()] + df.values.tolist()
        table = Table(data, colWidths=colw)
        table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgreen),
        ]))
        table.wrapOn(c, w, h)
        table.drawOn(c, 2*cm, y - len(data)*0.45*cm)
        y -= (len(data)+2)*0.45*cm

    draw_table("A. Laporan Keuangan", df_keu, [3*cm, 6*cm, 3*cm, 3*cm])
    draw_table("B. Barang Masuk", df_barang, [3*cm, 6*cm, 2*cm, 4*cm])

    y -= 1.5*cm
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
    return file

# ===============================
# MENU LAPORAN
# ===============================
elif menu == "📄 Laporan":
    st.subheader("📄 Laporan")

    st.dataframe(df_keu, use_container_width=True)
    st.dataframe(df_barang, use_container_width=True)

    if st.button("📄 Download Laporan PDF Resmi"):
        pdf = generate_pdf()
        with open(pdf, "rb") as f:
            st.download_button(
                "⬇️ Klik Download PDF",
                f,
                file_name=pdf,
                mime="application/pdf"
            )
