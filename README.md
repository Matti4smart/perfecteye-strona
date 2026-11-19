# Strona PerfectEye – www.perfecteye.pl

Statyczna strona salonu (GitHub Pages). Styl G: czerń + złoto.

## Edycja treści (panel CMS)
1. Wejdź na https://app.pagescms.org i zaloguj się kontem GitHub, które ma dostęp do tego repozytorium.
2. Wybierz repozytorium `perfecteye-strona`.
3. W menu po lewej: **Cennik**, **Promocje**, **Opinie**, **Portfolio**, **Zespół**, **Ustawienia salonu**.
4. Zapisz – zmiana pojawi się na stronie po ok. 1 minucie.

Zdjęcia dodawane przez panel trafiają do folderu `zdjecia/`.

## Struktura
- `index.html` – strona główna
- `rzesy/`, `twarz/`, `cennik/`, `akademia/`, `portfolio/`, `o-nas/`, `kontakt/` – podstrony
- `twarz/<zabieg>/`, `akademia/<kurs>/` – podstrony generowane z `_build/*.json` przez `python3 _build/build.py`
- `data/*.json` – treści edytowane w CMS (cennik, promocje, opinie, galeria, zespół, ustawienia)
- `assets/` – style, skrypty; `assets/head.js` zawiera tag Google i tryb zgody (Consent Mode v2)
- `usługi/`, `szkolenia/`, `strona-główna/` – przekierowania ze starych adresów Google Sites

## Dzień startu (checklista)
1. Usuń `<meta name="robots" content="noindex, nofollow">` ze wszystkich stron (`grep -rl noindex --include=index.html . | xargs sed -i '/noindex, nofollow/d'`) i w `_build/build.py` ustaw `NOINDEX = ''`.
2. `robots.txt` → `User-agent: *\nAllow: /\nSitemap: https://www.perfecteye.pl/sitemap.xml`
3. W sitemap.xml zostaw tylko prawdziwe strony (bez `usługi/`, `szkolenia/`, `strona-główna/`).
4. DNS domeny: rekord CNAME `www` → `matti4smart.github.io`; w ustawieniach repo Pages → Custom domain `www.perfecteye.pl` + Enforce HTTPS.
5. Google Search Console: dodaj właściwość, prześlij sitemap.
6. Wizytówka Google: link do strony z UTM `?utm_source=google&utm_medium=organic&utm_campaign=wizytowka`.
7. Google Ads: sprawdź tag (Menedżer danych), utwórz konwersje ze zdarzeń GA4 `klik_booksy` i `klik_telefon`.

## Ceny – jedno miejsce
Wszystkie ceny pochodzą z `data/cennik.json` (CMS → „Cennik”). Każdy wiersz ma „Kod ceny” (`id`) – nie zmieniaj go.
W treściach cena to `<span data-c="id">` – strona podmienia ją na aktualną z cennika (assets/site.js), także w danych FAQ dla Google.
W plikach źródłowych (`_build/*.json`, strony) cenę wpisuje się znacznikiem: `{{id}}`, `{{id.twarz}}`, `{{od id1|id2}}` (najniższa) – patrz `_build/ceny.py`.
`python3 _build/odswiez_ceny.py` – przebudowuje podstrony i wpisuje aktualne ceny na stałe do HTML (opcjonalnie, np. raz na jakiś czas).
