import streamlit as st
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt

# ==========================================================
# KONFIGURASI PASSWORD
# ==========================================================
ADMIN_PASSWORD = "ferri@123"


# ==========================================================
# FUNGSI PEMBANTU
# ==========================================================
def load_csv(path):
    if not os.path.exists(path):
        df = pd.DataFrame(columns=["Tanggal", "Tipe", "Jumlah", "Deskripsi"])
        df.to_csv(path, index=False)
        return df

    try:
        df = pd.read_csv(path)
        if df.empty:
            return pd.DataFrame(columns=["Tanggal", "Tipe", "Jumlah", "Deskripsi"])
        return df
    except:
        return pd.DataFrame(columns=["Tanggal", "Tipe", "Jumlah", "Deskripsi"])


def save_csv(df, path):
    df.to_csv(path, index=False)


# ==========================================================
# HALAMAN ADMIN (INPUT / EDIT / HAPUS)
# ==========================================================
def admin_page():
    st.header("📌 Input & Manajemen Transaksi")

    file_path = "data_keuangan.csv"
    df = load_csv(file_path)

    menu = st.radio("Pilih Menu", ["Kas Masuk", "Kas Keluar", "Edit Transaksi", "Hapus Transaksi"])

    # ------------------------------------------------------
    # INPUT KAS MASUK
    # ------------------------------------------------------
    if menu == "Kas Masuk":
        st.subheader("💰 Tambah Kas Masuk")

        tanggal = st.date_input("Tanggal", datetime.date.today())
        jumlah = st.number_input("Jumlah (Rp)", min_value=0)
        deskripsi = st.text_input("Deskripsi")

        if st.button("Simpan Kas Masuk"):
            new_row = pd.DataFrame([{
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Tipe": "Masuk",
                "Jumlah": jumlah,
                "Deskripsi": deskripsi
            }])

            df = pd.concat([df, new_row], ignore_index=True)
            save_csv(df, file_path)
            st.success("Kas masuk berhasil ditambahkan!")

    # ------------------------------------------------------
    # INPUT KAS KELUAR
    # ------------------------------------------------------
    if menu == "Kas Keluar":
        st.subheader("💸 Tambah Kas Keluar")

        tanggal = st.date_input("Tanggal", datetime.date.today())
        jumlah = st.number_input("Jumlah (Rp)", min_value=0)
        deskripsi = st.text_input("Deskripsi")

        if st.button("Simpan Kas Keluar"):
            new_row = pd.DataFrame([{
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Tipe": "Keluar",
                "Jumlah": jumlah,
                "Deskripsi": deskripsi
            }])

            df = pd.concat([df, new_row], ignore_index=True)
            save_csv(df, file_path)
            st.success("Kas keluar berhasil ditambahkan!")

    # ------------------------------------------------------
    # EDIT TRANSAKSI
    # ------------------------------------------------------
    if menu == "Edit Transaksi":
        st.subheader("✏️ Edit Transaksi")

        if df.empty:
            st.warning("Belum ada transaksi.")
            return

        index = st.number_input("Pilih Index Transaksi", 0, len(df)-1, 0)

        st.write(df.iloc[index])

        tanggal = st.date_input("Tanggal", datetime.date.fromisoformat(df.iloc[index]["Tanggal"]))
        tipe = st.selectbox("Tipe", ["Masuk", "Keluar"], index=0 if df.iloc[index]["Tipe"] == "Masuk" else 1)
        jumlah = st.number_input("Jumlah (Rp)", min_value=0, value=int(df.iloc[index]["Jumlah"]))
        deskripsi = st.text_input("Deskripsi", df.iloc[index]["Deskripsi"])

        if st.button("Simpan Perubahan"):
            df.at[index, "Tanggal"] = tanggal.strftime("%Y-%m-%d")
            df.at[index, "Tipe"] = tipe
            df.at[index, "Jumlah"] = jumlah
            df.at[index, "Deskripsi"] = deskripsi
            save_csv(df, file_path)
            st.success("Transaksi berhasil diperbarui!")

    # ------------------------------------------------------
    # HAPUS TRANSAKSI
    # ------------------------------------------------------
    if menu == "Hapus Transaksi":
        st.subheader("🗑️ Hapus Transaksi")

        if df.empty:
            st.warning("Belum ada transaksi.")
            return

        index = st.number_input("Index Transaksi", 0, len(df)-1, 0)
        st.write(df.iloc[index])

        if st.button("Hapus"):
            df = df.drop(index)
            df.reset_index(drop=True, inplace=True)
            save_csv(df, file_path)
            st.error("Transaksi berhasil dihapus!")


# ==========================================================
# HALAMAN LAPORAN / RINGKASAN
# ==========================================================
def laporan_page():
    st.header("📊 Laporan Keuangan Musholla At Taqwa")

    file_path = "data_keuangan.csv"
    df = load_csv(file_path)

    if df.empty:
        st.info("Belum ada data transaksi.")
        return

    st.subheader("📘 Semua Transaksi")
    st.dataframe(df)

    # Ringkasan
    pemasukan = df[df["Tipe"] == "Masuk"]["Jumlah"].sum()
    pengeluaran = df[df["Tipe"] == "Keluar"]["Jumlah"].sum()
    saldo = pemasukan - pengeluaran

    st.subheader("📌 Ringkasan")
    st.write(f"**Total Pemasukan:** Rp {pemasukan:,.0f}")
    st.write(f"**Total Pengeluaran:** Rp {pengeluaran:,.0f}")
    st.write(f"### 💵 Saldo Akhir: Rp {saldo:,.0f}")

    # Grafik
    st.subheader("📈 Grafik Keuangan")
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])

    fig, ax = plt.subplots(figsize=(10, 5))
    df.groupby(df["Tanggal"].dt.to_period("M"))["Jumlah"].sum().plot(ax=ax)
    st.pyplot(fig)


# ==========================================================
# MAIN PROGRAM
# ==========================================================
def main():
    st.title("Aplikasi Keuangan — Musholla At Taqwa RT.1 Dusun Klotok")
    st.write("Aplikasi sederhana untuk pencatatan dan pelaporan keuangan pembangunan musholla.")

    st.sidebar.subheader("Login Admin")
    password = st.sidebar.text_input("Masukkan Password", type="password")

    if password == ADMIN_PASSWORD:
        st.sidebar.success("Login berhasil!")
        menu = st.sidebar.radio("Menu", ["Input / Edit", "Laporan"])
        
        if menu == "Input / Edit":
            admin_page()
        else:
            laporan_page()

    elif password != "":
        st.sidebar.error("Password salah.")


if __name__ == "__main__":
    main()
