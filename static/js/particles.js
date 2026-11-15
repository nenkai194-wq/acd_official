/**
 * PT Aksara Cipta Digital (ACD Official)
 * Autonomous Neural Mesh & Cyber Spheres Engine (Bola-bola Berpendar & Garis Jaringan Dinamis)
 * 
 * Karakter Eksklusif ACD:
 * - 3-Tier Multi-Depth Spheres (Luminescent Orbs, Constellation Nodes, Micro Quantum Dust)
 * - Orbiting Micro-Satellites on Core Orbs (Melambangkan Microservices & Modul ERP)
 * - Dynamic Gradient Laser Lines connecting proximity nodes
 * - Flowing Cyber Data Packets (Pulsa partikel cahaya yang berjalan di sepanjang garis jaringan secara real-time)
 * - Interactive Magnetic Tether (Kursor mouse & sentuhan HP menghubungkan garis laser dan medan energi)
 * - 60 FPS GPU-accelerated Canvas with 0% battery waste & auto-pause on inactive tab
 */

(function() {
    'use strict';

    function initACDNeuralMesh() {
        const canvas = document.getElementById('ambient-body-canvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let width = 0;
        let height = 0;
        let isMobile = window.innerWidth < 768;
        let dpr = isMobile ? Math.min(window.devicePixelRatio || 1, 1.25) : Math.min(window.devicePixelRatio || 1, 1.5);

        // Core Configurations
        let particles = [];
        let dataPackets = [];
        let maxDistance = 140;
        let mouseDistance = 180;
        let scrollY = window.scrollY || 0;
        let lastScrollY = scrollY;
        let scrollDelta = 0;

        // Interactive Cursor State
        const mouse = {
            x: null,
            y: null,
            targetX: null,
            targetY: null,
            radius: mouseDistance,
            isActive: false,
            pulseAngle: 0
        };

        // ACD Enterprise Brand Color Palette (Deep Obsidian, Electric Indigo, Neon Cyan, Royal Violet, Emerald)
        const palette = [
            { r: 99,  g: 102, b: 241, hex: '#6366f1', name: 'Electric Indigo' },
            { r: 6,   g: 182, b: 212, hex: '#06b6d4', name: 'Cyber Cyan' },
            { r: 139, g: 92,  b: 246, hex: '#8b5cf6', name: 'Royal Violet' },
            { r: 56,  g: 189, b: 248, hex: '#38bdf8', name: 'Sky Tech' },
            { r: 16,  g: 185, b: 129, hex: '#10b981', name: 'Emerald Quantum' }
        ];

        // Screen Resize & DPR calibration
        function resize() {
            width = window.innerWidth;
            height = window.innerHeight;
            isMobile = width < 768;
            dpr = isMobile ? Math.min(window.devicePixelRatio || 1, 1.25) : Math.min(window.devicePixelRatio || 1, 1.5);

            canvas.width = width * dpr;
            canvas.height = height * dpr;
            ctx.scale(dpr, dpr);

            maxDistance = isMobile ? 98 : 142;
            mouseDistance = isMobile ? 125 : 185;
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

        // Touch listener for mobile phones & tablets
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

        // Parallax scroll listener
        window.addEventListener('scroll', () => {
            scrollY = window.scrollY || 0;
            scrollDelta = scrollY - lastScrollY;
            lastScrollY = scrollY;
        }, { passive: true });

        // Calibrated Node Density
        function getOptimalParticleCount() {
            if (window.innerWidth < 768) return 32;       // Smartphone (Presisi, rapi, lega, 0% beban)
            if (window.innerWidth < 1200) return 56;      // Tablet / small laptop
            return 82;                                    // Large desktop monitors
        }

        // --- PARTICLE (SPHERE / BOLA) CLASS ---
        class SphereNode {
            constructor() {
                this.reset(true);
            }

            reset(initial = false) {
                this.x = Math.random() * width;
                this.y = initial ? Math.random() * height : (Math.random() > 0.5 ? -15 : height + 15);

                const tierRand = Math.random();
                if (tierRand < 0.28) {
                    // Tier 1: Micro Quantum Dust (Partikel latar belakang melayang halus)
                    this.tier = 1;
                    this.size = Math.random() * 1.5 + 1.0;
                    this.baseAlpha = Math.random() * 0.35 + 0.15;
                    this.speedX = (Math.random() - 0.5) * 0.32;
                    this.speedY = (Math.random() - 0.5) * 0.32;
                    this.hasSatellite = false;
                    this.parallaxFactor = 0.05;
                } else if (tierRand < 0.78) {
                    // Tier 2: Constellation Node (Bola simpul penghubung garis)
                    this.tier = 2;
                    this.size = Math.random() * 2.2 + 2.0;
                    this.baseAlpha = Math.random() * 0.35 + 0.45;
                    this.speedX = (Math.random() - 0.5) * 0.55;
                    this.speedY = (Math.random() - 0.5) * 0.55;
                    this.hasSatellite = false;
                    this.parallaxFactor = 0.15;
                } else {
                    // Tier 3: Core Luminescent Orb (Bola besar berpendar dengan aura halo & satelit)
                    this.tier = 3;
                    this.size = Math.random() * 3.5 + 4.2;
                    this.baseAlpha = Math.random() * 0.3 + 0.65;
                    this.speedX = (Math.random() - 0.5) * 0.65;
                    this.speedY = (Math.random() - 0.5) * 0.65;
                    this.hasSatellite = !isMobile && Math.random() > 0.35;
                    this.satelliteAngle = Math.random() * Math.PI * 2;
                    this.satelliteSpeed = (Math.random() * 0.03 + 0.015) * (Math.random() > 0.5 ? 1 : -1);
                    this.satelliteDist = this.size * (Math.random() * 2.2 + 2.5);
                    this.parallaxFactor = 0.28;
                }

                this.color = palette[Math.floor(Math.random() * palette.length)];
                this.alpha = this.baseAlpha;
                this.pulseSpeed = Math.random() * 0.03 + 0.012;
                this.pulseAngle = Math.random() * Math.PI * 2;
                this.flashBoost = 0; // Spike when receiving a data packet
            }

            triggerDataPulseSpark() {
                this.flashBoost = 0.45;
            }

            update() {
                this.pulseAngle += this.pulseSpeed;
                this.alpha = this.baseAlpha + Math.sin(this.pulseAngle) * 0.2 + this.flashBoost;
                if (this.alpha > 1) this.alpha = 1;
                if (this.alpha < 0.1) this.alpha = 0.1;
                this.flashBoost *= 0.92;

                // Organic float
                this.x += this.speedX + Math.sin(this.pulseAngle) * 0.22;
                this.y += this.speedY + Math.cos(this.pulseAngle) * 0.22;

                // Satellite rotation
                if (this.hasSatellite) {
                    this.satelliteAngle += this.satelliteSpeed;
                }

                // Subtle parallax on scroll
                if (Math.abs(scrollDelta) > 0.1) {
                    this.y -= scrollDelta * this.parallaxFactor * 0.15;
                }

                // Boundary wrapping
                if (this.x < -25) this.x = width + 25;
                else if (this.x > width + 25) this.x = -25;
                if (this.y < -25) this.y = height + 25;
                else if (this.y > height + 25) this.y = -25;

                // Magnetic mouse repulsion / spring damping
                if (mouse.x !== null && mouse.y !== null) {
                    const dx = mouse.x - this.x;
                    const dy = mouse.y - this.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < mouse.radius && dist > 1) {
                        const force = (mouse.radius - dist) / mouse.radius;
                        const angle = Math.atan2(dy, dx);
                        const pushStrength = this.tier === 3 ? 2.8 : (this.tier === 2 ? 1.8 : 0.9);
                        this.x -= Math.cos(angle) * force * pushStrength;
                        this.y -= Math.sin(angle) * force * pushStrength;
                    }
                }
            }

            draw() {
                const c = this.color;

                // Tier 3: Radiant Multi-Layer Glowing Halo
                if (this.tier === 3) {
                    const glowRadius = this.size * 3.8;
                    const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, glowRadius);
                    grad.addColorStop(0, `rgba(${c.r}, ${c.g}, ${c.b}, ${this.alpha * 0.85})`);
                    grad.addColorStop(0.35, `rgba(${c.r}, ${c.g}, ${c.b}, ${this.alpha * 0.35})`);
                    grad.addColorStop(1, `rgba(${c.r}, ${c.g}, ${c.b}, 0)`);

                    ctx.beginPath();
                    ctx.arc(this.x, this.y, glowRadius, 0, Math.PI * 2);
                    ctx.fillStyle = grad;
                    ctx.fill();

                    // Micro Satellite Node
                    if (this.hasSatellite) {
                        const satX = this.x + Math.cos(this.satelliteAngle) * this.satelliteDist;
                        const satY = this.y + Math.sin(this.satelliteAngle) * this.satelliteDist;
                        ctx.beginPath();
                        ctx.arc(satX, satY, 1.4, 0, Math.PI * 2);
                        ctx.fillStyle = `rgba(6, 182, 212, ${this.alpha * 0.9})`;
                        ctx.fill();

                        // Faint orbital line
                        ctx.beginPath();
                        ctx.arc(this.x, this.y, this.satelliteDist, 0, Math.PI * 2);
                        ctx.strokeStyle = `rgba(${c.r}, ${c.g}, ${c.b}, ${this.alpha * 0.12})`;
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }

                // Core Sphere Body
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${c.r}, ${c.g}, ${c.b}, ${this.alpha})`;
                ctx.fill();

                // Bright center core for Tier 2 & 3 (Gem-like shine)
                if (this.tier >= 2) {
                    ctx.beginPath();
                    ctx.arc(this.x - this.size * 0.25, this.y - this.size * 0.25, this.size * 0.35, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(255, 255, 255, ${this.alpha * 0.75})`;
                    ctx.fill();
                }
            }
        }

        // --- CYBER DATA PACKET CLASS (PULSA DATA BERJALAN DI SEPANJANG GARIS) ---
        class DataPacket {
            constructor(p1, p2) {
                this.p1 = p1;
                this.p2 = p2;
                this.progress = 0;
                this.speed = Math.random() * 0.02 + 0.012; // Speed across the line
                this.color = p1.color;
                this.isDone = false;
            }

            update() {
                this.progress += this.speed;
                if (this.progress >= 1) {
                    this.progress = 1;
                    this.isDone = true;
                    if (this.p2.triggerDataPulseSpark) {
                        this.p2.triggerDataPulseSpark();
                    }
                }
            }

            draw() {
                const curX = this.p1.x + (this.p2.x - this.p1.x) * this.progress;
                const curY = this.p1.y + (this.p2.y - this.p1.y) * this.progress;
                const c = this.color;

                // Glowing tail
                const tailLen = 0.15;
                const tailStart = Math.max(0, this.progress - tailLen);
                const tailX = this.p1.x + (this.p2.x - this.p1.x) * tailStart;
                const tailY = this.p1.y + (this.p2.y - this.p1.y) * tailStart;

                const grad = ctx.createLinearGradient(tailX, tailY, curX, curY);
                grad.addColorStop(0, `rgba(${c.r}, ${c.g}, ${c.b}, 0)`);
                grad.addColorStop(1, 'rgba(255, 255, 255, 0.95)');

                ctx.beginPath();
                ctx.moveTo(tailX, tailY);
                ctx.lineTo(curX, curY);
                ctx.strokeStyle = grad;
                ctx.lineWidth = 1.8;
                ctx.stroke();

                // Photon head
                ctx.beginPath();
                ctx.arc(curX, curY, 2.0, 0, Math.PI * 2);
                ctx.fillStyle = '#ffffff';
                ctx.shadowColor = `rgb(${c.r}, ${c.g}, ${c.b})`;
                ctx.shadowBlur = 6;
                ctx.fill();
                ctx.shadowBlur = 0; // reset
            }
        }

        // Initialize particles
        function initParticles() {
            particles = [];
            dataPackets = [];
            const count = getOptimalParticleCount();
            for (let i = 0; i < count; i++) {
                particles.push(new SphereNode());
            }
        }

        initParticles();

        // Draw dynamic constellation lines & spawn cyber packets
        function drawConnections() {
            const len = particles.length;
            let activePairs = [];

            for (let i = 0; i < len; i++) {
                const p1 = particles[i];
                if (p1.tier === 1) continue; // Dust doesn't anchor lines

                for (let j = i + 1; j < len; j++) {
                    const p2 = particles[j];
                    if (p2.tier === 1) continue;

                    const dx = p1.x - p2.x;
                    const dy = p1.y - p2.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < maxDistance) {
                        const alpha = (1 - dist / maxDistance) * 0.26;
                        activePairs.push({ p1, p2 });

                        // Dynamic gradient line between node colors
                        const grad = ctx.createLinearGradient(p1.x, p1.y, p2.x, p2.y);
                        grad.addColorStop(0, `rgba(${p1.color.r}, ${p1.color.g}, ${p1.color.b}, ${alpha})`);
                        grad.addColorStop(1, `rgba(${p2.color.r}, ${p2.color.g}, ${p2.color.b}, ${alpha})`);

                        ctx.beginPath();
                        ctx.moveTo(p1.x, p1.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.strokeStyle = grad;
                        ctx.lineWidth = 0.9;
                        ctx.stroke();
                    }
                }

                // Interactive connection line to mouse cursor
                if (mouse.x !== null && mouse.y !== null && p1.tier >= 2) {
                    const mdx = p1.x - mouse.x;
                    const mdy = p1.y - mouse.y;
                    const mdist = Math.sqrt(mdx * mdx + mdy * mdy);

                    if (mdist < mouseDistance) {
                        const mAlpha = (1 - mdist / mouseDistance) * 0.42;
                        const mGrad = ctx.createLinearGradient(p1.x, p1.y, mouse.x, mouse.y);
                        mGrad.addColorStop(0, `rgba(${p1.color.r}, ${p1.color.g}, ${p1.color.b}, ${mAlpha})`);
                        mGrad.addColorStop(1, `rgba(6, 182, 212, ${mAlpha * 1.2})`);

                        ctx.beginPath();
                        ctx.moveTo(p1.x, p1.y);
                        ctx.lineTo(mouse.x, mouse.y);
                        ctx.strokeStyle = mGrad;
                        ctx.lineWidth = 1.1;
                        ctx.stroke();
                    }
                }
            }

            // Spawn data packets along active connections (Cap at 5 concurrent packets for 0% lag)
            if (activePairs.length > 0 && dataPackets.length < 5 && Math.random() < 0.06) {
                const randomPair = activePairs[Math.floor(Math.random() * activePairs.length)];
                dataPackets.push(new DataPacket(randomPair.p1, randomPair.p2));
            }

            // Update & render data packets
            for (let k = dataPackets.length - 1; k >= 0; k--) {
                const pkt = dataPackets[k];
                pkt.update();
                pkt.draw();
                if (pkt.isDone) {
                    dataPackets.splice(k, 1);
                }
            }
        }

        // Draw interactive cursor aura
        function drawCursorAura() {
            if (mouse.x === null || mouse.y === null || !mouse.isActive) return;

            mouse.pulseAngle += 0.05;
            const radius = isMobile ? 85 : 125;

            // Soft radial ambient field
            const grad = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, radius);
            grad.addColorStop(0, 'rgba(6, 182, 212, 0.16)');
            grad.addColorStop(0.45, 'rgba(99, 102, 241, 0.08)');
            grad.addColorStop(1, 'rgba(2, 6, 23, 0)');

            ctx.beginPath();
            ctx.arc(mouse.x, mouse.y, radius, 0, Math.PI * 2);
            ctx.fillStyle = grad;
            ctx.fill();

            // Central beacon dot with concentric ping ring
            ctx.beginPath();
            ctx.arc(mouse.x, mouse.y, 3, 0, Math.PI * 2);
            ctx.fillStyle = '#38bdf8';
            ctx.fill();

            const pingRadius = 6 + Math.sin(mouse.pulseAngle) * 4;
            ctx.beginPath();
            ctx.arc(mouse.x, mouse.y, Math.max(3, pingRadius), 0, Math.PI * 2);
            ctx.strokeStyle = 'rgba(6, 182, 212, 0.45)';
            ctx.lineWidth = 1;
            ctx.stroke();
        }

        // Animation Loop
        let animationFrameId = null;
        let isTabActive = true;

        function animate() {
            if (!isTabActive) return;

            // Lerp mouse coordinates smoothly
            if (mouse.targetX !== null && mouse.targetY !== null) {
                if (mouse.x === null) {
                    mouse.x = mouse.targetX;
                    mouse.y = mouse.targetY;
                } else {
                    mouse.x += (mouse.targetX - mouse.x) * 0.14;
                    mouse.y += (mouse.targetY - mouse.y) * 0.14;
                }
            } else {
                mouse.x = null;
                mouse.y = null;
            }

            // Dampen scroll
            scrollDelta *= 0.85;

            // Clear canvas
            ctx.clearRect(0, 0, width, height);

            // 1. Draw cursor interactive aura
            drawCursorAura();

            // 2. Draw constellation lines & cyber data packets
            drawConnections();

            // 3. Update & render spheres
            const pLen = particles.length;
            for (let i = 0; i < pLen; i++) {
                particles[i].update();
                particles[i].draw();
            }

            animationFrameId = requestAnimationFrame(animate);
        }

        animate();

        // Battery Saver: Pause loop when tab is hidden or minimized
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                isTabActive = false;
                if (animationFrameId) cancelAnimationFrame(animationFrameId);
            } else {
                isTabActive = true;
                lastScrollY = window.scrollY || 0;
                scrollDelta = 0;
                animate();
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initACDNeuralMesh);
    } else {
        initACDNeuralMesh();
    }
})();
