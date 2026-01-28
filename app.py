import streamlit as st
import pandas as pd
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Carbon Footprint Tracker Pro",
    page_icon="🌱",
    layout="wide"
)

# --- DATABASE FAKTOR EMISI & REFERENSI ---
FAKTOR_EMISI = {
    "Listrik": {
        "nilai": 0.87, 
        "satuan": "kgCO2/kWh",
        "sumber": "Kementerian ESDM (Grid Jamali)",
        "desc": "Emisi dari pembangkit listrik (dominan batubara) di Jawa-Bali."
    },
    "Bensin": {
        "nilai": 2.33, 
        "satuan": "kgCO2/Liter",
        "sumber": "IPCC Guidelines 2006",
        "desc": "Emisi pembakaran bensin (Pertalite/Pertamax)."
    },
    "Solar": {
        "nilai": 2.68, 
        "satuan": "kgCO2/Liter",
        "sumber": "IPCC Guidelines 2006",
        "desc": "Emisi pembakaran diesel/solar."
    },
    "LPG": {
        "nilai": 3.00, 
        "satuan": "kgCO2/kg",
        "sumber": "IPCC (Stationary Combustion)",
        "desc": "Emisi gas elpiji untuk memasak."
    },
    "Sampah": {
        "nilai": 0.70, 
        "satuan": "kgCO2e/kg",
        "sumber": "KLHK & World Bank (Estimasi)",
        "desc": "Emisi metana dari sampah organik di TPA."
    }
}

# --- HEADER ---
st.title("🌱 Kalkulator Jejak Karbon Pribadi")
st.markdown("""
Aplikasi ini membantu Anda menghitung, memahami, dan mencari solusi untuk mengurangi dampak lingkungan Anda.
""")
st.markdown("---")

# --- SIDEBAR: INPUT DATA ---
st.sidebar.header("📝 Input Aktivitas Bulanan")

def user_input_features():
    st.sidebar.subheader("🏠 Energi Rumah")
    listrik = st.sidebar.slider("Listrik (kWh)", 0, 1000, 150, 10, help="Cek struk token/tagihan PLN Anda.")
    lpg = st.sidebar.slider("LPG (kg)", 0, 60, 12, 3, help="1 Tabung melon = 3kg.")
    
    st.sidebar.subheader("🚗 Transportasi")
    motor = st.sidebar.slider("Bensin Motor (Liter)", 0, 150, 30, 1)
    mobil = st.sidebar.slider("BBM Mobil (Liter)", 0, 400, 0, 5)
    jenis_bbm = st.sidebar.radio("Jenis BBM Mobil", ["Bensin", "Solar"])
    
    st.sidebar.subheader("🗑️ Limbah")
    sampah = st.sidebar.slider("Sampah ke TPA (kg)", 0, 100, 20, 1, help="Estimasi sampah harian x 30 hari.")
    
    return listrik, lpg, motor, mobil, jenis_bbm, sampah

listrik, lpg, motor, mobil, jenis_bbm, sampah = user_input_features()

# --- PROSES PERHITUNGAN ---
e_listrik = listrik * FAKTOR_EMISI["Listrik"]["nilai"]
e_lpg = lpg * FAKTOR_EMISI["LPG"]["nilai"]
e_motor = motor * FAKTOR_EMISI["Bensin"]["nilai"]

if jenis_bbm == "Bensin":
    e_mobil = mobil * FAKTOR_EMISI["Bensin"]["nilai"]
else:
    e_mobil = mobil * FAKTOR_EMISI["Solar"]["nilai"]

e_sampah = sampah * FAKTOR_EMISI["Sampah"]["nilai"]

total_emisi = e_listrik + e_lpg + e_motor + e_mobil + e_sampah

# --- 1. GAMIFIKASI STATUS (LEVEL) ---
st.subheader("🏆 Status Lingkungan Anda")
col_status, col_score = st.columns([3, 1])

with col_status:
    if total_emisi < 150:
        st.success("🎉 **Level: ECO WARRIOR!**")
        st.write("Gaya hidup Anda sangat ramah lingkungan. Pertahankan!")
    elif 150 <= total_emisi < 350:
        st.info("🌿 **Level: PLANET FRIEND**")
        st.write("Cukup baik, namun masih ada ruang untuk penghematan energi.")
    else:
        st.error("⚠️ **Level: CARBON GIANT**")
        st.write("Jejak karbon Anda di atas rata-rata. Yuk, mulai kurangi sedikit demi sedikit!")

with col_score:
    st.metric("Total Emisi", f"{total_emisi:.1f} kgCO2e")

st.markdown("---")

# --- 2. DASHBOARD VISUALISASI ---
col_chart1, col_chart2 = st.columns(2)

