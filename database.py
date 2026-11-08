import sqlite3
import json
from datetime import datetime
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Inquiries table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        company TEXT,
        service_type TEXT NOT NULL,
        budget_range TEXT,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'Baru',
        notes TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Ensure ip_address column exists if table was previously created
    cursor.execute("PRAGMA table_info(inquiries)")
    cols = [col[1] for col in cursor.fetchall()]
    if 'ip_address' not in cols:
        cursor.execute("ALTER TABLE inquiries ADD COLUMN ip_address TEXT")

    # Table for tracking WhatsApp message click events (Rate Limiting anti-spam)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wa_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Services table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        subtitle TEXT,
        icon TEXT,
        summary TEXT,
        features TEXT, -- JSON
        tech_stack TEXT, -- JSON
        benefits TEXT, -- JSON
        is_featured INTEGER DEFAULT 1,
        is_published INTEGER DEFAULT 1
    )
    ''')

    # Portfolios table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS portfolios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        client_name TEXT NOT NULL,
        client_type TEXT NOT NULL, -- BUMN, Pemerintahan, Swasta, Industri
        year TEXT NOT NULL,
        summary TEXT,
        challenge TEXT,
        solution TEXT,
        impact TEXT,
        tech_stack TEXT, -- JSON
        image_url TEXT,
        metrics TEXT -- JSON
    )
    ''')

    # Blog posts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blog_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        author TEXT NOT NULL,
        read_time TEXT DEFAULT '5 Menit',
        summary TEXT,
        content TEXT,
        tags TEXT,
        image_url TEXT,
        published_date TEXT
    )
    ''')

    # Testimonials table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS testimonials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        client_title TEXT NOT NULL,
        company_name TEXT NOT NULL,
        content TEXT NOT NULL,
        rating INTEGER DEFAULT 5,
        project_name TEXT
    )
    ''')

    # Careers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS careers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        department TEXT NOT NULL,
        location TEXT DEFAULT 'Jakarta / Yogyakarta / Hybrid',
        job_type TEXT DEFAULT 'Full-time',
        experience TEXT,
        description TEXT,
        requirements TEXT, -- JSON
        responsibilities TEXT, -- JSON
        is_published INTEGER DEFAULT 1
    )
    ''')

    # FAQs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS faqs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        sort_order INTEGER DEFAULT 0
    )
    ''')

    # Admin Security & Audit Logs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_security_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT NOT NULL,
        username TEXT,
        event_type TEXT NOT NULL,
        details TEXT,
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Login Lockouts & Rate Limiting Table (Anti Brute-Force)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS login_lockouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT UNIQUE NOT NULL,
        failed_count INTEGER DEFAULT 1,
        locked_until TIMESTAMP,
        last_attempt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Settings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')

    # Seed default settings if empty
    default_settings = [
        ('company_name', Config.COMPANY_NAME),
        ('company_short_name', Config.COMPANY_SHORT_NAME),
        ('company_tagline', Config.COMPANY_TAGLINE),
        ('company_subtagline', Config.COMPANY_SUBTAGLINE),
        ('company_email', Config.COMPANY_EMAIL),
        ('company_consultation_email', Config.COMPANY_CONSULTATION_EMAIL),
        ('company_phone', Config.COMPANY_PHONE),
        ('company_whatsapp', Config.COMPANY_WHATSAPP),
        ('company_address', Config.COMPANY_ADDRESS),
        ('company_branch', ''),
        ('admin_username', Config.ADMIN_USERNAME),
        ('admin_password', Config.ADMIN_PASSWORD),
        ('admin_pin', Config.ADMIN_PIN),
        ('security_lockout_minutes', '15'),
        ('security_max_attempts', '3'),
        ('footer_brand_name', 'AKSARA CIPTA DIGITAL'),
        ('footer_brand_tagline', 'IT Consultant - AI, Software Developer'),
        ('footer_about', 'PT. Aksara Cipta Digital adalah perusahaan konsultan IT dan software house yang berpengalaman membangun ratusan aplikasi terbaik untuk berbagai sektor bisnis swasta, BUMN, dan institusi pemerintahan di seluruh Indonesia.'),
        ('footer_address_main', 'Gedung Cyber 2 Tower Lt. 18, Jl. H. R. Rasuna Said Blok X-5 No. 13, Kuningan Barat, Jakarta Selatan 12950'),
        ('footer_address_branch', ''),
        ('footer_phone', '+62 21 8299 8765'),
        ('footer_email', 'info@acd.co.id'),
        ('footer_whatsapp', '6281288882510'),
        ('footer_col2_title', 'Aplikasi & Website'),
        ('footer_col2_links', 'Mobile Apps (Android & iOS) | /layanan/mobile-apps\nWeb Base Apps | /layanan/sistem-informasi\nWebsite Korporat | /layanan/website-korporat\nGeographic Information System (GIS) | /layanan/gis-geoportal\nIntegrasi Sistem & API | /layanan/integrasi-sistem\nSemua Aplikasi & Website \u2192 | /layanan/kategori/Aplikasi%20&%20Website'),
        ('footer_col3_title', 'Aplikasi Bisnis ERP'),
        ('footer_col3_links', 'HRIS / Kepegawaian | /layanan/erp-hris-kepegawaian\nPresensi & Geofencing | /layanan/erp-presensi-absensi\nPayroll & Pajak PPh21 | /layanan/erp-payroll-penggajian\nAkuntansi & Keuangan | /layanan/erp-accounting-keuangan\nAsset Management | /layanan/erp-asset-management\nWarehouse Management | /layanan/erp-warehouse-management\nDocument Management | /layanan/erp-document-management\nDashboard Eksekutif | /layanan/erp-dashboard-eksekutif'),
        ('footer_col4_title', 'Aplikasi E-Gov'),
        ('footer_col4_links', 'Website Pemerintah Daerah | /layanan/egov-portal-daerah\ne-Data Sektoral SDI | /layanan/egov-data-sektoral\ne-Planning Internal & Pokir | /layanan/egov-e-planning-musrenbang\ne-Monev & e-SAKIP | /layanan/egov-e-monev-sakip\ne-Lapor & Pengaduan Warga | /layanan/egov-e-lapor-pengaduan\ne-Perizinan MPP TTE | /layanan/egov-e-perizinan-mpp'),
        ('footer_about_title', 'Tentang Kami'),
        ('footer_about_links', 'Profil Perusahaan ACD | /tentang-kami\nStudi Kasus & Portofolio | /portofolio\nKarir di ACD | /karir\nTanya Jawab (FAQ) | /faq'),
        ('footer_security_label', 'Standar Keamanan & Mutu:'),
        ('footer_badge1', 'ISO 27001 Certified'),
        ('footer_badge2', 'OWASP Top 10 Compliant'),
        ('footer_badge3', 'SLA 99.9% Uptime Support'),
        ('footer_support_text', 'Layanan Konsultasi & Aduan:'),
        ('footer_support_label', 'WhatsApp 24/7 Support'),
        ('footer_copyright', '\u00a9 2025 PT. Aksara Cipta Digital (acd.co.id). All rights reserved.'),
        ('footer_privacy_label', 'Kebijakan Privasi'),
        ('footer_privacy_url', '/tentang-kami'),
        ('footer_terms_label', 'Syarat & Ketentuan Layanan'),
        ('footer_terms_url', '/tentang-kami'),
        ('footer_consult_label', 'Hubungi Konsultan'),
        ('footer_consult_url', '/kontak'),
        ('contact_hero_badge', 'Hubungi Kami'),
        ('contact_hero_title', 'Konsultasi Gratis Rancang Bangun Software'),
        ('contact_hero_subtitle', 'Diskusikan kebutuhan aplikasi atau sistem perusahaan Anda dengan System Analyst senior kami. Kami siap memberikan masukan arsitektur dan estimasi anggaran tanpa biaya.'),
        ('contact_form_badge', 'FORMULIR KEBUTUHAN'),
        ('contact_form_title', 'Kirimkan Deskripsi Kebutuhan Anda'),
        ('contact_form_subtitle', 'Kami menghargai kerahasiaan data bisnis Anda (Non-Disclosure Agreement siap ditandatangani)'),
        ('contact_submit_btn', 'Kirim Formulir Konsultasi Gratis'),
        ('contact_wa_label', '+62 812-8888-2510 (Fast Response)'),
        ('contact_wa_number', '6281288882510'),
        ('contact_email', 'info@acd.co.id'),
        ('contact_phone', '+62 21 8299 8765'),
        ('contact_hours', 'Senin - Jumat: 08:30 - 17:00 WIB'),
        ('contact_address_main', 'Gedung Cyber 2 Tower Lt. 18, Jl. H. R. Rasuna Said Blok X-5 No. 13, Kuningan Barat, Jakarta Selatan 12950'),
        ('contact_address_branch', ''),
        ('contact_categories', 'Aplikasi Bisnis ERP (HRIS, Payroll, Akuntansi, Stok)\nAplikasi E-Government (Smart Governance / SPBE)\nMobile Apps (Android & iOS Native/Flutter)\nWeb Base App & Sistem Informasi Operasional\nWebsite Korporat & Portal Berita\nGIS & Geoportal Spasial\nIntegrasi Sistem & API Enterprise\nKonsultasi & Audit IT'),
        ('contact_budget_ranges', 'Di bawah Rp 50 Juta\nRp 50 Juta - Rp 150 Juta\nRp 150 Juta - Rp 300 Juta\n> Rp 300 Juta (Enterprise Scale)'),
        ('seo_meta_title', 'PT. Aksara Cipta Digital | IT Consultant - AI, Software Developer'),
        ('seo_meta_description', 'PT. Aksara Cipta Digital (ACD) adalah konsultan IT terkemuka dan software house spesialis arsitektur sistem ERP, E-Government, Mobile Apps, dan solusi kecerdasan buatan (AI) terpercaya di Indonesia.'),
        ('seo_meta_keywords', 'IT Consultant, Konsultan IT Jakarta, Software Developer Indonesia, Jasa Pembuatan Aplikasi, Jasa Sistem ERP, E-Government SPBE, AI Developer, GIS Geoportal, PT Aksara Cipta Digital, ACD'),
        ('seo_canonical_url', 'https://acd.co.id'),
        ('seo_author', 'PT. Aksara Cipta Digital'),
        ('seo_robots', 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1'),
        ('seo_og_title', 'PT. Aksara Cipta Digital - IT Consultant & Enterprise Software House'),
        ('seo_og_description', 'Solusi software inovatif, arsitektur sistem berkinerja tinggi, dan transformasi digital terpercaya untuk Korporasi Swasta, BUMN, dan Pemerintahan di seluruh Indonesia.'),
        ('seo_og_image', '/static/images/logo_acd_icon.png'),
        ('seo_og_type', 'website'),
        ('seo_twitter_card', 'summary_large_image'),
        ('seo_google_verification', ''),
        ('seo_bing_verification', ''),
        ('seo_google_analytics_id', ''),
        ('seo_gtm_id', ''),
        ('seo_organization_type', 'Corporation'),
        ('seo_geo_region', 'ID-JK'),
        ('seo_geo_placename', 'Jakarta Selatan'),
        ('seo_geo_position', '-6.2241;106.8315'),
    ]
    for k, v in default_settings:
        cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (k, v))

    conn.commit()
    conn.close()

