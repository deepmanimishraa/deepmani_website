/* ============================================================
   DEEPMANI MISHRAA — main.js v3
   Lightweight: no Three.js, no canvas
   Navbar · Journey scroll · Gallery · AI Chat · Contact
   ============================================================ */

/* ── NAVBAR ─────────────────────────────────────────── */
const $navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  $navbar?.classList.toggle('scrolled', window.scrollY > 70);
}, { passive: true });

/* ── MOBILE MENU ────────────────────────────────────── */
const $mBtn  = document.getElementById('mobile-menu-btn');
const $mMenu = document.getElementById('mobile-menu');

function closeMobileMenu() {
  $mMenu?.classList.remove('open');
  if ($mBtn) { $mBtn.textContent = '☰'; $mBtn.setAttribute('aria-expanded','false'); }
  document.body.style.overflow = '';
}
if ($mBtn && $mMenu) {
  $mBtn.addEventListener('click', e => {
    e.stopPropagation();
    const open = $mMenu.classList.toggle('open');
    $mBtn.textContent = open ? '✕' : '☰';
    $mBtn.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
  });
  $mMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMobileMenu));
  document.addEventListener('click', e => {
    if ($mMenu.classList.contains('open') && !$mMenu.contains(e.target) && e.target !== $mBtn)
      closeMobileMenu();
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMobileMenu(); });
}

/* ── SMOOTH SCROLL ──────────────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const y = target.getBoundingClientRect().top + window.scrollY - 72;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  });
});

/* ── REVEAL (IntersectionObserver also in bg.js, safe duplicate) ── */
if (!window._revealObserverRunning) {
  window._revealObserverRunning = true;
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('revealed'); obs.unobserve(e.target); } });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
  document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
}

/* ── TYPED HERO TEXT ────────────────────────────────── */
const $typed = document.getElementById('typed-text');
if ($typed) {
  const phrases = ['Student | IIT Madras', 'Co-Founder | PRAMANIIK'];
  let pi = 0, ci = 0, del = false;
  function typeLoop() {
    const p = phrases[pi];
    if (!del) { $typed.textContent = p.slice(0, ++ci); if (ci === p.length) { del = true; setTimeout(typeLoop, 2000); return; } }
    else { $typed.textContent = p.slice(0, --ci); if (ci === 0) { del = false; pi = (pi+1) % phrases.length; } }
    setTimeout(typeLoop, del ? 50 : 80);
  }
  setTimeout(typeLoop, 600);
}

/* ── JOURNEY TIMELINE — drag + touch ───────────────── */
const $track = document.getElementById('timeline-track');
if ($track) {
  fetch('/api/journey/list').then(r => r.json()).then(entries => {
    const icons = { rocket:'🚀', graduation:'🎓', shield:'🛡️', globe:'🌐', star:'⭐', code:'💻', award:'🏆' };
    $track.innerHTML = '';
    entries.forEach(e => {
      const card = document.createElement('div');
      card.className = 'timeline-card';
      card.innerHTML = `
        <div class="timeline-year">${e.year}</div>
        <div class="timeline-icon">${icons[e.icon]||'⭐'}</div>
        <div class="timeline-title">${e.title}</div>
        <div class="timeline-desc">${e.description||''}</div>
        <div class="timeline-cat">${e.category}</div>`;
      $track.appendChild(card);
    });
  }).catch(() => {
    $track.innerHTML = '<div class="timeline-card" style="flex:0 0 220px;display:flex;align-items:center;justify-content:center;"><span style="color:var(--text-dim);">Could not load</span></div>';
  });

  let dragging = false, sx = 0, sl = 0;
  $track.addEventListener('mousedown', e => { dragging=true; sx=e.pageX-$track.offsetLeft; sl=$track.scrollLeft; $track.style.cursor='grabbing'; $track.style.userSelect='none'; });
  window.addEventListener('mouseup', () => { dragging=false; $track.style.cursor='grab'; $track.style.userSelect=''; });
  $track.addEventListener('mouseleave', () => { dragging=false; $track.style.cursor='grab'; });
  $track.addEventListener('mousemove', e => { if (!dragging) return; e.preventDefault(); $track.scrollLeft = sl - (e.pageX - $track.offsetLeft - sx) * 1.4; });
  
  // NOTE: Touchstart and Touchmove lines deleted to enable native mobile scrolling
}

