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

    // 5b. AJAX Consultation Form Submission (with 2x/24h Anti-Spam & National Standard WA)
    const consultationForms = document.querySelectorAll('.ajax-consultation-form');
    consultationForms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn ? submitBtn.innerHTML : 'Kirim';

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
                alert('Mohon lengkapi semua kolom wajib bertanda bintang (*).');
                return;
            }

            // WhatsApp National Standard Check
            if (/[a-zA-Z]/.test(phone)) {
                alert('Nomor WhatsApp tidak boleh mengandung huruf. Harap masukkan nomor telepon yang valid.');
                return;
            }

            const cleanPhone = phone.replace(/[^0-9+]/g, '');
            const waRegex = /^(\+62|62|0)8[0-9]{8,12}$/;
            if (!waRegex.test(cleanPhone)) {
                alert('Format nomor WhatsApp tidak sesuai standar nasional Indonesia.\n\nContoh yang benar: 08123456789 atau 628123456789 (10-14 digit angka diawali 08/628).');
                return;
            }

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="inline-block animate-spin mr-2">⟳</span> Mengirim Data...';
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
                        submitBtn.innerHTML = '<span class="inline-block animate-spin mr-2">✓</span> Membuka WhatsApp (+62 852-8789-8937)...';
                    }

                    // Arahkan langsung ke WhatsApp resmi konsultan ACD (+62 852-8789-8937)
                    if (data.whatsapp_url) {
                        setTimeout(() => {
                            window.location.href = data.whatsapp_url;
                        }, 250);
                    } else {
                        alert('Terima kasih ' + name + '!\n\nPermintaan konsultasi Anda telah berhasil dikirim ke tim ACD.');
                    }
                } else if (res.status === 429) {
                    alert('⚠️ KUOTA PENGIRIMAN MAKSIMAL TERCAPAI\n\n' + data.message);
                } else {
                    alert(data.message || 'Terjadi kendala saat mengirim data. Silakan periksa kembali formulir Anda.');
                }
            } catch (err) {
                alert('Gagal terhubung ke server. Silakan periksa koneksi internet Anda atau hubungi kami langsung.');
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
        link.addEventListener('click', async (e) => {
            const recentClicks = getLocalWAClicks();
            if (recentClicks.length >= 2) {
                e.preventDefault();
                alert('⚠️ BATAS PENGIRIMAN PESAN WHATSAPP TERCAPAI\n\nAnda telah mencapai batas maksimal 2x pengiriman pesan WhatsApp dalam waktu 1 x 24 jam untuk kenyamanan bersama dan mencegah spam.\n\nSilakan hubungi kami via email resmi info@acd.co.id atau coba kembali besok.');
                return false;
            }

            // Sync with server rate limiter
            try {
                const res = await fetch('/api/v1/track-wa-click?source=user_click', { method: 'POST' });
                const data = await res.json();
                if (!data.allowed) {
                    e.preventDefault();
                    alert('⚠️ ' + (data.message || 'Batas maksimal 2x pengiriman pesan WhatsApp dalam 24 jam telah tercapai.'));
                    return false;
                }
                recordLocalWAClick();
            } catch (err) {
                // Fallback to local tracker
                recordLocalWAClick();
            }
        });
    });

    // 6. Interactive Project Cost Estimator Calculator
    const estimatorForm = document.getElementById('project-estimator-form');
    if (estimatorForm) {
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

            const resultDisplay = document.getElementById('est-result-price');
            const resultTimeline = document.getElementById('est-result-timeline');

            if (resultDisplay) {
                resultDisplay.innerText = `Rp ${finalMin} Juta - Rp ${finalMax} Juta*`;
            }

            // Timeline Dinamis Proporsional
            if (resultTimeline) {
                let estWeeks = '6 - 10 Minggu';
                
                if (projectType === 'website') {
                    if (scale === 'standard') estWeeks = '2 - 4 Minggu';
                    else if (scale === 'medium') estWeeks = '4 - 6 Minggu';
                    else estWeeks = '6 - 10 Minggu';
                } else if (projectType === 'web') {
                    if (scale === 'standard') estWeeks = '4 - 8 Minggu';
                    else if (scale === 'medium') estWeeks = '8 - 12 Minggu';
                    else estWeeks = '14 - 20 Minggu';
                } else if (projectType === 'mobile') {
                    if (scale === 'standard') estWeeks = '6 - 10 Minggu';
                    else if (scale === 'medium') estWeeks = '10 - 14 Minggu';
                    else estWeeks = '16 - 22 Minggu';
                } else if (projectType === 'erp' || projectType === 'egov') {
                    if (scale === 'standard') estWeeks = '8 - 12 Minggu';
                    else if (scale === 'medium') estWeeks = '12 - 18 Minggu';
                    else estWeeks = '18 - 26 Minggu';
                }

                if (timeline === 'express') {
                    estWeeks += ' (Fast-Track Prioritas)';
                }
                resultTimeline.innerText = estWeeks;
            }
        };

        const radioInputs = estimatorForm.querySelectorAll('input[type="radio"]');
        radioInputs.forEach(input => {
            input.addEventListener('change', calculateEstimate);
        });
        calculateEstimate();
    }
});
