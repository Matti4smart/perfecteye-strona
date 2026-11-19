#!/usr/bin/env python3
"""Dodaje dane strukturalne FAQPage (dla Google/AI) do stron statycznych z sekcją <details>."""
import re, json, html, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ['index.html', 'cennik/index.html', 'rzesy/index.html', 'twarz/index.html', 'kontakt/index.html', 'akademia/index.html', 'aktualnosci/index.html']
strip = lambda t: html.unescape(re.sub('<[^>]+>', '', t)).strip()
for f in PAGES:
    p = os.path.join(ROOT, f)
    if not os.path.exists(p): continue
    t = open(p, encoding='utf-8').read()
    t = re.sub(r'<script type="application/ld\+json" data-faq>.*?</script>\n', '', t, flags=re.S)
    qa = [(strip(q), strip(a)) for q, a in re.findall(r'<details><summary>(.*?)</summary><p>(.*?)</p></details>', t, flags=re.S)]
    qa = [x for x in qa if '[' not in x[1]]
    if qa:
        ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}
        t = t.replace('</head>', '<script type="application/ld+json" data-faq>' + json.dumps(ld, ensure_ascii=False) + '</script>\n</head>', 1)
    open(p, 'w', encoding='utf-8').write(t)
    print(f, len(qa))
