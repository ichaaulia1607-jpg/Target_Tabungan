import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

# Konfigurasi Halaman
st.set_page_config(page_title="FinTrack AI - Interactive Dashboard", layout="wide")

def format_rupiah(x, pos):
    return f'Rp {x:,.0f}'
formatter = FuncFormatter(format_rupiah)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_excel('target tabungan.xlsx')
    if df['tanggal'].dtype == 'int64' or df['tanggal'].dtype == 'float64':
        df['tanggal'] = pd.to_datetime(df['tanggal'], unit='D', origin='1899-12-30')
    else:
        df['tanggal'] = pd.to_datetime(df['tanggal'])
    return df

try:
    df = load_data()

    # --- SIDEBAR FILTER ---
    st.sidebar.header("🔍 Filter Dashboard")
    list_target = ["Semua Target"] + sorted(df['nama_target'].unique().tolist())
    selected_target = st.sidebar.selectbox("Pilih Nama Target:", list_target)

    st.title("💰 FinTrack AI: Interactive Analysis")
    
    if selected_target == "Semua Target":
        st.markdown("### Menampilkan Perbandingan Semua Target")
        
        # Grafik Q1 & Q2 (Seperti kode pertama kamu)
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sisa Nominal per Target")
            latest = df.groupby('nama_target').last().reset_index()
            latest['nominal_sisa'] = latest['jumlah_target'] * latest['sisa_target']
            latest = latest.sort_values('nominal_sisa', ascending=False)
            
            fig1, ax1 = plt.subplots()
            sns.barplot(x='nominal_sisa', y='nama_target', data=latest, palette='Blues_r', ax=ax1)
            ax1.xaxis.set_major_formatter(formatter)
            st.pyplot(fig1)

        with col2:
            st.subheader("Rata-rata Nabung Harian")
            avg_daily = df.groupby('nama_target')['nabung_harian'].mean().reset_index().sort_values('nabung_harian', ascending=False)
            fig2, ax2 = plt.subplots()
            sns.barplot(x='nabung_harian', y='nama_target', data=avg_daily, palette='viridis', ax=ax2)
            ax2.xaxis.set_major_formatter(formatter)
            st.pyplot(fig2)

    else:
        # --- FITUR INTERAKTIF: ANALISIS PER TARGET ---
        st.markdown(f"### 🎯 Analisis Detail: {selected_target}")
        target_df = df[df['nama_target'] == selected_target].sort_values('tanggal')
        
        c1, c2, c3 = st.columns(3)
        status_skrg = target_df['status'].iloc[-1]
        progres_skrg = target_df['progres'].iloc[-1] * 100
        total_tabungan = target_df['nabung_harian'].sum()
        
        c1.metric("Status Saat Ini", status_skrg)
        c2.metric("Progres Persentase", f"{progres_skrg:.1f}%")
        c3.metric("Total Terkumpul", f"Rp {total_tabungan:,.0f}")

        # Grafik Historis per Barang
        st.subheader(f"Riwayat Menabung {selected_target}")
        fig3, ax3 = plt.subplots(figsize=(12, 4))
        ax3.plot(target_df['tanggal'], target_df['nabung_harian'], marker='o', linestyle='-', color='#72BCD4')
        ax3.fill_between(target_df['tanggal'], target_df['nabung_harian'], alpha=0.2, color='#72BCD4')
        ax3.yaxis.set_major_formatter(formatter)
        st.pyplot(fig3)

    # --- FITUR TAMBAHAN MENARIK: SMART INSIGHTS ---
    st.divider()
    st.header("💡 FinTrack Smart Insights")
    
    with st.container():
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.info("**Hari Paling Produktif**")
            df['hari'] = df['tanggal'].dt.day_name()
            best_day = df.groupby('hari')['nabung_harian'].sum().idxmax()
            st.write(f"Berdasarkan data, Kamu paling rajin menabung pada hari **{best_day}**.")
            
        with col_b:
            st.success("**Rekomendasi Strategi**")
            if (df['nabung_harian'] == 0).any():
                st.write("Ada beberapa hari kosong. Cobalah fitur *Auto-Debit* agar target lebih cepat tercapai!")
            else:
                st.write("Konsistensi kamu sangat bagus! Pertahankan ritme ini untuk target besar berikutnya.")

except Exception as e:
    st.error(f"Gagal memproses data: {e}")