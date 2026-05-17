/* ============================================================
   DEEPMANI — Three.js 3D Background v2
   Neural particle network + Aurora wave ribbons
   Full mouse / touch / gyroscope reactivity
   ============================================================ */

const ThreeBG = (() => {
  let scene, camera, renderer;
  let pointsMesh, linesMesh;
  let auroraGroup;
  let targetX = 0, targetY = 0;
  let smoothX = 0, smoothY = 0;
  let isMobile = false;
  let clock = 0;

  let PARTICLE_COUNT, CONNECTION_DISTANCE;
  const particleData = [];

  /* ── INIT ─────────────────────────────────────────────── */
  function init(containerId = 'three-canvas') {
    const container = document.getElementById(containerId);
    if (!container) return;

    isMobile = window.innerWidth < 768;
    PARTICLE_COUNT = isMobile ? 55 : 120;
    CONNECTION_DISTANCE = isMobile ? 110 : 155;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 2000);
    camera.position.z = 650;

    renderer = new THREE.WebGLRenderer({ antialias: !isMobile, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, isMobile ? 1.5 : 2));
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);

    createParticleNetwork();
    createAuroraWaves();

    window.addEventListener('resize', onResize);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('touchmove', onTouchMove, { passive: true });
    document.addEventListener('scroll', onScroll);

    if (isMobile && window.DeviceOrientationEvent) {
      window.addEventListener('deviceorientation', onGyro, true);
    }

    animate();
  }

  /* ── PARTICLE NETWORK ─────────────────────────────────── */
  function createParticleNetwork() {
    const geo = new THREE.BufferGeometry();
    const positions = new Float32Array(PARTICLE_COUNT * 3);
    const colors    = new Float32Array(PARTICLE_COUNT * 3);
    const spread    = isMobile ? 0.65 : 1;

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const x = (Math.random() - 0.5) * 1400 * spread;
      const y = (Math.random() - 0.5) * 900  * spread;
      const z = (Math.random() - 0.5) * 400;
      positions[i*3] = x; positions[i*3+1] = y; positions[i*3+2] = z;
      particleData.push({
        vx: (Math.random() - 0.5) * 0.28,
        vy: (Math.random() - 0.5) * 0.28,
        vz: (Math.random() - 0.5) * 0.08,
      });

      const t = Math.random();
      if (t < 0.60)      { colors[i*3]=0.85; colors[i*3+1]=0.68; colors[i*3+2]=0.22; }
      else if (t < 0.85) { colors[i*3]=0.25; colors[i*3+1]=0.88; colors[i*3+2]=0.82; }
      else               { colors[i*3]=0.9;  colors[i*3+1]=0.9;  colors[i*3+2]=0.9;  }
    }

    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color',    new THREE.BufferAttribute(colors, 3));

    pointsMesh = new THREE.Points(geo, new THREE.PointsMaterial({
      size: isMobile ? 2.2 : 3.2,
      vertexColors: true, transparent: true, opacity: 0.9, sizeAttenuation: true
    }));
    scene.add(pointsMesh);

    const lineGeo = new THREE.BufferGeometry();
    const maxSegs = PARTICLE_COUNT * PARTICLE_COUNT;
    const lp = new Float32Array(maxSegs * 6);
    const lc = new Float32Array(maxSegs * 6);
    lineGeo.setAttribute('position', new THREE.BufferAttribute(lp, 3).setUsage(THREE.DynamicDrawUsage));
    lineGeo.setAttribute('color',    new THREE.BufferAttribute(lc, 3).setUsage(THREE.DynamicDrawUsage));
    lineGeo.setDrawRange(0, 0);
    linesMesh = new THREE.LineSegments(lineGeo, new THREE.LineBasicMaterial({
      vertexColors: true, transparent: true, opacity: isMobile ? 0.22 : 0.35
    }));
    scene.add(linesMesh);
  }

  /* ── AURORA WAVES (elegant replacement for geometry) ──── */
  function createAuroraWaves() {
    auroraGroup = new THREE.Group();

    const configs = [
      { color: 0xC9A84C, y: -180, z: -300, w: 2000, h: 130, op: 0.045, ph: 0.0   },
      { color: 0x40E0D0, y:  100, z: -420, w: 2200, h:  95, op: 0.032, ph: 1.2   },
      { color: 0x8B6914, y:  260, z: -260, w: 1800, h: 110, op: 0.038, ph: 2.4   },
      { color: 0xC9A84C, y: -350, z: -370, w: 2400, h:  75, op: 0.022, ph: 3.6   },
      { color: 0x40E0D0, y:  420, z: -480, w: 1600, h:  60, op: 0.018, ph: 0.7   },
    ];

    configs.forEach((cfg, idx) => {
      const segs = isMobile ? 40 : 90;
      const geo = new THREE.PlaneGeometry(cfg.w, cfg.h, segs, 1);
      const mat = new THREE.MeshBasicMaterial({
        color: cfg.color, transparent: true, opacity: cfg.op,
        side: THREE.DoubleSide, depthWrite: false,
      });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(0, cfg.y, cfg.z);
      mesh.rotation.x = -0.12 + idx * 0.07;
      mesh.userData = { baseY: cfg.y, phase: cfg.ph, baseOp: cfg.op };
      auroraGroup.add(mesh);
    });

    scene.add(auroraGroup);
  }

  /* ── UPDATE PARTICLE CONNECTIONS ─────────────────────── */
  function updateConnections() {
    const pa = pointsMesh.geometry.getAttribute('position');
    const lp = linesMesh.geometry.getAttribute('position');
    const lc = linesMesh.geometry.getAttribute('color');
    let idx = 0;
    const MAX = PARTICLE_COUNT * PARTICLE_COUNT / 2;

    for (let i = 0; i < PARTICLE_COUNT && idx < MAX; i++) {
      for (let j = i + 1; j < PARTICLE_COUNT && idx < MAX; j++) {
        const dx = pa.getX(i)-pa.getX(j), dy = pa.getY(i)-pa.getY(j), dz = pa.getZ(i)-pa.getZ(j);
        const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
        if (dist < CONNECTION_DISTANCE) {
          const a = (1 - dist / CONNECTION_DISTANCE) * 0.85;
          lp.setXYZ(idx*2,   pa.getX(i), pa.getY(i), pa.getZ(i));
          lp.setXYZ(idx*2+1, pa.getX(j), pa.getY(j), pa.getZ(j));
          lc.setXYZ(idx*2,   0.85*a, 0.68*a, 0.22*a);
          lc.setXYZ(idx*2+1, 0.85*a, 0.68*a, 0.22*a);
          idx++;
        }
      }
    }
    linesMesh.geometry.setDrawRange(0, idx * 2);
    lp.needsUpdate = true; lc.needsUpdate = true;
  }

  /* ── ANIMATION LOOP ───────────────────────────────────── */
  function animate() {
    requestAnimationFrame(animate);
    clock += 0.01;

    const lerpAmt = isMobile ? 0.09 : 0.055;
    smoothX += (targetX - smoothX) * lerpAmt;
    smoothY += (targetY - smoothY) * lerpAmt;

    const pa = pointsMesh.geometry.getAttribute('position');
    const bX = isMobile ? 455 : 700;
    const bY = isMobile ? 295 : 450;
    const mousePush = isMobile ? 0.00022 : 0.00020;

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const d = particleData[i];
      let x = pa.getX(i) + d.vx + smoothX * mousePush;
      let y = pa.getY(i) + d.vy - smoothY * mousePush;
      let z = pa.getZ(i) + d.vz;
      if (x >  bX) x = -bX; if (x < -bX) x = bX;
      if (y >  bY) y = -bY; if (y < -bY) y = bY;
      if (z >  200) z = -200; if (z < -200) z = 200;
      pa.setXYZ(i, x, y, z);
    }
    pa.needsUpdate = true;
    updateConnections();

    /* Animate aurora ribbons */
    auroraGroup.children.forEach((mesh) => {
      const { phase, baseY } = mesh.userData;
      const vpos = mesh.geometry.getAttribute('position');
      for (let i = 0; i < vpos.count; i++) {
        const ox = mesh.geometry.getAttribute('position').getX(i);
        const wave =
          Math.sin(ox * 0.0028 + clock * 2.2 + phase) * 24 +
          Math.sin(ox * 0.0055 + clock * 1.6 + phase * 1.4) * 13 +
          Math.sin(clock * 1.1 + phase * 0.6) * 7;
        const curY = vpos.getY(i);
        vpos.setY(i, curY + (wave - curY) * 0.035);
      }
      vpos.needsUpdate = true;
      mesh.position.y = baseY + Math.sin(clock * 0.6 + phase) * 16;
      mesh.rotation.z = smoothX * 0.000035;
    });

    /* Camera parallax — strong, smooth, reactive */
    const camStrength = isMobile ? 0.05 : 0.09;
    camera.position.x += (smoothX * camStrength - camera.position.x) * 0.028;
    camera.position.y += (-smoothY * camStrength - camera.position.y) * 0.028;
    camera.lookAt(scene.position);

    renderer.render(scene, camera);
  }

  /* ── EVENT HANDLERS ───────────────────────────────────── */
  function onMouseMove(e) {
    targetX = e.clientX - window.innerWidth  / 2;
    targetY = e.clientY - window.innerHeight / 2;
  }

  function onTouchMove(e) {
    if (!e.touches[0]) return;
    targetX = e.touches[0].clientX - window.innerWidth  / 2;
    targetY = e.touches[0].clientY - window.innerHeight / 2;
  }

  function onGyro(e) {
    if (e.gamma !== null) targetX = e.gamma * 14;
    if (e.beta  !== null) targetY = (e.beta - 45) * 9;
  }

  function onScroll() {
    const sy = window.scrollY;
    if (pointsMesh) pointsMesh.material.opacity = Math.max(0.12, 0.9 - sy * 0.0007);
    if (linesMesh)  linesMesh.material.opacity  = Math.max(0.04, 0.35 - sy * 0.0003);
    auroraGroup.children.forEach(m => {
      m.material.opacity = Math.max(0.004, m.userData.baseOp - sy * 0.000025);
    });
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
