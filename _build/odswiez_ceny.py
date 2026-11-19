#!/usr/bin/env python3
"""Opcjonalnie: wpisuje aktualne ceny z data/cennik.json na stałe do plików HTML
(przeglądarka i tak podmienia je na bieżąco – to tylko odświeżenie wersji „zapasowej” dla wyszukiwarek)."""
import os, re, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ceny, subprocess
ROOT = ceny.ROOT
subprocess.run([sys.executable, os.path.join(ROOT, '_build', 'build.py')], check=True)
n = 0
for f in glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True):
    t = open(f, encoding='utf-8').read()
    t2 = re.sub(r'<span data-c="([^"]+)"( data-od)?>[^<]*</span>', lambda m: ceny.render('{{' + ('od ' if m.group(2) else '') + m.group(1) + '}}'), t)
    if t2 != t: open(f, 'w', encoding='utf-8').write(t2); n += 1
subprocess.run([sys.executable, os.path.join(ROOT, '_build', 'faq_ld.py')], check=True, stdout=subprocess.DEVNULL)
print('odświeżono plików:', n)
