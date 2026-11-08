import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'acd-digital-consulting-secret-2025'
    DATABASE_PATH = os.path.join(BASE_DIR, 'acd_database.sqlite')
    
    # Company Profile Settings
    COMPANY_NAME = "PT. Aksara Cipta Digital"
    COMPANY_SHORT_NAME = "ACD Digital Consulting"
    COMPANY_TAGLINE = "Solusi Software Inovatif & Transformasi Digital Terpercaya"
    COMPANY_SUBTAGLINE = "Jasa Pembuatan Aplikasi Mobile, Web Base, Sistem ERP & E-Government Bergaransi"
    COMPANY_DOMAIN = "acd.co.id"
    COMPANY_EMAIL = "info@acd.co.id"
    COMPANY_CONSULTATION_EMAIL = "konsultasi@acd.co.id"
    COMPANY_PHONE = "+62 21 8299 8765"
    COMPANY_WHATSAPP = "6281288882510"
    COMPANY_ADDRESS = "Gedung Cyber 2 Tower Lt. 18, Jl. H. R. Rasuna Said Blok X-5 No. 13, Kuningan Barat, Jakarta Selatan 12950"
    COMPANY_BRANCH = ""
    
    # Admin Credentials & Security
    ADMIN_USERNAME = os.environ.get('ADMIN_USER') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASS') or 'Cipta!2345'
    ADMIN_PIN = os.environ.get('ADMIN_PIN') or '555556'
    
    # Session & Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 2700  # 45 menit auto-logout jika idle

