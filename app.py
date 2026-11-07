import os
import json
import re
import io
import random
from PIL import Image, ImageDraw, ImageFont
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort, flash
from config import Config
from database import init_db, seed_db
from models import (
    ServiceModel,
    PortfolioModel,
    BlogModel,
    CareerModel,
    TestimonialModel,
    FAQModel,
    InquiryModel,
    WALogModel,
    SettingModel,
    SecurityModel
)

app = Flask(__name__)
app.config.from_object(Config)

from translations import TRANSLATIONS

# Ensure database is initialized and seeded
with app.app_context():
    init_db()
    seed_db()

def get_client_ip():
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address and ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()
    return ip_address or '127.0.0.1'

# Security Headers (OWASP Top 10 Hardening)
@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Sesi login telah berakhir atau belum terautentikasi. Silakan login kembali.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def handle_language_preference():
    lang = request.args.get('lang')
    if lang in ['id', 'en']:
        session['lang'] = lang

# Context Processor for global variables & multilingual translations
@app.context_processor
def inject_global_data():
    services_by_cat = ServiceModel.get_grouped_by_category()
    current_lang = session.get('lang', 'id')
    if current_lang not in TRANSLATIONS:
        current_lang = 'id'
    
    t = TRANSLATIONS[current_lang]
    
    def set_lang_url(target_lang):
        return url_for('set_language', lang=target_lang)

    badge_new = 0
    if session.get('admin_logged_in'):
        try:
            badge_new = InquiryModel.get_stats().get('baru', 0)
        except Exception:
            badge_new = 0

    return {
        'config': Config,
        'nav_services': services_by_cat,
        'current_lang': current_lang,
        't': t,
        'set_lang_url': set_lang_url,
        'badge_new_inquiries': badge_new
    }

@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in ['id', 'en']:
        session['lang'] = lang
    referrer = request.referrer
    if referrer and ('127.0.0.1' in referrer or 'localhost' in referrer or '192.168.' in referrer or 'acd.' in referrer):
        return redirect(referrer)
    return redirect(url_for('index'))

# --- PUBLIC ROUTES ---

@app.route('/')
def index():
    featured_portfolios = PortfolioModel.get_all(limit=6)
    recent_blogs = BlogModel.get_all(limit=3)
    testimonials = TestimonialModel.get_all()
    faqs = FAQModel.get_all()
    return render_template(
        'index.html',
        featured_portfolios=featured_portfolios,
        recent_blogs=recent_blogs,
        testimonials=testimonials,
        faqs=faqs
    )

@app.route('/layanan')
def services():
    all_services = ServiceModel.get_all()
    return render_template('services.html', services=all_services, current_category='Semua')

@app.route('/layanan/kategori/<category>')
def services_category(category):
    cat_services = ServiceModel.get_all(category=category)
    return render_template('services.html', services=cat_services, current_category=category)

@app.route('/layanan/<slug>')
def service_detail(slug):
    service = ServiceModel.get_by_slug(slug)
    if not service:
        abort(404)
    return render_template('service_detail.html', service=service)

@app.route('/portofolio')
def portfolio():
    category = request.args.get('category')
    portfolios = PortfolioModel.get_all(category=category)
    return render_template('portfolio.html', portfolios=portfolios, current_category=category or 'Semua')

@app.route('/portofolio/<slug>')
def portfolio_detail(slug):
    item = PortfolioModel.get_by_slug(slug)
    if not item:
        abort(404)
    return render_template('portfolio_detail.html', portfolio=item)

@app.route('/tentang')
@app.route('/tentang-kami')
@app.route('/company-profile')
def about():
    return render_template('about.html')

@app.route('/blog')
def blog():
    search_query = request.args.get('search', '').strip()
    category = request.args.get('category')
    posts = BlogModel.get_all(category=category, search=search_query if search_query else None)
    return render_template('blog.html', posts=posts, search_query=search_query)

@app.route('/blog/<slug>')
def blog_detail(slug):
    post = BlogModel.get_by_slug(slug)
    if not post:
        abort(404)
    return render_template('blog_detail.html', post=post)

@app.route('/karir')
def career():
    careers = CareerModel.get_all()
    return render_template('career.html', careers=careers)

@app.route('/karir/<slug>')
def career_detail(slug):
    career = CareerModel.get_by_slug(slug)
    if not career:
        abort(404)
    return render_template('career_detail.html', career=career)

@app.route('/kontak')
@app.route('/hubungi-kami')
def contact():
    return render_template('contact.html')

# --- REST API ENDPOINTS ---

