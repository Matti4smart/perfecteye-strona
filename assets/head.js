/* Wspólny <head>: Consent Mode v2 (domyślnie brak zgody), tag Google, fonty.
   Wczytywany jako pierwszy skrypt każdej strony. */
(function () {
  const ROOT = document.currentScript.dataset.root || '';
  document.documentElement.dataset.root = ROOT;

  // Consent Mode v2 – domyślnie odmowa, aktualizacja po decyzji w banerze
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { dataLayer.push(arguments); };
  gtag('consent', 'default', { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied', wait_for_update: 500 });
  let saved = null; try { saved = localStorage.getItem('pe_consent'); } catch (e) {}
  if (saved) gtag('consent', 'update', { ad_storage: saved, ad_user_data: saved, ad_personalization: saved, analytics_storage: saved });

  // Tag Google (GA4 + Google Ads) – te same identyfikatory co na starej stronie
  const s = document.createElement('script'); s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=G-TN93V4DYJL';
  document.head.appendChild(s);
  gtag('js', new Date());
  gtag('config', 'G-TN93V4DYJL');
  gtag('config', 'AW-987464470');

  // Fonty
  const f = document.createElement('link'); f.rel = 'stylesheet';
  f.href = 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@300;400;500;600&display=swap';
  document.head.appendChild(f);
  const c = document.createElement('link'); c.rel = 'stylesheet'; c.href = ROOT + 'assets/style.css'; document.head.appendChild(c);
})();
