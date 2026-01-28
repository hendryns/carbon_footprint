import streamlit as st
import pandas as pd
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Kalkulator Jejak Karbon Edukatif",
    page_icon="🌏",
    layout="wide"
)

# --- DATABASE FAKTOR EMISI & REFERENSI ---
# Disimpan dalam Dictionary agar mudah dipanggil deskripsinya
FAKTOR_EMISI = {
    "Listrik": {
        "nilai": 0.87, 
        "satuan": "kgCO2/kWh",
        "sumber": "Kementerian ESDM (Faktor Emisi Grid Jamali)",
        "desc": "Emisi dari pembakaran batubara/gas di pembangkit listrik untuk menghasilkan 1 kWh listrik."
    },
    "Bensin": {
        "nilai": 2.33, 
        "satuan": "kgCO2/Liter",
        "sumber": "IPCC Guidelines 2006 (Mobile Combustion)",
        "desc": "Emisi langsung dari pembakaran bensin (Pertalite/Pertamax) pada mesin kendaraan."
    },
    "Solar": {
        "nilai": 2.68, 
        "satuan": "kgCO2/Liter",
        "sumber": "IPCC Guidelines 2006",
        "desc": "Solar memiliki kandungan karbon lebih padat dibanding bensin, sehingga emisinya sedikit lebih tinggi per liter."
    },
    "LPG": {
        "nilai": 3.00, 
        "satuan": "kgCO2/kg",
        "sumber": "IPCC & Pertamina (Estimasi)",
        "desc": "Emisi dari pembakaran gas propana/butana untuk memasak."
    },
    "Sampah": {
        "nilai": 0.70, 
        "satuan": "kgCO2e/kg",
        "sumber": "World Bank & KLHK (Estimasi TPA Anaerobik)",
        "desc": "Sampah organik di TPA menghasilkan gas Metana (CH4) yang 28x lebih kuat menahan panas dibanding CO2."
    }
}

# --- HEADER ---
st.title("🌏 Kalkulator Jejak Karbon & Edukasi")
st.write("Hitung emisi Anda dan pahami dampaknya terhadap lingkungan dengan data yang valid.")
st.markdown("---")

# --- SIDEBAR INPUT ---
st.sidebar.header("📝 Masukkan Aktivitas Bulanan")

def user_input_features():
    # Listrik
    st.sidebar.subheader("1. Energi")
    listrik = st.sidebar.slider("Listrik (kWh)", 0, 1000, 150, 10)
    lpg = st.sidebar.slider("LPG (kg)", 0, 60, 12, 3)
    
    # Transport
    st.sidebar.subheader("2. Transportasi")
    motor = st.sidebar.slider("Bensin Motor (Liter)", 0, 100, 30, 1)
    mobil = st.sidebar.slider("BBM Mobil (Liter)", 0, 300, 0, 5)
    jenis_bbm = st.sidebar.radio("Jenis BBM Mobil", ["Bensin", "Solar"])
    
    # Limbah
    st.sidebar.subheader("3. Limbah")
    sampah = st.sidebar.slider("Sampah ke TPA (kg)", 0, 100, 20, 1)
    
    return listrik, lpg, motor, mobil, jenis_bbm, sampah

listrik, lpg, motor, mobil, jenis_bbm, sampah = user_input_features()

# --- PERHITUNGAN ---
e_listrik = listrik * FAKTOR_EMISI["Listrik"]["nilai"]
e_lpg = lpg * FAKTOR_EMISI["LPG"]["nilai"]
e_motor = motor * FAKTOR_EMISI["Bensin"]["nilai"]

if jenis_bbm == "Bensin":
    e_mobil = mobil * FAKTOR_EMISI["Bensin"]["nilai"]
else:
    e_mobil = mobil * FAKTOR_EMISI["Solar"]["nilai"]

e_sampah = sampah * FAKTOR_EMISI["Sampah"]["nilai"]

total_emisi = e_listrik + e_lpg + e_motor + e_mobil + e_sampah

# --- TAMPILAN DASHBOARD ---

