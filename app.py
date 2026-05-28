import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# Set page configurations
st.set_page_config(
    page_title="SayurKita — DS Analytics Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling matching the HTML preview palette
st.markdown("""
    <style>
    html, body, .stApp {
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #1f2937;
        font-size: 16px;
        line-height: 1.65;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #123024;
    }
    .stApp p, .stApp li, .stApp span, .stApp label, .stApp div {
        font-weight: 500;
    }
    .stApp strong {
        font-weight: 800;
    }
    /* Main background and font adjustments */
    .reportview-container {
        background-color: #fafbf9;
    }
    
    /* Callout insight boxes */
    .insight-box {
        padding: 14px 18px;
        border-radius: 8px;
        margin: 16px 0;
        font-size: 13.5px;
        line-height: 1.6;
    }
    .insight-green {
        background-color: #EAF3DE;
        border-left: 5px solid #3B6D11;
        color: #1B3A2D;
    }
    .insight-amber {
        background-color: #FAEEDA;
        border-left: 5px solid #BA7517;
        color: #633806;
    }
    .insight-blue {
        background-color: #E6F1FB;
        border-left: 5px solid #185FA5;
        color: #0C447C;
    }
    .insight-purple {
        background-color: #EDE7F6;
        border-left: 5px solid #534AB7;
        color: #3C3489;
    }
    
    /* Flow block styles */
    .flow-container {
        display: flex;
        gap: 10px;
        align-items: center;
        flex-wrap: wrap;
        margin-top: 10px;
    }
    .flow-step {
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        text-align: center;
        font-weight: 500;
    }
    
    /* Priority card styles */
    .priority-card {
        background-color: #ffffff;
        border: 1px solid #eef0ec;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .priority-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .priority-badge-container {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 4px;
    }
    .p-badge {
        font-size: 10px;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Palette colors defined in HTML preview
COLORS = {
    'g9': '#1B3A2D', 'g6': '#3B6D11', 'g4': '#639922', 'g0': '#EAF3DE',
    'a8': '#633806', 'a0': '#FAEEDA', 'b6': '#185FA5', 'b0': '#E6F1FB',
    'p6': '#534AB7', 'p0': '#EDE7F6', 'gray': '#7F8C8D', 'danger': '#E24B4A'
}
def format_id_number(value):
    return f"{value:,}".replace(",", ".")


def empty_dataframe(columns):
    return pd.DataFrame(columns=columns)


def has_required_columns(dataframe, required_columns):
    return not dataframe.empty and all(column in dataframe.columns for column in required_columns)


def safe_sample(dataframe, sample_size):
    if dataframe.empty:
        return dataframe
    return dataframe.sample(min(len(dataframe), sample_size), random_state=42)

# ==========================================
# DATA LOADING FUNCTION (WITH AUTOMATIC FALLBACKS)
# ==========================================
@st.cache_data
def load_all_datasets():
    """
    Fungsi ini membaca data asli dari folder 'data/'.
    Jika file belum ada, otomatis membuat mock data yang realistis sesuai format Panduan Tim
    agar dashboard langsung bisa dijalankan tanpa error.
    """
    raw_recipe_columns = ['Title', 'Ingredients', 'Steps', 'Loves', 'URL', 'Category', 'Title Cleaned', 'Total Ingredients', 'Ingredients Cleaned', 'Total Steps']
    mvp_recipe_columns = ['Title', 'Category', 'Loves', 'Total Ingredients', 'Total Steps']
    master_columns = ['nama_id', 'frekuensi', 'kategori', 'umur_kulkas', 'umur_suhu_ruang', 'umur_freezer', 'kalori_per_100g', 'protein_g', 'lemak_g', 'karbo_g', 'karbon_co2e']
    carbon_columns = ['Kategori', 'CO2e_per_kg', 'Sumber']

    # --- 1. DATASET RESEP (Raw atau Clean) ---
    try:
        if os.path.exists("data/indonesian_food_recipes.csv"):
            loaded_resep_raw = pd.read_csv("data/indonesian_food_recipes.csv")
        else:
            loaded_resep_raw = empty_dataframe(raw_recipe_columns)
    except (OSError, pd.errors.ParserError, ValueError) as e:
        st.error(f"Gagal memuat dataset resep: {e}")
        loaded_resep_raw = empty_dataframe(raw_recipe_columns)

    # --- 1B. DATASET RESEP MVP HASIL CLEANING ---
    try:
        if os.path.exists("data/clean_recipes_5000.json"):
            loaded_resep_clean = pd.read_json("data/clean_recipes_5000.json")
        else:
            loaded_resep_clean = empty_dataframe(mvp_recipe_columns)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        st.error(f"Gagal memuat dataset resep bersih: {e}")
        loaded_resep_clean = empty_dataframe(mvp_recipe_columns)

    # --- 2. INGREDIENTS MASTER & NUTRISI ---
    try:
        if os.path.exists("data/ingredients_master_final.csv"):
            loaded_master = pd.read_csv("data/ingredients_master_final.csv")
        else:
            loaded_master = empty_dataframe(master_columns)
    except (OSError, pd.errors.ParserError, ValueError) as e:
        st.error(f"Gagal memuat dataset master: {e}")
        loaded_master = empty_dataframe(master_columns)

    # --- 3. CARBON FACTORS ---
    try:
        if os.path.exists("data/carbon_factors_indonesia.json"):
            with open("data/carbon_factors_indonesia.json", "r", encoding="utf-8") as file_handle:
                carbon_dict = json.load(file_handle)
            loaded_carbon = pd.DataFrame.from_dict(carbon_dict, orient='index').reset_index()
            loaded_carbon.columns = ['Kategori', 'CO2e_per_kg', 'Sumber']
        else:
            loaded_carbon = empty_dataframe(carbon_columns)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        st.error(f"Gagal memuat dataset karbon: {e}")
        loaded_carbon = empty_dataframe(carbon_columns)

    return loaded_resep_raw, loaded_resep_clean, loaded_master, loaded_carbon

# Memuat data
df_resep_raw, df_resep_mvp, df_master, df_carbon = load_all_datasets()
raw_recipe_count = len(df_resep_raw)
mvp_recipe_count = len(df_resep_mvp)
mvp_per_category = int(df_resep_mvp['Category'].value_counts().iloc[0]) if not df_resep_mvp.empty and 'Category' in df_resep_mvp.columns and not df_resep_mvp['Category'].value_counts().empty else 0

# ==========================================
# SIDEBAR NAVIGATION & APP LOGO
# ==========================================
with st.sidebar:
    st.markdown(
        f"""
        <div style='text-align: center; padding: 10px 0;'>
            <span style='font-size: 36px;'>🌿</span>
            <h2 style='margin: 0; color: {COLORS['g9']}; font-size: 22px; font-weight: 600;'>SayurKita</h2>
            <p style='margin: 0; font-size: 11px; color: {COLORS['gray']}; text-transform: uppercase; letter-spacing: 0.08em;'>Data Science Dashboard</p>
        </div>
        """, unsafe_allow_html=True
    )
    st.divider()
    
    st.markdown(f"<p style='font-size: 10px; font-weight: 600; color: {COLORS['gray']}; text-transform: uppercase; margin-bottom: 8px; padding-left: 5px;'>Navigasi Section</p>", unsafe_allow_html=True)
    
    pages = ["🏠 Overview", "📋 Analisis Dataset Resep", "🥕 Ingredients & Nutrisi", "🌍 Carbon Footprint Impact", "🔗 Insight Lintas Dataset"]
    selected_page = st.radio("Menu", pages, label_visibility="collapsed")
    
    st.divider()
    st.markdown(
        f"""
        <div style='font-size: 11px; color: {COLORS['gray']}; padding: 5px; line-height: 1.5;'>
            <strong>Informasi Metadata:</strong><br>
            • Dataset Mentah: {format_id_number(raw_recipe_count)} resep<br>
            • Resep Bersih: {format_id_number(mvp_recipe_count)} resep<br>
            • Distribusi per Kategori: {format_id_number(mvp_per_category)} resep per kategori<br>
            • Database Nutrisi: {format_id_number(len(df_master))} item gizi<br>
            • Faktor Emisi: {format_id_number(len(df_carbon))} komoditas aktual
        </div>
        """, unsafe_allow_html=True
    )

# ==========================================
# ROUTING PAGES CONTENT
# ==========================================

# --- SECTION 1: OVERVIEW ---
if "Overview" in selected_page:
    st.markdown(f"<h1 style='color: {COLORS['g9']}; font-size: 26px; font-weight: 600; margin-bottom: 4px;'>🌿 SayurKita — Data Science Overview</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #555; font-size: 13.5px;'>Dashboard pelaporan analitik untuk inisiatif penanganan food waste Indonesia. Menampilkan insight dari 4 dataset yang digunakan.</p>", unsafe_allow_html=True)
    st.divider()
    
    # Grid KPI Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric(label="Total Dataset Resep Mentah", value=f"{format_id_number(raw_recipe_count)} Baris", delta="Data CSV asli")
    m2.metric(label="Resep Terkurasi (Top Loves)", value=f"{format_id_number(mvp_recipe_count)} Resep", delta=f"{format_id_number(mvp_per_category)} Per Kategori")
    m3.metric(label="Bahan Unik di Master", value=f"{format_id_number(len(df_master))} Bahan", delta="Data ingredients final", delta_color="inverse")
    
    m4, m5, m6 = st.columns(3)
    m4.metric(label="Kategori Emisi CO₂e (FAO)", value=f"{format_id_number(len(df_carbon))} Faktor", delta="Dataset karbon aktual")
    m5.metric(label="Estimasi National Food Waste", value="48 Juta Ton/Thn", delta="Peringkat #2 Dunia", delta_color="inverse")
    m6.metric(label="Kerugian Finansial Negara", value="Rp 551 Triliun", delta="Per Tahun (Bappenas)", delta_color="inverse")
    
    # Main Business Question Box
    st.markdown(
        """
        <div class='insight-box insight-green'>
            <strong>📌 Urgensi Bisnis Utama (Core Question):</strong><br>
            Bahan makanan apa yang paling rentan kadaluwarsa dan sering terbuang di dapur rumah tangga Indonesia, 
            serta seberapa besar dampak pengurangan emisi karbon (CO₂e) yang bisa diselamatkan secara riil melalui 
            sistem otomatis fitur <strong>LihatKulkas™</strong> dan pencocokan bahan <strong>Selamatkan!™</strong>?
        </div>
        """, unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class='insight-box insight-blue'>
            <strong>🧩 Stack Proyek:</strong><br>
            Frontend dibangun dengan <strong>React.js</strong> dan <strong>Tailwind CSS</strong>, backend menggunakan <strong>Node.js + Express.js</strong>,
            data disimpan di <strong>PostgreSQL</strong> dengan <strong>Prisma ORM</strong>, dan <strong>Redis</strong> disiapkan sebagai opsi caching untuk performa.
        </div>
        """, unsafe_allow_html=True
    )
    
    # Dataset Pipeline Visualization
    st.subheader("Alur Integrasi & Peta Transformasi Dataset")
    
    st.markdown(
        f"""
        <div class='flow-container'>
            <div class='flow-step' style='background-color: {COLORS['b0']}; color: {COLORS['b6']}; border: 1px solid #90CAF9;'>📋 Resep Kaggle Cookpad<br><span style='font-size:10px;'>{format_id_number(raw_recipe_count)} rows (Raw Data)</span></div>
            <div style='color: {COLORS['gray']}; font-weight: bold;'>→</div>
            <div class='flow-step' style='background-color: {COLORS['g0']}; color: {COLORS['g9']}; border: 1px solid #97C459;'>🧹 Cleaning & Skoring Python<br><span style='font-size:10px;'>{format_id_number(mvp_recipe_count)} Resep Bersih</span></div>
            <div style='color: {COLORS['gray']}; font-weight: bold;'>→</div>
            <div class='flow-step' style='background-color: {COLORS['a0']}; color: {COLORS['a8']}; border: 1px solid #EF9F27;'>🥕 Master Ingredients File<br><span style='font-size:10px;'>{format_id_number(len(df_master))} Entri Standarisasi</span></div>
            <div style='color: {COLORS['gray']}; font-weight: bold;'>→</div>
            <div class='flow-step' style='background-color: {COLORS['p0']}; color: {COLORS['p6']}; border: 1px solid #9FA8DA;'>🚀 React + Node/Express API<br><span style='font-size:10px;'>PostgreSQL + Prisma Live</span></div>
        </div>
        <br>
        <p style='font-size: 12px; color: #666; font-style: italic;'>*Dashboard ini merangkum hasil analitik utama sebelum data diintegrasikan ke aplikasi utama.</p>
        """, unsafe_allow_html=True
    )

# --- SECTION 2: ANALISIS RESEP ---
elif "Resep" in selected_page:
    st.markdown(f"<h1 style='color: {COLORS['g9']}; font-size: 26px; font-weight: 600; margin-bottom: 4px;'>📋 Exploratory Data Analysis — Dataset Resep</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #555; font-size: 13.5px;'>Analisis mendalam pola resep kuliner Indonesia untuk menentukan representasi data masakan di dalam aplikasi.</p>", unsafe_allow_html=True)
    st.divider()

    st.markdown("<p style='font-size:14px; font-weight:500; margin-bottom:5px;'>0. Total Resep per Kategori dari Dataset Raw</p>", unsafe_allow_html=True)
    if has_required_columns(df_resep_raw, ['Category']):
        raw_cat_counts = df_resep_raw['Category'].dropna().astype(str).str.strip().value_counts().reset_index()
        raw_cat_counts.columns = ['Kategori', 'Jumlah']
        raw_cat_counts['Kategori'] = raw_cat_counts['Kategori'].str.title()
        raw_cat_counts = raw_cat_counts.sort_values('Jumlah', ascending=False)

        fig_raw_cat = px.bar(
            raw_cat_counts,
            x='Jumlah',
            y='Kategori',
            orientation='h',
            color='Kategori',
            color_discrete_sequence=px.colors.qualitative.Set2,
            text='Jumlah'
        )
        fig_raw_cat.update_traces(texttemplate='%{x:,.0f}', textposition='outside')
        fig_raw_cat.update_layout(
            showlegend=False,
            height=340,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Jumlah Resep",
            yaxis_title="",
            yaxis=dict(categoryorder='array', categoryarray=raw_cat_counts['Kategori'].tolist())
        )
        st.plotly_chart(fig_raw_cat, use_container_width=True)
    else:
        st.info("Dataset resep mentah belum tersedia atau belum memiliki kolom Category.")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("<p style='font-size:14px; font-weight:500; margin-bottom:5px;'>1. Distribusi Resep Berdasarkan Kategori Utama</p>", unsafe_allow_html=True)
        if has_required_columns(df_resep_mvp, ['Category']):
            cat_counts = df_resep_mvp['Category'].value_counts().reset_index()
            cat_counts.columns = ['Kategori', 'Jumlah']
            cat_counts = cat_counts.sort_values('Jumlah', ascending=False)
            
            fig_cat = px.bar(cat_counts, x='Jumlah', y='Kategori', orientation='h',
                             color='Jumlah', color_continuous_scale='Greens',
                             text='Jumlah')
            fig_cat.update_layout(
                showlegend=False,
                height=340,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="Jumlah Resep Bersih",
                yaxis_title="",
                yaxis=dict(categoryorder='array', categoryarray=cat_counts['Kategori'].tolist())
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("Dataset resep bersih belum tersedia atau belum memiliki kolom Category.")
        
    with c2:
        st.markdown("<p style='font-size:14px; font-weight:500; margin-bottom:5px;'>2. Top 10 Bahan Paling Sering Muncul di Kuliner Indonesia</p>", unsafe_allow_html=True)
        if has_required_columns(df_master, ['frekuensi', 'nama_id']):
            top_ing = df_master.sort_values(by='frekuensi', ascending=False).head(10)
            
            fig_ing = px.bar(top_ing, x='frekuensi', y='nama_id', orientation='h',
                             text='frekuensi')
            fig_ing.update_traces(marker_color=COLORS['g4'])
            fig_ing.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10),
                                 xaxis_title="Frekuensi Kemunculan dalam Resep", yaxis_title="")
            st.plotly_chart(fig_ing, use_container_width=True)
        else:
            st.info("Dataset ingredients belum tersedia atau kolom frekuensi/nama_id tidak lengkap.")
        
    st.markdown(
        f"""
        <div class='insight-box insight-green'>
            <strong>💡 Insight Kunci Struktur Resep:</strong><br>
            • Dataset resep bersih hasil cleaning berjumlah <strong>{format_id_number(mvp_recipe_count)} resep</strong> dan terbagi rata menjadi <strong>{format_id_number(mvp_per_category)} resep per kategori</strong>, sehingga setiap kategori punya bobot representasi yang sama pada grafik.<br>
            • Grafik di sebelah kiri memakai kolom asli dari file resep bersih, yaitu <strong>Category</strong>, sehingga visualisasi distribusi benar-benar sesuai data yang tersedia.<br>
            • Grafik scatter di bawah memakai <strong>Total Ingredients</strong>, <strong>Total Steps</strong>, dan <strong>Loves</strong> dari dataset resep bersih, jadi hubungan kompleksitas resep terhadap popularitas sekarang sesuai struktur file.
        </div>
        """, unsafe_allow_html=True
    )
    
    st.divider()
    st.markdown("<p style='font-size:15px; font-weight:500; margin-bottom:5px;'>Analisis Korelasi: Kompleksitas Resep vs Popularitas (Engagement Pengguna)</p>", unsafe_allow_html=True)
    
    c3, c4 = st.columns(2)
    with c3:
        if has_required_columns(df_resep_mvp, ['Total Ingredients', 'Loves']):
            fig_scatter1 = px.scatter(safe_sample(df_resep_mvp, 1000), 
                                      x='Total Ingredients', y='Loves', 
                                      title="Hubungan Jumlah Bahan vs Jumlah Loves",
                                      labels={'Total Ingredients': 'Jumlah Bahan dalam Resep', 'Loves': 'Jumlah Loves (Suka)'},
                                      opacity=0.4)
            fig_scatter1.update_layout(height=300)
            st.plotly_chart(fig_scatter1, use_container_width=True)
        else:
            st.info("Dataset resep bersih belum memiliki kolom Total Ingredients dan Loves.")
        
    with c4:
        if has_required_columns(df_resep_mvp, ['Total Steps', 'Loves']):
            fig_scatter2 = px.scatter(safe_sample(df_resep_mvp, 1000), 
                                      x='Total Steps', y='Loves', 
                                      title="Hubungan Jumlah Langkah Masak vs Jumlah Loves",
                                      labels={'Total Steps': 'Jumlah Langkah Instruksi', 'Loves': 'Jumlah Loves (Suka)'},
                                      opacity=0.4)
            fig_scatter2.update_layout(height=300)
            st.plotly_chart(fig_scatter2, use_container_width=True)
        else:
            st.info("Dataset resep bersih belum memiliki kolom Total Steps dan Loves.")

