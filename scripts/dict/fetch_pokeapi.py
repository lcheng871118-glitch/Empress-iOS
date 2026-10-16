# -*- coding: utf-8 -*-
"""从 PokéAPI 补齐缺失的官方简中译名（物种 + 特性），输出 sp_ext.json / ab_ext.json。"""
import json, csv, re, time, urllib.request

ROOT = r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port'
DICT = ROOT + r'\scripts\dict'
catalog = json.load(open(ROOT + r'\game\client\data\catalog.json', encoding='utf-8'))

def build_en_zh(fn, idcol):
    en, zh = {}, {}
    for r in csv.DictReader(open(DICT + fn, encoding='utf-8')):
        if r['local_language_id'] == '9':
            en[r[idcol]] = r['name']
        elif r['local_language_id'] == '12':
            zh[r[idcol]] = r['name']
    return en, zh

def slugify(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

def fetch(url, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'empress-l10n/1.0 (l10n tooling)'})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            print('  retry %s (%s): %s' % (i + 1, url.split('/')[-1], e))
            time.sleep(2 + i * 3)
    return None

def zh_name(d):
    if not d:
        return None
    for n in d.get('names', []):
        if n['language']['name'] == 'zh-hans':
            return n['name']
    return None

# ---- 1. species 缺口 ----
sp_en, sp_zh = build_en_zh(r'\pokemon_species_names.csv', 'pokemon_species_id')
sp_map = {slugify(en): zh for sid, en in sp_en.items() for zh in [sp_zh.get(sid)] if zh}
species = catalog['species']
plain = [s for s in species if not s.get('forme')]
miss_plain = [s for s in plain if slugify(s['name']) not in sp_map]
miss_nums = sorted(set(s['num'] for s in miss_plain))
print('物种缺口 num 数:', len(miss_nums), '范围', miss_nums[0], '-', miss_nums[-1])

# 特例手工兜底（仅限确认的官方简中译名；字符 slug 问题导致 veekun 未命中）
MANUAL_SPECIES = {
    29: '尼多兰', 32: '尼多朗', 669: '花蓓蓓', 865: '葱游兵', 866: '踏冰人偶',
}
sp_ext = {}
for num in miss_nums:
    if num in MANUAL_SPECIES:
        sp_ext[str(num)] = MANUAL_SPECIES[num]
        print('  manual %d -> %s' % (num, MANUAL_SPECIES[num]))
        continue
    d = fetch('https://pokeapi.co/api/v2/pokemon-species/%d/' % num)
    zh = zh_name(d)
    if zh:
        sp_ext[str(num)] = zh
        print('  %d -> %s' % (num, zh))
    else:
        print('  !! %d 无 zh-hans' % num)
    time.sleep(0.55)

json.dump(sp_ext, open(DICT + r'\sp_ext.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('species 补充完成:', len(sp_ext))

# ---- 2. abilities 缺口 ----
ab_en, ab_zh = build_en_zh(r'\ability_names.csv', 'ability_id')
ab_map = {slugify(en): zh for aid, en in ab_en.items() for zh in [ab_zh.get(aid)] if zh}
abs_ = catalog['abilities']
amiss = [a for a in abs_ if a not in ab_map]
print('特性缺口:', len(amiss))

MANUAL_AB = {}
ab_ext = {}
for slug in amiss:
    if slug in MANUAL_AB:
        ab_ext[slug] = MANUAL_AB[slug]
        print('  manual %s -> %s' % (slug, MANUAL_AB[slug]))
        continue
    d = fetch('https://pokeapi.co/api/v2/ability/%s/' % slug)
    zh = zh_name(d)
    if zh:
        ab_ext[slug] = zh
        print('  %s -> %s' % (slug, zh))
    else:
        print('  !! %s 无 zh-hans' % slug)
    time.sleep(0.55)

json.dump(ab_ext, open(DICT + r'\ab_ext.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('特性补充完成:', len(ab_ext))
