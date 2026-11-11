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
    COMPANY_PHONE = "+62 852-8789-8937"
    COMPANY_WHATSAPP = "6285287898937"
    COMPANY_ADDRESS = "Gununggede Kawalu, Kota Tasikmalaya Jawa Barat 46182"
    COMPANY_BRANCH = ""
    
    # Admin Credentials & Security
    ADMIN_USERNAME = os.environ.get('ADMIN_USER') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASS') or 'Cipta!2345'
    ADMIN_PIN = os.environ.get('ADMIN_PIN') or '555556'
    
    # Session & Cookie Security
    SESSION_COOKIE_NAME = 'acd_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ['true', '1']
    PERMANENT_SESSION_LIFETIME = 2700  # 45 menit auto-logout jika idle

