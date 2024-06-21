const canvas = document.getElementById('particleCanvas');
const ctx = canvas.getContext('2d');

let canvasWidth = window.innerWidth;
let canvasHeight = window.innerHeight;
canvas.width = canvasWidth;
canvas.height = canvasHeight;

let particles = [];
let particleCount = calculateParticleCount();

let angle = Math.PI / 4;

const bgCanvas = document.createElement('canvas');
const bgCtx = bgCanvas.getContext('2d');
bgCanvas.width = canvasWidth;
bgCanvas.height = canvasHeight;

const fgCanvas = document.createElement('canvas');
const fgCtx = fgCanvas.getContext('2d');
fgCanvas.width = canvasWidth;
fgCanvas.height = canvasHeight;

drawBackground(bgCtx);
drawForeground(fgCtx);

class Particle {
    constructor() {
        this.reset();
        this.fadeDelay = Math.random() * 600 + 100;
        this.fadeStart = Date.now() + this.fadeDelay;
        this.fadingOut = false;
        this.updateInterval = Math.random() * 10 + 5;
        this.lastUpdate = Date.now();
        this.trailLength = 20;
        this.trail = [];
    }

    reset() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.speed = Math.random() / 0.5 + 0.5;
        this.opacity = 1;
        this.fadeDelay = Math.random() * 600 + 100;
        this.fadeStart = Date.now() + this.fadeDelay;
        this.fadingOut = false;
        this.trail = [];
    }

    update() {
        const now = Date.now();
        const delta = now - this.lastUpdate;

        if (delta < this.updateInterval) {
            return;
        }

        this.lastUpdate = now;

        this.x += Math.cos(angle) * this.speed;
        this.y += Math.sin(angle) * this.speed;

        if (this.y > canvas.height) {
            this.reset();
        }

        if (!this.fadingOut && Date.now() > this.fadeStart) {
            this.fadingOut = true;
        }

        if (this.fadingOut) {
            this.opacity -= 0.002;
            if (this.opacity <= 0) {
                this.reset();
            }
        }

        this.trail.push({ x: this.x, y: this.y });
        if (this.trail.length > this.trailLength) {
            this.trail.shift();
        }
    }

    draw() {
        for (let i = 0; i < this.trail.length; i++) {
            const alpha = (i / this.trail.length) * (this.opacity * 0.5); // Reduce opacity
            ctx.fillStyle = `rgba(${255 - (Math.random() * 255/2)}, 255, 255, ${alpha})`;
            ctx.fillRect(this.trail[i].x, this.trail[i].y, 1, 1);
        }

        ctx.fillStyle = `rgba(${255 - (Math.random() * 255/2)}, 255, 255, ${this.opacity})`;
        ctx.fillRect(this.x, this.y, 1, 1);
    }
}

function calculateParticleCount() {
    return Math.floor((canvas.width * canvas.height) / 5000);
}

function drawBackground(ctx) {
    const background = new Image();
    background.src = "/static/images/sky.png";
    background.onload = () => {
        ctx.drawImage(background, 0, 0, canvasWidth, canvasHeight);
        drawForeground(fgCtx, offsetX, offsetY);
    };
}

function drawForeground(ctx, offsetX, offsetY) {
    const foreground = new Image();
    foreground.src = "/static/images/mountains.png";
    foreground.onload = () => {
        ctx.clearRect(0, 0, canvasWidth, canvasHeight);
        const centerX = canvasWidth / 2;
        const centerY = canvasHeight / 2;

        const imageWidth = foreground.width * zoom * 0.8;
        const imageHeight = foreground.height * zoom * 0.8;

        const drawX = centerX - imageWidth / 2 + offsetX;
        const drawY = centerY - imageHeight / 2 + offsetY;

        ctx.drawImage(foreground, drawX, drawY, imageWidth, imageHeight);
    };
}


function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw background from off-screen canvas
    ctx.drawImage(bgCanvas, 0, 0);

    particles.forEach(particle => {
        particle.update();
        particle.draw();
    });

    // Draw foreground from off-screen canvas
    ctx.drawImage(fgCanvas, 0, 0);

    requestAnimationFrame(animate);
}

function onResize() {
    canvasWidth = window.innerWidth;
    canvasHeight = window.innerHeight;
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    bgCanvas.width = canvasWidth;
    bgCanvas.height = canvasHeight;
    fgCanvas.width = canvasWidth;
    fgCanvas.height = canvasHeight;
    particleCount = calculateParticleCount();
    initParticles();
    drawBackground(bgCtx);
    drawForeground(fgCtx, offsetX, offsetY);
}

let zoom = 1;
let offsetX = 0;
let offsetY = 0;

let fgVelocityX = 0;
let fgVelocityY = 0;
const friction = 0.85; // Adjust friction for smooth movement

function handleMouseMove(event) {
    const mouseX = event.clientX;
    const mouseY = event.clientY;

    // Calculate the distance from the mouse pointer to the center of the canvas
    const centerX = canvasWidth / 2;
    const centerY = canvasHeight / 2;
    const distanceX = mouseX - centerX;
    const distanceY = mouseY - centerY;

    // Calculate the maximum distance from the center of the canvas
    const maxDistance = Math.sqrt(centerX * centerX + centerY * centerY);

    // Calculate the zoom based on the ratio of the distance from the center to the maximum distance
    const zoomFactor = Math.min(1, Math.sqrt(distanceX * distanceX + distanceY * distanceY) / maxDistance);
    const smoothFactor = 0.005; // Adjust the smoothness factor to make it very subtle
    const targetZoom = 1 + zoomFactor * 0.05; // Adjust the zoom factor to make it very subtle
    zoom += (targetZoom - zoom) * smoothFactor;

    // Calculate the new offset for the foreground image
    const targetOffsetX = -((mouseX - canvasWidth / 2) / 70) * zoom; // Reverse the direction for X-axis
    const targetOffsetY = -((mouseY - canvasHeight / 2) / 70) * zoom; // Reverse the direction for Y-axis

    // Add velocity for smoother movement
    fgVelocityX += (targetOffsetX - offsetX) * 0.01;
    fgVelocityY += (targetOffsetY - offsetY) * 0.01;

    // Apply friction to velocity
    fgVelocityX *= friction;
    fgVelocityY *= friction;

    // Update foreground offset with velocity
    offsetX += fgVelocityX;
    offsetY += fgVelocityY;

    // Redraw foreground based on mouse movement and zoom
    drawForeground(fgCtx, offsetX, offsetY);
}



window.addEventListener('resize', onResize);
document.addEventListener('mousemove', handleMouseMove);

function initParticles() {
    particles = [];
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
}

initParticles();
animate();
drawForeground(fgCtx, 0, 0);
