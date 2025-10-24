
# Pub-Sub Log Aggregator

Proyek ini merupakan implementasi sistem **Publish–Subscribe Log Aggregator** berbasis **FastAPI**.  
Sistem ini berfungsi sebagai pusat pengumpulan (aggregator) event dari berbagai sumber melalui endpoint publik, menyimpannya, dan menyediakan ringkasan statistik sederhana.

---

## Fitur Utama

- **Publish Event:** Menambahkan event baru dengan payload JSON.
- **Retrieve Events:** Melihat semua event yang telah diterima.
- **View Statistics:** Mendapatkan ringkasan jumlah event berdasarkan kategori/topik.

---

## Struktur Proyek

uts-aggregator/
│
├── src/ # Kode utama aplikasi (FastAPI)
│ ├── main.py # Entry point API
│ ├── models/ # Struktur data & schema
│ ├── services/ # Logika penyimpanan / aggregator
│ └── utils/ # Helper functions (opsional)
│
├── tests/ # Unit tests
│ └── test_api.py
│
├── requirements.txt # Dependensi Python
├── Dockerfile # Konfigurasi Docker
├── docker-compose.yml # (opsional) konfigurasi multi-service
├── README.md # Dokumentasi proyek (file ini)
└── report.md # Laporan penjelasan desain sistem

---

## Persyaratan

- **Python 3.10+**
- **Docker & Docker Compose**
- **FastAPI**
- **Uvicorn**
- **pytest** (untuk testing)

---

## Cara Build & Run

### 🔹 1. Menjalankan dengan Docker

```bash
# Build image
docker build -t uts-aggregator .

# Jalankan container
docker run -d -p 8080:8080 uts-aggregator

2. (Opsional) Jalankan dengan Docker Compose
docker-compose up --build

Aplikasi akan berjalan di:
👉 http://127.0.0.1:8080

---
Asumsi Sistem

Event yang dikirim ke /publish memiliki format JSON yang konsisten.

Tidak ada autentikasi (public API untuk keperluan simulasi).

Penyimpanan dilakukan secara in-memory (bisa dikembangkan ke database jika dibutuhkan).

---
Endpoint API
POST /publish

Publikasikan event baru ke sistem.

Contoh Request:
{
  "event_id": "evt-12345",
  "payload": {
    "user_id": 42,
    "action": "login"
  },
  "source": "frontend-app",
  "timestamp": "2025-10-22T10:30:00Z",
  "topic": "user.activity"
}

{"status": "success", "message": "Event received"}

---
GET /events

Ambil semua event yang tersimpan.
[
  {
    "event_id": "evt-12345",
    "topic": "user.activity",
    "timestamp": "2025-10-22T10:30:00Z"
  }
]

---
GET /stats
Melihat statistik event berdasarkan topik atau sumber.

Response:
{
  "total_events": 10,
  "topics": {
    "user.activity": 6,
    "system.error": 4
  }
}

Testing

Jalankan unit test:
pytest





Nama: Arifia Dyah Sulistyani
NIM : 11221061
```
=======
# UTS-Sister
>>>>>>> ff174ecc67d4d1dad4d9cdb54e5ac12de8807100
