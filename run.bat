@echo off
title PT. Aksara Cipta Digital (ACD Official)
echo =====================================================================
echo    PT. AKSARA CIPTA DIGITAL (ACD OFFICIAL)
echo    "Solusi Software Inovatif & Transformasi Digital Terpercaya"
echo =====================================================================
echo.
echo [!] Pastikan HP/Tablet/PC lain terhubung ke Wi-Fi / Jaringan yang sama.
echo.
echo * Akses di PC ini        : http://127.0.0.1:5000
echo * Akses di HP / Tablet   : http://192.168.2.105:5000
echo * Portal Admin           : http://192.168.2.105:5000/admin/login
echo   - User: admin
echo   - Pass: acd2025super
echo   - CAPTCHA : Masukkan kode gambar pada form login
echo.
echo =====================================================================
echo Menjalankan server Flask... Tekan Ctrl+C untuk berhenti.
echo =====================================================================
python app.py
pause
