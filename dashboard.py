import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

# ==============================================================================
# 0. CONFIG & SETTINGS
# ==============================================================================
st.set_page_config(
    page_title="FinTrack AI: Interactive Analysis",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Menghindari warning matplotlib di server cloud
import matplotlib
matplotlib.use("Agg")
# Baris di bawah ini sudah dihapus/dikomentari agar tidak error di Streamlit baru
# st.set_option('deprecation.showPyplotGlobalUse', False)

# Formatter Rupiah untuk Matplotlib grafik
def rupiah_formatter(x, pos):
    return f'Rp {x:,.0f}'

# ==============================================================================
# 1. LOAD DATA & ADVANCED FEATURE ENGINEERING
# ==============================================================================
# Membaca dataset utama
df = pd.read_excel("target tabungan.xlsx")

# Pastikan tipe data tanggal benar
df['tanggal'] = pd.to_datetime(df['tanggal'])

# --- PROSES FEATURE ENGINEERING ---
df['tahun'] = df['tanggal'].dt.year
df['bulan_nama'] = df['tanggal'].dt.strftime('%B %Y')
df['hari_nama'] = df['tanggal'].dt.day_name()

# ==============================================================================
# 2. SIDEBAR FILTER (Mata Rantai Utama Analisis)
# ==============================================================================
st.sidebar.title("🔍 FinTrack AI")
st.sidebar.markdown("Kelola & Analisis Kesehatan Finansial Anda secara Real-Time.")
st.sidebar.write("---")

# Filter 1: Nama Target (Fitur Lama Tetap Dipertahankan)
list_target = ["Semua Target"] + list(df['nama_target'].unique())
pilihan_target = st.sidebar.selectbox("🎯 Pilih Nama Target:", list_target)

# Filter 2: Periode Tahun (Multiselect seperti di contoh gambar)
list_tahun = sorted(list(df['tahun'].unique()))
pilihan_tahun = st.sidebar.columns(1)
pilihan_tahun = st.sidebar.multiselect("📅 Periode Tahun:", list_tahun, default=list_tahun)

# Filter 3: Rentang Bulan Analisis (Slider)
rentang_bulan = st.sidebar.slider("📅 Rentang Bulan Analisis:", 1, 12, (1, 12))

# --- Proses Sinkronisasi Filter ke Dataframe ---
df_filtered = df[df['tahun'].isin(pilihan_tahun)]
df_filtered = df_filtered[(df_filtered['tanggal'].dt.month >= rentang_bulan[0]) & (df_filtered['tanggal'].dt.month <= rentang_bulan[1])]

# ==============================================================================
# 3. TOP FINANCIAL METRICS (Kalkulasi Berbasis Feature Engineering)
# ==============================================================================
st.title("💰 FinTrack AI Dashboard")
st.markdown("Analisis komprehensif perilaku menabung, efisiensi target, dan tren akumulasi.")

# Kalkulasi Metrik Global untuk KPI Cards
total_tabungan_terkumpul = df_filtered['nabung_harian'].sum()
rata_global = df_filtered['nabung_harian'].mean()

# Mockup data target total (bisa disesuaikan dengan total kolom target riil kamu)
total_nilai_target = 840000000 
burn_rate = (total_tabungan_terkumpul / total_nilai_target) * 100 if total_nilai_target > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("📥 Total Nilai Target", f"Rp {total_nilai_target:,.0f}")
col2.metric("💸 Total Terkumpul (Filter)", f"Rp {total_tabungan_terkumpul:,.0f}")
col3.metric("🌱 Rata-rata Nabung Harian", f"Rp {rata_global:,.0f}")
col4.metric("📊 Rasio Pencapaian Global", f"{burn_rate:.2f}%")

st.write("---")

# ==============================================================================
# 4. TABS NAVIGATION (Memecah Setiap Pertanyaan Menjadi Kolom Eksklusif)
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Q1: Sisa Nominal Target", 
    "📊 Q2: Efisiensi Tabungan Harian", 
    "⏱️ Q3: Strategi Batas 30 Hari",
    "💡 Advanced AI Insights"
])

