# Report: Pub-Sub Log Aggregator

## **Bab 1 – Pendahuluan**

Sistem **Pub-Sub Log Aggregator** dirancang untuk mengelola aliran event dari berbagai sumber.  
Dalam arsitektur ini, setiap komponen dapat **mem-publish** event yang kemudian disimpan dan diolah oleh server aggregator. Sistem ini membantu proses **monitoring**, **debugging**, dan **analisis data real-time**.

---

## **Bab 2 – Rumusan Masalah**

Bagaimana membangun sistem agregator yang dapat menerima, menyimpan, dan menyajikan data event secara efisien dalam konteks **publish–subscribe pattern** menggunakan **FastAPI** dan **Docker**.

---

## **Bab 3 – Tujuan**

- Mengimplementasikan pola publish–subscribe berbasis REST API.
- Menerapkan **FastAPI** untuk penanganan endpoint secara asinkron.
- Membangun arsitektur kontainer menggunakan **Docker**.
- Menyediakan endpoint statistik untuk evaluasi data event.

---

## **Bab 4 – Landasan Teori**

- **Publish–Subscribe Model:** Pola komunikasi di mana publisher mengirim pesan tanpa mengetahui subscriber secara langsung.
- **FastAPI:** Framework Python modern untuk API asinkron dengan performa tinggi.
- **Docker:** Platform containerization yang memungkinkan aplikasi dijalankan secara konsisten di berbagai lingkungan.
- **Unit Testing (pytest):** Digunakan untuk memastikan setiap fungsi bekerja sesuai ekspektasi.

---

## **Bab 5 – Desain Sistem**

### **Arsitektur**

1. **Publisher:** Mengirim data event ke endpoint `/publish`.
2. **Aggregator (FastAPI):** Menyimpan event secara in-memory dan mencatat metadata.
3. **Subscriber (opsional):** Dapat dikembangkan untuk menerima notifikasi event.
4. **Storage/Stats Module:** Menghitung total dan distribusi event berdasarkan topik.

### **Diagram Alur (Sederhana)**

Publisher → POST /publish → Aggregator → Memory Storage
↳ GET /events → Client
↳ GET /stats → Admin/Monitoring

---

## **Bab 6 – Implementasi**

- Proyek dikemas menggunakan **Dockerfile** dengan base image `python:3.10-slim`.
- Dependensi diatur melalui `requirements.txt`.
- Endpoint diuji menggunakan **pytest** di folder `tests/`.
- Server dijalankan pada port `8080` di container.

---

## **Bab 7 – Hasil dan Kesimpulan**

Sistem berhasil menerima dan mengagregasi event dari berbagai sumber.  
Endpoint `/stats` memberikan informasi agregasi yang relevan tanpa perlu database eksternal.  
Dengan pendekatan berbasis Docker, deployment menjadi lebih mudah dan konsisten di berbagai platform.

---

## **Daftar Pustaka**

1. FastAPI Documentation – https://fastapi.tiangolo.com/
2. Docker Official Docs – https://docs.docker.com/
3. Pub/Sub Design Patterns – Microsoft Architecture Center
4. pytest Documentation – https://docs.pytest.org/
