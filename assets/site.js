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
        <a class="tel" href="tel:${u.telefon_link}" data-conv="tel">${u.telefon}</a>
        <a class="btn sm" href="${u.booksy}" data-conv="booksy" rel="noopener">Umów wizytę</a>
      </div></header>`;
    const footer = `
      <footer class="site"><div class="wrap">
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
