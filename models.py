import json
import sqlite3
import re
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

def slugify(text):
    """Konversi teks menjadi slug URL aman."""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

class ServiceModel:
    @staticmethod
    def get_all(category=None, only_published=False):
        conn = get_db_connection()
        conditions = []
        params = []
        if category and category != 'Semua':
            conditions.append('category = ?')
            params.append(category)
        if only_published:
            conditions.append('is_published = 1')
        
        query = 'SELECT * FROM services'
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        query += ' ORDER BY id ASC'
        
        rows = conn.execute(query, params).fetchall()
        conn.close()
        result = []
        for r in rows:
            item = dict(r)
            item['features_list'] = json.loads(item['features']) if item.get('features') else []
            item['tech_stack_list'] = json.loads(item['tech_stack']) if item.get('tech_stack') else []
            item['benefits_list'] = json.loads(item['benefits']) if item.get('benefits') else []
            if 'is_published' not in item or item['is_published'] is None:
                item['is_published'] = 1
            result.append(item)
        return result

    @staticmethod
    def get_by_id(service_id):
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM services WHERE id = ?', (service_id,)).fetchone()
        conn.close()
        if not row:
            return None
        res = dict(row)
        res['features_list'] = json.loads(res['features']) if res.get('features') else []
        res['tech_stack_list'] = json.loads(res['tech_stack']) if res.get('tech_stack') else []
        res['benefits_list'] = json.loads(res['benefits']) if res.get('benefits') else []
        if 'is_published' not in res or res['is_published'] is None:
            res['is_published'] = 1
        return res

    @staticmethod
    def get_by_slug(slug, only_published=False):
        conn = get_db_connection()
        if only_published:
            row = conn.execute('SELECT * FROM services WHERE slug = ? AND is_published = 1', (slug,)).fetchone()
        else:
            row = conn.execute('SELECT * FROM services WHERE slug = ?', (slug,)).fetchone()
        conn.close()
        if not row:
            return None
        res = dict(row)
        res['features'] = json.loads(res['features']) if res.get('features') else []
        res['tech_stack'] = json.loads(res['tech_stack']) if res.get('tech_stack') else []
        res['benefits'] = json.loads(res['benefits']) if res.get('benefits') else []
        if 'is_published' not in res or res['is_published'] is None:
            res['is_published'] = 1
        return res

    @staticmethod
    def get_grouped_by_category(only_published=True):
        all_services = ServiceModel.get_all(only_published=only_published)
        grouped = {}
        for s in all_services:
            cat = s['category']
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(s)
        return grouped

    @staticmethod
    def create(slug, category, title, subtitle, icon, summary, features, tech_stack, benefits, is_featured=1, is_published=1):
        conn = get_db_connection()
        cursor = conn.cursor()
        if not slug:
            slug = slugify(title)
        cursor.execute('''
        INSERT INTO services (slug, category, title, subtitle, icon, summary, features, tech_stack, benefits, is_featured, is_published)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            slug,
            category,
            title,
            subtitle or '',
            icon or 'layers',
            summary or '',
            json.dumps(features if isinstance(features, list) else [f.strip() for f in features.splitlines() if f.strip()]),
            json.dumps(tech_stack if isinstance(tech_stack, list) else [t.strip() for t in tech_stack.split(',') if t.strip()]),
            json.dumps(benefits if isinstance(benefits, list) else [b.strip() for b in benefits.splitlines() if b.strip()]),
            1 if is_featured else 0,
            1 if is_published else 0
        ))
        service_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return service_id

    @staticmethod
    def update(service_id, slug, category, title, subtitle, icon, summary, features, tech_stack, benefits, is_featured=1, is_published=1):
        conn = get_db_connection()
        cursor = conn.cursor()
        if not slug:
            slug = slugify(title)
        cursor.execute('''
        UPDATE services
        SET slug = ?, category = ?, title = ?, subtitle = ?, icon = ?, summary = ?, features = ?, tech_stack = ?, benefits = ?, is_featured = ?, is_published = ?
        WHERE id = ?
        ''', (
            slug,
            category,
            title,
            subtitle or '',
            icon or 'layers',
            summary or '',
            json.dumps(features if isinstance(features, list) else [f.strip() for f in features.splitlines() if f.strip()]),
            json.dumps(tech_stack if isinstance(tech_stack, list) else [t.strip() for t in tech_stack.split(',') if t.strip()]),
            json.dumps(benefits if isinstance(benefits, list) else [b.strip() for b in benefits.splitlines() if b.strip()]),
            1 if is_featured else 0,
            1 if is_published else 0,
            service_id
        ))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def toggle_published(service_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE services
        SET is_published = CASE WHEN is_published = 1 THEN 0 ELSE 1 END
        WHERE id = ?
        ''', (service_id,))
        conn.commit()
        row = conn.execute('SELECT is_published, title FROM services WHERE id = ?', (service_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def delete(service_id):
        conn = get_db_connection()
        conn.execute('DELETE FROM services WHERE id = ?', (service_id,))
        conn.commit()
        conn.close()
        return True


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
            item['tech_stack'] = json.loads(item['tech_stack']) if item.get('tech_stack') else []
            item['metrics'] = json.loads(item['metrics']) if item.get('metrics') else {}
            result.append(item)
        return result

    @staticmethod
    def get_by_id(portfolio_id):
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM portfolios WHERE id = ?', (portfolio_id,)).fetchone()
        conn.close()
        if not row:
            return None
        res = dict(row)
        res['tech_stack'] = json.loads(res['tech_stack']) if res.get('tech_stack') else []
        res['metrics'] = json.loads(res['metrics']) if res.get('metrics') else {}
        return res

    @staticmethod
    def get_by_slug(slug):
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM portfolios WHERE slug = ?', (slug,)).fetchone()
        conn.close()
        if not row:
            return None
        res = dict(row)
        res['tech_stack'] = json.loads(res['tech_stack']) if res.get('tech_stack') else []
        res['metrics'] = json.loads(res['metrics']) if res.get('metrics') else {}
        return res

    @staticmethod
    def create(slug, title, category, client_name, client_type, year, summary, challenge, solution, impact, tech_stack, image_url, metrics):
        conn = get_db_connection()
        cursor = conn.cursor()
        if not slug:
            slug = slugify(title)
        
        tech_json = json.dumps(tech_stack if isinstance(tech_stack, list) else [t.strip() for t in str(tech_stack).split(',') if t.strip()])
        metrics_json = json.dumps(metrics if isinstance(metrics, dict) else {})
        
        cursor.execute('''
        INSERT INTO portfolios (slug, title, category, client_name, client_type, year, summary, challenge, solution, impact, tech_stack, image_url, metrics)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (slug, title, category, client_name, client_type, str(year), summary or '', challenge or '', solution or '', impact or '', tech_json, image_url or '', metrics_json))
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return item_id

    @staticmethod
    def update(portfolio_id, slug, title, category, client_name, client_type, year, summary, challenge, solution, impact, tech_stack, image_url, metrics):
        conn = get_db_connection()
        cursor = conn.cursor()
        if not slug:
            slug = slugify(title)
            
        tech_json = json.dumps(tech_stack if isinstance(tech_stack, list) else [t.strip() for t in str(tech_stack).split(',') if t.strip()])
        metrics_json = json.dumps(metrics if isinstance(metrics, dict) else {})

        cursor.execute('''
        UPDATE portfolios
        SET slug = ?, title = ?, category = ?, client_name = ?, client_type = ?, year = ?, summary = ?, challenge = ?, solution = ?, impact = ?, tech_stack = ?, image_url = ?, metrics = ?
        WHERE id = ?
        ''', (slug, title, category, client_name, client_type, str(year), summary or '', challenge or '', solution or '', impact or '', tech_json, image_url or '', metrics_json, portfolio_id))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete(portfolio_id):
        conn = get_db_connection()
        conn.execute('DELETE FROM portfolios WHERE id = ?', (portfolio_id,))
        conn.commit()
        conn.close()
        return True


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
    def get_by_id(blog_id):
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM blog_posts WHERE id = ?', (blog_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_slug(slug):
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM blog_posts WHERE slug = ?', (slug,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(slug, title, category, author, read_time, summary, content, tags, image_url, published_date=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        if not slug:
            slug = slugify(title)
        if not published_date:
            published_date = datetime.now().strftime('%d %B %Y')
            
        cursor.execute('''
        INSERT INTO blog_posts (slug, title, category, author, read_time, summary, content, tags, image_url, published_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (slug, title, category, author or 'Tim Konsultan ACD', read_time or '5 Menit', summary or '', content or '', tags or '', image_url or '', published_date))
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return post_id

    @staticmethod
    def update(blog_id, slug, title, category, author, read_time, summary, content, tags, image_url, published_date):
        conn = get_db_connection()
        cursor = conn.cursor()
        if not slug:
            slug = slugify(title)
        cursor.execute('''
        UPDATE blog_posts
        SET slug = ?, title = ?, category = ?, author = ?, read_time = ?, summary = ?, content = ?, tags = ?, image_url = ?, published_date = ?
        WHERE id = ?
        ''', (slug, title, category, author, read_time, summary, content, tags, image_url, published_date, blog_id))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete(blog_id):
        conn = get_db_connection()
        conn.execute('DELETE FROM blog_posts WHERE id = ?', (blog_id,))
        conn.commit()
        conn.close()
        return True


class CareerModel:
    @staticmethod
    def get_all(only_published=False):
        conn = get_db_connection()
        if only_published:
            rows = conn.execute('SELECT * FROM careers WHERE is_published = 1 ORDER BY id DESC').fetchall()
        else:
            rows = conn.execute('SELECT * FROM careers ORDER BY id DESC').fetchall()
        conn.close()
        res = []
        for r in rows:
            item = dict(r)
            item['requirements'] = json.loads(item['requirements']) if item.get('requirements') else []
            item['responsibilities'] = json.loads(item['responsibilities']) if item.get('responsibilities') else []
            res.append(item)
        return res

    @staticmethod
    def get_by_id(career_id):
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM careers WHERE id = ?', (career_id,)).fetchone()
        conn.close()
        if not row:
            return None
        res = dict(row)
        res['requirements'] = json.loads(res['requirements']) if res.get('requirements') else []
        res['responsibilities'] = json.loads(res['responsibilities']) if res.get('responsibilities') else []
        return res

    @staticmethod
    def get_by_slug(slug, only_published=False):
        conn = get_db_connection()
        if only_published:
            row = conn.execute('SELECT * FROM careers WHERE slug = ? AND is_published = 1', (slug,)).fetchone()
        else:
            row = conn.execute('SELECT * FROM careers WHERE slug = ?', (slug,)).fetchone()
        conn.close()
        if not row:
            return None
        res = dict(row)
        res['requirements'] = json.loads(res['requirements']) if res.get('requirements') else []
        res['responsibilities'] = json.loads(res['responsibilities']) if res.get('responsibilities') else []
        return res

    @staticmethod
    def toggle_published(career_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE careers
        SET is_published = CASE WHEN is_published = 1 THEN 0 ELSE 1 END
        WHERE id = ?
        ''', (career_id,))
        conn.commit()
        cursor.execute('SELECT is_published FROM careers WHERE id = ?', (career_id,))
        row = cursor.fetchone()
        conn.close()
        return row['is_published'] if row else None

    @staticmethod
    def create(slug, title, department, location, job_type, experience, description, requirements, responsibilities, is_published=1):
        conn = get_db_connection()
        cursor = conn.cursor()
        if not slug:
            slug = slugify(title)
            
        req_json = json.dumps(requirements if isinstance(requirements, list) else [r.strip() for r in str(requirements).splitlines() if r.strip()])
        resp_json = json.dumps(responsibilities if isinstance(responsibilities, list) else [r.strip() for r in str(responsibilities).splitlines() if r.strip()])
        
        cursor.execute('''
        INSERT INTO careers (slug, title, department, location, job_type, experience, description, requirements, responsibilities, is_published)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (slug, title, department, location or 'Jakarta / Yogyakarta', job_type or 'Full-time', experience or '', description or '', req_json, resp_json, 1 if is_published else 0))
        c_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return c_id

    @staticmethod
    def update(career_id, slug, title, department, location, job_type, experience, description, requirements, responsibilities, is_published=1):
        conn = get_db_connection()
        cursor = conn.cursor()
        if not slug:
            slug = slugify(title)
            
        req_json = json.dumps(requirements if isinstance(requirements, list) else [r.strip() for r in str(requirements).splitlines() if r.strip()])
        resp_json = json.dumps(responsibilities if isinstance(responsibilities, list) else [r.strip() for r in str(responsibilities).splitlines() if r.strip()])

        cursor.execute('''
        UPDATE careers
        SET slug = ?, title = ?, department = ?, location = ?, job_type = ?, experience = ?, description = ?, requirements = ?, responsibilities = ?, is_published = ?
        WHERE id = ?
        ''', (slug, title, department, location, job_type, experience, description, req_json, resp_json, 1 if is_published else 0, career_id))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete(career_id):
        conn = get_db_connection()
        conn.execute('DELETE FROM careers WHERE id = ?', (career_id,))
        conn.commit()
        conn.close()
        return True


class TestimonialModel:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM testimonials ORDER BY id DESC').fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(testimonial_id):
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM testimonials WHERE id = ?', (testimonial_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(client_name, client_title, company_name, content, rating=5, project_name=''):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO testimonials (client_name, client_title, company_name, content, rating, project_name)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (client_name, client_title or '', company_name, content, int(rating or 5), project_name or ''))
        t_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return t_id

    @staticmethod
    def update(testimonial_id, client_name, client_title, company_name, content, rating=5, project_name=''):
        conn = get_db_connection()
        conn.execute('''
        UPDATE testimonials
        SET client_name = ?, client_title = ?, company_name = ?, content = ?, rating = ?, project_name = ?
        WHERE id = ?
        ''', (client_name, client_title or '', company_name, content, int(rating or 5), project_name or '', testimonial_id))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete(testimonial_id):
        conn = get_db_connection()
        conn.execute('DELETE FROM testimonials WHERE id = ?', (testimonial_id,))
        conn.commit()
        conn.close()
        return True


class FAQModel:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM faqs ORDER BY sort_order ASC, id ASC').fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(faq_id):
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM faqs WHERE id = ?', (faq_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(category, question, answer, sort_order=0):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO faqs (category, question, answer, sort_order)
        VALUES (?, ?, ?, ?)
        ''', (category or 'Umum', question, answer, int(sort_order or 0)))
        f_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return f_id

    @staticmethod
    def update(faq_id, category, question, answer, sort_order=0):
        conn = get_db_connection()
        conn.execute('''
        UPDATE faqs
        SET category = ?, question = ?, answer = ?, sort_order = ?
        WHERE id = ?
        ''', (category or 'Umum', question, answer, int(sort_order or 0), faq_id))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete(faq_id):
        conn = get_db_connection()
        conn.execute('DELETE FROM faqs WHERE id = ?', (faq_id,))
        conn.commit()
        conn.close()
        return True


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
    def get_all(status=None, search=None):
        conn = get_db_connection()
        query = 'SELECT * FROM inquiries WHERE 1=1'
        params = []
        if status and status != 'Semua':
            query += ' AND status = ?'
            params.append(status)
        if search:
            query += ' AND (name LIKE ? OR email LIKE ? OR phone LIKE ? OR company LIKE ? OR message LIKE ?)'
            sp = f'%{search}%'
            params.extend([sp, sp, sp, sp, sp])
        query += ' ORDER BY created_at DESC'
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(inquiry_id):
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM inquiries WHERE id = ?', (inquiry_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def update_status(inquiry_id, status, notes=None):
        conn = get_db_connection()
        if notes is not None:
            conn.execute('UPDATE inquiries SET status = ?, notes = ? WHERE id = ?', (status, notes, inquiry_id))
        else:
            conn.execute('UPDATE inquiries SET status = ? WHERE id = ?', (status, inquiry_id))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete(inquiry_id):
        conn = get_db_connection()
        conn.execute('DELETE FROM inquiries WHERE id = ?', (inquiry_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_stats():
        conn = get_db_connection()
        total = conn.execute('SELECT COUNT(*) FROM inquiries').fetchone()[0]
        baru = conn.execute("SELECT COUNT(*) FROM inquiries WHERE status = 'Baru'").fetchone()[0]
        dihubungi = conn.execute("SELECT COUNT(*) FROM inquiries WHERE status = 'Dihubungi'").fetchone()[0]
        diproses = conn.execute("SELECT COUNT(*) FROM inquiries WHERE status = 'Diproses'").fetchone()[0]
        selesai = conn.execute("SELECT COUNT(*) FROM inquiries WHERE status = 'Selesai'").fetchone()[0]
        conn.close()
        return {
            'total': total,
            'baru': baru,
            'dihubungi': dihubungi,
            'diproses': diproses,
            'selesai': selesai
        }


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

    @staticmethod
    def get_all(limit=100):
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM wa_logs ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def clear_all():
        conn = get_db_connection()
        conn.execute('DELETE FROM wa_logs')
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete(log_id):
        conn = get_db_connection()
        conn.execute('DELETE FROM wa_logs WHERE id = ?', (log_id,))
        conn.commit()
        conn.close()
        return True


class SettingModel:
    @staticmethod
    def get(key, default=None):
        conn = get_db_connection()
        row = conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
        conn.close()
        return row['value'] if row else default

    @staticmethod
    def set(key, value):
        conn = get_db_connection()
        conn.execute('INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?', (key, str(value), str(value)))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute('SELECT key, value FROM settings').fetchall()
        conn.close()
        return {r['key']: r['value'] for r in rows}

    @staticmethod
    def update_many(mapping):
        conn = get_db_connection()
        cursor = conn.cursor()
        for k, v in mapping.items():
            cursor.execute('INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?', (k, str(v), str(v)))
        conn.commit()
        conn.close()
        return True


class SecurityModel:
    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    @staticmethod
    def verify_password(raw_password, stored_password):
        if not raw_password or not stored_password:
            return False
        if str(stored_password).startswith(('scrypt:', 'pbkdf2:')):
            return check_password_hash(stored_password, raw_password)
        # Plain-text legacy fallback
        return raw_password == stored_password

    @staticmethod
    def check_lockout(ip_address):
        """Cek apakah IP sedang terkunci akibat gagal login beruntun."""
        conn = get_db_connection()
        row = conn.execute(
            'SELECT failed_count, locked_until FROM login_lockouts WHERE ip_address = ?',
            (ip_address,)
        ).fetchone()
        conn.close()

        if not row:
            return False, 0, 0

        failed_count = row['failed_count'] or 0
        locked_until_str = row['locked_until']

        if locked_until_str:
            try:
                locked_until = datetime.strptime(locked_until_str, '%Y-%m-%d %H:%M:%S')
                now = datetime.now()
                if locked_until > now:
                    diff_seconds = (locked_until - now).total_seconds()
                    remaining_mins = max(1, int(diff_seconds // 60) + 1)
                    return True, remaining_mins, failed_count
                else:
                    SecurityModel.unlock_ip(ip_address)
                    return False, 0, 0
            except Exception:
                pass

        return False, 0, failed_count

    @staticmethod
    def record_failed_attempt(ip_address, username, user_agent='', max_attempts=3, lockout_minutes=15, reason='Kredensial Tidak Cocok'):
        conn = get_db_connection()
        row = conn.execute('SELECT failed_count FROM login_lockouts WHERE ip_address = ?', (ip_address,)).fetchone()
        now = datetime.now()

        if row:
            new_count = row['failed_count'] + 1
        else:
            new_count = 1

        is_now_locked = (new_count >= max_attempts)
        locked_until_str = None

        if is_now_locked:
            locked_until = now + timedelta(minutes=lockout_minutes)
            locked_until_str = locked_until.strftime('%Y-%m-%d %H:%M:%S')
            event_type = 'LOCKED_OUT'
            details = f'IP diblokir {lockout_minutes} menit karena {new_count}x gagal login. Username: {username or "-"}'
        else:
            event_type = 'LOGIN_FAILED'
            details = f'Percobaan ke-{new_count} dari {max_attempts}. Username: {username or "-"}, Alasan: {reason}'

        conn.execute('''
        INSERT INTO login_lockouts (ip_address, failed_count, locked_until, last_attempt)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(ip_address) DO UPDATE SET
            failed_count = ?,
            locked_until = ?,
            last_attempt = ?
        ''', (
            ip_address, new_count, locked_until_str, now.strftime('%Y-%m-%d %H:%M:%S'),
            new_count, locked_until_str, now.strftime('%Y-%m-%d %H:%M:%S')
        ))

        # Catat ke admin_security_logs
        conn.execute('''
        INSERT INTO admin_security_logs (ip_address, username, event_type, details, user_agent)
        VALUES (?, ?, ?, ?, ?)
        ''', (ip_address, username or 'unknown', event_type, details, user_agent or ''))

        conn.commit()
        conn.close()
        return is_now_locked, lockout_minutes if is_now_locked else 0, new_count

    @staticmethod
    def record_successful_login(ip_address, username, user_agent=''):
        conn = get_db_connection()
        conn.execute('DELETE FROM login_lockouts WHERE ip_address = ?', (ip_address,))
        conn.execute('''
        INSERT INTO admin_security_logs (ip_address, username, event_type, details, user_agent)
        VALUES (?, ?, 'LOGIN_SUCCESS', 'Autentikasi staf/admin berhasil', ?)
        ''', (ip_address, username, user_agent or ''))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def record_security_event(ip_address, username, event_type, details, user_agent=''):
        conn = get_db_connection()
        conn.execute('''
        INSERT INTO admin_security_logs (ip_address, username, event_type, details, user_agent)
        VALUES (?, ?, ?, ?, ?)
        ''', (ip_address, username or 'unknown', event_type, details, user_agent or ''))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def unlock_ip(ip_address):
        conn = get_db_connection()
        conn.execute('DELETE FROM login_lockouts WHERE ip_address = ?', (ip_address,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_recent_logs(limit=100):
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM admin_security_logs ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_active_lockouts():
        conn = get_db_connection()
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rows = conn.execute('SELECT * FROM login_lockouts WHERE locked_until > ? ORDER BY last_attempt DESC', (now_str,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def clear_security_logs():
        conn = get_db_connection()
        conn.execute('DELETE FROM admin_security_logs')
        conn.commit()
        conn.close()
        return True

