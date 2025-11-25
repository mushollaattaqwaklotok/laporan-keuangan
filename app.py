import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Menampilkan informasi organisasi di sidebar
def display_organization_info():
    st.sidebar.image("https://i.pinimg.com/originals/f8/bf/8a/f8bf8a1221a81747154698816b7c9113.jpg", width=100)  # Gambar logo Musholla
    st.sidebar.title("Informasi Organisasi")
    st.sidebar.subheader("Panitia Pembangunan Musholla At Taqwa")
    st.sidebar.write("Lokasi: Dusun Klotok RT.1, Desa Simogirang, Kecamatan Prambon, Kabupaten Sidoarjo 61264")
    st.sidebar.write("Ketua: Ferri Kusuma")
    st.sidebar.write("Sekretaris: Alfan Fatik")
    st.sidebar.write("Bendahara: Sunhadi Prayitno")
    st.sidebar.write("Koordinator Humas: Riaji")
    st.sidebar.write("Koordinator Penggalangan Dana: Atmorejo")

    st.sidebar.subheader("Kontak")
    st.sidebar.write("Email: mushollaattaqwaklotok@gmail.com")
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

# Fungsi untuk menampilkan transaksi dengan filter
def filter_transactions(df, tipe=None, start_date=None, end_date=None):
    if tipe:
        df = df[df['Tipe'] == tipe]
    if start_date:
        df = df[df['Tanggal'] >= start_date]
    if end_date:
        df = df[df['Tanggal'] <= end_date]
    return df

# Fungsi untuk mengonversi format tanggal sesuai dengan format dd/mm/yyyy
def convert_date_format(df):
    # Mengonversi kolom 'Tanggal' ke format datetime dengan format dd/mm/yyyy
    df['Tanggal'] = pd.to_datetime(df['Tanggal'], format='%d/%m/%Y')
    return df

# Fungsi untuk membuat grafik pemasukan dan pengeluaran
def plot_transactions(df):
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    monthly_summary = df.groupby(df['Tanggal'].dt.to_period('M')).sum()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=monthly_summary.index.astype(str), y='Jumlah', data=monthly_summary, ax=ax)
    ax.set_title('Total Transaksi Per Bulan')
    ax.set_xlabel('Bulan')
    ax.set_ylabel('Jumlah (Rp)')
    st.pyplot(fig)

# Fungsi untuk menampilkan pie chart untuk kategori transaksi
def plot_pie_chart(df):
    category_summary = df.groupby('Tipe').sum()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(category_summary['Jumlah'], labels=category_summary.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)

# Fungsi utama aplikasi
def main():
    # Menampilkan informasi organisasi di sidebar
    display_organization_info()

    # Menampilkan bagian utama aplikasi
    st.title("Aplikasi Keuangan Musholla At Taqwa")
    st.markdown("## Visualisasi Transaksi Keuangan")

    # Menampilkan daftar transaksi
    try:
        df = pd.read_csv('data/data_transaksi.csv')

        # Mengonversi format tanggal sesuai dengan format dd/mm/yyyy
        df = convert_date_format(df)
    except FileNotFoundError:
        st.write("Belum ada data transaksi.")
        return

    # Filter Transaksi
    st.subheader("Filter Transaksi")
    tipe = st.selectbox("Pilih Tipe Transaksi", ['Semua', 'Uang Masuk', 'Uang Keluar', 'Operasional'])
    start_date = st.date_input("Dari Tanggal", df['Tanggal'].min())
    end_date = st.date_input("Sampai Tanggal", df['Tanggal'].max())

    if tipe != 'Semua':
        df_filtered = filter_transactions(df, tipe=tipe, start_date=start_date, end_date=end_date)
    else:
        df_filtered = filter_transactions(df, start_date=start_date, end_date=end_date)

    # Menampilkan data transaksi yang sudah difilter
    st.write(f"Menampilkan transaksi dari {start_date} hingga {end_date}")
    st.write(df_filtered)

    # Menambahkan tombol untuk input transaksi baru
    st.subheader("Tambah Transaksi Baru")
    tipe_input = st.selectbox("Tipe Transaksi", ['Uang Masuk', 'Uang Keluar', 'Operasional'])
    jumlah_input = st.number_input("Jumlah", min_value=0)
    deskripsi_input = st.text_input("Deskripsi Transaksi")
    tanggal_input = st.date_input("Tanggal", datetime.date.today())

    if st.button('Tambah Transaksi'):
        add_transaction(tipe_input, jumlah_input, deskripsi_input, tanggal_input)
        st.success("Transaksi berhasil ditambahkan!")

    # Menampilkan grafik transaksi
    st.subheader("Grafik Pemasukan dan Pengeluaran")
    plot_transactions(df_filtered)

    # Menampilkan grafik pie untuk kategori transaksi
    st.subheader("Pembagian Kategori Transaksi")
    plot_pie_chart(df_filtered)

if __name__ == "__main__":
    main()
