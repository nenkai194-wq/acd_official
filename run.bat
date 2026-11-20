@echo off
title PT Aksara Cipta Digital (ACD Official)
echo =====================================================================
echo    PT AKSARA CIPTA DIGITAL (ACD OFFICIAL)
echo    "Solusi Software Inovatif & Transformasi Digital Terpercaya"
echo =====================================================================
echo.
echo [!] Pastikan HP/Tablet/PC lain terhubung ke Wi-Fi / Jaringan yang sama.
echo.
echo * Akses di PC ini        : http://127.0.0.1:5000
echo * Akses di HP / Tablet   : http://192.168.2.106:5000
echo * Portal Admin (Dapur)   : http://192.168.2.106:5000/dapur/login
echo * Modul Transaksi & Keu  : http://192.168.2.106:5000/dapur/transaksi (atau http://192.168.2.106:5000/transaksi)
echo   - Tahap 1: User 'admin', Pass 'acd2026' (atau 'Cipta!2345'), & Kode CAPTCHA
echo   - Tahap 2: PIN Otorisasi Ganda 2FA '555556'
echo.
echo =====================================================================
echo Menjalankan server Flask... Tekan Ctrl+C untuk berhenti.
echo =====================================================================
python app.py
pause
