# app.py
# Aplikasi Keuangan — Musholla At-Taqwa RT.1 Dusun Klotok
# Fitur: multi-user login, upload bukti, edit/hapus, log aktivitas, backup, download CSV
# Tema: Putih - Hijau khas NU dengan sedikit ornamen

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# ==============================
# KONFIGURASI USER & FILE PATH
# ==============================
USERS = {
    "ferri": "ferri@123",
    "alfan": "ferri@123",
    "sunhadi": "ferri@123",
    "riki": "ferri@123",
    "riaji": "ferri@123",
    "bayu": "ferri@123"
}

DATA_FILE = "data.csv"
LOG_FILE = "log.csv"
BUKTI_FOLDER = "bukti"
BACKUP_FOLDER = "backup"
NU_LOGO_URL = "https://i.pinimg.com/originals/f8/bf/8a/f8bf8a1221a81747154698816b7c9113.jpg"  # small logo used as ornament
BACKGROUND_PATTERN_URL = "https://i.imgur.com/6YVQy0Y.png"  # subtle pattern; replace if desired

# Pastikan folder ada
os.makedirs(BUKTI_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# ==============================
# HELPERS: DATA & LOG
# ==============================
REQUIRED_COLUMNS = ["tanggal", "jenis", "keterangan", "jumlah", "panitia", "bukti"]

def ensure_datafile():
    """Buat data file dengan header jika tidak ada / rusak"""
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=REQUIRED_COLUMNS).to_csv(DATA_FILE, index=False)
    else:
        try:
            df_check = pd.read_csv(DATA_FILE)
            # jika kolom tidak sesuai, buat ulang header (keamanan)
            missing = [c for c in REQUIRED_COLUMNS if c not in df_check.columns]
            if missing:
                pd.DataFrame(columns=REQUIRED_COLUMNS).to_csv(DATA_FILE, index=False)
        except Exception:
            pd.DataFrame(columns=REQUIRED_COLUMNS).to_csv(DATA_FILE, index=False)

def load_data():
    ensure_datafile()
    return pd.read_csv(DATA_FILE)

def save_data(df):
    # simpan dan backup
    df.to_csv(DATA_FILE, index=False)
    backup_name = os.path.join(BACKUP_FOLDER, f"backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv")
    try:
        df.to_csv(backup_name, index=False)
    except Exception:
        pass

def ensure_logfile():
    if not os.path.exists(LOG_FILE):
        pd.DataFrame(columns=["waktu", "panitia", "aksi"]).to_csv(LOG_FILE, index=False)

def load_log():
    ensure_logfile()
    return pd.read_csv(LOG_FILE)

def append_log(panitia, aksi):
    ensure_logfile()
    log_df = load_log()
    new = pd.DataFrame({
        "waktu": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "panitia": [panitia],
        "aksi": [aksi]
    })
    log_df = pd.concat([log_df, new], ignore_index=True)
    log_df.to_csv(LOG_FILE, index=False)

