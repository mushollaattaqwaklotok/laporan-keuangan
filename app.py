import streamlit as st
import pandas as pd
import datetime

# Menampilkan informasi organisasi di sidebar
def display_organization_info():
    st.sidebar.image("https://example.com/logo.png", width=100)  # Ganti dengan URL logo Anda jika ada
    st.sidebar.title("Informasi Organisasi")
    st.sidebar.subheader("Panitia Pembangunan Musholla At Taqwa")
    st.sidebar.write("Lokasi: Dusun Klotok RT.1, Desa Simogirang, Kecamatan Prambon, Kabupaten Sidoarjo 61264")
    st.sidebar.write("Ketua: Ferri Kusuma")
    st.sidebar.write("Sekretaris: Alfan Fatik")
    st.sidebar.write("Bendahara: Sunhadi Prayitno")
    st.sidebar.write("Koordinator Humas: Riaji")
    st.sidebar.write("Koordinator Penggalangan Dana: Atmorejo")

    st.sidebar.subheader("Kontak")
    st.sidebar.write("Email: info@musholla-taqwa.com")
    st.sidebar.write("Facebook: Musholla At Taqwa")

# Fungsi untuk menambahkan transaksi baru
def add_transaction(tipe, jumlah, deskripsi, tanggal):
    new_data = pd.DataFrame({
        'Tipe': [tipe],
        'Jumlah': [jumlah],
        'Deskripsi': [deskripsi],
        'Tanggal': [tanggal]
    })
    new_data.to_csv('data/data_transaksi.csv', mode='a', header=False, index=False)

# Fungsi utama aplikasi
def main():
    # Menampilkan informasi organisasi di sidebar
    display_organization_info()

    # Menampilkan bagian utama aplikasi
    st.title("Aplikasi Keuangan Musholla At Taqwa")

    # Menampilkan daftar transaksi
    st.subheader("Daftar Transaksi")
    try:
        df = pd.read_csv('data/data_transaksi.csv')
        st.write(df)
    except FileNotFoundError:
        st.write("Belum ada data transaksi.")

    # Tombol input transaksi baru
    st.subheader("Tambah Transaksi Baru")
    tipe = st.selectbox("Tipe Transaksi", ['Uang Masuk', 'Uang Keluar', 'Operasional'])
    jumlah = st.number_input("Jumlah", min_value=0)
    deskripsi = st.text_input("Deskripsi Transaksi")
    tanggal = st.date_input("Tanggal", datetime.date.today())

    if st.button('Tambah Transaksi'):
        add_transaction(tipe, jumlah, deskripsi, tanggal)
        st.success("Transaksi berhasil ditambahkan!")

if __name__ == "__main__":
    main()
