import streamlit as st
import pandas as pd
import os

DATA_FILE = "data/barang.csv"

# ===============================
# Fungsi Muat & Simpan Data
# ===============================
def load_data():
    if not os.path.exists("data"):
        os.makedirs("data")

    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["id", "nama_barang", "jumlah", "keterangan"])
        df.to_csv(DATA_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ===============================
# Aplikasi Streamlit
# ===============================
st.title("📦 Manajemen Data Barang")

menu = st.sidebar.selectbox("Menu", ["Tambah Barang", "Daftar Barang"])

df = load_data()

# ===============================
# Halaman: Tambah Barang
# ===============================
if menu == "Tambah Barang":
    st.subheader("➕ Tambah Data Barang")

    nama = st.text_input("Nama Barang")
    jumlah = st.number_input("Jumlah", min_value=1, step=1)
    ket = st.text_area("Keterangan")

    if st.button("Simpan"):
        new_id = 1 if df.empty else df["id"].max() + 1

        new_data = pd.DataFrame([{
            "id": new_id,
            "nama_barang": nama,
            "jumlah": jumlah,
            "keterangan": ket
        }])

        df = pd.concat([df, new_data], ignore_index=True)
        save_data(df)

        st.success("Data barang berhasil ditambahkan!")

# ===============================
# Halaman: Daftar Barang
# ===============================
elif menu == "Daftar Barang":
    st.subheader("📋 Daftar Barang")

    if df.empty:
        st.info("Belum ada data barang.")
    else:
        st.dataframe(df)

        st.markdown("---")
        st.subheader("✏️ Edit / 🗑️ Hapus Data Barang")

        pilih_id = st.selectbox("Pilih ID Barang", df["id"])

        data_selected = df[df["id"] == pilih_id].iloc[0]

        nama_edit = st.text_input("Nama Barang", data_selected["nama_barang"])
        jumlah_edit = st.number_input("Jumlah", min_value=1, step=1, value=int(data_selected["jumlah"]))
        ket_edit = st.text_area("Keterangan", data_selected["keterangan"])

        col1, col2 = st.columns(2)

        # Tombol Edit
        with col1:
            if st.button("Simpan Perubahan"):
                df.loc[df["id"] == pilih_id, "nama_barang"] = nama_edit
                df.loc[df["id"] == pilih_id, "jumlah"] = jumlah_edit
                df.loc[df["id"] == pilih_id, "keterangan"] = ket_edit
                save_data(df)
                st.success("Perubahan berhasil disimpan!")

        # Tombol Hapus
        with col2:
            if st.button("Hapus Data"):
                df = df[df["id"] != pilih_id]
                save_data(df)
                st.error("Data berhasil dihapus!")

