# Smart Farming Project with WSN, Computer Vision, and Fuzzy Logic

Sistem Smart Farming ini menggunakan Raspberry Pi sebagai server utama, ESP32 sebagai node sensor, dan dilengkapi dengan kemampuan Computer Vision untuk deteksi kematangan tanaman serta Fuzzy Logic untuk pengambilan keputusan pengairan otomatis.

## Daftar Isi

- [Ringkasan Proyek](#ringkasan-proyek)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Komponen yang Dibutuhkan](#komponen-yang-dibutuhkan)
- [Instalasi dan Pengaturan](#instalasi-dan-pengaturan)
  - [Pengaturan Raspberry Pi](#pengaturan-raspberry-pi)
  - [Pengaturan ESP32](#pengaturan-esp32)
  - [Pengaturan Hardware](#pengaturan-hardware)
  - [Instalasi Web Interface](#instalasi-web-interface)
- [Penggunaan Sistem](#penggunaan-sistem)
- [Dokumentasi API](#dokumentasi-api)
- [Troubleshooting](#troubleshooting)
- [Pengembangan Lebih Lanjut](#pengembangan-lebih-lanjut)
- [Lisensi](#lisensi)

## Ringkasan Proyek

Proyek Smart Farming ini menggabungkan beberapa teknologi untuk membuat sistem monitoring dan irigasi otomatis:

1. **Wireless Sensor Network (WSN)**: ESP32 membaca data kelembaban tanah dan mengirimkannya ke Raspberry Pi.
2. **Fuzzy Logic**: Algoritma pengambilan keputusan untuk menentukan kapan irigasi dibutuhkan.
3. **Computer Vision**: Deteksi kematangan tanaman menggunakan kamera dan model machine learning.
4. **Web Interface**: Dashboard untuk monitoring dan kontrol sistem.

Sistem akan mengaktifkan selenoid valve untuk irigasi ketika tanah terdeteksi kering, dan akan menonaktifkannya ketika tanah sudah cukup lembab.

## Arsitektur Sistem

![Smart Farming System Architecture](docs/images/system_architecture.svg)

Data mengalir sebagai berikut:

1. Sensor kelembaban tanah pada ESP32 membaca data.
2. ESP32 mengirim data ke Raspberry Pi melalui WSN (WiFi).
3. Raspberry Pi memproses data menggunakan Fuzzy Logic.
4. Raspberry Pi mengirim perintah kontrol kembali ke ESP32.
5. ESP32 mengaktifkan/menonaktifkan selenoid valve sesuai kebutuhan.
6. Kamera terhubung ke Raspberry Pi mengambil gambar untuk deteksi kematangan.
7. Raspberry Pi memproses gambar dengan Computer Vision.
8. Web interface menampilkan semua data dan status sistem.

## Komponen yang Dibutuhkan

### Hardware:
- 1 x Raspberry Pi 4
- 2 x ESP32
- 2 x Sensor kelembaban tanah
- 2 x Selenoid valve
- 2 x Sprinkler
- 2 x Selang panjang 2 meter
- 1 x Pompa air
- 1 x Raspberry Pi Camera atau webcam
- Kabel jumper
- Relay board (untuk mengontrol selenoid valve dan pompa)
- Power supply untuk Raspberry Pi dan ESP32
- Kotak tahan air untuk elektronik

### Software:
- Raspberry Pi OS
- Python 3.7+
- Flask
- TensorFlow
- scikit-fuzzy
- Arduino IDE
- Libraries ESP32: WiFi, HTTPClient, ArduinoJson

## Instalasi dan Pengaturan

### Pengaturan Raspberry Pi

#### 1. Instalasi Raspberry Pi OS

Unduh dan instal Raspberry Pi OS menggunakan Raspberry Pi Imager:
```
https://www.raspberrypi.org/software/
```

#### 2. Pengaturan Awal Raspberry Pi

Setelah instalasi OS, lakukan pengaturan awal:

```bash
# Update sistem
sudo apt update
sudo apt upgrade -y

# Install dependensi yang dibutuhkan
sudo apt install -y git python3-pip python3-venv libatlas-base-dev libopenjp2-7 libtiff5

# Aktifkan kamera (jika menggunakan Raspberry Pi Camera)
sudo raspi-config
# Pilih Interface Options -> Camera -> Enable
```

#### 3. Clone Repository

```bash
git clone https://github.com/username/Smart-Farming-Project.git
cd Smart-Farming-Project
```

#### 4. Setup Python Environment

```bash
# Buat virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependensi Python
pip install -r requirements.txt
```

#### 5. Konfigurasi Server

Edit file konfigurasi sesuai kebutuhan:

```bash
nano raspberry_pi/config.py
```

Sesuaikan IP address, port, dan konfigurasi lainnya.

#### 6. Setup Model Computer Vision

Letakkan model yang sudah dilatih ke folder models:

```bash
mkdir -p raspberry_pi/models
# Salin model kematangan ke raspberry_pi/models/maturity_model.h5
```

### Pengaturan ESP32

#### 1. Instalasi Arduino IDE

Unduh dan instal Arduino IDE dari:
```
https://www.arduino.cc/en/software

#### 2. Instalasi ESP32 Board Manager

Tambahkan URL board manager ESP32 di Arduino IDE:

1. Buka Arduino IDE
2. Buka menu File -> Preferences
3. Pada "Additional Boards Manager URLs", tambahkan:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Klik OK
5. Buka menu Tools -> Board -> Boards Manager
6. Cari "ESP32", dan instal board ESP32 by Espressif Systems

#### 3. Instalasi Library yang Dibutuhkan

Buka menu Sketch -> Include Library -> Manage Libraries dan instal:
- WiFi
- HTTPClient
- ArduinoJson (versi 6.x)

#### 4. Konfigurasi Node ESP32

1. Buka file `esp32/node_1/config.h` dan `esp32/node_2/config.h`
2. Sesuaikan WiFi SSID, password, dan IP address Raspberry Pi:

```cpp
// File config.h
#define WIFI_SSID "YourWiFiName"
#define WIFI_PASSWORD "YourWiFiPassword"
#define SERVER_IP "192.168.1.100" // IP Raspberry Pi Anda
```

#### 5. Upload Kode ke ESP32

1. Hubungkan ESP32 pertama ke komputer menggunakan kabel USB
2. Pilih board dan port yang sesuai di menu Tools
3. Buka file `esp32/node_1/node_1.ino`
4. Klik tombol Upload untuk mengirim kode ke ESP32
5. Ulangi langkah 1-4 untuk ESP32 kedua, menggunakan file `esp32/node_2/node_2.ino`

### Pengaturan Hardware

#### 1. Koneksi Sensor Kelembaban Tanah ke ESP32

Untuk setiap node ESP32:
- Hubungkan VCC sensor ke pin 3.3V ESP32
- Hubungkan GND sensor ke pin GND ESP32
- Hubungkan pin data analog sensor ke pin 34 ESP32 (sesuaikan dengan kode)

#### 2. Koneksi Selenoid Valve ke ESP32

Gunakan relay untuk mengontrol selenoid valve:
- Hubungkan pin input relay ke pin 26 ESP32 (sesuaikan dengan kode)
- Hubungkan pin VCC relay ke 5V (dari power supply eksternal)
- Hubungkan pin GND relay ke GND ESP32
- Hubungkan selenoid valve ke output relay dan power supply

#### 3. Koneksi Kamera ke Raspberry Pi

Jika menggunakan Raspberry Pi Camera:
- Hubungkan kamera ke CSI port pada Raspberry Pi
- Pastikan kabel terkoneksi dengan benar

Jika menggunakan Webcam USB:
- Hubungkan webcam ke port USB Raspberry Pi

#### 4. Koneksi Sistem Irigasi

- Hubungkan pompa air ke power supply dan relay (yang dikontrol oleh ESP32)
- Pasang selang dari pompa air ke selenoid valve
- Pasang selang dari selenoid valve ke sprinkler
- Pastikan semua koneksi rapat dan tidak bocor

### Instalasi Web Interface

#### 1. Konfigurasi Web Server

```bash
# Masuk ke direktori web_interface
cd web_interface

# Jalankan aplikasi web
python app.py
```

Web interface akan berjalan di port 8080. Buka browser dan akses:
```
http://[raspberry-pi-ip]:8080
```

#### 2. Pengaturan Autostart pada Boot

Untuk menjalankan server dan web interface secara otomatis saat boot:

```bash
# Buat file service untuk systemd
sudo nano /etc/systemd/system/smartfarm.service
```

Isi dengan:
```
[Unit]
Description=Smart Farming System
After=network.target

[Service]
ExecStart=/home/pi/Smart-Farming-Project/venv/bin/python /home/pi/Smart-Farming-Project/raspberry_pi/server.py
WorkingDirectory=/home/pi/Smart-Farming-Project/raspberry_pi
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Buat file service untuk web interface:
```bash
sudo nano /etc/systemd/system/smartfarm-web.service
```

Isi dengan:
```
[Unit]
Description=Smart Farming Web Interface
After=network.target smartfarm.service

[Service]
ExecStart=/home/pi/Smart-Farming-Project/venv/bin/python /home/pi/Smart-Farming-Project/web_interface/app.py
WorkingDirectory=/home/pi/Smart-Farming-Project/web_interface
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Aktifkan service:
```bash
sudo systemctl enable smartfarm.service
sudo systemctl enable smartfarm-web.service
sudo systemctl start smartfarm.service
sudo systemctl start smartfarm-web.service
```

## Penggunaan Sistem

### Mengakses Dashboard

Buka browser web dan akses:
```
http://[raspberry-pi-ip]:8080
```

### Fitur Web Interface

- **Dashboard**: Menampilkan status kelembaban tanah, status valve, dan deteksi kematangan terkini
- **Grafik Tren**: Menampilkan data kelembaban tanah selama 24 jam terakhir
- **Kontrol Manual**: Tombol untuk mengaktifkan/menonaktifkan selenoid valve secara manual
- **Capture Gambar**: Tombol untuk mengambil gambar baru dan mendeteksi kematangan
- **Halaman Riwayat**: Melihat riwayat kelembaban tanah dan deteksi kematangan

### Pemahaman Logika Fuzzy

Sistem menggunakan logika fuzzy untuk menentukan kapan mengaktifkan irigasi:

1. **Input**: Persentase kelembaban tanah (0-100%)
2. **Membership Functions**:
   - Kering: 0-40%
   - Sedang: 20-80%
   - Basah: 60-100%
3. **Aturan Fuzzy**:
   - Jika tanah kering, aktifkan valve
   - Jika tanah sedang, pertahankan status valve
   - Jika tanah basah, matikan valve
4. **Output**: Perintah ON/OFF untuk selenoid valve

### Computer Vision untuk Deteksi Kematangan

Kamera akan mengambil gambar secara berkala atau melalui perintah manual:

1. Gambar diambil dan disimpan
2. Model CV memproses gambar untuk mengklasifikasikan kematangan
3. Hasil klasifikasi ditampilkan di dashboard
4. Hasil rinci (persentase setiap kelas) juga ditampilkan

## Dokumentasi API

### API Endpoints

#### Endpoint ESP32

- `POST /sensor-data`: Menerima data sensor dari node ESP32
- `GET /node-command/<node_id>`: ESP32 mengambil perintah terbaru

#### API Web Interface

- `GET /api/data`: Mendapatkan data terbaru dari semua sensor
- `GET /api/history?days=7`: Mendapatkan data historis selama N hari
- `GET /api/maturity`: Mendapatkan hasil deteksi kematangan terbaru
- `POST /api/manual-control`: Mengirim perintah kontrol manual
- `POST /api/capture`: Memicu pengambilan gambar dan deteksi kematangan
- `GET /api/images/<filename>`: Mengambil gambar yang tersimpan

### Format Data

#### Sensor Data (ESP32 -> Server)

```json
{
  "node_id": "node1",
  "soil_moisture": 45.7,
  "valve_status": false
}
```

#### Command Data (Server -> ESP32)

```json
{
  "valve_command": true
}
```

## Troubleshooting

### Masalah Koneksi WiFi

**Masalah**: ESP32 tidak dapat terhubung ke jaringan WiFi
**Solusi**:
- Pastikan SSID dan password WiFi benar
- Pastikan sinyal WiFi cukup kuat di lokasi ESP32
- Coba reset ESP32 dan periksa log serial

### Masalah Sensor Kelembaban

**Masalah**: Pembacaan kelembaban tanah tidak akurat
**Solusi**:
- Kalibrasi sensor dengan mengukur nilai ADC pada kondisi kering dan basah
- Sesuaikan nilai `MOISTURE_DRY_VALUE` dan `MOISTURE_WET_VALUE` di file config.h
- Pastikan sensor tertanam dengan benar di tanah

### Masalah Selenoid Valve

**Masalah**: Selenoid valve tidak aktif meskipun diberi perintah
**Solusi**:
- Periksa koneksi relay dan pastikan GPIO memberikan output yang benar
- Pastikan selenoid valve mendapat daya yang cukup
- Periksa apakah ada kesalahan pengkabelan

### Masalah Kamera

**Masalah**: Kamera tidak menangkap gambar
**Solusi**:
- Pastikan kamera terhubung dengan benar
- Jalankan `raspistill -o test.jpg` untuk menguji kamera
- Periksa izin akses file dan direktori

### Log dan Debugging

Untuk memeriksa log server:
```bash
tail -f raspberry_pi/server.log
```

Untuk memeriksa log web interface:
```bash
tail -f web_interface/web_interface.log
```

Untuk ESP32, buka Serial Monitor di Arduino IDE untuk melihat output debugging.

## Pengembangan Lebih Lanjut

Beberapa ide untuk pengembangan sistem:

1. **Integrasi Sensor Tambahan**: Suhu udara, kelembaban udara, intensitas cahaya
2. **Notifikasi**: Kirim notifikasi melalui email/SMS saat kondisi tertentu terpenuhi
3. **Kontrol Jarak Jauh**: Akses ke sistem dari internet (dengan keamanan yang memadai)
4. **Database Cloud**: Sinkronisasi data ke cloud untuk analisis jangka panjang
5. **Panel Surya**: Tambahkan panel surya dan baterai untuk power supply
6. **Machine Learning**: Prediksi kebutuhan air berdasarkan pola cuaca dan kelembaban
7. **Aplikasi Mobile**: Kembangkan aplikasi Android/iOS untuk monitoring dan kontrol

## Lisensi

Proyek ini dilisensikan di bawah MIT License - lihat file [LICENSE](LICENSE) untuk detail.

---

Dibuat oleh: NOVAL FADLI ROBBANI  
GitHub: Lyynov  
Kontak: novalfadli10@students.unnes.ac.id