import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_eda():
    print("Grafikler hazırlanıyor...")
    
    # Dosya yollarını belirle
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(CURRENT_DIR)
    
    csv_file = os.path.join(ROOT_DIR, "ready_for_analysis.csv")
    plots_dir = os.path.join(ROOT_DIR, "plots")

    if not os.path.exists(csv_file):
        print(f"Hata: {csv_file} bulunamadı. Önce veri işleme adımını çalıştırın.")
        return

    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)

    df = pd.read_csv(csv_file)
    
    # Sadece sayısal değişkenleri görselleştireceğiz
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    # Eğer modelleme öncesi Cluster sütunu oluştuysa onu çıkar (kategorik olduğu için)
    if 'Cluster' in numeric_cols: 
        numeric_cols.remove('Cluster')

    print(f"İncelenen değişkenler: {numeric_cols}")

    # 1. Korelasyon Matrisi (Multicollinearity kontrolü için önemli)
    plt.figure(figsize=(10, 8))
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Korelasyon Matrisi')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'correlation_matrix.png'))
    
    # 2. Boxplotlar (Aykırı değer / Outlier tespiti için)
    # Dinamik subplot ayarı: Değişken sayısına göre satır açar
    num_vars = len(numeric_cols)
    rows = (num_vars // 3) + 1
    
    plt.figure(figsize=(16, 5 * rows))
    for i, col in enumerate(numeric_cols, 1):
        plt.subplot(rows, 3, i)
        sns.boxplot(y=df[col], color='skyblue')
        plt.title(col)
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'boxplots.png'))
    
    print("Grafikler 'plots' klasörüne kaydedildi.")

if __name__ == "__main__":
    run_eda()