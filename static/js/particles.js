/**
 * PT Aksara Cipta Digital (ACD Official)
 * "Prismatic Light Beams / Cyber Laser Aurora"
 * (Berkas Serat Optik & Pita Cahaya Mengalir)
 * 
 * Filosofi Visual:
 * - Merepresentasikan "Transmisi Data Berkecepatan Cahaya" (Light-Speed Data Highway):
 *   kelancaran integrasi sistem, transformasi digital tanpa hambatan, dan konektivitas tak terbatas.
 * - Pita gelombang laser optik multi-lapisan (Fiber Optic Aurora Ribbons) dengan dispersi
 *   warna prismatik (Electric Cyan, Sky Blue, Royal Indigo, dan Velvet Violet).
 * - Berkas foton data meluncur kencang di sepanjang kurva serat optik.
 * - Sangat anggun, halus, futuristik, berkelas premium korporat, dan menenangkan di mata.
 * 
 * Fitur:
 * - Multi-layered Harmonic Bezier Laser Ribbons dengan dispersi spektral prismatik
 * - Traveling Photon Data Sparks dengan ekor komet bercahaya
 * - Interaktivitas Defleksi Fluida Elastis (Kursor mouse & sentuhan touch meliukkan pita cahaya)
 * - Gelombang denyut klik (Shockwave Optical Ping)
 * - Perlindungan kontras 100% jernih untuk teks headline
 * - 0 MB Video Overhead, 60 FPS Native Canvas, hemat daya baterai
 */

