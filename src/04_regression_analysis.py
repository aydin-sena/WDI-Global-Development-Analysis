import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats
import os

# Dosya yolları
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
DATA_PATH = os.path.join(ROOT_DIR, "ready_for_analysis.csv")
PLOTS_DIR = os.path.join(ROOT_DIR, "plots")

def run_regression_analysis():
    print("Regresyon analizi ve istatistiksel testler yapılıyor...")

    if not os.path.exists(DATA_PATH):
        print("Hata: Veri dosyası bulunamadı.")
        return

    df = pd.read_csv(DATA_PATH)
    
    # Model Değişkenleri
    # Bağımsız değişkenler arasından 'Internet_Usage' çıkarıldı çünkü 'Electricity_Access' ile 
    # korelasyonu çok yüksek (Multicollinearity sorunu yaratıyor).
    target = 'Life_Expectancy'
    features = ['GDP_Per_Capita', 'School_Enrollment', 'Electricity_Access', 'Urban_Population']
    
    X = df[features].copy()
    y = df[target]
    
    # ÖNEMLİ: GSYİH (GDP) verisi sağa çarpık (skewed) dağılım gösteriyor.
    # Lineer ilişkiyi yakalamak ve normallik varsayımını sağlamak için Log dönüşümü yapıyoruz.
    # Bu sayede model 'Log-Level' yoruma uygun hale gelir (% değişim etkisi).
    X['GDP_Per_Capita'] = np.log(X['GDP_Per_Capita'])
    X.rename(columns={'GDP_Per_Capita': 'Log_GDP'}, inplace=True)
    
    # Statsmodels kütüphanesi için sabiti (intercept/beta0) manuel eklememiz gerek
    X = sm.add_constant(X)
    
    # OLS (En Küçük Kareler) Modelini Kur
    model = sm.OLS(y, X).fit()
    
    print(model.summary())
    
    # Sonuçları text dosyasına da kaydedelim
    with open(os.path.join(ROOT_DIR, "regression_summary.txt"), "w") as f:
        f.write(model.summary().as_text())

    # --- İSTATİSTİKSEL VARSAYIM KONTROLLERİ ---
    print("\nModel Varsayımları Kontrol Ediliyor...")

    # 1. Çoklu Bağlantı (VIF) Kontrolü
    # VIF değerinin 10'un (hatta 5'in) altında olması istenir.
    vif_data = pd.DataFrame()
    vif_data["feature"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(len(X.columns))]
    
    print("\nVIF Değerleri:")
    print(vif_data)
    
    # 2. Hataların Normalliği (Normality of Residuals)
    residuals = model.resid
    
    # Q-Q Plot
    plt.figure(figsize=(8, 6))
    sm.qqplot(residuals, line='45', fit=True)
    plt.title('Q-Q Plot (Hataların Normalliği)')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'regression_qq_plot.png'))
    
    # Shapiro-Wilk Testi (P > 0.05 ise H0 reddedilemez -> Normal dağılıyor)
    shapiro_test = stats.shapiro(residuals)
    print(f"\nNormallik Testi (Shapiro-Wilk): p-value = {shapiro_test.pvalue:.4f}")
    
    if shapiro_test.pvalue > 0.05:
        print("-> Hatalar Normal Dağılıyor (Varsayım Sağlandı)")
    else:
        print("-> Hatalar Normal Dağılım göstermiyor (Dikkat)")

    # 3. Varyansın Sabitliği (Homoscedasticity)
    # Residuals vs Fitted grafiğinde rastgele dağılım bekliyoruz.
    plt.figure(figsize=(8, 6))
    plt.scatter(model.fittedvalues, residuals, alpha=0.7)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('Tahmin Değerleri')
    plt.ylabel('Hatalar (Residuals)')
    plt.title('Residuals vs Fitted (Eş Varyans Kontrolü)')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'regression_residuals_vs_fitted.png'))
    
    print("Tanısal grafikler 'plots' klasörüne kaydedildi.")

if __name__ == "__main__":
    run_regression_analysis()