# ==============================
# HELPERS: BUKTI (UPLOAD) & DOWNLOAD
# ==============================
def save_bukti(uploaded_file):
    """Simpan file upload (jpg/png/jpeg) ke folder bukti, kembalikan path relatif"""
    if uploaded_file is None:
        return ""
    safe_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
    out_path = os.path.join(BUKTI_FOLDER, safe_name)
    try:
        # simpan raw bytes — tidak perlu PIL
        with open(out_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return out_path
    except Exception:
        return ""

def get_csv_bytes(df):
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output.getvalue()

# ==============================
# THEME & ORNAMENT (CSS)
# ==============================
def nu_theme():
    st.markdown(
        f"""
    <style>
    /* Background pattern */
    .stApp {{
        background-color: #ffffff !important;
        background-image: url('{BACKGROUND_PATTERN_URL}');
        background-size: 300px 300px;
        background-repeat: repeat;
        background-position: center;
    }}

    /* Header / Titles */
    h1, h2, h3, h4 {{
        color: #1D6F42 !important;
        font-weight: 700 !important;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: #E7F5EB !important;
        border-right: 3px solid #1D6F42;
    }}

    /* Header logo */
    .nu-logo {{
        width:40px;
        height:40px;
        border-radius:6px;
        margin-right:10px;
    }}

    /* Tombol */
    .stButton>button {{
        background-color: #1D6F42 !important;
        color: #ffffff !important;
        border-radius: 8px;
        padding: 6px 18px;
        box-shadow: none !important;
        border: none !important;
    }}
    .stButton>button:hover {{
        background-color: #14532D !important;
    }}

    /* Metric */
    div[data-testid="stMetric"] {{
        background-color: #F2FBF5 !important;
        padding: 8px 12px !important;
        border-radius: 10px !important;
        border: 1px solid #C7EAD3 !important;
    }}

    /* Input border */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stDateInput>div>div>input {{
        border: 1.5px solid #1D6F42 !important;
        border-radius: 6px;
    }}

    /* Dataframe header */
    .stDataFrame thead th {{
        background-color: #1D6F42 !important;
        color: #ffffff !important;
        font-weight: 600;
    }}

    /* Small card for logo+title */
    .title-row {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}

    /* make file uploader nicer */
    .stFileUploader > div {{
        border: 1px dashed #1D6F42 !important;
        border-radius: 6px !important;
        padding: 8px !important;
    }}

    </style>
    """,
        unsafe_allow_html=True,
    )

# ==============================
# PAGE: LOGIN
# ==============================
def login_page():
    st.markdown(
        f"""
        <div class="title-row">
            <img class="nu-logo" src="{NU_LOGO_URL}" />
            <h1>Musholla At-Taqwa — Aplikasi Keuangan</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("Aplikasi sederhana untuk pencatatan dan pelaporan keuangan pembangunan musholla.")
    st.sidebar.title("Akses Panitia")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    btn = st.sidebar.button("Login")

    if btn:
        if username in USERS and USERS[username] == password:
            st.session_state["user"] = username
            append_log(username, "Login")
            st.experimental_rerun()
        else:
            st.sidebar.error("Username atau password salah")

# ==============================
# PAGE: ADMIN (INPUT / EDIT / HAPUS / LOG / DOWNLOAD / DASHBOARD)
# ==============================
def admin_page(user):
    # header with logo
    st.markdown(
        f"""
        <div class="title-row">
            <img class="nu-logo" src="{NU_LOGO_URL}" />
            <h2>Selamat datang, {user}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = load_data()
    # normalize columns if needed
    for c in REQUIRED_COLUMNS:
        if c not in df.columns:
            df[c] = ""

    menu = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Input Kas Masuk", "Input Kas Keluar", "Edit / Hapus", "Log Aktivitas", "Download Laporan", "Publikasi (Mode Publik)"]
    )

    # ---------- DASHBOARD ----------
    if menu == "Dashboard":
        st.subheader("📊 Ringkasan Keuangan")
        if df.empty:
            st.info("Belum ada transaksi.")
        else:
            # ensure proper types
            df["jumlah"] = pd.to_numeric(df["jumlah"], errors="coerce").fillna(0)
            df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")

            total_masuk = int(df[df["jenis"] == "masuk"]["jumlah"].sum())
            total_keluar = int(df[df["jenis"] == "keluar"]["jumlah"].sum())
            saldo = total_masuk - total_keluar

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Masuk", f"Rp {total_masuk:,.0f}")
            c2.metric("Total Keluar", f"Rp {total_keluar:,.0f}")
            c3.metric("Saldo Akhir", f"Rp {saldo:,.0f}")

            st.markdown("---")
            st.subheader("📅 Grafik Pemasukan / Pengeluaran (Per Hari)")
            chart_df = df.copy()
            chart_df = chart_df.dropna(subset=["tanggal"])
            if not chart_df.empty:
                chart_df_group = chart_df.groupby([pd.Grouper(key="tanggal", freq="D"), "jenis"])["jumlah"].sum().unstack(fill_value=0)
                st.bar_chart(chart_df_group)
            else:
                st.info("Tidak ada data tanggal valid untuk grafik.")

    # ---------- INPUT KAS MASUK ----------
    if menu == "Input Kas Masuk":
        st.subheader("📥 Input Kas Masuk")
        with st.form("form_masuk", clear_on_submit=True):
            tgl = st.date_input("Tanggal", datetime.now(), key="tgl_masuk")
            ket = st.text_input("Keterangan")
            jml = st.number_input("Jumlah (Rp)", min_value=0, step=1000, key="jml_masuk")
            bukti = st.file_uploader("Upload Bukti (opsional)", type=["jpg", "png", "jpeg"], key="bukti_masuk")
            submit = st.form_submit_button("Simpan Kas Masuk")

        if submit:
            saved_bukti = save_bukti(bukti) if bukti is not None else ""
            new = {
                "tanggal": str(tgl),
                "jenis": "masuk",
                "keterangan": ket,
                "jumlah": float(jml),
                "panitia": user,
                "bukti": saved_bukti
            }
            df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            save_data(df)
            append_log(user, f"Tambah kas masuk Rp {jml} - {ket}")
            st.success("Kas masuk tersimpan.")

    # ---------- INPUT KAS KELUAR ----------
    if menu == "Input Kas Keluar":
        st.subheader("📤 Input Kas Keluar")
        with st.form("form_keluar", clear_on_submit=True):
            tgl = st.date_input("Tanggal", datetime.now(), key="tgl_keluar")
            ket = st.text_input("Keterangan", key="ket_keluar")
            jml = st.number_input("Jumlah (Rp)", min_value=0, step=1000, key="jml_keluar")
            bukti = st.file_uploader("Upload Bukti (opsional)", type=["jpg", "png", "jpeg"], key="bukti_keluar")
            submit = st.form_submit_button("Simpan Kas Keluar")

        if submit:
            saved_bukti = save_bukti(bukti) if bukti is not None else ""
            new = {
                "tanggal": str(tgl),
                "jenis": "keluar",
                "keterangan": ket,
                "jumlah": float(jml),
                "panitia": user,
                "bukti": saved_bukti
            }
            df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            save_data(df)
            append_log(user, f"Tambah kas keluar Rp {jml} - {ket}")
            st.success("Kas keluar tersimpan.")

    # ---------- EDIT / HAPUS ----------
    if menu == "Edit / Hapus":
        st.subheader("✏️ Edit atau Hapus Transaksi")
        if df.empty:
            st.info("Belum ada transaksi.")
        else:
            st.write("Daftar terakhir (index ditampilkan di kolom kiri):")
            # show with index
            df_display = df.copy()
            df_display.index.name = "index"
            st.dataframe(df_display.reset_index())

            idx = st.number_input("Masukkan index baris untuk edit/hapus", min_value=0, max_value=max(0, len(df)-1), step=1, value=0)
            row = df.loc[int(idx)]

            st.write("Data yang dipilih:")
            st.json(row.to_dict())

            with st.form("edit_form"):
                new_ket = st.text_input("Keterangan", value=str(row.get("keterangan","")))
                new_jml = st.number_input("Jumlah (Rp)", min_value=0, value=int(float(row.get("jumlah",0))))
                new_bukti = st.file_uploader("Ganti Bukti (opsional)", type=["jpg","png","jpeg"], key="ganti_bukti")
                save_btn = st.form_submit_button("Simpan Perubahan")

            if save_btn:
                # simpan bukti baru jika ada
                bukti_path = row.get("bukti","")
                if new_bukti is not None:
                    bukti_path = save_bukti(new_bukti)
                df.at[int(idx), "keterangan"] = new_ket
                df.at[int(idx), "jumlah"] = float(new_jml)
                df.at[int(idx), "bukti"] = bukti_path
                df.at[int(idx), "panitia"] = user  # update editor
                save_data(df)
                append_log(user, f"Edit transaksi index {idx}")
                st.success("Perubahan disimpan.")
                st.experimental_rerun()

            if st.button("Hapus baris ini"):
                append_log(user, f"Hapus transaksi index {idx}")
                df = df.drop(int(idx)).reset_index(drop=True)
                save_data(df)
                st.success("Baris dihapus.")
                st.experimental_rerun()

    # ---------- LOG AKTIVITAS ----------
    if menu == "Log Aktivitas":
        st.subheader("📜 Log Aktivitas")
        log_df = load_log()
        if log_df.empty:
            st.info("Belum ada aktivitas.")
        else:
            st.dataframe(log_df)

    # ---------- DOWNLOAD LAPORAN ----------
    if menu == "Download Laporan":
        st.subheader("📥 Download Laporan (CSV)")
        if df.empty:
            st.info("Belum ada data untuk diunduh.")
        else:
            st.write("Unduh seluruh data transaksi saat ini:")
            csv_bytes = get_csv_bytes(df)
            st.download_button("Download CSV", csv_bytes, "laporan-keuangan.csv", mime="text/csv")
            # juga sediakan preview singkat
            st.markdown("Preview 10 baris terakhir:")
            st.dataframe(df.tail(10))

    # ---------- MODE PUBLISH (tampilkan halaman publik yang bisa dishare) ----------
    if menu == "Publikasi (Mode Publik)":
        st.subheader("🔗 Halaman Publik (Preview)")
        st.info("Halaman publik menampilkan ringkasan dan tabel, tanpa tombol edit.")
        if df.empty:
            st.info("Belum ada data.")
        else:
            df_pub = df.copy()
            df_pub["tanggal"] = pd.to_datetime(df_pub["tanggal"], errors="coerce")
            total_masuk = df_pub[df_pub["jenis"] == "masuk"]["jumlah"].sum()
            total_keluar = df_pub[df_pub["jenis"] == "keluar"]["jumlah"].sum()
            saldo = total_masuk - total_keluar

            st.metric("Total Masuk", f"Rp {int(total_masuk):,}")
            st.metric("Total Keluar", f"Rp {int(total_keluar):,}")
            st.metric("Saldo Akhir", f"Rp {int(saldo):,}")

            st.markdown("Daftar transaksi (publik):")
            st.dataframe(df_pub.sort_values("tanggal", ascending=False).reset_index(drop=True))

    # ---------- LOGOUT ----------
    st.markdown("---")
    if st.button("Logout"):
        append_log(user, "Logout")
        if "user" in st.session_state:
            del st.session_state["user"]
        st.experimental_rerun()

# ==============================
# PAGE: PUBLIC (tanpa login)
# ==============================
def public_page():
    st.markdown(
        f"""
        <div class="title-row">
            <img class="nu-logo" src="{NU_LOGO_URL}" />
            <h2>Musholla At-Taqwa — Laporan Publik</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    ensure_datafile()
    df = load_data()
    if df.empty:
        st.info("Belum ada data transaksi.")
        return

    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
    total_masuk = df[df["jenis"] == "masuk"]["jumlah"].sum()
    total_keluar = df[df["jenis"] == "keluar"]["jumlah"].sum()
    saldo = total_masuk - total_keluar

    st.subheader("Ringkasan Keuangan")
    st.write(f"**Total Masuk:** Rp {int(total_masuk):,}")
    st.write(f"**Total Keluar:** Rp {int(total_keluar):,}")
    st.write(f"**Saldo Akhir:** Rp {int(saldo):,}")

    st.subheader("Riwayat Transaksi (Terbaru)")
    st.dataframe(df.sort_values("tanggal", ascending=False).head(50))

    st.info("Untuk fitur lengkap (input/edit), silakan login panitia.")

# ==============================
# ENTREE: MAIN
# ==============================
def main():
    st.set_page_config(page_title="Musholla At-Taqwa - Keuangan", layout="wide")
    nu_theme()

    st.sidebar.image(NU_LOGO_URL, width=90)
    st.sidebar.title("Musholla At-Taqwa")
    st.sidebar.write("RT.1 Dusun Klotok — Aplikasi Keuangan")

    page_mode = st.sidebar.selectbox("Mode Aplikasi", ["Login (Panitia)", "Publik (Tampilkan Laporan Publik)"])

    if page_mode == "Publik (Tampilkan Laporan Publik)":
        public_page()
        return

    # Login flow
    if "user" not in st.session_state:
        login_page()
    else:
        admin_page(st.session_state["user"])

if __name__ == "__main__":
    main()
