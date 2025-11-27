import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from hashlib import sha256
import os
import io
import uuid

# ---------------------------
# CONFIG & AUTH
# ---------------------------
st.set_page_config(page_title="Aplikasi Keuangan Musholla At Taqwa", layout="wide")

# Authorized users (keep these simple — passwords will be hashed in-memory)
AUTHORIZED_USERS = ['ferri_kusuma', 'alfan_fatik', 'sunhadi_prayitno', 'riaji', 'atmorejo']
# NOTE: replace 'password1'.. with real passwords before deploy
_AUTH_RAW = {
    'ferri_kusuma': 'password1',
    'alfan_fatik': 'password2',
    'sunhadi_prayitno': 'password3',
    'riaji': 'password4',
    'atmorejo': 'password5',
}
# Precompute hashed passwords (sha256 hex)
AUTHORIZED_PASSWORDS = {u: sha256(p.encode('utf-8')).hexdigest() for u, p in _AUTH_RAW.items()}

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "data_transaksi.csv")

# ---------------------------
# HELPERS: File init, auth, formatting
# ---------------------------
def ensure_data_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        df_init = pd.DataFrame(columns=['ID', 'Tipe', 'Jumlah', 'Deskripsi', 'Tanggal', 'Dibuat_Oleh', 'Dibuat_Pada'])
        df_init.to_csv(DATA_FILE, index=False)

def verify_password(username, password):
    if username not in AUTHORIZED_PASSWORDS:
        return False
    hashed = sha256(password.encode('utf-8')).hexdigest()
    return hashed == AUTHORIZED_PASSWORDS[username]

def load_transactions():
    ensure_data_file()
    df = pd.read_csv(DATA_FILE, dtype={'ID': str})
    # Normalize tanggal
    if 'Tanggal' in df.columns:
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
    else:
        df['Tanggal'] = pd.NaT
    return df

def save_transactions(df):
    # Ensure Fecha formatted consistently (ISO date) when saving
    df_copy = df.copy()
    df_copy['Tanggal'] = pd.to_datetime(df_copy['Tanggal']).dt.date.astype(str)
    df_copy.to_csv(DATA_FILE, index=False)

def add_transaction(tipe, jumlah, deskripsi, tanggal, user):
    df = load_transactions()
    new = {
        'ID': str(uuid.uuid4()),
        'Tipe': tipe,
        'Jumlah': float(jumlah),
        'Deskripsi': deskripsi,
        'Tanggal': pd.to_datetime(tanggal).date(),
        'Dibuat_Oleh': user,
        'Dibuat_Pada': pd.Timestamp.now()
    }
    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    save_transactions(df)
    return df

def update_transaction(tx_id, tipe, jumlah, deskripsi, tanggal, user):
    df = load_transactions()
    if tx_id not in df['ID'].values:
        return None
    idx = df.index[df['ID'] == tx_id][0]
    df.at[idx, 'Tipe'] = tipe
    df.at[idx, 'Jumlah'] = float(jumlah)
    df.at[idx, 'Deskripsi'] = deskripsi
    df.at[idx, 'Tanggal'] = pd.to_datetime(tanggal).date()
    df.at[idx, 'Dibuat_Oleh'] = user  # update last editor info
    df.at[idx, 'Dibuat_Pada'] = pd.Timestamp.now()
    save_transactions(df)
    return df

def delete_transaction(tx_id):
    df = load_transactions()
    if tx_id not in df['ID'].values:
        return None
    df = df[df['ID'] != tx_id].reset_index(drop=True)
    save_transactions(df)
    return df

def filter_transactions(df, tipe='Semua', start_date=None, end_date=None):
    df_filtered = df.copy()
    if start_date is not None:
        df_filtered = df_filtered[df_filtered['Tanggal'] >= pd.to_datetime(start_date)]
    if end_date is not None:
        df_filtered = df_filtered[df_filtered['Tanggal'] <= pd.to_datetime(end_date)]
    if tipe and tipe != 'Semua':
        df_filtered = df_filtered[df_filtered['Tipe'] == tipe]
    return df_filtered

def format_currency(x):
    try:
        return "Rp {:,.0f}".format(float(x))
    except:
        return x

def get_csv_download(df):
    towrite = io.StringIO()
    df.to_csv(towrite, index=False)
    return towrite.getvalue().encode('utf-8')

# ---------------------------
# UI: Sidebar (organization + login)
# ---------------------------
def display_organization_info():
    st.sidebar.image("https://i.pinimg.com/originals/f8/bf/8a/f8bf8a1221a81747154698816b7c9113.jpg", width=100)
    st.sidebar.title("Informasi Organisasi")
    st.sidebar.subheader("Panitia Pembangunan Musholla At Taqwa")
    st.sidebar.write("Lokasi: Dusun Klotok RT.1, Desa Simogirang, Kecamatan Prambon, Kabupaten Sidoarjo 61264")
    st.sidebar.write("Ketua: Ferri Kusuma")
    st.sidebar.write("Sekretaris: Alfan Fatik")
    st.sidebar.write("Bendahara: Sunhadi Prayitno")
    st.sidebar.write("Koordinator Humas: Riaji")
    st.sidebar.write("Koordinator Penggalangan Dana: Atmorejo")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Akses Laporan")
    st.sidebar.write("[Lihat Laporan Publik](https://laporan-attaqwa.streamlit.app/)")

