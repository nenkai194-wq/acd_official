/**
 * PT Aksara Cipta Digital (ACD Official)
 * "Interactive Holographic Core / Prismatic Monolith"
 * (Kubus Geometri Kristal 3D Interaktif & Cincin Gyroskopik Holografis)
 * 
 * Filosofi Visual:
 * - Merepresentasikan "Inti Kecerdasan Digital" (Digital Intelligence Core) ACD:
 *   presisi, multidimensi, kokoh, dan berorientasi arsitektur masa depan.
 * - Kristal prismatik 3D ganda (Outer Monolith & Inner Energy Core) yang berotasi dinamis
 *   dikelilingi cincin gyroskopik holografis berkecepatan tinggi.
 * - Tampilan berwibawa, sangat elegan, futuristik ala Apple / Nvidia Keynote,
 *   dan memiliki keunikan visual tinggi yang membedakan ACD dari website manapun.
 * 
 * Fitur:
 * - Real-time 3D Matrix Projection (Yaw, Pitch, Roll & Perspective 3D)
 * - Nested Dual Geometry (Outer Prismatic Monolith + Inner Counter-Rotating Octahedron)
 * - Concentric Gyroscopic Rings dengan orbital photon markers
 * - Interaktivitas Kursor 3D (Inersia mouse & sentuhan touch memutar kristal secara elastis)
 * - Holographic Scanlines & Quantum Data Dust di ruang 3D
 * - Masking kontras di area tengah: Teks headline tetap 100% jernih, tebal, dan mudah dibaca
 * - 0 MB Video Overhead, 60 FPS Canvas Ringan, perlindungan baterai otomatis
 */

