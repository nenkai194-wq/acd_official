/**
 * PT Aksara Cipta Digital (ACD Official)
 * "Digital Horizon & 3D Topological Grid Wave"
 * 
 * Filosofi Visual:
 * - Merepresentasikan pondasi arsitektur data enterprise yang kokoh, terstruktur, dan berorientasi masa depan.
 * - Memetakan alur proses bisnis klien dari hulu ke hilir (Topografi Digital 3D).
 * - Berwibawa, elegan, presisi, dan sangat profesional tanpa kesan berantakan.
 * 
 * Fitur:
 * - 3D Wireframe Perspective Grid yang mengalir dinamis menuju horizon tak terhingga
 * - Harmonic wave elevation (gelombang topografi kontur digital)
 * - Interaktivitas Gravitasi Kursor (mouse & touch merespons lengkungan topografi elastis)
 * - Pulsa data bercahaya (cyan photons) yang meluncur di sepanjang garis meridian grid
 * - Latar atas langit kosmik bersih & tenang, menjamin keterbacaan judul 100% jernih di PC & HP
 * - 60 FPS GPU-accelerated Canvas with 0% battery waste
 */

(function() {
    'use strict';

    function initACDDigitalHorizon() {
        const canvas = document.getElementById('ambient-body-canvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let width = 0;
        let height = 0;
        let isMobile = window.innerWidth < 768;
        let dpr = isMobile ? Math.min(window.devicePixelRatio || 1, 1.25) : Math.min(window.devicePixelRatio || 1, 1.5);

        // Perspective 3D Grid Parameters
        let horizonY = 0;
        let fov = 300;
        let gridCols = 32;
        let gridRows = 24;
        let gridSpacingX = 85;
        let gridSpacingZ = 65;
        let gridSpeed = 1.35;
        let gridOffsetZ = 0;
        let time = 0;

        // Interactive Cursor & Touch Physics
        const mouse = {
            x: null,
            y: null,
            targetX: null,
            targetY: null,
            worldX: 0,
            worldZ: 400,
            radius: 220,
            isActive: false,
            elevation: 0
        };

        // Micro Data Pulses running along grid lines
        let gridPulses = [];

        // Stars / Quantum Dust above the horizon
        let stars = [];
        const STAR_COUNT = isMobile ? 35 : 70;

        function resize() {
            width = window.innerWidth;
            height = window.innerHeight;
            isMobile = width < 768;
            dpr = isMobile ? Math.min(window.devicePixelRatio || 1, 1.25) : Math.min(window.devicePixelRatio || 1, 1.5);

            canvas.width = width * dpr;
            canvas.height = height * dpr;
            ctx.scale(dpr, dpr);

            // Horizon position: sits comfortably in the lower half to frame typography cleanly
            horizonY = height * (isMobile ? 0.62 : 0.54);
            fov = isMobile ? 220 : 320;
            gridCols = isMobile ? 20 : 34;
            gridRows = isMobile ? 18 : 25;
            gridSpacingX = isMobile ? 65 : 85;
            gridSpacingZ = isMobile ? 50 : 62;
            mouse.radius = isMobile ? 140 : 220;

            initStars();
        }

        function initStars() {
            stars = [];
            const count = isMobile ? 35 : 70;
            for (let i = 0; i < count; i++) {
                stars.push({
                    x: Math.random() * width,
                    y: Math.random() * horizonY * 1.1,
                    size: Math.random() * 1.6 + 0.6,
                    baseAlpha: Math.random() * 0.5 + 0.2,
                    pulseSpeed: Math.random() * 0.02 + 0.008,
                    pulseAngle: Math.random() * Math.PI * 2,
                    color: Math.random() > 0.4 ? '6, 182, 212' : '99, 102, 241'
                });
            }
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

        // Touch listeners
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

        // Harmonic Wave Elevation Calculation
        function getWaveElevation(worldX, worldZ, t) {
            // Base undulating wave representing systemic workflow rhythm
            const w1 = Math.sin(worldX * 0.0032 + t * 0.018) * Math.cos(worldZ * 0.0028 + t * 0.014) * 38;
            const w2 = Math.sin(worldX * 0.0016 - worldZ * 0.0022 + t * 0.012) * 22;
            let elev = w1 + w2;

            // Interactive Cursor gravitational displacement
            if (mouse.x !== null && mouse.y !== null) {
                const dx = worldX - mouse.worldX;
                const dz = worldZ - mouse.worldZ;
                const distSq = dx * dx + dz * dz;
                const rSq = mouse.radius * mouse.radius * 2.2;
                if (distSq < rSq) {
                    const factor = (1 - distSq / rSq);
                    elev -= factor * factor * 55; // Elastic downward gravitation
                }
            }

            return elev;
        }

        // Pulse Data Class
        class GridPulse {
            constructor(colIndex) {
                this.col = colIndex;
                this.row = 0;
                this.speed = Math.random() * 0.25 + 0.18;
                this.isDone = false;
            }

            update() {
                this.row += this.speed;
                if (this.row >= gridRows - 1) {
                    this.isDone = true;
                }
            }
        }

        // Animation Loop
        let animationFrameId = null;
        let isTabActive = true;

        function animate() {
            if (!isTabActive) return;

            time++;
            gridOffsetZ = (gridOffsetZ + gridSpeed) % gridSpacingZ;

            // Smooth mouse interpolation
            if (mouse.targetX !== null && mouse.targetY !== null) {
                if (mouse.x === null) {
                    mouse.x = mouse.targetX;
                    mouse.y = mouse.targetY;
                } else {
                    mouse.x += (mouse.targetX - mouse.x) * 0.12;
                    mouse.y += (mouse.targetY - mouse.y) * 0.12;
                }
                // Estimate world coords for mouse
                mouse.worldX = (mouse.x - width / 2) * 2.2;
                const relY = Math.max(10, mouse.y - horizonY);
                mouse.worldZ = Math.min(900, Math.max(100, (fov * 80) / relY));
            } else {
                mouse.x = null;
                mouse.y = null;
            }

            // Clear canvas
            ctx.clearRect(0, 0, width, height);

            // 1. Render Upper Stars / Micro Quantum Dust
            for (let i = 0; i < stars.length; i++) {
                const s = stars[i];
                s.pulseAngle += s.pulseSpeed;
                const alpha = s.baseAlpha + Math.sin(s.pulseAngle) * 0.2;
                ctx.beginPath();
                ctx.arc(s.x, s.y, s.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${s.color}, ${Math.max(0.05, alpha)})`;
                ctx.fill();
            }

            // 2. Horizon Glow Line & Ambient Bloom
            const horizonGrad = ctx.createLinearGradient(0, horizonY - 40, 0, horizonY + 40);
            horizonGrad.addColorStop(0, 'rgba(6, 182, 212, 0)');
            horizonGrad.addColorStop(0.5, 'rgba(99, 102, 241, 0.18)');
            horizonGrad.addColorStop(1, 'rgba(6, 182, 212, 0)');

            ctx.fillStyle = horizonGrad;
            ctx.fillRect(0, horizonY - 40, width, 80);

            // Laser horizon boundary line
            const horizonLineGrad = ctx.createLinearGradient(0, 0, width, 0);
            horizonLineGrad.addColorStop(0, 'rgba(99, 102, 241, 0)');
            horizonLineGrad.addColorStop(0.2, 'rgba(99, 102, 241, 0.45)');
            horizonLineGrad.addColorStop(0.5, 'rgba(6, 182, 212, 0.85)');
            horizonLineGrad.addColorStop(0.8, 'rgba(139, 92, 246, 0.45)');
            horizonLineGrad.addColorStop(1, 'rgba(99, 102, 241, 0)');

            ctx.beginPath();
            ctx.moveTo(0, horizonY);
            ctx.lineTo(width, horizonY);
            ctx.strokeStyle = horizonLineGrad;
            ctx.lineWidth = 1.2;
            ctx.stroke();

            // 3. Compute 3D Projected Grid Points
            const halfCols = Math.floor(gridCols / 2);
            const centerX = width / 2;
            const points = []; // 2D array [row][col]

            for (let r = 0; r <= gridRows; r++) {
                points[r] = [];
                const worldZ = (r * gridSpacingZ) + (gridSpacingZ - gridOffsetZ) + 60;
                
                // Opacity fades gracefully near horizon (far plane)
                const depthFactor = Math.min(1, Math.max(0, (worldZ - 60) / (gridRows * gridSpacingZ)));
                const alpha = Math.sin(depthFactor * Math.PI) * (0.85 * depthFactor + 0.15);

                for (let c = -halfCols; c <= halfCols; c++) {
                    const worldX = c * gridSpacingX;
                    const worldY = getWaveElevation(worldX, worldZ, time);

                    // Perspective projection formula
                    const screenX = centerX + (worldX * fov) / worldZ;
                    const screenY = horizonY + ((worldY + 75) * fov) / worldZ;

                    points[r][c + halfCols] = {
                        x: screenX,
                        y: screenY,
                        z: worldZ,
                        alpha: alpha,
                        elev: worldY
                    };
                }
            }

            // 4. Draw Latitudinal Lines (Garis Horisontal Gelombang)
            for (let r = 0; r <= gridRows; r++) {
                ctx.beginPath();
                let started = false;
                const rowAlpha = points[r][halfCols].alpha;
                if (rowAlpha <= 0.02) continue;

                for (let c = 0; c < points[r].length; c++) {
                    const pt = points[r][c];
                    if (pt.x < -100 || pt.x > width + 100) continue;

                    if (!started) {
                        ctx.moveTo(pt.x, pt.y);
                        started = true;
                    } else {
                        ctx.lineTo(pt.x, pt.y);
                    }
                }

                if (started) {
                    const depthPercent = r / gridRows;
                    // Near: vibrant electric cyan/indigo; Far: deep purple
                    ctx.strokeStyle = `rgba(${depthPercent > 0.5 ? '6, 182, 212' : '99, 102, 241'}, ${rowAlpha * 0.45})`;
                    ctx.lineWidth = depthPercent > 0.6 ? 1.1 : 0.8;
                    ctx.stroke();
                }
            }

            // 5. Draw Longitudinal Lines (Garis Perspektif Menuju Horizon)
            const totalCols = halfCols * 2 + 1;
            for (let c = 0; c < totalCols; c++) {
                ctx.beginPath();
                let started = false;

                for (let r = 0; r <= gridRows; r++) {
                    const pt = points[r][c];
                    if (!pt || pt.alpha <= 0.02) continue;

                    if (!started) {
                        ctx.moveTo(pt.x, pt.y);
                        started = true;
                    } else {
                        ctx.lineTo(pt.x, pt.y);
                    }
                }

                if (started) {
                    const colDistFromCenter = Math.abs(c - halfCols) / halfCols;
                    const colAlpha = (1 - colDistFromCenter * 0.45) * 0.35;
                    ctx.strokeStyle = `rgba(99, 102, 241, ${Math.max(0.05, colAlpha)})`;
                    ctx.lineWidth = 0.85;
                    ctx.stroke();
                }
            }

            // 6. Spawn & Render Data Pulses Along Perspective Meridian Lines
            if (gridPulses.length < 6 && Math.random() < 0.08) {
                const randCol = Math.floor(Math.random() * totalCols);
                gridPulses.push(new GridPulse(randCol));
            }

            for (let k = gridPulses.length - 1; k >= 0; k--) {
                const pulse = gridPulses[k];
                pulse.update();

                const rIndex = Math.floor(pulse.row);
                const rFract = pulse.row - rIndex;
                const cIndex = pulse.col;

                if (points[rIndex] && points[rIndex + 1] && points[rIndex][cIndex] && points[rIndex + 1][cIndex]) {
                    const pA = points[rIndex][cIndex];
                    const pB = points[rIndex + 1][cIndex];
                    const pulseX = pA.x + (pB.x - pA.x) * rFract;
                    const pulseY = pA.y + (pB.y - pA.y) * rFract;

                    // Glowing data pulse head
                    ctx.beginPath();
                    ctx.arc(pulseX, pulseY, 2.2, 0, Math.PI * 2);
                    ctx.fillStyle = '#ffffff';
                    ctx.shadowColor = '#06b6d4';
                    ctx.shadowBlur = 8;
                    ctx.fill();
                    ctx.shadowBlur = 0;
                }

                if (pulse.isDone) {
                    gridPulses.splice(k, 1);
                }
            }

            // 7. Interactive Cursor Beacon & Ripple
            if (mouse.x !== null && mouse.y !== null && mouse.isActive) {
                ctx.beginPath();
                ctx.arc(mouse.x, mouse.y, 3, 0, Math.PI * 2);
                ctx.fillStyle = '#06b6d4';
                ctx.shadowColor = '#38bdf8';
                ctx.shadowBlur = 10;
                ctx.fill();
                ctx.shadowBlur = 0;

                const ringRadius = 8 + (time % 40) * 0.8;
                const ringAlpha = (1 - (time % 40) / 40) * 0.6;
                ctx.beginPath();
                ctx.arc(mouse.x, mouse.y, ringRadius, 0, Math.PI * 2);
                ctx.strokeStyle = `rgba(6, 182, 212, ${ringAlpha})`;
                ctx.lineWidth = 1;
                ctx.stroke();
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
                animate();
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initACDDigitalHorizon);
    } else {
        initACDDigitalHorizon();
    }
})();
