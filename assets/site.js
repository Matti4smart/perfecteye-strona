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
  // --- ceny: jedno źródło (data/cennik.json, edytowany w CMS) ---
  // <span data-c="id[.pole]|id2" data-od> – podmieniane na aktualną cenę na każdej stronie
  let PRICE = null;
  const priceText = el => {
    const vals = el.dataset.c.split('|').map(ref => { const [id, f] = ref.split('.'); const r = PRICE[id]; return r ? r[f || 'cena'] : undefined; })
      .filter(v => v !== undefined && v !== '' && v !== null);
    if (!vals.length) return null;
    const od = el.hasAttribute('data-od');
    const nums = vals.map(v => (typeof v === 'number' ? v : (/^\d+$/.test(String(v).trim()) ? +v : null)));
    let v = vals[0];
    if (od && nums.every(n => n !== null)) v = Math.min(...nums);
    return (od ? 'od ' : '') + v + ' zł';
  };
  const fillPrices = root => {
    if (!PRICE) return;
    let changed = false;
    (root.querySelectorAll ? root : document).querySelectorAll('[data-c]').forEach(el => {
      const t = priceText(el); if (t && el.textContent !== t) { el.textContent = t; changed = true; }
    });
    if (changed) refreshFaqLd();
  };
  // dane FAQ dla Google/AI odświeżane z treści strony (żeby zawierały aktualne ceny)
  const refreshFaqLd = () => {
    const qa = [...document.querySelectorAll('details')].map(d => [d.querySelector('summary')?.textContent.trim(), d.querySelector('p')?.textContent.trim()]).filter(x => x[0] && x[1] && !x[1].includes('['));
    if (!qa.length) return;
    document.querySelectorAll('script[type="application/ld+json"]').forEach(sc => {
      try { if (JSON.parse(sc.textContent)['@type'] === 'FAQPage') sc.textContent = JSON.stringify({ '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: qa.map(([q, a]) => ({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: a } })) }); } catch (e) {}
    });
  };
  PE.loadPrices = async () => {
    if (PRICE) return PRICE;
    const c = await PE.load('cennik'); const idx = {};
    Object.values(c).forEach(rows => Array.isArray(rows) && rows.forEach(r => { if (r.id) idx[r.id] = r; }));
    PRICE = idx; fillPrices(document);
    new MutationObserver(ms => ms.forEach(m => m.addedNodes.forEach(n => n.nodeType === 1 && (n.matches?.('[data-c]') ? fillPrices(n.parentNode || document) : fillPrices(n))))).observe(document.body, { childList: true, subtree: true });
    return PRICE;
  };

  // --- aktualności (strona główna + /aktualnosci/) ---
  const esc = t => String(t || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const fmtD = d => new Date(d + 'T12:00:00').toLocaleDateString('pl-PL', { day: 'numeric', month: 'long', year: 'numeric' });
  PE.newsSplit = posts => {
    const today = new Date().toISOString().slice(0, 10);
    const sorted = [...posts].sort((a, b) => (b.data || '').localeCompare(a.data || ''));
    return { active: sorted.filter(p => !p.wazne_do || p.wazne_do >= today), archive: sorted.filter(p => p.wazne_do && p.wazne_do < today) };
  };
  PE.newsCard = (p, full, old) => {
    const lines = String(p.tekst || '').split('\n').map(l => l.trim()).filter(Boolean);
    let body = '', inList = false;
    for (const l of lines) {
      if (/^[•\-]/.test(l)) { if (!inList) { body += '<ul>'; inList = true; } body += `<li>${esc(l.replace(/^[•\-]\s*/, ''))}</li>`; }
      else { if (inList) { body += '</ul>'; inList = false; } body += `<p>${esc(l)}</p>`; }
    }
    if (inList) body += '</ul>';
    if (!full) body = `<p>${esc(lines[0] || '')}</p>`;
    const img = p.zdjecie ? `<img src="${ROOT}${esc(p.zdjecie)}" alt="${esc(p.tytul)}" loading="lazy">` : '';
    const meta = `<p class="news-meta"><span class="news-typ">${esc(p.typ)}</span>${p.data ? fmtD(p.data) : ''}${p.wazne_do ? ` · ${old ? 'zakończona' : 'ważne do ' + fmtD(p.wazne_do)}` : ''}</p>`;
    const btn = p.link && !old ? `<a class="btn sm${full ? '' : ' ghost'}" href="${esc(p.link)}"${/booksy/.test(p.link) ? ' data-conv="booksy"' : ''}>${esc(p.link_tekst || 'Szczegóły')}</a>` : '';
    return `<article class="card news${old ? ' old' : ''}">${img}<div class="news-body">${meta}<h3>${esc(p.tytul)}</h3>${body}${btn}</div></article>`;
  };

  // --- nagłówek / stopka wspólne ---
  async function renderChrome() {
    const u = await PE.load('ustawienia');
    const here = (document.body.dataset.page || '');
    const link = (href, label, cls = '') =>
      `<a href="${ROOT}${href}" class="${cls}${here === href.replace(/\/$/, '').replace('index.html','') ? ' on' : ''}">${label}</a>`;
    const topbar = u.pasek_promo_wlaczony && u.pasek_promo
      ? `<div class="topbar"><a href="${/booksy\.com/.test(u.pasek_promo_link || '') ? u.booksy : (u.pasek_promo_link || u.booksy)}">${u.pasek_promo}</a></div>` : '';
    const header = `
      <header class="site"><div class="wrap">
        <a class="logo" href="${ROOT}" aria-label="PerfectEye – strona główna"><img src="${ROOT}zdjecia/logo.png" alt="PerfectEye" width="165" height="60"></a>
        <button class="navtoggle" aria-expanded="false" aria-controls="menu">Menu</button>
        <nav class="main" id="menu" aria-label="Menu główne">
          ${link('rzesy/', 'Rzęsy i brwi')}${link('twarz/', 'Twarz')}${link('cennik/', 'Cennik')}${link('akademia/', 'Akademia', 'acc')}${link('aktualnosci/', 'Aktualności')}${link('portfolio/', 'Portfolio')}${link('o-nas/', 'O nas')}${link('kontakt/', 'Kontakt')}
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
    document.querySelectorAll('a').forEach(ext);
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

  // --- Booksy, Facebook, Instagram i mapy otwieramy w nowej karcie ---
  const EXT = /(booksy\.com|facebook\.com|instagram\.com|google\.[a-z.]+\/maps)/;
  const ext = a => { if (a && a.href && EXT.test(a.href)) { a.target = '_blank'; a.rel = 'noopener'; } };
  document.addEventListener('click', e => ext(e.target.closest('a')), true);

  // --- zdarzenia konwersji (Booksy, telefon) ---
  document.addEventListener('click', e => {
    const a = e.target.closest('a[data-conv]'); if (!a || !window.gtag) return;
    gtag('event', a.dataset.conv === 'booksy' ? 'klik_booksy' : 'klik_telefon', { link_url: a.href });
  });

  document.addEventListener('DOMContentLoaded', () => { renderChrome(); consent(); PE.loadPrices(); });
})();
