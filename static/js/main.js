// PT. Aksara Cipta Digital (ACD Digital Consulting) - Interactive Scripts

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Menu Toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenuClose = document.getElementById('mobile-menu-close');
    const mobileDrawer = document.getElementById('mobile-drawer');
    const mobileBackdrop = document.getElementById('mobile-backdrop');

    if (mobileMenuBtn && mobileDrawer) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileDrawer.classList.remove('translate-x-full');
            if (mobileBackdrop) mobileBackdrop.classList.remove('hidden');
            document.body.classList.add('overflow-hidden');
        });

        const closeDrawer = () => {
            mobileDrawer.classList.add('translate-x-full');
            if (mobileBackdrop) mobileBackdrop.classList.add('hidden');
            document.body.classList.remove('overflow-hidden');
        };

        if (mobileMenuClose) mobileMenuClose.addEventListener('click', closeDrawer);
        if (mobileBackdrop) mobileBackdrop.addEventListener('click', closeDrawer);
    }

    // 2. Mobile Accordion for Submenus
    const mobileDropdownToggles = document.querySelectorAll('.mobile-dropdown-toggle');
    mobileDropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = toggle.getAttribute('data-target');
            const targetEl = document.getElementById(targetId);
            const icon = toggle.querySelector('.arrow-icon');
            if (targetEl) {
                targetEl.classList.toggle('hidden');
                if (icon) icon.classList.toggle('rotate-180');
            }
        });
    });

    // 3. Back to Top Button
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 400) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
        });

        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // 4. Consultation Modal Logic
    window.openConsultationModal = function(preselectedService = '') {
        const modal = document.getElementById('consultation-modal');
        if (modal) {
            modal.classList.remove('hidden');
            document.body.classList.add('overflow-hidden');
            if (preselectedService) {
                const serviceSelect = document.getElementById('modal-service-type');
                if (serviceSelect) serviceSelect.value = preselectedService;
            }
        }
    };

    window.closeConsultationModal = function() {
        const modal = document.getElementById('consultation-modal');
        if (modal) {
            modal.classList.add('hidden');
            document.body.classList.remove('overflow-hidden');
        }
    };

    // 5. Real-Time Indonesian Phone Input Sanitizer (No letters allowed)
    const phoneInputs = document.querySelectorAll('input[name="phone"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', (e) => {
            let val = e.target.value;
            // Strictly strip any letters and non-phone characters
            let cleaned = val.replace(/[^0-9+]/g, '');
            // Only allow + at the very beginning
            if (cleaned.indexOf('+') > 0) {
                cleaned = cleaned.charAt(0) === '+' ? '+' + cleaned.replace(/\+/g, '') : cleaned.replace(/\+/g, '');
            }
            if (val !== cleaned) {
                e.target.value = cleaned;
            }
        });
    });

    // Helper: Detect active language (id / en) and dynamic WA number
    const isEn = (document.documentElement.lang || 'id').toLowerCase() === 'en';
    const targetWaNumber = (document.body.getAttribute('data-wa-number') || '6285287898937').replace(/[^0-9]/g, '') || '6285287898937';

    // 5b. AJAX Consultation Form Submission (with 2x/24h Anti-Spam & National Standard WA)
    const consultationForms = document.querySelectorAll('.ajax-consultation-form');
    consultationForms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn ? submitBtn.innerHTML : (isEn ? 'Send' : 'Kirim');

            const formData = new FormData(form);
            const name = (formData.get('name') || '').trim();
            const email = (formData.get('email') || '').trim();
            const phone = (formData.get('phone') || '').trim();
            const company = (formData.get('company') || '').trim();
            const service_type = formData.get('service_type');
            const budget_range = formData.get('budget_range') || '';
            const message = (formData.get('message') || '').trim();

            // Client-Side Validation
            if (!name || !email || !phone || !message) {
                alert(isEn ? 'Please complete all required fields marked with (*).' : 'Mohon lengkapi semua kolom wajib bertanda bintang (*).');
                return;
            }

            // WhatsApp National Standard Check
            if (/[a-zA-Z]/.test(phone)) {
                alert(isEn ? 'WhatsApp number must not contain letters. Please enter a valid phone number.' : 'Nomor WhatsApp tidak boleh mengandung huruf. Harap masukkan nomor telepon yang valid.');
                return;
            }

            const cleanPhone = phone.replace(/[^0-9+]/g, '');
            const waRegex = /^(\+62|62|0)8[0-9]{8,12}$/;
            if (!waRegex.test(cleanPhone)) {
                alert(isEn
                    ? 'Invalid Indonesian WhatsApp number format.\n\nValid examples: 08123456789 or 628123456789 (10-14 digits starting with 08/628).'
                    : 'Format nomor WhatsApp tidak sesuai standar nasional Indonesia.\n\nContoh yang benar: 08123456789 atau 628123456789 (10-14 digit angka diawali 08/628).');
                return;
            }

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<span class="inline-block animate-spin mr-2">⟳</span> ${isEn ? 'Sending & Opening WhatsApp...' : 'Mengirim Data & Membuka WhatsApp...'}`;
            }

            const payload = {
                name,
                email,
                phone,
                company,
                service_type,
                budget_range,
                message
            };

            try {
                const res = await fetch('/api/v1/consultation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (res.status === 200 && data.status === 'success') {
                    form.reset();
                    if (window.closeConsultationModal) window.closeConsultationModal();

                    if (submitBtn) {
                        submitBtn.innerHTML = `<span class="inline-block mr-2">✓</span> ${isEn ? 'Opening WhatsApp...' : 'Membuka WhatsApp (+62 852-8789-8937)...'}`;
                    }

                    // Arahkan langsung ke WhatsApp resmi konsultan ACD (+62 852-8789-8937)
                    if (data.whatsapp_url) {
                        window.location.href = data.whatsapp_url;
                    } else {
                        alert(isEn ? `Thank you ${name}! Your consultation request has been sent to the ACD team.` : `Terima kasih ${name}!\n\nPermintaan konsultasi Anda telah berhasil dikirim ke tim ACD.`);
                    }
                } else if (res.status === 429) {
                    alert((isEn ? '⚠️ SUBMISSION LIMIT REACHED\n\n' : '⚠️ KUOTA PENGIRIMAN MAKSIMAL TERCAPAI\n\n') + data.message);
                } else {
                    alert(data.message || (isEn ? 'An error occurred while sending data. Please check your form.' : 'Terjadi kendala saat mengirim data. Silakan periksa kembali formulir Anda.'));
                }
            } catch (err) {
                alert(isEn ? 'Unable to connect to the server. Please check your internet connection or contact us directly.' : 'Gagal terhubung ke server. Silakan periksa koneksi internet Anda atau hubungi kami langsung.');
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            }
        });
    });

    // 5c. WhatsApp Message Click Rate Limiter (Maksimal 2x Pengiriman / 24 Jam)
    function getLocalWAClicks() {
        try {
            const raw = localStorage.getItem('acd_wa_click_timestamps');
            const arr = raw ? JSON.parse(raw) : [];
            const cutoff = Date.now() - (24 * 60 * 60 * 1000);
            return arr.filter(t => t > cutoff);
        } catch (e) {
            return [];
        }
    }

    function recordLocalWAClick() {
        try {
            const list = getLocalWAClicks();
            list.push(Date.now());
            localStorage.setItem('acd_wa_click_timestamps', JSON.stringify(list));
        } catch (e) {}
    }

    const waLinks = document.querySelectorAll('a[href*="wa.me"], .track-wa-btn, .floating-wa-btn');
    waLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const recentClicks = getLocalWAClicks();
            if (recentClicks.length >= 2) {
                e.preventDefault();
                alert(isEn
                    ? '⚠️ WHATSAPP MESSAGE LIMIT REACHED\n\nYou have reached the maximum limit of 2 WhatsApp messages within 24 hours to prevent spam.\n\nPlease contact us via official email info@acd.co.id or try again tomorrow.'
                    : '⚠️ BATAS PENGIRIMAN PESAN WHATSAPP TERCAPAI\n\nAnda telah mencapai batas maksimal 2x pengiriman pesan WhatsApp dalam waktu 1 x 24 jam untuk kenyamanan bersama dan mencegah spam.\n\nSilakan hubungi kami via email resmi info@acd.co.id atau coba kembali besok.');
                return false;
            }

            // Record synchronously & send non-blocking telemetry with keepalive so wa.me opens immediately without popup blocking
            recordLocalWAClick();
            const source = link.getAttribute('data-wa-source') || link.id || 'user_click';
            fetch(`/api/v1/track-wa-click?source=${encodeURIComponent(source)}`, {
                method: 'POST',
                keepalive: true
            }).then(res => res.json()).then(data => {
                if (data && data.allowed === false) {
                    // Ensure local storage reflects reached cap
                    try {
                        const now = Date.now();
                        localStorage.setItem('acd_wa_click_timestamps', JSON.stringify([now, now]));
                    } catch (err) {}
                }
            }).catch(() => {});
        });
    });

    // 6. Interactive Project Cost Estimator Calculator (Bilingual + Direct WhatsApp Export)
    const estimatorForm = document.getElementById('project-estimator-form');
    if (estimatorForm) {
        const typeLabels = {
            website: isEn ? 'Website & Portal (Corporate / Landing)' : 'Website & Portal (Korporat / Landing)',
            web: isEn ? 'Information System (Custom Web App)' : 'Sistem Informasi (Web Base Custom)',
            mobile: isEn ? 'Mobile Apps (Android & iOS)' : 'Mobile Apps (Android & iOS)',
            erp: isEn ? 'Enterprise ERP Software' : 'Aplikasi ERP Bisnis & Operasional',
            egov: isEn ? 'E-Government (Smart City & SPBE)' : 'E-Government (Smart City & SPBE)'
        };
        const scaleLabels = {
            standard: isEn ? 'Standard / Single Team (<= 50 users)' : 'Standar / Tim Tunggal (<= 50 pengguna)',
            medium: isEn ? 'Medium / Multi-Division (50 - 500 users)' : 'Menengah / Multi-Divisi (50 - 500 pengguna)',
            enterprise: isEn ? 'Enterprise / Public Scale (> 1,000 users)' : 'Enterprise / Skala Publik (> 1.000 pengguna)'
        };
        const timelineLabels = {
            standard: isEn ? 'Regular / Agile Sprint' : 'Reguler / Agile Sprint',
            express: isEn ? 'Fast-Track / Dedicated Priority' : 'Fast-Track / Dedicated Priority'
        };

        const calculateEstimate = () => {
            const projectType = document.querySelector('input[name="est_type"]:checked')?.value || 'web';
            const scale = document.querySelector('input[name="est_scale"]:checked')?.value || 'medium';
            const timeline = document.querySelector('input[name="est_timeline"]:checked')?.value || 'standard';
            
            // Base Prices untuk Skala Standar (dalam Juta Rupiah)
            let baseMin = 20;
            let baseMax = 45;

            if (projectType === 'website') {
                baseMin = 10;
                baseMax = 25;
            } else if (projectType === 'web') {
                baseMin = 20;
                baseMax = 45;
            } else if (projectType === 'mobile') {
                baseMin = 35;
                baseMax = 65;
            } else if (projectType === 'erp') {
                baseMin = 65;
                baseMax = 120;
            } else if (projectType === 'egov') {
                baseMin = 80;
                baseMax = 180;
            }

            // Pengali Skala Kompleksitas
            let multiplier = 1.0;
            if (scale === 'medium') {
                multiplier = 1.6;
            } else if (scale === 'enterprise') {
                multiplier = 2.5;
            }

            // Pengali Fast-Track / Prioritas Cepat
            if (timeline === 'express') {
                multiplier *= 1.2;
            }

            const finalMin = Math.round(baseMin * multiplier);
            const finalMax = Math.round(baseMax * multiplier);

            const priceStr = isEn
                ? `IDR ${finalMin}M - ${finalMax}M*`
                : `Rp ${finalMin} Juta - Rp ${finalMax} Juta*`;

            const resultDisplay = document.getElementById('est-result-price');
            const resultTimeline = document.getElementById('est-result-timeline');

            if (resultDisplay) {
                resultDisplay.innerText = priceStr;
            }

            // Timeline Dinamis Proporsional
            let estWeeks = isEn ? '8 - 12 Weeks' : '8 - 12 Minggu';
            const wkUnit = isEn ? 'Weeks' : 'Minggu';
            
            if (projectType === 'website') {
                if (scale === 'standard') estWeeks = `2 - 4 ${wkUnit}`;
                else if (scale === 'medium') estWeeks = `4 - 6 ${wkUnit}`;
                else estWeeks = `6 - 10 ${wkUnit}`;
            } else if (projectType === 'web') {
                if (scale === 'standard') estWeeks = `4 - 8 ${wkUnit}`;
                else if (scale === 'medium') estWeeks = `8 - 12 ${wkUnit}`;
                else estWeeks = `14 - 20 ${wkUnit}`;
            } else if (projectType === 'mobile') {
                if (scale === 'standard') estWeeks = `6 - 10 ${wkUnit}`;
                else if (scale === 'medium') estWeeks = `10 - 14 ${wkUnit}`;
                else estWeeks = `16 - 22 ${wkUnit}`;
            } else if (projectType === 'erp' || projectType === 'egov') {
                if (scale === 'standard') estWeeks = `8 - 12 ${wkUnit}`;
                else if (scale === 'medium') estWeeks = `12 - 18 ${wkUnit}`;
                else estWeeks = `18 - 26 ${wkUnit}`;
            }

            if (timeline === 'express') {
                estWeeks += isEn ? ' (Fast-Track Priority)' : ' (Fast-Track Prioritas)';
            }

            if (resultTimeline) {
                resultTimeline.innerText = estWeeks;
            }

            // Update direct WhatsApp & Contact Form links with live estimator payload
            const summaryNote = isEn
                ? `Hello PT. Aksara Cipta Digital (ACD) Team,\n\nI ran a project budget simulation on the website:\n• Solution Category: ${typeLabels[projectType] || projectType}\n• User Scale: ${scaleLabels[scale] || scale}\n• Priority Mode: ${timelineLabels[timeline] || timeline}\n• Estimated Investment: ${priceStr.replace('*', '')}\n• Estimated Delivery: ${estWeeks}\n\nPlease share a detailed technical proposal and consultation schedule.`
                : `Halo Tim Konsultan PT. Aksara Cipta Digital (ACD),\n\nSaya telah melakukan simulasi anggaran proyek di website:\n• Kategori Solusi: ${typeLabels[projectType] || projectType}\n• Skala Pengguna: ${scaleLabels[scale] || scale}\n• Prioritas Rilis: ${timelineLabels[timeline] || timeline}\n• Perkiraan Investasi: ${priceStr.replace('*', '')}\n• Estimasi Pengerjaan: ${estWeeks}\n\nMohon diskusi lebih lanjut mengenai rincian RAB dan jadwal konsultasinya.`;

            const estWaBtn = document.getElementById('est-wa-btn');
            if (estWaBtn) {
                estWaBtn.href = `https://wa.me/${targetWaNumber}?text=${encodeURIComponent(summaryNote)}`;
            }
            const estContactBtn = document.getElementById('est-contact-btn');
            if (estContactBtn) {
                estContactBtn.href = `/kontak?note=${encodeURIComponent(summaryNote)}`;
            }
        };

        const radioInputs = estimatorForm.querySelectorAll('input[type="radio"]');
        radioInputs.forEach(input => {
            input.addEventListener('change', calculateEstimate);
        });
        calculateEstimate();
    }

    // 7. Active Navigation Link Indicator (Immediate White Line on Click)
    const mainNavLinks = document.querySelectorAll('.main-nav-link');
    mainNavLinks.forEach(link => {
        link.addEventListener('click', function() {
            mainNavLinks.forEach(l => l.classList.remove('nav-link-active'));
            this.classList.add('nav-link-active');
        });
    });
});
