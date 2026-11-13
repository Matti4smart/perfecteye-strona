#!/usr/bin/env python3
"""Generuje podstrony zabiegów (twarz/<slug>/) i szkoleń (akademia/<slug>/) z JSON + szablonu."""
import json, os, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p): return json.load(open(os.path.join(ROOT, '_build', p), encoding='utf-8'))
def wr(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(content)
CEN = json.load(open(os.path.join(ROOT, 'data', 'cennik.json'), encoding='utf-8'))
def booksy_names(key, slug):
    seen = []
    for r in CEN[key]:
        if r.get('slug') == slug and r['nazwa'] not in seen: seen.append(r['nazwa'])
    return seen
def hint(names):
    if not names: return ''
    q = ' lub '.join(f'<b>„{html.escape(n)}”</b>' for n in names[:3])
    return f'<p class="booksy-hint">W Booksy wybierz: {q}</p>'
NOINDEX = '<meta name="robots" content="noindex, nofollow">'  # usunąć w dniu startu

HEAD = '''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{meta}">
{noindex}
<link rel="canonical" href="https://www.perfecteye.pl/{path}/">
<link rel="icon" href="../../favicon.ico" sizes="32x32">
<script src="../../assets/head.js" data-root="../../"></script>
{ld}
</head>
<body data-page="{section}/">
<div id="chrome-top"></div>
<nav class="wrap crumbs" aria-label="Ścieżka"><a href="../../">Strona główna</a> / <a href="../">{section_label}</a> / <span style="color:var(--text)">{crumb}</span></nav>
'''
FOOT = '''
<section class="section center" style="background:linear-gradient(160deg,#2A2012 0%,#120F0B 60%)"><div class="wrap">
  <h2>{cta_h}</h2>
  <p class="muted" style="margin:14px 0 28px">ul. Kościuszki 180, Katowice · Pon–Pt 8:00–20:00 · Sob 8:00–13:00</p>
  <div style="display:flex;flex-wrap:wrap;gap:12px;justify-content:center"><a class="btn" href="{cta_href}" data-conv="{cta_conv}" rel="noopener">{cta_btn}</a><a class="btn ghost" href="tel:+48600102689" data-conv="tel">600 102 689</a></div>
</div></section>
<div id="chrome-bottom"></div>
<script src="../../assets/site.js"></script>
</body>
</html>
'''
def li(items): return ''.join(f'<li>{html.escape(x)}</li>' for x in items)

def zabieg(z):
    ld = json.dumps({"@context":"https://schema.org","@type":"Service","name":z['tytul'],"provider":{"@type":"BeautySalon","name":"PerfectEye Dorota Górecka","telephone":"+48600102689"},"areaServed":"Katowice","description":z['lead']}, ensure_ascii=False)
    etapy = ''.join(f'<li><span class="n">{i+1}</span><div><h3>{html.escape(t)}</h3><p>{html.escape(d)}</p></div></li>' for i,(t,d) in enumerate(z['etapy']))
    cen = ''.join(f'<tr><th scope="row" style="font-weight:400">{html.escape(r[0])}</th><td class="r">{r[1]}</td><td class="r">{r[2]}</td><td class="r">{r[3]}</td></tr>' for r in z['cennik'])
    faq = ''.join(f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q,a in z['faq'])
    zr = ''
    if z.get('zrodla'):
        s = z['zrodla']
        lst = ''.join(f'<li style="margin-bottom:14px"><a href="{u}" rel="noopener">{html.escape(t)}</a> <span class="muted2">{html.escape(n)}</span></li>' for t,u,n in s['lista'])
        zr = f'''<section class="band section"><div class="wrap" style="max-width:860px"><p class="eyebrow">Źródła i stan wiedzy</p><h2 style="font-size:38px;margin-bottom:18px">{html.escape(s['tytul'])}</h2><p class="muted">{html.escape(s['tekst'])}</p><ol class="muted" style="padding-left:22px">{lst}</ol><p class="muted2" style="font-size:14px">Opis zabiegu ma charakter informacyjny i nie zastępuje porady lekarza.</p></div></section>'''
    foto = (f'<div class="photo-frame"><img src="../../{z["foto_plik"]}" alt="{html.escape(z.get("foto_alt",""),quote=True)}" width="1200" height="1600" style="aspect-ratio:4/5;object-fit:cover"></div>'
            if z.get('foto_plik') else f'<div class="frame"><div class="ph" style="min-height:500px">{html.escape(z["foto"])}</div></div>')
    gal = ''
    if z.get('galeria'):
        gal = '<section class="wrap" style="max-width:1040px;padding:72px 0 0"><h2 class="center" style="font-size:38px;margin-bottom:24px">Tak to wygląda w salonie</h2><div class="thumbs">' + ''.join(f'<figure style="margin:0"><img src="../../{p}" alt="{html.escape(a,quote=True)}" loading="lazy"><figcaption class="muted2" style="font-size:14px;margin-top:8px">{html.escape(a)}</figcaption></figure>' for p,a in z['galeria']) + '</div></section>'
    body = f'''
<section class="hero"><div class="wrap split">
  <div>
    <p class="eyebrow line">{html.escape(z['kat'])}</p>
    <h1 style="font-size:clamp(40px,6vw,66px)">{z['tytul_h1'].replace('<em>','<em style="color:var(--gold)">')}</h1>
    <p class="lead">{html.escape(z['lead'])}</p>
    <div class="ctas" style="margin-bottom:18px"><a class="btn" href="https://perfecteye.booksy.com" data-conv="booksy" rel="noopener">Zarezerwuj zabieg</a><a class="btn ghost" href="tel:+48600102689" data-conv="tel">Zapytaj: 600 102 689</a></div>
    {hint(booksy_names('twarz', z['slug']))}
    <div style="display:flex;flex-wrap:wrap;border:1px solid var(--line)">
      <div style="flex:1 1 140px;padding:16px 20px;border-right:1px solid var(--line)"><p class="eyebrow" style="font-size:12px;letter-spacing:.18em;color:var(--muted2);margin:0">Cena</p><p style="margin:4px 0 0;font-family:var(--serif);font-size:26px;color:var(--gold)">{z['cena_od']}</p></div>
      <div style="flex:1 1 140px;padding:16px 20px;border-right:1px solid var(--line)"><p class="eyebrow" style="font-size:12px;letter-spacing:.18em;color:var(--muted2);margin:0">Obszar</p><p style="margin:4px 0 0;font-family:var(--serif);font-size:26px">{z['obszar']}</p></div>
      <div style="flex:1 1 140px;padding:16px 20px"><p class="eyebrow" style="font-size:12px;letter-spacing:.18em;color:var(--muted2);margin:0">{z['trzeci_label']}</p><p style="margin:4px 0 0;font-family:var(--serif);font-size:26px">{z['trzeci']}</p></div>
    </div>
  </div>
  {foto}
</div></section>

<section class="band section"><div class="wrap" style="max-width:1040px">
  <div class="head"><p class="eyebrow">Przebieg</p><h2>{len(z['etapy'])} etap{'y' if len(z['etapy'])<5 else 'ów'}, jedna wizyta</h2></div>
  <ol class="steps">{etapy}</ol>
  {f'<p class="muted2" style="margin-top:24px;font-size:15px">{html.escape(z["etapy_uwaga"])}</p>' if z.get('etapy_uwaga') else ''}
</div></section>

{gal}
<section class="section"><div class="wrap grid c3">
  <div class="card"><h3 style="color:var(--gold);margin-bottom:18px">Dla kogo</h3><ul class="muted" style="margin:0;padding-left:20px;line-height:1.9">{li(z['dla_kogo'])}</ul></div>
  <div class="card"><h3 style="color:var(--gold);margin-bottom:18px">Czego się spodziewać</h3><ul class="muted" style="margin:0;padding-left:20px;line-height:1.9">{li(z['efekty'])}</ul></div>
  <div class="card gold"><h3 style="color:var(--gold);margin-bottom:18px">Przeciwwskazania</h3><p class="muted" style="margin:0">{html.escape(z['przeciw'])} W razie wątpliwości umów <a href="https://perfecteye.booksy.com" rel="noopener">konsultację (50 zł)</a>.</p></div>
</div></section>

<section class="wrap" style="max-width:1040px;padding-bottom:88px">
  <h2 class="center" style="font-size:44px;margin-bottom:28px">Cennik</h2>
  <div class="table"><table><thead><tr><th>Wariant</th><th class="r">Twarz</th><th class="r">+ szyja</th><th class="r">+ dekolt</th></tr></thead><tbody>{cen}</tbody></table></div>
  <p class="muted2 center" style="margin-top:16px;font-size:15px">Ceny standardowe. Aktualne promocje – w Booksy.</p>
</section>

<section class="wrap" style="max-width:860px;padding-bottom:88px"><h2 style="font-size:44px;margin-bottom:24px">Pytania</h2>{faq}</section>
{zr}'''
    return HEAD.format(title=f"{z['tytul']} Katowice – PerfectEye", meta=html.escape(z['meta'],quote=True), noindex=NOINDEX, path=f"twarz/{z['slug']}", ld=f'<script type="application/ld+json">{ld}</script>', section='twarz', section_label='Zabiegi na twarz', crumb=html.escape(z['tytul'])) + body + FOOT.format(cta_h=f"Zarezerwuj: {html.escape(z['tytul'])}", cta_href='https://perfecteye.booksy.com', cta_conv='booksy', cta_btn='Wybierz termin w Booksy')

def szkolenie(s):
    ld = json.dumps({"@context":"https://schema.org","@type":"Course","name":s['tytul'],"description":s['lead'],"provider":{"@type":"Organization","name":"Akademia PerfectEye","sameAs":"https://www.perfecteye.pl"}}, ensure_ascii=False)
    prog = ''.join(f'<li><span class="n">{i+1}</span><div><p style="margin:0;font-size:18px">{html.escape(p)}</p></div></li>' for i,p in enumerate(s['program']))
    body = f'''
<section class="hero"><div class="wrap split">
  <div>
    <p class="eyebrow line">{html.escape(s['kat'])}</p>
    <h1 style="font-size:clamp(38px,5.5vw,60px)">{html.escape(s['tytul'])}</h1>
    <p class="lead">{html.escape(s['lead'])}</p>
    <div class="ctas" style="margin-bottom:18px"><a class="btn" href="tel:+48600102689" data-conv="tel">Zapytaj o termin</a><a class="btn ghost" href="https://perfecteye.booksy.com" data-conv="booksy" rel="noopener">Zapisz się w Booksy</a></div>
    {hint(booksy_names('szkolenia', s['slug']))}
    <div style="display:flex;flex-wrap:wrap;border:1px solid var(--line)">
      <div style="flex:1 1 140px;padding:16px 20px;border-right:1px solid var(--line)"><p style="margin:0;font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted2)">Cena</p><p style="margin:4px 0 0;font-family:var(--serif);font-size:24px;color:var(--gold)">{s['cena']}</p></div>
      <div style="flex:1 1 140px;padding:16px 20px;border-right:1px solid var(--line)"><p style="margin:0;font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted2)">Czas</p><p style="margin:4px 0 0;font-family:var(--serif);font-size:24px">{s['czas']}</p></div>
      <div style="flex:1 1 140px;padding:16px 20px"><p style="margin:0;font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted2)">Poziom</p><p style="margin:4px 0 0;font-family:var(--serif);font-size:24px">{s['poziom']}</p></div>
    </div>
  </div>
  <div class="frame"><div class="ph" style="min-height:480px">[Zdjęcie: kursantka przy pracy, instruktorka obok]</div></div>
</div></section>

<section class="band section"><div class="wrap" style="max-width:1040px">
  <div class="head"><p class="eyebrow">Program</p><h2>Czego się nauczysz</h2></div>
  <ol class="steps">{prog}</ol>
</div></section>

<section class="section"><div class="wrap split" style="align-items:flex-start">
  <div class="card gold"><h3 style="color:var(--gold);margin-bottom:18px">W pakiecie szkolenia</h3><ul class="muted" style="margin:0;padding-left:20px;line-height:1.9">{li(s['pakiet'])}</ul></div>
  <div>
    <h3 style="margin-bottom:14px">Jak wygląda dzień szkolenia</h3>
    <p class="muted">Szkolenie prowadzi inż. Dorota Górecka w działającym salonie na Brynowie. Rano teoria i ćwiczenia na główce treningowej, po przerwie praca na modelce, którą zapewniamy. Grupa jest kameralna (1–2 osoby), więc instruktorka cały czas jest przy Tobie.</p>
    <p class="muted">Na koniec otrzymujesz certyfikat, statuetkę i skrypt. Po kursie możesz pisać i dzwonić z pytaniami – wspieramy pierwsze samodzielne stylizacje.</p>
    <p class="muted"><b style="color:var(--text);font-weight:500">Dalej:</b> {html.escape(s['nastepne'])}</p>
    <p class="muted2" style="font-size:15px">Zaliczka przy zapisie rezerwuje termin i jest odliczana od ceny szkolenia.</p>
  </div>
</div></section>'''
    return HEAD.format(title=f"{s['tytul']} – szkolenie Katowice | Akademia PerfectEye", meta=html.escape(s['meta'],quote=True), noindex=NOINDEX, path=f"akademia/{s['slug']}", ld=f'<script type="application/ld+json">{ld}</script>', section='akademia', section_label='Akademia', crumb=html.escape(s['tytul'])) + body + FOOT.format(cta_h='Zapytaj o najbliższy termin', cta_href='https://perfecteye.booksy.com', cta_conv='booksy', cta_btn='Zapisz się w Booksy')

if __name__ == '__main__':
    n = 0
    for z in rd('zabiegi.json'):
        wr(os.path.join(ROOT, 'twarz', z['slug'], 'index.html'), zabieg(z)); n += 1
    for s in rd('szkolenia.json'):
        wr(os.path.join(ROOT, 'akademia', s['slug'], 'index.html'), szkolenie(s)); n += 1
    print('wygenerowano', n, 'podstron')