# KOLOM 1: HASIL UTAMA & KOMPARASI
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Hasil Analisis")
    st.metric("Total Jejak Karbon Bulanan", f"{total_emisi:.2f} kgCO2e")
    
    # FITUR BARU: KOMPARASI / EKUIVALENSI
    st.markdown("##### 💡 Tahukah kamu? Angka di atas setara dengan:")
    
    # Rumus Konversi Sederhana (Estimasi EPA/Berbagai Sumber)
    km_mobil = total_emisi / 0.2  # Asumsi mobil rata-rata emisi 0.2 kg/km
    pohon_tahun = (total_emisi * 12) / 20 # 1 Pohon menyerap ~20kg/tahun
    charge_hp = total_emisi / 0.008 # Charge smartphone ~0.008 kgCO2
    ac_jam = total_emisi / 0.4 # AC 1PK ~0.4 kg/jam (tergantung efisiensi)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.info(f"🚗 **{int(km_mobil):,}**\n\nKm perjalanan mobil")
    with c2:
        st.success(f"🌲 **{int(pohon_tahun)}**\n\nPohon butuh ditanam/thn")
    with c3:
        st.warning(f"📱 **{int(charge_hp):,}**\n\nKali charge HP")
    with c4:
        st.error(f"❄️ **{int(ac_jam):,}**\n\nJam pemakaian AC")

    # Grafik Breakdown
    data = {
        'Sumber': ['Listrik', 'LPG', 'Motor', 'Mobil', 'Sampah'],
        'Emisi': [e_listrik, e_lpg, e_motor, e_mobil, e_sampah]
    }
    df = pd.DataFrame(data)
    
    fig = px.bar(df, x='Sumber', y='Emisi', color='Sumber', 
                 title="Kontribusi per Kategori", text_auto='.1f',
                 color_discrete_sequence=px.colors.qualitative.Prism)
    st.plotly_chart(fig, use_container_width=True)

# KOLOM 2: EDUKASI & REFERENSI
with col2:
    st.subheader("📚 Referensi & Validitas")
    st.write("Penjelasan indikator yang digunakan dalam aplikasi ini:")
    
    with st.expander("⚡ Faktor Emisi Listrik"):
        d = FAKTOR_EMISI["Listrik"]
        st.markdown(f"**Nilai:** {d['nilai']} {d['satuan']}")
        st.markdown(f"**Sumber:** {d['sumber']}")
        st.caption(d['desc'])
        
    with st.expander("⛽ Faktor Emisi BBM"):
        d1 = FAKTOR_EMISI["Bensin"]
        d2 = FAKTOR_EMISI["Solar"]
        st.markdown(f"**Bensin:** {d1['nilai']} {d1['satuan']}")
        st.markdown(f"**Solar:** {d2['nilai']} {d2['satuan']}")
        st.markdown(f"**Sumber:** {d1['sumber']}")
        st.caption("Berasal dari pembakaran sempurna karbon dalam bahan bakar.")

    with st.expander("🗑️ Faktor Emisi Sampah"):
        d = FAKTOR_EMISI["Sampah"]
        st.markdown(f"**Nilai:** {d['nilai']} {d['satuan']}")
        st.markdown(f"**Sumber:** {d['sumber']}")
        st.caption(d['desc'])
        
    st.info("""
    **Catatan:** Perhitungan ini menggunakan metode **Tier 1 (Estimasi)**. 
    Hasil aktual bisa berbeda tergantung efisiensi alat elektronik, jenis kendaraan, 
    dan pengelolaan sampah spesifik di daerah Anda.
    """)

# --- REKOMENDASI ---
st.markdown("---")
st.subheader("🌱 Langkah Selanjutnya")
col_rek1, col_rek2 = st.columns(2)

with col_rek1:
    st.markdown("**Jika ingin mengurangi Emisi Listrik:**")
    st.markdown("- Ganti lampu ke LED (Hemat ~50%)")
    st.markdown("- Bersihkan filter AC rutin (Hemat ~10%)")
    st.markdown("- Cabut colokan dispenser/TV saat malam.")

with col_rek2:
    st.markdown("**Jika ingin mengurangi Emisi Transportasi:**")
    st.markdown("- Cek tekanan ban (Ban kempes boros BBM ~5%)")
    st.markdown("- Gunakan KRL/MRT untuk jarak jauh.")
    st.markdown("- Lakukan servis berkala uji emisi.")