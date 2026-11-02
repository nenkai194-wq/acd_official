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

    // 5. AJAX Consultation Form Submission
    const consultationForms = document.querySelectorAll('.ajax-consultation-form');
    consultationForms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn ? submitBtn.innerHTML : 'Kirim';
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="inline-block animate-spin mr-2">⟳</span> Mengirim Data...';
            }

            const formData = new FormData(form);
            const payload = {
                name: formData.get('name'),
                email: formData.get('email'),
                phone: formData.get('phone'),
                company: formData.get('company') || '',
                service_type: formData.get('service_type'),
                budget_range: formData.get('budget_range') || '',
                message: formData.get('message')
            };

            try {
                const res = await fetch('/api/v1/consultation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.status === 'success') {
                    alert('Terima kasih! Tim Konsultan PT. Aksara Cipta Digital (ACD) telah menerima konsultasi Anda. Kami akan segera menghubungi dalam 1x24 jam.');
                    form.reset();
                    if (window.closeConsultationModal) window.closeConsultationModal();
                } else {
                    alert(data.message || 'Terjadi kendala saat mengirim. Silakan hubungi langsung WhatsApp kami.');
                }
            } catch (err) {
                alert('Gagal terhubung ke server. Silakan hubungi WhatsApp kami langsung.');
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
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
            
            let baseMin = 25;
            let baseMax = 45;

            if (projectType === 'mobile') {
                baseMin = 45; baseMax = 85;
            } else if (projectType === 'erp') {
                baseMin = 75; baseMax = 160;
            } else if (projectType === 'egov') {
                baseMin = 80; baseMax = 200;
            } else if (projectType === 'website') {
                baseMin = 12; baseMax = 25;
            }

            let multiplier = 1.0;
            if (scale === 'large') multiplier = 1.7;
            if (scale === 'enterprise') multiplier = 2.5;

            if (timeline === 'express') multiplier *= 1.25;

            const finalMin = Math.round(baseMin * multiplier);
            const finalMax = Math.round(baseMax * multiplier);

            const resultDisplay = document.getElementById('est-result-price');
            const resultTimeline = document.getElementById('est-result-timeline');

            if (resultDisplay) {
                resultDisplay.innerText = `Rp ${finalMin} Juta - Rp ${finalMax} Juta*`;
            }
            if (resultTimeline) {
                let estWeeks = '8 - 12 Minggu';
                if (projectType === 'erp' || projectType === 'egov') estWeeks = '12 - 20 Minggu';
                if (timeline === 'express') estWeeks += ' (Prioritas Cepat)';
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
