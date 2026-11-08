import os
import json
import re
import io
import time
import random
from PIL import Image, ImageDraw, ImageFont
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort, flash, Response
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

ADMIN_INACTIVITY_TIMEOUT = 15 * 60  # 15 menit (900 detik) batas waktu otomatis logout saat tidak aktif

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Sesi login telah berakhir atau belum terautentikasi. Silakan login kembali.', 'warning')
            return redirect(url_for('admin_login'))
            
        last_activity = session.get('last_activity')
        now = time.time()
        if last_activity and (now - last_activity > ADMIN_INACTIVITY_TIMEOUT):
            user = session.get('admin_user', 'admin')
            ip = get_client_ip()
            user_agent = request.headers.get('User-Agent', '')
            SecurityModel.record_security_event(
                ip, user, 'SESSION_TIMEOUT',
                f'Sesi admin logout otomatis karena tidak aktif selama {int(ADMIN_INACTIVITY_TIMEOUT // 60)} menit (Auto-Logout Protection)',
                user_agent
            )
            session.clear()
            flash(f'Sesi Anda telah logout otomatis karena tidak ada aktivitas selama {int(ADMIN_INACTIVITY_TIMEOUT // 60)} menit demi keamanan sistem. Silakan masuk kembali.', 'warning')
            return redirect(url_for('admin_login'))

        session['last_activity'] = now
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def handle_language_preference():
    lang = request.args.get('lang')
    if lang in ['id', 'en']:
        session['lang'] = lang


def parse_footer_links(raw_text):
    items = []
    for line in (raw_text or '').splitlines():
        line = line.strip()
        if not line:
            continue
        if '|' in line:
            parts = line.split('|', 1)
            items.append({'label': parts[0].strip(), 'url': parts[1].strip()})
        else:
            items.append({'label': line, 'url': '#'})
    return items