/* ── STATS COUNTER ──────────────────────────────────── */
function animCount(el, target, ms=1200) {
  const start = performance.now();
  (function step(now) {
    const p = Math.min((now - start) / ms, 1);
    el.textContent = Math.floor(p * target).toLocaleString();
    if (p < 1) requestAnimationFrame(step);
  })(performance.now());
}
const $stats = document.getElementById('stats-section');
if ($stats) {
  new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting) {
      fetch('/api/stats').then(r=>r.json()).then(data => {
        document.querySelectorAll('[data-count]').forEach(el => {
          animCount(el, data[el.dataset.count] || 0);
        });
      });
    }
  }, {threshold:0.3}).observe($stats);
}

/* ── GALLERY ────────────────────────────────────────── */
const $ggrid  = document.getElementById('gallery-grid');
const $gModal = document.getElementById('gallery-modal');
const $cModal = document.getElementById('comment-modal');
let gPage=1, gLoading=false, gMore=true;

function loadGallery(page=1) {
  if (gLoading || !gMore || !$ggrid) return;
  gLoading = true;
  const $ld = document.getElementById('gallery-loading');
  if ($ld) $ld.style.display = 'block';
  fetch(`/gallery/api/list?page=${page}`)
    .then(r=>r.json())
    .then(data => {
      if (page===1) $ggrid.innerHTML = '';
      data.images.forEach(img => {
        const d = document.createElement('div');
        d.className = 'gallery-card';
        d.innerHTML = `
          <div class="gallery-img-wrap">
            <img src="${img.url}" alt="${img.title||''}" loading="lazy" />
            <div class="gallery-overlay">
              <button class="gal-btn like-btn ${img.liked?'liked':''}" data-id="${img.id}">
                ♥ <span class="lc">${img.likes}</span>
              </button>
              <button class="gal-btn comment-btn" data-id="${img.id}">
                💬 <span>${img.comments}</span>
              </button>
              <button class="gal-btn expand-btn" data-img='${JSON.stringify(img).replace(/'/g,"&#39;")}'>⤢</button>
            </div>
          </div>
          ${img.title    ?`<p class="gallery-caption">${img.title}</p>`:''}
          ${img.taken_at ?`<p class="gallery-date">${img.taken_at}</p>`:''}`;
        $ggrid.appendChild(d);
      });
      gMore = data.has_next; gLoading = false;
      if ($ld) $ld.style.display = gMore ? 'block' : 'none';
    }).catch(()=>{gLoading=false;});
}

if ($ggrid) {
  loadGallery();
  window.addEventListener('scroll', () => {
    if (gMore && !gLoading && window.scrollY + window.innerHeight >= document.body.scrollHeight - 500)
      loadGallery(++gPage);
  }, {passive:true});

  $ggrid.addEventListener('click', e => {
    const lb = e.target.closest('.like-btn');
    const xb = e.target.closest('.expand-btn');
    const cb = e.target.closest('.comment-btn');
    if (lb) {
      fetch(`/gallery/api/like/${lb.dataset.id}`, {method:'POST'})
        .then(r=>r.json()).then(d => { lb.querySelector('.lc').textContent=d.count; lb.classList.toggle('liked',d.liked); });
    }
    if (xb) {
      const img = JSON.parse(xb.getAttribute('data-img'));
      $gModal.querySelector('#modal-img').src = img.url;
      $gModal.querySelector('#modal-title').textContent = img.title||'';
      $gModal.querySelector('#modal-desc').textContent  = img.description||'';
      $gModal.querySelector('#modal-date').textContent  = img.taken_at||'';
      $gModal.classList.remove('hidden'); document.body.style.overflow='hidden';
    }
    if (cb) {
      $cModal.dataset.imgId = cb.dataset.id;
      $cModal.classList.remove('hidden'); document.body.style.overflow='hidden';
      loadComments(cb.dataset.id);
    }
  });
}
function closeModal(el) { el?.classList.add('hidden'); document.body.style.overflow=''; }
$gModal?.querySelector('.modal-close')?.addEventListener('click', ()=>closeModal($gModal));
$gModal?.addEventListener('click', e => { if (e.target===$gModal) closeModal($gModal); });
$cModal?.querySelector('.modal-close')?.addEventListener('click', ()=>closeModal($cModal));
$cModal?.addEventListener('click', e => { if (e.target===$cModal) closeModal($cModal); });