# Chart 1: Breakdown Sumber Emisi
with col_chart1:
    st.subheader("📊 Sumber Emisi Anda")
    data_source = {
        'Kategori': ['Listrik', 'LPG', 'Motor', 'Mobil', 'Sampah'],
        'Emisi': [e_listrik, e_lpg, e_motor, e_mobil, e_sampah]
    }
    df_source = pd.DataFrame(data_source)
    
    fig_pie = px.pie(
        df_source, 
        values='Emisi', 
        names='Kategori',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Tealgrn_r
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

# Chart 2: Benchmarking (Pembanding)
with col_chart2:
    st.subheader("🆚 Perbandingan (Benchmark)")
    # Data Referensi:
    # Global Target 2030: ~2 ton/tahun -> ~167 kg/bulan (Paris Agreement compatible)
    # Rata-rata Indonesia: ~2.3 ton/tahun -> ~191 kg/bulan (World Bank Data)
    
    target_global = 167
    rata_indo = 191
    
    data_bench = {
        "Entitas": ["Target Global", "Rata-rata Indonesia", "Anda"],
        "Emisi (kg)": [target_global, rata_indo, total_emisi],
        "Color": ["Target", "Indo", "User"]
    }
    df_bench = pd.DataFrame(data_bench)
    
    fig_bar = px.bar(
        df_bench, 
        x="Entitas", 
        y="Emisi (kg)", 
        color="Entitas",
        color_discrete_map={
            "Target Global": "#2ecc71",       # Hijau
            "Rata-rata Indonesia": "#95a5a6", # Abu-abu
            "Anda": "#e74c3c" if total_emisi > rata_indo else "#3498db" # Merah jika tinggi, Biru jika rendah
        },
        text_auto='.0f'
    )
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

# --- 3. EKUIVALENSI (Kontekstualisasi) ---
st.subheader("💡 Konteks Nyata")
st.write("Angka emisi Anda bulan ini setara dengan:")

col_k1, col_k2, col_k3, col_k4 = st.columns(4)

km_mobil = total_emisi / 0.2  # Asumsi 1km mobil = 0.2 kgCO2
pohon_butuh = (total_emisi * 12) / 20 # 1 Pohon serap 20kg/thn
charge_hp = total_emisi / 0.008 # EPA estimate
es_mencair = total_emisi * 0.03 # 1kg CO2 mencairkan ~0.03 m2 es kutub (Scientific est)

with col_k1:
    st.info(f"🚗 **{int(km_mobil):,} km**\n\nPerjalanan Mobil")
with col_k2:
    st.success(f"🌲 **{int(pohon_butuh)} pohon**\n\nHarus ditanam/thn")
with col_k3:
    st.warning(f"📱 **{int(charge_hp):,} kali**\n\nCharge Smartphone")
with col_k4:
    st.error(f"🧊 **{es_mencair:.2f} m²**\n\nEs Kutub Mencair")

st.markdown("---")

# --- 4. SIMULASI WHAT-IF & TEBUS DOSA ---
col_sim, col_offset = st.columns([2, 1])

with col_sim:
    st.subheader("🧪 Simulasi Penghematan")
    st.write("Apa yang terjadi jika Anda melakukan perubahan kecil?")
    
    # Checkbox Simulasi
    sim_listrik = st.checkbox("💡 Hemat Listrik 20% (Matikan AC/Lampu)")
    sim_transport = st.checkbox("🚌 Kurangi Mobil/Motor 30% (Naik angkutan umum)")
    sim_sampah = st.checkbox("♻️ Pilah Sampah (Kurangi sampah ke TPA 50%)")
    
    potensi_turun = 0
    if sim_listrik: potensi_turun += e_listrik * 0.20
    if sim_transport: potensi_turun += (e_motor + e_mobil) * 0.30
    if sim_sampah: potensi_turun += e_sampah * 0.50
    
    emisi_baru = total_emisi - potensi_turun
    
    if potensi_turun > 0:
        st.metric(
            label="Estimasi Emisi Baru",
            value=f"{emisi_baru:.1f} kgCO2e",
            delta=f"-{potensi_turun:.1f} kg (Hemat!)"
        )
    else:
        st.caption("👈 Centang opsi di atas untuk melihat simulasi.")

with col_offset:
    st.subheader("💸 Biaya Tebus Dosa")
    st.write("Biaya *Carbon Offset* untuk menebus emisi tahunan Anda:")
    
    # Asumsi harga tanam pohon: Rp 25.000/pohon
    biaya_pohon = pohon_butuh * 25000 
    
    st.info(f"💰 **Rp {int(biaya_pohon):,}** / tahun")
    st.caption("*Asumsi donasi penanaman pohon Rp 25.000/batang.")
    st.button("🌱 Donasi Sekarang (Demo)")

# --- 5. FOOTER & REFERENSI ---
st.markdown("---")
with st.expander("📚 Lihat Detail Referensi & Faktor Emisi"):
    st.write("Berikut adalah angka yang digunakan dalam perhitungan:")
    for key, val in FAKTOR_EMISI.items():
        st.markdown(f"- **{key}:** {val['nilai']} {val['satuan']} ({val['sumber']})")
    st.caption("Aplikasi dikembangkan dengan Streamlit. Data berdasarkan pendekatan Tier-1 IPCC & ESDM.")