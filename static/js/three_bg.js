/* ============================================================
   DEEPMANI — Premium Cinematic Embers UI
   Lightweight, highly optimized, non-blocking 3D background
   ============================================================ */

const ThreeBG = (() => {
  let scene, camera, renderer, particles;
  let mouseX = 0, mouseY = 0;
  let targetX = 0, targetY = 0;
  let isMobile = false;

  function init(containerId = 'three-canvas') {
    const container = document.getElementById(containerId);
    if (!container) return;

    isMobile = window.innerWidth < 768;

    // 1. Scene & Camera setup
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 1000);
    camera.position.z = 300;

    // 2. Renderer (Transparent, optimized)
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: false });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(isMobile ? 1 : Math.min(window.devicePixelRatio, 2));
    
    // CRITICAL FIX: Force the canvas to be an absolute ghost layer.
    // It sits behind everything and lets all touches pass through to the HTML.
    renderer.domElement.style.position = 'fixed';
    renderer.domElement.style.top = '0';
    renderer.domElement.style.left = '0';
    renderer.domElement.style.pointerEvents = 'none';
    renderer.domElement.style.zIndex = '-1';

    container.appendChild(renderer.domElement);

    // 3. Generate Soft Glowing Texture (No external images needed)
    const canvas = document.createElement('canvas');
    canvas.width = 32; canvas.height = 32;
    const ctx = canvas.getContext('2d');
    const gradient = ctx.createRadialGradient(16, 16, 0, 16, 16, 16);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');       // White core
    gradient.addColorStop(0.2, 'rgba(201, 168, 76, 0.8)');    // Gold inner glow
    gradient.addColorStop(0.5, 'rgba(201, 168, 76, 0.2)');    // Gold outer glow
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');             // Fade out
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 32, 32);
    const texture = new THREE.CanvasTexture(canvas);

    // 4. Create Particles (Embers)
    const particleCount = isMobile ? 80 : 200;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const velocities = [];

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 800;       // x
      positions[i * 3 + 1] = (Math.random() - 0.5) * 800;   // y
      positions[i * 3 + 2] = (Math.random() - 0.5) * 400;   // z
      
      velocities.push({
        y: Math.random() * 0.4 + 0.1,  // Float up speed
        x: (Math.random() - 0.5) * 0.2 // Gentle horizontal sway
      });
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const material = new THREE.PointsMaterial({
      size: isMobile ? 6 : 8,
      map: texture,
      transparent: true,
      opacity: 0.6,
      depthWrite: false,
      blending: THREE.AdditiveBlending // Creates a cinematic bloom effect
    });

    particles = new THREE.Points(geometry, material);
    scene.add(particles);

    // 5. Event Listeners for subtle parallax (Mouse only, no touch blocks)
    window.addEventListener('resize', onResize);
    if (!isMobile) {
      window.addEventListener('mousemove', (e) => {
        targetX = (e.clientX - window.innerWidth / 2) * 0.05;
        targetY = (e.clientY - window.innerHeight / 2) * 0.05;
      });
    }

    animate();
  }

  function animate() {
    requestAnimationFrame(animate);

    // Smooth camera parallax
    mouseX += (targetX - mouseX) * 0.05;
    mouseY += (targetY - mouseY) * 0.05;
    camera.position.x = mouseX;
    camera.position.y = -mouseY;
    camera.lookAt(scene.position);

    // Float particles upwards gently
    const positions = particles.geometry.attributes.position.array;
    for (let i = 0; i < positions.length / 3; i++) {
      positions[i * 3 + 1] += velocities[i].y; // Move up
      positions[i * 3] += velocities[i].x;     // Sway sideways

      // If particle floats past the top, loop it back to the bottom
      if (positions[i * 3 + 1] > 400) {
        positions[i * 3 + 1] = -400;
        positions[i * 3] = (Math.random() - 0.5) * 800;
      }
    }
    particles.geometry.attributes.position.needsUpdate = true;

    renderer.render(scene, camera);
  }

  function onResize() {
    isMobile = window.innerWidth < 768;
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }

  return { init };
})();

document.addEventListener('DOMContentLoaded', () => ThreeBG.init('three-canvas'));