def sidebar_login():
    st.sidebar.subheader("Login untuk Akses Edit")
    username = st.sidebar.text_input("Username", key="username_input")
    password = st.sidebar.text_input("Password", type="password", key="password_input")
    login_btn = st.sidebar.button("Login", key="login_btn")
    if login_btn:
        if verify_password(username, password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.sidebar.success(f"Selamat datang, {username}!")
        else:
            st.session_state['logged_in'] = False
            st.session_state['username'] = ""
            st.sidebar.error("Username atau Password salah")
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""

# ---------------------------
# DASHBOARD: summary, recent tx, plots
# ---------------------------
def display_financial_summary(df):
    # avoid NaNs
    df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce').fillna(0)
    total_income = df[df['Tipe'] == 'Uang Masuk']['Jumlah'].sum()
    total_expenses = df[df['Tipe'] == 'Uang Keluar']['Jumlah'].sum()
    operational = df[df['Tipe'] == 'Operasional']['Jumlah'].sum() if 'Operasional' in df['Tipe'].unique() else 0
    balance = total_income - total_expenses

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Pemasukan", format_currency(total_income))
    col2.metric("Total Pengeluaran", format_currency(total_expenses))
    col3.metric("Biaya Operasional", format_currency(operational))
    col4.metric("Saldo Terakhir", format_currency(balance))

def display_recent_transactions(df, n=10):
    st.subheader(f"{n} Transaksi Terakhir")
    df_sorted = df.sort_values(by='Tanggal', ascending=False).head(n)
    if df_sorted.empty:
        st.info("Belum ada transaksi.")
        return
    df_show = df_sorted[['ID', 'Tipe', 'Jumlah', 'Deskripsi', 'Tanggal', 'Dibuat_Oleh']]
    df_show['Jumlah'] = df_show['Jumlah'].apply(format_currency)
    st.dataframe(df_show, use_container_width=True)

def plot_transactions(df):
    if df.empty:
        st.info("Tidak ada data untuk grafik.")
        return
    df_plot = df.copy()
    df_plot['Tanggal'] = pd.to_datetime(df_plot['Tanggal'])
    df_plot['Bulan'] = df_plot['Tanggal'].dt.to_period('M').dt.to_timestamp()
    summary = df_plot.groupby(['Bulan', 'Tipe'])['Jumlah'].sum().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 4))
    summary.plot(kind='bar', stacked=False, ax=ax)
    ax.set_title("Total Transaksi Per Bulan (per Tipe)")
    ax.set_ylabel("Jumlah (Rp)")
    ax.set_xlabel("Bulan")
    plt.xticks(rotation=45)
    st.pyplot(fig)