# ------------------------------------------------------------------------------
# TAB 1: PERTANYAAN 1 (Sisa Nominal yang Harus Ditabung per Target)
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("📌 Analisis Sisa Nominal per Target")
    
    # Filter tambahan jika user memilih target spesifik di sidebar
    df_q1 = df_filtered.copy()
    if pilihan_target != "Semua Target":
        df_q1 = df_q1[df_q1['nama_target'] == pilihan_target]
        
    # Logika Pertanyaan 1
    latest_data_q1 = df_q1.groupby('nama_target').last().reset_index()
    latest_data_q1['nominal_sisa'] = latest_data_q1['jumlah_target'] * latest_data_q1['sisa_target']
    latest_data_q1 = latest_data_q1.sort_values('nominal_sisa', ascending=False)
    
    if not latest_data_q1.empty:
        col_g1, col_t1 = st.columns([2, 1])
        
        with col_g1:
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            colors = ["#D3D3D3"] * len(latest_data_q1)
            if len(colors) > 0:
                colors[0] = "#72BCD4"  # Highlight sisa terbesar dengan warna biru muda
            
            sns.barplot(x='nominal_sisa', y='nama_target', data=latest_data_q1, palette=colors, ax=ax1)
            ax1.set_title('Sisa Nominal yang Harus Ditabung per Target', fontsize=14)
            ax1.set_xlabel('Sisa Uang (Rp)')
            ax1.set_ylabel('Nama Target')
            ax1.grid(axis='x', linestyle='--', alpha=0.6)
            ax1.xaxis.set_major_formatter(FuncFormatter(rupiah_formatter))
            st.pyplot(fig1)
            
        with col_t1:
            st.info("💡 **AI Insight Q1:**")
            target_tertinggi = latest_data_q1.iloc[0]['nama_target']
            sisa_tertinggi = latest_data_q1.iloc[0]['nominal_sisa']
            st.write(f"Target **{target_tertinggi}** memiliki sisa tanggungan terbesar yaitu senilai **Rp {sisa_tertinggi:,.0f}**. Fokus alokasi dana sangat disarankan dialihkan ke sini.")
            st.dataframe(latest_data_q1[['nama_target', 'nominal_sisa']].style.format({'nominal_sisa': 'Rp {:,.0f}'}))
    else:
        st.warning("Data tidak tersedia untuk kombinasi filter ini.")

# ------------------------------------------------------------------------------
# TAB 2: PERTANYAAN 2 (Rata-rata Nominal Tabungan Harian per Target)
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("📌 Analisis Efisiensi & Rata-rata Tabungan Harian")
    
    df_q2 = df_filtered.copy()
    if pilihan_target != "Semua Target":
        df_q2 = df_q2[df_q2['nama_target'] == pilihan_target]
        
    # Logika Pertanyaan 2
    avg_daily_saving = df_q2.groupby('nama_target')['nabung_harian'].mean().reset_index()
    avg_daily_saving = avg_daily_saving.sort_values('nabung_harian', ascending=False)
    
    if not avg_daily_saving.empty:
        col_g2, col_t2 = st.columns([2, 1])
        
        with col_g2:
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            sns.barplot(x='nabung_harian', y='nama_target', data=avg_daily_saving, palette='viridis', ax=ax2)
            
            # Benchmark line
            overall_avg = df_filtered['nabung_harian'].mean()
            ax2.axvline(overall_avg, color='red', linestyle='--', label=f'Rata-rata Global: Rp {overall_avg:,.0f}')
            
            ax2.set_title('Rata-rata Nominal Tabungan Harian per Target', fontsize=14)
            ax2.set_xlabel('Rata-rata Tabungan (Rp)')
            ax2.set_ylabel('Nama Target')
            ax2.legend()
            ax2.grid(axis='x', linestyle='--', alpha=0.5)
            ax2.xaxis.set_major_formatter(FuncFormatter(rupiah_formatter))
            st.pyplot(fig2)
            
        with col_t2:
            st.success("💡 **AI Insight Q2:**")
            hari_rajin = df_q2.groupby('hari_nama')['nabung_harian'].sum().idxmax()
            st.write(f"Berdasarkan performa historical data, Kamu tercatat paling konsisten dan rajin menyisihkan uang pada hari **{hari_rajin}**.")
            st.dataframe(avg_daily_saving.style.format({'nabung_harian': 'Rp {:,.0f}'}))
    else:
        st.warning("Data tidak tersedia.")

