import os
import shutil

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Check if running in Vercel or serverless environment
IS_VERCEL = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))

if IS_VERCEL:
    TMP_DB_PATH = '/tmp/acd_database.sqlite'
    SOURCE_DB_PATH = os.path.join(BASE_DIR, 'acd_database.sqlite')
    if os.path.exists(SOURCE_DB_PATH) and not os.path.exists(TMP_DB_PATH):
        try:
            shutil.copyfile(SOURCE_DB_PATH, TMP_DB_PATH)
        except Exception:
            pass
    DATABASE_PATH = TMP_DB_PATH if os.path.exists(TMP_DB_PATH) else SOURCE_DB_PATH
else:
    DATABASE_PATH = os.path.join(BASE_DIR, 'acd_database.sqlite')

class Config:
    BASE_DIR = BASE_DIR
    IS_VERCEL = IS_VERCEL
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'acd-digital-consulting-secret-2025'
    DATABASE_PATH = DATABASE_PATH
    
    # Company Profile Settings
    COMPANY_NAME = "PT Aksara Cipta Digital"
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