def seed_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute('SELECT COUNT(*) FROM services')
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    print("Seeding database with ACD content mirroring JMC structure...")

    # --- SERVICES SEED ---
    services = [
        # 1. Aplikasi & Website
        (
            'mobile-apps',
            'Aplikasi & Website',
            'Jasa Pembuatan Mobile Apps (Android & iOS)',
            'Aplikasi mobile performa tinggi, responsif, dan interaktif untuk skalabilitas bisnis modern',
            'smartphone',
            'Solusi pengembangan aplikasi mobile native maupun multi-platform (Flutter, React Native) dengan standar keamanan tinggi dan UI/UX yang memanjakan pengguna.',
            json.dumps(['Pengembangan Android & iOS Native & Hybrid (Flutter/React Native)', 'Integrasi Payment Gateway, Push Notification & Realtime Tracking', 'Offline First Architecture & Local Data Encryption', 'Optimalisasi Battery & Memory Usage', 'Dukungan Publish ke Google Play Store & Apple App Store']),
            json.dumps(['Flutter', 'React Native', 'Kotlin', 'Swift', 'Node.js', 'Firebase', 'PostgreSQL']),
            json.dumps(['Jangkau jutaan pengguna aktif smartphone secara langsung', 'Proses transaksi lebih cepat dengan notifikasi instan', 'Meningkatkan loyalitas pelanggan melalui program retensi & reward'])
        ),
        (
            'sistem-informasi',
            'Aplikasi & Website',
            'Web Base Application & Sistem Informasi',
            'Sistem informasi terintegrasi untuk mengotomatiskan seluruh alur operasional bisnis',
            'globe',
            'Pengembangan aplikasi berbasis web khusus (custom tailored) yang dirancang untuk mengurai proses rumit menjadi dashboard operasional yang cepat dan efisien.',
            json.dumps(['Arsitektur Cloud-Native & Microservices', 'Manajemen Hak Akses Bertingkat (RBAC)', 'Audit Trail & Rekam Jejak Aktivitas Pengguna', 'Export/Import Multi-format (PDF, Excel, CSV, JSON)', 'API Terbuka untuk Integrasi Pihak Ketiga']),
            json.dumps(['Python/Flask/FastAPI', 'Laravel/PHP', 'React', 'Vue.js', 'PostgreSQL', 'Docker', 'Redis']),
            json.dumps(['Efisiensi waktu operasional hingga 65%', 'Transparansi data real-time antar departemen', 'Pengambilan keputusan berbasis data akurat'])
        ),
        (
            'website-korporat',
            'Aplikasi & Website',
            'Jasa Pembuatan Website Korporat & Portal',
            'Citra brand profesional dengan kecepatan loading tinggi dan optimalisasi SEO maksimal',
            'layout',
            'Website perusahaan modern dengan desain berkelas, keamanan tingkat lanjut (SSL, DDoS Protection), serta Content Management System (CMS) yang mudah dikelola.',
            json.dumps(['Desain UI/UX Eksklusif & Mobile-First', 'Optimalisasi On-Page SEO & Core Web Vitals', 'CMS Interaktif & Ramah Pengguna', 'Dukungan Multi-bahasa (Indonesia & English)', 'Keamanan Standar OWASP & SSL Grade A']),
            json.dumps(['Tailwind CSS', 'TypeScript', 'Next.js', 'WordPress Headless', 'FastAPI']),
            json.dumps(['Meningkatkan kredibilitas & otoritas brand di mata klien dan investor', 'Peringkat halaman teratas di pencarian Google', 'Lead generation formulir otomatis terhubung ke WhatsApp Sales'])
        ),
        (
            'gis-geoportal',
            'Aplikasi & Website',
            'Geographic Information System (GIS) & Geoportal',
            'Visualisasi spasial dan pemetaan aset berbasis koordinat geografis presisi tinggi',
            'map-pin',
            'Aplikasi pemetaan digital interaktif untuk monitoring persebaran aset wilayah, tata ruang kota, potensi sumber daya, serta logistik terpadu.',
            json.dumps(['Peta Tematik Multi-Layer & Clustering', 'Analisis Spasial & Polygon Overlay Geografis', 'Dukungan Standar Geospasial OGC (WMS, WFS, GeoJSON)', 'Pelacakan Armada & Surveyor Real-Time GPS', 'Dashboard Statistik Terintegrasi Peta']),
            json.dumps(['Leaflet.js', 'Mapbox GL', 'GeoServer', 'PostGIS', 'Python GeoPandas']),
            json.dumps(['Kemudahan inventarisasi dan monitoring aset fisik di seluruh penjuru negeri', 'Deteksi tumpang tindih lahan & izin tata ruang secara visual', 'Perencanaan pembangunan daerah berbasis spasial akurat'])
        ),
        (
            'integrasi-sistem',
            'Aplikasi & Website',
            'Integrasi Sistem & Enterprise API',
            'Hubungkan berbagai aplikasi lama (legacy) dan baru dalam satu ekosistem data yang harmonis',
            'layers',
            'Layanan interkoneksi sistem untuk menghilangkan silo data. Menggunakan Enterprise Service Bus (ESB) dan RESTful/GraphQL API berkecepatan tinggi.',
            json.dumps(['Pembangunan API Gateway Terpusat', 'Integrasi Single Sign-On (SSO) & OAuth2 / SAML', 'Sinkronisasi Database Antar Cabang Secara Real-Time', 'Koneksi dengan Core Banking, SAP, Oracle, atau Dukcapil', 'Monitoring Traffic API & Error Logging']),
            json.dumps(['Kong Gateway', 'RabbitMQ', 'Apache Kafka', 'REST API', 'GraphQL', 'Docker']),
            json.dumps(['Menghilangkan proses entri data berulang yang rawan human-error', 'Data antar departemen tersinkronisasi dalam hitungan detik', 'Menghemat investasi software lama tanpa perlu membangun dari nol'])
        ),

        # 2. Aplikasi Bisnis ERP
        (
            'erp-hris-kepegawaian',
            'Aplikasi Bisnis ERP',
            'ERP HRIS & Manajemen Kepegawaian',
            'Kelola talenta perusahaan dari rekrutmen, KPI kinerja, hingga jenjang karir dalam satu atap',
            'users',
            'Sistem Human Resource Information System (HRIS) komprehensif yang disesuaikan dengan regulasi ketenagakerjaan dan struktur organisasi perusahaan Anda.',
            json.dumps(['Database Karyawan Digital & Dokumen Elektronik', 'Manajemen Cuti, Izin, Lembur, dan Dinas Luar', 'Penilaian Kinerja KPI 360 Derajat & OKR', 'Modul Rekrutmen & Onboarding Digital', 'Struktur Organisasi & Riwayat Mutasi Promosi']),
            json.dumps(['PostgreSQL', 'Python', 'Vue.js', 'Redis', 'Docker']),
            json.dumps(['Memangkas beban administrasi HR hingga 70%', 'Evaluasi performa kerja karyawan objektif dan terukur', 'Kepatuhan mutlak terhadap regulasi UU Ketenagakerjaan'])
        ),
        (
            'erp-presensi-absensi',
            'Aplikasi Bisnis ERP',
            'Aplikasi Presensi Online & Geofencing (Absensi)',
            'Pencatatan kehadiran presisi dengan validasi radius lokasi GPS dan deteksi wajah anti-fake GPS',
            'check-circle',
            'Aplikasi absensi mobile terintegrasi untuk karyawan WFH, WFO, maupun tim lapangan dengan anti-spoofing kamera dan sinkronisasi real-time.',
            json.dumps(['Face Recognition dengan Liveness Detection', 'Radius Geofencing Koordinat Kantor & Project Site', 'Mode Offline Presensi untuk Area Susah Sinyal', 'Pengajuan Sakit & Tukar Shift Terpadu', 'Rekap Presensi Otomatis Siap Tarik ke Penggajian']),
            json.dumps(['OpenCV AI Face Match', 'Flutter', 'PostGIS', 'Node.js']),
            json.dumps(['Nol potensi manipulasi atau titip absen', 'Pemantauan lokasi staf lapangan secara transparan', 'Rekapitulasi otomatis tanpa input manual akhir bulan'])
        ),
        (
            'erp-payroll-penggajian',
            'Aplikasi Bisnis ERP',
            'Aplikasi Payroll & Perhitungan Pajak PPh 21',
            'Hitung gaji, tunjangan, lembur, BPJS Kesehatan, BPJS Ketenagakerjaan, dan PPh 21 TER otomatis',
            'dollar-sign',
            'Modul payroll cerdas yang mengkalkulasi komponen gaji rumit secara otomatis, menghasilkan slip gaji digital terenkripsi dan file transfer massal bank.',
            json.dumps(['Kalkulasi Otomatis PPh 21 Tarif Efektif Rata-rata (TER) Terbaru', 'Integrasi Pemotongan BPJS Ketenagakerjaan & BPJS Kesehatan', 'Generate Slip Gaji PDF dengan Password Terproteksi', 'Format Siap Transfer Bank (BCA, Mandiri, BNI, BRI, dll)', 'Audit Trail Pengeluaran Biaya Tenaga Kerja']),
            json.dumps(['Python Calculation Engine', 'PostgreSQL', 'ReportLab PDF', 'Encryption Module']),
            json.dumps(['Selesai hitung gaji ribuan karyawan dalam hitungan menit', 'Bebas dari denda keterlambatan atau salah hitung pajak PPh 21', 'Kerahasiaan gaji karyawan terjamin dengan enkripsi level perbankan'])
        ),
        (
            'erp-accounting-keuangan',
            'Aplikasi Bisnis ERP',
            'Aplikasi Akuntansi & Manajemen Keuangan',
            'Laporan keuangan standar PSAK/IFRS, arus kas, buku besar, dan neraca laba rugi real-time',
            'trending-up',
            'Sistem pencatatan akuntansi terintegrasi dari jurnal umum, otomatisasi faktur, rekonsiliasi bank, hingga laporan keuangan konsolidasi.',
            json.dumps(['Bagan Akun (Chart of Accounts) Fleksibel Multi-level', 'Jurnal Otomatis dari Transaksi Penjualan & Pembelian', 'Laporan Laba Rugi, Neraca, dan Arus Kas Real-time', 'Modul Piutang (AR) & Utang Dagang (AP) dengan Pengingat Jatuh Tempo', 'Rekonsiliasi Rekening Koran Bank Otomatis']),
            json.dumps(['PostgreSQL', 'Python Financial Engine', 'React', 'Export Engine']),
            json.dumps(['Kesehatan finansial perusahaan terpantau setiap detik', 'Penutupan buku bulanan (closing) lebih cepat dari 10 hari jadi 1 hari', 'Audit-ready untuk auditor eksternal dan otoritas pajak'])
        ),
        (
            'erp-asset-management',
            'Aplikasi Bisnis ERP',
            'Aplikasi Asset Management & Inventaris',
            'Lacak siklus hidup aset dari pengadaan, penempatan, depresiasi nilai, hingga jadwal servis berkala',
            'box',
            'Manajemen aset fisik dan non-fisik dengan pelabelan QR Code / Barcode / RFID untuk pencegahan kehilangan aset dan optimasi biaya perawatan.',
            json.dumps(['Kalkulasi Penyusutan Aset Otomatis (Garis Lurus & Saldo Menurun)', 'Pencetakan & Pemindaian QR Code / Barcode Aset via Smartphone', 'Penjadwalan Servis Preventif & Riwayat Perbaikan', 'Pencatatan Peminjaman & Pengembalian Aset Antar Divisi', 'Laporan Nilai Buku & Lokasi Fisik Terkini']),
            json.dumps(['PostgreSQL', 'Python', 'QR Code Generator', 'Mobile Scanner Support']),
            json.dumps(['Mencegah aset terbengkalai atau hilang tanpa jejak', 'Perpanjang masa pakai mesin dan peralatan melalui perawatan teratur', 'Transparansi nilai aset riil dalam neraca keuangan'])
        ),
        (
            'erp-warehouse-management',
            'Aplikasi Bisnis ERP',
            'Warehouse & Supply Chain Management',
            'Kontrol stok pergudangan multi-gudang, nomor batch, serial number, dan metode FIFO/LIFO',
            'archive',
            'Optimalisasi operasional pergudangan mulai dari penerimaan barang (receiving), penataan rak (put-away), stock opname, hingga pengiriman (shipping).',
            json.dumps(['Manajemen Multi-Gudang & Multi-Lokasi Rak', 'Peringatan Dini Stok Minimum & Rekomendasi Restock', 'Stock Opname Cepat Menggunakan Barcode Scanner Handheld', 'Pelacakan Batch Number & Tanggal Kedaluwarsa (Expired Date)', 'Integrasi Surat Jalan & Delivery Order']),
            json.dumps(['PostgreSQL', 'Redis Cache', 'Vue.js', 'Barcode Scanner Engine']),
            json.dumps(['Akurasi stok mencapai 99.8% menghindari selisih fisik', 'Kecepatan pemenuhan order pelanggan meningkat 2x lipat', 'Pencegahan kerugian akibat barang rusak atau lewat tanggal kedaluwarsa'])
        ),
        (
            'erp-document-management',
            'Aplikasi Bisnis ERP',
            'Document Management System & E-Persuratan',
            'Transformasi kantor tanpa kertas (paperless) dengan disposisi surat elektronik dan tanda tangan digital',
            'file-text',
            'Pengelolaan dokumen persuratan masuk/keluar, arsip penting, nota dinas, serta alur disposisi hierarkis yang bisa ditandatangani dari ponsel.',
            json.dumps(['Alur Disposisi Bertingkat Sesuai Hirarki Jabatan', 'Pemberian Nomor Surat Otomatis Berdasarkan Kode Klasifikasi', 'Tanda Tangan Elektronik Terverifikasi (Digital Signature)', 'Optical Character Recognition (OCR) Pencarian Isi Dokumen', 'Penyimpanan Terenkripsi & Pembatasan Hak Unduh']),
            json.dumps(['OCR Tesseract', 'Python', 'Digital Signature Module', 'PostgreSQL']),
            json.dumps(['Proses persetujuan dokumen dinas dari berhari-hari menjadi hitungan menit', 'Pencarian surat masa lampau hanya dalam 3 detik', 'Penghematan anggaran kertas, cetak, dan kurir fisik hingga 85%'])
        ),
        (
            'erp-dashboard-eksekutif',
            'Aplikasi Bisnis ERP',
            'Executive Dashboard & Business Intelligence',
            'Visualisasi indikator kinerja utama (KPI) perusahaan dalam bentuk grafik interaktif untuk Direksi',
            'pie-chart',
            'Dashboard analitik eksekutif yang merangkum data penjualan, biaya produksi, profitabilitas cabang, dan efisiensi tenaga kerja dalam layar tunggal.',
            json.dumps(['Visualisasi Metrik Keuangan, Operasional & SDM Secara Real-time', 'Filter Analitik Berdasarkan Cabang, Periode, & Produk', 'Prediksi Tren Penjualan dengan Algoritma Machine Learning', 'Notifikasi Anomali dan Pencapaian Target via Email & WhatsApp', 'Dapat Diakses Aman dari Tablet, Laptop, maupun Smartphone']),
            json.dumps(['Apache Superset / Custom Chart.js', 'PostgreSQL Data Warehouse', 'Python']),
            json.dumps(['Pimpinan mendapatkan visibilitas 360 derajat atas seluruh unit usaha', 'Keputusan strategis dieksekusi berdasarkan fakta data bukan intuisi semata', 'Deteksi cepat pembengkakan biaya atau penurunan omzet cabang'])
        ),

        # 3. Aplikasi E-Government (Smart Governance)
        (
            'egov-portal-daerah',
            'Aplikasi E-Government',
            'Portal Resmi Pemerintah Daerah & OPD',
            'Website resmi institusi pemerintah berstandar Kominfo dengan keterbukaan informasi publik (KIP)',
            'shield',
            'Pembangunan portal pemda dan website dinas yang ramah disabilitas, aman dari serangan siber (web defacement), serta menyajikan transparansi program daerah.',
            json.dumps(['Standar Desain Aksesibilitas Web (WCAG 2.1) & Ramah Disabilitas', 'Modul PPID (Pejabat Pengelola Informasi dan Dokumentasi)', 'Integrasi Berita Daerah, Pengumuman Lelang & Agenda Kegiatan', 'Proteksi Web Application Firewall (WAF) Anti-Hacking & Anti-Deface', 'Pusat Unduhan Regulasi Daerah (Perda & Perbup/Perwali)']),
            json.dumps(['Python Flask / Next.js', 'Tailwind CSS', 'Cloudflare Enterprise', 'PostgreSQL']),
            json.dumps(['Meningkatkan indeks kepuasan masyarakat terhadap transparansi Pemda', 'Keamanan teruji lolos assessment vulnerability testing BSSN', 'Menjadi rujukan informasi resmi yang menangkal hoax di wilayah daerah'])
        ),
        (
            'egov-data-sektoral',
            'Aplikasi E-Government',
            'e-Data Sektoral & Satu Data Indonesia',
            'Platform integrasi statistik sektoral daerah sesuai Perpres No. 39 Tahun 2019 tentang Satu Data Indonesia',
            'database',
            'Sistem pengumpulan, verifikasi, validasi, dan publikasi data statistik sektoral dari seluruh OPD produsen data ke walidata daerah (Diskominfo) dan pembina data (BPS).',
            json.dumps(['Format Standar Metadata & Interoperabilitas Satu Data Indonesia', 'Alur Validasi Data Bertingkat (Produsen Data -> Walidata -> Publik)', 'Open Data Portal Siap Unduh API (JSON, CSV, XLS)', 'Katalog Data Statistik Ekonomi, Sosial, Infrastruktur, dan Pendidikan', 'Visualisasi Infografis & Grafik Dinamis Publik']),
            json.dumps(['CKAN Architecture / Custom Python SDI', 'PostgreSQL', 'D3.js Data Charts']),
            json.dumps(['Meraih peringkat tertinggi dalam evaluasi Satu Data Daerah Nasional', 'Perumusan kebijakan pembangunan berbasis evidence-based policy', 'Masyarakat & akademisi mendapatkan akses data valid secara cuma-cuma'])
        ),
        (
            'egov-e-planning-musrenbang',
            'Aplikasi E-Government',
            'e-Planning & Musrenbang Online',
            'Sistem perencanaan pembangunan daerah dari tingkat Dusun, Desa, Kecamatan hingga Renja OPD',
            'calendar',
            'Mendukung perumusan RPJMD, Renstra, RKPD, dan Renja secara sistematis, transparan, dan terhubung langsung dengan usulan aspirasi masyarakat (Pokir/Musrenbang).',
            json.dumps(['Input Usulan Musrenbang Desa hingga Kabupaten dengan Bukti Foto & GPS', 'Penyusunan Pohon Kinerja Cascading RPJMD ke Renja OPD', 'Integrasi Pokir (Pokok Pikiran DPRD) Sesuai Ketentuan Kemendagri', 'Sinkronisasi dengan Standar Satuan Harga (SSH & ASB)', 'Cetak Dokumen Rancangan RKPD Otomatis Standar Permendagri']),
            json.dumps(['PostgreSQL', 'Python Calculation Core', 'Bootstrap/Tailwind', 'PDF Engine']),
            json.dumps(['Usulan masyarakat terkawal tanpa manipulasi di tengah jalan', 'Kesesuaian 100% antara target RPJMD kepala daerah dengan anggaran OPD', 'Proses rekap musrenbang yang sebelumnya berminggu-minggu tuntas dalam 2 hari'])
        ),
        (
            'egov-e-monev-sakip',
            'Aplikasi E-Government',
            'e-Monev & e-SAKIP (Sistem Akuntabilitas Kinerja)',
            'Monitoring realisasi fisik & keuangan serta penilaian reformasi birokrasi berpredikat A/BB Kemenpan-RB',
            'award',
            'Aplikasi evaluasi capaian kinerja berkala instansi pemerintah untuk memantau serapan APBD, pencapaian target output, dan laporan akuntabilitas LHE SAKIP.',
            json.dumps(['Penginputan Realisasi Fisik & Anggaran Tiap Triwulan', 'Kalkulasi Otomatis Tingkat Deviasi & Indeks Capaian Kinerja (IKU)', 'Laporan LKjIP (Laporan Kinerja Instansi Pemerintah) Siap Cetak', 'Upload Bukti Dukung Sakip untuk Evaluasi Kemenpan-RB', 'Notifikasi Peringatan Program dengan Deviasi Merah']),
            json.dumps(['Python', 'PostgreSQL', 'Highcharts Data Viz', 'Docker']),
            json.dumps(['Mendongkrak nilai akuntabilitas SAKIP Pemda menuju predikat A', 'Mencegah penumpukan pencairan anggaran di akhir tahun anggaran', 'Pimpinan daerah mengetahui OPD mana yang berkinerja unggul dan lambat'])
        ),
        (
            'egov-e-lapor-pengaduan',
            'Aplikasi E-Government',
            'e-Lapor & Aduan Warga Terintegrasi SP4N',
            'Kanal pengaduan masyarakat cepat tanggap dengan pelacakan status tiket penanganan OPD',
            'message-square',
            'Memfasilitasi aspirasi dan keluhan warga kota/kabupaten dengan sistem disposisi instan ke dinas terkait, batas waktu SLA respon, dan notifikasi SMS/WhatsApp.',
            json.dumps(['Pengaduan via Web, Mobile Apps, dan WhatsApp Bot', 'Disposisi Otomatis Berdasarkan Kategori Urusan Dinas', 'SLA Response Time & Escalation Matrix ke Sekretaris Daerah', 'Peta Sebaran Titik Aduan Masalah Publik (Jalan Rusak, Sampah, Lampu)', 'Rating Kepuasan Warga atas Penyelesaian Masalah']),
            json.dumps(['WhatsApp Business API', 'Flutter', 'PostgreSQL', 'Leaflet Map Tracker']),
            json.dumps(['Kecepatan tindak lanjut keluhan warga meningkat 400%', 'Mencegah viral negatif di media sosial karena kanal aduan aktif & solutif', 'Peta tematik membantu dinas teknis memprioritaskan perbaikan infrastruktur'])
        ),
        (
            'egov-e-perizinan-mpp',
            'Aplikasi E-Government',
            'e-Perizinan & Mal Pelayanan Publik (MPP)',
            'Layanan izin usaha dan non-usaha satu pintu terintegrasi dengan tanda tangan digital TTE BSrE',
            'clipboard',
            'Digitalisasi loket dinas DPMPTSP untuk pengajuan izin online, verifikasi berkas virtual, pembayaran retribusi daerah, dan penerbitan izin ber-barcode sah.',
            json.dumps(['Formulir Dinamis Ratusan Jenis Izin Usaha & Non-Usaha', 'Integrasi Tanda Tangan Elektronik Bersertifikasi BSrE BSSN', 'Tracking Berkas Permohonan Real-time oleh Pemohon', 'Koneksi Payment Gateway BPD Bank Daerah untuk Retribusi', 'Antrean Online Mal Pelayanan Publik (MPP)']),
            json.dumps(['BSrE BSSN API Connector', 'Python Engine', 'PostgreSQL', 'QR Verification']),
            json.dumps(['Waktu pengurusan izin dipangkas dari 14 hari kerja menjadi 24 jam', 'Pemberantasan calo dan pungutan liar secara tuntas', 'Peningkatan signifikan investasi daerah dan Pendapatan Asli Daerah (PAD)'])
        )
    ]

    for s in services:
        cursor.execute('''
        INSERT INTO services (slug, category, title, subtitle, icon, summary, features, tech_stack, benefits)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', s)

    # --- PORTFOLIO SEED (HASIL PROJEK RESMI PT. AKSARA CIPTA DIGITAL) ---
    portfolios = [
        (
            'sisurvei-lembaga-survei-riset',
            'SISURVEI (Sistem Informasi Manajemen Survei & Riset Lapangan Terpadu)',
            'Sistem Informasi',
            'Lembaga Riset & Konsultan Survei Nasional',
            'Swasta / Lembaga Riset',
            '2024',
            'Aplikasi untuk mengelola berbagai jenis kegiatan survei dari lembaga survei dan research konsultan yang terintegrasi langsung dengan petugas lapangan untuk menghasilkan data riset yang berkualitas, valid, dan realtime.',
            'Pengelolaan sampling responden survei di berbagai wilayah sering lambat, rawan rekayasa data kuesioner oleh petugas lapangan fiktif (fraud entry), dan lambatnya kompilasi ribuan lembar kuesioner fisik ke pusat data riset.',
            'ACD membangun platform SISURVEI dengan integrasi CAPI (Computer-Assisted Personal Interviewing) mobile offline-first, validasi GPS geotagging & timestamp saat wawancara, audio audit sampling, serta dashboard analitik visual tabulasi data riset instan.',
            'Meniadakan kecurangan data survei lapangan hingga 100%, mempercepat proses tabulasi hasil survei dari 3 minggu menjadi hitungan jam, serta menghasilkan dataset riset yang berkualitas tinggi dan akuntabel.',
            json.dumps(['Flutter Mobile CAPI', 'Python FastAPI', 'PostgreSQL', 'GIS Geolocation', 'Automated Quality Control Engine', 'Statistical Tabulation JS']),
            '',
            json.dumps({'Akurasi Data Riset': '99.9%', 'Pencegahan Fraud Survey': '100%', 'Kecepatan Tabulasi': 'Real-time'})
        ),
        (
            'sicepat-desa',
            'SICEPAT DESA (Sistem Informasi Pencatatan Kependudukan dan Layanan Masyarakat Desa)',
            'E-Government',
            'Pemerintah Desa & Kantor Kelurahan Terpadu',
            'Pemerintahan',
            '2024',
            'Aplikasi yang menghimpun data kependudukan, pencatatan penduduk, serta pelayanan administrasi surat-menyurat desa secara cepat dan digital.',
            'Warga desa harus datang langsung dan antre berjam-jam untuk meminta surat pengantar domisili, surat keterangan usaha (SKU), dan permohonan bansos yang dicatat manual di buku arsip kertas.',
            'ACD membangun platform SICEPAT DESA berbasis web & mobile-friendly dengan fitur e-Surat mandiri ber-QR Code legalitas digital, buku induk penduduk desa digital, serta notifikasi WhatsApp instan saat surat selesai.',
            'Waktu penerbitan surat terpangkas dari 2 hari menjadi kurang dari 10 menit, arsip desa 100% digital tanpa risiko rusak/hilang, dan indeks kepuasan masyarakat desa melonjak ke 98%.',
            json.dumps(['PHP Laravel', 'MySQL', 'Tailwind CSS', 'PDF Generator with QR Verify', 'WhatsApp Gateway API']),
            '',
            json.dumps({'Waktu Penerbitan Surat': '< 10 Menit', 'Kepuasan Warga': '98%', 'Digitalisasi Arsip': '100%'})
        ),
        (
            'simanja-waroeng-jamur-mang-yayat',
            'SIMANJA (Sistem Informasi Monitoring Pekerjaan & Belanja Waroeng Jamur Mang Yayat)',
            'Aplikasi Mobile',
            'Waroeng Jamur Mang Yayat (Agribisnis & Kuliner Jamur)',
            'Swasta',
            '2024',
            'Aplikasi mobile APK untuk mencatat hasil panen jamur, memonitor alur distribusi logistik, mencatat biaya operasional belanja harian, dan rekapitulasi laba rugi otomatis.',
            'Hasil panen jamur tiram dan olahan sering mengalami selisih timbangan saat pengiriman ke mitra resto/pasar, pencatatan belanja bibit dan baglog masih manual, serta sulitnya mengetahui laba bersih harian.',
            'ACD mengembangkan aplikasi mobile APK SIMANJA dengan fitur input panen harian, tracking delivery logistik ke mitra pemesan, scan barcode keranjang panen, pencatatan pos belanja operasional, dan dashboard laporan P&L (Profit & Loss).',
            'Selisih timbangan panen berkurang 95%, pencatatan pengeluaran modal harian transparan, dan pemilik usaha dapat memantau pergerakan laba rugi secara realtime langsung dari genggaman HP Android.',
            json.dumps(['Flutter Mobile Android APK', 'Node.js REST API', 'PostgreSQL', 'Google Cloud Storage', 'Report Export Engine']),
            '',
            json.dumps({'Akurasi Timbangan': '99.8%', 'Kebocoran Logistik': '-95%', 'Monitoring Laba': 'Real-time APK'})
        ),
        (
            'simantra-alokasi-pekerjaan-honor-mitra',
            'SIMANTRA (Sistem Informasi Alokasi Pekerjaan dan Pembagian Honor Mitra)',
            'ERP & HRIS',
            'Lembaga Manajemen Survei & Mitra Lapangan',
            'Swasta',
            '2024',
            'Sistem informasi tata kelola pengalokasian penugasan pekerjaan dan pembagian honor mitra kerja secara adil, akuntabel, dan terkontrol dengan batas pagu tertentu.',
            'Manajemen kesulitan mendistribusikan ratusan paket pekerjaan kepada puluhan mitra surveyor freelance, sering terjadi tumpang tindih penugasan, dan akumulasi honor melebihi batas pagu anggaran (over-budget).',
            'ACD membangun SIMANTRA dengan algoritma smart-allocation yang otomatis mengunci penugasan jika mitra telah mencapai batas pagu honor per periode, kalkulasi pajak PPh otomatis, dan penerbitan slip pembayaran digital.',
            'Nihil over-budget anggaran (0%), alokasi kerja antar-mitra adil dan merata, serta proses verifikasi dan pembayaran honor yang sebelumnya butuh 1 minggu selesai dalam 1 hari.',
            json.dumps(['Python Django', 'PostgreSQL', 'Tailwind CSS', 'Automated Payroll Calculation', 'Slip Generator']),
            '',
            json.dumps({'Over-budget Risk': '0%', 'Kecepatan Payroll': '7x Lebih Cepat', 'Mitra Terkelola': '500+ Mitra'})
        ),
        (
            'website-profil-transparansi-desa',
            'Website Profil Desa & Portal Transparansi Publik',
            'Website Korporat',
            'Pemerintah Desa Mandiri Sejahtera',
            'Pemerintahan',
            '2024',
            'Website resmi profil desa untuk publikasi potensi pariwisata, produk unggulan UMKM desa, transparansi realisasi APBDes, serta berita kegiatan warga desa.',
            'Banyak desa memiliki komoditas unggulan dan potensi wisata alam yang luar biasa namun tidak memiliki kanal promosi digital, serta tuntutan keterbukaan informasi publik (KIP) penggunaan dana desa.',
            'ACD merancang portal web profil desa modern dengan antarmuka mobile-first, visual galeri potensi desa, peta spasial sentra UMKM, infografis APBDes yang mudah dipahami warga, dan kanal pengaduan masyarakat.',
            'Kunjungan wisatawan ke destinasi lokal meningkat 35%, produk UMKM desa dikenal hingga luar daerah, dan keterbukaan tata kelola desa meraih predikat Desa Informatif.',
            json.dumps(['HTML5 / Tailwind CSS', 'Python Flask Web', 'MySQL', 'Interactive Infographic JS', 'SEO Optimization']),
            '',
            json.dumps({'Pengunjung Bulanan': '12.000+', 'Keterbukaan APBDes': '100%', 'Kecepatan Muat': '< 1 detik'})
        ),
        (
            'website-profil-akademik-sekolah',
            'Website Resmi Profil, Akademik & PPDB Online Sekolah',
            'Website Korporat',
            'SMK & Lembaga Pendidikan Terpadu Unggulan',
            'Pendidikan',
            '2024',
            'Website profil sekolah modern yang memuat visi misi, program kejuruan, prestasi siswa, fasilitas sekolah, direktori tenaga pendidik, dan pendaftaran PPDB online.',
            'Proses Penerimaan Peserta Didik Baru (PPDB) masih bergantung pada formulir fisik dan brosur cetak yang memakan biaya besar serta jangkauan calon siswa yang terbatas di area sekitar.',
            'ACD membangun portal sekolah terintegrasi dengan modul profil interaktif, tur virtual fasilitas belajar, formulir pendaftaran PPDB online lengkap dengan upload berkas, dan integrasi konfirmasi WhatsApp.',
            'Jumlah pendaftar calon siswa baru melonjak 45%, penghematan biaya cetak brosur promosi hingga 70%, dan kemudahan akses informasi nilai serta kalender akademik bagi wali murid.',
            json.dumps(['Next.js / Python', 'Tailwind CSS', 'PostgreSQL', 'WhatsApp Confirmation API', 'Responsive UI']),
            '',
            json.dumps({'Peningkatan PPDB': '+45%', 'Efisiensi Brosur': '70%', 'Akses Mobile': '94%'})
        ),
        (
            'cuan-servis-ac-mobile-apk',
            'CUAN (Catatan Usaha Anak Rantau) - Servis AC, Work Order & Penjualan Unit',
            'Aplikasi Mobile',
            'CV Catatan Usaha Anak Rantau (CUAN Cooling Specialist)',
            'Swasta',
            '2024',
            'Aplikasi mobile APK untuk perusahaan jasa servis dan penjualan unit serta onderdil AC rumah dan kantor, dilengkapi sistem Work Order teknisi, customer CRM, dan laba rugi.',
            'Jadwal kunjungan teknisi servis AC sering bentrok, penggunaan suku cadang/freon di lapangan tidak sinkron dengan gudang, dan sering terjadi lupa follow-up jadwal cuci AC berkala pelanggan.',
            'ACD merancang aplikasi mobile Android APK CUAN dengan fitur dispatching penugasan Work Order (WO) ke ponsel teknisi, riwayat servis customer, modul kasir penjualan unit AC & onderdil, notifikasi jadwal servis berkala otomatis via WA, dan rekapitulasi laba rugi harian.',
            'Kapasitas pengerjaan unit servis naik 60% per hari, kebocoran stok sparepart freon menjadi 0%, dan repeat order pelanggan servis berkala meningkat drastis.',
            json.dumps(['Flutter Android Mobile APK', 'FastAPI Python Backend', 'PostgreSQL', 'Thermal Bluetooth Printer API', 'WhatsApp Service Reminder']),
            '',
            json.dumps({'Kapasitas Servis': '+60%', 'Nihil Selisih Onderdil': '0%', 'Repeat Order': '+55%'})
        ),
        (
            'umkm-dimsum-pos-outlet-apk',
            'Aplikasi Kasir POS & Multi-Outlet Management UMKM Dimsum',
            'Aplikasi Mobile',
            'Jaringan Outlet Dimsum Nusantara',
            'Swasta',
            '2024',
            'Aplikasi mobile APK untuk pencatatan transaksi penjualan kasir POS di berbagai cabang outlet, kontrol biaya belanja operasional, stok bahan baku beku, dan rekapitulasi laba rugi.',
            'Pemilik usaha kesulitan memantau setoran omzet dari 8 cabang gerobak/outlet dimsum, rentan manipulasi nota kasir manual, dan sering terjadi kehabisan stok dimsum beku di outlet tertentu saat jam ramai.',
            'ACD membangun aplikasi mobile APK kasir POS touchscreen yang ringan dengan sinkronisasi cloud realtime, mutasi transfer stok bahan antar-cabang, otorisasi diskon kasir, dan ringkasan omzet serta laba bersih harian langsung ke aplikasi HP owner.',
            'Proses tutup buku kasir harian selesai dalam 5 menit, menekan selisih stok bahan baku hingga 0%, dan memudahkan evaluasi cabang yang paling menguntungkan.',
            json.dumps(['Flutter Mobile APK', 'SQLite Offline-First', 'Node.js Cloud Sync', 'Bluetooth Receipt Printer', 'Executive Dashboard']),
            '',
            json.dumps({'Tutup Kasir Harian': '5 Menit', 'Akurasi Stok Outlet': '100%', 'Cabang Terintegrasi': '8+ Outlet'})
        ),
        (
            'platform-ecommerce-sewa-toko-digital',
            'Platform E-Commerce & Penyewaan Toko Digital Siap Pakai',
            'Sistem Informasi',
            'Digital Storefront & Retail Platform Provider',
            'Swasta',
            '2024',
            'Platform website e-commerce modern penyedia dan penyewaan etalase toko digital bagi para UMKM dan merchant online dengan sistem langganan terintegrasi.',
            'Banyak pedagang online ingin memiliki website toko online sendiri dengan katalog profesional tetapi tidak mengerti coding, sementara platform penyedia butuh sistem tagihan sewa dan aktivasi toko otomatis.',
            'ACD membangun platform SaaS e-commerce multi-tenant di mana merchant dapat menyewa dan mengaktifkan toko digital instan dalam hitungan menit, terintegrasi payment gateway (QRIS, VA, E-Wallet), modul manajemen pesanan, dan ongkos kirim otomatis.',
            'Memungkinkan lebih dari 150 merchant aktif membuka toko online mandiri dalam waktu kurang dari 10 menit, serta sistem penagihan langganan sewa platform berjalan 100% otomatis.',
            json.dumps(['Next.js / React Frontend', 'Python Backend API', 'PostgreSQL', 'Midtrans Payment Gateway', 'RajaOngkir Logistics API', 'Cloudflare CDN']),
            '',
            json.dumps({'Aktivasi Toko': '< 10 Menit', 'Uptime Platform': '99.95%', 'Merchant Terdaftar': '150+ Toko'})
        )
    ]

    for p in portfolios:
        cursor.execute('''
        INSERT INTO portfolios (slug, title, category, client_name, client_type, year, summary, challenge, solution, impact, tech_stack, image_url, metrics)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', p)

    # --- BLOG POSTS SEED ---
    blogs = [
        (
            'panduan-memilih-jasa-pembuatan-aplikasi-enterprise',
            'Panduan Lengkap Memilih Jasa Pembuatan Aplikasi Enterprise yang Tepat & Bergaransi',
            'Teknologi & Bisnis',
            'Tim Konsultan ACD',
            '6 Menit',
            'Menemukan software house yang mengerti proses bisnis bukan perkara mudah. Pelajari kriteria esensial mulai dari metodologi agile, jaminan SLA garansi, hingga audit keamanan kode sumber.',
            '''Membangun software untuk level enterprise bukan sekadar menulis baris kode pemrograman. Software enterprise harus andal menangani ribuan transaksi bersamaan, memiliki perlindungan keamanan data yang kokoh, dan mudah disesuaikan ketika skala bisnis bertumbuh secara eksponensial.

Banyak perusahaan terjebak memilih vendor perangkat lunak yang hanya menawarkan harga murah di awal, namun berakhir mangkrak karena vendor tidak memahami seluk-beluk alur proses bisnis klien. Berikut adalah indikator utama saat Anda memilih mitra konsultan software:

1. **Pemahaman Proses Bisnis Mendalam (Business Analyst First)**: Jangan percaya vendor yang langsung memberikan estimasi biaya sebelum melakukan bedah proses bisnis Anda. Mitra yang baik mengalokasikan waktu wawancara dan analisis alur kerja secara komprehensif.
2. **Jaminan Garansi & Service Level Agreement (SLA)**: Pastikan kontrak kerja mencakup garansi perbaikan bug tanpa batas biaya tersembunyi dan layanan maintenance berkala.
3. **Standar Keamanan Internasional**: Pastikan sistem lolos uji penetration testing (pentest) dan memenuhi prinsip OWASP Top 10 serta enkripsi data saat disimpan (at rest) maupun saat dikirim (in transit).
4. **Kepemilikan Source Code & Dokumentasi Arsitektur**: Anda harus memiliki hak milik penuh atas kode sumber aplikasi beserta dokumentasi API dan petunjuk deployment yang rapi.

Di PT. Aksara Cipta Digital (ACD), kami menerapkan pendekatan konsultatif dari tahap discovery hingga post-launch maintenance, memastikan investasi digital perusahaan Anda memberikan ROI (Return on Investment) yang nyata.''',
            'Jasa Pembuatan Aplikasi, Software Enterprise, Konsultan IT, Transformasi Digital',
            '/static/images/blog_1.svg',
            '18 Oktober 2024'
        ),
        (
            'transformasi-digital-pemerintah-daerah-satu-data',
            'Akselerasi SPBE: Bagaimana Pemda Mengoptimalkan Satu Data Indonesia dan E-SAKIP',
            'E-Government & Smart City',
            'Dr. Irwan Setiawan, S.Kom., M.T.',
            '8 Menit',
            'Strategi menghubungkan silo data antar Organisasi Perangkat Daerah (OPD) untuk mendongkrak indeks SPBE dan efisiensi belanja APBD secara terukur.',
            '''Implementasi Sistem Pemerintahan Berbasis Elektronik (SPBE) bukan lagi pilihan, melainkan keharusan mutlak bagi seluruh pemerintah provinsi, kabupaten, dan kota di Indonesia. Namun, salah satu tantangan terbesar yang sering dihadapi adalah keberadaan ratusan aplikasi yang saling terisolasi (silo data).

Dinas Komunikasi dan Informatika (Diskominfo) sebagai walidata daerah sering kali kesulitan menyatukan data sektoral dari dinas kesehatan, pendidikan, perizinan, dan kependudukan. Akibatnya, kepala daerah sulit mengambil keputusan strategis karena data yang tersedia tidak selaras.

Kunci sukses transformasi digital pemerintah daerah terletak pada tiga pilar utama:
- **Interoperabilitas Standar OGC & Satu Data**: Pemanfaatan API Gateway terpusat yang mewajibkan seluruh produsen data menyuplai data dengan format metadata yang seragam sesuai standar Satu Data Indonesia.
- **Penyelarasan RPJMD ke Renja Melalui e-Planning**: Menutup celah anggaran siluman dengan sistem pohon kinerja (cascading) yang ketat.
- **Transparansi Kinerja Melalui e-SAKIP**: Memastikan setiap rupiah uang rakyat (APBD) dapat dipertanggungjawabkan output dan outcome dampaknya terhadap kesejahteraan masyarakat.

ACD Digital Consulting telah berpengalaman mendampingi puluhan pemda dalam mewujudkan tata kelola smart governance yang modern, akuntabel, dan berpredikat A.''',
            'SPBE, Smart City, Satu Data Indonesia, E-Gov, E-SAKIP',
            '/static/images/blog_2.svg',
            '10 Oktober 2024'
        ),
        (
            'mengapa-perusahaan-memerlukan-custom-erp-dibanding-saas-kaku',
            'Custom ERP vs Software Jadi (Off-The-Shelf): Mana yang Paling Menguntungkan untuk Perusahaan Anda?',
            'ERP & Otomasi',
            'Bambang Wicaksono, M.M.',
            '7 Menit',
            'Analisis perbandingan biaya jangka panjang, fleksibilitas alur kerja, dan kedaulatan data antara membangun sistem ERP custom dengan menyewa aplikasi siap pakai bulanan.',
            '''Banyak pemilik bisnis bingung menentukan pilihan saat ingin mengotomatiskan operasional: haruskah berlangganan aplikasi SaaS off-the-shelf yang sudah jadi, atau membangun Custom ERP khusus yang dirancang sesuai alur kerja perusahaan?

Meskipun software jadi terlihat menarik dengan biaya awal yang relatif murah, sering kali di kemudian hari perusahaan dihadapkan pada keterbatasan besar:
- Alur kerja bisnis perusahaan yang unik terpaksa harus 'mengalah' dan mengikuti batasan software template.
- Biaya langganan per user (per-seat license) membengkak drastis saat jumlah karyawan bertambah ratusan orang.
- Data sensitif pelanggan dan keuangan tersimpan di server pihak ketiga di luar kendali perusahaan.
- Sulit atau mahalnya biaya integrasi ketika ingin dikoneksikan dengan mesin pabrik atau aplikasi internal lain.

Dengan membangun **Custom ERP** bersama ACD Digital Consulting:
1. Alur sistem 100% menyesuaikan keunggulan kompetitif proses bisnis Anda (bukan sebaliknya).
2. Tanpa biaya langganan bulanan per user (zero license recurring cost), Anda bebas menambahkan ribuan karyawan tanpa biaya tambahan.
3. Hak milik data dan database sepenuhnya berada di infrastruktur server milik perusahaan Anda sendiri.
4. Fleksibel untuk dikembangkan dan diperluas seiring pertumbuhan unit bisnis baru.

Investasi pada Custom ERP terbukti memberikan penghematan biaya total (TCO - Total Cost of Ownership) hingga 58% dalam jangka waktu 3 tahun.''',
            'ERP, Software Custom, Otomasi Bisnis, Efisiensi Biaya',
            '/static/images/blog_3.svg',
            '28 September 2024'
        )
    ]

    for b in blogs:
        cursor.execute('''
        INSERT INTO blog_posts (slug, title, category, author, read_time, summary, content, tags, image_url, published_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', b)

    # --- TESTIMONIALS SEED ---
    testimonials = [
        (
            'Hendra Kurniawan, S.T., M.M.',
            'Direktur Operasional & Produksi',
            'PT Tri Dharma Otomotif Indonesia',
            'Sistem KDPL yang dibangun oleh tim ACD benar-benar mengubah lantai pabrik kami. Pencatatan part assembling yang dulu lambat dan sering salah stok kini tuntas 100% otomatis. Dedikasi tim ACD dalam memahami alur kerja manufaktur kami sangat luar biasa.',
            5,
            'Sistem KDPL Otomotif'
        ),
        (
            'H. Dedi Suhardi, M.T.',
            'Direktur Utama',
            'Perumda Air Minum Tirta Khatulistiwa',
            'Aplikasi SIAP dari ACD Digital Consulting membuat respon keluhan pipa bocor kami melompat drastis. Petugas lapangan lebih sigap, koordinasi transparan, dan masyarakat memberikan apresiasi tinggi atas peningkatan mutu pelayanan kami.',
            5,
            'Aplikasi SIAP Aduan Pelanggan'
        ),
        (
            'Siti Rahmah, S.E.',
            'General Manager Keuangan & SDM',
            'PT Angkasa Nusantara Mandiri Tours',
            'Mengelola 45 kantor cabang kini seringan mengklik smartphone. Modul Sales Management & Payroll ACD memotong waktu rekonsiliasi bulanan kami dari 2 minggu jadi hanya beberapa jam. Sangat direkomendasikan bagi pemilik bisnis!',
            5,
            'Sales Management & CRM'
        ),
        (
            'Drs. Ahmad Fauzan, M.Si.',
            'Kepala Badan Perencanaan Pembangunan (Bappeda)',
            'Pemerintah Kabupaten Barito Cipta',
            'Kerja sama kami dengan ACD dalam membangun sistem e-Planning & e-Monev sangat memuaskan. Tim selalu tepat waktu, responsif terhadap dinamika regulasi Permendagri, dan sistemnya terbukti sangat aman dan andal.',
            5,
            'e-Planning & e-Monev Daerah'
        )
    ]

    for t in testimonials:
        cursor.execute('''
        INSERT INTO testimonials (client_name, client_title, company_name, content, rating, project_name)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', t)

    # --- CAREERS SEED ---
    careers = [
        (
            'senior-fullstack-python-engineer',
            'Senior Full-stack Software Engineer (Python & Vue/React)',
            'Engineering & Development',
            'Jakarta / Yogyakarta / Hybrid',
            'Full-time',
            'Minimal 4 Tahun',
            'Kami mencari engineer berpengalaman untuk memimpin perancangan dan implementasi arsitektur aplikasi berskala besar untuk klien BUMN, Pemerintahan, dan Korporasi swasta.',
            json.dumps(['Pengalaman solid minimal 4 tahun dalam pengembangan web backend menggunakan Python (FastAPI/Flask/Django)', 'Mahir menggunakan modern frontend framework (Vue.js 3 atau React/Next.js)', 'Pemahaman mendalam mengenai relational database (PostgreSQL) dan caching (Redis)', 'Terbiasa dengan containerization (Docker) dan CI/CD pipeline', 'Kemampuan problem-solving tinggi dan komunikasi tim yang konstruktif']),
            json.dumps(['Merancang arsitektur sistem yang scalable, maintainable, dan aman', 'Mengembangkan RESTful & GraphQL API berkinerja tinggi', 'Melakukan code review dan mentoring bagi software engineer junior', 'Berkolaborasi erat dengan Product Manager, UI/UX Designer, dan System Analyst'])
        ),
        (
            'lead-system-analyst-consultant',
            'Lead System Analyst & Business Consultant',
            'Product & Consulting',
            'Jakarta / Yogyakarta',
            'Full-time',
            'Minimal 3 Tahun',
            'Posisi kunci untuk menerjemahkan kebutuhan bisnis kompleks klien menjadi blueprint spesifikasi teknis software (SRS, BRD, Flowchart, Wireframe) yang siap dieksekusi tim developer.',
            json.dumps(['Pengalaman minimal 3 tahun sebagai System Analyst atau IT Consultant', 'Menguasai pemodelan proses bisnis (BPMN, UML, Use Case Diagram, Data Flow Diagram)', 'Kemampuan wawancara dan komunikasi diplomatis dengan level direksi maupun staf operasional', 'Memahami alur dasar ERP (Akuntansi, HRIS, Supply Chain) atau e-Government']),
            json.dumps(['Memimpin sesi requirement gathering dan discovery workshop bersama klien', 'Menyusun dokumen Software Requirement Specification (SRS) dan alur logic sistem', 'Menjembatani komunikasi antara stakeholder bisnis dengan tim pengembang software', 'Memastikan hasil akhir sistem selaras dengan ekspektasi awal klien'])
        ),
        (
            'senior-ui-ux-product-designer',
            'Senior UI/UX & Product Designer',
            'Design & Creative',
            'Yogyakarta / Hybrid',
            'Full-time',
            'Minimal 3 Tahun',
            'Menciptakan pengalaman pengguna kelas dunia untuk aplikasi mobile dan dashboard enterprise yang bersih, intuitif, dan memudahkan aktivitas kerja sehari-hari.',
            json.dumps(['Portofolio kuat yang mendemonstrasikan proses desain end-to-end (User Research, Wireframing, Hi-Fi Prototype)', 'Keahlian tinggi dalam Figma, Design System, Auto Layout, dan Interactive Components', 'Pemahaman mendalam mengenai Design Thinking, UX Research, dan Usability Testing', 'Kemampuan merancang antarmuka dashboard kompleks dengan visualisasi data yang mudah dipahami']),
            json.dumps(['Mengembangkan user persona, journey map, dan information architecture sistem', 'Membangun dan memelihara Design System terstandar untuk percepatan pengembangan produk', 'Melakukan usability testing bersama pengguna nyata untuk validasi hipotesis desain', 'Menyerahkan aset desain terstruktur (hand-off) kepada tim developer'])
        ),
        (
            'devops-cloud-security-engineer',
            'DevOps & Cloud Security Specialist',
            'Infrastructure & Security',
            'Jakarta / Remote',
            'Full-time',
            'Minimal 3 Tahun',
            'Mengelola infrastruktur cloud server, orkestrasi microservices, serta memastikan keamanan siber tingkat tinggi untuk platform klien enterprise dan pemerintahan.',
            json.dumps(['Pengalaman mengelola Linux Server (Ubuntu/Debian) dan Cloud Provider (AWS, GCP, atau Cloud Lokal Indonesia)', 'Keahlian dalam Docker, Kubernetes, Nginx, HAProxy, dan Database Clustering', 'Menguasai implementasi CI/CD menggunakan GitLab CI atau GitHub Actions', 'Memahami praktik Web Application Firewall (WAF), SSL/TLS, hardening server, dan OWASP']),
            json.dumps(['Membangun dan mengotomatiskan pipeline deployment aplikasi', 'Memantau performa server 24/7 dan mengoptimalkan latensi serta uptime 99.9%', 'Melakukan audit keamanan berkala dan simulasi vulnerability assessment', 'Menyusun prosedur disaster recovery dan backup data otomatis'])
        )
    ]

    for c in careers:
        cursor.execute('''
        INSERT INTO careers (slug, title, department, location, job_type, experience, description, requirements, responsibilities, is_published)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', c + (1,))

    # --- FAQS SEED ---
    faqs = [
        (
            'Umum',
            'Mengapa memilih PT. Aksara Cipta Digital (ACD) untuk pembuatan software?',
            'ACD bukan sekadar vendor koding lepas, melainkan mitra konsultan teknologi strategis. Kami mendalami alur proses bisnis Anda terlebih dahulu sebelum membangun arsitektur software. Seluruh aplikasi kami bergaransi, bebas biaya lisensi per user, didukung tim berpengalaman lebih dari 15 tahun, dan memiliki standar keamanan setara perbankan.',
            1
        ),
        (
            'Teknis & Garansi',
            'Berapa lama waktu yang dibutuhkan untuk membangun sebuah aplikasi?',
            'Waktu pengerjaan bervariasi bergantung pada skala dan kompleksitas fitur. Untuk Website Korporat profesional memakan waktu 2-4 minggu. Untuk Aplikasi Mobile atau Sistem Informasi operasional menengah berkisar 1.5 - 3 bulan. Sedangkan untuk implementasi Custom ERP dan E-Government terintegrasi memakan waktu 3 - 6 bulan dengan rilis milestone bertahap menggunakan metode Agile Scrum.',
            2
        ),
        (
            'Garansi & Keamanan',
            'Bagaimana jaminan garansi dan layanan pemeliharaan (maintenance) setelah aplikasi selesai?',
            'Setiap aplikasi yang dibangun oleh ACD mendapatkan jaminan Garansi Bug & Error Free selama masa pemeliharaan resmi. Kami juga menyediakan Service Level Agreement (SLA) dukungan teknis cepat tanggap, update keamanan berkala, pendampingan implementasi pelatihan pengguna (training session), serta opsi perpanjangan maintenance tahunan.',
            3
        ),
        (
            'Hak Milik & Keuangan',
            'Apakah source code (kode sumber) dan hak cipta aplikasi menjadi milik klien?',
            'Ya, 100%. Kami menyerahkan seluruh source code, database, hak kekayaan intelektual (HAKI), serta dokumentasi teknis secara transparan kepada klien setelah proyek selesai dan serah terima tuntas. Perusahaan Anda memiliki kebebasan penuh atas aset digital tersebut tanpa keterikatan lisensi sewa tahunan.',
            4
        ),
        (
            'Metodologi & Konsultasi',
            'Bagaimana cara memulai konsultasi dan berapa biaya estimasi pembuatan aplikasi?',
            'Anda dapat mengklik tombol "Konsultasi Gratis" atau menghubungi WhatsApp resmi kami di pojok kanan bawah. Tim Konsultan Teknis ACD akan menjadwalkan sesi diskusi (online via Zoom/Meet maupun tatap muka) untuk menganalisis kebutuhan Anda dan menyusun Dokumen Penawaran Teknis & Rincian Anggaran Biaya (RAB) secara cuma-cuma tanpa dipungut biaya apa pun.',
            5
        )
    ]

    for f in faqs:
        cursor.execute('''
        INSERT INTO faqs (category, question, answer, sort_order)
        VALUES (?, ?, ?, ?)
        ''', f)

    conn.commit()
    conn.close()
    print("Database initialization and seeding completed successfully!")

if __name__ == '__main__':
    init_db()
    seed_db()
