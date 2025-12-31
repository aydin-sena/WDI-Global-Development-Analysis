import subprocess
import sys
import time
import os

# Kodların olduğu klasör
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Çalıştırılacak dosyalar listesi (Sırası önemli)
scripts = [
    "01_data_processing.py",
    "02_eda.py",
    "03_modeling.py",
    "04_regression_analysis.py"
]

def run_pipeline():
    print("Veri analiz süreci başlatılıyor...\n")
    total_start = time.time()

    for script_name in scripts:
        # Tam dosya yolunu oluştur
        script_path = os.path.join(BASE_DIR, script_name)
        
        print(f"-> {script_name} çalıştırılıyor...")
        
        try:
            # sys.executable: Şu anki python.exe'yi kullanır (env hatası olmasın diye)
            subprocess.run([sys.executable, script_path], check=True)
            print("   Tamamlandı.\n")
            
        except subprocess.CalledProcessError:
            print(f"\nHATA: {script_name} çalışırken bir sorun oldu. İşlem durduruldu.")
            sys.exit(1) # Hata varsa devam etme, çık
        except Exception as e:
            print(f"Beklenmedik hata: {e}")
            sys.exit(1)

    total_end = time.time()
    print(f"Tüm işlemler başarıyla bitti! (Toplam süre: {total_end - total_start:.2f} saniye)")

if __name__ == "__main__":
    run_pipeline()