@app.route('/api/v1/consultation', methods=['POST'])
def api_consultation():
    data = request.get_json(silent=True) or request.form
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    phone = (data.get('phone') or '').strip()
    company = (data.get('company') or '').strip()
    service_type = (data.get('service_type') or 'Aplikasi & Website').strip()
    budget_range = (data.get('budget_range') or '').strip()
    message = (data.get('message') or '').strip()

    if not name or not email or not phone or not message:
        return jsonify({
            'status': 'error',
            'message': 'Mohon lengkapi nama, email, nomor WhatsApp, dan deskripsi kebutuhan.'
        }), 400

    # 1. Validasi Standar Nasional Nomor WhatsApp (tidak boleh ada huruf)
    is_phone_valid, normalized_phone, phone_err = InquiryModel.validate_and_normalize_phone(phone)
    if not is_phone_valid:
        return jsonify({
            'status': 'error',
            'message': phone_err
        }), 400

    # 2. Validasi Format Email
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return jsonify({
            'status': 'error',
            'message': 'Format email tidak valid. Harap masukkan alamat email yang benar (contoh: nama@perusahaan.co.id).'
        }), 400

    # 3. Pembatasan Anti-Spam: Maksimal 2x kirim dalam 1x24 jam per Nomor WA dan Email
    email_count = InquiryModel.count_recent_by_email(email, hours=24)
    if email_count >= 2:
        return jsonify({
            'status': 'error',
            'message': f'Email "{email}" telah mencapai batas maksimal 2x pengiriman dalam 1 x 24 jam untuk pencegahan spam. Silakan coba kembali besok atau hubungi hotline kami langsung.'
        }), 429

    phone_count = InquiryModel.count_recent_by_phone(normalized_phone, hours=24)
    if phone_count >= 2:
        return jsonify({
            'status': 'error',
            'message': f'Nomor WhatsApp "{normalized_phone}" telah mencapai batas maksimal 2x pengiriman dalam 1 x 24 jam untuk pencegahan spam. Silakan coba kembali besok atau hubungi hotline kami langsung.'
        }), 429

    ip_address = get_client_ip()

    inquiry_id = InquiryModel.create(
        name=name,
        email=email,
        phone=normalized_phone,
        company=company,
        service_type=service_type,
        budget_range=budget_range,
        message=message,
        ip_address=ip_address
    )

    remaining = max(0, 2 - (max(email_count, phone_count) + 1))
    return jsonify({
        'status': 'success',
        'message': 'Permintaan konsultasi berhasil dikirim! Tim konsultan ACD akan segera menghubungi Anda.',
        'inquiry_id': inquiry_id,
        'remaining_submissions': remaining
    })

@app.route('/api/v1/track-wa-click', methods=['POST', 'GET'])
def api_track_wa_click():
    ip_address = get_client_ip()
    source = request.args.get('source') or (request.get_json(silent=True) or {}).get('source', 'whatsapp_button')
    
    # Cek batas maksimal pengiriman pesan via WA (maksimal 2x per 24 jam per IP / device)
    wa_count = WALogModel.count_recent_by_ip(ip_address, hours=24)
    if wa_count >= 2:
        return jsonify({
            'status': 'error',
            'allowed': False,
            'count': wa_count,
            'max': 2,
            'message': 'Pemberitahuan: Anda telah mencapai batas maksimal 2x pengiriman pesan WhatsApp dalam waktu 1 x 24 jam untuk kenyamanan bersama dan mencegah spam. Silakan hubungi kami via email resmi info@acd.co.id atau coba kembali besok.'
        }), 429

    WALogModel.record_click(ip_address, source)
    new_count = wa_count + 1
    remaining = max(0, 2 - new_count)

    return jsonify({
        'status': 'success',
        'allowed': True,
        'count': new_count,
        'remaining': remaining,
        'message': f'Pengiriman pesan WhatsApp ke-{new_count} dari kuota maksimal 2x dalam 24 jam.'
    })

@app.route('/api/v1/estimate', methods=['POST'])
def api_estimate():
    data = request.get_json() or {}
    project_type = data.get('project_type', 'web')
    scale = data.get('scale', 'medium')
    timeline = data.get('timeline', 'standard')

    base_min = 20
    base_max = 45

    if project_type == 'website':
        base_min, base_max = 10, 25
    elif project_type == 'web':
        base_min, base_max = 20, 45
    elif project_type == 'mobile':
        base_min, base_max = 35, 65
    elif project_type == 'erp':
        base_min, base_max = 65, 120
    elif project_type == 'egov':
        base_min, base_max = 80, 180

    mult = 1.0
    if scale == 'medium':
        mult = 1.6
    elif scale == 'enterprise':
        mult = 2.5

    if timeline == 'express':
        mult *= 1.2

    final_min = round(base_min * mult)
    final_max = round(base_max * mult)

    est_weeks = '6 - 10 Minggu'
    if project_type == 'website':
        if scale == 'standard':
            est_weeks = '2 - 4 Minggu'
        elif scale == 'medium':
            est_weeks = '4 - 6 Minggu'
        else:
            est_weeks = '6 - 10 Minggu'
    elif project_type == 'web':
        if scale == 'standard':
            est_weeks = '4 - 8 Minggu'
        elif scale == 'medium':
            est_weeks = '8 - 12 Minggu'
        else:
            est_weeks = '14 - 20 Minggu'
    elif project_type == 'mobile':
        if scale == 'standard':
            est_weeks = '6 - 10 Minggu'
        elif scale == 'medium':
            est_weeks = '10 - 14 Minggu'
        else:
            est_weeks = '16 - 22 Minggu'
    elif project_type in ('erp', 'egov'):
        if scale == 'standard':
            est_weeks = '8 - 12 Minggu'
        elif scale == 'medium':
            est_weeks = '12 - 18 Minggu'
        else:
            est_weeks = '18 - 26 Minggu'

    if timeline == 'express':
        est_weeks += ' (Fast-Track Prioritas)'

    return jsonify({
        'status': 'success',
        'estimated_min_idr_million': final_min,
        'estimated_max_idr_million': final_max,
        'formatted': f'Rp {final_min} Juta - Rp {final_max} Juta*',
        'timeline': est_weeks
    })

