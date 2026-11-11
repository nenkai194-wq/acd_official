# Panduan Deploy Gratis (Rp 0) & Menghubungkan Domain `acd.co.id`

Dokumen ini disiapkan khusus agar website **PT. Aksara Cipta Digital (ACD)** dapat langsung online di internet menggunakan domain sendiri (`acd.co.id`) **tanpa harus menyewa hosting berbayar** terlebih dahulu.

---

## Opsi A: Hosting Gratis di Cloud (`Render.com` / `Koyeb`) + Custom Domain (Disarankan Jika Tanpa PC Menyala 24 Jam)

Repository ini sudah dilengkapi file **`render.yaml`** dan **`Procfile`**, sehingga siap di-deploy dalam hitungan menit:

1. **Daftar / Login Gratis** ke [Render.com](https://render.com) atau [Koyeb.com](https://www.koyeb.com) menggunakan akun GitHub (`nenkai194-wq`).
2. Pilih **New > Blueprint** (di Render) atau **Create Web Service** dan hubungkan ke repository **`acd_official` (`main`)**.
3. Konfigurasi build & environment (`SECRET_KEY`, `FLASK_DEBUG=False`, `SESSION_COOKIE_SECURE=True`, `gunicorn wsgi:app`, `/health`) akan terbaca otomatis dari `render.yaml` / `Procfile`.
4. **Hubungkan Domain (`acd.co.id`)**:
   - Di menu **Settings > Custom Domains** Render/Koyeb, tambahkan `acd.co.id` dan `www.acd.co.id`.
   - Salin record DNS (`CNAME` / `A`) yang diberikan lalu masukkan ke DNS Panel registrar domain Anda (atau gunakan Cloudflare DNS Gratis). SSL HTTPS otomatis aktif.
5. **Agar Server Gratis Tidak "Tidur" (*Sleep*)**:
   - Daftar gratis di [UptimeRobot.com](https://uptimerobot.com), tambahkan monitor HTTP(s) ke `https://acd.co.id/health` setiap **5 menit**.

> **Catatan Penting Mode Gratis Cloud**:
> - Seluruh pesan client dari form website akan **tetap langsung masuk ke WhatsApp `+62 852-8789-8937`** dengan normal.
> - Disk free-tier pada Render/Koyeb akan reset ke data `acd_database.sqlite` yang ada di GitHub setiap kali ada redeploy. Jika ingin edit konten permanen sebelum punya VPS, edit dulu di lokal lalu `git push` atau nanti sambungkan ke VPS lokal.

---

## Opsi B: Hosting Rp 0 Pakai Laptop/PC Sendiri + Domain `acd.co.id` (`Cloudflare Tunnel`)

Jika website ingin berjalan 100% penuh dengan **database SQLite permanen** tanpa batas *sleep*:
1. Pindahkan DNS nameserver domain `acd.co.id` ke akun **Cloudflare (Free Plan)**.
2. Jalankan website Flask (`python app.py` atau Waitress) di PC/Laptop pada port `5000`.
3. Pasang **Cloudflare Tunnel (`cloudflared`)** dan arahkan hostname `acd.co.id` -> `http://127.0.0.1:5000`.
4. Website langsung aktif di `https://acd.co.id` dengan HTTPS Cloudflare Gratis (syarat: PC harus dalam keadaan menyala saat diakses).

---

## Checklist Final Setelah Website Online (3% Terakhir)

1. **Ubah Password & PIN Admin Default**:
   - Masuk ke `https://acd.co.id/admin`, login, lalu masuk ke menu **Pengaturan Website** untuk mengganti password dan 6-digit PIN Master (`555556`) demi keamanan penuh.
2. **Daftarkan ke Google Search Console**:
   - Buka [Google Search Console](https://search.google.com/search-console), verifikasi domain `acd.co.id` dan tempel kode verifikasi di menu admin **Optimasi SEO**.
   - Submit sitemap URL: `https://acd.co.id/sitemap.xml`.
3. **Uji Coba Pengiriman WhatsApp**:
   - Buka `https://acd.co.id/kontak` dan Kalkulator di beranda, coba kirim pesan uji coba, pastikan otomatis membuka WhatsApp ke `+62 852-8789-8937`.
