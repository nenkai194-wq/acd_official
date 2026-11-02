import json
import sqlite3
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
    def create(name, email, phone, company, service_type, budget_range, message):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO inquiries (name, email, phone, company, service_type, budget_range, message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, phone, company, service_type, budget_range, message))
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
