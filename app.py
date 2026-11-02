import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
from config import Config
from database import init_db, seed_db
from models import (
    ServiceModel,
    PortfolioModel,
    BlogModel,
    CareerModel,
    TestimonialModel,
    FAQModel,
    InquiryModel
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
    data = request.get_json() or request.form
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    company = data.get('company', '')
    service_type = data.get('service_type')
    budget_range = data.get('budget_range', '')
    message = data.get('message')

    if not name or not email or not phone or not message:
        return jsonify({
            'status': 'error',
            'message': 'Mohon lengkapi nama, email, nomor WhatsApp, dan deskripsi kebutuhan.'
        }), 400

    inquiry_id = InquiryModel.create(
        name=name,
        email=email,
        phone=phone,
        company=company,
        service_type=service_type or 'Aplikasi & Website',
        budget_range=budget_range,
        message=message
    )

    return jsonify({
        'status': 'success',
        'message': 'Permintaan konsultasi berhasil dikirim! Tim konsultan ACD akan segera menghubungi Anda.',
        'inquiry_id': inquiry_id
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
