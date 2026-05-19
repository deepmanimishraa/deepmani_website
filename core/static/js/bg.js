/* ============================================================
   bg.js — Lightweight background: CSS-only orbs + scroll parallax
   Zero canvas, zero WebGL, zero heavy libs.
   ============================================================ */

(function () {
  /* Subtle scroll parallax on hero orbs */
  const orbs = document.querySelectorAll('.bg-orb');
  let ticking = false;

  function onScroll() {
    if (!ticking) {
      requestAnimationFrame(() => {
        const y = window.scrollY;
        orbs.forEach((orb, i) => {
          const speed = (i % 2 === 0) ? 0.12 : 0.08;
          orb.style.transform = `translateY(${y * speed}px)`;
        });
        ticking = false;
      });
      ticking = true;
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });

  /* Subtle mouse-tracking glow on hero (desktop only) */
  const heroGlow = document.getElementById('hero-mouse-glow');
  if (heroGlow && window.matchMedia('(pointer:fine)').matches) {
    document.addEventListener('mousemove', (e) => {
      const x = (e.clientX / window.innerWidth)  * 100;
      const y = (e.clientY / window.innerHeight) * 100;
      heroGlow.style.background =
        `radial-gradient(600px circle at ${x}% ${y}%,
          rgba(201,168,76,0.06) 0%,
          rgba(64,224,208,0.03) 40%,
          transparent 70%)`;
    });
  }

  /* Intersection-based reveal (IntersectionObserver) */
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
})();
