import json
import sqlite3
import re
from datetime import datetime, timedelta
from database import get_db_connection

class ServiceModel:
    @staticmethod
    def get_all(category=None):
        conn = get_db_connection()
        if category:
            rows = conn.execute('SELECT * FROM services WHERE category = ? ORDER BY id ASC', (category,)).fetchall()
        else:
            rows = conn.execute('SELECT * FROM services ORDER BY id ASC').fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_slug(slug):
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM services WHERE slug = ?', (slug,)).fetchone()
        conn.close()
        if not row:
            return None
        res = dict(row)
        res['features'] = json.loads(res['features']) if res['features'] else []
        res['tech_stack'] = json.loads(res['tech_stack']) if res['tech_stack'] else []
        res['benefits'] = json.loads(res['benefits']) if res['benefits'] else []
        return res

    @staticmethod
    def get_grouped_by_category():
        all_services = ServiceModel.get_all()
        grouped = {}
        for s in all_services:
            cat = s['category']
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(s)
        return grouped

class PortfolioModel:
    @staticmethod
    def get_all(category=None, limit=None):
        conn = get_db_connection()
        query = 'SELECT * FROM portfolios'
        params = []
        if category and category != 'Semua':
            query += ' WHERE category = ?'
            params.append(category)
        query += ' ORDER BY id DESC'
        if limit:
            query += f' LIMIT {int(limit)}'
        rows = conn.execute(query, params).fetchall()
        conn.close()
        
        result = []
        for r in rows:
            item = dict(r)
            item['tech_stack'] = json.loads(item['tech_stack']) if item['tech_stack'] else []
            item['metrics'] = json.loads(item['metrics']) if item['metrics'] else {}
            result.append(item)
        return result

    @staticmethod
    def get_by_slug(slug):
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM portfolios WHERE slug = ?', (slug,)).fetchone()
        conn.close()
        if not row:
            return None
        res = dict(row)
        res['tech_stack'] = json.loads(res['tech_stack']) if res['tech_stack'] else []
        res['metrics'] = json.loads(res['metrics']) if res['metrics'] else {}
        return res

class BlogModel:
    @staticmethod
    def get_all(category=None, limit=None, search=None):
        conn = get_db_connection()
        query = 'SELECT * FROM blog_posts WHERE 1=1'
        params = []
        if category and category != 'Semua':
            query += ' AND category = ?'
            params.append(category)
        if search:
            query += ' AND (title LIKE ? OR summary LIKE ? OR tags LIKE ?)'
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param])
        query += ' ORDER BY id DESC'
        if limit:
            query += f' LIMIT {int(limit)}'
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_slug(slug):
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM blog_posts WHERE slug = ?', (slug,)).fetchone()
        conn.close()
        return dict(row) if row else None

class CareerModel:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM careers ORDER BY id ASC').fetchall()
        conn.close()
        res = []
        for r in rows:
            item = dict(r)
            item['requirements'] = json.loads(item['requirements']) if item['requirements'] else []
            item['responsibilities'] = json.loads(item['responsibilities']) if item['responsibilities'] else []
            res.append(item)
        return res

    @staticmethod
    def get_by_slug(slug):
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM careers WHERE slug = ?', (slug,)).fetchone()
        conn.close()
        if not row:
            return None
        res = dict(row)
        res['requirements'] = json.loads(res['requirements']) if res['requirements'] else []
        res['responsibilities'] = json.loads(res['responsibilities']) if res['responsibilities'] else []
        return res

class TestimonialModel:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM testimonials ORDER BY id ASC').fetchall()
        conn.close()
        return [dict(r) for r in rows]

class FAQModel:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM faqs ORDER BY sort_order ASC').fetchall()
        conn.close()
        return [dict(r) for r in rows]

