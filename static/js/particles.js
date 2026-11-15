/**
 * PT Aksara Cipta Digital (ACD Official)
 * "Living Architecture Blueprint" (Cetak Biru Arsitektur Sistem Dinamis)
 * 
 * Filosofi Visual:
 * - Merepresentasikan pondasi cetak biru arsitektur enterprise: microservices, data bus,
 *   dan pipeline data real-time sebelum software dibangun.
 * - Selaras dengan nilai utama ACD: "ACD akan mendalami alur proses bisnis Anda terlebih
 *   dahulu sebelum membangun software."
 * - Berwibawa, futuristik, presisi engineering-grade, dan berkelas korporat tinggi.
 * 
 * Fitur:
 * - Orthogonal Circuit Buses: Jalur sirkuit bersudut presisi 90° dan 45° chamfered
 * - System Architecture Nodes: Blok chip mikro-arsitektur (CORE.AI, GATEWAY.API, ERP.ENGINE, DB.CLUSTER, dll.)
 * - Flowing Photon Data Packets: Pulsa cahaya paket data berkecepatan tinggi dengan comet tail
 * - Dynamic Blueprint Grid: Matriks grid titik & crosshair presisi dengan koordinat telemetri
 * - Interactive Diagnostic Reticle: Kursor mouse & sentuhan touch sebagai probe pemindai arsitektur sistem
 * - 100% Bebas Video, 60 FPS Canvas Ringan, hemat daya baterai (0% CPU saat tab tidak aktif)
 */

