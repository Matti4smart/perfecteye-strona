#!/usr/bin/env python3
"""Ceny w jednym miejscu: data/cennik.json (edytowany w CMS).
Każdy wiersz cennika ma pole `id`. W tekstach źródłowych cenę wpisujemy jako znacznik:
  {{id}}            -> 199 zł           (pole `cena`)
  {{id.twarz}}      -> 299 zł           (inne pole, np. twarz/szyja/dekolt/t1/t2/t3)
  {{od id|id2}}     -> od 199 zł        (najniższa z podanych)
Znacznik zamienia się w <span data-c="..."> – strona przy każdym wyświetleniu
podmienia liczbę na aktualną z cennika (assets/site.js), więc zmiana ceny w CMS
zmienia ją wszędzie bez przebudowy stron."""
import json, os, re, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'data', 'cennik.json')
PREFIX = {'rzesy_od_zera': 'rz', 'rzesy_uzupelnienie': 'uz', 'rzesy_dodatki': 'dod', 'laminacja_brwi': 'lam',
          'twarz': 'tw', 'depilacja': 'dep', 'pakiety': 'pak', 'szkolenia': 'szk'}

def slug(t):
    t = unicodedata.normalize('NFKD', t.replace('ł', 'l').replace('Ł', 'L')).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:34].strip('-')

def load(assign=False):
    c = json.load(open(PATH, encoding='utf-8'))
    changed = False
    for sec, rows in c.items():
        if not isinstance(rows, list): continue
        for r in rows:
            if not r.get('id'):
                base = PREFIX.get(sec, sec[:3]) + '-' + slug(r['nazwa']); i, cand = 2, base
                ids = {x.get('id') for rr in c.values() if isinstance(rr, list) for x in rr}
                while cand in ids: cand = f'{base}-{i}'; i += 1
                r['id'] = cand; changed = True
    if changed and assign:
        json.dump(c, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    return c

C = load(assign=True)
IDX = {r['id']: r for rows in C.values() if isinstance(rows, list) for r in rows}

def value(ref):
    rid, _, field = ref.partition('.')
    if rid not in IDX: raise KeyError(f'Brak w cenniku id „{rid}”')
    return IDX[rid].get(field or 'cena')

def fmt_num(v):
    return f'{v} zł' if v not in (None, '') else '—'

def render(text, as_html=True):
    def rep(m):
        od, refs = bool(m.group(1)), m.group(2).strip()
        vals = [value(r) for r in refs.split('|')]
        nums = [v for v in vals if isinstance(v, (int, float))]
        v = min(nums) if (od and nums) else vals[0]
        txt = ('od ' if od else '') + fmt_num(v)
        if not as_html: return txt
        return f'<span data-c="{refs}"{" data-od" if od else ""}>{txt}</span>'
    return re.sub(r'\{\{\s*(od\s+)?([a-z0-9.|\-]+)\s*\}\}', rep, text)

if __name__ == '__main__':
    for k in IDX: print(k)
