/* PerfectEye – wspólny skrypt: dane JSON, nawigacja, zgoda cookies, konwersje */
(function () {
  const ROOT = document.documentElement.dataset.root || '';
  const zl = v => (typeof v === 'number' ? v + ' zł' : v);
  window.PE = { ROOT, zl };

  // --- dane ---
  const cache = {};
  window.PE.load = async name => {
    if (!cache[name]) cache[name] = fetch(ROOT + 'data/' + name + '.json', { cache: 'no-cache' }).then(r => r.json());
    return cache[name];
  };


  const ICON = {
    facebook: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M14 8.5V6.8c0-.8.5-1.3 1.3-1.3H17V2.2h-2.6C11.6 2.2 10.4 4 10.4 6.4v2.1H8v3.3h2.4V22H14V11.8h2.6l.5-3.3H14z"/></svg>',
    instagram: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r="1" fill="currentColor" stroke="none"/></svg>',
    booksy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/><path d="M9 15l2 2 4-4"/></svg>'
  };
  window.PE.socialHTML = u => `<div class="social"><a href="${u.instagram}" rel="noopener" aria-label="Instagram PerfectEye">${ICON.instagram}</a><a href="${u.facebook}" rel="noopener" aria-label="Facebook PerfectEye">${ICON.facebook}</a><a href="${u.booksy}" rel="noopener" data-conv="booksy" aria-label="PerfectEye na Booksy">${ICON.booksy}</a></div>`;
  // --- nagłówek / stopka wspólne ---
  async function renderChrome() {
    const u = await PE.load('ustawienia');
    const here = (document.body.dataset.page || '');
    const link = (href, label, cls = '') =>
      `<a href="${ROOT}${href}" class="${cls}${here === href.replace(/\/$/, '').replace('index.html','') ? ' on' : ''}">${label}</a>`;
    const topbar = u.pasek_promo_wlaczony && u.pasek_promo
      ? `<div class="topbar"><a href="${u.pasek_promo_link}">${u.pasek_promo}</a></div>` : '';
    const header = `
      <header class="site"><div class="wrap">
        <a class="logo" href="${ROOT}"><b class="gold-text">PERFECT EYE</b><small>KATOWICE · OD ${u.rok_zalozenia}</small></a>
        <button class="navtoggle" aria-expanded="false" aria-controls="menu">Menu</button>
        <nav class="main" id="menu" aria-label="Menu główne">
          ${link('rzesy/', 'Rzęsy i brwi')}${link('twarz/', 'Twarz')}${link('cennik/', 'Cennik')}${link('akademia/', 'Akademia', 'acc')}${link('portfolio/', 'Portfolio')}${link('o-nas/', 'O nas')}${link('kontakt/', 'Kontakt')}
        </nav>
        ${PE.socialHTML(u)}
        <a class="tel" href="tel:${u.telefon_link}" data-conv="tel">${u.telefon}</a>
        <a class="btn sm" href="${u.booksy}" data-conv="booksy" rel="noopener">Umów wizytę</a>
      </div></header>`;
    const footer = `
      <footer class="site"><div class="wrap">
        ${PE.socialHTML(u)}
        <span>© ${new Date().getFullYear()} PerfectEye ${u.wlasciciel.replace('inż. ', '')} · ${u.adres_ulica}, ${u.adres_miasto}</span>
        <span><a href="${ROOT}akademia/">Akademia</a> · <a href="${u.instagram}" rel="noopener">Instagram</a> · <a href="${u.facebook}" rel="noopener">Facebook</a> · <a href="${ROOT}polityka-prywatnosci/">Polityka prywatności</a></span>
      </div></footer>
      <div class="mobilebar"><a class="btn ghost" href="tel:${u.telefon_link}" data-conv="tel">Zadzwoń</a><a class="btn" href="${u.booksy}" data-conv="booksy" rel="noopener">Umów online</a></div>`;
    document.getElementById('chrome-top').innerHTML = topbar + header;
    document.getElementById('chrome-bottom').innerHTML = footer;
    document.querySelector('.navtoggle').addEventListener('click', e => {
      const m = document.getElementById('menu'); const open = m.classList.toggle('open');
      e.currentTarget.setAttribute('aria-expanded', open);
    });
    // podstawienie danych kontaktowych w treści
    document.querySelectorAll('[data-social]').forEach(el => { el.innerHTML = PE.socialHTML(u); });
    document.querySelectorAll('[data-u]').forEach(el => { const k = el.dataset.u; if (u[k] !== undefined) el.textContent = u[k]; });
    document.querySelectorAll('a[data-href-u]').forEach(el => { el.href = u[el.dataset.hrefU]; });
    // każdy link do Booksy = bezprowizyjny link salonu (Booksy nie pobiera prowizji Boost)
    document.querySelectorAll('a[href*="booksy.com"]').forEach(el => { if (/perfecteye\.booksy\.com/.test(el.href)) el.href = u.booksy; });
  }

  // --- zgoda cookies (Consent Mode v2) ---
  function consent() {
    let saved = null; try { saved = localStorage.getItem('pe_consent'); } catch (e) {}
    if (saved) return;
    const box = document.createElement('div'); box.className = 'cookie'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-label', 'Pliki cookie');
    box.innerHTML = `<p>Używamy plików cookie, aby mierzyć skuteczność reklam i ruch na stronie. Możesz się zgodzić lub odrzucić – strona działa tak samo.</p>
      <div class="row"><button class="btn" id="ck-ok">Zgadzam się</button><button class="btn ghost" id="ck-no">Odrzuć</button> <a href="${ROOT}polityka-prywatnosci/" style="align-self:center;font-size:13px">Więcej</a></div>`;
    document.body.appendChild(box);
    const set = v => {
      try { localStorage.setItem('pe_consent', v); } catch (e) {}
      if (window.gtag) gtag('consent', 'update', { ad_storage: v, ad_user_data: v, ad_personalization: v, analytics_storage: v });
      box.remove();
    };
    document.getElementById('ck-ok').onclick = () => set('granted');
    document.getElementById('ck-no').onclick = () => set('denied');
  }

  // --- zdarzenia konwersji (Booksy, telefon) ---
  document.addEventListener('click', e => {
    const a = e.target.closest('a[data-conv]'); if (!a || !window.gtag) return;
    gtag('event', a.dataset.conv === 'booksy' ? 'klik_booksy' : 'klik_telefon', { link_url: a.href });
  });

  document.addEventListener('DOMContentLoaded', () => { renderChrome(); consent(); });
})();
