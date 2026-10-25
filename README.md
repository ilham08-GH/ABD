# 🌦️ Indonesia Climate Explorer (BMKG 2010–2020)

Dashboard visualisasi interaktif data iklim historis BMKG Indonesia (193 stasiun pengamatan, rentang 2010–2020) yang terinspirasi oleh antarmuka modern **Windy.com**.

Projek ini disusun untuk memenuhi tugas **UAS Analisis Big Data (ABD)**.

---

## ✨ Fitur Utama

1. **🗺️ Peta Iklim Spasial Berkelanjutan (Windy-Style Continuous Field)**
   - **🌈 Hamparan Kontur 2D (Raster Interpolation)**: Menggunakan interpolasi spasial 2D halus (*Scipy GridData + Gaussian Smoothing*) yang menyelimuti seluruh daratan pulau dan perairan laut Indonesia dengan spektrum warna gradien (*turbo, viridis, YlGnBu*), persis seperti citra satelit/model numerik Windy.
   - **💨 Aliran Vektor Angin (Wind Streamlines)**: Garis-garis putih aliran angin dengan panah arah (*streamplot*) yang melintang melintasi kepulauan Indonesia berdasarkan vektor kecepatan ($u, v$).
   - **📍 Station Circle Markers**: Titik stasiun BMKG dengan penanda warna gradien nilai aktual dan *rich tooltip/popup* informasi stasiun.
   - **🌐 Windy.com Live Weather Radar**: Tab terintegrasi yang menyematkan peta interaktif resmi dari Windy.com (animasi partikel angin live dan radar cuaca ECMWF/GFS).

2. **🌤️ Meteogram Multi-Parameter yang Sejajar (Konsep Kunci Windy)**
   - Seluruh parameter cuaca (Suhu, Hujan, Kelembaban, Penyinaran, Angin) disusun bertumpuk dalam satu garis waktu (*timeline*) yang tersinkronisasi (*shared X-axis*).
   - Fitur *unified crosshair hover*: Menyorot korelasi cuaca secara simultan (misal: saat suhu turun, kelembaban naik, dan hujan melonjak).

3. **⏱️ Multi-Resolusi Waktu**
   - **Harian (Daily)**: Analisis fluktuasi harian data cuaca.
   - **Bulanan (Monthly)**: Pola musiman dan fluktuasi bulanan.
   - **Tahunan (Yearly)**: Tren iklim jangka panjang 2010–2020.
   - Slider filter tahun (2010–2020) dan filter bulan (1–12).

4. **🎨 5 Parameter Iklim Utama**
   - 🌡️ **Suhu Udara**: Rata-rata (`Tavg`), Minimum (`Tn`), dan Maksimum (`Tx`) dengan diagram pita rentang suhu (*temperature band*).
   - 🌧️ **Curah Hujan**: Total akumulasi dan rata-rata harian dengan pewarnaan intensitas BMKG (Biru muda -> Jingga/Merah).
   - 💧 **Kelembaban Udara (`RH`)**: Persentase kelembaban relatif.
   - 💨 **Kecepatan & Arah Angin**: Kecepatan rata-rata/maksimum dan diagram **Wind Rose** polar berkodekan kecepatan (*Plasma colormap*).
   - ☀️ **Penyinaran Matahari**: Durasi jam penyinaran matahari.

5. **📊 Analisis Detail & Interaktif per Stasiun**
   - Pilih stasiun langsung dengan **klik pada peta** atau via *search dropdown*.
   - Tab visualisasi analitik interaktif berbasis Plotly.
   - Panel koordinat, nama stasiun, kabupaten/kota, dan provinsi.

6. **📈 Perbandingan Regional Antar Provinsi**
   - Bar chart komparasi rata-rata parameter per provinsi di Indonesia.

7. **🔮 Prediksi Iklim Lintas Waktu (Sebelum 2026, Real-Time 2026, & Masa Depan 2027)**
   - Estimasi cuaca 7 hari ke depan untuk 193 stasiun BMKG dengan pita interval kepercayaan (*confidence band* 95%).
   - Mendukung 4 rezim waktu: *Historis 2020*, *Backcasting Retrospektif (2021–2025)*, *Tahun Berjalan 2026*, dan *Prospektif 2027*.