(function() {
    'use strict';

    function initACDArchitectureBlueprint() {
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

        // Interactive Cursor & Touch Scanner
        const pointer = {
            x: null,
            y: null,
            targetX: null,
            targetY: null,
            isActive: false,
            clickPulse: 0,
            reticleAngle: 0
        };

        // Architecture Blueprint Nodes & Circuits
        let nodes = [];
        let circuitTracks = [];
        let dataPackets = [];
        let pingRipples = [];

        // Grid parameters
        let gridStep = 54;

        // Node Definition Templates
        function setupArchitectureLayout() {
            nodes = [];
            circuitTracks = [];
            dataPackets = [];

            if (isMobile) {
                // Mobile layout: Nodes placed safely along perimeter to keep headline 100% clear
                gridStep = 44;
                nodes = [
                    {
                        id: 'CORE.AI',
                        label: 'CORE.AI',
                        sub: 'ACTIVE',
                        x: width * 0.18,
                        y: height * 0.12,
                        w: 72,
                        h: 30,
                        color: '#06b6d4',
                        type: 'ai',
                        pulse: 0
                    },
                    {
                        id: 'API.GW',
                        label: 'API.GW',
                        sub: 'SECURE',
                        x: width * 0.82,
                        y: height * 0.12,
                        w: 72,
                        h: 30,
                        color: '#6366f1',
                        type: 'gw',
                        pulse: 0
                    },
                    {
                        id: 'ERP.SYS',
                        label: 'ERP.SYS',
                        sub: 'ONLINE',
                        x: width * 0.18,
                        y: height * 0.88,
                        w: 74,
                        h: 30,
                        color: '#8b5cf6',
                        type: 'erp',
                        pulse: 0
                    },
                    {
                        id: 'DB.DATA',
                        label: 'DB.DATA',
                        sub: 'SYNCED',
                        x: width * 0.82,
                        y: height * 0.88,
                        w: 74,
                        h: 30,
                        color: '#10b981',
                        type: 'db',
                        pulse: 0
                    }
                ];
            } else {
                // Desktop layout: Enterprise Service Grid surrounding the central hero zone
                gridStep = 56;
                nodes = [
                    {
                        id: 'CORE.AI',
                        label: 'CORE.AI',
                        sub: 'NEURAL_ENGINE',
                        x: width * 0.11,
                        y: height * 0.22,
                        w: 104,
                        h: 38,
                        color: '#06b6d4',
                        type: 'ai',
                        pulse: 0
                    },
                    {
                        id: 'GATEWAY.API',
                        label: 'GATEWAY.API',
                        sub: 'REVERSE_PROXY',
                        x: width * 0.89,
                        y: height * 0.20,
                        w: 112,
                        h: 38,
                        color: '#6366f1',
                        type: 'gw',
                        pulse: 0
                    },
                    {
                        id: 'ERP.ENGINE',
                        label: 'ERP.ENGINE',
                        sub: 'BUSINESS_LOGIC',
                        x: width * 0.09,
                        y: height * 0.58,
                        w: 110,
                        h: 38,
                        color: '#8b5cf6',
                        type: 'erp',
                        pulse: 0
                    },
                    {
                        id: 'DB.CLUSTER',
                        label: 'DB.CLUSTER',
                        sub: 'ACID_ENCRYPTED',
                        x: width * 0.91,
                        y: height * 0.60,
                        w: 112,
                        h: 38,
                        color: '#10b981',
                        type: 'db',
                        pulse: 0
                    },
                    {
                        id: 'AUTH.OAUTH',
                        label: 'AUTH.2FA',
                        sub: 'ZERO_TRUST',
                        x: width * 0.28,
                        y: height * 0.14,
                        w: 96,
                        h: 34,
                        color: '#38bdf8',
                        type: 'auth',
                        pulse: 0
                    },
                    {
                        id: 'SVC.MESH',
                        label: 'SVC.MESH',
                        sub: 'K8S_HYBRID',
                        x: width * 0.73,
                        y: height * 0.13,
                        w: 98,
                        h: 34,
                        color: '#a855f7',
                        type: 'mesh',
                        pulse: 0
                    },
                    {
                        id: 'QUEUE.EVENT',
                        label: 'QUEUE.EVENT',
                        sub: 'KAFKA_STREAM',
                        x: width * 0.23,
                        y: height * 0.86,
                        w: 106,
                        h: 36,
                        color: '#f59e0b',
                        type: 'queue',
                        pulse: 0
                    },
                    {
                        id: 'ANALYTICS.BI',
                        label: 'ANALYTICS.BI',
                        sub: 'REALTIME_DASH',
                        x: width * 0.77,
                        y: height * 0.85,
                        w: 110,
                        h: 36,
                        color: '#06b6d4',
                        type: 'bi',
                        pulse: 0
                    }
                ];
            }

            // Snap nodes gently to nearest grid coordinate for crisp engineering precision
            nodes.forEach(node => {
                node.x = Math.round(node.x / gridStep) * gridStep;
                node.y = Math.round(node.y / gridStep) * gridStep;
            });

            // Generate structured orthogonal circuit tracks with 90° and 45° bends
            generateCircuitTracks();

            // Spawn initial flowing photon packets
            const packetCount = isMobile ? 8 : 18;
            for (let i = 0; i < packetCount; i++) {
                spawnDataPacket(true);
            }
        }

        // Helper: Create orthogonal path between two points avoiding center headline
        function buildOrthogonalPath(p1, p2, style = 'solid') {
            const waypoints = [];
            waypoints.push({ x: p1.x, y: p1.y });

            const dx = p2.x - p1.x;
            const dy = p2.y - p1.y;

            // Intermediate corner routing
            if (Math.abs(dx) > Math.abs(dy)) {
                const midX = p1.x + dx * 0.5;
                const chamfer = 16;
                // Add chamfered 45 degree turn
                waypoints.push({ x: midX - (dx > 0 ? chamfer : -chamfer), y: p1.y });
                waypoints.push({ x: midX + (dx > 0 ? chamfer : -chamfer), y: p1.y + (dy > 0 ? chamfer : -chamfer) });
                waypoints.push({ x: p2.x, y: p1.y + dy });
            } else {
                const midY = p1.y + dy * 0.5;
                const chamfer = 16;
                waypoints.push({ x: p1.x, y: midY - (dy > 0 ? chamfer : -chamfer) });
                waypoints.push({ x: p1.x + (dx > 0 ? chamfer : -chamfer), y: midY + (dy > 0 ? chamfer : -chamfer) });
                waypoints.push({ x: p2.x, y: p2.y });
            }

            // Calculate cumulative lengths for smooth interpolation
            let totalLength = 0;
            const lengths = [0];
            for (let i = 0; i < waypoints.length - 1; i++) {
                const segLen = Math.hypot(waypoints[i + 1].x - waypoints[i].x, waypoints[i + 1].y - waypoints[i].y);
                totalLength += segLen;
                lengths.push(totalLength);
            }

            return {
                waypoints,
                lengths,
                totalLength,
                style,
                color: Math.random() > 0.4 ? 'rgba(99, 102, 241, ' : 'rgba(6, 182, 212, ',
                targetNode: null
            };
        }

        function generateCircuitTracks() {
            circuitTracks = [];

            if (isMobile) {
                // Mobile connections
                if (nodes.length >= 4) {
                    circuitTracks.push(buildOrthogonalPath(nodes[0], nodes[1]));
                    circuitTracks.push(buildOrthogonalPath(nodes[0], nodes[2]));
                    circuitTracks.push(buildOrthogonalPath(nodes[1], nodes[3]));
                    circuitTracks.push(buildOrthogonalPath(nodes[2], nodes[3]));
                }
            } else {
                // Desktop interconnect topology
                // 1. Perimeter bus lines
                if (nodes.length >= 8) {
                    circuitTracks.push(buildOrthogonalPath(nodes[0], nodes[4])); // AI -> AUTH
                    circuitTracks.push(buildOrthogonalPath(nodes[4], nodes[5])); // AUTH -> MESH
                    circuitTracks.push(buildOrthogonalPath(nodes[5], nodes[1])); // MESH -> GATEWAY
                    circuitTracks.push(buildOrthogonalPath(nodes[0], nodes[2])); // AI -> ERP
                    circuitTracks.push(buildOrthogonalPath(nodes[1], nodes[3])); // GATEWAY -> DB
                    circuitTracks.push(buildOrthogonalPath(nodes[2], nodes[6])); // ERP -> QUEUE
                    circuitTracks.push(buildOrthogonalPath(nodes[6], nodes[7])); // QUEUE -> BI
                    circuitTracks.push(buildOrthogonalPath(nodes[7], nodes[3])); // BI -> DB

                    // Diagonal cross-highways routing around central text area
                    circuitTracks.push(buildOrthogonalPath(
                        { x: nodes[0].x, y: nodes[0].y + 40 },
                        { x: width * 0.35, y: height * 0.42 }
                    ));
                    circuitTracks.push(buildOrthogonalPath(
                        { x: width * 0.35, y: height * 0.42 },
                        { x: nodes[6].x + 40, y: nodes[6].y }
                    ));
                    circuitTracks.push(buildOrthogonalPath(
                        { x: nodes[1].x, y: nodes[1].y + 40 },
                        { x: width * 0.65, y: height * 0.42 }
                    ));
                    circuitTracks.push(buildOrthogonalPath(
                        { x: width * 0.65, y: height * 0.42 },
                        { x: nodes[7].x - 40, y: nodes[7].y }
                    ));
                }
            }
        }

        // Spawn a flowing photon data packet
        function spawnDataPacket(randomStart = false) {
            if (circuitTracks.length === 0) return;
            const trackIndex = Math.floor(Math.random() * circuitTracks.length);
            const track = circuitTracks[trackIndex];
            if (!track || track.totalLength <= 0) return;

            dataPackets.push({
                trackIndex: trackIndex,
                dist: randomStart ? Math.random() * track.totalLength : 0,
                speed: (isMobile ? 1.4 : 1.8) + Math.random() * 1.2,
                size: isMobile ? 2.5 : 3.5,
                tailLength: isMobile ? 22 : 36,
                colorType: Math.random() > 0.4 ? 'cyan' : 'indigo'
            });
        }

        // Trigger Node Ping Ripple
        function triggerNodePing(x, y, color = '#06b6d4') {
            pingRipples.push({
                x,
                y,
                r: 6,
                maxR: isMobile ? 24 : 38,
                alpha: 0.8,
                color
            });
        }

        function resize() {
            width = window.innerWidth;
            height = window.innerHeight;
            isMobile = width < 768;
            dpr = isMobile ? Math.min(window.devicePixelRatio || 1, 1.25) : Math.min(window.devicePixelRatio || 1, 1.5);

            canvas.width = Math.floor(width * dpr);
            canvas.height = Math.floor(height * dpr);
            ctx.scale(dpr, dpr);

            setupArchitectureLayout();
        }

        window.addEventListener('resize', resize, { passive: true });

        // Pointer listeners
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

        // Touch listeners
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

        // Click / Tap injection: Dispatches burst of diagnostic pulses
        window.addEventListener('click', (e) => {
            pointer.clickPulse = 1.0;
            triggerNodePing(e.clientX, e.clientY, '#38bdf8');
            for (let i = 0; i < 3; i++) {
                spawnDataPacket(false);
            }
        }, { passive: true });

        // Interpolate position along track waypoints
        function getPointOnTrack(track, dist) {
            const clampedDist = Math.max(0, Math.min(dist, track.totalLength));
            for (let i = 0; i < track.lengths.length - 1; i++) {
                if (clampedDist >= track.lengths[i] && clampedDist <= track.lengths[i + 1]) {
                    const segLen = track.lengths[i + 1] - track.lengths[i];
                    if (segLen === 0) return track.waypoints[i];
                    const t = (clampedDist - track.lengths[i]) / segLen;
                    return {
                        x: track.waypoints[i].x + (track.waypoints[i + 1].x - track.waypoints[i].x) * t,
                        y: track.waypoints[i].y + (track.waypoints[i + 1].y - track.waypoints[i].y) * t
                    };
                }
            }
            return track.waypoints[track.waypoints.length - 1];
        }

        // Initial setup
        resize();

        // Animation Loop (60 FPS)
        function animate(timestamp) {
            if (!isTabActive) return;

            const delta = lastTimestamp ? Math.min((timestamp - lastTimestamp) / 1000, 0.1) : 0.016;
            lastTimestamp = timestamp;
            time += delta;

            ctx.clearRect(0, 0, width, height);

            // 1. Smooth Pointer Lerp
            if (pointer.isActive && pointer.targetX !== null) {
                pointer.x += (pointer.targetX - pointer.x) * 0.15;
                pointer.y += (pointer.targetY - pointer.y) * 0.15;
                pointer.reticleAngle += delta * 1.5;
            }
            if (pointer.clickPulse > 0) {
                pointer.clickPulse = Math.max(0, pointer.clickPulse - delta * 2.0);
            }

            // 2. Blueprint Matrix Crosshairs & Coordinate Grid
            ctx.save();
            ctx.fillStyle = 'rgba(99, 102, 241, 0.18)';
            ctx.strokeStyle = 'rgba(6, 182, 212, 0.14)';
            ctx.lineWidth = 1;

            const crossSize = 3;
            for (let x = gridStep; x < width; x += gridStep) {
                for (let y = gridStep; y < height; y += gridStep) {
                    // Attenuate grid in the center reading area to guarantee crystal-clear headline text
                    const distXFromCenter = Math.abs(x - width * 0.5);
                    const distYFromCenter = Math.abs(y - height * 0.44);
                    let alphaMultiplier = 1.0;
                    if (distXFromCenter < width * 0.38 && distYFromCenter < height * 0.22) {
                        alphaMultiplier = 0.3; // Low contrast in center text area
                    }

                    ctx.globalAlpha = 0.45 * alphaMultiplier;
                    ctx.beginPath();
                    ctx.moveTo(x - crossSize, y);
                    ctx.lineTo(x + crossSize, y);
                    ctx.moveTo(x, y - crossSize);
                    ctx.lineTo(x, y + crossSize);
                    ctx.stroke();
                }
            }
            ctx.restore();

            // 3. Technical Blueprint Corner Brackets & Metadata (Desktop only)
            if (!isMobile) {
                ctx.save();
                ctx.font = '9px "JetBrains Mono", "Fira Code", monospace';
                ctx.fillStyle = 'rgba(148, 163, 184, 0.45)';
                ctx.strokeStyle = 'rgba(99, 102, 241, 0.4)';
                ctx.lineWidth = 1.2;

                const bracketSize = 18;
                const margin = 28;

                // Top-Left Bracket & Spec
                ctx.beginPath();
                ctx.moveTo(margin + bracketSize, margin);
                ctx.lineTo(margin, margin);
                ctx.lineTo(margin, margin + bracketSize);
                ctx.stroke();
                ctx.fillText('SYS.BLUEPRINT // v4.2 [ORTHOGONAL_BUS]', margin + 8, margin - 8);

                // Top-Right Bracket & Security Spec
                ctx.beginPath();
                ctx.moveTo(width - margin - bracketSize, margin);
                ctx.lineTo(width - margin, margin);
                ctx.lineTo(width - margin, margin + bracketSize);
                ctx.stroke();
                ctx.textAlign = 'right';
                ctx.fillText('ARCH_SPEC: ISO-27001 // OWASP_TOP10', width - margin - 8, margin - 8);

                // Bottom-Left Bracket & Coordinates
                ctx.beginPath();
                ctx.moveTo(margin, height - margin - bracketSize);
                ctx.lineTo(margin, height - margin);
                ctx.lineTo(margin + bracketSize, height - margin);
                ctx.stroke();
                ctx.textAlign = 'left';
                ctx.fillText('GEO.GRID: 107.6°E 06.9°S // SLA 99.9%', margin + 8, height - margin + 14);

                // Bottom-Right Bracket & Live Status
                ctx.beginPath();
                ctx.moveTo(width - margin - bracketSize, height - margin);
                ctx.lineTo(width - margin, height - margin);
                ctx.lineTo(width - margin, height - margin - bracketSize);
                ctx.stroke();
                ctx.textAlign = 'right';
                ctx.fillText('BUS_MONITOR: REALTIME_ACTIVE [60 FPS]', width - margin - 8, height - margin + 14);

                ctx.restore();
            }

            // 4. Render Orthogonal Circuit Busses (Garis Sirkuit Arsitektur)
            circuitTracks.forEach((track) => {
                ctx.save();
                // Proximity glow to cursor
                let trackAlpha = 0.22;
                if (pointer.isActive && pointer.x !== null) {
                    const midP = track.waypoints[Math.floor(track.waypoints.length / 2)];
                    const distToPointer = Math.hypot(pointer.x - midP.x, pointer.y - midP.y);
                    if (distToPointer < 200) {
                        trackAlpha = 0.22 + (1 - distToPointer / 200) * 0.45;
                    }
                }

                ctx.strokeStyle = track.color + trackAlpha + ')';
                ctx.lineWidth = track.style === 'bold' ? 2 : 1.2;
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';

                ctx.beginPath();
                track.waypoints.forEach((pt, idx) => {
                    if (idx === 0) ctx.moveTo(pt.x, pt.y);
                    else ctx.lineTo(pt.x, pt.y);
                });
                ctx.stroke();

                // Draw tiny terminal junction solder dots at corners
                ctx.fillStyle = track.color + (trackAlpha * 1.5) + ')';
                track.waypoints.forEach(pt => {
                    ctx.beginPath();
                    ctx.arc(pt.x, pt.y, 1.8, 0, Math.PI * 2);
                    ctx.fill();
                });

                ctx.restore();
            });

            // 5. Update & Render Luminous Photon Data Packets (Pulsa Aliran Data)
            for (let i = dataPackets.length - 1; i >= 0; i--) {
                const packet = dataPackets[i];
                const track = circuitTracks[packet.trackIndex];
                if (!track) continue;

                packet.dist += packet.speed;

                // Reached end of track -> trigger node ping and respawn
                if (packet.dist >= track.totalLength) {
                    const endPt = track.waypoints[track.waypoints.length - 1];
                    triggerNodePing(endPt.x, endPt.y, packet.colorType === 'cyan' ? '#06b6d4' : '#818cf8');
                    dataPackets.splice(i, 1);
                    spawnDataPacket(false);
                    continue;
                }

                const headPos = getPointOnTrack(track, packet.dist);

                ctx.save();
                // Draw comet glowing tail
                const tailSteps = 8;
                for (let s = 1; s <= tailSteps; s++) {
                    const tailDist = Math.max(0, packet.dist - (packet.tailLength * (s / tailSteps)));
                    const tailPos = getPointOnTrack(track, tailDist);
                    const tailAlpha = (1 - s / tailSteps) * 0.6;
                    ctx.beginPath();
                    ctx.arc(tailPos.x, tailPos.y, packet.size * (1 - (s / tailSteps) * 0.5), 0, Math.PI * 2);
                    ctx.fillStyle = packet.colorType === 'cyan' 
                        ? `rgba(6, 182, 212, ${tailAlpha})` 
                        : `rgba(99, 102, 241, ${tailAlpha})`;
                    ctx.fill();
                }

                // Draw bright glowing photon head
                ctx.beginPath();
                ctx.arc(headPos.x, headPos.y, packet.size, 0, Math.PI * 2);
                ctx.fillStyle = packet.colorType === 'cyan' ? '#38bdf8' : '#c7d2fe';
                ctx.shadowColor = packet.colorType === 'cyan' ? '#06b6d4' : '#6366f1';
                ctx.shadowBlur = isMobile ? 8 : 14;
                ctx.fill();

                // Core brilliant spark
                ctx.beginPath();
                ctx.arc(headPos.x, headPos.y, packet.size * 0.45, 0, Math.PI * 2);
                ctx.fillStyle = '#ffffff';
                ctx.fill();

                ctx.restore();
            }

            // 6. Update & Render Node Ping Ripples
            for (let r = pingRipples.length - 1; r >= 0; r--) {
                const rip = pingRipples[r];
                rip.r += delta * 45;
                rip.alpha -= delta * 1.5;

                if (rip.alpha <= 0 || rip.r >= rip.maxR) {
                    pingRipples.splice(r, 1);
                    continue;
                }

                ctx.save();
                ctx.beginPath();
                ctx.arc(rip.x, rip.y, rip.r, 0, Math.PI * 2);
                ctx.strokeStyle = rip.color;
                ctx.globalAlpha = Math.max(0, rip.alpha);
                ctx.lineWidth = 1.2;
                ctx.stroke();
                ctx.restore();
            }

            // 7. Render Architecture Terminal Nodes (Chip Komponen Sistem)
            nodes.forEach(node => {
                ctx.save();

                const hw = node.w * 0.5;
                const hh = node.h * 0.5;
                const x0 = node.x - hw;
                const y0 = node.y - hh;

                // Subtle proximity illumination from pointer
                let proximityBoost = 0;
                if (pointer.isActive && pointer.x !== null) {
                    const distToPtr = Math.hypot(pointer.x - node.x, pointer.y - node.y);
                    if (distToPtr < 160) {
                        proximityBoost = (1 - distToPtr / 160) * 0.5;
                    }
                }

                // Node Box Background
                ctx.fillStyle = 'rgba(7, 12, 34, 0.78)';
                ctx.strokeStyle = `rgba(99, 102, 241, ${0.4 + proximityBoost})`;
                ctx.lineWidth = 1;
                ctx.shadowColor = node.color;
                ctx.shadowBlur = proximityBoost > 0 ? 12 : 4;

                // Rounded Rect container
                const radius = 4;
                ctx.beginPath();
                ctx.moveTo(x0 + radius, y0);
                ctx.lineTo(x0 + node.w - radius, y0);
                ctx.quadraticCurveTo(x0 + node.w, y0, x0 + node.w, y0 + radius);
                ctx.lineTo(x0 + node.w, y0 + node.h - radius);
                ctx.quadraticCurveTo(x0 + node.w, y0 + node.h, x0 + node.w - radius, y0 + node.h);
                ctx.lineTo(x0 + radius, y0 + node.h);
                ctx.quadraticCurveTo(x0, y0 + node.h, x0, y0 + node.h - radius);
                ctx.lineTo(x0, y0 + radius);
                ctx.quadraticCurveTo(x0, y0, x0 + radius, y0);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                ctx.shadowBlur = 0;

                // Corner Cyan Accent Markers
                ctx.strokeStyle = node.color;
                ctx.lineWidth = 1.5;
                const acc = 4;
                // Top-left
                ctx.beginPath();
                ctx.moveTo(x0, y0 + acc);
                ctx.lineTo(x0, y0);
                ctx.lineTo(x0 + acc, y0);
                ctx.stroke();
                // Bottom-right
                ctx.beginPath();
                ctx.moveTo(x0 + node.w - acc, y0 + node.h);
                ctx.lineTo(x0 + node.w, y0 + node.h);
                ctx.lineTo(x0 + node.w, y0 + node.h - acc);
                ctx.stroke();

                // Status LED Dot (Pulsing Green or Cyan)
                const ledSine = Math.sin(time * 3 + node.x * 0.05);
                const ledAlpha = 0.7 + ledSine * 0.3;
                ctx.beginPath();
                ctx.arc(x0 + 8, node.y, 2.5, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(16, 185, 129, ${ledAlpha})`;
                ctx.shadowColor = '#10b981';
                ctx.shadowBlur = 6;
                ctx.fill();
                ctx.shadowBlur = 0;

                // Node Monospace Typography
                ctx.fillStyle = '#ffffff';
                ctx.font = `bold ${isMobile ? '8px' : '9.5px'} "JetBrains Mono", "Fira Code", monospace`;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'middle';
                ctx.fillText(node.label, x0 + 15, node.y - (isMobile ? 0 : 4));

                // Micro Status Subtext (Desktop only)
                if (!isMobile) {
                    ctx.fillStyle = 'rgba(148, 163, 184, 0.75)';
                    ctx.font = '7.5px "JetBrains Mono", monospace';
                    ctx.fillText(node.sub, x0 + 15, node.y + 7);
                }

                ctx.restore();
            });

            // 8. Interactive Diagnostic Scanner Reticle (Mengikuti Kursor Mouse & Sentuhan)
            if (pointer.isActive && pointer.x !== null) {
                ctx.save();
                ctx.translate(pointer.x, pointer.y);

                // Rotating Dashed Target Ring
                ctx.rotate(pointer.reticleAngle);
                ctx.beginPath();
                ctx.arc(0, 0, isMobile ? 22 : 30, 0, Math.PI * 2);
                ctx.strokeStyle = 'rgba(6, 182, 212, 0.55)';
                ctx.lineWidth = 1;
                ctx.setLineDash([4, 6]);
                ctx.stroke();

                // Crosshair brackets
                ctx.setLineDash([]);
                ctx.rotate(-pointer.reticleAngle); // reset rotation for static crosshair
                const chSize = isMobile ? 12 : 16;
                const chGap = 6;
                ctx.strokeStyle = 'rgba(99, 102, 241, 0.7)';
                ctx.lineWidth = 1.2;

                // Top
                ctx.beginPath();
                ctx.moveTo(0, -chSize);
                ctx.lineTo(0, -chGap);
                // Bottom
                ctx.moveTo(0, chGap);
                ctx.lineTo(0, chSize);
                // Left
                ctx.moveTo(-chSize, 0);
                ctx.lineTo(-chGap, 0);
                // Right
                ctx.moveTo(chGap, 0);
                ctx.lineTo(chSize, 0);
                ctx.stroke();

                // Central Focus Dot
                ctx.beginPath();
                ctx.arc(0, 0, 2, 0, Math.PI * 2);
                ctx.fillStyle = '#38bdf8';
                ctx.shadowColor = '#06b6d4';
                ctx.shadowBlur = 8;
                ctx.fill();
                ctx.shadowBlur = 0;

                // HUD Diagnostic Readout next to reticle (Desktop only)
                if (!isMobile) {
                    ctx.font = '8px "JetBrains Mono", monospace';
                    ctx.fillStyle = 'rgba(56, 189, 248, 0.75)';
                    ctx.textAlign = 'left';
                    ctx.fillText('DIAGNOSTIC_PROBE // LIVE', 36, -8);
                    ctx.fillStyle = 'rgba(148, 163, 184, 0.65)';
                    ctx.fillText(`BUS_TRACE: ACTIVE // X:${Math.round(pointer.x)} Y:${Math.round(pointer.y)}`, 36, 4);
                }

                ctx.restore();
            }

            animationFrameId = requestAnimationFrame(animate);
        }

        animationFrameId = requestAnimationFrame(animate);

        // Battery Guard: Immediately halt canvas render loop when tab is hidden or minimized
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
        document.addEventListener('DOMContentLoaded', initACDArchitectureBlueprint);
    } else {
        initACDArchitectureBlueprint();
    }
})();
