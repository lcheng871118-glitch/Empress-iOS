# -*- coding: utf-8 -*-
"""分析 catalog.json 与 veekun 词典的匹配度，确定缺口。"""
import json, csv, re

ROOT = r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port'
catalog = json.load(open(ROOT + r'\game\client\data\catalog.json', encoding='utf-8'))

def load_dict(fn, idcol, namecol):
    d = {}
    for r in csv.DictReader(open(ROOT + r'\scripts\dict' + fn, encoding='utf-8')):
        if r['local_language_id'] == '12':  # 简体中文
            d[r[idcol]] = r[namecol]
    return d

sp_zh = load_dict(r'\pokemon_species_names.csv', 'pokemon_species_id', 'name')
mv_zh = load_dict(r'\move_names.csv', 'move_id', 'name')
ab_zh = load_dict(r'\ability_names.csv', 'ability_id', 'name')

species = catalog['species']
print('species 总数:', len(species))

# 按 num 分桶（num 1..1025，form 共享 num）
plain = [s for s in species if not s.get('forme')]
formed = [s for s in species if s.get('forme')]
print('无 forme:', len(plain), ' 有 forme:', len(formed))

# plain 里能直接匹配的（name == 基础名）
plain_lower = {s['name'].lower() for s in plain}
covered = 0
uncovered = []
for s in plain:
    # veekun 用英文名匹配
    hit = None
    for v in sp_zh.values():
        pass
    uncovered.append(s)
print()
print('=== plain 物种 name 列表（前 40，看命名风格）===')
for s in plain[:40]:
    print('  id=%s num=%s name=%r forme=%r baseSpecies=%r' % (s['id'], s.get('num'), s['name'], s.get('forme'), s.get('baseSpecies')))

print()
print('=== formed 前 20 ===')
for s in formed[:20]:
    print('  id=%s num=%s name=%r forme=%r baseSpecies=%r' % (s['id'], s.get('num'), s['name'], s.get('forme'), s.get('baseSpecies')))

print()
print('=== moves 数量/匹配 ===')
moves = catalog['moves']
print('moves 总数:', len(moves))
mism = [m for m in moves if m not in mv_zh]
print('veekun 缺简中的 move id:', len(mism))
print('  样例:', mism[:30])
print('  veekun 有:', len(moves) - len(mism))

print()
print('=== abilities 数量/匹配 ===')
abs_ = catalog['abilities']
print('abilities 总数:', len(abs_))
amism = [a for a in abs_ if a not in ab_zh]
print('veekun 缺简中的 ability id:', len(amism))
print('  样例:', amism[:30])
