import pandas as pd
import numpy as np
import os

# Path ayarları
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, 'data')

TARGET_INDICATORS = {
    'NY.GDP.PCAP.CD': 'GDP_Per_Capita',
    'SP.DYN.LE00.IN': 'Life_Expectancy',
    'SE.SEC.ENRR': 'School_Enrollment',
    'EG.ELC.ACCS.ZS': 'Electricity_Access',
    'SP.URB.TOTL.IN.ZS': 'Urban_Population',
    'IT.NET.USER.ZS': 'Internet_Usage'
}

def load_and_clean_data():
    print("Veri hazırlanıyor...")
    
    # Veri setini zip içinden veya csv olarak oku
    csv_path = os.path.join(DATA_DIR, "WDICSV.zip") # GitHub boyutu yüzünden zip yaptık
    country_path = os.path.join(DATA_DIR, "WDICountry.csv")
    
    if not os.path.exists(csv_path):
         # Zip yoksa csv dene
         csv_path = os.path.join(DATA_DIR, "WDICSV.csv")

    df_data = pd.read_csv(csv_path)
    df_country = pd.read_csv(country_path)

    # İlgili göstergeleri filtrele
    df_filtered = df_data[df_data['Indicator Code'].isin(TARGET_INDICATORS.keys())].copy()
    
    # Son 12 yılın ortalamasını alarak veriyi tekilleştir
    year_cols = [str(y) for y in range(2010, 2022)] 
    available_years = [col for col in year_cols if col in df_filtered.columns]
    df_filtered['Mean_Value'] = df_filtered[available_years].mean(axis=1)

    # Tabloyu düzenle (Wide format)
    df_pivot = df_filtered.pivot(index='Country Code', columns='Indicator Code', values='Mean_Value')
    df_pivot.rename(columns=TARGET_INDICATORS, inplace=True)

    # Sadece gerçek ülkeleri filtrele (Bölge gruplarını çıkar)
    real_countries = df_country.dropna(subset=['Region'])['Country Code']
    df_final = df_pivot[df_pivot.index.isin(real_countries)].copy()
    
    # Bölge bilgisini ekle
    df_final = df_final.merge(df_country[['Country Code', 'Short Name', 'Region']], 
                              left_index=True, right_on='Country Code')
    
    return df_final

def impute_missing_values(df):
    print("Eksik veriler dolduruluyor...")
    numeric_cols = [c for c in df.columns if c in TARGET_INDICATORS.values()]
    
    for col in numeric_cols:
        if df[col].isnull().all():
            df.drop(columns=[col], inplace=True)
            continue

        # Bölgesel medyan ile doldur (Global ortalama yerine bias önlemek için)
        df[col] = df[col].fillna(df.groupby('Region')[col].transform('median'))
        
        # Hala boş kalan varsa genel medyanı bas
        if df[col].isnull().sum() > 0:
             df[col] = df[col].fillna(df[col].median())
    
    return df

if __name__ == "__main__":
    try:
        df = load_and_clean_data()
        df = impute_missing_values(df)
        
        output_path = os.path.join(ROOT_DIR, "ready_for_analysis.csv")
        df.to_csv(output_path, index=False)
        print(f"Hazır veri kaydedildi: {output_path}")
        
    except Exception as e:
        print(f"Hata: {e}")