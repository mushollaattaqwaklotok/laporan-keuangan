import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from hashlib import sha256

# List of authorized users (5 people)
AUTHORIZED_USERS = ['ferri_kusuma', 'alfan_fatik', 'sunhadi_prayitno', 'riaji', 'atmorejo']
AUTHORIZED_PASSWORDS = {
    'ferri_kusuma': 'password1',
    'alfan_fatik': 'password2',
    'sunhadi_prayitno': 'password3',
    'riaji': 'password4',
    'atmorejo': 'password5',
}

# Function to verify user credentials
def verify_password(username, password):
    # Hashing the password and comparing it to the stored password
    hashed_password = sha256(password.encode('utf-8')).hexdigest()
    stored_password = sha256(AUTHORIZED_PASSWORDS.get(username, '').encode('utf-8')).hexdigest()
    return hashed_password == stored_password

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

    st.sidebar.subheader("Laporan Keuangan")
    st.sidebar.write("[Laporan Keuangan: Musholla At Taqwa](https://laporan-attaqwa.streamlit.app/)")

# Fungsi untuk menambahkan transaksi baru
def add_transaction(tipe, jumlah, deskripsi, tanggal):
    new_data = pd.DataFrame({
        'Tipe': [tipe],
        'Jumlah': [jumlah],
        'Deskripsi': [deskripsi],
        'Tanggal': [tanggal]
    })
    new_data.to_csv('data/data_transaksi.csv', mode='a', header=False, index=False)

# Fungsi untuk mengonversi format tanggal sesuai dengan format dd/mm/yyyy
def convert_date_format(df):
    df['Tanggal'] = pd.to_datetime(df['Tanggal'], format='%d/%m/%Y')
    return df

# Fungsi untuk menampilkan ringkasan keuangan
def display_financial_summary(df):
    total_income = df[df['Tipe'] == 'Uang Masuk']['Jumlah'].sum()
    total_expenses = df[df['Tipe'] == 'Uang Keluar']['Jumlah'].sum()
    operational_costs = df[df['Tipe'] == 'Operasional']['Jumlah'].sum()
    balance = total_income - total_expenses

    st.subheader("Ringkasan Keuangan")
    st.write(f"**Total Pemasukan**: Rp {total_income:,.0f}")
    st.write(f"**Total Pengeluaran**: Rp {total_expenses:,.0f}")
    st.write(f"**Biaya Operasional**: Rp {operational_costs:,.0f}")
    st.write(f"**Saldo Terakhir**: Rp {balance:,.0f}")

# Fungsi untuk menampilkan transaksi terakhir
def display_recent_transactions(df):
    st.subheader("10 Transaksi Terakhir")
    recent_transactions = df.sort_values(by='Tanggal', ascending=False).head(10)
    st.write(recent_transactions[['Tipe', 'Jumlah', 'Deskripsi', 'Tanggal']])

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

    # Memverifikasi login
    st.sidebar.subheader("Login untuk Akses Fitur Edit")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type='password')

    if username and password:
        if verify_password(username, password):
            st.sidebar.success(f"Selamat datang, {username}!")
            # Tombol untuk tambah, edit, hapus transaksi hanya muncul setelah login
            action = st.selectbox("Pilih Aksi", ['Tambah Transaksi', 'Edit Transaksi', 'Hapus Transaksi'])
            if action == 'Tambah Transaksi':
                transaksi_type = st.selectbox("Pilih Jenis Transaksi", ['Uang Masuk', 'Uang Keluar'])
                jumlah_input = st.number_input("Jumlah", min_value=0)
                deskripsi_input = st.text_input("Deskripsi Transaksi")
                tanggal_input = st.date_input("Tanggal", datetime.date.today())
                
                if st.button(f'Tambah {transaksi_type}'):
                    add_transaction(transaksi_type, jumlah_input, deskripsi_input, tanggal_input)
                    st.success(f"Transaksi {transaksi_type} berhasil ditambahkan!")
            elif action == 'Edit Transaksi':
                # Edit transaksi logic here (if needed)
                st.write("Fitur edit transaksi belum diterapkan.")
            elif action == 'Hapus Transaksi':
                # Hapus transaksi logic here (if needed)
                st.write("Fitur hapus transaksi belum diterapkan.")
        else:
            st.sidebar.error("Username atau Password Salah")

    # Menampilkan daftar transaksi
    try:
        df = pd.read_csv('data/data_transaksi.csv')
        df = convert_date_format(df)
    except FileNotFoundError:
        st.write("Belum ada data transaksi.")
        return

    # Menampilkan ringkasan keuangan
    display_financial_summary(df)

    # Menampilkan transaksi terakhir
    display_recent_transactions(df)

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

    # Menampilkan grafik transaksi
    st.subheader("Grafik Pemasukan dan Pengeluaran")
    plot_transactions(df_filtered)

    # Menampilkan grafik pie untuk kategori transaksi
    st.subheader("Pembagian Kategori Transaksi")
    plot_pie_chart(df_filtered)

if __name__ == "__main__":
    main()
