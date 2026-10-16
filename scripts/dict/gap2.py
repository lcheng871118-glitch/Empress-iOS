# -*- coding: utf-8 -*-
"""修正：veekun 词典 en->zh 映射，再匹配 catalog slug。找出真实缺口。"""
import json, csv, re

ROOT = r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port'
catalog = json.load(open(ROOT + r'\game\client\data\catalog.json', encoding='utf-8'))

def build_en_zh(fn, idcol):
    en = {}
    zh = {}
    for r in csv.DictReader(open(ROOT + r'\scripts\dict' + fn, encoding='utf-8')):
        if r['local_language_id'] == '9':   # 英文
            en[r[idcol]] = r['name']
        elif r['local_language_id'] == '12':  # 简体中文
            zh[r[idcol]] = r['name']
    return en, zh

def slugify(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

# moves
mv_en, mv_zh = build_en_zh(r'\move_names.csv', 'move_id')
mv_map = {slugify(en): zh for mid, en in mv_en.items() for zh in [mv_zh.get(mid)] if zh}
# abilities
ab_en, ab_zh = build_en_zh(r'\ability_names.csv', 'ability_id')
ab_map = {slugify(en): zh for aid, en in ab_en.items() for zh in [ab_zh.get(aid)] if zh}

moves = catalog['moves']
abs_ = catalog['abilities']
mmiss = [m for m in moves if m not in mv_map]
amiss = [a for a in abs_ if a not in ab_map]
print('moves: %d 个，映射命中 %d，缺 %d' % (len(moves), len(moves)-len(mmiss), len(mmiss)))
if mmiss: print('  moves 缺口:', mmiss[:40])
print('abilities: %d 个，映射命中 %d，缺 %d' % (len(abs_), len(abs_)-len(amiss), len(amiss)))
if amiss: print('  abilities 缺口:', amiss[:40])

# species: 用 baseSpecies 英文名匹配
sp_en, sp_zh = build_en_zh(r'\pokemon_species_names.csv', 'pokemon_species_id')
sp_map = {slugify(en): zh for sid, en in sp_en.items() for zh in [sp_zh.get(sid)] if zh}

species = catalog['species']
plain = [s for s in species if not s.get('forme')]
miss_plain = [s for s in plain if slugify(s['name']) not in sp_map]
print()
print('无 forme 物种: %d，映射命中 %d，缺 %d' % (len(plain), len(plain)-len(miss_plain), len(miss_plain)))
nums_miss = sorted(set(s['num'] for s in miss_plain))
print('缺失 num 范围:', min(nums_miss), '-', max(nums_miss), ' 共 %d 个 num' % len(nums_miss))
print('缺样例:', [(s['num'], s['name']) for s in miss_plain[:15]])

# formed：baseSpecies 匹配
formed = [s for s in species if s.get('forme')]
fb = set(s['baseSpecies'] for s in formed)
fb_miss = [b for b in fb if slugify(b) not in sp_map]
print()
print('有 forme: %d，涉及 baseSpecies %d 个，其中缺简中 %d 个' % (len(formed), len(fb), len(fb_miss)))
print('baseSpecies 缺:', fb_miss[:30])

# 输出所有缺失的简中映射清单（供 PokéAPI 补充）
print()
print('=== 需要补充的完整列表 ===')
for s in miss_plain:
    print('SPECIES|%s|%s|%s' % (s['num'], s['id'], s['name']))
