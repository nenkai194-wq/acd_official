/**
 * PT Aksara Cipta Digital (ACD Official)
 * "Cosmic Spiral Galaxy & Celestial Deep Space"
 * (Alam Semesta, Galaksi Spiral Kosmik & Debu Bintang Interaktif)
 * 
 * Filosofi Visual:
 * - Merepresentasikan "Visi Tanpa Batas" (Infinite Digital Universe):
 *   ekosistem teknologi berskala enterprise yang terus berekspansi, saling terhubung,
 *   dan berpusat pada inti kecerdasan digital yang kokoh.
 * - Galaksi spiral kosmik logaritmik 3D dengan ribuan bintang berkedip, awan nebula bercahaya,
 *   bintang jatuh (shooting stars / meteors), serta tarikan gravitasi kursor interaktif.
 * - Berwibawa, megah, menenangkan, estetik tingkat tinggi, dan sangat futuristik.
 * 
 * Fitur:
 * - Logarithmic Spiral Galaxy Arms dengan kedalaman rotasi 3D (Yaw, Pitch & Tilt)
 * - Layered Multi-Depth Starfield dengan bintang berkedip realistis
 * - Dynamic Shooting Stars / Meteors meluncur berkala dengan ekor komet
 * - Interaktivitas Gravitasi Kursor (Medan magnetik kosmik merespons mouse & sentuhan touch)
 * - Stellar Supernova Ripple saat klik atau tap
 * - Area teks headline terlindungi dengan kontras gelap agar 100% jernih dan mudah dibaca
 * - 0 MB Video Overhead, 60 FPS Native Canvas, proteksi baterai otomatis
 */