8. **🤖 Integrasi Model Machine Learning (Random Forest Regressor & Classifier)**
   - **🌲 RF Regressor**: Prediksi suhu numerik ($Tavg_{t+1}$) harian dengan **MAE 0.52 °C** dan **R² 87.14%**.
   - **🏷️ RF Classifier**: Klasifikasi kondisi cuaca 4 kelas (*Cerah / Berawan*, *Hujan Ringan*, *Hujan Lebat*, *Panas Terik*) dengan **Akurasi 53.65%**.
   - **📊 Dashboard Evaluasi**: Plot *Feature Importance* dan *Confusion Matrix* interaktif 117.614 sampel uji BMKG.
   - **🧪 Simulator Inferensi Real-Time**: Uji coba skenario input kustom dengan kalkulasi probabilitas kelas instan.

---

## 📁 Struktur Direktori

```text
UAS/
├── .streamlit/
│   └── config.toml          # Konfigurasi dark theme & port
├── data/                    # Dataset teroptimasi (Parquet)
│   ├── climate_daily.parquet    (~5.0 MB)
│   ├── climate_monthly.parquet  (~0.4 MB)
│   ├── climate_yearly.parquet   (~0.1 MB)
│   ├── wind_direction.parquet   (~0.02 MB)
│   ├── station_detail.csv       (~15 KB)
│   └── province_detail.csv      (~1 KB)
├── models/                  # Model Machine Learning Terlatih
│   ├── model_rf_regressor.pkl   (~132 MB, RF Regressor Suhu)
│   └── model_rf_classifier.pkl  (~58 MB, RF Classifier Cuaca)
├── app.py                   # Aplikasi utama Streamlit + Windy Engine
├── generate_climate_projections.py # Generator proyeksi tren iklim 2021–2027
├── prepare_data.py          # Script preprocessing ETL ke Parquet
├── requirements.txt         # Daftar pustaka Python (Streamlit, Scikit-Learn, Plotly, dll)
└── README.md                # Dokumentasi & panduan deploy
```


> **Catatan Optimasi Big Data**: File mentah CSV berukuran besar (~63 MB) telah dikonversi dan diindeks ke dalam format kolom **Apache Parquet** dengan total hanya **~5.5 MB**. Hal ini membuat *load time* menjadi instan (< 1 detik) dan sangat hemat memori, ideal untuk *cloud hosting*.

---

## 🚀 Menjalankan Secara Lokal

### 1. Prasyarat
Pastikan Python 3.10+ sudah terpasang.

### 2. Instalasi Dependensi
```bash
cd UAS
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi
```bash
streamlit run app.py
```
Buka browser pada alamat: `http://localhost:8501`

---

## 🌐 Panduan Deploy Online (Gratis)

Pilih salah satu platform gratis berikut:

### Opsi 1: Streamlit Community Cloud (Sangat Direkomendasikan ⭐)
1. **Buat Git Repository**:
   - Inisialisasi git di folder `UAS`:
     ```bash
     git init
     git add .
     git commit -m "Initial commit UAS Climate Explorer"
     ```
   - Buat repository baru di [GitHub](https://github.com/new) (misal: `indonesia-climate-explorer`).
   - Push kode ke GitHub:
     ```bash
     git remote add origin https://github.com/<username-kamu>/indonesia-climate-explorer.git
     git branch -M main
     git push -u origin main
     ```
2. **Deploy di Streamlit Cloud**:
   - Buka [share.streamlit.io](https://share.streamlit.io/) dan login dengan akun GitHub.
   - Klik **"New app"**.
   - Pilih Repository, Branch: `main`, Main file path: `app.py`.
   - Klik **"Deploy!"**.
   - Aplikasi akan live dalam 1-2 menit dengan URL publik `https://<nama-app>.streamlit.app`!

---

### Opsi 2: Hugging Face Spaces
1. Buka [huggingface.co/spaces](https://huggingface.co/spaces) dan login.
2. Klik **"Create new Space"**.
3. Isi nama Space (misal: `indonesia-climate-explorer`), pilih SDK: **Streamlit**, Hardware: **Free (2 vCPU, 16GB RAM)**.
4. Clone repo Space yang diberikan oleh Hugging Face atau upload langsung file-file dari folder `UAS/` (`app.py`, `requirements.txt`, `.streamlit/`, dan folder `data/`).
5. Space akan otomatis membangun (*build*) dan siap diakses publik!