(function() {
    'use strict';

    function initLaserAurora() {
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

        // Pointer state & fluid physics
        const pointer = {
            x: null,
            y: null,
            targetX: null,
            targetY: null,
            vx: 0,
            vy: 0,
            radius: 220,
            strength: 0,
            isActive: false,
            shockwaves: []
        };

        // Fiber optic ribbons configuration
        let ribbons = [];
        const RIBBON_COUNT = isMobile ? 6 : 9;

        // Photon data pulses traveling along ribbons
        let photons = [];
        const PHOTON_COUNT = isMobile ? 12 : 24;

        // Optical background glints
        let glints = [];
        const GLINT_COUNT = isMobile ? 25 : 55;

        // Palette presets (Prismatic Spectrum)
        const beamGradients = [
            { primary: 'rgba(6, 182, 212, ',  glow: '#06b6d4', core: '#38bdf8' }, // Electric Cyan
            { primary: 'rgba(56, 189, 248, ', glow: '#38bdf8', core: '#ffffff' }, // Sky Blue
            { primary: 'rgba(99, 102, 241, ', glow: '#6366f1', core: '#a5b4fc' }, // Royal Indigo
            { primary: 'rgba(139, 92, 246, ', glow: '#8b5cf6', core: '#c4b5fd' }, // Violet
            { primary: 'rgba(168, 85, 247, ', glow: '#a855f7', core: '#e9d5ff' }, // Purple
            { primary: 'rgba(236, 72, 153, ', glow: '#ec4899', core: '#fbcfe8' }  // Pink prism edge
        ];

        function setupRibbons() {
            ribbons = [];
            const count = isMobile ? 6 : 9;

            for (let i = 0; i < count; i++) {
                const colorDef = beamGradients[i % beamGradients.length];
                // Base Y distribution: sweep gracefully from mid-bottom to diagonal crest
                const yRatio = isMobile 
                    ? 0.35 + (i / count) * 0.45 
                    : 0.30 + (i / count) * 0.48;

                ribbons.push({
                    baseY: height * yRatio,
                    amplitude1: (isMobile ? 35 : 65) + Math.sin(i * 1.3) * 20,
                    amplitude2: (isMobile ? 20 : 40) + Math.cos(i * 0.9) * 15,
                    freq1: 0.0018 + (i * 0.0003),
                    freq2: 0.0035 + (i * 0.0005),
                    speed1: 0.75 + (i * 0.12),
                    speed2: -0.55 - (i * 0.10),
                    phaseOffset: i * 0.75,
                    lineWidth: (isMobile ? 1.2 : 1.8) + (i % 2 === 0 ? 0.6 : 0),
                    alpha: isMobile ? 0.35 : 0.45,
                    colorDef: colorDef,
                    hasCurtain: i % 2 === 1 // Aurora translucent curtain fill
                });
            }

            // Setup photons
            photons = [];
            const pCount = isMobile ? 12 : 24;
            for (let j = 0; j < pCount; j++) {
                photons.push({
                    ribbonIndex: j % ribbons.length,
                    progress: Math.random(),
                    speed: (isMobile ? 0.0025 : 0.0035) + Math.random() * 0.002,
                    tailLength: isMobile ? 18 : 32,
                    size: isMobile ? 2.2 : 3.2,
                    color: beamGradients[j % beamGradients.length]
                });
            }

            // Setup optical glints
            glints = [];
            const gCount = isMobile ? 25 : 55;
            for (let k = 0; k < gCount; k++) {
                glints.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    size: Math.random() * 1.8 + 0.6,
                    phase: Math.random() * Math.PI * 2,
                    speed: Math.random() * 0.02 + 0.01,
                    color: Math.random() > 0.4 ? '6, 182, 212' : '99, 102, 241'
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

            pointer.radius = isMobile ? 140 : 230;

            setupRibbons();
        }

        window.addEventListener('resize', resize, { passive: true });

        // Pointer interactions
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

        // Touch interactions
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

        // Optical Ping shockwave on click/tap
        window.addEventListener('click', (e) => {
            pointer.shockwaves.push({
                x: e.clientX,
                y: e.clientY,
                r: 10,
                maxR: isMobile ? 180 : 320,
                alpha: 0.85
            });
        }, { passive: true });

        // Calculate Y on a ribbon curve at given X coordinate
        function getRibbonY(ribbon, x, t) {
            // Harmonic multi-frequency wave calculation
            const wave1 = Math.sin(x * ribbon.freq1 + t * ribbon.speed1 + ribbon.phaseOffset) * ribbon.amplitude1;
            const wave2 = Math.cos(x * ribbon.freq2 + t * ribbon.speed2 + ribbon.phaseOffset * 1.5) * ribbon.amplitude2;
            let currentY = ribbon.baseY + wave1 + wave2;

            // Interactive pointer elastic fluid deflection
            if (pointer.isActive && pointer.x !== null) {
                const dx = x - pointer.x;
                const dy = currentY - pointer.y;
                const dist = Math.hypot(dx, dy);

                if (dist < pointer.radius) {
                    const factor = (1 - dist / pointer.radius);
                    // Smooth gaussian bell deflection
                    const deflection = Math.sin(factor * Math.PI) * (isMobile ? 35 : 65);
                    currentY += (dy > 0 ? deflection : -deflection) * 0.7;
                }
            }

            // Shockwave perturbation
            for (let s = 0; s < pointer.shockwaves.length; s++) {
                const sw = pointer.shockwaves[s];
                const distToShock = Math.hypot(x - sw.x, currentY - sw.y);
                const diff = Math.abs(distToShock - sw.r);
                if (diff < 35) {
                    const waveFactor = (1 - diff / 35) * sw.alpha;
                    currentY += Math.sin(diff * 0.2) * 20 * waveFactor;
                }
            }

            return currentY;
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

            // 1. Smooth Pointer Lerp
            if (pointer.isActive && pointer.targetX !== null) {
                pointer.vx = (pointer.targetX - pointer.x) * 0.12;
                pointer.vy = (pointer.targetY - pointer.y) * 0.12;
                pointer.x += pointer.vx;
                pointer.y += pointer.vy;
            }

            // 2. Update Shockwaves
            for (let s = pointer.shockwaves.length - 1; s >= 0; s--) {
                const sw = pointer.shockwaves[s];
                sw.r += delta * (isMobile ? 220 : 380);
                sw.alpha -= delta * 1.4;

                if (sw.alpha <= 0 || sw.r >= sw.maxR) {
                    pointer.shockwaves.splice(s, 1);
                    continue;
                }

                ctx.save();
                ctx.beginPath();
                ctx.arc(sw.x, sw.y, sw.r, 0, Math.PI * 2);
                ctx.strokeStyle = `rgba(6, 182, 212, ${sw.alpha * 0.6})`;
                ctx.lineWidth = 1.5;
                ctx.stroke();
                ctx.restore();
            }

            // 3. Render Optical Background Glints
            glints.forEach(g => {
                const pulse = Math.sin(time * 3 + g.phase);
                const alpha = Math.max(0.1, 0.45 + pulse * 0.35);

                ctx.beginPath();
                ctx.arc(g.x, g.y, g.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${g.color}, ${alpha})`;
                ctx.fill();
            });

            // 4. Render Aurora Light Beams & Fiber Optic Ribbons
            const stepX = isMobile ? 18 : 14;

            ribbons.forEach((ribbon, rIdx) => {
                const points = [];
                for (let x = -20; x <= width + 20; x += stepX) {
                    points.push({ x, y: getRibbonY(ribbon, x, time) });
                }

                // Render Aurora Translucent Curtain Fill below ribbon (for atmospheric depth)
                if (ribbon.hasCurtain) {
                    ctx.save();
                    ctx.beginPath();
                    ctx.moveTo(points[0].x, points[0].y);
                    for (let p = 1; p < points.length; p++) {
                        ctx.lineTo(points[p].x, points[p].y);
                    }
                    // Extend down
                    ctx.lineTo(width + 20, height);
                    ctx.lineTo(-20, height);
                    ctx.closePath();

                    const curtainGrad = ctx.createLinearGradient(0, ribbon.baseY - 50, 0, height);
                    curtainGrad.addColorStop(0, ribbon.colorDef.primary + (isMobile ? '0.04)' : '0.07)'));
                    curtainGrad.addColorStop(0.5, ribbon.colorDef.primary + (isMobile ? '0.015)' : '0.025)'));
                    curtainGrad.addColorStop(1, 'transparent');

                    ctx.fillStyle = curtainGrad;
                    ctx.fill();
                    ctx.restore();
                }

                // Render Main Fiber Optic Laser Strand
                ctx.save();
                ctx.beginPath();
                ctx.moveTo(points[0].x, points[0].y);
                for (let p = 1; p < points.length - 1; p++) {
                    const xc = (points[p].x + points[p + 1].x) * 0.5;
                    const yc = (points[p].y + points[p + 1].y) * 0.5;
                    ctx.quadraticCurveTo(points[p].x, points[p].y, xc, yc);
                }
                ctx.lineTo(points[points.length - 1].x, points[points.length - 1].y);

                // Prismatic Horizontal Gradient along wave
                const waveGrad = ctx.createLinearGradient(0, 0, width, 0);
                waveGrad.addColorStop(0, 'rgba(6, 182, 212, 0.15)');
                waveGrad.addColorStop(0.25, ribbon.colorDef.primary + ribbon.alpha + ')');
                waveGrad.addColorStop(0.65, ribbon.colorDef.primary + (ribbon.alpha * 1.1) + ')');
                waveGrad.addColorStop(0.9, 'rgba(168, 85, 247, ' + ribbon.alpha + ')');
                waveGrad.addColorStop(1, 'rgba(236, 72, 153, 0.2)');

                ctx.strokeStyle = waveGrad;
                ctx.lineWidth = ribbon.lineWidth;
                ctx.shadowColor = ribbon.colorDef.glow;
                ctx.shadowBlur = isMobile ? 6 : 12;
                ctx.stroke();

                ctx.restore();
            });

            // 5. Update & Render Traveling Photon Data Sparks (Berkas Foton Cepat)
            photons.forEach(pt => {
                pt.progress += pt.speed;
                if (pt.progress > 1.0) {
                    pt.progress = 0;
                    pt.ribbonIndex = Math.floor(Math.random() * ribbons.length);
                }

                const ribbon = ribbons[pt.ribbonIndex];
                const currentX = pt.progress * (width + 40) - 20;
                const currentY = getRibbonY(ribbon, currentX, time);

                ctx.save();
                // Draw comet glowing tail
                const tailSteps = 6;
                for (let s = 1; s <= tailSteps; s++) {
                    const tailX = currentX - (pt.tailLength * (s / tailSteps));
                    const tailY = getRibbonY(ribbon, tailX, time);
                    const tailAlpha = (1 - s / tailSteps) * 0.55;

                    ctx.beginPath();
                    ctx.arc(tailX, tailY, pt.size * (1 - s / tailSteps * 0.4), 0, Math.PI * 2);
                    ctx.fillStyle = pt.color.primary + tailAlpha + ')';
                    ctx.fill();
                }

                // Bright glowing photon head
                ctx.beginPath();
                ctx.arc(currentX, currentY, pt.size, 0, Math.PI * 2);
                ctx.fillStyle = pt.color.core;
                ctx.shadowColor = pt.color.glow;
                ctx.shadowBlur = isMobile ? 8 : 14;
                ctx.fill();

                ctx.restore();
            });

            // 6. Interactive Pointer Laser Aura & Fluid Wake
            if (pointer.isActive && pointer.x !== null) {
                ctx.save();
                // Pointer ambient halo
                const ptrGlow = ctx.createRadialGradient(
                    pointer.x, pointer.y, 4,
                    pointer.x, pointer.y, isMobile ? 55 : 85
                );
                ptrGlow.addColorStop(0, 'rgba(56, 189, 248, 0.45)');
                ptrGlow.addColorStop(0.4, 'rgba(99, 102, 241, 0.2)');
                ptrGlow.addColorStop(1, 'transparent');

                ctx.fillStyle = ptrGlow;
                ctx.beginPath();
                ctx.arc(pointer.x, pointer.y, isMobile ? 55 : 85, 0, Math.PI * 2);
                ctx.fill();

                // Center laser probe bead
                ctx.beginPath();
                ctx.arc(pointer.x, pointer.y, 3.5, 0, Math.PI * 2);
                ctx.fillStyle = '#ffffff';
                ctx.shadowColor = '#38bdf8';
                ctx.shadowBlur = 12;
                ctx.fill();

                ctx.restore();
            }

            // 7. Corner Optical Telemetry HUD (Desktop Only)
            if (!isMobile) {
                ctx.save();
                ctx.font = '9px "JetBrains Mono", "Fira Code", monospace';
                ctx.fillStyle = 'rgba(148, 163, 184, 0.45)';
                ctx.strokeStyle = 'rgba(99, 102, 241, 0.35)';
                ctx.lineWidth = 1;

                const margin = 32;

                // Top-Left Legend
                ctx.fillText('ACD // OPTICAL_FIBER_MESH v4.0', margin, margin);
                ctx.fillText('SPECTRUM: PRISMATIC_AURORA [480nm - 620nm]', margin, margin + 14);

                // Top-Right Legend
                ctx.textAlign = 'right';
                ctx.fillText('THROUGHPUT: 100 Gbps // LOW_JITTER', width - margin, margin);
                ctx.fillText('DATA_HIGHWAY: REALTIME_60FPS', width - margin, margin + 14);

                // Bottom-Left
                ctx.textAlign = 'left';
                ctx.fillText('INTEGRATION: FLUID_ELASTIC_AURORA', margin, height - margin);

                // Bottom-Right
                ctx.textAlign = 'right';
                ctx.fillText('STATUS: OPTICAL_CARRIER_LOCKED', width - margin, height - margin);

                ctx.restore();
            }

            animationFrameId = requestAnimationFrame(animate);
        }

        animationFrameId = requestAnimationFrame(animate);

        // Battery Guard: Instantly halt rendering loop when tab is hidden
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
        document.addEventListener('DOMContentLoaded', initLaserAurora);
    } else {
        initLaserAurora();
    }
})();
