/* ============================================================
   DEEPMANI MISHRAA — Main Frontend JS v2
   Custom cursor · Navbar · Journey scroll · Gallery · AI · Contact
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ── CUSTOM CURSOR (desktop only) ──────────────────────────── */
  const $cursor    = document.getElementById('cursor');
  const $cursorDot = document.getElementById('cursor-dot');
  let curX = 0, curY = 0, dotX = 0, dotY = 0;

  if (window.matchMedia('(pointer:fine)').matches && $cursor) {
    document.addEventListener('mousemove', e => {
      curX = e.clientX; curY = e.clientY;
      $cursorDot.style.transform = `translate(${curX - 4}px,${curY - 4}px)`;
    });
    (function animCursor() {
      dotX += (curX - dotX) * 0.12;
      dotY += (curY - dotY) * 0.12;
      $cursor.style.transform = `translate(${dotX - 20}px,${dotY - 20}px)`;
      requestAnimationFrame(animCursor);
    })();
    document.querySelectorAll('a,button,[data-hover]').forEach(el => {
      el.addEventListener('mouseenter', () => $cursor.classList.add('hover'));
      el.addEventListener('mouseleave', () => $cursor.classList.remove('hover'));
    });
  }

  /* ── NAVBAR ────────────────────────────────────────────────── */
  const $navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    $navbar.classList.toggle('scrolled', window.scrollY > 80);
  }, { passive: true });

  /* ── MOBILE MENU ───────────────────────────────────────────── */
  const $mBtn  = document.getElementById('mobile-menu-btn');
  const $mMenu = document.getElementById('mobile-menu');

  function closeMobileMenu() {
    if (!$mMenu) return;
    $mMenu.classList.remove('open');
    if ($mBtn) { $mBtn.textContent = '☰'; $mBtn.setAttribute('aria-expanded', 'false'); }
    document.body.style.overflow = '';
  }

  if ($mBtn && $mMenu) {
    $mBtn.addEventListener('click', e => {
      e.stopPropagation();
      const isOpen = $mMenu.classList.toggle('open');
      $mBtn.setAttribute('aria-expanded', String(isOpen));
      $mMenu.setAttribute('aria-hidden', String(!isOpen));
      $mBtn.textContent = isOpen ? '✕' : '☰';
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });

    $mMenu.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', closeMobileMenu);
    });

    document.addEventListener('click', e => {
      if ($mMenu.classList.contains('open') &&
          !$mMenu.contains(e.target) && e.target !== $mBtn) {
        closeMobileMenu();
      }
    });

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeMobileMenu();
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        e.preventDefault();
        const offset = 72; 
        const y = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top: y, behavior: 'smooth' });
      }
    });
  });

  /* ── INTERSECTION OBSERVER — REVEAL ANIMATIONS ────────────── */
  const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('revealed');
        revealObserver.unobserve(e.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

  document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

  /* ── TYPED HERO TEXT ───────────────────────────────────────── */
  const $typed = document.getElementById('typed-text');
  if ($typed) {
    const phrases = [
      'Data Scientist', 'IIT Madras Scholar',
      'Cybersecurity Founder', 'ML Engineer',
      'Tech Visionary', 'Co-Founder @ PRAMANIIK'
    ];
    let pIdx = 0, cIdx = 0, deleting = false;
    function typeLoop() {
      const phrase = phrases[pIdx];
      if (!deleting) {
        $typed.textContent = phrase.slice(0, ++cIdx);
        if (cIdx === phrase.length) { deleting = true; setTimeout(typeLoop, 2200); return; }
      } else {
        $typed.textContent = phrase.slice(0, --cIdx);
        if (cIdx === 0) { deleting = false; pIdx = (pIdx + 1) % phrases.length; }
      }
      setTimeout(typeLoop, deleting ? 55 : 85);
    }
    setTimeout(typeLoop, 500);
  }

 /* ── JOURNEY TIMELINE — DESKTOP DRAG & MOBILE CSS SCROLL ────── */
  const $track = document.getElementById('timeline-track');

  if ($track) {
    fetch('/api/journey/list')
      .then(r => r.json())
      .then(entries => {
        $track.innerHTML = '';
        const icons = { rocket:'🚀', graduation:'🎓', shield:'🛡️', globe:'🌐', star:'⭐', code:'💻', award:'🏆' };
        entries.forEach((e, i) => {
          const card = document.createElement('article');
          card.className = 'timeline-card reveal';
          card.innerHTML = `
            <div class="timeline-category">${e.category}</div>
            <div class="timeline-icon">${icons[e.icon] || '⭐'}</div>
            <div class="timeline-year">${e.year}</div>
            <div class="timeline-content">
              <h3>${e.title}</h3>
              <p>${e.description || ''}</p>
            </div>`;
          $track.appendChild(card);
          
          if (typeof revealObserver !== 'undefined') {
              revealObserver.observe(card);
          }
        });
      })
      .catch(() => {
        $track.innerHTML = '<div class="timeline-card" style="flex:0 0 290px;display:flex;align-items:center;justify-content:center;"><span style="color:var(--text-dim)">Could not load journey</span></div>';
      });

    /* Hardware-Strict Drag: ONLY activates for a physical mouse */
    let isDown = false;
    let startX;
    let scrollLeft;

    $track.addEventListener('pointerdown', (e) => {
      // If it's a finger touching the screen, IGNORE IT and let CSS handle the scroll
      if (e.pointerType !== 'mouse') return; 
      
      isDown = true;
      $track.style.cursor = 'grabbing';
      $track.style.scrollSnapType = 'none'; // Disable snapping during drag
      startX = e.pageX - $track.offsetLeft;
      scrollLeft = $track.scrollLeft;
    });

    $track.addEventListener('pointerleave', (e) => {
      if (e.pointerType !== 'mouse') return;
      isDown = false;
      $track.style.cursor = 'grab';
      $track.style.scrollSnapType = 'x mandatory';
    });

    $track.addEventListener('pointerup', (e) => {
      if (e.pointerType !== 'mouse') return;
      isDown = false;
      $track.style.cursor = 'grab';
      $track.style.scrollSnapType = 'x mandatory';
    });

    $track.addEventListener('pointermove', (e) => {
      // If the mouse isn't clicked down, OR if it's a touch screen, do nothing
      if (!isDown || e.pointerType !== 'mouse') return; 
      
      e.preventDefault(); // Prevent text highlighting while dragging with mouse
      const x = e.pageX - $track.offsetLeft;
      const walk = (x - startX) * 1.5; // Scroll speed
      $track.scrollLeft = scrollLeft - walk;
    });
  }

  /* ── GALLERY ───────────────────────────────────────────────── */
  const $galleryGrid = document.getElementById('gallery-grid');
  const $galleryModal = document.getElementById('gallery-modal');
  const $commentModal = document.getElementById('comment-modal');
  let galleryPage = 1, galleryLoading = false, galleryHasMore = true;

  function loadGallery(page = 1) {
    if (galleryLoading || !galleryHasMore || !$galleryGrid) return;
    galleryLoading = true;
    const $loader = document.getElementById('gallery-loading');
    if ($loader) $loader.style.display = 'block';

    fetch(`/gallery/api/list?page=${page}`)
      .then(r => r.json())
      .then(data => {
        if (page === 1) $galleryGrid.innerHTML = '';
        data.images.forEach(img => {
          const card = document.createElement('div');
          card.className = 'gallery-card reveal';
          card.innerHTML = `
            <div class="gallery-img-wrap">
              <img src="${img.url}" alt="${img.title || ''}" loading="lazy" />
              <div class="gallery-overlay">
                <button class="like-btn ${img.liked?'liked':''}" data-id="${img.id}">
                  <span>♥</span> <span class="like-count">${img.likes}</span>
                </button>
                <button class="comment-btn" data-id="${img.id}">
                  <span>💬</span> <span class="comment-count">${img.comments}</span>
                </button>
                <button class="expand-btn" data-img='${JSON.stringify(img).replace(/'/g,"&#39;")}'>⤢</button>
              </div>
            </div>
            ${img.title    ? `<p class="gallery-caption">${img.title}</p>` : ''}
            ${img.taken_at ? `<p class="gallery-date">${img.taken_at}</p>` : ''}`;
          $galleryGrid.appendChild(card);
          revealObserver.observe(card);
        });
        galleryHasMore = data.has_next;
        galleryLoading = false;
        if ($loader) $loader.style.display = galleryHasMore ? 'block' : 'none';
      })
      .catch(() => { galleryLoading = false; });
  }

  if ($galleryGrid) {
    loadGallery();

    window.addEventListener('scroll', () => {
      if (galleryHasMore && !galleryLoading &&
          window.scrollY + window.innerHeight >= document.body.scrollHeight - 500) {
        galleryPage++; loadGallery(galleryPage);
      }
    }, { passive: true });

    $galleryGrid.addEventListener('click', e => {
      const likeBtn    = e.target.closest('.like-btn');
      const expandBtn  = e.target.closest('.expand-btn');
      const commentBtn = e.target.closest('.comment-btn');

      if (likeBtn) {
        fetch(`/gallery/api/like/${likeBtn.dataset.id}`, { method: 'POST' })
          .then(r => r.json())
          .then(d => {
            likeBtn.querySelector('.like-count').textContent = d.count;
            likeBtn.classList.toggle('liked', d.liked);
          });
      }
      if (expandBtn) {
        const img = JSON.parse(expandBtn.getAttribute('data-img'));
        openImgModal(img);
      }
      if (commentBtn) openCommentModal(commentBtn.dataset.id);
    });
  }

  function openImgModal(img) {
    if (!$galleryModal) return;
    $galleryModal.querySelector('#modal-img').src   = img.url;
    $galleryModal.querySelector('#modal-title').textContent = img.title       || '';
    $galleryModal.querySelector('#modal-desc').textContent  = img.description || '';
    $galleryModal.querySelector('#modal-date').textContent  = img.taken_at    || '';
    $galleryModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }
  
  function closeModal(el) {
    if (!el) return;
    el.classList.add('hidden');
    document.body.style.overflow = '';
  }

  if ($galleryModal) {
    $galleryModal.querySelector('.modal-close').addEventListener('click', () => closeModal($galleryModal));
    $galleryModal.addEventListener('click', e => { if (e.target === $galleryModal) closeModal($galleryModal); });
  }

  function openCommentModal(imgId) {
    if (!$commentModal) return;
    $commentModal.dataset.imgId = imgId;
    $commentModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    loadComments(imgId);
  }
  
  function loadComments(imgId) {
    const $list = document.getElementById('comments-list');
    if (!$list) return;
    fetch(`/gallery/api/comments/${imgId}`)
      .then(r => r.json())
      .then(d => {
        $list.innerHTML = d.comments.length
          ? d.comments.map(c => `
              <div class="comment-item">
                <strong>${c.name}</strong>
                <p>${c.content}</p>
                <small>${c.date}</small>
              </div>`).join('')
          : '<p style="color:var(--text-dim);font-size:.85rem;padding:.5rem 0;">No comments yet. Be the first!</p>';
      });
  }

  if ($commentModal) {
    $commentModal.querySelector('.modal-close').addEventListener('click', () => closeModal($commentModal));
    $commentModal.addEventListener('click', e => { if (e.target === $commentModal) closeModal($commentModal); });
    document.getElementById('comment-form')?.addEventListener('submit', e => {
      e.preventDefault();
      const id = $commentModal.dataset.imgId;
      const f = e.target;
      fetch(`/gallery/api/comment/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name:    f.querySelector('[name=name]').value,
          email:   f.querySelector('[name=email]').value,
          content: f.querySelector('[name=content]').value
        })
      }).then(() => { f.reset(); loadComments(id); });
    });
  }

  /* ── AI CHAT ───────────────────────────────────────────────── */
  const $chatWidget   = document.getElementById('ai-chat-widget');
  const $chatToggle   = document.getElementById('chat-toggle');
  const $chatClose    = document.getElementById('chat-close');
  const $chatInput    = document.getElementById('chat-input');
  const $chatSend     = document.getElementById('chat-send');
  const $chatMessages = document.getElementById('chat-messages');
  let chatHistory = [];

  $chatToggle?.addEventListener('click', () => {
    $chatWidget.classList.toggle('open');
    if ($chatWidget.classList.contains('open') && !$chatMessages.children.length) {
      appendChat('ai', "Hii! I'm Deepmani's AI. Ask me about his work, PRAMANIIK, or anything tech! 🚀");
    }
  });
  $chatClose?.addEventListener('click', () => $chatWidget.classList.remove('open'));

  function appendChat(role, text) {
    const div = document.createElement('div');
    div.className = `chat-msg ${role === 'user' ? 'chat-msg-user' : 'chat-msg-ai'}`;
    div.innerHTML = `<span>${text}</span>`;
    $chatMessages.appendChild(div);
    $chatMessages.scrollTop = $chatMessages.scrollHeight;
  }

  async function sendChat() {
    const msg = $chatInput.value.trim();
    if (!msg) return;
    $chatInput.value = '';
    appendChat('user', msg);
    chatHistory.push({ role: 'user', parts: [{ text: msg }] });

    const loading = document.createElement('div');
    loading.className = 'chat-msg chat-msg-ai';
    loading.innerHTML = '<span><span class="dot-pulse"></span></span>';
    $chatMessages.appendChild(loading);
    $chatMessages.scrollTop = $chatMessages.scrollHeight;

    try {
      const res = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, history: chatHistory.slice(-10) })
      });
      const data = await res.json();
      loading.remove();
      appendChat('ai', data.reply);
      chatHistory.push({ role: 'model', parts: [{ text: data.reply }] });
    } catch {
      loading.remove();
      appendChat('ai', 'Hmm, something went wrong. Try again!');
    }
  }

  $chatSend?.addEventListener('click', sendChat);
  $chatInput?.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); } });

  /* ── CONTACT FORM ──────────────────────────────────────────── */
  document.getElementById('contact-form')?.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = e.target.querySelector('[type=submit]');
    btn.disabled = true; btn.textContent = 'Sending…';
    const form = e.target;
    try {
      const res = await fetch('/api/messages/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name:    form.querySelector('[name=name]').value,
          email:   form.querySelector('[name=email]').value,
          subject: form.querySelector('[name=subject]')?.value || '',
          message: form.querySelector('[name=message]').value
        })
      });
      const data = await res.json();
      if (data.success) {
        form.innerHTML = `
          <div class="contact-success">
            <span>✓</span>
            <p>${data.message}</p>
          </div>`;
      } else { btn.disabled = false; btn.textContent = 'Send Message →'; }
    } catch { btn.disabled = false; btn.textContent = 'Send Message →'; }
  });

  /* ── STATS COUNTER ─────────────────────────────────────────── */
  function animCounter(el, target, ms = 1400) {
    let start = null;
    (function step(ts) {
      if (!start) start = ts;
      const p = Math.min((ts - start) / ms, 1);
      el.textContent = Math.floor(p * target).toLocaleString();
      if (p < 1) requestAnimationFrame(step);
    })(performance.now());
  }

  const $stats = document.getElementById('stats-section');
  if ($stats) {
    new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) {
        fetch('/api/stats').then(r => r.json()).then(data => {
          document.querySelectorAll('[data-count]').forEach(el => {
            animCounter(el, data[el.dataset.count] || 0);
          });
        });
      }
    }, { threshold: 0.3 }).observe($stats);
  }

}); // END OF DOMContentLoaded