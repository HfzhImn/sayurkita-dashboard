import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
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
    
    pages = ["🏠 Overview", "📋 Analisis Dataset Resep", "🥕 Ingredients & Nutrisi", "🌍 Carbon Footprint Impact", "🔗 Insight Lintas Dataset", "🧪 Analisis Berdasarkan Notebook"]
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
    
    st.markdown("""
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

    st.markdown("""
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

# --- SECTION 6: ANALISIS BERDASARKAN NOTEBOOK ---
elif "Notebook" in selected_page:
    st.markdown(f"<h1 style='color: {COLORS['g9']}; font-size: 26px; font-weight: 600; margin-bottom: 4px;'>🧪 Section 6 — Analisis Berdasarkan Notebook</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #555; font-size: 13.5px;'>Seluruh blok di section ini mengikuti alur notebook: <strong>Pertanyaan Bisnis</strong> terlebih dahulu, lalu <strong>Visualisasi</strong>, dan ditutup <strong>Insight & Rekomendasi</strong>.</p>", unsafe_allow_html=True)
    st.divider()

    tab_a, tab_b = st.tabs([
        "Notebook A: Dataset Resep dan Karbon",
        "Notebook B: Dataset Ingredients Master dan Nutrisi"
    ])

    with tab_a:
        st.subheader("A. Analisis Dataset Resep Indonesia (Raw 14.945 resep)")
        df_recipe = df_resep_raw.copy()

        # A1
        st.markdown("### 📊 Pertanyaan Bisnis 1 (Resep)")
        st.markdown("**Kategori masakan apa yang paling banyak resepnya di Indonesia pada dataset raw indonesian_food_recipes, dan apakah distribusinya seimbang?**")
        if has_required_columns(df_recipe, ['Category']):
            kategori_counts = (
                df_recipe['Category']
                .dropna()
                .astype(str)
                .str.strip()
                .value_counts()
                .reset_index()
            )
            kategori_counts.columns = ['Kategori', 'Jumlah Resep']
            kategori_counts['Persentase (%)'] = (kategori_counts['Jumlah Resep'] / len(df_recipe) * 100).round(2)

            mean_cat = float(kategori_counts['Jumlah Resep'].mean())
            std_cat = float(kategori_counts['Jumlah Resep'].std(ddof=1)) if len(kategori_counts) > 1 else 0.0
            cov = (std_cat / mean_cat * 100) if mean_cat > 0 else 0.0

            v1, v2 = st.columns(2)
            with v1:
                fig_a1_bar = px.bar(
                    kategori_counts.sort_values('Jumlah Resep', ascending=True),
                    x='Jumlah Resep',
                    y='Kategori',
                    orientation='h',
                    text='Jumlah Resep',
                    color='Kategori',
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig_a1_bar.update_layout(showlegend=False, height=360, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_a1_bar, use_container_width=True)
            with v2:
                fig_a1_pie = px.pie(
                    kategori_counts,
                    names='Kategori',
                    values='Jumlah Resep',
                    hole=0.35,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_a1_pie.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_a1_pie, use_container_width=True)

            st.markdown(
                f"""
                <div class='insight-box insight-green'>
                    <strong>💡 Insight — Pertanyaan Bisnis 1</strong><br><br>
                    <strong>Temuan:</strong><br>
                        • Dataset raw resep berisi <strong>{format_id_number(len(df_recipe))} resep</strong> dengan kategori masakan Indonesia yang dominan pada protein hewani dan olahan.<br>
                    • Kategori <strong>Ikan</strong> mendominasi dengan jumlah resep terbanyak, diikuti oleh <strong>Telur</strong> dan <strong>Udang</strong>.<br>
                    • Coefficient of Variation sebesar <strong>{cov:.1f}%</strong>. Jika CoV &lt; 20%, distribusi antar kategori <strong>cukup seimbang</strong>.<br><br>
                    <strong>Implikasi untuk SayurKita:</strong><br>
                        • Strategi seleksi top resep per kategori dari dataset raw tetap valid dan representatif.<br>
                        • Rekomendasi berbasis konten tidak akan bias ke satu kategori karena jumlah data antarkategori proporsional.<br>
                        • Kategori tahu perlu perhatian saat seleksi agar tidak kurang representatif.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("Kolom Category pada dataset resep bersih belum tersedia untuk menjawab pertanyaan ini.")

        # A2
        st.markdown("### 📊 Pertanyaan Bisnis 2 (Resep)")
        st.markdown("**Berapa rata-rata jumlah bahan per resep pada dataset raw, dan apakah resep dengan bahan lebih sedikit cenderung lebih populer (loves lebih tinggi)?**")
        if has_required_columns(df_recipe, ['Total Ingredients', 'Loves']):
            df_a2 = df_recipe.copy()
            df_a2['Total Ingredients'] = pd.to_numeric(df_a2['Total Ingredients'], errors='coerce')
            df_a2['Loves'] = pd.to_numeric(df_a2['Loves'], errors='coerce')
            df_a2 = df_a2.dropna(subset=['Total Ingredients', 'Loves'])

            if not df_a2.empty:
                avg_bahan = float(df_a2['Total Ingredients'].mean())
                corr_bahan = float(df_a2['Total Ingredients'].corr(df_a2['Loves'])) if len(df_a2) > 1 else 0.0

                bins = [0, 7, 12, 18, np.inf]
                labels = ['Sangat Simpel (1-7)', 'Simpel (8-12)', 'Sedang (13-18)', 'Kompleks (>18)']
                df_a2['kelompok_bahan'] = pd.cut(df_a2['Total Ingredients'], bins=bins, labels=labels)
                group_stats = (
                    df_a2.groupby('kelompok_bahan', observed=True)['Loves']
                    .mean()
                    .reset_index(name='Rata-rata Loves')
                )

                v1, v2 = st.columns(2)
                with v1:
                    fig_a2_scatter = px.scatter(
                        safe_sample(df_a2, 2500),
                        x='Total Ingredients',
                        y='Loves',
                        opacity=0.35,
                        title='Korelasi Jumlah Bahan vs Loves'
                    )
                    x_vals = df_a2['Total Ingredients'].to_numpy()
                    y_vals = df_a2['Loves'].to_numpy()
                    if len(x_vals) > 1:
                        slope, intercept = np.polyfit(x_vals, y_vals, 1)
                        x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
                        fig_a2_scatter.add_scatter(
                            x=x_line,
                            y=slope * x_line + intercept,
                            mode='lines',
                            name='Tren',
                            line=dict(color=COLORS['danger'], width=2)
                        )
                    fig_a2_scatter.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10))
                    st.plotly_chart(fig_a2_scatter, use_container_width=True)
                with v2:
                    fig_a2_bar = px.bar(
                        group_stats,
                        x='kelompok_bahan',
                        y='Rata-rata Loves',
                        color='kelompok_bahan',
                        color_discrete_sequence=[COLORS['g4'], COLORS['g6'], COLORS['a8'], COLORS['danger']],
                        title='Rata-rata Loves per Kelompok Jumlah Bahan'
                    )
                    fig_a2_bar.update_layout(showlegend=False, height=360, margin=dict(l=10, r=10, t=30, b=10), xaxis_title='Kelompok Bahan')
                    st.plotly_chart(fig_a2_bar, use_container_width=True)

                st.markdown(
                    f"""
                    <div class='insight-box insight-green'>
                        <strong>💡 Insight — Pertanyaan Bisnis 2</strong><br><br>
                        <strong>Temuan:</strong><br>
                        • Rata-rata jumlah bahan per resep pada dataset raw adalah <strong>{avg_bahan:.2f}</strong> bahan.<br>
                        • Korelasi Pearson antara jumlah bahan dan loves sebesar <strong>{corr_bahan:.4f}</strong>, menunjukkan hubungan sangat lemah.<br>
                        • Resep sangat simpel tidak otomatis lebih populer dibanding kelompok lain berdasarkan rata-rata loves.<br><br>
                        <strong>Implikasi untuk SayurKita:</strong><br>
                        • Batas ≤12 bahan tetap valid untuk kemudahan eksekusi dengan bahan sisa, bukan semata karena popularitas.<br>
                        • Faktor popularitas (loves) tetap menjadi komponen utama quality score.<br>
                        • Resep simpel tetap relevan untuk konteks food waste karena lebih mungkin dimasak dari bahan yang hampir expired.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.info("Data numerik Total Ingredients/Loves tidak cukup untuk visualisasi pertanyaan ini.")
        else:
            st.info("Kolom Total Ingredients dan Loves belum lengkap pada dataset resep bersih.")

        # A3
        st.markdown("### 📊 Pertanyaan Bisnis 3 (Resep)")
        st.markdown("**Bahan makanan apa yang paling sering muncul di seluruh resep Indonesia pada dataset raw?**")
        if has_required_columns(df_resep_raw, ['Ingredients']) or has_required_columns(df_resep_raw, ['Ingredients Cleaned']):
            source_col = 'Ingredients Cleaned' if 'Ingredients Cleaned' in df_resep_raw.columns else 'Ingredients'
            bahan_series = df_resep_raw[source_col].dropna().astype(str)
            all_tokens = []
            for raw_text in bahan_series:
                for token in raw_text.split(','):
                    tkn = token.strip().lower()
                    if tkn:
                        all_tokens.append(tkn)

            if all_tokens:
                freq_df = pd.Series(all_tokens).value_counts().reset_index()
                freq_df.columns = ['Bahan', 'Frekuensi']
                top15 = freq_df.head(15).copy()
                top15['Bahan'] = top15['Bahan'].str.replace('_', ' ', regex=False)
                top15 = top15.sort_values('Frekuensi', ascending=True)

                fig_a3 = px.bar(
                    top15,
                    x='Frekuensi',
                    y='Bahan',
                    orientation='h',
                    text='Frekuensi',
                    color='Frekuensi',
                    color_continuous_scale='YlGn'
                )
                fig_a3.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), yaxis_title='')
                st.plotly_chart(fig_a3, use_container_width=True)

                top5_names = ', '.join(freq_df.head(5)['Bahan'].str.replace('_', ' ', regex=False).tolist())
                st.markdown(
                    f"""
                    <div class='insight-box insight-green'>
                        <strong>💡 Insight — Pertanyaan Bisnis 3</strong><br><br>
                        <strong>Temuan:</strong><br>
                        • Bawang putih dan garam merupakan bahan paling universal di resep Indonesia pada dataset raw.<br>
                        • Lima bahan teratas saat ini adalah: <strong>{top5_names}</strong>.<br>
                        • Berdasarkan prinsip Pareto, sebagian kecil bahan mencakup proporsi besar kemunculan bahan pada resep.<br><br>
                        <strong>Implikasi untuk SayurKita:</strong><br>
                        • Bahan teratas wajib diprioritaskan di Ingredients Master dengan data umur simpan yang akurat.<br>
                        • Autocomplete LihatKulkas™ perlu mengutamakan bahan-bahan dominan agar cepat diakses pengguna.<br>
                        • Bahan bumbu/rempah perlu klasifikasi kategori yang konsisten agar notifikasi dan rekomendasi lebih tepat.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.info("Data bahan tidak dapat diparse menjadi token bahan.")
        else:
            st.info("Kolom Ingredients/Ingredients Cleaned belum tersedia pada dataset resep mentah.")

        # A4
        st.markdown("### 📊 Pertanyaan Bisnis 4 (Resep)")
        st.markdown("**Apakah resep dengan langkah lebih banyak (lebih kompleks) pada dataset raw mendapat engagement (loves) lebih tinggi?**")
        if has_required_columns(df_recipe, ['Total Steps', 'Loves']):
            df_a4 = df_recipe.copy()
            df_a4['Total Steps'] = pd.to_numeric(df_a4['Total Steps'], errors='coerce')
            df_a4['Loves'] = pd.to_numeric(df_a4['Loves'], errors='coerce')
            df_a4 = df_a4.dropna(subset=['Total Steps', 'Loves'])

            if not df_a4.empty:
                corr_steps = float(df_a4['Total Steps'].corr(df_a4['Loves'])) if len(df_a4) > 1 else 0.0
                bins_steps = [0, 3, 5, 8, np.inf]
                labels_steps = ['Cepat (1-3)', 'Standar (4-5)', 'Detail (6-8)', 'Panjang (>8)']
                df_a4['kelompok_steps'] = pd.cut(df_a4['Total Steps'], bins=bins_steps, labels=labels_steps)
                steps_stats = (
                    df_a4.groupby('kelompok_steps', observed=True)['Loves']
                    .mean()
                    .reset_index(name='Rata-rata Loves')
                )

                v1, v2 = st.columns(2)
                with v1:
                    fig_a4_scatter = px.scatter(
                        safe_sample(df_a4, 2500),
                        x='Total Steps',
                        y='Loves',
                        opacity=0.35,
                        title='Korelasi Jumlah Langkah vs Loves'
                    )
                    x_vals = df_a4['Total Steps'].to_numpy()
                    y_vals = df_a4['Loves'].to_numpy()
                    if len(x_vals) > 1:
                        slope, intercept = np.polyfit(x_vals, y_vals, 1)
                        x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
                        fig_a4_scatter.add_scatter(
                            x=x_line,
                            y=slope * x_line + intercept,
                            mode='lines',
                            name='Tren',
                            line=dict(color=COLORS['danger'], width=2)
                        )
                    fig_a4_scatter.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10))
                    st.plotly_chart(fig_a4_scatter, use_container_width=True)
                with v2:
                    fig_a4_bar = px.bar(
                        steps_stats,
                        x='kelompok_steps',
                        y='Rata-rata Loves',
                        color='kelompok_steps',
                        color_discrete_sequence=[COLORS['g4'], COLORS['g6'], COLORS['a8'], COLORS['danger']],
                        title='Rata-rata Loves per Kelompok Langkah'
                    )
                    fig_a4_bar.update_layout(showlegend=False, height=360, margin=dict(l=10, r=10, t=30, b=10), xaxis_title='Kelompok Langkah')
                    st.plotly_chart(fig_a4_bar, use_container_width=True)

                st.markdown(
                    f"""
                    <div class='insight-box insight-green'>
                        <strong>💡 Insight — Pertanyaan Bisnis 4</strong><br><br>
                        <strong>Temuan:</strong><br>
                        • Korelasi Pearson antara jumlah langkah dan loves pada dataset raw sebesar <strong>{corr_steps:.4f}</strong>, mendekati nol.<br>
                        • Resep panjang tidak otomatis mendapat lebih banyak loves dibanding resep pendek.<br>
                        • Kelompok langkah standar dan detail cenderung memiliki rata-rata loves yang serupa.<br><br>
                        <strong>Implikasi untuk SayurKita:</strong><br>
                        • Jumlah langkah bukan faktor penentu popularitas, sehingga bobot skor langkah tidak perlu dominan.<br>
                        • Bobot skor_loves tetap menjadi komponen terbesar dalam quality score.<br>
                        • Detail instruksi tetap relevan untuk meningkatkan keberhasilan user memasak resep.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.info("Data numerik Total Steps/Loves tidak cukup untuk visualisasi pertanyaan ini.")
        else:
            st.info("Kolom Total Steps dan Loves belum lengkap pada dataset resep bersih.")

        st.divider()
        st.subheader("B. Analisis Dataset Carbon Factors Indonesia")

        if has_required_columns(df_carbon, ['Kategori', 'CO2e_per_kg']):
            df_carbon_work = df_carbon.copy()
            df_carbon_work['CO2e_per_kg'] = pd.to_numeric(df_carbon_work['CO2e_per_kg'], errors='coerce')
            df_carbon_work = df_carbon_work.dropna(subset=['Kategori', 'CO2e_per_kg'])
            df_carbon_work['nama_bahan'] = df_carbon_work['Kategori'].astype(str)

            def assign_carbon_category(nama):
                n = nama.lower()
                if any(x in n for x in ['sapi', 'beef']):
                    return 'Daging Sapi'
                if any(x in n for x in ['kambing', 'domba', 'goat', 'lamb']):
                    return 'Kambing/Domba'
                if any(x in n for x in ['udang', 'shrimp', 'lobster', 'kepiting', 'cumi']):
                    return 'Udang & Seafood'
                if any(x in n for x in ['ayam', 'unggas', 'bebek', 'kalkun', 'chicken']):
                    return 'Ayam & Unggas'
                if any(x in n for x in ['ikan', 'tuna', 'salmon', 'lele', 'nila', 'bandeng', 'fish']):
                    return 'Ikan'
                if any(x in n for x in ['susu', 'keju', 'yogurt', 'mentega', 'milk', 'cheese']):
                    return 'Produk Susu'
                if any(x in n for x in ['tempe', 'tahu', 'kedelai', 'tofu', 'soy']):
                    return 'Tempe & Tahu'
                if any(x in n for x in ['beras', 'nasi', 'rice']):
                    return 'Beras & Nasi'
                if any(x in n for x in ['sayur', 'bayam', 'wortel', 'kol', 'brokoli', 'tomat', 'kubis', 'kangkung']):
                    return 'Sayuran'
                if any(x in n for x in ['buah', 'apel', 'pisang', 'mangga', 'pepaya', 'jeruk']):
                    return 'Buah-buahan'
                if 'telur' in n:
                    return 'Telur'
                return 'Lainnya'

            df_carbon_work['kategori'] = df_carbon_work['nama_bahan'].apply(assign_carbon_category)
            cat_summary = (
                df_carbon_work.groupby('kategori', as_index=False)['CO2e_per_kg']
                .mean()
                .rename(columns={'CO2e_per_kg': 'Rata-rata'})
            )

            # B1
            st.markdown("### 📊 Pertanyaan Bisnis 1 (Karbon)")
            st.markdown("**Kategori makanan mana yang paling besar emisi CO₂-nya jika terbuang, dan seberapa besar perbedaannya?**")
            cat_plot = cat_summary[cat_summary['kategori'] != 'Lainnya'].copy()
            if not cat_plot.empty:
                max_row = cat_plot.loc[cat_plot['Rata-rata'].idxmax()]
                min_row = cat_plot.loc[cat_plot['Rata-rata'].idxmin()]
                rasio = float(max_row['Rata-rata'] / min_row['Rata-rata']) if min_row['Rata-rata'] > 0 else 0.0

                v1, v2 = st.columns(2)
                with v1:
                    fig_b1_bar = px.bar(
                        cat_plot.sort_values('Rata-rata', ascending=True),
                        x='Rata-rata',
                        y='kategori',
                        orientation='h',
                        text='Rata-rata',
                        color='kategori',
                        color_discrete_sequence=px.colors.qualitative.Bold
                    )
                    fig_b1_bar.update_layout(showlegend=False, height=380, margin=dict(l=10, r=10, t=10, b=10), xaxis_title='kg CO2e per kg')
                    st.plotly_chart(fig_b1_bar, use_container_width=True)
                with v2:
                    fig_b1_log = px.bar(
                        cat_plot.sort_values('Rata-rata', ascending=True),
                        x='Rata-rata',
                        y='kategori',
                        orientation='h',
                        text='Rata-rata',
                        log_x=True,
                        color='kategori',
                        color_discrete_sequence=px.colors.qualitative.Safe
                    )
                    fig_b1_log.update_layout(showlegend=False, height=380, margin=dict(l=10, r=10, t=10, b=10), xaxis_title='kg CO2e per kg (log scale)')
                    st.plotly_chart(fig_b1_log, use_container_width=True)

                st.markdown(
                    f"""
                    <div class='insight-box insight-blue'>
                        <strong>💡 Insight — Pertanyaan Bisnis Karbon 1</strong><br><br>
                        <strong>Temuan:</strong><br>
                        • Kategori emisi tertinggi adalah <strong>{max_row['kategori']}</strong> ({max_row['Rata-rata']:.2f} kg CO₂e/kg).<br>
                        • Kategori emisi terendah adalah <strong>{min_row['kategori']}</strong> ({min_row['Rata-rata']:.2f} kg CO₂e/kg).<br>
                        • Kesenjangan emisi mencapai sekitar <strong>{rasio:.1f}x</strong>.<br><br>
                        <strong>Implikasi untuk SayurKita:</strong><br>
                        • Jejak Hijau™ perlu memberi penekanan visual pada protein hewani karena dampaknya jauh lebih besar.<br>
                        • Notifikasi expiry untuk daging dan kambing perlu diprioritaskan lebih tinggi dibanding sayuran.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # B2
            st.markdown("### 📊 Pertanyaan Bisnis 2 (Karbon)")
            st.markdown("**Jika rata-rata rumah tangga membuang 1 kg makanan per hari, berapa total CO₂ yang bisa dicegah SayurKita dalam sebulan untuk 1.000 pengguna aktif?**")
            assumptions = {
                'WASTE_PER_DAY_KG': 1.0,
                'DAYS_PER_MONTH': 30,
                'N_USERS': 1000,
                'REDUCTION_RATE': 0.30
            }
            avg_co2 = float(cat_plot['Rata-rata'].mean()) if not cat_plot.empty else 0.0
            saved_ton = avg_co2 * assumptions['WASTE_PER_DAY_KG'] * assumptions['DAYS_PER_MONTH'] * assumptions['REDUCTION_RATE'] * assumptions['N_USERS'] / 1000

            scenario_users = pd.DataFrame({'Users': [100, 500, 1000, 5000, 10000]})
            scenario_users['CO2 Dicegah (ton/bulan)'] = (
                avg_co2 * assumptions['WASTE_PER_DAY_KG'] * assumptions['DAYS_PER_MONTH'] * assumptions['REDUCTION_RATE'] * scenario_users['Users'] / 1000
            ).round(2)

            v1, v2 = st.columns(2)
            with v1:
                if not cat_plot.empty:
                    sim_cat = cat_plot.copy()
                    sim_cat['CO2 Dicegah 1000 User (ton)'] = (
                        sim_cat['Rata-rata'] * assumptions['WASTE_PER_DAY_KG'] * assumptions['DAYS_PER_MONTH'] * assumptions['REDUCTION_RATE'] * assumptions['N_USERS'] / 1000
                    ).round(2)
                    fig_b2_bar = px.bar(
                        sim_cat.sort_values('CO2 Dicegah 1000 User (ton)', ascending=True),
                        x='CO2 Dicegah 1000 User (ton)',
                        y='kategori',
                        orientation='h',
                        text='CO2 Dicegah 1000 User (ton)',
                        color='kategori',
                        color_discrete_sequence=px.colors.qualitative.Prism
                    )
                    fig_b2_bar.update_layout(showlegend=False, height=380, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_b2_bar, use_container_width=True)
            with v2:
                fig_b2_line = px.line(
                    scenario_users,
                    x='Users',
                    y='CO2 Dicegah (ton/bulan)',
                    markers=True,
                    title='Proyeksi Dampak terhadap Skala Pengguna'
                )
                fig_b2_line.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_b2_line, use_container_width=True)

            st.markdown(
                f"""
                <div class='insight-box insight-blue'>
                    <strong>💡 Insight — Pertanyaan Bisnis Karbon 2</strong><br><br>
                    <strong>Temuan:</strong><br>
                    • Dengan asumsi 1 kg buang/hari, 30% berhasil dicegah, dan 1.000 user aktif, dampak campuran berada di sekitar <strong>{saved_ton:.1f} ton CO₂e/bulan</strong>.<br>
                    • Ketika jumlah pengguna bertambah, dampak pengurangan emisi meningkat secara linear dan signifikan.<br><br>
                    <strong>Implikasi untuk SayurKita:</strong><br>
                    • Angka ini dapat menjadi baseline impact projection untuk presentasi capstone.<br>
                    • Dashboard Jejak Hijau™ sebaiknya menampilkan dampak komunitas agar dampaknya lebih terasa bagi pengguna.<br>
                    • Skenario sensitivitas 100–10.000 user cocok untuk menunjukkan potensi scaling produk.
                </div>
                """,
                unsafe_allow_html=True
            )

            # B3
            st.markdown("### 📊 Pertanyaan Bisnis 3 (Karbon)")
            st.markdown("**Dalam satuan yang lebih relatable: berapa km perjalanan mobil yang setara dengan menyelamatkan 1 kg daging sapi vs 1 kg sayuran?**")
            CO2_PER_KM_CAR = 0.21
            compare_labels = ['Daging Sapi', 'Kambing/Domba', 'Ayam & Unggas', 'Sayuran', 'Tempe & Tahu']
            cmp = cat_plot[cat_plot['kategori'].isin(compare_labels)].copy()
            if not cmp.empty:
                cmp['km Mobil'] = (cmp['Rata-rata'] / CO2_PER_KM_CAR).round(1)
                fig_b3 = px.bar(
                    cmp.sort_values('km Mobil', ascending=True),
                    x='km Mobil',
                    y='kategori',
                    orientation='h',
                    text='km Mobil',
                    color='kategori',
                    color_discrete_sequence=px.colors.qualitative.Vivid
                )
                fig_b3.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10), xaxis_title='Setara km mobil per 1 kg diselamatkan')
                st.plotly_chart(fig_b3, use_container_width=True)

                sapi_km = float(cmp.loc[cmp['kategori'] == 'Daging Sapi', 'km Mobil'].iloc[0]) if (cmp['kategori'] == 'Daging Sapi').any() else 0.0
                sayur_km = float(cmp.loc[cmp['kategori'] == 'Sayuran', 'km Mobil'].iloc[0]) if (cmp['kategori'] == 'Sayuran').any() else 0.0
                ratio_km = (sapi_km / sayur_km) if sayur_km > 0 else 0.0

                st.markdown(
                    f"""
                    <div class='insight-box insight-blue'>
                        <strong>💡 Insight — Pertanyaan Bisnis Karbon 3</strong><br><br>
                        <strong>Temuan:</strong><br>
                        • Menyelamatkan 1 kg daging sapi setara mengurangi perjalanan mobil sekitar <strong>{sapi_km:.1f} km</strong>.<br>
                        • Menyelamatkan 1 kg sayuran setara mengurangi perjalanan mobil sekitar <strong>{sayur_km:.1f} km</strong>.<br>
                        • Dampak per kg daging sapi sekitar <strong>{ratio_km:.1f}x</strong> dibanding sayuran.<br><br>
                        <strong>Implikasi untuk SayurKita:</strong><br>
                        • Satuan km berkendara layak dijadikan default output Jejak Hijau™ karena lebih relatable.<br>
                        • Notifikasi expiry protein hewani bisa menampilkan pesan kontekstual berbasis jarak berkendara.<br>
                        • Perbandingan ini efektif sebagai konten edukasi di onboarding screen.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("Dataset karbon belum memiliki kolom Kategori dan CO2e_per_kg yang diperlukan.")

    with tab_b:
        st.subheader("Analisis Ingredients Master dan Nutrition")

        # Q1
        st.markdown("### 📊 Pertanyaan Bisnis 1")
        st.markdown("**Kategori bahan apa yang paling banyak digunakan dalam resep, dan seberapa besar kontribusinya terhadap total penggunaan?**")
        if has_required_columns(df_master, ['kategori', 'frekuensi']):
            df_b1 = df_master.copy()
            df_b1['frekuensi'] = pd.to_numeric(df_b1['frekuensi'], errors='coerce')
            df_b1 = df_b1.dropna(subset=['kategori', 'frekuensi'])
            if not df_b1.empty:
                frek_kat = (
                    df_b1.groupby('kategori', as_index=False)['frekuensi']
                    .sum()
                    .rename(columns={'frekuensi': 'total_frekuensi'})
                    .sort_values('total_frekuensi', ascending=False)
                )
                total_semua = float(frek_kat['total_frekuensi'].sum())
                frek_kat['persentase'] = (frek_kat['total_frekuensi'] / total_semua * 100).round(2)

                v1, v2 = st.columns(2)
                with v1:
                    fig_q1_bar = px.bar(
                        frek_kat.sort_values('total_frekuensi', ascending=True),
                        x='total_frekuensi',
                        y='kategori',
                        orientation='h',
                        text='total_frekuensi',
                        color='kategori',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_q1_bar.update_layout(showlegend=False, height=360, margin=dict(l=10, r=10, t=10, b=10), xaxis_title='Total Frekuensi')
                    st.plotly_chart(fig_q1_bar, use_container_width=True)
                with v2:
                    fig_q1_pie = px.pie(
                        frek_kat,
                        names='kategori',
                        values='total_frekuensi',
                        hole=0.35,
                        color_discrete_sequence=px.colors.qualitative.Safe
                    )
                    fig_q1_pie.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_q1_pie, use_container_width=True)

                top_kat = frek_kat.iloc[0]
                st.markdown(
                    f"""
                    <div class='insight-box insight-amber'>
                        <strong>💡 Insight:</strong><br>
                        Bumbu mendominasi pemakaian bahan di dapur, dan kategori dominan saat ini adalah <strong>{top_kat['kategori']}</strong>
                        dengan kontribusi sekitar <strong>{top_kat['persentase']:.2f}%</strong>.<br><br>
                        <strong>🎯 Rekomendasi:</strong><br>
                        Buat batas minimum safety stock untuk bahan-bahan bumbu inti agar staf dapat memesan sebelum stok habis.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("Kolom kategori/frekuensi pada ingredients master belum lengkap.")

        # Q2
        st.markdown("### 📊 Pertanyaan Bisnis 2")
        st.markdown("**Bahan-bahan apa saja yang paling sering digunakan (top 20), dan apakah ketersediaannya sudah mencerminkan prioritas stok yang tepat?**")
        if has_required_columns(df_master, ['nama_id', 'frekuensi', 'kategori']):
            top20 = (
                df_master[['nama_id', 'frekuensi', 'kategori']]
                .copy()
            )
            top20['frekuensi'] = pd.to_numeric(top20['frekuensi'], errors='coerce')
            top20 = top20.dropna(subset=['nama_id', 'frekuensi', 'kategori']).sort_values('frekuensi', ascending=False).head(20)
            if not top20.empty:
                fig_q2 = px.bar(
                    top20.sort_values('frekuensi', ascending=True),
                    x='frekuensi',
                    y='nama_id',
                    orientation='h',
                    color='kategori',
                    text='frekuensi',
                    color_discrete_sequence=px.colors.qualitative.Dark24
                )
                fig_q2.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), yaxis_title='Nama Bahan', xaxis_title='Frekuensi')
                st.plotly_chart(fig_q2, use_container_width=True)

                st.markdown(
                    """
                    <div class='insight-box insight-amber'>
                        <strong>💡 Insight:</strong><br>
                        Tiga bahan utama penyangga resep adalah bawang putih, garam, dan bawang merah, sehingga ketiganya paling krusial untuk kontinuitas operasional masak.<br><br>
                        <strong>🎯 Rekomendasi:</strong><br>
                        Evaluasi bahan yang jarang dipakai namun mudah rusak, lalu pertimbangkan substitusi ke bahan kering/bubuk agar lebih awet.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("Kolom nama_id/frekuensi/kategori belum lengkap untuk membentuk top 20 bahan.")

        # Q3
        st.markdown("### 📊 Pertanyaan Bisnis 3")
        st.markdown("**Bagaimana perbandingan rata-rata umur simpan bahan di kulkas, suhu ruang, dan freezer antar kategori? Kategori mana yang paling rentan pembusukan?**")
        if has_required_columns(df_master, ['kategori', 'umur_kulkas', 'umur_suhu_ruang', 'umur_freezer']):
            umur = df_master[['kategori', 'umur_kulkas', 'umur_suhu_ruang', 'umur_freezer']].copy()
            for col in ['umur_kulkas', 'umur_suhu_ruang', 'umur_freezer']:
                umur[col] = pd.to_numeric(umur[col], errors='coerce')
            umur = umur.dropna(subset=['kategori'])

            umur_kat = (
                umur.groupby('kategori', as_index=False)[['umur_kulkas', 'umur_suhu_ruang', 'umur_freezer']]
                .mean()
                .round(1)
                .sort_values('umur_suhu_ruang', ascending=True)
            )
            if not umur_kat.empty:
                umur_melt = umur_kat.melt(
                    id_vars='kategori',
                    value_vars=['umur_suhu_ruang', 'umur_kulkas', 'umur_freezer'],
                    var_name='Metode Penyimpanan',
                    value_name='Rata-rata Hari'
                )
                map_name = {
                    'umur_suhu_ruang': 'Suhu Ruang',
                    'umur_kulkas': 'Kulkas',
                    'umur_freezer': 'Freezer'
                }
                umur_melt['Metode Penyimpanan'] = umur_melt['Metode Penyimpanan'].map(map_name)

                fig_q3 = px.bar(
                    umur_melt,
                    x='kategori',
                    y='Rata-rata Hari',
                    color='Metode Penyimpanan',
                    barmode='group',
                    color_discrete_sequence=[COLORS['danger'], COLORS['b6'], COLORS['g6']]
                )
                fig_q3.update_layout(height=430, margin=dict(l=10, r=10, t=10, b=10), xaxis_title='Kategori', yaxis_title='Rata-rata Umur Simpan (Hari)')
                st.plotly_chart(fig_q3, use_container_width=True)

                st.markdown(
                    """
                    <div class='insight-box insight-amber'>
                        <strong>💡 Insight:</strong><br>
                        Protein hewani adalah kelompok paling cepat busuk di suhu ruang, tetapi umur simpan dapat diperpanjang signifikan ketika dipindahkan ke freezer.<br><br>
                        <strong>🎯 Rekomendasi:</strong><br>
                        Maksimalkan kapasitas freezer khusus lauk hewani, dan langsung bekukan stok mentah setelah bahan datang dari supplier.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("Kolom umur simpan belum lengkap untuk analisis perbandingan antar metode penyimpanan.")

        # Q4
        st.markdown("### 📊 Pertanyaan Bisnis 4")
        st.markdown("**Berapa proporsi bahan yang tergolong berisiko tinggi pembusukan (umur simpan suhu ruang ≤ 3 hari), dan tersebar di kategori apa saja?**")
        if has_required_columns(df_master, ['kategori', 'nama_id', 'umur_suhu_ruang']):
            risiko = df_master[['kategori', 'nama_id', 'umur_suhu_ruang']].copy()
            risiko['umur_suhu_ruang'] = pd.to_numeric(risiko['umur_suhu_ruang'], errors='coerce')
            risiko = risiko.dropna(subset=['kategori', 'nama_id', 'umur_suhu_ruang'])

            def klasifikasi_risiko(hari):
                if hari <= 3:
                    return 'Tinggi (<=3 hari)'
                if hari <= 7:
                    return 'Sedang (4-7 hari)'
                return 'Rendah (>7 hari)'

            risiko['risiko_suhu_ruang'] = risiko['umur_suhu_ruang'].apply(klasifikasi_risiko)
            ringkasan = risiko['risiko_suhu_ruang'].value_counts().reset_index()
            ringkasan.columns = ['Risiko', 'Jumlah']

            risiko_tinggi_kat = (
                risiko[risiko['risiko_suhu_ruang'] == 'Tinggi (<=3 hari)']
                .groupby('kategori', as_index=False)['nama_id']
                .count()
                .rename(columns={'nama_id': 'jumlah_bahan_berisiko'})
                .sort_values('jumlah_bahan_berisiko', ascending=False)
            )

            v1, v2 = st.columns(2)
            with v1:
                fig_q4_pie = px.pie(
                    ringkasan,
                    names='Risiko',
                    values='Jumlah',
                    hole=0.5,
                    color='Risiko',
                    color_discrete_map={
                        'Tinggi (<=3 hari)': '#e74c3c',
                        'Sedang (4-7 hari)': '#f39c12',
                        'Rendah (>7 hari)': '#2ecc71'
                    }
                )
                fig_q4_pie.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_q4_pie, use_container_width=True)
            with v2:
                fig_q4_bar = px.bar(
                    risiko_tinggi_kat,
                    x='kategori',
                    y='jumlah_bahan_berisiko',
                    text='jumlah_bahan_berisiko',
                    color='jumlah_bahan_berisiko',
                    color_continuous_scale='Reds'
                )
                fig_q4_bar.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10), xaxis_title='Kategori', yaxis_title='Jumlah Bahan Risiko Tinggi')
                st.plotly_chart(fig_q4_bar, use_container_width=True)

            high_count = int(ringkasan.loc[ringkasan['Risiko'] == 'Tinggi (<=3 hari)', 'Jumlah'].sum()) if not ringkasan.empty else 0
            total_count = int(ringkasan['Jumlah'].sum()) if not ringkasan.empty else 0
            high_pct = (high_count / total_count * 100) if total_count > 0 else 0.0

            st.markdown(
                f"""
                <div class='insight-box insight-amber'>
                    <strong>💡 Insight:</strong><br>
                    Sekitar <strong>{high_pct:.1f}%</strong> bahan tergolong risiko tinggi pembusukan di suhu ruang (≤3 hari), terutama pada kelompok protein hewani dan olahan.<br><br>
                    <strong>🎯 Rekomendasi:</strong><br>
                    Terapkan belanja berkala (just-in-time) untuk bahan basah agar stok cepat rusak tidak menumpuk dan food waste berkurang.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("Kolom umur_suhu_ruang/kategori/nama_id belum lengkap untuk analisis risiko pembusukan.")

        # Q5
        st.markdown("### 📊 Pertanyaan Bisnis 5")
        st.markdown("**Bahan apa saja yang paling hemat kalori namun tinggi protein (efisiensi nutrisi tertinggi), dan kategori apa yang mendominasi?**")
        if has_required_columns(df_master, ['nama_id', 'kategori', 'kalori_per_100g', 'protein_g']):
            gizi = df_master[['nama_id', 'kategori', 'kalori_per_100g', 'protein_g']].copy()
            gizi['kalori_per_100g'] = pd.to_numeric(gizi['kalori_per_100g'], errors='coerce')
            gizi['protein_g'] = pd.to_numeric(gizi['protein_g'], errors='coerce')
            gizi = gizi[(gizi['kalori_per_100g'] > 0) & (gizi['protein_g'] > 0)].dropna(subset=['nama_id', 'kategori'])

            if not gizi.empty:
                gizi['efisiensi_nutrisi'] = (gizi['protein_g'] / gizi['kalori_per_100g'] * 100).round(2)
                top15 = gizi.sort_values('efisiensi_nutrisi', ascending=False).head(15)

                v1, v2 = st.columns(2)
                with v1:
                    fig_q5_bar = px.bar(
                        top15.sort_values('efisiensi_nutrisi', ascending=True),
                        x='efisiensi_nutrisi',
                        y='nama_id',
                        orientation='h',
                        color='kategori',
                        text='efisiensi_nutrisi',
                        color_discrete_sequence=px.colors.qualitative.Dark24
                    )
                    fig_q5_bar.update_layout(height=430, margin=dict(l=10, r=10, t=10, b=10), xaxis_title='g protein per 100 kkal', yaxis_title='Nama Bahan')
                    st.plotly_chart(fig_q5_bar, use_container_width=True)
                with v2:
                    fig_q5_scatter = px.scatter(
                        gizi,
                        x='kalori_per_100g',
                        y='protein_g',
                        color='kategori',
                        hover_name='nama_id',
                        opacity=0.55,
                        title='Sebaran Kalori vs Protein'
                    )
                    fig_q5_scatter.update_layout(height=430, margin=dict(l=10, r=10, t=30, b=10), xaxis_title='Kalori per 100g', yaxis_title='Protein per 100g')
                    st.plotly_chart(fig_q5_scatter, use_container_width=True)

                top_eff = top15.iloc[0]
                st.markdown(
                    f"""
                    <div class='insight-box insight-amber'>
                        <strong>💡 Insight:</strong><br>
                        Bahan paling efisien pada data saat ini adalah <strong>{top_eff['nama_id']}</strong> dengan skor
                        <strong>{top_eff['efisiensi_nutrisi']:.2f}</strong> g protein per 100 kkal; secara umum protein hewani cenderung paling efisien untuk rasio protein per kalori.<br><br>
                        <strong>🎯 Rekomendasi:</strong><br>
                        Manfaatkan bahan ikan/hewani berprotein tinggi sebagai variasi menu sehat untuk pengguna yang peduli gizi dan diet.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("Kolom gizi (kalori/protein) belum lengkap untuk analisis efisiensi nutrisi.")