def plot_pie_chart(df):
    if df.empty:
        st.info("Tidak ada data untuk pie chart.")
        return
    cat = df.groupby('Tipe')['Jumlah'].sum()
    if cat.sum() == 0:
        st.info("Jumlah semua kategori = 0, pie chart tidak ditampilkan.")
        return
    fig, ax = plt.subplots(figsize=(5,5))
    ax.pie(cat, labels=cat.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

# ---------------------------
# MAIN
# ---------------------------
def main():
    display_organization_info()
    sidebar_login()
    st.title("Aplikasi Keuangan — Musholla At Taqwa RT.1 Dusun Klotok")
    st.markdown("Aplikasi sederhana untuk pencatatan dan pelaporan keuangan pembangunan musholla.")

    # Load data
    df_all = load_transactions()

    # --- LEFT: input / manage (restricted) ---
    col_left, col_right = st.columns([3,7])
    with col_left:
        st.header("Input / Pengelolaan")
        if st.session_state['logged_in']:
            action = st.selectbox("Pilih aksi", ["Tambah Transaksi", "Edit Transaksi", "Hapus Transaksi"])
            if action == "Tambah Transaksi":
                tipe = st.selectbox("Jenis Transaksi", ["Uang Masuk", "Uang Keluar", "Operasional"])
                jumlah = st.number_input("Jumlah (Rp)", min_value=0.0, step=50000.0, format="%f")
                deskripsi = st.text_input("Deskripsi")
                tanggal = st.date_input("Tanggal", datetime.date.today())
                if st.button("Tambah"):
                    if jumlah <= 0:
                        st.error("Jumlah harus lebih dari 0.")
                    else:
                        df_all = add_transaction(tipe, jumlah, deskripsi, tanggal, st.session_state['username'])
                        st.success("Transaksi berhasil ditambahkan.")
            elif action == "Edit Transaksi":
                if df_all.empty:
                    st.info("Tidak ada transaksi untuk diedit.")
                else:
                    # allow selection by ID (show a readable choice)
                    df_select = df_all.sort_values(by='Tanggal', ascending=False)
                    df_select['label'] = df_select.apply(lambda r: f"{r['Tanggal']} | {r['Tipe']} | {format_currency(r['Jumlah'])} | {r['Deskripsi'][:30]}", axis=1)
                    choice = st.selectbox("Pilih transaksi untuk diedit", ["-"] + df_select['label'].tolist())
                    if choice != "-":
                        selected_idx = df_select[df_select['label'] == choice].index[0]
                        selected_row = df_select.loc[selected_idx]
                        tx_id = selected_row['ID']
                        tipe_e = st.selectbox("Jenis Transaksi", ["Uang Masuk", "Uang Keluar", "Operasional"], index=["Uang Masuk","Uang Keluar","Operasional"].index(selected_row['Tipe']))
                        jumlah_e = st.number_input("Jumlah (Rp)", value=float(selected_row['Jumlah']))
                        deskripsi_e = st.text_input("Deskripsi", value=str(selected_row['Deskripsi']))
                        tanggal_e = st.date_input("Tanggal", value=pd.to_datetime(selected_row['Tanggal']).date())
                        if st.button("Simpan Perubahan"):
                            df_res = update_transaction(tx_id, tipe_e, jumlah_e, deskripsi_e, tanggal_e, st.session_state['username'])
                            if df_res is not None:
                                st.success("Transaksi berhasil diperbarui.")
                                df_all = df_res
                            else:
                                st.error("Terjadi kesalahan: ID tidak ditemukan.")
            elif action == "Hapus Transaksi":
                if df_all.empty:
                    st.info("Tidak ada transaksi untuk dihapus.")
                else:
                    df_select = df_all.sort_values(by='Tanggal', ascending=False)
                    df_select['label'] = df_select.apply(lambda r: f"{r['Tanggal']} | {r['Tipe']} | {format_currency(r['Jumlah'])} | {r['Deskripsi'][:30]}", axis=1)
                    choice_del = st.selectbox("Pilih transaksi untuk dihapus", ["-"] + df_select['label'].tolist(), key="del_select")
                    if choice_del != "-":
                        selected_idx = df_select[df_select['label'] == choice_del].index[0]
                        tx_id = df_select.loc[selected_idx,'ID']
                        if st.button("Hapus Permanen"):
                            df_all = delete_transaction(tx_id)
                            if df_all is not None:
                                st.success("Transaksi dihapus.")
                            else:
                                st.error("Gagal menghapus. ID tidak ditemukan.")
        else:
            st.info("Login untuk menambah / edit / hapus transaksi.")

        st.markdown("---")
        st.download_button("Download CSV Semua Transaksi", data=get_csv_download(df_all), file_name="data_transaksi.csv", mime="text/csv")

    # --- RIGHT: laporan, filter, grafik ---
    with col_right:
        st.header("Laporan & Visualisasi")
        display_financial_summary(df_all)
        st.markdown("---")

        # Filters
        st.subheader("Filter Transaksi")
        tipe_filter = st.selectbox("Tipe", ["Semua", "Uang Masuk", "Uang Keluar", "Operasional"])
        if df_all.empty:
            min_date = datetime.date.today()
            max_date = datetime.date.today()
        else:
            min_date = pd.to_datetime(df_all['Tanggal']).min().date()
            max_date = pd.to_datetime(df_all['Tanggal']).max().date()

        start_date = st.date_input("Dari Tanggal", min_date)
        end_date = st.date_input("Sampai Tanggal", max_date)
        if start_date > end_date:
            st.error("Dari Tanggal tidak boleh lebih besar dari Sampai Tanggal.")
        df_filtered = filter_transactions(df_all, tipe=tipe_filter, start_date=start_date, end_date=end_date)
        st.write(f"Menampilkan transaksi dari **{start_date}** hingga **{end_date}** (Tipe: **{tipe_filter}**)")
        if not df_filtered.empty:
            df_view = df_filtered.sort_values(by='Tanggal', ascending=False).reset_index(drop=True)
            df_view_display = df_view[['ID', 'Tipe', 'Jumlah', 'Deskripsi', 'Tanggal', 'Dibuat_Oleh']]
            df_view_display['Jumlah'] = df_view_display['Jumlah'].apply(format_currency)
            st.dataframe(df_view_display, use_container_width=True)
        else:
            st.info("Tidak ada transaksi di rentang yang dipilih.")

        st.markdown("---")
        st.subheader("Grafik Transaksi")
        plot_transactions(df_filtered)

        st.subheader("Pembagian Kategori")
        plot_pie_chart(df_filtered)

        st.markdown("---")
        st.subheader("10 Transaksi Teratas")
        display_recent_transactions(df_all, n=10)

# ---------------------------
# ENTRY
# ---------------------------
if __name__ == "__main__":
    main()
