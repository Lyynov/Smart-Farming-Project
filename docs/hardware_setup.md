# Hardware Setup Instructions

Panduan ini memberikan petunjuk detil tentang cara menyiapkan hardware untuk sistem Smart Farming.

## Daftar Isi

- [Komponen yang Dibutuhkan](#komponen-yang-dibutuhkan)
- [Diagram Koneksi](#diagram-koneksi)
- [Raspberry Pi Setup](#raspberry-pi-setup)
- [ESP32 Node Setup](#esp32-node-setup)
- [Sensor Kelembaban Tanah](#sensor-kelembaban-tanah)
- [Selenoid Valve dan Pompa](#selenoid-valve-dan-pompa)
- [Kamera Setup](#kamera-setup)
- [Tips Pemasangan di Lapangan](#tips-pemasangan-di-lapangan)

## Komponen yang Dibutuhkan

### Komponen Utama:
- 1 x Raspberry Pi 4 (min. 2GB RAM)
- 2 x ESP32 Development Board
- 2 x Sensor kelembaban tanah (Soil moisture sensor)
- 2 x Selenoid valve 12V
- 2 x Sprinkler
- 1 x Pompa air 12V
- 1 x Raspberry Pi Camera V2 atau webcam USB

### Komponen Penunjang:
- 2 x Modul relay 2 channel
- 1 x Power supply 12V / 5A
- 1 x Buck converter 12V to 5V (untuk ESP32)
- Kabel jumper (male-to-male, male-to-female, female-to-female)
- 2 x Selang panjang 2 meter
- Box tahan air untuk elektronik
- Kabel AWG 16 atau 18 untuk jalur daya
- Konektor waterproof (opsional tapi direkomendasikan)
- Sekrup, baut, dan pengikat (zip tie)
- SD Card 16GB atau lebih untuk Raspberry Pi

### Alat yang Dibutuhkan:
- Obeng (plus dan minus)
- Tang potong
- Tang kombinasi
- Solder dan timah
- Multimeter
- Heat shrink tubing
- Isolasi listrik

## Diagram Koneksi

### Koneksi Raspberry Pi

```
Raspberry Pi:
+---------------------------------------------------------------+
|                                                               |
|  [Camera Port] -- CSI Cable -- Raspberry Pi Camera Module     |
|                                                               |
|  [USB Port] ------- USB Cable ------- USB Webcam (alternatif) |
|                                                               |
|  [Ethernet] -------- LAN Cable ------ Router                  |
|   or [WiFi]                                                   |
|                                                               |
|  [Power Port] ------ USB-C Cable ---- Power Supply            |
|                                                               |
+---------------------------------------------------------------+
```

### Koneksi ESP32 Node 1

```
ESP32 Node 1:
+---------------------------------------------------+
|                                                   |
|  GPIO34 ------- Sensor Kelembaban Tanah 1         |
|                                                   |
|  GPIO26 ------- IN1 Relay Module                  |
|                                                   |
|  5V ----------- 5V dari Buck Converter            |
|                                                   |
|  GND ---------- GND dari Power Supply             |
|                                                   |
+---------------------------------------------------+

Relay Module 1:
+---------------------------------------------------+
|                                                   |
|  IN1 ---------- GPIO26 ESP32                      |
|                                                   |
|  VCC ---------- 5V dari Buck Converter            |
|                                                   |
|  GND ---------- GND dari Power Supply             |
|                                                   |
|  COM1 --------- 12V dari Power Supply             |
|                                                   |
|  NO1 ---------- Selenoid Valve 1 (+)              |
|                                                   |
+---------------------------------------------------+

Selenoid Valve 1:
+---------------------------------------------------+
|                                                   |
|  (+) ---------- NO1 dari Relay Module 1           |
|                                                   |
|  (-) ---------- GND dari Power Supply             |
|                                                   |
+---------------------------------------------------+
```

### Koneksi ESP32 Node 2

```
ESP32 Node 2:
+---------------------------------------------------+
|                                                   |
|  GPIO34 ------- Sensor Kelembaban Tanah 2         |
|                                                   |
|  GPIO26 ------- IN1 Relay Module                  |
|                                                   |
|  5V ----------- 5V dari Buck Converter            |
|                                                   |
|  GND ---------- GND dari Power Supply             |
|                                                   |
+---------------------------------------------------+

Relay Module 2:
+---------------------------------------------------+
|                                                   |
|  IN1 ---------- GPIO26 ESP32                      |
|                                                   |
|  VCC ---------- 5V dari Buck Converter            |
|                                                   |
|  GND ---------- GND dari Power Supply             |
|                                                   |
|  COM1 --------- 12V dari Power Supply             |
|                                                   |
|  NO1 ---------- Selenoid Valve 2 (+)              |
|                                                   |
+---------------------------------------------------+

Selenoid Valve 2:
+---------------------------------------------------+
|                                                   |
|  (+) ---------- NO1 dari Relay Module 2           |
|                                                   |
|  (-) ---------- GND dari Power Supply             |
|                                                   |
+---------------------------------------------------+
```

### Koneksi Pompa Air

```
Pompa Air:
+---------------------------------------------------+
|                                                   |
|  (+) ---------- NO2 dari Relay Module 1 (Node 1)  |
|                                                   |
|  (-) ---------- GND dari Power Supply             |
|                                                   |
+---------------------------------------------------+
```

## Raspberry Pi Setup

1. **Persiapan Raspberry Pi**
   - Pasang SD card yang sudah diinstall Raspberry Pi OS ke slot SD card
   - Hubungkan Raspberry Pi Camera ke port CSI (jika menggunakan Pi Camera)
   - Hubungkan webcam USB ke port USB (jika menggunakan webcam)
   - Hubungkan kabel ethernet (atau gunakan WiFi)
   - Terakhir, hubungkan power supply ke port power

2. **Persiapan Kotak Pelindung**
   - Tempatkan Raspberry Pi di dalam kotak tahan air
   - Pastikan ada ventilasi yang cukup untuk menghindari overheating
   - Buat lubang untuk kabel kamera, ethernet (jika digunakan), dan power

3. **Konfigurasi Awal**
   - Lakukan konfigurasi dasar Raspberry Pi (enable SSH, camera, setting timezone)
   - Pastikan Raspberry Pi terhubung ke jaringan internet

## ESP32 Node Setup

1. **Persiapan ESP32**
   - Siapkan board ESP32 untuk Node 1 dan Node 2
   - Pasang ESP32 pada breadboard atau PCB jika menggunakan soldered version

2. **Power Supply Setup**
   - Hubungkan buck converter ke power supply 12V
   - Atur output buck converter ke 5V menggunakan multimeter
   - Hubungkan output 5V ke pin VIN ESP32 dan VCC relay module
   - Hubungkan GND dari power supply ke GND ESP32 dan GND relay module

3. **Pin Connections**
   - Hubungkan GPIO34 ke pin data sensor kelembaban tanah
   - Hubungkan GPIO26 ke pin IN1 modul relay
   - Pastikan semua koneksi GND terhubung satu sama lain

4. **Persiapan Kotak Pelindung**
   - Tempatkan ESP32 dan relay module di dalam kotak tahan air
   - Buat lubang untuk kabel sensor, kabel selenoid valve, dan power
   - Pastikan semua kabel dilindungi dengan baik

## Sensor Kelembaban Tanah

1. **Persiapan Sensor**
   - Setiap sensor kelembaban tanah memiliki 3 pin: VCC, GND, dan DATA
   - Buat kabel ekstensi waterproof jika sensor akan ditempatkan jauh dari ESP32

2. **Koneksi Sensor**
   - Hubungkan VCC sensor ke 3.3V ESP32
   - Hubungkan GND sensor ke GND ESP32
   - Hubungkan pin DATA sensor ke GPIO34 ESP32

3. **Penempatan Sensor**
   - Pasang sensor di dalam tanah pada kedalaman yang sesuai (biasanya 5-10 cm)
   - Pastikan bagian sensing (bagian logam) terkubur sempurna
   - Lindungi bagian circuit sensor dari air dan kelembaban

4. **Kalibrasi Sensor**
   - Sesuaikan nilai `MOISTURE_DRY_VALUE` dan `MOISTURE_WET_VALUE` di file config.h
   - Lakukan pengukuran pada tanah kering dan tanah basah untuk kalibrasi yang akurat

## Selenoid Valve dan Pompa

1. **Persiapan Selenoid Valve**
   - Selenoid valve 12V memiliki 2 pin: (+) dan (-)
   - Pastikan rating valve sesuai dengan tekanan air yang akan digunakan

2. **Koneksi Selenoid Valve**
   - Hubungkan (+) selenoid valve ke pin NO (Normally Open) relay
   - Hubungkan (-) selenoid valve ke GND power supply
   - Hubungkan COM relay ke 12V power supply

3. **Pemasangan Selang**
   - Pasang selang input ke sisi input selenoid valve
   - Pasang selang output ke sisi output selenoid valve
   - Pasang sprinkler di ujung selang output
   - Pastikan semua sambungan rapat dan tidak bocor

4. **Koneksi Pompa Air**
   - Hubungkan (+) pompa air ke pin NO2 relay module
   - Hubungkan (-) pompa air ke GND power supply
   - Hubungkan selang input pompa ke sumber air
   - Hubungkan selang output pompa ke cabang selang untuk kedua selenoid valve

## Kamera Setup

1. **Persiapan Kamera**
   - Jika menggunakan Raspberry Pi Camera:
     - Buka port kamera CSI pada Raspberry Pi dengan hati-hati
     - Pasang kabel ribbon kamera dengan benar (sisi biru menghadap ke Ethernet port)
     - Kencangkan pengunci kabel ribbon
   - Jika menggunakan webcam USB:
     - Hubungkan webcam ke port USB Raspberry Pi
     - Pastikan webcam sudah terdeteksi dengan perintah `lsusb` di terminal

2. **Posisi Kamera**
   - Pasang kamera menghadap ke tanaman target
   - Atur jarak dan sudut kamera untuk mendapatkan gambar yang jelas
   - Gunakan mounting bracket jika diperlukan
   - Lindungi kamera dari air dan sinar matahari langsung

3. **Konfigurasi Kamera**
   - Aktifkan kamera pada Raspberry Pi dengan `sudo raspi-config`
   - Pilih "Interface Options" > "Camera" > "Enable"
   - Uji kamera dengan perintah `raspistill -o test.jpg`
   - Sesuaikan parameter kamera seperti resolusi dan kecerahan di `config.py`

## Tips Pemasangan di Lapangan

1. **Perlindungan dari Cuaca**
   - Pastikan semua komponen elektronik terlindungi dalam box tahan air
   - Gunakan sealant silikon untuk menutup lubang kabel
   - Posisikan box pada ketinggian untuk menghindari genangan air
   - Tambahkan desicant (silica gel) di dalam box untuk mengurangi kelembaban

2. **Manajemen Kabel**
   - Gunakan kabel yang kuat dan tahan air untuk instalasi outdoor
   - Lindungi kabel dengan conduit/pelindung kabel
   - Kuburkan kabel di dalam tanah atau pasang di atas tanah dengan rapi
   - Beri label pada setiap kabel untuk memudahkan troubleshooting

3. **Power Management**
   - Gunakan power supply yang stabil dan memadai
   - Pertimbangkan penggunaan UPS untuk mengatasi pemadaman listrik
   - Opsional: Tambahkan solar panel dan baterai untuk sistem off-grid
   - Pasang surge protector untuk melindungi dari lonjakan listrik

4. **Penempatan Sensor dan Sprinkler**
   - Letakkan sensor kelembaban tanah di dekat akar tanaman
   - Pastikan sensor tidak terlalu dekat dengan sprinkler (untuk pengukuran yang akurat)
   - Atur posisi sprinkler untuk mendapatkan cakupan penyiraman yang merata
   - Hindari posisi sensor di tempat yang tergenang air

5. **Pemeliharaan Rutin**
   - Periksa koneksi kabel secara berkala
   - Bersihkan sensor kelembaban tanah dari kotoran atau korosi
   - Periksa selenoid valve dari kebocoran atau penyumbatan
   - Periksa dan bersihkan kamera dari kotoran dan debu
   - Pastikan box pelindung tetap kedap air

## Troubleshooting Hardware

1. **Sensor Kelembaban Tidak Akurat**
   - Periksa koneksi kabel sensor
   - Pastikan sensor terpasang dengan benar di tanah
   - Kalibrasi ulang sensor dengan mengukur nilai ADC pada kondisi kering dan basah
   - Ganti sensor jika terdapat korosi

2. **Selenoid Valve Tidak Berfungsi**
   - Periksa koneksi relay dan selenoid valve
   - Ukur tegangan pada selenoid valve saat aktif (harus ~12V)
   - Periksa apakah relay berfungsi (terdengar suara 'klik' saat aktivasi)
   - Periksa tekanan air yang mencukupi

3. **ESP32 Sering Restart**
   - Periksa power supply (tegangan harus stabil 5V)
   - Pastikan tidak ada koneksi yang short circuit
   - Periksa apakah ESP32 tidak terlalu panas
   - Reset ke firmware default dan upload kode kembali

4. **Kamera Tidak Berfungsi**
   - Periksa koneksi kabel kamera
   - Pastikan kamera sudah diaktifkan di raspi-config
   - Uji kamera dengan perintah terminal
   - Periksa permissions pada file dan direktori kamera

5. **Koneksi WiFi Tidak Stabil**
   - Pasang ESP32 lebih dekat dengan router/access point
   - Gunakan range extender jika diperlukan
   - Pertimbangkan untuk menggunakan antena eksternal pada ESP32
   - Periksa interferensi dari perangkat elektronik lain

## Referensi Pin dan Koneksi

### Raspberry Pi 4 GPIO Pinout

```
+-----+-----+---------+------+---+---Pi 4B--+---+------+---------+-----+-----+
| BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
+-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
|     |     |    3.3V |      |   |  1 || 2  |   |      | 5V      |     |     |
|   2 |   8 |   SDA.1 | ALT0 | 1 |  3 || 4  |   |      | 5V      |     |     |
|   3 |   9 |   SCL.1 | ALT0 | 1 |  5 || 6  |   |      | GND     |     |     |
|   4 |   7 | GPIO. 7 |   IN | 1 |  7 || 8  | 1 | ALT5 | TxD     | 15  | 14  |
|     |     |     GND |      |   |  9 || 10 | 1 | ALT5 | RxD     | 16  | 15  |
|  17 |   0 | GPIO. 0 |   IN | 0 | 11 || 12 | 0 | IN   | GPIO. 1 | 1   | 18  |
|  27 |   2 | GPIO. 2 |   IN | 0 | 13 || 14 |   |      | GND     |     |     |
|  22 |   3 | GPIO. 3 |   IN | 0 | 15 || 16 | 0 | IN   | GPIO. 4 | 4   | 23  |
|     |     |    3.3V |      |   | 17 || 18 | 0 | IN   | GPIO. 5 | 5   | 24  |
|  10 |  12 |    MOSI | ALT0 | 0 | 19 || 20 |   |      | GND     |     |     |
|   9 |  13 |    MISO | ALT0 | 0 | 21 || 22 | 0 | IN   | GPIO. 6 | 6   | 25  |
|  11 |  14 |    SCLK | ALT0 | 0 | 23 || 24 | 1 | OUT  | CE0     | 10  | 8   |
|     |     |     GND |      |   | 25 || 26 | 1 | OUT  | CE1     | 11  | 7   |
|   0 |  30 |   SDA.0 |   IN | 1 | 27 || 28 | 1 | IN   | SCL.0   | 31  | 1   |
|   5 |  21 | GPIO.21 |   IN | 1 | 29 || 30 |   |      | GND     |     |     |
|   6 |  22 | GPIO.22 |   IN | 1 | 31 || 32 | 0 | IN   | GPIO.26 | 26  | 12  |
|  13 |  23 | GPIO.23 |   IN | 0 | 33 || 34 |   |      | GND     |     |     |
|  19 |  24 | GPIO.24 |   IN | 0 | 35 || 36 | 0 | IN   | GPIO.27 | 27  | 16  |
|  26 |  25 | GPIO.25 |   IN | 0 | 37 || 38 | 0 | IN   | GPIO.28 | 28  | 20  |
|     |     |     GND |      |   | 39 || 40 | 0 | IN   | GPIO.29 | 29  | 21  |
+-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
```

### ESP32 DevKit Pinout

```
                  +---------------------+
                  |              RST GND|
                  |     NC          SVP|
                  |     NC          SVN|
                  |     34           32|
                  |     35           33|
                  |     32           25|
                  |     33           26|
                  |     25           27|
                  |     26           14|
                  |     27           12|
                  |     14           GND|
                  |     12           13|
                  |    GND           D2|
                  |     13           D3|
                  |     D2          CMD|
                  |     D3          5V |
       ESP32      +---------------------+
    Development
       Board
```

### Spesifikasi Sensor dan Aktuator

**Sensor Kelembaban Tanah**
- Tegangan kerja: 3.3V-5V
- Output: Analog (0-4095 pada ESP32)
- Nilai indikasi:
  - ~4095: Sangat kering
  - ~1500: Dalam air
  - Nilai tengah: Kelembaban sedang

**Selenoid Valve**
- Tegangan kerja: 12V DC
- Arus: ~300-500mA
- Jenis: Normally Closed (NC)
- Maksimum tekanan air: 0.8MPa (sesuaikan dengan spesifikasi aktual)

**Relay Module**
- Tegangan kontrol: 3.3V/5V
- Tegangan switching: hingga 250V AC / 30V DC
- Arus switching: hingga 10A