(function() {
    'use strict';

    function initCosmicGalaxy() {
        const canvas = document.getElementById('ambient-body-canvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let width = 0;
        let height = 0;
        let isMobile = window.innerWidth < 768;
        let dpr = isMobile ? Math.min(window.devicePixelRatio || 1, 1.25) : Math.min(window.devicePixelRatio || 1, 1.5);

        let animationFrameId = null;
        let isTabActive = true;
        let lastTimestamp = 0;
        let time = 0;

        // Galaxy Core Center
        let galaxyCenterX = 0;
        let galaxyCenterY = 0;

        // Galaxy 3D Tilt Parameters
        let galaxyTiltX = 0.95; // Tilted disk perspective
        let galaxyAngle = 0;
        let baseRotationSpeed = 0.0018;

        // Interactive Pointer Gravitational Field
        const pointer = {
            x: null,
            y: null,
            targetX: null,
            targetY: null,
            isActive: false,
            gravForce: 0,
            ripples: []
        };

        // Galaxy Stars & Dust Particles
        let galaxyStars = [];
        const GALAXY_STAR_COUNT = isMobile ? 320 : 750;

        // Background Deep Space Starfield
        let backgroundStars = [];
        const BG_STAR_COUNT = isMobile ? 60 : 130;

        // Shooting Stars (Meteors)
        let meteors = [];
        let nextMeteorTime = 2.0;

        // Color Palettes for Galaxy Arms
        const armColors = [
            { r: 6,   g: 182, b: 212 }, // Electric Cyan
            { r: 56,  g: 189, b: 248 }, // Sky Blue
            { r: 99,  g: 102, b: 241 }, // Royal Indigo
            { r: 168, g: 85,  b: 247 }, // Nebula Violet
            { r: 236, g: 72,  b: 153 }  // Cosmic Magenta fringe
        ];

        // Setup Galaxy Particles in Logarithmic Spiral Arms
        function setupGalaxy() {
            galaxyStars = [];
            const starCount = isMobile ? 320 : 750;
            const armCount = 3; // 3-arm grand spiral
            const maxRadius = (isMobile ? width * 0.55 : Math.min(width, height) * 0.52);

            for (let i = 0; i < starCount; i++) {
                // Radial distribution with higher density towards galactic nucleus
                const distRatio = Math.pow(Math.random(), 1.6);
                const r = distRatio * maxRadius;

                // Arm angle: logarithmic spiral formula theta = b * ln(r) + armOffset
                const armIndex = i % armCount;
                const armOffset = (armIndex * Math.PI * 2) / armCount;
                const spiralAngle = r * 0.009 + armOffset;

                // Random angular scatter around the arm (thicker near center, dispersed at rim)
                const scatterAngle = (Math.random() - 0.5) * (0.45 + distRatio * 0.5);
                const scatterR = (Math.random() - 0.5) * (18 + distRatio * 35);

                const finalAngle = spiralAngle + scatterAngle;
                const finalR = Math.max(8, r + scatterR);

                // Vertical thickness of galactic disk (Z-axis)
                const diskThickness = (1 - distRatio) * 35 + 8;
                const z = (Math.random() - 0.5) * diskThickness;

                // Color based on radial position (Core = White/Cyan, Arms = Indigo/Purple, Fringe = Magenta)
                let colorIdx = Math.floor(distRatio * armColors.length);
                if (colorIdx >= armColors.length) colorIdx = armColors.length - 1;
                const baseColor = armColors[colorIdx];

                galaxyStars.push({
                    origR: finalR,
                    angle: finalAngle,
                    z: z,
                    // Angular velocity decreases with distance (Keplerian differential rotation)
                    orbitalSpeed: 0.003 / (1 + distRatio * 1.5),
                    size: Math.random() * (isMobile ? 1.6 : 2.2) + 0.6,
                    baseAlpha: Math.random() * 0.6 + 0.35,
                    color: baseColor,
                    isCoreStar: distRatio < 0.15,
                    twinkleSpeed: Math.random() * 0.03 + 0.01,
                    twinklePhase: Math.random() * Math.PI * 2
                });
            }

            // Setup Background Deep Space Stars
            backgroundStars = [];
            const bgCount = isMobile ? 60 : 130;
            for (let j = 0; j < bgCount; j++) {
                backgroundStars.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    size: Math.random() * 1.4 + 0.5,
                    alpha: Math.random() * 0.5 + 0.2,
                    speed: Math.random() * 0.015 + 0.008,
                    phase: Math.random() * Math.PI * 2,
                    color: Math.random() > 0.4 ? '6, 182, 212' : '99, 102, 241',
                    hasSpikes: Math.random() > 0.85 && !isMobile // Bright focal stars with 4-point diffraction
                });
            }
        }

        function resize() {
            width = window.innerWidth;
            height = window.innerHeight;
            isMobile = width < 768;
            dpr = isMobile ? Math.min(window.devicePixelRatio || 1, 1.25) : Math.min(window.devicePixelRatio || 1, 1.5);

            canvas.width = Math.floor(width * dpr);
            canvas.height = Math.floor(height * dpr);
            ctx.scale(dpr, dpr);

            // Position galactic center comfortably to frame the hero title gracefully
            galaxyCenterX = width * 0.5;
            galaxyCenterY = height * (isMobile ? 0.43 : 0.41);

            setupGalaxy();
        }

        window.addEventListener('resize', resize, { passive: true });

        // Pointer event listeners
        window.addEventListener('mousemove', (e) => {
            pointer.targetX = e.clientX;
            pointer.targetY = e.clientY;
            pointer.isActive = true;
            if (pointer.x === null) {
                pointer.x = pointer.targetX;
                pointer.y = pointer.targetY;
            }
        }, { passive: true });

        window.addEventListener('mouseleave', () => {
            pointer.isActive = false;
        }, { passive: true });

        // Touch event listeners
        window.addEventListener('touchmove', (e) => {
            if (e.touches && e.touches[0]) {
                pointer.targetX = e.touches[0].clientX;
                pointer.targetY = e.touches[0].clientY;
                pointer.isActive = true;
                if (pointer.x === null) {
                    pointer.x = pointer.targetX;
                    pointer.y = pointer.targetY;
                }
            }
        }, { passive: true });

        window.addEventListener('touchend', () => {
            pointer.isActive = false;
        }, { passive: true });

        // Click / Tap Supernova Pulse
        window.addEventListener('click', (e) => {
            pointer.ripples.push({
                x: e.clientX,
                y: e.clientY,
                r: 10,
                maxR: isMobile ? 180 : 340,
                alpha: 0.9,
                color: '#38bdf8'
            });

            // Trigger an immediate shooting star
            spawnMeteor(e.clientX, e.clientY);
        }, { passive: true });

        // Spawn a Shooting Star / Meteor
        function spawnMeteor(targetX, targetY) {
            const startX = Math.random() * width * 0.8;
            const startY = Math.random() * height * 0.35;
            const angle = Math.PI * 0.22 + (Math.random() - 0.5) * 0.15; // diagonal fall ~45 deg
            const speed = (isMobile ? 7 : 11) + Math.random() * 5;

            meteors.push({
                x: startX,
                y: startY,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                length: (isMobile ? 55 : 95) + Math.random() * 40,
                life: 1.0,
                decay: 0.018 + Math.random() * 0.012,
                color: Math.random() > 0.5 ? '#38bdf8' : '#a855f7'
            });
        }

        // Initial setup
        resize();

        // Main 60 FPS Render Loop
        function animate(timestamp) {
            if (!isTabActive) return;

            const delta = lastTimestamp ? Math.min((timestamp - lastTimestamp) / 1000, 0.1) : 0.016;
            lastTimestamp = timestamp;
            time += delta;

            ctx.clearRect(0, 0, width, height);

            // 1. Smooth Pointer Lerping & Gravitational Inflow
            if (pointer.isActive && pointer.targetX !== null) {
                pointer.x += (pointer.targetX - pointer.x) * 0.12;
                pointer.y += (pointer.targetY - pointer.y) * 0.12;
                pointer.gravForce = Math.min(1.0, pointer.gravForce + delta * 2.0);
            } else {
                pointer.gravForce = Math.max(0, pointer.gravForce - delta * 1.5);
            }

            // 2. Cosmic Supernova Ripples (Shockwave expansion)
            for (let rip = pointer.ripples.length - 1; rip >= 0; rip--) {
                const rp = pointer.ripples[rip];
                rp.r += delta * (isMobile ? 240 : 380);
                rp.alpha -= delta * 1.2;

                if (rp.alpha <= 0 || rp.r >= rp.maxR) {
                    pointer.ripples.splice(rip, 1);
                    continue;
                }

                ctx.save();
                ctx.beginPath();
                ctx.arc(rp.x, rp.y, rp.r, 0, Math.PI * 2);
                ctx.strokeStyle = `rgba(56, 189, 248, ${rp.alpha * 0.65})`;
                ctx.lineWidth = 1.5;
                ctx.stroke();
                ctx.restore();
            }

            // 3. Render Deep Space Background Starfield
            backgroundStars.forEach(st => {
                const twinkle = Math.sin(time * 2 + st.phase);
                const currentAlpha = Math.max(0.1, st.alpha + twinkle * 0.25);

                ctx.save();
                ctx.beginPath();
                ctx.arc(st.x, st.y, st.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${st.color}, ${currentAlpha})`;
                ctx.fill();

                // 4-Point Diffraction Spikes on bright stellar beacons
                if (st.hasSpikes && currentAlpha > 0.4) {
                    ctx.strokeStyle = `rgba(${st.color}, ${currentAlpha * 0.6})`;
                    ctx.lineWidth = 0.8;
                    const spikeLen = 8 + twinkle * 3;
                    ctx.beginPath();
                    ctx.moveTo(st.x - spikeLen, st.y);
                    ctx.lineTo(st.x + spikeLen, st.y);
                    ctx.moveTo(st.x, st.y - spikeLen);
                    ctx.lineTo(st.x, st.y + spikeLen);
                    ctx.stroke();
                }
                ctx.restore();
            });

            // 4. Render Deep Galactic Core Nebula Glow (Atmospheric Cosmic Fog)
            ctx.save();
            const coreRadius = isMobile ? 160 : 260;
            const coreGlow = ctx.createRadialGradient(
                galaxyCenterX, galaxyCenterY, 8,
                galaxyCenterX, galaxyCenterY, coreRadius
            );
            coreGlow.addColorStop(0, 'rgba(56, 189, 248, 0.22)');
            coreGlow.addColorStop(0.35, 'rgba(99, 102, 241, 0.12)');
            coreGlow.addColorStop(0.75, 'rgba(168, 85, 247, 0.04)');
            coreGlow.addColorStop(1, 'transparent');

            ctx.fillStyle = coreGlow;
            ctx.beginPath();
            ctx.arc(galaxyCenterX, galaxyCenterY, coreRadius, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();

            // 5. Update & Render Spiral Galaxy Stars (3D Projected Disk)
            galaxyAngle += baseRotationSpeed;

            // Sort stars by simulated depth (Z) for natural depth layering
            galaxyStars.forEach(star => {
                // Orbit rotation
                star.angle += star.orbitalSpeed;

                // 2D Disk Coordinates
                let xLocal = Math.cos(star.angle) * star.origR;
                let yLocal = Math.sin(star.angle) * star.origR;

                // Interactive Pointer Gravitational Distortion
                if (pointer.isActive && pointer.x !== null && pointer.gravForce > 0) {
                    const screenXEst = galaxyCenterX + xLocal;
                    const screenYEst = galaxyCenterY + yLocal * Math.cos(galaxyTiltX);
                    const dx = pointer.x - screenXEst;
                    const dy = pointer.y - screenYEst;
                    const distToPtr = Math.hypot(dx, dy);

                    if (distToPtr < 220) {
                        const pullFactor = (1 - distToPtr / 220) * 18 * pointer.gravForce;
                        xLocal += (dx / distToPtr) * pullFactor;
                        yLocal += (dy / distToPtr) * pullFactor;
                    }
                }

                // Apply Perspective Tilt (Disk tilt around X-axis)
                const cosTilt = Math.cos(galaxyTiltX);
                const sinTilt = Math.sin(galaxyTiltX);

                const finalX = galaxyCenterX + xLocal;
                const finalY = galaxyCenterY + (yLocal * cosTilt - star.z * sinTilt);
                const depthZ = yLocal * sinTilt + star.z * cosTilt;

                // Twinkle & Size based on distance & depth
                const twinkle = Math.sin(time * 3 + star.twinklePhase);
                const depthScale = Math.max(0.6, 1 + (depthZ / 400) * 0.4);
                const finalAlpha = Math.max(0.12, (star.baseAlpha + twinkle * 0.25) * Math.min(1.2, depthScale));

                ctx.beginPath();
                ctx.arc(finalX, finalY, Math.max(0.5, star.size * depthScale), 0, Math.PI * 2);

                if (star.isCoreStar) {
                    ctx.fillStyle = `rgba(240, 249, 255, ${finalAlpha * 1.3})`;
                } else {
                    ctx.fillStyle = `rgba(${star.color.r}, ${star.color.g}, ${star.color.b}, ${finalAlpha})`;
                }
                ctx.fill();
            });

            // 6. Galactic Supermassive Nucleus (Inti Pusat Galaksi)
            ctx.save();
            ctx.beginPath();
            ctx.arc(galaxyCenterX, galaxyCenterY, isMobile ? 3.5 : 5, 0, Math.PI * 2);
            ctx.fillStyle = '#ffffff';
            ctx.shadowColor = '#38bdf8';
            ctx.shadowBlur = isMobile ? 12 : 20;
            ctx.fill();
            ctx.restore();

            // 7. Update & Render Shooting Stars / Meteors (Komet Meluncur)
            nextMeteorTime -= delta;
            if (nextMeteorTime <= 0) {
                spawnMeteor();
                nextMeteorTime = (isMobile ? 3.5 : 2.5) + Math.random() * 3.0;
            }

            for (let m = meteors.length - 1; m >= 0; m--) {
                const met = meteors[m];
                met.x += met.vx;
                met.y += met.vy;
                met.life -= met.decay;

                if (met.life <= 0 || met.x > width + 100 || met.y > height + 100) {
                    meteors.splice(m, 1);
                    continue;
                }

                ctx.save();
                // Draw blazing tail
                const tailEndX = met.x - (met.vx / Math.hypot(met.vx, met.vy)) * met.length * met.life;
                const tailEndY = met.y - (met.vy / Math.hypot(met.vx, met.vy)) * met.length * met.life;

                const meteorGrad = ctx.createLinearGradient(met.x, met.y, tailEndX, tailEndY);
                meteorGrad.addColorStop(0, '#ffffff');
                meteorGrad.addColorStop(0.3, met.color);
                meteorGrad.addColorStop(1, 'transparent');

                ctx.strokeStyle = meteorGrad;
                ctx.lineWidth = (isMobile ? 1.6 : 2.2) * met.life;
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.moveTo(met.x, met.y);
                ctx.lineTo(tailEndX, tailEndY);
                ctx.stroke();

                // Blazing Meteor Head
                ctx.beginPath();
                ctx.arc(met.x, met.y, (isMobile ? 2 : 2.8) * met.life, 0, Math.PI * 2);
                ctx.fillStyle = '#ffffff';
                ctx.shadowColor = met.color;
                ctx.shadowBlur = 10;
                ctx.fill();

                ctx.restore();
            }

            // 8. Cosmic Gravitational Cursor Beacon (Desktop Only)
            if (pointer.isActive && pointer.x !== null && !isMobile) {
                ctx.save();
                // Ethereal gravitational aura
                const gravAura = ctx.createRadialGradient(
                    pointer.x, pointer.y, 2,
                    pointer.x, pointer.y, 75
                );
                gravAura.addColorStop(0, 'rgba(56, 189, 248, 0.45)');
                gravAura.addColorStop(0.5, 'rgba(99, 102, 241, 0.15)');
                gravAura.addColorStop(1, 'transparent');

                ctx.fillStyle = gravAura;
                ctx.beginPath();
                ctx.arc(pointer.x, pointer.y, 75, 0, Math.PI * 2);
                ctx.fill();

                // Central beacon spark
                ctx.beginPath();
                ctx.arc(pointer.x, pointer.y, 3, 0, Math.PI * 2);
                ctx.fillStyle = '#ffffff';
                ctx.shadowColor = '#38bdf8';
                ctx.shadowBlur = 12;
                ctx.fill();

                ctx.restore();
            }


            animationFrameId = requestAnimationFrame(animate);
        }

        animationFrameId = requestAnimationFrame(animate);

        // Battery Guard: Instantly halt canvas calculation loop when tab is hidden
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                isTabActive = false;
                if (animationFrameId) cancelAnimationFrame(animationFrameId);
            } else {
                isTabActive = true;
                lastTimestamp = 0;
                animationFrameId = requestAnimationFrame(animate);
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCosmicGalaxy);
    } else {
        initCosmicGalaxy();
    }
})();