# ------------------------------------------------------------------------------
# TAB 3: PERTANYAAN 3 (Estimasi Tabungan Harian Agar Tercapai 30 Hari)
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("📌 Simulasi Target Kilat (Batas Waktu 30 Hari)")
    
    df_q3 = df_filtered.copy()
    if pilihan_target != "Semua Target":
        df_q3 = df_q3[df_q3['nama_target'] == pilihan_target]
        
    # Logika Pertanyaan 3
    latest_data_q3 = df_q3.groupby('nama_target').last().reset_index()
    latest_data_q3['nominal_sisa'] = latest_data_q3['jumlah_target'] * latest_data_q3['sisa_target']
    latest_data_q3['target_harian_30'] = latest_data_q3['nominal_sisa'] / 30
    latest_data_q3 = latest_data_q3.sort_values('target_harian_30', ascending=False)
    
    if not latest_data_q3.empty:
        col_g3, col_t3 = st.columns([2, 1])
        
        with col_g3:
            fig3, ax3 = plt.subplots(figsize=(10, 5))
            colors_q3 = sns.color_palette("Reds_r", len(latest_data_q3))
            sns.barplot(x='target_harian_30', y='nama_target', data=latest_data_q3, palette=colors_q3, ax=ax3)
            
            mean_target_30 = latest_data_q3['target_harian_30'].mean()
            if mean_target_30 > 0:
                ax3.axvline(mean_target_30, color='blue', linestyle='--', label=f'Rata-rata Kuota: Rp {mean_target_30:,.0f}')
                
            ax3.set_title('Estimasi Tabungan Harian per Target (Batas Selesai 30 Hari)', fontsize=14)
            ax3.set_xlabel('Nominal Harus Ditabung per Hari (Rp)')
            ax3.set_ylabel('Nama Target')
            ax3.legend()
            ax3.grid(axis='x', linestyle='--', alpha=0.5)
            ax3.xaxis.set_major_formatter(FuncFormatter(rupiah_formatter))
            st.pyplot(fig3)
            
        with col_t3:
            st.warning("⚠️ **Tingkat Urgensi Beban Finansial:**")
            st.write("Semakin merah grafik, semakin besar beban harian yang harus kamu sisihkan jika bersikeras ingin menutup target dalam waktu 1 bulan penuh.")
            st.dataframe(latest_data_q3[['nama_target', 'target_harian_30']].style.format({'target_harian_30': 'Rp {:,.0f}'}))
    else:
        st.warning("Data kosong.")

# ------------------------------------------------------------------------------
# TAB 4: ADVANCED FEATURE ENGINEERING & PREDICTIONS (Nilai Tambah!)
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("🧠 FinTrack AI Smart Predictive Analytics")
    st.markdown("Bagian ini menggabungkan fitur harian asli dengan rata-rata kemampuan finansialmu untuk memprediksi tanggal pencapaian.")
    
    # Gabung data rata-rata harian saat ini dengan target sisa (Feature Engineering Lanjutan)
    summary_df = df_filtered.groupby('nama_target').agg(
        rata_sekarang=('nabung_harian', 'mean'),
        total_terkumpul=('nabung_harian', 'sum')
    ).reset_index()
    
    # Menghitung estimasi hari sisa secara realistis berdasarkan kebiasaan riil user
    # (Menggunakan asumsi harga barang konstan dari total yang harus dicapai)
    latest_status = df_filtered.groupby('nama_target').last().reset_index()
    latest_status['nominal_sisa'] = latest_status['jumlah_target'] * latest_status['sisa_target']
    
    analytics_df = pd.merge(summary_df, latest_status[['nama_target', 'nominal_sisa']], on='nama_target')
    
    # FEATURE ENGINEERING: Membuat metrik "Hari Menuju Goal" & "Status Kelayakan"
    analytics_df['Hari_Menuju_Goal'] = analytics_df['nominal_sisa'] / analytics_df['rata_sekarang']
    
    st.write("### 📅 Prediksi Selesai Realistis Berdasarkan Performa Menabung")
    
    # Tampilan kartu informasi dinamis berdasarkan target pilihan di sidebar
    if pilihan_target != "Semua Target":
        target_info = analytics_df[analytics_df['nama_target'] == pilihan_target]
        if not target_info.empty:
            hari_lagi = target_info.iloc[0]['Hari_Menuju_Goal']
            if hari_lagi > 0:
                st.info(f"🔮 Berdasarkan rata-rata menabungmu sebesar **Rp {target_info.iloc[0]['rata_sekarang']:,.0f}/hari**, target **{pilihan_target}** diprediksi akan lunas total dalam **{round(hari_lagi)} hari** lagi.")
            else:
                st.success(f"✅ Target **{pilihan_target}** sudah lunas sepenuhnya!")
    else:
        st.write("Silakan pilih target spesifik di sidebar untuk memunculkan model estimasi tanggal pencapaian.")
        st.dataframe(analytics_df.style.format({
            'rata_sekarang': 'Rp {:,.0f}',
            'total_terkumpul': 'Rp {:,.0f}',
            'nominal_sisa': 'Rp {:,.0f}',
            'Hari_Menuju_Goal': '{:.1f} Hari'
        }))