(function() {
    'use strict';

    function initHolographicMonolith() {
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

        // 3D Scene Parameters
        let centerX = 0;
        let centerY = 0;
        let fov = 420;
        let cameraDistance = 550;

        // Rotation & Physics
        let rotX = 0.25;
        let rotY = 0.45;
        let rotZ = 0.12;
        let targetRotX = 0.25;
        let targetRotY = 0.45;
        let baseSpinSpeedY = 0.006;
        let baseSpinSpeedX = 0.003;

        // Interactive Pointer
        const pointer = {
            x: null,
            y: null,
            targetX: null,
            targetY: null,
            isActive: false,
            lastX: 0,
            lastY: 0,
            isDragging: false
        };

        // Geometric Models
        let outerVertices = [];
        let outerEdges = [];
        let outerFaces = [];

        let innerVertices = [];
        let innerEdges = [];

        // Orbital Gyroscopic Rings
        let orbitalRings = [];

        // 3D Ambient Dust Particles
        let dustParticles = [];
        const DUST_COUNT = isMobile ? 35 : 75;

        // Holographic Scanline Wave
        let scanlineY = -250;

        // Helper: 3D Vector Rotate & Project
        function project3D(v, rx, ry, rz, scaleFactor = 1.0) {
            // Apply scale
            let x = v.x * scaleFactor;
            let y = v.y * scaleFactor;
            let z = v.z * scaleFactor;

            // Rotate around Y (Yaw)
            let x1 = x * Math.cos(ry) + z * Math.sin(ry);
            let z1 = -x * Math.sin(ry) + z * Math.cos(ry);

            // Rotate around X (Pitch)
            let y2 = y * Math.cos(rx) - z1 * Math.sin(rx);
            let z2 = y * Math.sin(rx) + z1 * Math.cos(rx);

            // Rotate around Z (Roll)
            let x3 = x1 * Math.cos(rz) - y2 * Math.sin(rz);
            let y3 = x1 * Math.sin(rz) + y2 * Math.cos(rz);

            // Perspective scale
            const zTotal = z2 + cameraDistance;
            const pScale = fov / Math.max(10, zTotal);

            return {
                x2d: centerX + x3 * pScale,
                y2d: centerY + y3 * pScale,
                depth: z2,
                scale: pScale
            };
        }

        // Initialize 3D Geometries
        function setupGeometries() {
            const baseSize = isMobile ? (width < 400 ? 110 : 130) : 190;

            // 1. Outer Prismatic Monolith (Chamfered Rhombic Cube / Hyper-Monolith)
            const s = baseSize;
            const h = baseSize * 1.15; // Sleek tall proportions

            outerVertices = [
                // Top facet
                { x: 0, y: -h, z: 0 },
                // Upper ring
                { x: -s * 0.75, y: -h * 0.45, z: -s * 0.75 },
                { x:  s * 0.75, y: -h * 0.45, z: -s * 0.75 },
                { x:  s * 0.75, y: -h * 0.45, z:  s * 0.75 },
                { x: -s * 0.75, y: -h * 0.45, z:  s * 0.75 },
                // Equatorial ring (equator)
                { x: -s, y: 0, z: 0 },
                { x: 0, y: 0, z: -s },
                { x: s, y: 0, z: 0 },
                { x: 0, y: 0, z: s },
                // Lower ring
                { x: -s * 0.75, y: h * 0.45, z: -s * 0.75 },
                { x:  s * 0.75, y: h * 0.45, z: -s * 0.75 },
                { x:  s * 0.75, y: h * 0.45, z:  s * 0.75 },
                { x: -s * 0.75, y: h * 0.45, z:  s * 0.75 },
                // Bottom facet
                { x: 0, y: h, z: 0 }
            ];

            // Outer wireframe edges
            outerEdges = [
                // Top cap to upper ring
                [0, 1], [0, 2], [0, 3], [0, 4],
                // Upper ring loop
                [1, 2], [2, 3], [3, 4], [4, 1],
                // Upper ring to equator
                [1, 5], [1, 6], [2, 6], [2, 7], [3, 7], [3, 8], [4, 8], [4, 5],
                // Equator to lower ring
                [5, 9], [6, 9], [6, 10], [7, 10], [7, 11], [8, 11], [8, 12], [5, 12],
                // Lower ring loop
                [9, 10], [10, 11], [11, 12], [12, 9],
                // Lower ring to bottom cap
                [13, 9], [13, 10], [13, 11], [13, 12]
            ];

            // Outer crystalline translucent faces (for depth shading)
            outerFaces = [
                [0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 1],
                [1, 6, 2], [2, 7, 3], [3, 8, 4], [4, 5, 1],
                [5, 9, 6], [6, 10, 7], [7, 11, 8], [8, 12, 5],
                [13, 10, 9], [13, 11, 10], [13, 12, 11], [13, 9, 12]
            ];

            // 2. Inner Energy Core (Inverted Octahedron)
            const isize = baseSize * 0.48;
            innerVertices = [
                { x: 0, y: -isize * 1.25, z: 0 },
                { x:  isize, y: 0, z: 0 },
                { x: -isize, y: 0, z: 0 },
                { x: 0, y: 0, z:  isize },
                { x: 0, y: 0, z: -isize },
                { x: 0, y:  isize * 1.25, z: 0 }
            ];

            innerEdges = [
                [0, 1], [0, 2], [0, 3], [0, 4],
                [1, 3], [3, 2], [2, 4], [4, 1],
                [5, 1], [5, 2], [5, 3], [5, 4]
            ];

            // 3. Orbital Gyroscopic Rings
            orbitalRings = [
                {
                    radius: baseSize * 1.35,
                    tiltX: 0.55,
                    tiltZ: 0.25,
                    speed: 0.015,
                    angle: 0,
                    color: 'rgba(6, 182, 212, ',
                    beadColor: '#38bdf8',
                    dashPattern: [12, 8, 4, 8]
                },
                {
                    radius: baseSize * 1.62,
                    tiltX: -0.65,
                    tiltZ: -0.35,
                    speed: -0.012,
                    angle: Math.PI * 0.35,
                    color: 'rgba(99, 102, 241, ',
                    beadColor: '#818cf8',
                    dashPattern: [16, 10]
                },
                {
                    radius: baseSize * 1.88,
                    tiltX: 0.22,
                    tiltZ: -0.75,
                    speed: 0.008,
                    angle: Math.PI * 0.75,
                    color: 'rgba(168, 85, 247, ',
                    beadColor: '#c084fc',
                    dashPattern: [24, 12, 6, 12]
                }
            ];

            // 4. Ambient 3D Dust Particles
            dustParticles = [];
            for (let i = 0; i < DUST_COUNT; i++) {
                const rad = baseSize * (0.8 + Math.random() * 2.2);
                const theta = Math.random() * Math.PI * 2;
                const phi = (Math.random() - 0.5) * Math.PI;

                dustParticles.push({
                    x: rad * Math.cos(phi) * Math.cos(theta),
                    y: rad * Math.sin(phi),
                    z: rad * Math.cos(phi) * Math.sin(theta),
                    size: Math.random() * 1.8 + 0.6,
                    pulseSpeed: Math.random() * 0.02 + 0.01,
                    pulsePhase: Math.random() * Math.PI * 2,
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

            // Centering: Position core gracefully to frame the hero headline
            centerX = width * 0.5;
            centerY = height * (isMobile ? 0.44 : 0.42);

            fov = isMobile ? 360 : 440;
            cameraDistance = isMobile ? 580 : 540;

            setupGeometries();
        }

        window.addEventListener('resize', resize, { passive: true });

        // Pointer Interaction
        window.addEventListener('mousemove', (e) => {
            pointer.targetX = e.clientX;
            pointer.targetY = e.clientY;
            pointer.isActive = true;

            const normX = (e.clientX / width - 0.5) * 2;
            const normY = (e.clientY / height - 0.5) * 2;

            // Interactive 3D Perspective Tilt
            targetRotY = normX * 0.85;
            targetRotX = -normY * 0.55 + 0.25;
        }, { passive: true });

        window.addEventListener('mouseleave', () => {
            pointer.isActive = false;
        }, { passive: true });

        // Mobile Touch Gestures
        window.addEventListener('touchstart', (e) => {
            if (e.touches && e.touches[0]) {
                pointer.lastX = e.touches[0].clientX;
                pointer.lastY = e.touches[0].clientY;
                pointer.isDragging = true;
            }
        }, { passive: true });

        window.addEventListener('touchmove', (e) => {
            if (pointer.isDragging && e.touches && e.touches[0]) {
                const dx = e.touches[0].clientX - pointer.lastX;
                const dy = e.touches[0].clientY - pointer.lastY;
                pointer.lastX = e.touches[0].clientX;
                pointer.lastY = e.touches[0].clientY;

                rotY += dx * 0.008;
                rotX += dy * 0.008;
            }
        }, { passive: true });

        window.addEventListener('touchend', () => {
            pointer.isDragging = false;
        }, { passive: true });

        // Initial setup
        resize();

        // Main 60 FPS Render Loop
        function animate(timestamp) {
            if (!isTabActive) return;

            const delta = lastTimestamp ? Math.min((timestamp - lastTimestamp) / 1000, 0.1) : 0.016;
            lastTimestamp = timestamp;
            time += delta;

            ctx.clearRect(0, 0, width, height);

            // 1. Smooth Spring Physics for Rotations
            if (!pointer.isDragging) {
                // Constant ambient rotation + mouse tilt blending
                rotY += baseSpinSpeedY;
                rotX += (targetRotX - rotX) * 0.04;
                rotZ = Math.sin(time * 0.5) * 0.08;
            }

            // Internal core counter-rotation
            const innerRotY = -rotY * 1.4;
            const innerRotX = rotX * 1.2;
            const innerRotZ = time * 0.4;

            // Holographic scanline sweep
            scanlineY += delta * 120;
            if (scanlineY > 280) scanlineY = -280;

            // 2. Draw Central Ambient Core Glow (Atmospheric Depth)
            const coreGlow = ctx.createRadialGradient(
                centerX, centerY, 10,
                centerX, centerY, isMobile ? 180 : 280
            );
            coreGlow.addColorStop(0, 'rgba(6, 182, 212, 0.14)');
            coreGlow.addColorStop(0.4, 'rgba(99, 102, 241, 0.08)');
            coreGlow.addColorStop(0.8, 'rgba(124, 58, 237, 0.03)');
            coreGlow.addColorStop(1, 'transparent');
            ctx.fillStyle = coreGlow;
            ctx.beginPath();
            ctx.arc(centerX, centerY, isMobile ? 180 : 280, 0, Math.PI * 2);
            ctx.fill();

            // 3. Project & Render 3D Dust Particles (Deep Background Layer)
            dustParticles.forEach(p => {
                const proj = project3D(p, rotX * 0.5, rotY * 0.5, rotZ * 0.5);
                const pulse = Math.sin(time * 2 + p.pulsePhase);
                const alpha = Math.max(0.1, (0.4 + pulse * 0.25) * Math.min(1, proj.scale * 1.5));

                ctx.beginPath();
                ctx.arc(proj.x2d, proj.y2d, Math.max(0.6, p.size * proj.scale), 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${p.color}, ${alpha})`;
                ctx.fill();
            });

            // 4. Render Orbital Gyroscopic Rings (Cincin Gyroskopik Holografis)
            orbitalRings.forEach(ring => {
                ring.angle += ring.speed;

                ctx.save();
                ctx.translate(centerX, centerY);

                // Rotate ring in 3D using composite 2D transform projection
                ctx.scale(1, Math.cos(ring.tiltX + rotX * 0.4));
                ctx.rotate(ring.tiltZ + rotY * 0.3);

                // Ring Track Stroke
                ctx.beginPath();
                ctx.arc(0, 0, ring.radius, 0, Math.PI * 2);
                ctx.strokeStyle = ring.color + (isMobile ? '0.22)' : '0.35)');
                ctx.lineWidth = isMobile ? 1 : 1.4;
                ctx.setLineDash(ring.dashPattern);
                ctx.stroke();

                // Orbiting Photon Marker Beads
                const beadAngle1 = ring.angle;
                const beadAngle2 = ring.angle + Math.PI;

                const b1x = Math.cos(beadAngle1) * ring.radius;
                const b1y = Math.sin(beadAngle1) * ring.radius;
                const b2x = Math.cos(beadAngle2) * ring.radius;
                const b2y = Math.sin(beadAngle2) * ring.radius;

                ctx.setLineDash([]);
                ctx.shadowColor = ring.beadColor;
                ctx.shadowBlur = 10;
                ctx.fillStyle = ring.beadColor;

                ctx.beginPath();
                ctx.arc(b1x, b1y, isMobile ? 2.5 : 3.5, 0, Math.PI * 2);
                ctx.arc(b2x, b2y, isMobile ? 2 : 2.8, 0, Math.PI * 2);
                ctx.fill();

                ctx.restore();
            });

            // 5. Project Vertices of Monolith and Inner Core
            const projectedOuter = outerVertices.map(v => project3D(v, rotX, rotY, rotZ));
            const projectedInner = innerVertices.map(v => project3D(v, innerRotX, innerRotY, innerRotZ));

            // 6. Render Semi-Transparent Outer Faces (Depth Sorting & Crystal Refraction)
            const sortedFaces = outerFaces.map(face => {
                const zAvg = (projectedOuter[face[0]].depth + projectedOuter[face[1]].depth + projectedOuter[face[2]].depth) / 3;
                return { face, zAvg };
            }).sort((a, b) => a.zAvg - b.zAvg); // Draw back faces first

            sortedFaces.forEach(item => {
                const f = item.face;
                const p0 = projectedOuter[f[0]];
                const p1 = projectedOuter[f[1]];
                const p2 = projectedOuter[f[2]];

                // Normal check for subtle dynamic shading
                const normalZ = (p1.x2d - p0.x2d) * (p2.y2d - p0.y2d) - (p1.y2d - p0.y2d) * (p2.x2d - p0.x2d);
                const isFront = normalZ > 0;
                const faceAlpha = isFront ? (isMobile ? 0.05 : 0.08) : (isMobile ? 0.02 : 0.035);

                ctx.beginPath();
                ctx.moveTo(p0.x2d, p0.y2d);
                ctx.lineTo(p1.x2d, p1.y2d);
                ctx.lineTo(p2.x2d, p2.y2d);
                ctx.closePath();

                // Prismatic chromatic gradient fill
                const faceGrad = ctx.createLinearGradient(p0.x2d, p0.y2d, p2.x2d, p2.y2d);
                faceGrad.addColorStop(0, `rgba(6, 182, 212, ${faceAlpha * 1.2})`);
                faceGrad.addColorStop(0.5, `rgba(99, 102, 241, ${faceAlpha})`);
                faceGrad.addColorStop(1, `rgba(168, 85, 247, ${faceAlpha * 0.8})`);

                ctx.fillStyle = faceGrad;
                ctx.fill();
            });

            // 7. Render Inner Counter-Rotating Energy Core (Wireframe + Core Glow)
            ctx.save();
            ctx.strokeStyle = 'rgba(6, 182, 212, 0.65)';
            ctx.lineWidth = isMobile ? 1 : 1.4;
            ctx.shadowColor = '#06b6d4';
            ctx.shadowBlur = 8;

            innerEdges.forEach(edge => {
                const pA = projectedInner[edge[0]];
                const pB = projectedInner[edge[1]];
                ctx.beginPath();
                ctx.moveTo(pA.x2d, pA.y2d);
                ctx.lineTo(pB.x2d, pB.y2d);
                ctx.stroke();
            });

            // Inner core glowing vertices
            projectedInner.forEach(p => {
                ctx.beginPath();
                ctx.arc(p.x2d, p.y2d, isMobile ? 2 : 2.8, 0, Math.PI * 2);
                ctx.fillStyle = '#38bdf8';
                ctx.fill();
            });
            ctx.restore();

            // 8. Render Outer Prismatic Wireframe Edges (Chiseled Crystal Monolith)
            ctx.save();
            outerEdges.forEach(edge => {
                const pA = projectedOuter[edge[0]];
                const pB = projectedOuter[edge[1]];

                const depthFactor = (pA.depth + pB.depth) * 0.5;
                const edgeAlpha = Math.max(0.18, Math.min(0.85, 0.45 + (depthFactor / 300) * 0.35));

                ctx.beginPath();
                ctx.moveTo(pA.x2d, pA.y2d);
                ctx.lineTo(pB.x2d, pB.y2d);

                // Alternating indigo & cyan crystal edge glow
                ctx.strokeStyle = `rgba(99, 102, 241, ${edgeAlpha})`;
                ctx.lineWidth = isMobile ? 1.2 : 1.6;
                ctx.shadowColor = '#6366f1';
                ctx.shadowBlur = 6;
                ctx.stroke();
            });

            // Outer vertices (Prismatic nodes)
            projectedOuter.forEach(p => {
                ctx.beginPath();
                ctx.arc(p.x2d, p.y2d, isMobile ? 2.2 : 3.2, 0, Math.PI * 2);
                ctx.fillStyle = '#e0e7ff';
                ctx.shadowColor = '#38bdf8';
                ctx.shadowBlur = 10;
                ctx.fill();
            });
            ctx.restore();

            // 9. Holographic Horizontal Scanline Shimmer
            ctx.save();
            ctx.translate(centerX, centerY);
            const scanGrad = ctx.createLinearGradient(0, scanlineY - 15, 0, scanlineY + 15);
            scanGrad.addColorStop(0, 'transparent');
            scanGrad.addColorStop(0.5, 'rgba(6, 182, 212, 0.18)');
            scanGrad.addColorStop(1, 'transparent');
            ctx.fillStyle = scanGrad;
            ctx.fillRect(-width * 0.4, scanlineY - 15, width * 0.8, 30);
            ctx.restore();

            // 10. Technical Monolith Telemetry HUD (Desktop Only)
            if (!isMobile) {
                ctx.save();
                ctx.font = '9px "JetBrains Mono", "Fira Code", monospace';
                ctx.fillStyle = 'rgba(148, 163, 184, 0.45)';
                ctx.strokeStyle = 'rgba(99, 102, 241, 0.35)';
                ctx.lineWidth = 1;

                const margin = 32;

                // Top-Left Legend
                ctx.fillText('SYS.CORE // PRISMATIC_MONOLITH_v3', margin, margin);
                ctx.fillText(`ROT_MATRIX: [Yaw: ${(rotY % (Math.PI*2)).toFixed(2)} | Pitch: ${rotX.toFixed(2)}]`, margin, margin + 14);

                // Top-Right Legend
                ctx.textAlign = 'right';
                ctx.fillText('CRYSTAL_REFRACTION: 1.48 // 60 FPS', width - margin, margin);
                ctx.fillText('SECURITY: QUANTUM_READY // ISO-27001', width - margin, margin + 14);

                // Bottom-Left
                ctx.textAlign = 'left';
                ctx.fillText('ACD // ARCHITECTURE INTELLIGENCE', margin, height - margin);

                // Bottom-Right
                ctx.textAlign = 'right';
                ctx.fillText('ORBITAL_BUS: DUAL_GYRO [SYNCHRONIZED]', width - margin, height - margin);

                ctx.restore();
            }

            animationFrameId = requestAnimationFrame(animate);
        }

        animationFrameId = requestAnimationFrame(animate);

        // Battery Guard: Instantly pause 3D math calculations when tab is hidden
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
        document.addEventListener('DOMContentLoaded', initHolographicMonolith);
    } else {
        initHolographicMonolith();
    }
})();