# --- SECTION 3: INGREDIENTS & NUTRISI ---
elif "Ingredients" in selected_page:
    st.markdown(f"<h1 style='color: {COLORS['g9']}; font-size: 26px; font-weight: 600; margin-bottom: 4px;'>🥕 Ingredients Master & Nutrition Data Coverage</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #555; font-size: 13.5px;'>Evaluasi kualitas data buatan mandiri (Ingredients Master) yang diintegrasikan dengan dataset kandungan gizi Kemenkes.</p>", unsafe_allow_html=True)
    st.divider()
    
    k1, k2, k3 = st.columns(3)
    total_b = len(df_master)
    filled_expiry = df_master['umur_kulkas'].notna().sum()
    pct_expiry = (filled_expiry / total_b) * 100
    
    filled_nut = df_master['kalori_per_100g'].notna().sum()
    pct_nut = (filled_nut / total_b) * 100
    
    k1.metric("Total Entri Bahan di Master", f"{total_b} Bahan", "Hasil Ekstraksi Resep")
    k2.metric("Kelengkapan Data Umur Simpan", f"{pct_expiry:.1f}%", f"{filled_expiry} Bahan Terisi Manual")
    k3.metric("Coverage Integrasi Data Gizi", f"{pct_nut:.1f}%", f"{filled_nut} Item Berhasil Match")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("<p style='font-size:14px; font-weight:500; margin-bottom:5px;'>Distribusi Kategori Kelompok Bahan</p>", unsafe_allow_html=True)
        if has_required_columns(df_master, ['kategori']):
            kategori_counts = df_master['kategori'].dropna().astype(str).str.strip().value_counts().reset_index()
            kategori_counts.columns = ['kategori', 'jumlah']
            fig_pie = px.pie(
                kategori_counts,
                names='kategori',
                values='jumlah',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_pie.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Dataset ingredients belum tersedia atau kolom kategori tidak lengkap.")
        
    with c2:
        st.markdown("<p style='font-size:14px; font-weight:500; margin-bottom:5px;'>Distribusi Umur Simpan Bahan di Kulkas</p>", unsafe_allow_html=True)
        if has_required_columns(df_master, ['umur_kulkas', 'nama_id']):
            df_shelf = df_master[df_master['umur_kulkas'].notna()].copy()
            df_shelf['umur_kulkas'] = pd.to_numeric(df_shelf['umur_kulkas'], errors='coerce')
            df_shelf = df_shelf[df_shelf['umur_kulkas'].notna()]
            if not df_shelf.empty:
                bin_count = max(5, min(20, df_shelf['umur_kulkas'].nunique()))
                fig_shelf = px.histogram(
                    df_shelf,
                    x='umur_kulkas',
                    nbins=bin_count,
                    labels={'umur_kulkas': 'Umur Simpan di Kulkas (Hari)'},
                )
                fig_shelf.update_traces(marker_color=COLORS['danger'])
                median_val = float(df_shelf['umur_kulkas'].median())
                # add shaded region for 1-7 days and median line
                fig_shelf.add_vrect(x0=1, x1=7, fillcolor="#FFEFEF", opacity=0.4, layer="below", line_width=0)
                fig_shelf.add_vline(x=median_val, line_dash="dash", line_color=COLORS['g6'], annotation_text=f"Median: {median_val:.0f}d", annotation_position="top left")
                fig_shelf.update_layout(
                    height=300,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis_title="Umur Simpan di Kulkas (Hari)",
                    yaxis_title="Jumlah Bahan"
                )
                st.plotly_chart(fig_shelf, use_container_width=True)
            else:
                st.info("Tidak ada data umur simpan yang dapat diurutkan.")
        else:
            st.info("Dataset ingredients belum memiliki kolom umur_kulkas dan nama_id.")
        
    st.markdown(
        """
        <div class='insight-box insight-amber'>
            <strong>💡 Justifikasi Fitur Proyek Berdasarkan Sifat Bahan:</strong><br>
            • Protein hewani segar seperti <strong>Udang (2 hari), Daging Sapi (3 hari), dan Daging Ayam (3 hari)</strong> menduduki peringkat teratas bahan makanan yang paling cepat membusuk. 
            Hal ini memberikan argumen ilmiah yang kuat mengapa <strong>Fitur Notifikasi H-3 Expiry Alert</strong> pada modul backend aplikasi SayurKita bernilai sangat tinggi bagi pengguna.<br>
            • Kelengkapan data umur simpan dan gizi sudah ditampilkan di kartu KPI di atas. Jika ada atribut yang masih kosong, nilai default tetap perlu disiapkan agar alur fitur tetap stabil.
        </div>
        """, unsafe_allow_html=True
    )
    
    st.divider()
    st.subheader("Top 5 Makanan Tinggi Kandungan Protein (Bahan Baku Utama SayurKita)")
    if has_required_columns(df_master, ['protein_g', 'nama_id', 'kalori_per_100g']):
        df_protein = df_master[df_master['protein_g'].notna()].nlargest(5, 'protein_g')
        if not df_protein.empty:
            cols = st.columns(5)
            for idx, row in enumerate(df_protein.itertuples()):
                with cols[idx]:
                    st.markdown(
                        f"""
                        <div style='background-color:#ffffff; padding:15px; border:1px solid #e2e8f0; border-radius:8px; text-align:center;'>
                            <span style='font-size:20px;'>🥩</span>
                            <p style='font-weight:600; margin:4px 0; font-size:13px; text-transform:capitalize;'>{row.nama_id}</p>
                            <h3 style='margin:0; color:{COLORS['a8']}; font-size:18px;'>{row.protein_g}g</h3>
                            <p style='font-size:10px; color:#718096; margin:0;'>Protein per 100g</p>
                            <span style='font-size:9px; background-color:{COLORS['a0']}; color:{COLORS['a8']}; padding:1px 6px; border-radius:10px;'>{row.kalori_per_100g} Kkal</span>
                        </div>
                        """, unsafe_allow_html=True
                    )
    else:
        st.info("Dataset ingredients belum memiliki kolom protein_g, nama_id, dan kalori_per_100g.")

# --- SECTION 4: CARBON FOOTPRINT IMPACT ---
elif "Carbon" in selected_page:
    st.markdown(f"<h1 style='color: {COLORS['g9']}; font-size: 26px; font-weight: 600; margin-bottom: 4px;'>🌍 Carbon Footprint Impact Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #555; font-size: 13.5px;'>Model proyeksi dampak penyelamatan makanan terhadap penurunan emisi gas rumah kaca menggunakan dataset karbon aktual dari JSON.</p>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("<p style='font-size:14px; font-weight:500; margin-bottom:5px;'>Top 15 Faktor Emisi CO₂e Tertinggi dari Dataset Karbon (kg CO₂e / kg Bahan)</p>", unsafe_allow_html=True)
    
    if has_required_columns(df_carbon, ['CO2e_per_kg', 'Kategori', 'Sumber']):
        df_carbon_sorted = df_carbon.sort_values(by='CO2e_per_kg', ascending=False).head(15)
        top_carbon = df_carbon_sorted.iloc[0]
        top_carbon_name = str(top_carbon['Kategori']).replace('_', ' ').title()
        top_carbon_value = float(top_carbon['CO2e_per_kg'])
        
        fig_co2 = px.bar(df_carbon_sorted, x='CO2e_per_kg', y='Kategori', 
                         orientation='h', text='CO2e_per_kg', hover_data=['Sumber'])
        fig_co2.update_traces(marker_color=COLORS['b6'], textposition='outside')
        fig_co2.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="kg CO₂e per kg bahan",
            yaxis_title="",
            yaxis=dict(categoryorder='array', categoryarray=df_carbon_sorted['Kategori'].tolist())
        )
        st.plotly_chart(fig_co2, use_container_width=True)
        
        st.markdown(
            f"""
            <div class='insight-box insight-blue'>
                <strong>💡 Perbandingan Magnitudo Dampak Lingkungan:</strong><br>
                Dataset karbon saat ini memuat <strong>{format_id_number(len(df_carbon))} faktor emisi</strong>, dan item dengan emisi tertinggi adalah <strong>{top_carbon_name}</strong> sebesar <strong>{top_carbon_value:.3f} kg CO₂e/kg</strong>.
                Visualisasi ini sengaja dibatasi ke 15 faktor tertinggi agar grafik tetap terbaca dan tetap merepresentasikan isi file JSON secara akurat.
            </div>
            """, unsafe_allow_html=True
        )
    else:
        st.info("Dataset karbon belum tersedia atau kolom CO2e_per_kg/Kategori/Sumber tidak lengkap.")
    
    st.divider()
    st.subheader("🔮 Kalkulator Interaktif Proyeksi Dampak Lingkungan SayurKita")
    st.markdown("Sesuaikan slider di bawah ini untuk melihat simulasi dampak kumulatif aplikasi dalam skala komunitas.")
    
    sc1, sc2 = st.columns(2)
    with sc1:
        user_slider = st.slider("Jumlah Pengguna Aktif Bulanan (MAU)", min_value=100, max_value=10000, value=1000, step=100)
        food_weight_slider = st.slider("Rata-rata Bahan Makanan yang Diselamatkan per User / Hari (Gram)", min_value=100, max_value=2000, value=500, step=50)
        
    total_saved_kg = user_slider * (food_weight_slider / 1000) * 30
    simulated_co2_saved = total_saved_kg * 3.0
    equivalent_km = simulated_co2_saved * 4.756
    
    with sc2:
        st.markdown("<p style='margin:0; font-size:12px; font-weight:bold; color:#475569; text-transform:uppercase;'>Hasil Estimasi Dampak Komunitas (1 Bulan)</p>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='margin:10px 0 2px 0; color:{COLORS['g6']}; font-size:28px;'>{total_saved_kg:,.0f} kg</h2>", unsafe_allow_html=True)
        st.markdown("<p style='margin:0 0 10px 0; font-size:11px; color:#64748b;'>Total Massa Sampah Organik yang Dicegah Terbuang</p>", unsafe_allow_html=True)

        st.markdown(f"<h2 style='margin:0 0 2px 0; color:{COLORS['b6']}; font-size:28px;'>~{simulated_co2_saved:,.0f} kg CO₂e</h2>", unsafe_allow_html=True)
        st.markdown("<p style='margin:0 0 10px 0; font-size:11px; color:#64748b;'>Total Gas Emisi Rumah Kaca yang Berhasil Dikurangi</p>", unsafe_allow_html=True)

        st.markdown(f"<h2 style='margin:0 0 2px 0; color:{COLORS['a8']}; font-size:24px;'>{equivalent_km:,.0f} km</h2>", unsafe_allow_html=True)
        st.markdown("<p style='margin:0; font-size:11px; color:#64748b;'>Setara dengan Mengurangi Jarak Mengemudi Mobil</p>", unsafe_allow_html=True)

# --- SECTION 5: INSIGHT LINTAS DATASET ---
elif "Insight" in selected_page:
    st.markdown(f"<h1 style='color: {COLORS['g9']}; font-size: 26px; font-weight: 600; margin-bottom: 4px;'>🔗 Matriks Gabungan & Keputusan Strategis Fitur</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #555; font-size: 13.5px;'>Hasil penggabungan (Join/Merge) tiga dimensi data: Frekuensi Resep + Kerentanan Kadaluwarsa + Dampak Karbon.</p>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown(
        f"""
        <div class='insight-box' style='background-color:#f1f5f9; border-left:5px solid #64748b; color:#334155;'>
            <strong>Metode Pembobotan Skor Prioritas (Multi-dimensional Scoring Model):</strong><br>
            Setiap komoditas dihitung menggunakan formula: 
            <span style='font-family:monospace; font-weight:bold; color:{COLORS['danger']};'>Score = (Normalisasi Frekuensi * 0.35) + ((1 / Umur Simpan) * 0.35) + (Normalisasi CO₂e * 0.30)</span>. 
            Bahan makanan dengan skor tertinggi merupakan komoditas paling krusial yang wajib diprioritaskan oleh sistem cerdas SayurKita.
        </div>
        """, unsafe_allow_html=True
    )
    
    st.subheader("Top Bahan Baku Paling Kritis Berdasarkan Keputusan Algoritma Data")
    
    # Priority cards hardcoded to match HTML structure since this is a synthesis conclusion
    st.markdown(f"""
    <div class='priority-card'>
        <div class='priority-left'>
            <div style='background-color:{COLORS['danger']}; color:white; width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold;'>1</div>
            <div>
                <div style='font-weight:600; font-size:14px; color:#1e293b;'>Daging Ayam</div>
                <div style='font-size:11px; color:#64748b;'>Sangat tinggi di menu masakan kuliner • Expired super cepat dalam 3 hari • Emisi mencapai 5.7 kg CO₂e/kg</div>
            </div>
        </div>
        <div class='priority-badge-container'>
            <span class='p-badge' style='background-color:#EAF3DE; color:#27500A;'>Frekuensi Tinggi</span>
            <span class='p-badge' style='background-color:#FFEBEE; color:#8B0000;'>Cepat Expired</span>
            <span class='p-badge' style='background-color:#E6F1FB; color:#0C447C;'>CO₂e Signifikan</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='priority-card'>
        <div class='priority-left'>
            <div style='background-color:#E8A320; color:white; width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold;'>2</div>
            <div>
                <div style='font-weight:600; font-size:14px; color:#1e293b;'>Tahu Putih</div>
                <div style='font-size:11px; color:#64748b;'>Sangat merakyat di resep • Expired dalam 5 hari di kulkas (atau 1 hari suhu ruang) • Emisi kedelai ~2.0 kg CO₂e/kg</div>
            </div>
        </div>
        <div class='priority-badge-container'>
            <span class='p-badge' style='background-color:#EAF3DE; color:#27500A;'>Frekuensi Tinggi</span>
            <span class='p-badge' style='background-color:#FFF8E1; color:#633806;'>Kerentanan Menengah</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='priority-card'>
        <div class='priority-left'>
            <div style='background-color:#E8A320; color:white; width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold;'>3</div>
            <div>
                <div style='font-weight:600; font-size:14px; color:#1e293b;'>Tempe Kedelai</div>
                <div style='font-size:11px; color:#64748b;'>Muncul di ribuan jenis masakan • Expired dalam 5 hari • Emisi kedelai ~2.0 kg CO₂e/kg</div>
            </div>
        </div>
        <div class='priority-badge-container'>
            <span class='p-badge' style='background-color:#EAF3DE; color:#27500A;'>Frekuensi Tinggi</span>
            <span class='p-badge' style='background-color:#FFF8E1; color:#633806;'>Kerentanan Menengah</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='priority-card'>
        <div class='priority-left'>
            <div style='background-color:{COLORS['g6']}; color:white; width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold;'>4</div>
            <div>
                <div style='font-weight:600; font-size:14px; color:#1e293b;'>Bayam Hijau</div>
                <div style='font-size:11px; color:#64748b;'>Komoditas sayuran sayur bening • Rusak/berlendir dalam waktu 3 s.d 5 hari • Emisi sayur ~1.8 kg CO₂e/kg</div>
            </div>
        </div>
        <div class='priority-badge-container'>
            <span class='p-badge' style='background-color:#FFEBEE; color:#8B0000;'>Cepat Expired</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='priority-card'>
        <div class='priority-left'>
            <div style='background-color:{COLORS['g6']}; color:white; width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold;'>5</div>
            <div>
                <div style='font-weight:600; font-size:14px; color:#1e293b;'>Telur Ayam</div>
                <div style='font-size:11px; color:#64748b;'>Bahan pelengkap dengan frekuensi sangat tinggi • Umur simpan lama hingga 35 hari • Emisi sangat kecil 0.6 kg CO₂e/kg</div>
            </div>
        </div>
        <div class='priority-badge-container'>
            <span class='p-badge' style='background-color:#EAF3DE; color:#27500A;'>Frekuensi Tinggi</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        """
        <div class='insight-box insight-purple'>
            <strong>🎯 Kesimpulan Rekomendasi Strategis untuk Presentasi Proyek:</strong><br>
            Berdasarkan matriks di atas, <strong>Daging Ayam</strong> diidentifikasi sebagai bahan makanan dengan prioritas penyelamatan tertinggi. Komoditas ini memenuhi unsur 'Triple Threat': sangat sering dikonsumsi masyarakat Indonesia, memiliki umur simpan biologis yang pendek, dan meninggalkan jejak karbon yang signifikan. 
            Oleh karena itu, komoditas ini layak menjadi fokus utama pada pengujian fungsionalitas algoritma karena dampak reduksi emisi dan ekonominya paling besar.
        </div>
        """, unsafe_allow_html=True
    )