def get_seo_data():
    all_s = SettingModel.get_all()
    
    def s_val(k, fallback):
        v = all_s.get(k)
        return v if (v is not None and str(v).strip() != '') else fallback

    meta_title = s_val('seo_meta_title', 'PT. Aksara Cipta Digital | IT Consultant - AI, Software Developer')
    meta_desc = s_val('seo_meta_description', 'PT. Aksara Cipta Digital (ACD) adalah konsultan IT terkemuka dan software house spesialis arsitektur sistem ERP, E-Government, Mobile Apps, dan solusi kecerdasan buatan (AI) terpercaya di Indonesia.')
    meta_keywords = s_val('seo_meta_keywords', 'IT Consultant, Konsultan IT Indonesia, Software Developer Indonesia, Jasa Pembuatan Aplikasi, Jasa Sistem ERP, E-Government SPBE, AI Developer, GIS Geoportal, PT Aksara Cipta Digital, ACD')
    canonical_url = s_val('seo_canonical_url', 'https://acd.co.id').rstrip('/')
    author = s_val('seo_author', 'PT. Aksara Cipta Digital')
    robots = s_val('seo_robots', 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1')
    og_title = s_val('seo_og_title', 'PT. Aksara Cipta Digital - IT Consultant & Enterprise Software House')
    og_desc = s_val('seo_og_description', 'Solusi software inovatif, arsitektur sistem berkinerja tinggi, dan transformasi digital terpercaya untuk Korporasi Swasta, BUMN, dan Pemerintahan di seluruh Indonesia.')
    og_image = s_val('seo_og_image', '/static/images/logo_acd_icon.png')
    og_type = s_val('seo_og_type', 'website')
    twitter_card = s_val('seo_twitter_card', 'summary_large_image')
    google_ver = s_val('seo_google_verification', '')
    bing_ver = s_val('seo_bing_verification', '')
    ga_id = s_val('seo_google_analytics_id', '')
    gtm_id = s_val('seo_gtm_id', '')
    org_type = s_val('seo_organization_type', 'Corporation')

    return {
        'meta_title': meta_title,
        'meta_description': meta_desc,
        'meta_keywords': meta_keywords,
        'canonical_url': canonical_url,
        'author': author,
        'robots': robots,
        'og_title': og_title,
        'og_description': og_desc,
        'og_image': og_image,
        'og_type': og_type,
        'twitter_card': twitter_card,
        'google_verification': google_ver,
        'bing_verification': bing_ver,
        'google_analytics_id': ga_id,
        'gtm_id': gtm_id,
        'organization_type': org_type
    }

def get_contact_data():
    all_s = SettingModel.get_all()
    
    def s_val(k, fallback):
        v = all_s.get(k)
        return v if (v is not None and str(v).strip() != '') else fallback

    hero_badge = s_val('contact_hero_badge', 'Hubungi Kami')
    hero_title = s_val('contact_hero_title', 'Konsultasi Gratis Rancang Bangun Software')
    hero_subtitle = s_val('contact_hero_subtitle', 'Diskusikan kebutuhan aplikasi atau sistem perusahaan Anda dengan System Analyst senior kami. Kami siap memberikan masukan arsitektur dan estimasi anggaran tanpa biaya.')
    form_badge = s_val('contact_form_badge', 'FORMULIR KEBUTUHAN')
    form_title = s_val('contact_form_title', 'Kirimkan Deskripsi Kebutuhan Anda')
    form_subtitle = s_val('contact_form_subtitle', 'Kami menghargai kerahasiaan data bisnis Anda (Non-Disclosure Agreement siap ditandatangani)')
    submit_btn = s_val('contact_submit_btn', 'Kirim Formulir Konsultasi Gratis')
    wa_label = s_val('contact_wa_label', '+62 812-8888-2510 (Fast Response)')
    wa_number = s_val('contact_wa_number', '6281288882510')
    email = s_val('contact_email', 'info@acd.co.id')
    phone = s_val('contact_phone', '+62 21 8299 8765')
    hours = s_val('contact_hours', 'Senin - Jumat: 08:30 - 17:00 WIB')
    address_main = s_val('contact_address_main', 'Gununggede Kawalu, Kota Tasikmalaya Jawa Barat 46182')
    address_branch = ''
    
    categories_raw = s_val('contact_categories', "Aplikasi Bisnis ERP (HRIS, Payroll, Akuntansi, Stok)\nAplikasi E-Government (Smart Governance / SPBE)\nMobile Apps (Android & iOS Native/Flutter)\nWeb Base App & Sistem Informasi Operasional\nWebsite Korporat & Portal Berita\nGIS & Geoportal Spasial\nIntegrasi Sistem & API Enterprise\nKonsultasi & Audit IT")
    categories_list = [line.strip() for line in categories_raw.splitlines() if line.strip()]

    budget_raw = s_val('contact_budget_ranges', "Di bawah Rp 50 Juta\nRp 50 Juta - Rp 150 Juta\nRp 150 Juta - Rp 300 Juta\n> Rp 300 Juta (Enterprise Scale)")
    budget_list = [line.strip() for line in budget_raw.splitlines() if line.strip()]

    return {
        'hero_badge': hero_badge,
        'hero_title': hero_title,
        'hero_subtitle': hero_subtitle,
        'form_badge': form_badge,
        'form_title': form_title,
        'form_subtitle': form_subtitle,
        'submit_btn': submit_btn,
        'wa_label': wa_label,
        'wa_number': wa_number,
        'email': email,
        'phone': phone,
        'hours': hours,
        'address_main': address_main,
        'address_branch': address_branch,
        'categories': categories_list,
        'categories_raw': categories_raw,
        'budget_ranges': budget_list,
        'budget_raw': budget_raw
    }

def get_footer_data():
    all_s = SettingModel.get_all()
    
    def s_val(k, fallback):
        v = all_s.get(k)
        return v if (v is not None and str(v).strip() != '') else fallback

    brand_name = s_val('footer_brand_name', 'AKSARA CIPTA DIGITAL')
    brand_tagline = s_val('footer_brand_tagline', 'IT Consultant - AI, Software Developer')
    about = s_val('footer_about', 'PT. Aksara Cipta Digital adalah perusahaan konsultan IT dan software house yang berpengalaman membangun ratusan aplikasi terbaik untuk berbagai sektor bisnis swasta, BUMN, dan institusi pemerintahan di seluruh Indonesia.')
    address_main = s_val('footer_address_main', 'Gununggede Kawalu, Kota Tasikmalaya Jawa Barat 46182')
    address_branch = ''
    phone = s_val('footer_phone', '+62 21 8299 8765')
    email = s_val('footer_email', 'info@acd.co.id')
    whatsapp = s_val('footer_whatsapp', '6281288882510')

    col2_title = s_val('footer_col2_title', 'Aplikasi & Website')
    col2_raw = s_val('footer_col2_links', "Mobile Apps (Android & iOS) | /layanan/mobile-apps\nWeb Base Apps | /layanan/sistem-informasi\nWebsite Korporat | /layanan/website-korporat\nGeographic Information System (GIS) | /layanan/gis-geoportal\nIntegrasi Sistem & API | /layanan/integrasi-sistem\nSemua Aplikasi & Website \u2192 | /layanan/kategori/Aplikasi%20&%20Website")

    col3_title = s_val('footer_col3_title', 'Aplikasi Bisnis ERP')
    col3_raw = s_val('footer_col3_links', "HRIS / Kepegawaian | /layanan/erp-hris-kepegawaian\nPresensi & Geofencing | /layanan/erp-presensi-absensi\nPayroll & Pajak PPh21 | /layanan/erp-payroll-penggajian\nAkuntansi & Keuangan | /layanan/erp-accounting-keuangan\nAsset Management | /layanan/erp-asset-management\nWarehouse Management | /layanan/erp-warehouse-management\nDocument Management | /layanan/erp-document-management\nDashboard Eksekutif | /layanan/erp-dashboard-eksekutif")

    col4_title = s_val('footer_col4_title', 'Aplikasi E-Gov')
    col4_raw = s_val('footer_col4_links', "Website Pemerintah Daerah | /layanan/egov-portal-daerah\ne-Data Sektoral SDI | /layanan/egov-data-sektoral\ne-Planning Internal & Pokir | /layanan/egov-e-planning-musrenbang\ne-Monev & e-SAKIP | /layanan/egov-e-monev-sakip\ne-Lapor & Pengaduan Warga | /layanan/egov-e-lapor-pengaduan\ne-Perizinan MPP TTE | /layanan/egov-e-perizinan-mpp")

    about_title = s_val('footer_about_title', 'Tentang Kami')
    about_raw = s_val('footer_about_links', "Profil Perusahaan ACD | /tentang-kami\nStudi Kasus & Portofolio | /portofolio\nKarir di ACD | /karir\nTanya Jawab (FAQ) | /faq")

    security_label = s_val('footer_security_label', 'Standar Keamanan & Mutu:')
    badge1 = s_val('footer_badge1', 'ISO 27001 Certified')
    badge2 = s_val('footer_badge2', 'OWASP Top 10 Compliant')
    badge3 = s_val('footer_badge3', 'SLA 99.9% Uptime Support')
    support_text = s_val('footer_support_text', 'Layanan Konsultasi & Aduan:')
    support_label = s_val('footer_support_label', 'WhatsApp 24/7 Support')

    copyright_text = s_val('footer_copyright', '\u00a9 2025 PT. Aksara Cipta Digital (acd.co.id). All rights reserved.')
    privacy_label = s_val('footer_privacy_label', 'Kebijakan Privasi')
    privacy_url = s_val('footer_privacy_url', '/tentang-kami')
    terms_label = s_val('footer_terms_label', 'Syarat & Ketentuan Layanan')
    terms_url = s_val('footer_terms_url', '/tentang-kami')
    consult_label = s_val('footer_consult_label', 'Hubungi Konsultan')
    consult_url = s_val('footer_consult_url', '/kontak')

    return {
        'brand_name': brand_name,
        'brand_tagline': brand_tagline,
        'about': about,
        'address_main': address_main,
        'address_branch': address_branch,
        'phone': phone,
        'email': email,
        'whatsapp': whatsapp,
        'col2_title': col2_title,
        'col2_links': parse_footer_links(col2_raw),
        'col2_raw': col2_raw,
        'col3_title': col3_title,
        'col3_links': parse_footer_links(col3_raw),
        'col3_raw': col3_raw,
        'col4_title': col4_title,
        'col4_links': parse_footer_links(col4_raw),
        'col4_raw': col4_raw,
        'about_title': about_title,
        'about_links': parse_footer_links(about_raw),
        'about_raw': about_raw,
        'security_label': security_label,
        'badge1': badge1,
        'badge2': badge2,
        'badge3': badge3,
        'support_text': support_text,
        'support_label': support_label,
        'copyright': copyright_text,
        'privacy_label': privacy_label,
        'privacy_url': privacy_url,
        'terms_label': terms_label,
        'terms_url': terms_url,
        'consult_label': consult_label,
        'consult_url': consult_url,
    }

# Context Processor for global variables & multilingual translations
@app.context_processor
def inject_global_data():
    services_by_cat = ServiceModel.get_grouped_by_category(only_published=True)
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
        'badge_new_inquiries': badge_new,
        'admin_inactivity_timeout': ADMIN_INACTIVITY_TIMEOUT,
        'footer': get_footer_data(),
        'contact_cfg': get_contact_data(),
        'seo': get_seo_data()
    }

@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in ['id', 'en']:
        session['lang'] = lang
    referrer = request.referrer
    if referrer and ('127.0.0.1' in referrer or 'localhost' in referrer or '192.168.' in referrer or 'acd.' in referrer):
        return redirect(referrer)
    return redirect(url_for('index'))


# --- SEO ENDPOINTS: SITEMAP & ROBOTS ---

