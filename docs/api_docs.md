# Smart Farming API Documentation

Dokumen ini menjelaskan API yang digunakan dalam sistem Smart Farming untuk komunikasi antara berbagai komponen.

## Daftar Isi

- [Endpoint API](#endpoint-api)
- [Format Data](#format-data)
- [Autentikasi](#autentikasi)
- [Sensor Data API](#sensor-data-api)
- [Command API](#command-api)
- [Web Interface API](#web-interface-api)
- [Error Handling](#error-handling)
- [Contoh Penggunaan](#contoh-penggunaan)

## Endpoint API

Server Raspberry Pi menyediakan endpoint berikut:

| Endpoint | Metode | Deskripsi |
|----------|--------|------------|
| `/sensor-data` | POST | Menerima data sensor dari node ESP32 |
| `/node-command/{node_id}` | GET | Node ESP32 mengambil perintah terbaru |
| `/api/data` | GET | Mendapatkan data terbaru dari semua sensor |
| `/api/history` | GET | Mendapatkan data historis |
| `/api/maturity` | GET | Mendapatkan hasil deteksi kematangan terbaru |
| `/api/manual-control` | POST | Mengirim perintah kontrol manual |
| `/api/capture` | POST | Memicu pengambilan gambar dan deteksi kematangan |
| `/api/images/{filename}` | GET | Mengambil gambar yang tersimpan |

## Format Data

### Sensor Data (ESP32 -> Server)

```json
{
  "node_id": "node1",
  "soil_moisture": 45.7,
  "valve_status": false,
  "battery": 100
}
```

Fields:
- `node_id` (string): ID unik dari node
- `soil_moisture` (float): Nilai kelembaban tanah (0-100%)
- `valve_status` (boolean): Status valve (true = ON, false = OFF)
- `battery` (integer): Level baterai (0-100%) - opsional

### Command Data (Server -> ESP32)

```json
{
  "valve_command": true
}
```

Fields:
- `valve_command` (boolean): Perintah valve (true = ON, false = OFF)

### Latest Data Response (Server -> Web Interface)

```json
{
  "soil_moisture": {
    "node1": {
      "moisture": 45.7,
      "valve": false,
      "timestamp": "2025-04-13T10:30:45"
    },
    "node2": {
      "moisture": 67.2,
      "valve": true,
      "timestamp": "2025-04-13T10:30:30"
    }
  },
  "maturity": {
    "image_path": "capture_20250413_103015.jpg",
    "maturity_class": "semi_mature",
    "confidence": 0.85,
    "predictions": {
      "immature": 0.1,
      "semi_mature": 0.85,
      "mature": 0.05
    },
    "timestamp": "2025-04-13T10:30:15"
  },
  "timestamp": "2025-04-13T10:31:00"
}
```

### Historical Data Response

```json
{
  "soil_moisture": {
    "node1": [
      {
        "moisture": 45.7,
        "valve": false,
        "timestamp": "2025-04-13T10:30:45"
      },
      // ... more entries
    ],
    "node2": [
      // ... entries
    ]
  },
  "maturity": [
    {
      "image_path": "capture_20250413_103015.jpg",
      "maturity_class": "semi_mature",
      "confidence": 0.85,
      "timestamp": "2025-04-13T10:30:15"
    },
    // ... more entries
  ],
  "days": 7,
  "start_date": "2025-04-06T00:00:00",
  "end_date": "2025-04-13T10:31:00"
}
```

## Autentikasi

Untuk versi awal, sistem tidak mengimplementasikan autentikasi formal. Untuk penggunaan di lingkungan produksi, disarankan untuk menambahkan:

1. Autentikasi API key untuk komunikasi ESP32
2. Login berbasis token untuk web interface

## Sensor Data API

### Send Sensor Data

Endpoint: `/sensor-data`  
Method: POST  
Description: Digunakan oleh node ESP32 untuk mengirim data sensor kelembaban tanah dan status valve.

**Request Body:**
```json
{
  "node_id": "node1",
  "soil_moisture": 45.7,
  "valve_status": false,
  "battery": 100
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Data received"
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Incomplete data"
}
```

## Command API

### Get Node Command

Endpoint: `/node-command/{node_id}`  
Method: GET  
Description: Digunakan oleh node ESP32 untuk mengambil perintah terbaru untuk valve.

**Path Parameters:**
- `node_id` (string): ID unik dari node (misalnya "node1", "node2")

**Response:**
```json
{
  "valve_command": true
}
```

## Web Interface API

### Get Latest Data

Endpoint: `/api/data`  
Method: GET  
Description: Mendapatkan data terbaru dari semua sensor dan status sistem.

**Response:**
```json
{
  "soil_moisture": {
    "node1": {
      "moisture": 45.7,
      "valve": false,
      "timestamp": "2025-04-13T10:30:45"
    },
    "node2": {
      "moisture": 67.2,
      "valve": true,
      "timestamp": "2025-04-13T10:30:30"
    }
  },
  "maturity": {
    "image_path": "capture_20250413_103015.jpg",
    "maturity_class": "semi_mature",
    "confidence": 0.85,
    "predictions": {
      "immature": 0.1,
      "semi_mature": 0.85,
      "mature": 0.05
    },
    "timestamp": "2025-04-13T10:30:15"
  },
  "timestamp": "2025-04-13T10:31:00"
}
```

### Get Historical Data

Endpoint: `/api/history`  
Method: GET  
Description: Mendapatkan data historis untuk semua sensor.

**Query Parameters:**
- `days` (integer, optional): Jumlah hari untuk data historis (default: 7)

**Response:**
Lihat [Historical Data Response](#historical-data-response)

### Get Latest Maturity Detection

Endpoint: `/api/maturity`  
Method: GET  
Description: Mendapatkan hasil deteksi kematangan terbaru.

**Response:**
```json
{
  "image_path": "capture_20250413_103015.jpg",
  "maturity_class": "semi_mature",
  "confidence": 0.85,
  "predictions": {
    "immature": 0.1,
    "semi_mature": 0.85,
    "mature": 0.05
  },
  "timestamp": "2025-04-13T10:30:15"
}
```

### Manual Control

Endpoint: `/api/manual-control`  
Method: POST  
Description: Mengirim perintah kontrol manual ke node tertentu.

**Request Body:**
```json
{
  "node_id": "node1",
  "command": "valve",
  "value": true
}
```

**Response:**
```json
{
  "status": "success"
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Unknown command"
}
```

### Trigger Camera Capture

Endpoint: `/api/capture`  
Method: POST  
Description: Memicu pengambilan gambar dan deteksi kematangan.

**Response:**
```json
{
  "status": "success",
  "image": "capture_20250413_103015.jpg",
  "result": {
    "maturity_class": "semi_mature",
    "confidence": 0.85,
    "predictions": {
      "immature": 0.1,
      "semi_mature": 0.85,
      "mature": 0.05
    }
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Failed to capture image"
}
```

### Get Image

Endpoint: `/api/images/{filename}`  
Method: GET  
Description: Mengambil gambar yang tersimpan.

**Path Parameters:**
- `filename` (string): Nama file gambar

**Response:**
Binary image data (JPEG/PNG)

**Error Response:**
Status code 404 jika gambar tidak ditemukan

## Error Handling

Semua API mengembalikan kode status HTTP yang sesuai:

- 200 OK: Request berhasil
- 400 Bad Request: Parameter tidak valid atau tidak lengkap
- 404 Not Found: Resource tidak ditemukan
- 500 Internal Server Error: Error server

Untuk error, respons berisi:
```json
{
  "status": "error",
  "message": "Deskripsi error"
}
```

## Contoh Penggunaan

### ESP32 Mengirim Data Sensor

```
POST /sensor-data HTTP/1.1
Host: 192.168.1.100:5000
Content-Type: application/json

{
  "node_id": "node1",
  "soil_moisture": 45.7,
  "valve_status": false,
  "battery": 100
}
```

### ESP32 Mengambil Perintah

```
GET /node-command/node1 HTTP/1.1
Host: 192.168.1.100:5000
```

### Web Interface Mengambil Data Terbaru

```
GET /api/data HTTP/1.1
Host: 192.168.1.100:5000
```

### Web Interface Mengaktifkan Valve Secara Manual

```
POST /api/manual-control HTTP/1.1
Host: 192.168.1.100:5000
Content-Type: application/json

{
  "node_id": "node1",
  "command": "valve",
  "value": true
}
```