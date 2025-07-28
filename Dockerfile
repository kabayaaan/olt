# Dockerfile
# Gunakan base image Python yang ringan
FROM python:3.9-slim-buster

# Tetapkan direktori kerja di dalam container
WORKDIR /app

# Salin file requirements.txt ke direktori kerja
# Ini akan menginstal dependensi sebelum menyalin kode aplikasi
COPY requirements.txt .

# Instal dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode aplikasi ke direktori kerja
COPY . .

# Ekspos port 5000, karena Flask berjalan di port ini secara default
EXPOSE 5000

# Perintah untuk menjalankan aplikasi Flask
# Gunakan Gunicorn sebagai server WSGI produksi yang lebih tangguh
# daripada server development bawaan Flask.
# Pastikan Anda telah menginstal gunicorn di requirements.txt
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