function loadComments(id) {
  const $list = document.getElementById('comments-list');
  if (!$list) return;
  fetch(`/gallery/api/comments/${id}`).then(r=>r.json()).then(d => {
    $list.innerHTML = d.comments.length
      ? d.comments.map(c=>`<div class="comment-item"><strong>${c.name}</strong><p>${c.content}</p><small>${c.date}</small></div>`).join('')
      : '<p style="color:var(--text-dim);font-size:.84rem;padding:.5rem 0;">No comments yet. Be the first!</p>';
  });
}
document.getElementById('comment-form')?.addEventListener('submit', e => {
  e.preventDefault();
  const id=$cModal.dataset.imgId, f=e.target;
  fetch(`/gallery/api/comment/${id}`,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({name:f.querySelector('[name=name]').value,email:f.querySelector('[name=email]').value,content:f.querySelector('[name=content]').value})})
    .then(()=>{f.reset();loadComments(id);});
});

/* ── AI CHAT ────────────────────────────────────────── */
const $widget   = document.getElementById('ai-chat-widget');
const $toggle   = document.getElementById('chat-toggle');
const $close    = document.getElementById('chat-close');
const $input    = document.getElementById('chat-input');
const $send     = document.getElementById('chat-send');
const $messages = document.getElementById('chat-messages');
let chatHistory = [];

$toggle?.addEventListener('click', () => {
  $widget.classList.toggle('open');
  if ($widget.classList.contains('open') && !$messages.children.length)
    addMsg('ai', "Hi! I'm Deepmani's AI assistant. Ask me about his work, academics, or anything!");
});
$close?.addEventListener('click', () => $widget.classList.remove('open'));

function addMsg(role, text) {
  const d = document.createElement('div');
  d.className = `chat-msg chat-msg-${role}`;
  d.innerHTML = `<span>${text}</span>`;
  $messages.appendChild(d);
  $messages.scrollTop = $messages.scrollHeight;
}

async function sendChat() {
  const msg = ($input?.value||'').trim();
  if (!msg) return;
  $input.value = '';
  addMsg('user', msg);
  chatHistory.push({role:'user',parts:[{text:msg}]});
  const ld = document.createElement('div');
  ld.className='chat-msg chat-msg-ai';
  ld.innerHTML='<span><span class="dot-pulse"></span></span>';
  $messages.appendChild(ld); $messages.scrollTop=$messages.scrollHeight;
  try {
    const res = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, history: chatHistory.slice(-8) })
    });
    
    ld.remove();
    
    // Read the stream chunk by chunk
    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let fullReply = '';
    
    // Create an empty message bubble first
    addMsg('ai', '');
    const $msgSpan = $messages.lastElementChild.querySelector('span');
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      fullReply += chunk;
      // Type it out on the screen instantly
      $msgSpan.innerHTML = fullReply.replace(/\n/g, '<br>');
      $messages.scrollTop = $messages.scrollHeight;
    }
    
    chatHistory.push({ role: 'model', parts: [{ text: fullReply }] });
  } catch { 
    ld.remove(); addMsg('ai','Connection error. Please try again!'); 
  }
}
$send?.addEventListener('click', sendChat);
$input?.addEventListener('keydown', e => { if (e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendChat();} });

/* ── CONTACT FORM ───────────────────────────────────── */
document.getElementById('contact-form')?.addEventListener('submit', async e => {
  e.preventDefault();
  const btn = e.target.querySelector('[type=submit]');
  btn.disabled=true; btn.querySelector('span').textContent='Sending…';
  const f = e.target;
  try {
    const res = await fetch('/api/messages/send',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({name:f.querySelector('[name=name]').value,email:f.querySelector('[name=email]').value,
        subject:f.querySelector('[name=subject]')?.value||'',message:f.querySelector('[name=message]').value})});
    const data = await res.json();
    if (data.success) {
      f.innerHTML=`<div class="contact-success"><span class="check">✓</span><p>${data.message}</p></div>`;
    } else { btn.disabled=false; btn.querySelector('span').textContent='Send Message →'; }
  } catch { btn.disabled=false; btn.querySelector('span').textContent='Send Message →'; }
});
