# -*- coding: utf-8 -*-
"""验证汉化后 catalog.json：抽样 + 未翻译残留检查。"""
import json, re

c = json.load(open(r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port\game\client\data\catalog.json', encoding='utf-8'))

print('=== 抽样 species ===')
for sid in ('bulbasaur', 'charizardmegax', 'pikachualola', 'zaciancrowned', 'ogerpon', 'nidoranf', '906'.join('')):
    pass
ids = ['bulbasaur', 'charizard', 'charizardmegax', 'pikachualola', 'zaciancrowned', 'ogerpon', 'nidoranf', 'corviknight', 'koraidon']
by_id = {s['id']: s for s in c['species']}
for i in ids:
    s = by_id.get(i)
    if s:
        print('  %-18s name=%-10s base=%-8s forme=%s' % (i, s['name'], s['baseSpecies'], s.get('forme', '')))

print('=== 抽样 moves ===')
for k in ('tackle', 'quickattack', 'flamethrower', 'struggle', 'surf'):
    m = c['moves'].get(k)
    if m:
        print('  %-14s name=%-6s shortDesc=%s' % (k, m['name'], (m.get('shortDesc') or '')[:44]))

print('=== 抽样 abilities ===')
for k in ('overgrow', 'chlorophyll', 'pastelveil', 'embodyaspectteal'):
    a = c['abilities'].get(k)
    if a:
        print('  %-18s name=%s' % (k, a['name']))

print('=== 残留英文检查 ===')
pat = re.compile(r"[A-Za-z]{3,}")
# species name 残留英文（除纯英文兜底形态外）
residual = [s['id'] for s in c['species'] if pat.search(s['name']) and '（' not in s['name']]
print('species name 含英文（无括号兜底）:', len(residual), residual[:20])
mres = [k for k, m in c['moves'].items() if pat.search(m['name'])]
print('moves name 含英文:', len(mres), mres[:20])
ares = [k for k, a in c['abilities'].items() if pat.search(a['name'])]
print('abilities name 含英文:', len(ares), ares[:20])
# shortDesc 残留英文
sres = [k for k, m in c['moves'].items() if pat.search(m.get('shortDesc') or '')]
print('shortDesc 仍英文:', len(sres), sres[:20])