@app.route('/sitemap.xml', methods=['GET'])
def sitemap_xml():
    base_url = SettingModel.get('seo_canonical_url', 'https://acd.co.id').rstrip('/')
    services = ServiceModel.get_all(only_published=True)
    portfolios = PortfolioModel.get_all()
    careers = CareerModel.get_all(only_published=True)
    
    pages = [
        {'loc': f"{base_url}/", 'changefreq': 'daily', 'priority': '1.0'},
        {'loc': f"{base_url}/layanan", 'changefreq': 'weekly', 'priority': '0.9'},
        {'loc': f"{base_url}/portofolio", 'changefreq': 'weekly', 'priority': '0.9'},
        {'loc': f"{base_url}/tentang-kami", 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': f"{base_url}/karir", 'changefreq': 'weekly', 'priority': '0.8'},
        {'loc': f"{base_url}/kontak", 'changefreq': 'monthly', 'priority': '0.8'},
    ]
    for s in services:
        pages.append({'loc': f"{base_url}/layanan/{s['slug']}", 'changefreq': 'weekly', 'priority': '0.8'})
    for p in portfolios:
        pages.append({'loc': f"{base_url}/portofolio/{p['slug']}", 'changefreq': 'monthly', 'priority': '0.7'})
    for c in careers:
        pages.append({'loc': f"{base_url}/karir/{c['slug']}", 'changefreq': 'weekly', 'priority': '0.6'})

    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for page in pages:
        xml_lines.append('  <url>')
        xml_lines.append(f"    <loc>{page['loc']}</loc>")
        xml_lines.append(f"    <changefreq>{page['changefreq']}</changefreq>")
        xml_lines.append(f"    <priority>{page['priority']}</priority>")
        xml_lines.append('  </url>')
    xml_lines.append('</urlset>')

    return Response('\n'.join(xml_lines), mimetype='application/xml')

@app.route('/robots.txt', methods=['GET'])
def robots_txt():
    base_url = SettingModel.get('seo_canonical_url', 'https://acd.co.id').rstrip('/')
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/

Sitemap: {base_url}/sitemap.xml
"""
    return Response(content, mimetype='text/plain')

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
    all_services = ServiceModel.get_all(only_published=True)
    return render_template('services.html', services=all_services, current_category='Semua')

@app.route('/layanan/kategori/<category>')
def services_category(category):
    cat_services = ServiceModel.get_all(category=category, only_published=True)
    return render_template('services.html', services=cat_services, current_category=category)

@app.route('/layanan/<slug>')
def service_detail(slug):
    is_admin = session.get('admin_logged_in', False)
    service = ServiceModel.get_by_slug(slug, only_published=not is_admin)
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
    careers = CareerModel.get_all(only_published=True)
    return render_template('career.html', careers=careers)

@app.route('/karir/<slug>')
def career_detail(slug):
    # Admin preview allows viewing unpublished
    is_admin = bool(session.get('admin_logged_in'))
    career = CareerModel.get_by_slug(slug, only_published=not is_admin)
    if not career:
        abort(404)
    return render_template('career_detail.html', career=career)

@app.route('/faq')
def faq():
    return redirect('/#faq')

@app.route('/hubungi-kami', methods=['GET', 'POST'])
@app.route('/kontak', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        company = request.form.get('company', '').strip()
        service_type = request.form.get('service_type', 'Aplikasi & Website').strip()
        budget_range = request.form.get('budget_range', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not phone or not message:
            flash('Mohon lengkapi semua kolom wajib yang bertanda bintang (*).', 'error')
            return render_template('contact.html')

        is_phone_valid, normalized_phone, phone_err = InquiryModel.validate_and_normalize_phone(phone)
        if not is_phone_valid:
            flash(phone_err, 'error')
            return render_template('contact.html')

        if InquiryModel.count_recent_by_email(email, hours=24) >= 2 or InquiryModel.count_recent_by_phone(normalized_phone, hours=24) >= 2:
            flash('Batas maksimal pengiriman (2x dalam 24 jam) telah tercapai untuk nomor WhatsApp atau Email ini.', 'error')
            return render_template('contact.html')

        InquiryModel.create(
            name=name,
            email=email,
            phone=normalized_phone,
            company=company,
            service_type=service_type,
            budget_range=budget_range,
            message=message,
            ip_address=get_client_ip()
        )
        flash('Terima kasih! Formulir Kebutuhan Anda telah berhasil dikirim ke tim konsultan ACD. Kami akan segera menghubungi Anda.', 'success')
        return redirect(url_for('contact'))

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
            session['last_activity'] = time.time()

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
    reason = request.args.get('reason')
    if reason == 'timeout':
        event_type = 'SESSION_TIMEOUT'
        event_note = f'Sesi admin logout otomatis karena tidak aktif selama {int(ADMIN_INACTIVITY_TIMEOUT // 60)} menit (Inactivity Watchdog)'
        flash_msg = f'Sesi Anda telah logout otomatis karena tidak ada aktivitas selama {int(ADMIN_INACTIVITY_TIMEOUT // 60)} menit demi keamanan sistem. Silakan masuk kembali.'
        flash_cat = 'warning'
    else:
        event_type = 'LOGOUT'
        event_note = 'Sesi staf keluar secara normal'
        flash_msg = 'Anda telah berhasil keluar dari panel manajemen.'
        flash_cat = 'info'

    SecurityModel.record_security_event(ip, user, event_type, event_note, request.headers.get('User-Agent', ''))
    session.clear()
    flash(flash_msg, flash_cat)
    return redirect(url_for('admin_login'))

@app.route('/admin/ping-session', methods=['POST'])
@admin_required
def admin_ping_session():
    return jsonify({
        'status': 'ok',
        'refreshed_at': time.time(),
        'timeout_seconds': ADMIN_INACTIVITY_TIMEOUT
    })

@app.route('/admin/session-status')
def admin_session_status():
    if not session.get('admin_logged_in'):
        return jsonify({'logged_in': False, 'remaining': 0})
    last_act = session.get('last_activity', time.time())
    elapsed = time.time() - last_act
    remaining = max(0, int(ADMIN_INACTIVITY_TIMEOUT - elapsed))
    return jsonify({
        'logged_in': True,
        'remaining': remaining,
        'timeout_total': ADMIN_INACTIVITY_TIMEOUT
    })

@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    inquiries = InquiryModel.get_all()
    inquiry_stats = InquiryModel.get_stats()
    services = ServiceModel.get_all()
    portfolios = PortfolioModel.get_all()
    careers = CareerModel.get_all()
    recent_wa_logs = WALogModel.get_all(limit=10)

    return render_template(
        'admin/dashboard.html',
        inquiries=inquiries,
        inquiry_stats=inquiry_stats,
        total_inquiries=len(inquiries),
        total_services=len(services),
        total_portfolios=len(portfolios),
        total_careers=len(careers),
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
    status_filter = request.args.get('status')  # 'tayang', 'draft', or None
    q = request.args.get('q', '').strip().lower()
    
    all_services = ServiceModel.get_all(category=category)
    
    services = all_services
    if status_filter == 'tayang':
        services = [s for s in services if s.get('is_published') == 1]
    elif status_filter == 'draft':
        services = [s for s in services if s.get('is_published') == 0]
        
    if q:
        services = [s for s in services if q in s['title'].lower() or q in (s.get('subtitle') or '').lower() or q in (s.get('summary') or '').lower() or q in s['category'].lower()]

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
        current_category=category or 'Semua',
        current_status=status_filter or 'semua',
        search_query=q
    )

@app.route('/admin/services/<int:service_id>/toggle-status', methods=['POST'])
@admin_required
def admin_service_toggle_status(service_id):
    updated = ServiceModel.toggle_published(service_id)
    if updated:
        status_text = 'TAYANG di Website Publik' if updated['is_published'] == 1 else 'TIDAK TAYANG (Disembunyikan dari Publik)'
        flash(f'Status layanan "{updated["title"]}" berhasil diubah menjadi: {status_text}.', 'success')
    else:
        flash('Layanan tidak ditemukan.', 'danger')
    return redirect(request.referrer or url_for('admin_services'))

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
        is_published = int(request.form.get('is_published', 1))

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
                is_featured=is_featured,
                is_published=is_published
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
        is_published = int(request.form.get('is_published', 1))

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
                is_featured=is_featured,
                is_published=is_published
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
    q = request.args.get('q', '').strip().lower()
    portfolios = PortfolioModel.get_all(category=category)
    if q:
        portfolios = [p for p in portfolios if q in p['title'].lower() or q in p['client_name'].lower() or q in p['category'].lower() or q in (p.get('summary') or '').lower()]
    categories = ['E-Government', 'Aplikasi Mobile', 'ERP & HRIS', 'Website Korporat', 'Sistem Informasi']
    return render_template(
        'admin/portfolios.html',
        portfolios=portfolios,
        categories=categories,
        current_category=category or 'Semua',
        search_query=q
    )

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
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('q', '').strip()
    
    all_careers = CareerModel.get_all(only_published=False)
    
    # Filter
    careers = []
    for c in all_careers:
        # Status match
        if status_filter == 'tayang' and not c.get('is_published'):
            continue
        if status_filter == 'draft' and c.get('is_published'):
            continue
            
        # Search match
        if search_query:
            q = search_query.lower()
            match = (q in c.get('title', '').lower() or
                     q in c.get('department', '').lower() or
                     q in c.get('location', '').lower())
            if not match:
                continue
        careers.append(c)
        
    counts = {
        'total': len(all_careers),
        'tayang': len([c for c in all_careers if c.get('is_published')]),
        'draft': len([c for c in all_careers if not c.get('is_published')])
    }
    return render_template('admin/careers.html', careers=careers, counts=counts, current_status=status_filter, current_q=search_query)

@app.route('/admin/careers/<int:career_id>/toggle-status', methods=['POST'])
@admin_required
def admin_career_toggle_status(career_id):
    new_status = CareerModel.toggle_published(career_id)
    if new_status is None:
        flash('Lowongan tidak ditemukan.', 'danger')
    else:
        status_text = 'Ditayangkan di website publik' if new_status == 1 else 'Disembunyikan (Tidak Tayang)'
        flash(f'Status lowongan berhasil diubah menjadi: {status_text}', 'success')
    return redirect(request.referrer or url_for('admin_careers'))

@app.route('/admin/careers/add', methods=['GET', 'POST'])
@admin_required
def admin_career_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        department = request.form.get('department', '').strip()
        location = request.form.get('location', 'Onsite / Hybrid / Remote').strip()
        job_type = request.form.get('job_type', 'Full-time').strip()
        experience = request.form.get('experience', '').strip()
        description = request.form.get('description', '').strip()
        requirements = request.form.get('requirements', '').strip()
        responsibilities = request.form.get('responsibilities', '').strip()
        is_published = int(request.form.get('is_published', 1))

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
                responsibilities=responsibilities,
                is_published=is_published
            )
            flash(f'Lowongan "{title}" berhasil disimpan ({ "Tayang" if is_published else "Draft / Tidak Tayang" })!', 'success')
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
        is_published = int(request.form.get('is_published', 1))

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
                responsibilities=responsibilities,
                is_published=is_published
            )
            flash(f'Lowongan "{title}" berhasil diperbarui ({ "Tayang" if is_published else "Draft / Tidak Tayang" })!', 'success')
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



# --- KELOLA FORM KONTAK & KONSULTASI ---

@app.route('/admin/contact-form', methods=['GET', 'POST'])
@admin_required
def admin_contact_form():
    if request.method == 'POST':
        updates = {
            'contact_hero_badge': request.form.get('contact_hero_badge', '').strip(),
            'contact_hero_title': request.form.get('contact_hero_title', '').strip(),
            'contact_hero_subtitle': request.form.get('contact_hero_subtitle', '').strip(),
            'contact_form_badge': request.form.get('contact_form_badge', '').strip(),
            'contact_form_title': request.form.get('contact_form_title', '').strip(),
            'contact_form_subtitle': request.form.get('contact_form_subtitle', '').strip(),
            'contact_submit_btn': request.form.get('contact_submit_btn', '').strip(),
            'contact_wa_label': request.form.get('contact_wa_label', '').strip(),
            'contact_wa_number': request.form.get('contact_wa_number', '').strip(),
            'contact_email': request.form.get('contact_email', '').strip(),
            'contact_phone': request.form.get('contact_phone', '').strip(),
            'contact_hours': request.form.get('contact_hours', '').strip(),
            'contact_address_main': request.form.get('contact_address_main', '').strip(),
            'contact_categories': request.form.get('contact_categories', '').strip(),
            'contact_budget_ranges': request.form.get('contact_budget_ranges', '').strip(),
        }
        SettingModel.update_many(updates)
        flash('Pengaturan konten, opsi dropdown, dan informasi formulir kontak berhasil diperbarui!', 'success')
        return redirect(url_for('admin_contact_form'))

    contact_data = get_contact_data()
    inquiries_count = InquiryModel.get_stats().get('total', 0)
    recent_inquiries = InquiryModel.get_all()[:6]
    return render_template('admin/contact_form.html', contact=contact_data, total_inquiries=inquiries_count, recent_inquiries=recent_inquiries)

@app.route('/admin/contact-form/reset-defaults', methods=['POST'])
@admin_required
def admin_contact_form_reset_defaults():
    defaults = {
        'contact_hero_badge': 'Hubungi Kami',
        'contact_hero_title': 'Konsultasi Gratis Rancang Bangun Software',
        'contact_hero_subtitle': 'Diskusikan kebutuhan aplikasi atau sistem perusahaan Anda dengan System Analyst senior kami. Kami siap memberikan masukan arsitektur dan estimasi anggaran tanpa biaya.',
        'contact_form_badge': 'FORMULIR KEBUTUHAN',
        'contact_form_title': 'Kirimkan Deskripsi Kebutuhan Anda',
        'contact_form_subtitle': 'Kami menghargai kerahasiaan data bisnis Anda (Non-Disclosure Agreement siap ditandatangani)',
        'contact_submit_btn': 'Kirim Formulir Konsultasi Gratis',
        'contact_wa_label': '+62 812-8888-2510 (Fast Response)',
        'contact_wa_number': '6281288882510',
        'contact_email': 'info@acd.co.id',
        'contact_phone': '+62 21 8299 8765',
        'contact_hours': 'Senin - Jumat: 08:30 - 17:00 WIB',
        'contact_address_main': 'Gununggede Kawalu, Kota Tasikmalaya Jawa Barat 46182',
        'contact_address_branch': '',
        'contact_categories': "Aplikasi Bisnis ERP (HRIS, Payroll, Akuntansi, Stok)\nAplikasi E-Government (Smart Governance / SPBE)\nMobile Apps (Android & iOS Native/Flutter)\nWeb Base App & Sistem Informasi Operasional\nWebsite Korporat & Portal Berita\nGIS & Geoportal Spasial\nIntegrasi Sistem & API Enterprise\nKonsultasi & Audit IT",
        'contact_budget_ranges': "Di bawah Rp 50 Juta\nRp 50 Juta - Rp 150 Juta\nRp 150 Juta - Rp 300 Juta\n> Rp 300 Juta (Enterprise Scale)"
    }
    SettingModel.update_many(defaults)
    flash('Pengaturan form kontak berhasil dikembalikan ke standar awal PT. Aksara Cipta Digital.', 'info')
    return redirect(url_for('admin_contact_form'))

# --- KELOLA FOOTER WEBSITE ---

@app.route('/admin/footer', methods=['GET', 'POST'])
@admin_required
def admin_footer():
    if request.method == 'POST':
        updates = {
            'footer_brand_name': request.form.get('footer_brand_name', '').strip(),
            'footer_brand_tagline': request.form.get('footer_brand_tagline', '').strip(),
            'footer_about': request.form.get('footer_about', '').strip(),
            'footer_address_main': request.form.get('footer_address_main', '').strip(),
            'footer_phone': request.form.get('footer_phone', '').strip(),
            'footer_email': request.form.get('footer_email', '').strip(),
            'footer_whatsapp': request.form.get('footer_whatsapp', '').strip(),
            'footer_col2_title': request.form.get('footer_col2_title', '').strip(),
            'footer_col2_links': request.form.get('footer_col2_links', '').strip(),
            'footer_col3_title': request.form.get('footer_col3_title', '').strip(),
            'footer_col3_links': request.form.get('footer_col3_links', '').strip(),
            'footer_col4_title': request.form.get('footer_col4_title', '').strip(),
            'footer_col4_links': request.form.get('footer_col4_links', '').strip(),
            'footer_about_title': request.form.get('footer_about_title', '').strip(),
            'footer_about_links': request.form.get('footer_about_links', '').strip(),
            'footer_security_label': request.form.get('footer_security_label', '').strip(),
            'footer_badge1': request.form.get('footer_badge1', '').strip(),
            'footer_badge2': request.form.get('footer_badge2', '').strip(),
            'footer_badge3': request.form.get('footer_badge3', '').strip(),
            'footer_support_text': request.form.get('footer_support_text', '').strip(),
            'footer_support_label': request.form.get('footer_support_label', '').strip(),
            'footer_copyright': request.form.get('footer_copyright', '').strip(),
            'footer_privacy_label': request.form.get('footer_privacy_label', '').strip(),
            'footer_privacy_url': request.form.get('footer_privacy_url', '').strip(),
            'footer_terms_label': request.form.get('footer_terms_label', '').strip(),
            'footer_terms_url': request.form.get('footer_terms_url', '').strip(),
            'footer_consult_label': request.form.get('footer_consult_label', '').strip(),
            'footer_consult_url': request.form.get('footer_consult_url', '').strip(),
        }
        
        SettingModel.update_many(updates)
        flash('Konten dan pengaturan footer website berhasil diperbarui!', 'success')
        return redirect(url_for('admin_footer'))

    footer_data = get_footer_data()
    return render_template('admin/footer.html', footer=footer_data)

@app.route('/admin/footer/reset-defaults', methods=['POST'])
@admin_required
def admin_footer_reset_defaults():
    defaults = {
        'footer_brand_name': 'AKSARA CIPTA DIGITAL',
        'footer_brand_tagline': 'IT Consultant - AI, Software Developer',
        'footer_about': 'PT. Aksara Cipta Digital adalah perusahaan konsultan IT dan software house yang berpengalaman membangun ratusan aplikasi terbaik untuk berbagai sektor bisnis swasta, BUMN, dan institusi pemerintahan di seluruh Indonesia.',
        'footer_address_main': 'Gununggede Kawalu, Kota Tasikmalaya Jawa Barat 46182',
        'footer_address_branch': '',
        'footer_phone': '+62 21 8299 8765',
        'footer_email': 'info@acd.co.id',
        'footer_whatsapp': '6281288882510',
        'footer_col2_title': 'Aplikasi & Website',
        'footer_col2_links': "Mobile Apps (Android & iOS) | /layanan/mobile-apps\nWeb Base Apps | /layanan/sistem-informasi\nWebsite Korporat | /layanan/website-korporat\nGeographic Information System (GIS) | /layanan/gis-geoportal\nIntegrasi Sistem & API | /layanan/integrasi-sistem\nSemua Aplikasi & Website \u2192 | /layanan/kategori/Aplikasi%20&%20Website",
        'footer_col3_title': 'Aplikasi Bisnis ERP',
        'footer_col3_links': "HRIS / Kepegawaian | /layanan/erp-hris-kepegawaian\nPresensi & Geofencing | /layanan/erp-presensi-absensi\nPayroll & Pajak PPh21 | /layanan/erp-payroll-penggajian\nAkuntansi & Keuangan | /layanan/erp-accounting-keuangan\nAsset Management | /layanan/erp-asset-management\nWarehouse Management | /layanan/erp-warehouse-management\nDocument Management | /layanan/erp-document-management\nDashboard Eksekutif | /layanan/erp-dashboard-eksekutif",
        'footer_col4_title': 'Aplikasi E-Gov',
        'footer_col4_links': "Website Pemerintah Daerah | /layanan/egov-portal-daerah\ne-Data Sektoral SDI | /layanan/egov-data-sektoral\ne-Planning Internal & Pokir | /layanan/egov-e-planning-musrenbang\ne-Monev & e-SAKIP | /layanan/egov-e-monev-sakip\ne-Lapor & Pengaduan Warga | /layanan/egov-e-lapor-pengaduan\ne-Perizinan MPP TTE | /layanan/egov-e-perizinan-mpp",
        'footer_about_title': 'Tentang Kami',
        'footer_about_links': "Profil Perusahaan ACD | /tentang-kami\nStudi Kasus & Portofolio | /portofolio\nKarir di ACD | /karir\nTanya Jawab (FAQ) | /faq",
        'footer_security_label': 'Standar Keamanan & Mutu:',
        'footer_badge1': 'ISO 27001 Certified',
        'footer_badge2': 'OWASP Top 10 Compliant',
        'footer_badge3': 'SLA 99.9% Uptime Support',
        'footer_support_text': 'Layanan Konsultasi & Aduan:',
        'footer_support_label': 'WhatsApp 24/7 Support',
        'footer_copyright': '\u00a9 2025 PT. Aksara Cipta Digital (acd.co.id). All rights reserved.',
        'footer_privacy_label': 'Kebijakan Privasi',
        'footer_privacy_url': '/tentang-kami',
        'footer_terms_label': 'Syarat & Ketentuan Layanan',
        'footer_terms_url': '/tentang-kami',
        'footer_consult_label': 'Hubungi Konsultan',
        'footer_consult_url': '/kontak',
    }
    SettingModel.update_many(defaults)
    flash('Pengaturan footer berhasil dikembalikan ke standar awal PT. Aksara Cipta Digital.', 'info')
    return redirect(url_for('admin_footer'))


# --- KELOLA OPTIMASI SEO WEBSITE ---

@app.route('/admin/seo', methods=['GET', 'POST'])
@admin_required
def admin_seo():
    if request.method == 'POST':
        updates = {
            'seo_meta_title': request.form.get('seo_meta_title', '').strip(),
            'seo_meta_description': request.form.get('seo_meta_description', '').strip(),
            'seo_meta_keywords': request.form.get('seo_meta_keywords', '').strip(),
            'seo_canonical_url': request.form.get('seo_canonical_url', '').strip(),
            'seo_author': request.form.get('seo_author', '').strip(),
            'seo_robots': request.form.get('seo_robots', '').strip(),
            'seo_og_title': request.form.get('seo_og_title', '').strip(),
            'seo_og_description': request.form.get('seo_og_description', '').strip(),
            'seo_og_image': request.form.get('seo_og_image', '').strip(),
            'seo_twitter_card': request.form.get('seo_twitter_card', '').strip(),
            'seo_google_verification': request.form.get('seo_google_verification', '').strip(),
            'seo_bing_verification': request.form.get('seo_bing_verification', '').strip(),
            'seo_google_analytics_id': request.form.get('seo_google_analytics_id', '').strip(),
            'seo_gtm_id': request.form.get('seo_gtm_id', '').strip(),
            'seo_organization_type': request.form.get('seo_organization_type', 'Corporation').strip(),
        }
        SettingModel.update_many(updates)
        flash('Konfigurasi optimasi SEO website PT. Aksara Cipta Digital berhasil diperbarui!', 'success')
        return redirect(url_for('admin_seo'))

    seo_data = get_seo_data()
    return render_template('admin/seo.html', seo=seo_data)

@app.route('/admin/seo/reset-defaults', methods=['POST'])
@admin_required
def admin_seo_reset_defaults():
    defaults = {
        'seo_meta_title': 'PT. Aksara Cipta Digital | IT Consultant - AI, Software Developer',
        'seo_meta_description': 'PT. Aksara Cipta Digital (ACD) adalah konsultan IT terkemuka dan software house spesialis arsitektur sistem ERP, E-Government, Mobile Apps, dan solusi kecerdasan buatan (AI) terpercaya di Indonesia.',
        'seo_meta_keywords': 'IT Consultant, Konsultan IT Indonesia, Software Developer Indonesia, Jasa Pembuatan Aplikasi, Jasa Sistem ERP, E-Government SPBE, AI Developer, GIS Geoportal, PT Aksara Cipta Digital, ACD',
        'seo_canonical_url': 'https://acd.co.id',
        'seo_author': 'PT. Aksara Cipta Digital',
        'seo_robots': 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1',
        'seo_og_title': 'PT. Aksara Cipta Digital - IT Consultant & Enterprise Software House',
        'seo_og_description': 'Solusi software inovatif, arsitektur sistem berkinerja tinggi, dan transformasi digital terpercaya untuk Korporasi Swasta, BUMN, dan Pemerintahan di seluruh Indonesia.',
        'seo_og_image': '/static/images/logo_acd_icon.png',
        'seo_og_type': 'website',
        'seo_twitter_card': 'summary_large_image',
        'seo_google_verification': '',
        'seo_bing_verification': '',
        'seo_google_analytics_id': '',
        'seo_gtm_id': '',
        'seo_organization_type': 'Corporation'
    }
    SettingModel.update_many(defaults)
    flash('Konfigurasi SEO berhasil dikembalikan ke standar awal PT. Aksara Cipta Digital.', 'info')
    return redirect(url_for('admin_seo'))

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

# ==============================================================================
# BUKU PANDUAN PENGOPERASIAN SISTEM & INFRASTRUKTUR (MANUAL BOOK)
# ==============================================================================
@app.route('/admin/manual-book')
@admin_required
def admin_manual_book():
    from database import get_db_connection
    import platform
    import sys

    # Informasi Arsitektur & Infrastruktur
    infra_info = {
        'company_name': SettingModel.get('company_name', Config.COMPANY_NAME),
        'domain': SettingModel.get('seo_canonical_url', 'https://acd.co.id'),
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'framework': 'Python Flask 3.x (WSGI / Jinja2)',
        'database_engine': 'SQLite 3 (ACID Relational Engine, Write-Ahead Logging)',
        'frontend_stack': 'Tailwind CSS, Vanilla JavaScript, Lucide Icons',
        'security_features': [
            'Otorisasi Ganda 2FA (PIN Master 6-Digit)',
            'Brute-Force Rate Limiting (Kunci IP otomatis setelah 3x gagal, lockout 15 menit)',
            'Dynamic Visual & Math CAPTCHA',
            'Honeypot Anti-Bot Field Detector',
            'Proteksi Anti-Spam WhatsApp & Leads (Maks 2x per 24 jam)',
            'Auto-Logout Sesi Idle 15 Menit',
            'OWASP Hardened Security Headers (CSP, X-Frame-Options, HSTS, nosniff)',
            'Audit Logging Realtime & IP Lockout Management'
        ]
    }

    # Kamus Basis Data Dinamis (Dynamic Database Schema & Stats)
    db_tables = [
        {
            'name': 'inquiries',
            'label': 'Permintaan Masuk (Leads Klien)',
            'desc': 'Menyimpan data calon klien yang mengirim form kebutuhan / konsultasi proyek software.'
        },
        {
            'name': 'services',
            'label': 'Katalog Layanan Solusi IT',
            'desc': 'Menyimpan data solusi IT, fitur unggulan, tech stack, dan status tayang di web.'
        },
        {
            'name': 'portfolios',
            'label': 'Studi Kasus Portofolio',
            'desc': 'Menyimpan riwayat proyek klien (BUMN, Pemerintah, Swasta), tantangan, solusi, dan metrik dampak.'
        },
        {
            'name': 'careers',
            'label': 'Lowongan Karir & Rekrutmen',
            'desc': 'Menyimpan data lowongan pekerjaan, departemen, kualifikasi, tanggung jawab, dan status tayang.'
        },
        {
            'name': 'faqs',
            'label': 'Tanya Jawab (FAQ)',
            'desc': 'Menyimpan daftar pertanyaan yang sering diajukan klien beserta jawaban resmi.'
        },
        {
            'name': 'wa_logs',
            'label': 'Log Anti-Spam WhatsApp',
            'desc': 'Merekam setiap klik tombol konsultasi WhatsApp per IP pengunjung untuk mencegah flooding spam.'
        },
        {
            'name': 'admin_security_logs',
            'label': 'Audit Log Keamanan',
            'desc': 'Mencatat seluruh percobaan login, kegagalan kredensial, deteksi bot, dan aktivitas penting sistem.'
        },
        {
            'name': 'login_lockouts',
            'label': 'Daftar Blokir IP Brute-Force',
            'desc': 'Menyimpan daftar alamat IP penyerang yang sedang terkunci otomatis akibat salah password berulang.'
        },
        {
            'name': 'settings',
            'label': 'Konfigurasi Global & SEO',
            'desc': 'Menyimpan identitas perusahaan, nomor hotline, email, konfigurasi SEO meta, dan kredensial admin.'
        }
    ]

    conn = get_db_connection()
    cursor = conn.cursor()

    for table in db_tables:
        # Hitung jumlah baris data
        try:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table['name']}")
            table['count'] = cursor.fetchone()['count']
        except Exception:
            table['count'] = 0

        # Ambil skema kolom PRAGMA
        try:
            cursor.execute(f"PRAGMA table_info({table['name']})")
            table['columns'] = [dict(col) for col in cursor.fetchall()]
        except Exception:
            table['columns'] = []

    conn.close()

    return render_template(
        'admin/manual_book.html',
        infra=infra_info,
        tables=db_tables,
        now=datetime.now().strftime('%d %B %Y, %H:%M WIB')
    )

@app.route('/admin/manual-book/download')
@admin_required
def admin_manual_book_download():
    from database import get_db_connection
    import platform

    company_name = SettingModel.get('company_name', Config.COMPANY_NAME)
    company_domain = SettingModel.get('seo_canonical_url', 'https://acd.co.id')
    export_date = datetime.now().strftime('%d %B %Y, %H:%M WIB')

    # Bangun dokumen teks Markdown lengkap
    doc = []
    doc.append(f"# BUKU PANDUAN PENGOPERASIAN & DOKUMENTASI TEKNIS SISTEM (MANUAL BOOK)")
    doc.append(f"**Website Resmi**: {company_name} ({company_domain})  ")
    doc.append(f"**Tanggal Generate Dokumen**: {export_date}  ")
    doc.append(f"**Klasifikasi Dokumen**: Rahasia / Internal Administrator  \n")
    doc.append("---\n")

    doc.append("## 1. PENDAHULUAN & TUJUAN")
    doc.append(f"Buku Panduan ini disusun sebagai standar operasional prosedur (SOP) dan dokumentasi komprehensif arsitektur teknologi website **{company_name}**. Dokumen ini wajib dipahami oleh tim administrator, IT internal, maupun DevOps yang bertugas memelihara, memperbarui konten, dan mengawasi keamanan website.\n")

    doc.append("## 2. INFRASTRUKTUR & STACK TEKNOLOGI")
    doc.append("Website ini dirancang menggunakan standar teknologi modern yang mengutamakan kecepatan akses, keamanan data tingkat tinggi, dan kemudahan skalabilitas:")
    doc.append(f"- **Bahasa Pemrograman**: Python {platform.python_version()}")
    doc.append("- **Web Framework**: Python Flask 3.x (WSGI Architecture, Jinja2 Templating Engine)")
    doc.append("- **Database Engine**: SQLite 3 Relational Engine (ACID Compliant, WAL / Write-Ahead Logging Enabled)")
    doc.append("- **Frontend Styling**: Tailwind CSS (Utility-first framework) + Custom Cosmic Dark Theme CSS")
    doc.append("- **Icon Library**: Lucide Icons (SVG Vector Engine)")
    doc.append("- **Interactive Canvas**: HTML5 Canvas Particle Constellation System (Efek Grafis Cosmic Modern)")
    doc.append("- **Production Web Server**: Nginx Reverse Proxy + Gunicorn / Waitress WSGI Server")
    doc.append("- **Sertifikat Keamanan**: SSL/TLS HTTPS Let's Encrypt (Grade A+ Security)\n")

    doc.append("## 3. ARSITEKTUR KEAMANAN SISTEM (SECURITY DEFENSE)")
    doc.append("Website dilengkapi dengan 6 lapis pertahanan siber berlapis untuk melindungi data perusahaan dan klien:")
    doc.append("1. **Otorisasi Ganda 2FA (PIN Master 6-Digit)**: Setelah username dan kata sandi benar, sistem meminta verifikasi PIN Master sebelum memberikan akses ke panel kendali CMS.")
    doc.append("2. **Proteksi Anti Brute-Force & Rate Limiting**: Batas toleransi maksimal 3 kali kesalahan login per alamat IP. Percobaan ke-4 memicu pemblokiran otomatis (Lockout) selama 15 menit.")
    doc.append("3. **Anti-Bot Dynamic CAPTCHA**: Algoritma kalkulasi dinamis dan verifikasi visual untuk mencegah pengisian otomatis oleh script peretas.")
    doc.append("4. **Honeypot Trap Detector**: Jebakan input tak kasat mata yang mendeteksi bot otomatis secara instan.")
    doc.append("5. **Proteksi Anti-Spam WhatsApp & Leads**: Membatasi pengiriman formulir dan interaksi klik WA maksimal 2 kali per 24 jam per pengunjung/IP.")
    doc.append("6. **Auto-Logout Sesi Inaktivitas (15 Menit)**: Bila staf tidak menyentuh mouse/keyboard selama 15 menit, sistem otomatis mengakhiri sesi untuk mencegah pencurian akses.")
    doc.append("7. **Audit Trail Realtime**: Setiap aktivitas login, kegagalan autentikasi, dan aksi penting tercatat lengkap dengan IP dan User-Agent.\n")

    doc.append("## 4. STRUKTUR BASIS DATA (DATABASE SCHEMA & DATA DICTIONARY)")
    doc.append("Basis data SQLite dirancang dalam format tabel relasional terstruktur:\n")

    db_tables = [
        ('inquiries', 'Permintaan Masuk (Leads Klien)', 'Menyimpan calon klien yang mengisi formulir kebutuhan software.'),
        ('services', 'Katalog Layanan Solusi IT', 'Katalog solusi IT, fitur, tech stack, dan status tayang.'),
        ('portfolios', 'Portofolio Proyek Klien', 'Showcase implementasi sistem untuk Pemerintahan, BUMN, dan Swasta.'),
        ('careers', 'Lowongan Karir & Rekrutmen', 'Daftar lowongan kerja, kualifikasi talenta, dan status tayang.'),
        ('faqs', 'Tanya Jawab (FAQ)', 'Daftar tanya jawab interaktif untuk mengedukasi calon klien.'),
        ('wa_logs', 'Log Anti-Spam WhatsApp', 'Pencatatan interaksi tombol WA untuk penegakan batas 2x/24 jam.'),
        ('admin_security_logs', 'Audit Log Keamanan', 'Riwayat percobaan login, serangan bot, dan akses administrator.'),
        ('login_lockouts', 'Daftar Blokir IP Brute-Force', 'Daftar alamat IP yang terkunci sementara oleh sistem keamanan.'),
        ('settings', 'Konfigurasi Sistem & SEO', 'Key-value konfigurasi identitas brand, kontak, dan metadata SEO.')
    ]

    conn = get_db_connection()
    cursor = conn.cursor()

    for tbl_name, tbl_label, tbl_desc in db_tables:
        doc.append(f"### Tabel: `{tbl_name}` ({tbl_label})")
        doc.append(f"_{tbl_desc}_\n")
        try:
            cursor.execute(f"PRAGMA table_info({tbl_name})")
            cols = cursor.fetchall()
            cursor.execute(f"SELECT COUNT(*) as count FROM {tbl_name}")
            cnt = cursor.fetchone()['count']
            doc.append(f"**Total Data Saat Ini**: {cnt} baris\n")
            doc.append("| No | Nama Kolom | Tipe Data | Not Null | Primary Key | Keterangan |")
            doc.append("|:---|:---|:---|:---:|:---:|:---|")
            for col in cols:
                cid, name, col_type, notnull, dflt, pk = col
                nn_str = "Ya" if notnull else "Tidak"
                pk_str = "PK" if pk else "-"
                doc.append(f"| {cid + 1} | `{name}` | `{col_type}` | {nn_str} | {pk_str} | - |")
            doc.append("")
        except Exception as e:
            doc.append(f"Gagal membaca skema tabel: {str(e)}\n")

    conn.close()

    doc.append("## 5. PANDUAN PENGOPERASIAN MODUL CMS (SOP ADMINISTRATOR)")
    doc.append("Berikut alur pengoperasian tiap modul pada panel kendali internal:")
    doc.append("### A. Mengelola Leads Masuk & Follow-Up Klien")
    doc.append("1. Buka menu **Permintaan Masuk (Form Kebutuhan)**.")
    doc.append("2. Periksa badge status: **Baru**, **Dihubungi**, **Diproses**, atau **Selesai**.")
    doc.append("3. Klik tombol **Follow-Up via WA** untuk langsung membuka WhatsApp Web / App dengan pesan sapaan resmi yang sudah terisi otomatis.")
    doc.append("4. Masukkan catatan internal pada kolom *Tambah catatan...* lalu ubah status ke *Dihubungi* / *Diproses* dan klik **Simpan**.\n")

    doc.append("### B. Mengelola Solusi & Layanan IT")
    doc.append("1. Buka menu **Kelola Layanan**.")
    doc.append("2. Untuk menambahkan layanan baru, klik tombol **Tambah Layanan Baru**.")
    doc.append("3. Isi judul layanan, kategori (misal: Solusi Pemerintahan & E-Gov, Aplikasi Bisnis ERP), subjudul, ringkasan, fitur unggulan, dan daftar teknologi (tech stack).")
    doc.append("4. Tentukan status tayang (Tayang / Draft) lalu simpan.\n")

    doc.append("### C. Mengelola Portofolio & Studi Kasus")
    doc.append("1. Buka menu **Kelola Portofolio**.")
    doc.append("2. Klik **Tambah Portofolio Baru**.")
    doc.append("3. Masukkan nama proyek, nama klien, tipe klien (BUMN, Swasta, Pemerintahan), tahun implementasi, tantangan, solusi, dan dampak konkret.")
    doc.append("4. Portofolio otomatis muncul di halaman depan dan halaman portofolio publik.\n")

    doc.append("### D. Mengelola Lowongan Karir")
    doc.append("1. Buka menu **Karir & Lowongan**.")
    doc.append("2. Klik **Buka Lowongan Baru**.")
    doc.append("3. Isi posisi pekerjaan, departemen, jenis kerja (Onsite/Hybrid/Remote), kualifikasi syarat, dan tanggung jawab.")
    doc.append("4. Anda dapat mengaktifkan atau menonaktifkan status tayang kapan saja dengan satu klik tombol toggle.\n")

    doc.append("### E. Mengatur SEO & Metadata Pencarian Google")
    doc.append("1. Buka menu **Optimasi SEO**.")
    doc.append("2. Isi Meta Title, Meta Description, Keywords, URL Canonical (`https://acd.co.id`), dan Kode Verifikasi Google Search Console.")
    doc.append("3. File `sitemap.xml` dan `robots.txt` digenerate secara otomatis oleh sistem secara dinamis.\n")

    doc.append("### F. Memantau Keamanan & Membuka Blokir IP")
    doc.append("1. Buka menu **Keamanan & Audit Log**.")
    doc.append("2. Periksa daftar *IP yang Sedang Diblokir Otomatis* jika ada staf yang salah memasukkan password lebih dari 3 kali.")
    doc.append("3. Klik tombol hijau **Buka Blokir** untuk mengembalikan akses IP tersebut secara instan.")
    doc.append("4. Periksa riwayat log aktivitas untuk memastikan tidak ada percobaan hacking yang mencurigakan.\n")

    doc.append("## 6. PROSEDUR BACKUP & RESTORE DATA")
    doc.append("1. Seluruh data website tersimpan dalam satu file database SQLite: `acd_database.sqlite`.")
    doc.append("2. Lakukan backup berkala dengan menyalin (copy) file `acd_database.sqlite` ke tempat penyimpanan aman (cloud drive / server backup terpisah).")
    doc.append("3. Untuk restore data, cukup gantikan file `acd_database.sqlite` dengan file backup yang diinginkan saat server web sedang tidak menerima beban tinggi.\n")

    doc.append("---\n")
    doc.append(f"_Dokumen ini digenerate secara otomatis oleh Internal CMS Portal {company_name}._")

    content = "\n".join(doc)
    filename = f"Manual_Book_Operasional_PT_Aksara_Cipta_Digital.md"

    response = Response(content, mimetype='text/markdown; charset=utf-8')
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Running on local port 5000 (debug configurable via env FLASK_DEBUG)
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1']
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
