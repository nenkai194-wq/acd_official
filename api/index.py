import sys
import os

# Menambahkan root project directory ke sys.path agar semua modul (config, database, models, dll) terbaca
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# Expose WSGI handler for Vercel Serverless Function
app = app
