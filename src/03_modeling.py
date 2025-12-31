import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import os

def run_model():
    print("Modelleme (PCA ve Clustering) yapılıyor...")
    
    # Dosya yolları
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(CURRENT_DIR)
    
    csv_file = os.path.join(ROOT_DIR, "ready_for_analysis.csv")
    plots_dir = os.path.join(ROOT_DIR, "plots")
    
    if not os.path.exists(csv_file):
        print("Hata: Veri dosyası bulunamadı.")
        return

    df = pd.read_csv(csv_file)
    
    # Sadece sayısal verileri alıyoruz
    features = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    X = df[features]

    # ÖNEMLİ: Ölçek Farklılığı Sorunu
    # GSYİH 50.000 dolar iken Yaşam Süresi 80 yıl. Bu fark algoritmayı yanıltır.
    # Bu yüzden veriyi standartlaştırıyoruz (Z-Score).
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA (Boyut İndirgeme)
    # Çoklu bağlantı (Multicollinearity) sorununu aşmak ve görselleştirme için boyutu 2'ye indiriyoruz.
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    # Varyansın ne kadarını koruduk?
    explained_variance = pca.explained_variance_ratio_.sum() * 100
    print(f"PCA Toplam Açıklanan Varyans: %{explained_variance:.2f}")

    # K-Means Kümeleme
    # Ülkeleri 3 ana gruba (Gelişmiş, Gelişmekte, Az Gelişmiş) ayırmayı hedefliyoruz.
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    df['Cluster'] = clusters
    
    # Sonuçları Görselleştirme
    plt.figure(figsize=(12, 8))
    sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=df['Cluster'], 
                    palette='viridis', s=100, alpha=0.8, style=df['Region'])
    
    plt.title(f'Ülke Kümeleri (PCA) - Varyans: %{explained_variance:.1f}', fontsize=14)
    plt.xlabel('PC1 (Genel Kalkınma)')
    plt.ylabel('PC2 (Yapısal Farklılık)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'clustering_results.png'))
    
    print("Kümeleme grafiği kaydedildi.")
    
    # Hangi küme ne anlama geliyor? Ortalamalara bakarak yorumlayacağız.
    print("\nKümelerin Ortalamaları:")
    print(df.groupby('Cluster')[features].mean())

if __name__ == "__main__":
    run_model()