# -*- coding: utf-8 -*-
"""汉化 catalog.json：species/moves/abilities/trainers 名称 + 形态规则 + move 官方简中描述。
只改显示字段（name/baseSpecies/shortDesc/rules.description），逻辑字段（id/num/types/category 等）不动。
"""
import json, csv, re, shutil

ROOT = r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port'
DICT = ROOT + r'\scripts\dict'
CATALOG = ROOT + r'\game\client\data\catalog.json'

def slugify(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

def load_en_zh(fn, idcol):
    en, zh = {}, {}
    for r in csv.DictReader(open(DICT + fn, encoding='utf-8')):
        if r['local_language_id'] == '9':
            en[r[idcol]] = r['name']
        elif r['local_language_id'] == '12':
            zh[r[idcol]] = r['name']
    return en, zh

# ---- 词典装载 ----
sp_en, sp_zh = load_en_zh(r'\pokemon_species_names.csv', 'pokemon_species_id')
sp_map = {slugify(en): zh for sid, en in sp_en.items() for zh in [sp_zh.get(sid)] if zh}
sp_ext = json.load(open(DICT + r'\sp_ext.json', encoding='utf-8'))

mv_en, mv_zh = load_en_zh(r'\move_names.csv', 'move_id')
mv_map = {slugify(en): zh for mid, en in mv_en.items() for zh in [mv_zh.get(mid)] if zh}

ab_en, ab_zh = load_en_zh(r'\ability_names.csv', 'ability_id')
ab_map = {slugify(en): zh for aid, en in ab_en.items() for zh in [ab_zh.get(aid)] if zh}
ab_ext = json.load(open(DICT + r'\ab_ext.json', encoding='utf-8'))

# move flavor（简中，vg18 优先 vg17 兜底）
flavor = {}
for r in csv.DictReader(open(DICT + r'\move_flavor_text.csv', encoding='utf-8')):
    if r['language_id'] != '12':
        continue
    key = (r['move_id'], r['version_group_id'])
    flavor[key] = r['flavor_text'].replace('\n', '')
mv_flavor = {}
for mid, en in mv_en.items():
    zhf = None
    for vg in ('18', '17'):
        if (mid, vg) in flavor:
            zhf = flavor[(mid, vg)]
            break
    if zhf:
        mv_flavor[slugify(en)] = zhf
print('flavor 简中可匹配 move:', len(mv_flavor))

# ---- 形态规则（官方译名；未列出的用「（英文forme）」兜底） ----
FORMES = {
    'Mega': ('超级', 'pre', ''), 'Mega-X': ('超级', 'pre', 'X'), 'Mega-Y': ('超级', 'pre', 'Y'),
    'Gmax': ('超极巨化', 'pre', ''),
    'Alola': ('阿罗拉', 'pre'), 'Galar': ('伽勒尔', 'pre'), 'Hisui': ('洗翠', 'pre'),
    'Totem': ('霸主', 'pre'), 'Alola-Totem': ('阿罗拉霸主', 'pre'), 'Galar-Totem': ('伽勒尔霸主', 'pre'),
    'Primal': ('原始', 'pre'),
    'Origin': ('（起源形态）', 'suf'),
    'Therian': ('（灵兽形态）', 'suf'),
    'Ultra': ('究极', 'pre'),
    'Unbound': ('（解放形态）', 'suf'),
    'Eternamax': ('无极巨化', 'pre'),
    'Dawn-Wings': ('（拂晓之翼）', 'suf'), 'Dusk-Mane': ('（黄昏之鬃）', 'suf'),
    'Complete': ('（完全体形态）', 'suf'),
    '10%': ('（10%形态）', 'suf'), '50%': ('（50%形态）', 'suf'),
    'Ash': ('小智', 'pre'), 'Bond': ('（牵绊变身）', 'suf'),
    'Zen': ('（达摩模式）', 'suf'), 'Galar-Zen': ('（伽勒尔达摩模式）', 'suf'),
    'Heat': ('加热', 'pre'), 'Wash': ('清洗', 'pre'), 'Frost': ('结冰', 'pre'), 'Fan': ('风扇', 'pre'), 'Mow': ('割草', 'pre'),
    'Sky': ('天空', 'pre'),
    'F': ('（雌性）', 'suf'), 'M': ('（雄性）', 'suf'),
    'East': ('（东）', 'suf'), 'West': ('（西）', 'suf'),
    'Sandy': ('（沙尘）', 'suf'), 'Trash': ('（垃圾）', 'suf'),
    'Large': ('（大）', 'suf'), 'Small': ('（小）', 'suf'), 'Super': ('（超大）', 'suf'),
    'Black': ('（黑）', 'suf'), 'White': ('（白）', 'suf'),
    'Blue': ('（蓝）', 'suf'), 'Yellow': ('（黄）', 'suf'), 'Green': ('（绿）', 'suf'), 'Red': ('（红）', 'suf'),
    'Rainy': ('（雨天）', 'suf'), 'Snowy': ('（雪天）', 'suf'), 'Sunny': ('（晴天）', 'suf'),
    'Gulping': ('（一口吞形态）', 'suf'), 'Gorging': ('（大口吞形态）', 'suf'),
    'Low-Key': ('（低调形态）', 'suf'),
    'Dada': ('（老爹形态）', 'suf'),
    'Rapid-Strike': ('（一击流）', 'suf'),
    'Bloodmoon': ('（血月形态）', 'suf'),
    'Stellar': ('（星晶形态）', 'suf'),
    'Terastal': ('（太晶形态）', 'suf'),
    'Hero': ('（英雄形态）', 'suf'),
    'School': ('（学校形态）', 'suf'),
    'Midnight': ('（午夜形态）', 'suf'),
    'Antique': ('（古董形态）', 'suf'),
    'Crowned': None,  # 特判（苍响/藏玛然特）
    # 属性类（阿尔宙斯/银伴战兽）
    'Bug': ('（虫）', 'suf'), 'Dark': ('（恶）', 'suf'), 'Dragon': ('（龙）', 'suf'),
    'Electric': ('（电）', 'suf'), 'Fairy': ('（妖精）', 'suf'), 'Fighting': ('（格斗）', 'suf'),
    'Fire': ('（火）', 'suf'), 'Flying': ('（飞行）', 'suf'), 'Ghost': ('（幽灵）', 'suf'),
    'Grass': ('（草）', 'suf'), 'Ground': ('（地面）', 'suf'), 'Poison': ('（毒）', 'suf'),
    'Psychic': ('（超能力）', 'suf'), 'Rock': ('（岩石）', 'suf'), 'Steel': ('（钢）', 'suf'),
    'Water': ('（水）', 'suf'),
}
CROWNED = {'zacian': '（剑之王）', 'zamazenta': '（盾之王）'}

def species_zh(name_en, num):
    if num is not None and str(num) in sp_ext:
        return sp_ext[str(num)]
    return sp_map.get(slugify(name_en), name_en)

def forme_name(base_zh, forme, sid):
    if forme == 'Crowned':
        for k, v in CROWNED.items():
            if k in sid:
                return base_zh + v
        return base_zh + '（剑之王）'
    rule = FORMES.get(forme)
    if rule:
        kind = rule[1]
        post = rule[2] if len(rule) > 2 else ''
        return (rule[0] + base_zh + post) if kind == 'pre' else (base_zh + rule[0] + post)
    return base_zh + '（' + forme + '）'

# ---- 主处理 ----
c = json.load(open(CATALOG, encoding='utf-8'))

miss_species, miss_move, miss_ab = [], [], []
for s in c['species']:
    base_zh = species_zh(s['baseSpecies'], s.get('num'))
    if s.get('forme'):
        zh = forme_name(base_zh, s['forme'], s['id'])
    else:
        zh = base_zh
    if zh == s['baseSpecies']:
        miss_species.append((s['id'], s['baseSpecies']))
    s['name'] = zh
    s['baseSpecies'] = base_zh

for k, m in c['moves'].items():
    zh = mv_map.get(slugify(m['name']))
    if not zh:
        miss_move.append((k, m['name']))
    else:
        m['name'] = zh
    if k in mv_flavor and 'shortDesc' in m:
        m['shortDesc'] = mv_flavor[k]

for k, a in c['abilities'].items():
    zh = ab_map.get(k) or ab_ext.get(k)
    if not zh:
        miss_ab.append((k, a['name']))
    else:
        if 'enName' not in a:
            a['enName'] = a['name']  # 保留英文原名（服务端逻辑与前端反查用）
        a['name'] = zh

TRAINERS = {
    'red': '赤红', 'blue': '青绿', 'ethan': '阿响', 'lyra': '琴音',
    'brendan': '小悠', 'may': '小遥', 'lucas': '光辉', 'dawn': '小光',
    'brock': '小刚', 'misty': '小霞', 'ltsurge': '马志士', 'erika': '莉佳',
    'koga': '阿桔', 'sabrina': '娜姿', 'blaine': '夏伯', 'giovanni': '坂木',
    'lance': '渡', 'cynthia': '竹兰', 'steven': '大吾', 'iris': '艾莉丝',
}
for t in c['trainers']:
    if t['id'] in TRAINERS:
        t['name'] = TRAINERS[t['id']]

c['rules']['description'] = '基于正版基础数据的实时竞技场适配：基础种族值、属性、招式威力、PP、命中率与受支持的效果。部分宝可梦的小型自学技能池可能少于四个槽位。特性效果以服务端规则集为准。'

# 备份英文原版
shutil.copyfile(CATALOG, DICT + r'\catalog.en.json')
json.dump(c, open(CATALOG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('species 未命中:', len(miss_species), miss_species[:20])
print('moves 未命中:', len(miss_move), miss_move[:20])
print('abilities 未命中:', len(miss_ab), miss_ab[:20])
print('species 数:', len(c['species']), 'moves:', len(c['moves']), 'abilities:', len(c['abilities']))
print('OK catalog.json 已汉化')
