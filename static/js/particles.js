/**
 * PT Aksara Cipta Digital (ACD Official)
 * Ambient Body Animation & Constellation Mesh (Komunigrafik Style)
 * 
 * Features:
 * - Full-body fixed ambient cosmic canvas
 * - 3-tier depth-of-field particles (cosmic dust, constellation nodes, radiant glowing orbs)
 * - Harmonious ACD Brand Palette (Deep Obsidian, Electric Indigo #6366f1, Neon Cyan #06b6d4, Violet #8b5cf6)
 * - Interactive cursor magnetic repulsion & smooth ambient aura
 * - Parallax scroll dynamics
 * - Auto battery saver (pauses on inactive tabs) & 60 FPS mobile optimization
 */

(function() {
    'use strict';

    function initAmbientBodyAnimation() {
        const canvas = document.getElementById('ambient-body-canvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let width = 0;
        let height = 0;
        let isMobile = window.innerWidth < 768;
        let dpr = isMobile ? Math.min(window.devicePixelRatio || 1, 1.25) : Math.min(window.devicePixelRatio || 1, 1.75); // Capped for ultra-light GPU & battery usage

        // Particle configuration
        let particles = [];
        let maxDistance = 135;
        let mouseDistance = 165;
        let scrollY = window.scrollY || 0;
        let lastScrollY = scrollY;
        let scrollDelta = 0;

        // Smooth mouse tracking with lerp interpolation
        const mouse = {
            x: null,
            y: null,
            targetX: null,
            targetY: null,
            radius: mouseDistance,
            isActive: false
        };

        // ACD Primary Color Palette (Harmonized with Dark Obsidian #020617)
        const palette = [
            { r: 99,  g: 102, b: 241, name: 'indigo' },   // #6366f1
            { r: 6,   g: 182, b: 212, name: 'cyan' },     // #06b6d4
            { r: 56,  g: 189, b: 248, name: 'sky' },      // #38bdf8
            { r: 139, g: 92,  b: 246, name: 'violet' },   // #8b5cf6
            { r: 129, g: 140, b: 248, name: 'softBlue' }  // #818cf8
        ];

        // Resize & Retina display setup
        function resize() {
            width = window.innerWidth;
            height = window.innerHeight;
            canvas.width = width * dpr;
            canvas.height = height * dpr;
            ctx.scale(dpr, dpr);

            maxDistance = width < 768 ? 95 : 135;
            mouseDistance = width < 768 ? 120 : 175;
            mouse.radius = mouseDistance;
        }

        resize();
        window.addEventListener('resize', resize, { passive: true });

        // Mouse listeners
        window.addEventListener('mousemove', (e) => {
            mouse.targetX = e.clientX;
            mouse.targetY = e.clientY;
            mouse.isActive = true;
        }, { passive: true });

        window.addEventListener('mouseleave', () => {
            mouse.targetX = null;
            mouse.targetY = null;
            mouse.isActive = false;
        }, { passive: true });

        // Touch listener for mobile interaction
        window.addEventListener('touchmove', (e) => {
            if (e.touches && e.touches[0]) {
                mouse.targetX = e.touches[0].clientX;
                mouse.targetY = e.touches[0].clientY;
                mouse.isActive = true;
            }
        }, { passive: true });

        window.addEventListener('touchend', () => {
            mouse.targetX = null;
            mouse.targetY = null;
            mouse.isActive = false;
        }, { passive: true });

        // Scroll listener for 3D parallax depth
        window.addEventListener('scroll', () => {
            scrollY = window.scrollY || 0;
            scrollDelta = scrollY - lastScrollY;
            lastScrollY = scrollY;
        }, { passive: true });

        // Determine particle count based on screen size (Ultra-lightweight footprint)
        function getOptimalParticleCount() {
            if (window.innerWidth < 768) return 22;      // Mobile phone (feather-light, 0% lag)
            if (window.innerWidth < 1200) return 45;     // Tablet / small laptop
            return 72;                                   // Large desktop monitors
        }

        // Particle Class
        class Particle {
            constructor() {
                this.reset(true);
            }

            reset(initial = false) {
                this.x = Math.random() * width;
                this.y = initial ? Math.random() * height : (Math.random() > 0.5 ? -10 : height + 10);
                
                // Tier assignment: 1 = Background Dust (40%), 2 = Constellation Node (45%), 3 = Glowing Orb (15%)
                const tierRand = Math.random();
                if (tierRand < 0.40) {
                    this.tier = 1; // Faint background dust
                    this.size = Math.random() * 1.2 + 0.6;
                    this.baseAlpha = Math.random() * 0.35 + 0.15;
                    this.speedX = (Math.random() - 0.5) * 0.35;
                    this.speedY = (Math.random() - 0.5) * 0.35;
                    this.parallaxFactor = 0.05;
                } else if (tierRand < 0.85) {
                    this.tier = 2; // Interactive constellation node
                    this.size = Math.random() * 1.8 + 1.2;
                    this.baseAlpha = Math.random() * 0.45 + 0.35;
                    this.speedX = (Math.random() - 0.5) * 0.65;
                    this.speedY = (Math.random() - 0.5) * 0.65;
                    this.parallaxFactor = 0.18;
                } else {
                    this.tier = 3; // Radiant glowing orb
                    this.size = Math.random() * 2.5 + 2.2;
                    this.baseAlpha = Math.random() * 0.4 + 0.55;
                    this.speedX = (Math.random() - 0.5) * 0.85;
                    this.speedY = (Math.random() - 0.5) * 0.85;
                    this.parallaxFactor = 0.35;
                }

                this.color = palette[Math.floor(Math.random() * palette.length)];
                this.alpha = this.baseAlpha;
                this.pulseSpeed = Math.random() * 0.025 + 0.01;
                this.pulseAngle = Math.random() * Math.PI * 2;
                this.waveAngle = Math.random() * Math.PI * 2;
                this.waveSpeed = Math.random() * 0.02 + 0.008;
            }

            update() {
                // Organic harmonic wave motion
                this.pulseAngle += this.pulseSpeed;
                this.waveAngle += this.waveSpeed;
                this.alpha = this.baseAlpha + Math.sin(this.pulseAngle) * 0.18;
                if (this.alpha < 0.05) this.alpha = 0.05;

                // Base velocity + sine oscillation (underwater/cosmic dust feel)
                this.x += this.speedX + Math.cos(this.waveAngle) * 0.25;
                this.y += this.speedY + Math.sin(this.waveAngle) * 0.25;

                // Subtle parallax shift on scroll
                if (Math.abs(scrollDelta) > 0.1) {
                    this.y -= scrollDelta * this.parallaxFactor * 0.15;
                }

                // Smooth boundary wrapping
                if (this.x < -20) this.x = width + 20;
                else if (this.x > width + 20) this.x = -20;
                if (this.y < -20) this.y = height + 20;
                else if (this.y > height + 20) this.y = -20;

                // Interactive mouse repulsion with spring damping
                if (mouse.x !== null && mouse.y !== null) {
                    const dx = mouse.x - this.x;
                    const dy = mouse.y - this.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < mouse.radius && dist > 1) {
                        const force = (mouse.radius - dist) / mouse.radius;
                        const angle = Math.atan2(dy, dx);
                        const pushStrength = this.tier === 3 ? 3.2 : (this.tier === 2 ? 2.2 : 1.2);
                        
                        this.x -= Math.cos(angle) * force * pushStrength;
                        this.y -= Math.sin(angle) * force * pushStrength;
                    }
                }
            }

            draw() {
                const c = this.color;
                
                // Tier 3: Glowing Bokeh Halo
                if (this.tier === 3) {
                    const glowRadius = this.size * 3.8;
                    const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, glowRadius);
                    grad.addColorStop(0, `rgba(${c.r}, ${c.g}, ${c.b}, ${this.alpha * 0.9})`);
                    grad.addColorStop(0.35, `rgba(${c.r}, ${c.g}, ${c.b}, ${this.alpha * 0.4})`);
                    grad.addColorStop(1, `rgba(${c.r}, ${c.g}, ${c.b}, 0)`);

                    ctx.beginPath();
                    ctx.arc(this.x, this.y, glowRadius, 0, Math.PI * 2);
                    ctx.fillStyle = grad;
                    ctx.fill();
                }

                // Core Particle Dot
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${c.r}, ${c.g}, ${c.b}, ${this.alpha})`;
                ctx.fill();
            }
        }

        // Initialize particles
        function initParticles() {
            particles = [];
            const count = getOptimalParticleCount();
            for (let i = 0; i < count; i++) {
                particles.push(new Particle());
            }
        }

        initParticles();

        // Connect constellation nodes with delicate glowing lines
        function drawConnections() {
            const len = particles.length;
            for (let i = 0; i < len; i++) {
                const p1 = particles[i];
                if (p1.tier === 1) continue; // Dust doesn't connect lines for clarity

                for (let j = i + 1; j < len; j++) {
                    const p2 = particles[j];
                    if (p2.tier === 1) continue;

                    const dx = p1.x - p2.x;
                    const dy = p1.y - p2.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < maxDistance) {
                        const alpha = (1 - dist / maxDistance) * 0.22;
                        
                        // Linear gradient connection line between two nodes
                        const grad = ctx.createLinearGradient(p1.x, p1.y, p2.x, p2.y);
                        grad.addColorStop(0, `rgba(${p1.color.r}, ${p1.color.g}, ${p1.color.b}, ${alpha})`);
                        grad.addColorStop(1, `rgba(${p2.color.r}, ${p2.color.g}, ${p2.color.b}, ${alpha})`);

                        ctx.beginPath();
                        ctx.moveTo(p1.x, p1.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.strokeStyle = grad;
                        ctx.lineWidth = 0.85;
                        ctx.stroke();
                    }
                }

                // Draw delicate line to mouse cursor if near
                if (mouse.x !== null && mouse.y !== null && p1.tier >= 2) {
                    const mdx = p1.x - mouse.x;
                    const mdy = p1.y - mouse.y;
                    const mdist = Math.sqrt(mdx * mdx + mdy * mdy);

                    if (mdist < mouseDistance) {
                        const mAlpha = (1 - mdist / mouseDistance) * 0.35;
                        ctx.beginPath();
                        ctx.moveTo(p1.x, p1.y);
                        ctx.lineTo(mouse.x, mouse.y);
                        ctx.strokeStyle = `rgba(6, 182, 212, ${mAlpha})`;
                        ctx.lineWidth = 1;
                        ctx.stroke();
                    }
                }
            }
        }

        // Draw ambient interactive cursor halo
        function drawCursorAura() {
            if (mouse.x === null || mouse.y === null || !mouse.isActive) return;

            const radius = width < 768 ? 90 : 130;
            const grad = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, radius);
            grad.addColorStop(0, 'rgba(99, 102, 241, 0.12)');
            grad.addColorStop(0.5, 'rgba(6, 182, 212, 0.05)');
            grad.addColorStop(1, 'rgba(2, 6, 23, 0)');

            ctx.beginPath();
            ctx.arc(mouse.x, mouse.y, radius, 0, Math.PI * 2);
            ctx.fillStyle = grad;
            ctx.fill();
        }

        // Main Animation Loop
        let animationFrameId = null;
        let isTabActive = true;

        function animate() {
            if (!isTabActive) return;

            // Lerp mouse cursor smoothly
            if (mouse.targetX !== null && mouse.targetY !== null) {
                if (mouse.x === null) {
                    mouse.x = mouse.targetX;
                    mouse.y = mouse.targetY;
                } else {
                    mouse.x += (mouse.targetX - mouse.x) * 0.12;
                    mouse.y += (mouse.targetY - mouse.y) * 0.12;
                }
            } else {
                mouse.x = null;
                mouse.y = null;
            }

            // Dampen scroll delta smoothly
            scrollDelta *= 0.85;

            // Clear canvas
            ctx.clearRect(0, 0, width, height);

            // 1. Draw interactive cursor aura
            drawCursorAura();

            // 2. Draw connections first (behind nodes)
            drawConnections();

            // 3. Update & draw particles
            for (let i = 0; i < particles.length; i++) {
                particles[i].update();
                particles[i].draw();
            }

            animationFrameId = requestAnimationFrame(animate);
        }

        animate();

        // Video Autoplay & Battery Watchdog (Supports hero-ambient-video & ambient-body-video)
        const video = document.getElementById('hero-ambient-video') || document.getElementById('ambient-body-video');
        if (video) {
            video.muted = true;
            const playPromise = video.play();
            if (playPromise !== undefined) {
                playPromise.catch(() => {
                    const tryPlay = () => {
                        video.play().catch(() => {});
                        window.removeEventListener('click', tryPlay);
                        window.removeEventListener('touchstart', tryPlay);
                        window.removeEventListener('scroll', tryPlay);
                    };
                    window.addEventListener('click', tryPlay, { once: true });
                    window.addEventListener('touchstart', tryPlay, { once: true });
                    window.addEventListener('scroll', tryPlay, { once: true });
                });
            }

            // Smart IntersectionObserver: Freeze video decoding when scrolled out of Hero (0% CPU/GPU overhead)
            if ('IntersectionObserver' in window) {
                const videoObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            if (video.paused && !document.hidden) {
                                video.play().catch(() => {});
                            }
                        } else {
                            if (!video.paused) {
                                video.pause();
                            }
                        }
                    });
                }, { threshold: 0.05 });
                videoObserver.observe(video);
            }
        }

        // Battery Saver: Pause loop and video when tab is hidden or minimized
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                isTabActive = false;
                if (animationFrameId) cancelAnimationFrame(animationFrameId);
                if (video && !video.paused) video.pause();
            } else {
                isTabActive = true;
                lastScrollY = window.scrollY || 0;
                scrollDelta = 0;
                if (video && video.paused) video.play().catch(() => {});
                animate();
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAmbientBodyAnimation);
    } else {
        initAmbientBodyAnimation();
    }
})();
