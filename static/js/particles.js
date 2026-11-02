/**
 * ACD Tech Particle Network (Deptech Digital Style Constellation)
 * Floating nodes connected by dynamic lines with subtle mouse interaction
 */
function initParticleNetwork(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width = canvas.width = canvas.parentElement.offsetWidth;
    let height = canvas.height = canvas.parentElement.offsetHeight;

    let particles = [];
    // Responsive particle count: ~35 on mobile, ~55 on tablet, ~80 on desktop
    const particleCount = window.innerWidth < 768 ? 35 : (window.innerWidth < 1200 ? 55 : 80);
    const maxDistance = 140; // connection line distance
    const mouseDistance = 160;

    let mouse = {
        x: null,
        y: null,
        radius: mouseDistance
    };

    window.addEventListener('resize', () => {
        if (!canvas.parentElement) return;
        width = canvas.width = canvas.parentElement.offsetWidth;
        height = canvas.height = canvas.parentElement.offsetHeight;
    });

    const parent = canvas.parentElement;
    parent.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        mouse.x = e.clientX - rect.left;
        mouse.y = e.clientY - rect.top;
    });

    parent.addEventListener('mouseleave', () => {
        mouse.x = null;
        mouse.y = null;
    });

    // Particle colors: Indigo, Cyan, Violet, Soft Blue
    const colors = [
        'rgba(99, 102, 241, ',   // Indigo #6366f1
        'rgba(56, 189, 248, ',   // Cyan #38bdf8
        'rgba(168, 85, 247, ',   // Violet #a855f7
        'rgba(129, 140, 248, '   // Soft blue #818cf8
    ];

    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.size = Math.random() * 2 + 1.2; // 1.2px - 3.2px
            this.speedX = (Math.random() - 0.5) * 0.8;
            this.speedY = (Math.random() - 0.5) * 0.8;
            this.colorPrefix = colors[Math.floor(Math.random() * colors.length)];
            this.alpha = Math.random() * 0.5 + 0.4; // 0.4 - 0.9
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            // Bounce off edges smoothly
            if (this.x < 0 || this.x > width) this.speedX = -this.speedX;
            if (this.y < 0 || this.y > height) this.speedY = -this.speedY;

            // Mouse interaction
            if (mouse.x !== null && mouse.y !== null) {
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < mouse.radius) {
                    const force = (mouse.radius - dist) / mouse.radius;
                    const directionX = dx / dist;
                    const directionY = dy / dist;
                    this.x -= directionX * force * 1.5;
                    this.y -= directionY * force * 1.5;
                }
            }
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = this.colorPrefix + this.alpha + ')';
            ctx.shadowBlur = 8;
            ctx.shadowColor = this.colorPrefix + '0.8)';
            ctx.fill();
            ctx.shadowBlur = 0; // reset
        }
    }

    // Initialize particles
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }

    // Connect particles with straight lines
    function connect() {
        for (let a = 0; a < particles.length; a++) {
            for (let b = a + 1; b < particles.length; b++) {
                const dx = particles[a].x - particles[b].x;
                const dy = particles[a].y - particles[b].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < maxDistance) {
                    const opacity = (1 - distance / maxDistance) * 0.28;
                    ctx.strokeStyle = `rgba(99, 102, 241, ${opacity})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(particles[a].x, particles[a].y);
                    ctx.lineTo(particles[b].x, particles[b].y);
                    ctx.stroke();
                }
            }

            // Connect to mouse
            if (mouse.x !== null && mouse.y !== null) {
                const dx = particles[a].x - mouse.x;
                const dy = particles[a].y - mouse.y;
                const mouseDist = Math.sqrt(dx * dx + dy * dy);
                if (mouseDist < mouseDistance) {
                    const opacity = (1 - mouseDist / mouseDistance) * 0.45;
                    ctx.strokeStyle = `rgba(56, 189, 248, ${opacity})`;
                    ctx.lineWidth = 1.2;
                    ctx.beginPath();
                    ctx.moveTo(particles[a].x, particles[a].y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.stroke();
                }
            }
        }
    }

    // Animation Loop
    function animate() {
        ctx.clearRect(0, 0, width, height);
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();
        }
        connect();
        requestAnimationFrame(animate);
    }

    animate();
}

document.addEventListener('DOMContentLoaded', () => {
    initParticleNetwork('hero-particle-canvas');
});
