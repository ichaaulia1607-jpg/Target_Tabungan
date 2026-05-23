# Proyek Analisis Data: FinTrack AI - Target Tabungan 💰

## Deskripsi
Proyek ini bertujuan untuk menganalisis data historis target tabungan personal guna memahami sisa nominal pemenuhan target, rata-rata kemampuan menabung harian, serta estimasi alokasi dana untuk 30 hari ke depan. Hasil analisis ini disajikan dalam bentuk dashboard interaktif yang dibangun menggunakan library Streamlit untuk mempermudah pemantauan progres keuangan secara real-time.

## Struktur Folder
```text
.
├── Capstone/
│   ├── dashboard.py           # File utama dashboard Streamlit
│   ├── target tabungan.xlsx   # Dataset utama historis tabungan
│   ├── notebook.ipynb         # File eksplorasi data (Jupyter Notebook)
│   ├── README.md              # Dokumentasi proyek (File ini)
│   ├── requirements.txt       # Daftar library/dependencies Python
│   └── url.txt                # Tautan link tautan web Streamlit Cloud (jika di-deploy)
```

# Setup Environment - Anaconda
```bash
conda create --name fintrack-ds python=3.9
conda activate fintrack-ds
pip install -r requirements.txt
```

# Setup Environment - Terminal/Command Prompt
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
# Cara Menjalankan Dashboard
```bash
streamlit run dashboard.py
```