class InquiryModel:
    @staticmethod
    def validate_and_normalize_phone(phone_raw):
        """
        Validasi nomor WhatsApp standar nasional Indonesia:
        - Tidak boleh ada huruf
        - Harus diawali 08... atau 628... / +628...
        - Panjang digit valid 10-14 digit
        - Dinormalisasi ke format standar '08xxxxxxxxxx'
        """
        if not phone_raw:
            return False, None, 'Nomor WhatsApp wajib diisi.'
        
        phone_str = str(phone_raw).strip()
        
        # 1. Cek apakah ada huruf
        if re.search(r'[a-zA-Z]', phone_str):
            return False, None, 'Nomor WhatsApp tidak boleh mengandung huruf. Harap masukkan nomor WhatsApp yang valid.'
        
        # 2. Bersihkan karakter spasi, tanda hubung, titik, kurung
        cleaned = re.sub(r'[\s\-\.\(\)]', '', phone_str)
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
            
        # 3. Harus murni angka
        if not cleaned.isdigit():
            return False, None, 'Nomor WhatsApp hanya boleh berisi angka tanpa karakter aneh atau simbol.'
            
        # 4. Standarisasi awalan ke format nasional 08...
        if cleaned.startswith('628'):
            normalized = '08' + cleaned[3:]
        elif cleaned.startswith('08'):
            normalized = cleaned
        elif cleaned.startswith('8'):
            normalized = '08' + cleaned[1:]
        else:
            return False, None, 'Nomor WhatsApp harus mengikuti standar nasional Indonesia (diawali dengan 08... atau 628...).'
            
        # 5. Panjang digit nomor HP di Indonesia antara 10 hingga 14 digit
        if len(normalized) < 10 or len(normalized) > 14:
            return False, None, f'Panjang nomor WhatsApp tidak valid ({len(normalized)} digit). Standar nasional adalah 10-14 digit (contoh: 08123456789).'
            
        return True, normalized, None

    @staticmethod
    def count_recent_by_email(email, hours=24):
        """Menghitung berapa kali email mengirim dalam kurun waktu X jam terakhir."""
        if not email:
            return 0
        cutoff = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        conn = get_db_connection()
        row = conn.execute(
            'SELECT COUNT(*) as cnt FROM inquiries WHERE LOWER(email) = LOWER(?) AND created_at >= ?',
            (email.strip(), cutoff)
        ).fetchone()
        conn.close()
        return row['cnt'] if row else 0

    @staticmethod
    def count_recent_by_phone(normalized_phone, hours=24):
        """Menghitung berapa kali no WA mengirim dalam kurun waktu X jam terakhir."""
        if not normalized_phone:
            return 0
        cutoff = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        conn = get_db_connection()
        # Mencocokkan nomor ternormalisasi (misal 0812...) dan varian 628...
        alt_phone = '62' + normalized_phone[1:] if normalized_phone.startswith('08') else normalized_phone
        row = conn.execute(
            'SELECT COUNT(*) as cnt FROM inquiries WHERE (phone = ? OR phone = ?) AND created_at >= ?',
            (normalized_phone, alt_phone, cutoff)
        ).fetchone()
        conn.close()
        return row['cnt'] if row else 0

    @staticmethod
    def create(name, email, phone, company, service_type, budget_range, message, ip_address=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO inquiries (name, email, phone, company, service_type, budget_range, message, ip_address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, phone, company, service_type, budget_range, message, ip_address))
        inquiry_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return inquiry_id

    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM inquiries ORDER BY created_at DESC').fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def update_status(inquiry_id, status, notes=None):
        conn = get_db_connection()
        if notes:
            conn.execute('UPDATE inquiries SET status = ?, notes = ? WHERE id = ?', (status, notes, inquiry_id))
        else:
            conn.execute('UPDATE inquiries SET status = ? WHERE id = ?', (status, inquiry_id))
        conn.commit()
        conn.close()
        return True


class WALogModel:
    @staticmethod
    def count_recent_by_ip(ip_address, hours=24):
        """Menghitung berapa kali IP melakukan pengiriman / klik WhatsApp dalam X jam."""
        if not ip_address:
            return 0
        cutoff = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        conn = get_db_connection()
        row = conn.execute(
            'SELECT COUNT(*) as cnt FROM wa_logs WHERE ip_address = ? AND created_at >= ?',
            (ip_address, cutoff)
        ).fetchone()
        conn.close()
        return row['cnt'] if row else 0

    @staticmethod
    def record_click(ip_address, source='floating_wa'):
        """Mencatat interaksi pengiriman / klik WhatsApp."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO wa_logs (ip_address, source) VALUES (?, ?)',
            (ip_address or 'unknown', source)
        )
        conn.commit()
        conn.close()
        return True