# --- ADMIN CMS PORTAL & IMAGE CAPTCHA GENERATOR ---

def generate_captcha_image(code):
    width, height = 150, 44
    img = Image.new('RGB', (width, height), color=(10, 15, 29))
    draw = ImageDraw.Draw(img)

    # Random noise lines
    for _ in range(4):
        draw.line(
            [(random.randint(0, width), random.randint(0, height)),
             (random.randint(0, width), random.randint(0, height))],
            fill=(random.randint(50, 90), random.randint(70, 120), random.randint(140, 220)),
            width=1
        )
    # Random dots
    for _ in range(50):
        draw.point(
            (random.randint(0, width), random.randint(0, height)),
            fill=(random.randint(90, 160), random.randint(110, 190), 240)
        )

    try:
        font = ImageFont.truetype('arial.ttf', 24)
    except Exception:
        font = ImageFont.load_default()

    for i, char in enumerate(code):
        char_img = Image.new('RGBA', (30, 36), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((5, 2), char, font=font, fill=(random.randint(210, 255), random.randint(220, 255), 255, 255))
        angle = random.randint(-15, 15)
        char_img = char_img.rotate(angle, expand=1)
        x = 12 + i * 25 + random.randint(-2, 2)
        y = (height - char_img.height) // 2 + random.randint(-2, 2)
        img.paste(char_img, (x, y), char_img)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

@app.route('/admin/captcha-image')
def admin_captcha_image():
    chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
    code = ''.join(random.choices(chars, k=5))
    session['admin_captcha_code'] = code

    img_bytes = generate_captcha_image(code)
    response = app.response_class(img_bytes, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    ip_address = get_client_ip()
    user_agent = request.headers.get('User-Agent', '')

    # 1. Cek apakah IP sedang terkunci / diblokir (Anti Brute-Force)
    is_locked, remaining_mins, failed_count = SecurityModel.check_lockout(ip_address)
    if is_locked:
        return render_template(
            'admin/login.html',
            is_locked=True,
            lockout_remaining=remaining_mins
        ), 429

    error = None
    if request.method == 'POST':
        # 2. Cek Invisible Honeypot Trap (Deteksi Bot / Crawler Otomatis)
        trap_value = (request.form.get('admin_sec_trap') or '').strip()
        if trap_value:
            SecurityModel.record_security_event(
                ip_address, 'bot_crawler', 'BOT_HONEYPOT',
                f'Bot scanner terdeteksi mengisi honeypot trap: "{trap_value}"', user_agent
            )
            SecurityModel.record_failed_attempt(ip_address, 'bot_crawler', user_agent, reason='Honeypot Trap Triggered')
            return render_template(
                'admin/login.html',
                is_locked=False,
                error='Permintaan ditolak oleh sistem keamanan.'
            ), 403

        # 3. Verifikasi Kode CAPTCHA Gambar (Case-Insensitive)
        user_captcha = (request.form.get('captcha_code') or '').strip().upper()
        stored_captcha = (session.get('admin_captcha_code') or '').upper()

        if not user_captcha or user_captcha != stored_captcha:
            is_now_locked, lock_mins, f_cnt = SecurityModel.record_failed_attempt(
                ip_address, request.form.get('username'), user_agent, reason='Kode CAPTCHA Salah'
            )
            if is_now_locked:
                return render_template('admin/login.html', is_locked=True, lockout_remaining=lock_mins), 429
            return render_template(
                'admin/login.html',
                is_locked=False,
                error='Kode verifikasi CAPTCHA gambar tidak cocok. Silakan coba lagi.',
                last_username=request.form.get('username')
            ), 400

        # 4. Verifikasi Kredensial (Username & Password)
        user = (request.form.get('username') or '').strip()
        pwd = (request.form.get('password') or '').strip()

        valid_user = SettingModel.get('admin_username', Config.ADMIN_USERNAME)
        valid_pass = SettingModel.get('admin_password', Config.ADMIN_PASSWORD)

        is_user_ok = (user == valid_user)
        is_pass_ok = SecurityModel.verify_password(pwd, valid_pass)

        if is_user_ok and is_pass_ok:
            # Upgrade plaintext password ke PBKDF2/SHA256 salted hash secara otomatis
            if not str(valid_pass).startswith(('scrypt:', 'pbkdf2:')):
                SettingModel.set('admin_password', SecurityModel.hash_password(valid_pass))

            # Step 1 Lolos -> Lanjut ke Step 2: Otorisasi Ganda (Two-Factor PIN Master) 6 Digit
            session['auth_step1_user'] = user
            session['auth_step1_time'] = datetime.now().isoformat()
            return redirect(url_for('admin_verify_pin'))
        else:
            is_now_locked, lock_mins, f_cnt = SecurityModel.record_failed_attempt(
                ip_address, user, user_agent, max_attempts=3, lockout_minutes=15, reason='Username atau Password Salah'
            )
            if is_now_locked:
                return render_template('admin/login.html', is_locked=True, lockout_remaining=lock_mins), 429
            return render_template(
                'admin/login.html',
                is_locked=False,
                error='Username atau kata sandi yang Anda masukkan salah.',
                last_username=user
            ), 401

    return render_template('admin/login.html', is_locked=False, error=None)

@app.route('/admin/verify-pin', methods=['GET', 'POST'])
def admin_verify_pin():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    user = session.get('auth_step1_user')
    if not user:
        flash('Silakan login dengan username dan kata sandi terlebih dahulu.', 'warning')
        return redirect(url_for('admin_login'))

    ip_address = get_client_ip()
    user_agent = request.headers.get('User-Agent', '')

    # 1. Cek apakah IP sedang terkunci / diblokir (Anti Brute-Force)
    is_locked, remaining_mins, failed_count = SecurityModel.check_lockout(ip_address)
    if is_locked:
        return render_template(
            'admin/verify_2fa.html',
            is_locked=True,
            lockout_remaining=remaining_mins,
            username=user
        ), 429

    error = None
    if request.method == 'POST':
        pin = (request.form.get('security_pin') or '').strip()
        valid_pin = SettingModel.get('admin_pin', Config.ADMIN_PIN)

        if pin == valid_pin:
            # PIN Otorisasi Benar! Masuk ke Halaman Backend Dashboard
            SecurityModel.record_successful_login(ip_address, user, user_agent)
            session.clear()
            session['admin_logged_in'] = True
            session['admin_user'] = user
            session['login_ip'] = ip_address

            flash('Otorisasi Two-Factor PIN berhasil! Selamat datang di Panel CMS ACD.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            is_now_locked, lock_mins, f_cnt = SecurityModel.record_failed_attempt(
                ip_address, user, user_agent, max_attempts=3, lockout_minutes=15, reason='PIN Master 2FA Salah'
            )
            if is_now_locked:
                return render_template(
                    'admin/verify_2fa.html',
                    is_locked=True,
                    lockout_remaining=lock_mins,
                    username=user
                ), 429
            else:
                rem = max(0, 3 - f_cnt)
                return render_template(
                    'admin/verify_2fa.html',
                    is_locked=False,
                    error=f'PIN Otorisasi 6-digit salah. Tersisa {rem} kesempatan sebelum IP diblokir.',
                    username=user
                ), 401

    return render_template('admin/verify_2fa.html', is_locked=False, error=None, username=user)

@app.route('/admin/verify-pin/cancel')
def admin_verify_pin_cancel():
    session.pop('auth_step1_user', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/logout')
def admin_logout():
    user = session.get('admin_user', 'admin')
    ip = get_client_ip()
    SecurityModel.record_security_event(ip, user, 'LOGOUT', 'Sesi staf keluar secara normal', request.headers.get('User-Agent', ''))
    session.clear()
    flash('Anda telah berhasil keluar dari panel manajemen.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    inquiries = InquiryModel.get_all()
    inquiry_stats = InquiryModel.get_stats()
    services = ServiceModel.get_all()
    portfolios = PortfolioModel.get_all()
    blogs = BlogModel.get_all()
    recent_wa_logs = WALogModel.get_all(limit=10)

    return render_template(
        'admin/dashboard.html',
        inquiries=inquiries,
        inquiry_stats=inquiry_stats,
        total_inquiries=len(inquiries),
        total_services=len(services),
        total_portfolios=len(portfolios),
        total_blogs=len(blogs),
        total_wa_logs=len(recent_wa_logs),
        recent_wa_logs=recent_wa_logs
    )

# --- 1. KELOLA LEADS / INQUIRIES ---

@app.route('/admin/inquiries')
@admin_required
def admin_inquiries():
    status = request.args.get('status')
    search = request.args.get('search')
    inquiries = InquiryModel.get_all(status=status, search=search)
    stats = InquiryModel.get_stats()
    return render_template(
        'admin/inquiries.html',
        inquiries=inquiries,
        stats=stats,
        current_status=status or 'Semua',
        search_query=search
    )

@app.route('/admin/inquiries/<int:inquiry_id>/status', methods=['POST'])
@admin_required
def admin_update_inquiry_status(inquiry_id):
    status = request.form.get('status', 'Baru')
    notes = request.form.get('notes')
    InquiryModel.update_status(inquiry_id, status, notes)
    flash(f'Status permintaan #{inquiry_id} berhasil diperbarui menjadi "{status}".', 'success')
    
    redirect_to = request.form.get('redirect_to')
    if redirect_to == 'admin_dashboard':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('admin_inquiries'))

@app.route('/admin/inquiries/<int:inquiry_id>/delete', methods=['POST'])
@admin_required
def admin_delete_inquiry(inquiry_id):
    InquiryModel.delete(inquiry_id)
    flash(f'Data konsultasi #{inquiry_id} berhasil dihapus.', 'info')
    return redirect(url_for('admin_inquiries'))

# --- 2. KELOLA LAYANAN (SERVICES) ---

@app.route('/admin/services')
@admin_required
def admin_services():
    category = request.args.get('category')
    services = ServiceModel.get_all(category=category)
    categories = [
        'Aplikasi & Website',
        'Aplikasi Bisnis ERP',
        'Aplikasi E-Government',
        'Konsultasi & Audit IT',
        'Infrastruktur & Keamanan Cyber'
    ]
    return render_template(
        'admin/services.html',
        services=services,
        categories=categories,
        current_category=category or 'Semua'
    )

@app.route('/admin/services/add', methods=['GET', 'POST'])
@admin_required
def admin_service_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        category = request.form.get('category', '').strip()
        subtitle = request.form.get('subtitle', '').strip()
        icon = request.form.get('icon', 'layers').strip()
        summary = request.form.get('summary', '').strip()
        features = request.form.get('features', '').strip()
        tech_stack = request.form.get('tech_stack', '').strip()
        benefits = request.form.get('benefits', '').strip()
        is_featured = bool(request.form.get('is_featured'))

        if not title or not category or not summary:
            flash('Harap lengkapi judul, kategori, dan ringkasan layanan.', 'danger')
            return render_template('admin/service_form.html', service=None)

        try:
            ServiceModel.create(
                slug=slug,
                category=category,
                title=title,
                subtitle=subtitle,
                icon=icon,
                summary=summary,
                features=features,
                tech_stack=tech_stack,
                benefits=benefits,
                is_featured=is_featured
            )
            flash(f'Layanan "{title}" berhasil ditambahkan!', 'success')
            return redirect(url_for('admin_services'))
        except Exception as e:
            flash(f'Gagal menambahkan layanan: {e}', 'danger')

    return render_template('admin/service_form.html', service=None)

@app.route('/admin/services/<int:service_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_service_edit(service_id):
    service = ServiceModel.get_by_id(service_id)
    if not service:
        flash('Layanan tidak ditemukan.', 'danger')
        return redirect(url_for('admin_services'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        category = request.form.get('category', '').strip()
        subtitle = request.form.get('subtitle', '').strip()
        icon = request.form.get('icon', 'layers').strip()
        summary = request.form.get('summary', '').strip()
        features = request.form.get('features', '').strip()
        tech_stack = request.form.get('tech_stack', '').strip()
        benefits = request.form.get('benefits', '').strip()
        is_featured = bool(request.form.get('is_featured'))

        if not title or not category or not summary:
            flash('Harap lengkapi judul, kategori, dan ringkasan layanan.', 'danger')
            return render_template('admin/service_form.html', service=service)

        try:
            ServiceModel.update(
                service_id=service_id,
                slug=slug,
                category=category,
                title=title,
                subtitle=subtitle,
                icon=icon,
                summary=summary,
                features=features,
                tech_stack=tech_stack,
                benefits=benefits,
                is_featured=is_featured
            )
            flash(f'Layanan "{title}" berhasil diperbarui!', 'success')
            return redirect(url_for('admin_services'))
        except Exception as e:
            flash(f'Gagal memperbarui layanan: {e}', 'danger')

    return render_template('admin/service_form.html', service=service)

@app.route('/admin/services/<int:service_id>/delete', methods=['POST'])
@admin_required
def admin_service_delete(service_id):
    ServiceModel.delete(service_id)
    flash('Layanan berhasil dihapus dari sistem.', 'info')
    return redirect(url_for('admin_services'))

# --- 3. KELOLA PORTOFOLIO (PORTFOLIOS) ---

@app.route('/admin/portfolios')
@admin_required
def admin_portfolios():
    category = request.args.get('category')
    portfolios = PortfolioModel.get_all(category=category)
    return render_template('admin/portfolios.html', portfolios=portfolios, current_category=category or 'Semua')

@app.route('/admin/portfolios/add', methods=['GET', 'POST'])
@admin_required
def admin_portfolio_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        category = request.form.get('category', '').strip()
        client_name = request.form.get('client_name', '').strip()
        client_type = request.form.get('client_type', 'BUMN').strip()
        year = request.form.get('year', '2025').strip()
        summary = request.form.get('summary', '').strip()
        challenge = request.form.get('challenge', '').strip()
        solution = request.form.get('solution', '').strip()
        impact = request.form.get('impact', '').strip()
        tech_stack = request.form.get('tech_stack', '').strip()
        image_url = request.form.get('image_url', '').strip()

        if not title or not client_name or not summary:
            flash('Harap lengkapi nama proyek, nama klien, dan ringkasan studi kasus.', 'danger')
            return render_template('admin/portfolio_form.html', portfolio=None)

        try:
            PortfolioModel.create(
                slug=slug,
                title=title,
                category=category,
                client_name=client_name,
                client_type=client_type,
                year=year,
                summary=summary,
                challenge=challenge,
                solution=solution,
                impact=impact,
                tech_stack=tech_stack,
                image_url=image_url,
                metrics={}
            )
            flash(f'Portofolio "{title}" berhasil ditambahkan!', 'success')
            return redirect(url_for('admin_portfolios'))
        except Exception as e:
            flash(f'Gagal menambahkan portofolio: {e}', 'danger')

    return render_template('admin/portfolio_form.html', portfolio=None)

@app.route('/admin/portfolios/<int:portfolio_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_portfolio_edit(portfolio_id):
    portfolio = PortfolioModel.get_by_id(portfolio_id)
    if not portfolio:
        flash('Portofolio tidak ditemukan.', 'danger')
        return redirect(url_for('admin_portfolios'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        category = request.form.get('category', '').strip()
        client_name = request.form.get('client_name', '').strip()
        client_type = request.form.get('client_type', 'BUMN').strip()
        year = request.form.get('year', '2025').strip()
        summary = request.form.get('summary', '').strip()
        challenge = request.form.get('challenge', '').strip()
        solution = request.form.get('solution', '').strip()
        impact = request.form.get('impact', '').strip()
        tech_stack = request.form.get('tech_stack', '').strip()
        image_url = request.form.get('image_url', '').strip()

        if not title or not client_name or not summary:
            flash('Harap lengkapi nama proyek, nama klien, dan ringkasan studi kasus.', 'danger')
            return render_template('admin/portfolio_form.html', portfolio=portfolio)

        try:
            PortfolioModel.update(
                portfolio_id=portfolio_id,
                slug=slug,
                title=title,
                category=category,
                client_name=client_name,
                client_type=client_type,
                year=year,
                summary=summary,
                challenge=challenge,
                solution=solution,
                impact=impact,
                tech_stack=tech_stack,
                image_url=image_url,
                metrics=portfolio.get('metrics', {})
            )
            flash(f'Portofolio "{title}" berhasil diperbarui!', 'success')
            return redirect(url_for('admin_portfolios'))
        except Exception as e:
            flash(f'Gagal memperbarui portofolio: {e}', 'danger')

    return render_template('admin/portfolio_form.html', portfolio=portfolio)

@app.route('/admin/portfolios/<int:portfolio_id>/delete', methods=['POST'])
@admin_required
def admin_portfolio_delete(portfolio_id):
    PortfolioModel.delete(portfolio_id)
    flash('Portofolio berhasil dihapus dari sistem.', 'info')
    return redirect(url_for('admin_portfolios'))

# --- 4. KELOLA BLOG & ARTIKEL ---

@app.route('/admin/blogs')
@admin_required
def admin_blogs():
    category = request.args.get('category')
    blogs = BlogModel.get_all(category=category)
    return render_template('admin/blogs.html', blogs=blogs, current_category=category or 'Semua')

@app.route('/admin/blogs/add', methods=['GET', 'POST'])
@admin_required
def admin_blog_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        category = request.form.get('category', 'Transformasi Digital').strip()
        author = request.form.get('author', 'Tim Konsultan ACD').strip()
        read_time = request.form.get('read_time', '5 Menit').strip()
        published_date = request.form.get('published_date', '').strip()
        image_url = request.form.get('image_url', '').strip()
        tags = request.form.get('tags', '').strip()
        summary = request.form.get('summary', '').strip()
        content = request.form.get('content', '').strip()

        if not title or not summary or not content:
            flash('Harap lengkapi judul, ringkasan, dan konten artikel.', 'danger')
            return render_template('admin/blog_form.html', post=None)

        try:
            BlogModel.create(
                slug=slug,
                title=title,
                category=category,
                author=author,
                read_time=read_time,
                summary=summary,
                content=content,
                tags=tags,
                image_url=image_url,
                published_date=published_date
            )
            flash(f'Artikel "{title}" berhasil dipublikasikan!', 'success')
            return redirect(url_for('admin_blogs'))
        except Exception as e:
            flash(f'Gagal menambahkan artikel: {e}', 'danger')

    return render_template('admin/blog_form.html', post=None)

@app.route('/admin/blogs/<int:blog_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_blog_edit(blog_id):
    post = BlogModel.get_by_id(blog_id)
    if not post:
        flash('Artikel blog tidak ditemukan.', 'danger')
        return redirect(url_for('admin_blogs'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        category = request.form.get('category', 'Transformasi Digital').strip()
        author = request.form.get('author', 'Tim Konsultan ACD').strip()
        read_time = request.form.get('read_time', '5 Menit').strip()
        published_date = request.form.get('published_date', '').strip()
        image_url = request.form.get('image_url', '').strip()
        tags = request.form.get('tags', '').strip()
        summary = request.form.get('summary', '').strip()
        content = request.form.get('content', '').strip()

        if not title or not summary or not content:
            flash('Harap lengkapi judul, ringkasan, dan konten artikel.', 'danger')
            return render_template('admin/blog_form.html', post=post)

        try:
            BlogModel.update(
                blog_id=blog_id,
                slug=slug,
                title=title,
                category=category,
                author=author,
                read_time=read_time,
                summary=summary,
                content=content,
                tags=tags,
                image_url=image_url,
                published_date=published_date
            )
            flash(f'Artikel "{title}" berhasil diperbarui!', 'success')
            return redirect(url_for('admin_blogs'))
        except Exception as e:
            flash(f'Gagal memperbarui artikel: {e}', 'danger')

    return render_template('admin/blog_form.html', post=post)

@app.route('/admin/blogs/<int:blog_id>/delete', methods=['POST'])
@admin_required
def admin_blog_delete(blog_id):
    BlogModel.delete(blog_id)
    flash('Artikel blog berhasil dihapus.', 'info')
    return redirect(url_for('admin_blogs'))

# --- 5. KELOLA TESTIMONI ---

@app.route('/admin/testimonials', methods=['GET', 'POST'])
@admin_required
def admin_testimonials():
    if request.method == 'POST':
        client_name = request.form.get('client_name', '').strip()
        client_title = request.form.get('client_title', '').strip()
        company_name = request.form.get('company_name', '').strip()
        rating = int(request.form.get('rating', 5))
        project_name = request.form.get('project_name', '').strip()
        content = request.form.get('content', '').strip()

        if not client_name or not company_name or not content:
            flash('Harap lengkapi nama klien, perusahaan, dan isi testimoni.', 'danger')
        else:
            TestimonialModel.create(client_name, client_title, company_name, content, rating, project_name)
            flash('Testimoni klien berhasil ditambahkan!', 'success')
        return redirect(url_for('admin_testimonials'))

    testimonials = TestimonialModel.get_all()
    return render_template('admin/testimonials.html', testimonials=testimonials)

@app.route('/admin/testimonials/<int:testimonial_id>/delete', methods=['POST'])
@admin_required
def admin_testimonial_delete(testimonial_id):
    TestimonialModel.delete(testimonial_id)
    flash('Testimoni berhasil dihapus.', 'info')
    return redirect(url_for('admin_testimonials'))

# --- 6. KELOLA KARIR & LOWONGAN ---

@app.route('/admin/careers')
@admin_required
def admin_careers():
    careers = CareerModel.get_all()
    return render_template('admin/careers.html', careers=careers)

@app.route('/admin/careers/add', methods=['GET', 'POST'])
@admin_required
def admin_career_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        department = request.form.get('department', '').strip()
        location = request.form.get('location', 'Jakarta / Yogyakarta / Hybrid').strip()
        job_type = request.form.get('job_type', 'Full-time').strip()
        experience = request.form.get('experience', '').strip()
        description = request.form.get('description', '').strip()
        requirements = request.form.get('requirements', '').strip()
        responsibilities = request.form.get('responsibilities', '').strip()

        if not title or not department or not description:
            flash('Harap lengkapi posisi, departemen, dan deskripsi pekerjaan.', 'danger')
            return render_template('admin/career_form.html', career=None)

        try:
            CareerModel.create(
                slug=slug,
                title=title,
                department=department,
                location=location,
                job_type=job_type,
                experience=experience,
                description=description,
                requirements=requirements,
                responsibilities=responsibilities
            )
            flash(f'Lowongan "{title}" berhasil dibuka!', 'success')
            return redirect(url_for('admin_careers'))
        except Exception as e:
            flash(f'Gagal menambahkan lowongan: {e}', 'danger')

    return render_template('admin/career_form.html', career=None)

@app.route('/admin/careers/<int:career_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_career_edit(career_id):
    career = CareerModel.get_by_id(career_id)
    if not career:
        flash('Lowongan tidak ditemukan.', 'danger')
        return redirect(url_for('admin_careers'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        department = request.form.get('department', '').strip()
        location = request.form.get('location', '').strip()
        job_type = request.form.get('job_type', 'Full-time').strip()
        experience = request.form.get('experience', '').strip()
        description = request.form.get('description', '').strip()
        requirements = request.form.get('requirements', '').strip()
        responsibilities = request.form.get('responsibilities', '').strip()

        if not title or not department or not description:
            flash('Harap lengkapi posisi, departemen, dan deskripsi pekerjaan.', 'danger')
            return render_template('admin/career_form.html', career=career)

        try:
            CareerModel.update(
                career_id=career_id,
                slug=slug,
                title=title,
                department=department,
                location=location,
                job_type=job_type,
                experience=experience,
                description=description,
                requirements=requirements,
                responsibilities=responsibilities
            )
            flash(f'Lowongan "{title}" berhasil diperbarui!', 'success')
            return redirect(url_for('admin_careers'))
        except Exception as e:
            flash(f'Gagal memperbarui lowongan: {e}', 'danger')

    return render_template('admin/career_form.html', career=career)

@app.route('/admin/careers/<int:career_id>/delete', methods=['POST'])
@admin_required
def admin_career_delete(career_id):
    CareerModel.delete(career_id)
    flash('Lowongan karir berhasil dihapus.', 'info')
    return redirect(url_for('admin_careers'))

# --- 7. KELOLA TANYA JAWAB (FAQ) ---

@app.route('/admin/faqs', methods=['GET', 'POST'])
@admin_required
def admin_faqs():
    if request.method == 'POST':
        category = request.form.get('category', 'Umum').strip()
        question = request.form.get('question', '').strip()
        answer = request.form.get('answer', '').strip()
        sort_order = int(request.form.get('sort_order', 0))

        if not question or not answer:
            flash('Harap lengkapi pertanyaan dan jawaban FAQ.', 'danger')
        else:
            FAQModel.create(category, question, answer, sort_order)
            flash('Pertanyaan FAQ berhasil ditambahkan!', 'success')
        return redirect(url_for('admin_faqs'))

    faqs = FAQModel.get_all()
    return render_template('admin/faqs.html', faqs=faqs)

@app.route('/admin/faqs/<int:faq_id>/delete', methods=['POST'])
@admin_required
def admin_faq_delete(faq_id):
    FAQModel.delete(faq_id)
    flash('Pertanyaan FAQ berhasil dihapus.', 'info')
    return redirect(url_for('admin_faqs'))

# --- 8. LOG WHATSAPP & ANTI-SPAM ---

@app.route('/admin/wa-logs')
@admin_required
def admin_wa_logs():
    logs = WALogModel.get_all(limit=150)
    return render_template('admin/wa_logs.html', logs=logs)

@app.route('/admin/wa-logs/clear', methods=['POST'])
@admin_required
def admin_wa_logs_clear():
    WALogModel.clear_all()
    flash('Seluruh riwayat log WhatsApp berhasil dikosongkan.', 'success')
    return redirect(url_for('admin_wa_logs'))

@app.route('/admin/wa-logs/<int:log_id>/delete', methods=['POST'])
@admin_required
def admin_wa_logs_delete(log_id):
    WALogModel.delete(log_id)
    flash('Log interaksi berhasil dihapus.', 'info')
    return redirect(url_for('admin_wa_logs'))

# --- 9. PUSAT KEAMANAN & AUDIT LOG SISTEM ---

@app.route('/admin/security')
@admin_required
def admin_security():
    logs = SecurityModel.get_recent_logs(limit=100)
    lockouts = SecurityModel.get_active_lockouts()
    return render_template('admin/security.html', logs=logs, lockouts=lockouts)

@app.route('/admin/security/unlock-ip', methods=['POST'])
@admin_required
def admin_security_unlock_ip():
    ip_address = (request.form.get('ip_address') or '').strip()
    if ip_address:
        SecurityModel.unlock_ip(ip_address)
        SecurityModel.record_security_event(
            get_client_ip(), session.get('admin_user'), 'ADMIN_UNLOCKED_IP',
            f'Administrator membuka blokir IP: {ip_address}', request.headers.get('User-Agent', '')
        )
        flash(f'Blokir untuk IP {ip_address} berhasil dibuka.', 'success')
    return redirect(url_for('admin_security'))

@app.route('/admin/security/clear-logs', methods=['POST'])
@admin_required
def admin_security_clear_logs():
    SecurityModel.clear_security_logs()
    flash('Seluruh riwayat audit keamanan berhasil dibersihkan.', 'success')
    return redirect(url_for('admin_security'))

# --- 10. PENGATURAN WEBSITE & PROFIL PERUSAHAAN ---

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    if request.method == 'POST':
        update_data = {
            'company_name': request.form.get('company_name', '').strip(),
            'company_short_name': request.form.get('company_short_name', '').strip(),
            'company_tagline': request.form.get('company_tagline', '').strip(),
            'company_subtagline': request.form.get('company_subtagline', '').strip(),
            'company_email': request.form.get('company_email', '').strip(),
            'company_consultation_email': request.form.get('company_consultation_email', '').strip(),
            'company_phone': request.form.get('company_phone', '').strip(),
            'company_whatsapp': request.form.get('company_whatsapp', '').strip(),
            'company_address': request.form.get('company_address', '').strip(),
            'company_branch': request.form.get('company_branch', '').strip(),
            'admin_username': request.form.get('admin_username', '').strip(),
        }

        new_password = request.form.get('admin_password', '').strip()
        if new_password:
            update_data['admin_password'] = SecurityModel.hash_password(new_password)

        new_pin = request.form.get('admin_pin', '').strip()
        if new_pin:
            update_data['admin_pin'] = new_pin

        valid_updates = {k: v for k, v in update_data.items() if v}
        SettingModel.update_many(valid_updates)

        if valid_updates.get('admin_username'):
            session['admin_user'] = valid_updates['admin_username']

        flash('Pengaturan website, profil perusahaan, dan keamanan akun berhasil disimpan!', 'success')
        return redirect(url_for('admin_settings'))

    settings = SettingModel.get_all()
    return render_template('admin/settings.html', settings=settings)

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html'), 404

if __name__ == '__main__':
    # Running on local port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
