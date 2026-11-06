import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
from config import Config
from database import init_db, seed_db
import re
from models import (
    ServiceModel,
    PortfolioModel,
    BlogModel,
    CareerModel,
    TestimonialModel,
    FAQModel,
    InquiryModel,
    WALogModel
)

app = Flask(__name__)
app.config.from_object(Config)

from translations import TRANSLATIONS

# Ensure database is initialized and seeded
with app.app_context():
    init_db()
    seed_db()

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

    return {
        'config': Config,
        'nav_services': services_by_cat,
        'current_lang': current_lang,
        't': t,
        'set_lang_url': set_lang_url
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

    # Ambil IP Pengunjung
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address and ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()

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
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address and ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()
    
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

    base_min = 25
    base_max = 45

    if project_type == 'mobile':
        base_min, base_max = 45, 85
    elif project_type == 'erp':
        base_min, base_max = 75, 160
    elif project_type == 'egov':
        base_min, base_max = 80, 200
    elif project_type == 'website':
        base_min, base_max = 12, 25

    mult = 1.0
    if scale == 'large':
        mult = 1.7
    elif scale == 'enterprise':
        mult = 2.5

    if timeline == 'express':
        mult *= 1.25

    final_min = round(base_min * mult)
    final_max = round(base_max * mult)

    return jsonify({
        'status': 'success',
        'estimated_min_idr_million': final_min,
        'estimated_max_idr_million': final_max,
        'formatted': f'Rp {final_min} Juta - Rp {final_max} Juta*'
    })

# --- ADMIN CMS PORTAL ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    error = None
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if user == Config.ADMIN_USERNAME and pwd == Config.ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Username atau password yang Anda masukkan salah.'

    return render_template('admin/login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    inquiries = InquiryModel.get_all()
    services_count = len(ServiceModel.get_all())
    portfolios_count = len(PortfolioModel.get_all())
    blogs_count = len(BlogModel.get_all())

    return render_template(
        'admin/dashboard.html',
        inquiries=inquiries,
        total_inquiries=len(inquiries),
        total_services=services_count,
        total_portfolios=portfolios_count,
        total_blogs=blogs_count
    )

@app.route('/admin/inquiries')
def admin_inquiries():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    inquiries = InquiryModel.get_all()
    return render_template('admin/inquiries.html', inquiries=inquiries)

@app.route('/admin/inquiries/<int:inquiry_id>/status', methods=['POST'])
def admin_update_inquiry_status(inquiry_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    new_status = request.form.get('status', 'Baru')
    InquiryModel.update_status(inquiry_id, new_status)
    return redirect(url_for('admin_inquiries'))

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html'), 404

if __name__ == '__main__':
    # Running on local port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
