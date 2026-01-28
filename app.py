import streamlit as st
import pandas as pd
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Kalkulator Jejak Karbon (Slider Mode)",
    page_icon="🎚️",
    layout="wide"
)

# --- DATABASE FAKTOR EMISI (Konteks Indonesia) ---
EMISSION_FACTORS = {
    "Listrik (kWh)": 0.87,          # Faktor emisi Grid Jamali (rata-rata)
    "Bensin (Liter)": 2.33,         # Pertalite/Pertamax
    "Solar (Liter)": 2.68,          # Biosolar/Dexlite
    "LPG (kg)": 3.00,               # Elpiji
    "Sampah (kg)": 0.70             # Estimasi organik ke TPA
}

# --- HEADER ---
st.title("🎚️ Kalkulator Jejak Karbon Interaktif")
st.markdown("""
Geser **slider** di sebelah kiri (atau di atas pada tampilan mobile) untuk melihat bagaimana 
gaya hidup Anda mempengaruhi total emisi karbon secara *real-time*.
""")
st.markdown("---")

# --- SIDEBAR DENGAN SLIDER ---
st.sidebar.header("Psst... Geser di sini! 🎚️")

def user_input_features():
    st.sidebar.subheader("🏠 Energi Rumah")
    # Listrik: Range 0 - 2000 kWh, Default 150, Kelipatan 10
    listrik = st.sidebar.slider(
        "Tagihan Listrik (kWh/bulan)", 
        min_value=0, max_value=1000, value=150, step=10,
        help="Geser sesuai angka kWh di meteran/struk token Anda."
    )
    
    # LPG: Range 0 - 60 kg, Default 12 (4 tabung melon), Kelipatan 3 (berat tabung melon)
    lpg = st.sidebar.slider(
        "Konsumsi LPG (kg/bulan)", 
        min_value=0, max_value=60, value=12, step=3,
        help="1 Tabung melon = 3kg. 1 Tabung biru = 12kg."
    )
    
    st.sidebar.subheader("🚗 Transportasi")
    # Motor: Range 0 - 200 Liter, Default 30, Kelipatan 1
    jarak_motor = st.sidebar.slider(
        "BBM Motor (Liter/bulan)", 
        min_value=0, max_value=200, value=30, step=1
    )
    
    # Mobil: Range 0 - 500 Liter
    jarak_mobil = st.sidebar.slider(
        "BBM Mobil (Liter/bulan)", 
        min_value=0, max_value=400, value=0, step=5
    )
    
    # Pilihan jenis bahan bakar mobil
    jenis_bbm_mobil = st.sidebar.radio(
        "Jenis BBM Mobil:", 
        ("Bensin (Pertalite/Pertamax)", "Solar (Dex/Biosolar)")
    )
    
    st.sidebar.subheader("🗑️ Limbah")
    # Sampah: Range 0 - 100 kg
    sampah = st.sidebar.slider(
        "Sampah Buangan (kg/bulan)", 
        min_value=0, max_value=100, value=20, step=1,
        help="Estimasi sampah yang berakhir di tong sampah (bukan didaur ulang)."
    )
    
    return listrik, lpg, jarak_motor, jarak_mobil, jenis_bbm_mobil, sampah

# Memanggil fungsi input
listrik, lpg, bbm_motor, bbm_mobil, jenis_mobil_str, sampah = user_input_features()

# --- LOGIKA PERHITUNGAN ---
emisi_listrik = listrik * EMISSION_FACTORS["Listrik (kWh)"]
emisi_lpg = lpg * EMISSION_FACTORS["LPG (kg)"]
emisi_motor = bbm_motor * EMISSION_FACTORS["Bensin (Liter)"]

# Cek jenis mobil untuk faktor emisi yang tepat
if "Bensin" in jenis_mobil_str:
    emisi_mobil = bbm_mobil * EMISSION_FACTORS["Bensin (Liter)"]
else:
    emisi_mobil = bbm_mobil * EMISSION_FACTORS["Solar (Liter)"]

emisi_sampah = sampah * EMISSION_FACTORS["Sampah (kg)"]

total_emisi = emisi_listrik + emisi_lpg + emisi_motor + emisi_mobil + emisi_sampah

# --- VISUALISASI UTAMA (LAYOUT KOLOM) ---

# Kolom Kiri: Angka Utama
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Hasil Kalkulasi")
    # Card Total Emisi
    st.metric(
        label="Total Emisi Bulanan", 
        value=f"{total_emisi:.1f} kgCO2e",
        delta="Update Real-time",
        delta_color="off"
    )
    
    st.info(f"""
    **Rincian Cepat:**
    ⚡ Listrik: {emisi_listrik:.1f} kg
    🔥 LPG: {emisi_lpg:.1f} kg
    🛵 Motor: {emisi_motor:.1f} kg
    🚗 Mobil: {emisi_mobil:.1f} kg
    🗑️ Sampah: {emisi_sampah:.1f} kg
    """)
    
    # Pohon yang dibutuhkan (Estimasi 1 pohon menyerap ~20kg CO2/tahun)
    pohon_butuh = (total_emisi * 12) / 20
    st.warning(f"🌲 Anda butuh menanam **{int(pohon_butuh)} pohon** per tahun untuk menyerap jejak karbon ini.")

with col2:
    # Grafik Donut Chart yang lebih besar
    data_vis = {
        'Sumber': ['Listrik', 'LPG', 'Motor', 'Mobil', 'Sampah'],
        'Emisi': [emisi_listrik, emisi_lpg, emisi_motor, emisi_mobil, emisi_sampah]
    }
    df_vis = pd.DataFrame(data_vis)
    
    # --- BAGIAN YANG DIPERBAIKI (Tealgrn_r) ---
    fig = px.pie(
        df_vis, 
        values='Emisi', 
        names='Sumber',
        title='Proporsi Penyumbang Emisi Anda',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Tealgrn_r
    )
    # ------------------------------------------
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

# --- REKOMENDASI DINAMIS ---
st.markdown("### 💡 Apa yang bisa dikurangi?")
col_rec1, col_rec2, col_rec3 = st.columns(3)

if emisi_listrik > 100:
    col_rec1.error("⚡ Listrik Tinggi")
    col_rec1.write("Matikan AC saat keluar ruangan. Pertimbangkan ganti lampu ke LED.")
else:
    col_rec1.success("⚡ Listrik Aman")

if (emisi_motor + emisi_mobil) > 150:
    col_rec2.error("🚗 Transportasi Boros")
    col_rec2.write("Coba kurangi penggunaan kendaraan pribadi 1 hari dalam seminggu.")
else:
    col_rec2.success("🚗 Transportasi Efisien")

if emisi_sampah > 20:
    col_rec3.error("🗑️ Sampah Banyak")
    col_rec3.write("Pisahkan sampah organik untuk kompos. Kurangi plastik sekali pakai.")
else:
    col_rec3.success("🗑️ Minim Sampah")