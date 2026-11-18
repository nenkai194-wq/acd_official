/**
 * PT Aksara Cipta Digital (ACD Official)
 * "Cosmic Spiral Galaxy & Celestial Deep Space - Ultra Fidelity"
 * (Alam Semesta, Galaksi Spiral Kosmik 3D, Debu Bintang & Komet Interaktif)
 * 
 * Filosofi Visual:
 * - Merepresentasikan "Visi Tanpa Batas & Arsitektur Teknologi Berwibawa":
 *   Sebuah ekosistem digital enterprise yang luas, saling terhubung, berputar megah,
 *   dan berpusat pada inti kecerdasan digital yang jernih.
 * - Format: 4-Arm Grand Logarithmic Spiral Galaxy dengan ribuan bintang berkedip,
 *   awan nebula berpendar halus, hujan meteor/bintang jatuh berkala, serta medan gravitasi kursor.
 * 
 * Preservasi Keterbacaan Teks (Zero Noise / Pure Reading Contrast):
 * - Menggunakan "Intelligent Text Clearance Zone" (Focal Masking):
 *   Bintang dan partikel yang melintasi tepat di balik teks headline & sub-headline
 *   secara otomatis meredup halus (dimmed), sementara di area sekelilingnya
 *   (atas, samping, dan bawah) berpendar tajam, kaya, dan sangat jelas.
 * - Bebas dari kotak-kotak kaku / elemen diagram yang mengganggu.
 * - 60 FPS Native Canvas, hemat daya baterai (0% CPU saat tab browser tidak aktif).
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

        // Galaxy 3D Tilt Parameters (Majestic oblique angle)
        let galaxyTiltX = 0.98; // Oblique tilt around X-axis
        let galaxyAngle = 0;
        let baseRotationSpeed = 0.0016;

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

        // Collections
        let galaxyStars = [];
        let stardust = [];
        let backgroundStars = [];
        let meteors = [];
        let nextMeteorTime = 1.8;

        // Astronomical Color Palettes (Multi-spectrum starlight)
        const armColors = [
            { r: 240, g: 249, b: 255 }, // 0: Core Starlight (Diamond White)
            { r: 56,  g: 189, b: 248 }, // 1: Electric Cyan (Class B Hot Star)
            { r: 99,  g: 102, b: 241 }, // 2: Royal Indigo (Luminous Arm Star)
            { r: 129, g: 140, b: 248 }, // 3: Soft Periwinkle
            { r: 168, g: 85,  b: 247 }, // 4: Nebula Violet
            { r: 217, g: 70,  b: 239 }, // 5: Radiant Magenta Accent
            { r: 253, g: 224, b: 71  }  // 6: Golden Starlight Sparkle
        ];

        // Setup All Cosmic Entities
        function setupCosmos() {
            galaxyStars = [];
            stardust = [];
            backgroundStars = [];

            // 1. Galaxy Stars (4 Grand Spiral Arms)
            const starCount = isMobile ? 650 : 1600;
            const armCount = 4; // 4-arm grand design spiral
            const maxRadius = isMobile ? width * 0.65 : Math.max(width * 0.52, height * 0.62);

            for (let i = 0; i < starCount; i++) {
                // Non-linear radial distribution: dense galactic bulge tapering into spiral arms
                const distRatio = Math.pow(Math.random(), 1.55);
                const r = distRatio * maxRadius;

                // Arm angle: logarithmic spiral formula theta = b * ln(r) + armOffset
                const armIndex = i % armCount;
                const armOffset = (armIndex * Math.PI * 2) / armCount;
                const spiralAngle = r * 0.0075 + armOffset;

                // Angular scatter (wider at the tips, tighter near the core)
                const scatterAngle = (Math.random() - 0.5) * (0.35 + distRatio * 0.6);
                const scatterR = (Math.random() - 0.5) * (15 + distRatio * 45);

                const finalAngle = spiralAngle + scatterAngle;
                const finalR = Math.max(10, r + scatterR);

                // Disk thickness (Z-axis height distribution)
                const diskThickness = (1 - distRatio) * 45 + 10;
                const z = (Math.random() - 0.5) * diskThickness;

                // Color mapping: Core = Diamond White/Aqua, Mid = Indigo/Sky Blue, Outer = Violet/Magenta
                let colorIdx;
                if (distRatio < 0.12) {
                    colorIdx = Math.random() > 0.4 ? 0 : 1;
                } else if (distRatio < 0.35) {
                    colorIdx = Math.random() > 0.5 ? 1 : 2;
                } else if (distRatio < 0.65) {
                    colorIdx = Math.random() > 0.4 ? 2 : 3;
                } else if (distRatio < 0.85) {
                    colorIdx = Math.random() > 0.3 ? 4 : 5;
                } else {
                    colorIdx = Math.random() > 0.7 ? 6 : 4;
                }
                const baseColor = armColors[colorIdx];

                galaxyStars.push({
                    origR: finalR,
                    angle: finalAngle,
                    z: z,
                    // Keplerian orbital velocity decreases smoothly outward
                    orbitalSpeed: 0.0032 / (1 + distRatio * 1.6),
                    size: Math.random() * (isMobile ? 1.8 : 2.5) + 0.65,
                    baseAlpha: Math.random() * 0.65 + 0.35,
                    color: baseColor,
                    isCoreStar: distRatio < 0.15,
                    twinkleSpeed: Math.random() * 0.035 + 0.012,
                    twinklePhase: Math.random() * Math.PI * 2
                });
            }

            // 2. Fine Stardust Particles (Ethereal Cosmic Fog Specks)
            const dustCount = isMobile ? 180 : 450;
            for (let d = 0; d < dustCount; d++) {
                const distRatio = Math.pow(Math.random(), 1.4);
                const r = distRatio * maxRadius;
                const armIndex = d % armCount;
                const armOffset = (armIndex * Math.PI * 2) / armCount;
                const spiralAngle = r * 0.0075 + armOffset + (Math.random() - 0.5) * 0.8;

                stardust.push({
                    origR: Math.max(12, r + (Math.random() - 0.5) * 40),
                    angle: spiralAngle,
                    z: (Math.random() - 0.5) * 30,
                    orbitalSpeed: 0.0028 / (1 + distRatio * 1.5),
                    size: Math.random() * 1.2 + 0.4,
                    alpha: Math.random() * 0.45 + 0.15,
                    color: Math.random() > 0.5 ? '56, 189, 248' : '168, 85, 247'
                });
            }

            // 3. Background Deep Space Stars (Layered multi-plane starfield)
            const bgCount = isMobile ? 120 : 280;
            for (let j = 0; j < bgCount; j++) {
                const isBeacon = Math.random() > 0.92;
                backgroundStars.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    size: isBeacon ? (Math.random() * 1.8 + 1.2) : (Math.random() * 1.2 + 0.4),
                    alpha: Math.random() * 0.65 + 0.25,
                    speed: Math.random() * 0.018 + 0.008,
                    phase: Math.random() * Math.PI * 2,
                    color: isBeacon ? '255, 255, 255' : (Math.random() > 0.45 ? '56, 189, 248' : '129, 140, 248'),
                    hasSpikes: isBeacon && !isMobile
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

            // Frame the galactic nucleus elegantly behind the hero header
            galaxyCenterX = width * 0.5;
            galaxyCenterY = height * (isMobile ? 0.42 : 0.40);

            setupCosmos();
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
                maxR: isMobile ? 220 : 380,
                alpha: 1.0,
                color: '#38bdf8'
            });

            // Trigger an immediate shooting star
            spawnMeteor(e.clientX, e.clientY);
        }, { passive: true });

        // Spawn Shooting Star / Meteor
        function spawnMeteor(targetX, targetY) {
            // Directional variation: diagonal trajectory across the sky
            const startX = Math.random() * width * 0.85;
            const startY = Math.random() * height * 0.40;
            const angle = Math.PI * 0.22 + (Math.random() - 0.5) * 0.25;
            const speed = (isMobile ? 8 : 13) + Math.random() * 6;

            const meteorPalette = ['#ffffff', '#38bdf8', '#818cf8', '#c084fc'];
            const chosenColor = meteorPalette[Math.floor(Math.random() * meteorPalette.length)];

            meteors.push({
                x: startX,
                y: startY,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                length: (isMobile ? 70 : 120) + Math.random() * 50,
                life: 1.0,
                decay: 0.016 + Math.random() * 0.014,
                color: chosenColor
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
                pointer.gravForce = Math.min(1.0, pointer.gravForce + delta * 2.2);
            } else {
                pointer.gravForce = Math.max(0, pointer.gravForce - delta * 1.5);
            }

            // 2. Cosmic Supernova Ripples (Shockwave expansion)
            for (let rip = pointer.ripples.length - 1; rip >= 0; rip--) {
                const rp = pointer.ripples[rip];
                rp.r += delta * (isMobile ? 260 : 420);
                rp.alpha -= delta * 1.1;

                if (rp.alpha <= 0 || rp.r >= rp.maxR) {
                    pointer.ripples.splice(rip, 1);
                    continue;
                }

                ctx.save();
                ctx.beginPath();
                ctx.arc(rp.x, rp.y, rp.r, 0, Math.PI * 2);
                ctx.strokeStyle = `rgba(56, 189, 248, ${rp.alpha * 0.75})`;
                ctx.lineWidth = 1.8;
                ctx.stroke();
                ctx.restore();
            }

            // 3. Render Deep Space Background Starfield
            backgroundStars.forEach(st => {
                const twinkle = Math.sin(time * 2.4 + st.phase);
                const currentAlpha = Math.max(0.12, st.alpha + twinkle * 0.3);

                ctx.save();
                ctx.beginPath();
                ctx.arc(st.x, st.y, st.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${st.color}, ${currentAlpha})`;
                ctx.fill();

                // 4-Point Diffraction Spikes on bright stellar beacons
                if (st.hasSpikes && currentAlpha > 0.45) {
                    ctx.strokeStyle = `rgba(${st.color}, ${currentAlpha * 0.75})`;
                    ctx.lineWidth = 0.9;
                    const spikeLen = 10 + twinkle * 4;
                    ctx.beginPath();
                    ctx.moveTo(st.x - spikeLen, st.y);
                    ctx.lineTo(st.x + spikeLen, st.y);
                    ctx.moveTo(st.x, st.y - spikeLen);
                    ctx.lineTo(st.x, st.y + spikeLen);
                    ctx.stroke();
                }
                ctx.restore();
            });

            // 4. Render Deep Galactic Core Nebula Glow (Vivid Multi-Spectrum Cosmic Aura)
            ctx.save();
            const coreRadius = isMobile ? 220 : 380;
            const coreGlow = ctx.createRadialGradient(
                galaxyCenterX, galaxyCenterY, 12,
                galaxyCenterX, galaxyCenterY, coreRadius
            );
            coreGlow.addColorStop(0, 'rgba(56, 189, 248, 0.28)');
            coreGlow.addColorStop(0.25, 'rgba(99, 102, 241, 0.18)');
            coreGlow.addColorStop(0.60, 'rgba(168, 85, 247, 0.08)');
            coreGlow.addColorStop(0.85, 'rgba(217, 70, 239, 0.03)');
            coreGlow.addColorStop(1, 'transparent');

            ctx.fillStyle = coreGlow;
            ctx.beginPath();
            ctx.arc(galaxyCenterX, galaxyCenterY, coreRadius, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();

            // 5. Update & Render Stardust Particles (Fine Luminescent Cosmic Fog)
            const cosTilt = Math.cos(galaxyTiltX);
            const sinTilt = Math.sin(galaxyTiltX);

            stardust.forEach(dust => {
                dust.angle += dust.orbitalSpeed;
                const xL = Math.cos(dust.angle) * dust.origR;
                const yL = Math.sin(dust.angle) * dust.origR;
                const fX = galaxyCenterX + xL;
                const fY = galaxyCenterY + (yL * cosTilt - dust.z * sinTilt);

                // Intelligent Text Focal Masking (Dim softly when behind text banner)
                const dxText = fX - galaxyCenterX;
                const dyText = (fY - galaxyCenterY) * 2.3;
                const textDist = Math.hypot(dxText, dyText);
                const clearR = isMobile ? 220 : 420;
                let textFactor = 1.0;
                if (textDist < clearR) {
                    textFactor = 0.2 + 0.8 * Math.pow(textDist / clearR, 1.8);
                }

                ctx.beginPath();
                ctx.arc(fX, fY, dust.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${dust.color}, ${dust.alpha * textFactor})`;
                ctx.fill();
            });

            // 6. Update & Render Spiral Galaxy Stars (3D Projected Disk with Crisp Brilliance)
            galaxyAngle += baseRotationSpeed;

            galaxyStars.forEach(star => {
                // Orbit rotation
                star.angle += star.orbitalSpeed;

                // 2D Disk Coordinates
                let xLocal = Math.cos(star.angle) * star.origR;
                let yLocal = Math.sin(star.angle) * star.origR;

                // Interactive Pointer Gravitational Inflow
                if (pointer.isActive && pointer.x !== null && pointer.gravForce > 0) {
                    const screenXEst = galaxyCenterX + xLocal;
                    const screenYEst = galaxyCenterY + yLocal * cosTilt;
                    const dx = pointer.x - screenXEst;
                    const dy = pointer.y - screenYEst;
                    const distToPtr = Math.hypot(dx, dy);

                    if (distToPtr < 260) {
                        const pullFactor = (1 - distToPtr / 260) * 22 * pointer.gravForce;
                        xLocal += (dx / distToPtr) * pullFactor;
                        yLocal += (dy / distToPtr) * pullFactor;
                    }
                }

                const finalX = galaxyCenterX + xLocal;
                const finalY = galaxyCenterY + (yLocal * cosTilt - star.z * sinTilt);
                const depthZ = yLocal * sinTilt + star.z * cosTilt;

                // Perspective depth scale & twinkle
                const twinkle = Math.sin(time * 3.2 + star.twinklePhase);
                const depthScale = Math.max(0.65, 1 + (depthZ / 420) * 0.45);

                // Intelligent Text Focal Masking:
                // Partikel di luar area teks tetap cerah & tajam; partikel tepat di balik tulisan meredup halus
                const dxText = finalX - galaxyCenterX;
                const dyText = (finalY - galaxyCenterY) * 2.3;
                const textDist = Math.hypot(dxText, dyText);
                const clearR = isMobile ? 220 : 420;
                let textFactor = 1.0;
                if (textDist < clearR) {
                    textFactor = 0.25 + 0.75 * Math.pow(textDist / clearR, 1.8);
                }

                const finalAlpha = Math.max(0.12, (star.baseAlpha + twinkle * 0.28) * Math.min(1.25, depthScale) * textFactor);

                ctx.beginPath();
                ctx.arc(finalX, finalY, Math.max(0.6, star.size * depthScale), 0, Math.PI * 2);

                if (star.isCoreStar) {
                    ctx.fillStyle = `rgba(240, 249, 255, ${finalAlpha * 1.35})`;
                } else {
                    ctx.fillStyle = `rgba(${star.color.r}, ${star.color.g}, ${star.color.b}, ${finalAlpha})`;
                }
                ctx.fill();
            });

            // 7. Galactic Supermassive Nucleus (Inti Pusat Galaksi)
            ctx.save();
            ctx.beginPath();
            ctx.arc(galaxyCenterX, galaxyCenterY, isMobile ? 4.5 : 6.5, 0, Math.PI * 2);
            ctx.fillStyle = '#ffffff';
            ctx.shadowColor = '#38bdf8';
            ctx.shadowBlur = isMobile ? 16 : 26;
            ctx.fill();
            ctx.restore();

            // 8. Update & Render Shooting Stars / Meteors (Komet Meluncur Berkala)
            nextMeteorTime -= delta;
            if (nextMeteorTime <= 0) {
                spawnMeteor();
                // Spawn next meteor in 1.4 to 3.2 seconds
                nextMeteorTime = (isMobile ? 2.5 : 1.4) + Math.random() * 2.0;
            }

            for (let m = meteors.length - 1; m >= 0; m--) {
                const met = meteors[m];
                met.x += met.vx;
                met.y += met.vy;
                met.life -= met.decay;

                if (met.life <= 0 || met.x > width + 120 || met.y > height + 120) {
                    meteors.splice(m, 1);
                    continue;
                }

                ctx.save();
                const tailLen = met.length * met.life;
                const vMag = Math.hypot(met.vx, met.vy);
                const tailEndX = met.x - (met.vx / vMag) * tailLen;
                const tailEndY = met.y - (met.vy / vMag) * tailLen;

                const meteorGrad = ctx.createLinearGradient(met.x, met.y, tailEndX, tailEndY);
                meteorGrad.addColorStop(0, '#ffffff');
                meteorGrad.addColorStop(0.25, met.color);
                meteorGrad.addColorStop(1, 'transparent');

                ctx.strokeStyle = meteorGrad;
                ctx.lineWidth = (isMobile ? 2.0 : 2.8) * met.life;
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.moveTo(met.x, met.y);
                ctx.lineTo(tailEndX, tailEndY);
                ctx.stroke();

                // Blazing Meteor Head
                ctx.beginPath();
                ctx.arc(met.x, met.y, (isMobile ? 2.5 : 3.5) * met.life, 0, Math.PI * 2);
                ctx.fillStyle = '#ffffff';
                ctx.shadowColor = met.color;
                ctx.shadowBlur = 14;
                ctx.fill();

                ctx.restore();
            }

            // 9. Cosmic Gravitational Cursor Beacon (Desktop Only)
            if (pointer.isActive && pointer.x !== null && !isMobile) {
                ctx.save();
                const gravAura = ctx.createRadialGradient(
                    pointer.x, pointer.y, 2,
                    pointer.x, pointer.y, 90
                );
                gravAura.addColorStop(0, 'rgba(56, 189, 248, 0.45)');
                gravAura.addColorStop(0.5, 'rgba(99, 102, 241, 0.16)');
                gravAura.addColorStop(1, 'transparent');

                ctx.fillStyle = gravAura;
                ctx.beginPath();
                ctx.arc(pointer.x, pointer.y, 90, 0, Math.PI * 2);
                ctx.fill();

                // Central beacon spark
                ctx.beginPath();
                ctx.arc(pointer.x, pointer.y, 3.5, 0, Math.PI * 2);
                ctx.fillStyle = '#ffffff';
                ctx.shadowColor = '#38bdf8';
                ctx.shadowBlur = 14;
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
