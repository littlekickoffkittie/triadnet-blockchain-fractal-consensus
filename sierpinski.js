// Sierpinski Triangle Animation
class SierpinskiBackground {
  constructor() {
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
    this.scale = 1;
    this.offset = { x: 0, y: 0 };
    this.zoomSpeed = 0.002; // Smooth zoom
    this.rotation = 0;
    this.rotationSpeed = 0.0002; // Very subtle rotation
    this.opacity = 0;
    
    this.setupCanvas();
    this.fadeIn();
    this.animate();
  }

  setupCanvas() {
    document.body.insertBefore(this.canvas, document.body.firstChild);
    this.canvas.style.position = 'fixed';
    this.canvas.style.top = '0';
    this.canvas.style.left = '0';
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    this.canvas.style.zIndex = '-1';
    this.canvas.style.opacity = '0';
    this.canvas.style.filter = 'blur(1.5px) saturate(1.2)';
    this.canvas.style.transition = 'opacity 2s ease';
    
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
  }

  fadeIn() {
    setTimeout(() => {
      this.canvas.style.opacity = '0.12';
    }, 300);
  }

  resizeCanvas() {
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = window.innerWidth * dpr;
    this.canvas.height = window.innerHeight * dpr;
    this.ctx.scale(dpr, dpr);
  }

  drawTriangle(x1, y1, x2, y2, x3, y3, depth) {
    if (depth === 0) {
      this.ctx.beginPath();
      this.ctx.moveTo(x1, y1);
      this.ctx.lineTo(x2, y2);
      this.ctx.lineTo(x3, y3);
      this.ctx.closePath();
      
      // Create gradient for each triangle
      const gradient = this.ctx.createLinearGradient(x1, y1, x3, y3);
      gradient.addColorStop(0, 'rgba(0, 245, 212, 0.4)'); // --accent-teal
      gradient.addColorStop(0.5, 'rgba(0, 209, 255, 0.4)'); // --accent-blue
      gradient.addColorStop(1, 'rgba(155, 81, 224, 0.4)'); // --accent-purple
      
      this.ctx.strokeStyle = gradient;
      this.ctx.stroke();

      // Add subtle glow effect
      this.ctx.shadowColor = 'rgba(0, 209, 255, 0.15)';
      this.ctx.shadowBlur = 3;
      return;
    }

    const x12 = (x1 + x2) / 2;
    const y12 = (y1 + y2) / 2;
    const x23 = (x2 + x3) / 2;
    const y23 = (y2 + y3) / 2;
    const x31 = (x3 + x1) / 2;
    const y31 = (y3 + y1) / 2;

    this.drawTriangle(x1, y1, x12, y12, x31, y31, depth - 1);
    this.drawTriangle(x12, y12, x2, y2, x23, y23, depth - 1);
    this.drawTriangle(x31, y31, x23, y23, x3, y3, depth - 1);
  }

  draw() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    this.ctx.lineWidth = 0.5; // Thinner lines for more delicate appearance
    
    const size = Math.min(this.canvas.width, this.canvas.height) * this.scale;
    const centerX = this.canvas.width / 2 + this.offset.x;
    const centerY = this.canvas.height / 2 + this.offset.y;
    
    // Apply rotation
    this.ctx.save();
    this.ctx.translate(centerX, centerY);
    this.ctx.rotate(this.rotation);
    this.ctx.translate(-centerX, -centerY);
    
    // Draw multiple triangles with different sizes for depth effect
    for (let i = 0; i < 4; i++) {
      const scaleFactor = 1 + (i * 0.4);
      const x1 = centerX;
      const y1 = centerY - (size * scaleFactor) / 2;
      const x2 = centerX - (size * scaleFactor) / 2;
      const y2 = centerY + (size * scaleFactor) / 2;
      const x3 = centerX + (size * scaleFactor) / 2;
      const y3 = centerY + (size * scaleFactor) / 2;

      this.drawTriangle(x1, y1, x2, y2, x3, y3, 5); // Balanced depth for performance
    }
    
    this.ctx.restore();
  }

  animate() {
    this.scale *= (1 + this.zoomSpeed);
    this.rotation += this.rotationSpeed;
    
    if (this.scale > 4) {
      this.scale = 1;
    }
    
    this.draw();
    requestAnimationFrame(() => this.animate());
  }
}

// Initialize the background when the document is loaded
document.addEventListener('DOMContentLoaded', () => {
  new SierpinskiBackground();
});
