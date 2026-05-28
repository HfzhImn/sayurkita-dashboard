# SayurKita Dashboard

Interactive Streamlit dashboard for Indonesian recipe analytics, nutrition coverage, and carbon footprint insights.

---

## Versi Bahasa Indonesia

### Deskripsi Singkat

SayurKita Dashboard adalah aplikasi visualisasi berbasis Streamlit yang membantu mengeksplorasi dataset resep masakan Indonesia, master ingredients (standarisasi bahan), informasi kandungan gizi, serta faktor emisi karbon per komoditas. Dashboard ini dirancang untuk mendukung analisis pengurangan food waste dan membantu menentukan prioritas komoditas yang memberikan dampak lingkungan dan ekonomi terbesar.

### Fitur Utama

- Ringkasan KPI: jumlah resep mentah dan yang sudah dibersihkan, cakupan data nutrisi, dan faktor emisi.
- Analisis distribusi resep per kategori dan bahan yang paling sering muncul.
- Visualisasi umur simpan bahan (kulkas) dan coverage integrasi gizi.
- Kalkulator proyeksi dampak penghematan emisi CO₂e berdasarkan asumsi pengguna aktif dan massa bahan yang diselamatkan.
- Matriks prioritas komoditas untuk pengambilan keputusan fitur aplikasi (mis. notifikasi expiry dan rekomendasi penggunaan bahan).

### Data yang Digunakan

- `data/indonesian_food_recipes.csv` — dataset resep mentah (opsional jika ingin memuat data asli).
- `data/clean_recipes_5000.json` — dataset resep bersih hasil proses cleaning (jika tersedia).
- `data/ingredients_master_final.csv` — master list bahan yang berisi frekuensi, kategori, umur simpan, dan kandungan gizi.
- `data/carbon_factors_indonesia.json` — faktor emisi CO₂e per komoditas.

> Catatan: Jika folder `data/` disertakan di repo, Streamlit Cloud akan menggunakan file tersebut saat menjalankan aplikasi. Untuk data besar, pertimbangkan menyimpan di storage eksternal (Google Drive, S3) dan modifikasi `app.py` untuk memuat dari URL.

### Cara Menjalankan (Lokal)

1. (Opsional) Buat environment virtual dan aktifkan:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Pasang dependensi:

```bash
pip install -r requirements.txt
```

3. Jalankan aplikasi:

```bash
streamlit run app.py
```

### Deploy ke Streamlit Cloud

1. Push repository ke GitHub.
2. Buka https://share.streamlit.io, login dengan akun GitHub.
3. Pilih "New app", hubungkan ke repository, atur `app.py` sebagai main file, lalu klik Deploy. Streamlit akan menginstall paket dari `requirements.txt`.

---

## English Version

### Short Description

SayurKita Dashboard is an interactive Streamlit application for exploring Indonesian recipe datasets, a standardized ingredients master list, nutrition coverage, and commodity-level carbon footprint factors. It is built to support food waste reduction analysis and prioritize items with the largest environmental and economic impact.

### Key Features

- KPI overview: raw and cleaned recipe counts, nutrition coverage, and emission factors.
- Distribution analysis of recipes by category and the most frequently used ingredients.
- Shelf-life visualizations and nutrition matching coverage.
- Interactive CO₂e impact calculator to estimate community-level environmental savings.
- Priority scoring matrix for suggesting features like expiry alerts and ingredient-saving recommendations.

### Data Files

- `data/indonesian_food_recipes.csv` — raw recipes dataset (optional).
- `data/clean_recipes_5000.json` — cleaned recipes dataset used by dashboard.
- `data/ingredients_master_final.csv` — ingredients master with frequency, categories, shelf-life and nutrition.
- `data/carbon_factors_indonesia.json` — carbon emission factors per commodity.

Note: Keep the `data/` folder in the repository if you want Streamlit Cloud to use the local datasets. For large files, host them externally and update `app.py` to load from URL.

### Quick Start (Local)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

### Deploying to Streamlit Cloud

1. Push the project to a GitHub repository (e.g., `sayurkita-dashboard`).
2. Go to https://share.streamlit.io and log in with GitHub.
3. Create a new app, select the repository and branch, set the main file to `app.py`, and deploy. Streamlit will install dependencies from `requirements.txt`.

---

## Contact / License

If you have questions or want to collaborate, open an issue or contact the maintainer.
