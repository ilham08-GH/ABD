"""
Preprocessing script: Converts the large climate CSV to optimized Parquet files.
Creates daily, monthly, and yearly aggregations for fast loading.
"""
import pandas as pd
import numpy as np
import os
import sys

SRC_CSV = os.path.join('..', 'tugasProjek', 'climate_data_clean.csv')
OUT_DIR = 'data'

os.makedirs(OUT_DIR, exist_ok=True)

print("📂 Loading climate_data_clean.csv ...")
df = pd.read_csv(SRC_CSV, parse_dates=['Date'])

# ── Rename for internal consistency ──
df = df.rename(columns={
    'Date': 'date',
    'Year': 'year',
    'Month': 'month',
    'Month_Name': 'month_name',
    'Season': 'season',
    'Station_ID': 'station_id',
    'Temp_Min_C': 'temp_min',
    'Temp_Max_C': 'temp_max',
    'Temp_Avg_C': 'temp_avg',
    'Humidity_Pct': 'humidity',
    'Rainfall_mm': 'rainfall',
    'Sunshine_Hours': 'sunshine',
    'Wind_Speed_Avg': 'wind_avg',
    'Wind_Speed_Max': 'wind_max',
    'Wind_Direction_Card': 'wind_dir',
    'Rainfall_Category': 'rain_cat',
})

# Drop the raw date column if exists
if 'Date_Raw' in df.columns:
    df = df.drop(columns=['Date_Raw'])

# Clean wind_dir (strip whitespace)
df['wind_dir'] = df['wind_dir'].str.strip()

print(f"   ✅ Loaded {len(df):,} rows, {len(df.columns)} columns")
print(f"   📅 Date range: {df['date'].min()} → {df['date'].max()}")
print(f"   🏢 Stations: {df['station_id'].nunique()}")

# ── 1. Save daily data as parquet ──
print("\n💾 Saving daily parquet ...")
df.to_parquet(os.path.join(OUT_DIR, 'climate_daily.parquet'), index=False)
size_mb = os.path.getsize(os.path.join(OUT_DIR, 'climate_daily.parquet')) / 1024 / 1024
print(f"   ✅ climate_daily.parquet ({size_mb:.1f} MB)")

# ── 2. Monthly aggregation ──
print("\n📊 Creating monthly aggregation ...")
agg_funcs = {
    'temp_min': 'mean',
    'temp_max': 'mean',
    'temp_avg': 'mean',
    'humidity': 'mean',
    'rainfall': 'sum',
    'sunshine': 'mean',
    'wind_avg': 'mean',
    'wind_max': 'max',
}
monthly = df.groupby(['station_id', 'year', 'month']).agg(agg_funcs).reset_index()

# Add month names
month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'Mei', 6:'Jun',
               7:'Jul', 8:'Agu', 9:'Sep', 10:'Okt', 11:'Nov', 12:'Des'}
monthly['month_name'] = monthly['month'].map(month_names)

# Add season
def get_season(m):
    if m in [11, 12, 1, 2, 3, 4]:
        return 'Musim Hujan'
    return 'Musim Kemarau'
monthly['season'] = monthly['month'].apply(get_season)

monthly.to_parquet(os.path.join(OUT_DIR, 'climate_monthly.parquet'), index=False)
size_mb = os.path.getsize(os.path.join(OUT_DIR, 'climate_monthly.parquet')) / 1024 / 1024
print(f"   ✅ climate_monthly.parquet ({size_mb:.1f} MB) — {len(monthly):,} rows")

# ── 3. Yearly aggregation ──
print("\n📊 Creating yearly aggregation ...")
yearly = df.groupby(['station_id', 'year']).agg(agg_funcs).reset_index()
yearly.to_parquet(os.path.join(OUT_DIR, 'climate_yearly.parquet'), index=False)
size_mb = os.path.getsize(os.path.join(OUT_DIR, 'climate_yearly.parquet')) / 1024 / 1024
print(f"   ✅ climate_yearly.parquet ({size_mb:.1f} MB) — {len(yearly):,} rows")

# ── 4. Wind direction aggregation (for wind rose) ──
print("\n🌬️ Creating wind direction stats ...")
wind_stats = df.groupby(['station_id', 'wind_dir']).agg(
    count=('wind_dir', 'size'),
    avg_speed=('wind_avg', 'mean'),
    max_speed=('wind_max', 'max'),
).reset_index()
wind_stats.to_parquet(os.path.join(OUT_DIR, 'wind_direction.parquet'), index=False)
size_mb = os.path.getsize(os.path.join(OUT_DIR, 'wind_direction.parquet')) / 1024 / 1024
print(f"   ✅ wind_direction.parquet ({size_mb:.1f} MB) — {len(wind_stats):,} rows")

print("\n🎉 All done! Data is ready for the Streamlit app.")
