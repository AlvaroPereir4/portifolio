const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');

let width, height;
let particles = [];

// Configurações
const particleCount = 80; // Aumentado ligeiramente
const connectionDistance = 160; 
const mouseDistance = 220;
const moveSpeed = 0.6; 

// Cor base (Laranja: #e87c03)
const colorR = 232;
const colorG = 124;
const colorB = 3;

let mouse = {
    x: null,
    y: null
}

window.addEventListener('mousemove', (e) => {
    mouse.x = e.x;
    mouse.y = e.y;
});

window.addEventListener('mouseout', () => {
    mouse.x = null;
    mouse.y = null;
});

function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
}

class Particle {
    constructor() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.vx = (Math.random() - 0.5) * moveSpeed;
        this.vy = (Math.random() - 0.5) * moveSpeed;
        this.size = Math.random() * 2.5 + 1; // Tamanho ligeiramente maior
        this.baseX = this.x;
        this.baseY = this.y;
        this.pulseSpeed = Math.random() * 0.05 + 0.01;
        this.pulseAngle = Math.random() * Math.PI * 2;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;

        // Efeito de pulsação no tamanho
        this.pulseAngle += this.pulseSpeed;
        const currentSize = this.size + Math.sin(this.pulseAngle) * 0.5;

        if (this.x < 0 || this.x > width) this.vx *= -1;
        if (this.y < 0 || this.y > height) this.vy *= -1;

        if (mouse.x != null) {
            let dx = mouse.x - this.x;
            let dy = mouse.y - this.y;
            let distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < mouseDistance) {
                const forceDirectionX = dx / distance;
                const forceDirectionY = dy / distance;
                const force = (mouseDistance - distance) / mouseDistance;
                const directionX = forceDirectionX * force * 2.5; // Força um pouco maior
                const directionY = forceDirectionY * force * 2.5;

                this.x += directionX;
                this.y += directionY;
            }
        }
        
        return currentSize;
    }

    draw(currentSize) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, Math.max(0.1, currentSize), 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${colorR}, ${colorG}, ${colorB}, 0.6)`;
        ctx.fill();
    }
}

function init() {
    particles = [];
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
}

function animate() {
    ctx.clearRect(0, 0, width, height);
    
    for (let i = 0; i < particles.length; i++) {
        let p = particles[i];
        const currentSize = p.update();
        p.draw(currentSize);

        for (let j = i + 1; j < particles.length; j++) {
            let p2 = particles[j];
            let dx = p.x - p2.x;
            let dy = p.y - p2.y;
            let distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < connectionDistance) {
                ctx.beginPath();
                // Opacidade baseada na distância
                const opacity = 1 - distance / connectionDistance;
                ctx.strokeStyle = `rgba(${colorR}, ${colorG}, ${colorB}, ${opacity * 0.5})`; // Linhas um pouco mais sutis
                ctx.lineWidth = 1;
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();
            }
        }

        if (mouse.x != null) {
            let dx = p.x - mouse.x;
            let dy = p.y - mouse.y;
            let distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < mouseDistance) {
                ctx.beginPath();
                const opacity = 1 - distance / mouseDistance;
                ctx.strokeStyle = `rgba(${colorR}, ${colorG}, ${colorB}, ${opacity * 0.8})`;
                ctx.lineWidth = 1.5;
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(mouse.x, mouse.y);
                ctx.stroke();
            }
        }
    }
    requestAnimationFrame(animate);
}

window.addEventListener('resize', () => {
    resize();
    init();
});

resize();
init();
animate();