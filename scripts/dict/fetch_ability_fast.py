# -*- coding: utf-8 -*-
"""从 fetch.log 恢复已成功项，用连字符 slug 快速补齐能力缺口，dump ab_ext.json。"""
import json, time, urllib.request, re

DICT = r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port\scripts\dict'

# 1. 从日志恢复（可选；格式兼容两种成功行）
ab = {}
for line in open(DICT + r'\fetch.log', encoding='utf-8', errors='replace'):
    m = re.match(r'\s+([a-z0-9]+)\s+->\s+(\S+)', line.strip())
    if m:
        ab[m.group(1)] = m.group(2)
print('日志恢复 %d 个' % len(ab))
import csv
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
ab_en, ab_zh = build_en_zh(r'\ability_names.csv', 'ability_id')
ab_map = {slugify(en): zh for aid, en in ab_en.items() for zh in [ab_zh.get(aid)] if zh}
catalog = json.load(open(r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port\game\client\data\catalog.json', encoding='utf-8'))
need = [a for a in catalog['abilities'] if a not in ab_map]
print('缺失能力总数:', len(need))

HYPHEN = {
    'pastelveil': 'pastel-veil', 'quickdraw': 'quick-draw', 'neutralizinggas': 'neutralizing-gas',
    'screencleaner': 'screen-cleaner', 'cudchew': 'cud-chew', 'curiousmedicine': 'curious-medicine',
    'windrider': 'wind-rider', 'gorillatactics': 'gorilla-tactics', 'wanderingspirit': 'wandering-spirit',
    'mirrorarmor': 'mirror-armor', 'cottondown': 'cotton-down', 'ballfetch': 'ball-fetch',
    'steamengine': 'steam-engine', 'sandspit': 'sand-spit', 'gulpmissile': 'gulp-missile',
    'propellertail': 'propeller-tail', 'punkrock': 'punk-rock', 'steelyspirit': 'steely-spirit',
    'perishbody': 'perish-body', 'icescales': 'ice-scales', 'powerspot': 'power-spot',
    'iceface': 'ice-face', 'hungerswitch': 'hunger-switch', 'stalwart': 'stalwart',
    'intrepidsword': 'intrepid-sword', 'dauntlessshield': 'dauntless-shield', 'unseenfist': 'unseen-fist',
    'transistor': 'transistor', 'dragonsmaw': 'dragon-s-maw', 'chillingneigh': 'chilling-neigh',
    'grimneigh': 'grim-neigh', 'asoneglastrier': 'as-one-glastrier', 'asonespectrier': 'as-one-spectrier',
    'mindseye': 'mind-s-eye', 'lingeringaroma': 'lingering-aroma', 'wellbakedbody': 'well-baked-body',
    'zerotohero': 'zero-to-hero', 'commander': 'commander', 'electromorphosis': 'electromorphosis',
    'protosynthesis': 'protosynthesis', 'quarkdrive': 'quark-drive', 'goodasgold': 'good-as-gold',
    'toxicdebris': 'toxic-debris', 'supersweetsyrup': 'super-sweet-syrup', 'hospitality': 'hospitality',
    'costar': 'costar', 'tastysweet': 'tasty-sweet', 'empathicarmor': 'empathic-armor',
    'opportunist': 'opportunist', 'dispensingsand': 'dispensing-sand', 'blackglasses': 'black-glasses',
    'mountainstorm': 'mountain-storm', 'poisonpuppeteer': 'poison-puppeteer', 'stakeout': 'stakeout',
    'download': 'download', 'defiant': 'defiant', 'synchronize': 'synchronize',
    'frisk': 'frisk', 'infiltrator': 'infiltrator', 'illuminate': 'illuminate',
    'pickpocket': 'pickpocket', 'harvest': 'harvest', 'magicbounce': 'magic-bounce',
    'teravolt': 'teravolt', 'turboblaze': 'turboblaze', 'moxie': 'moxie',
}

def fetch(url, tries=2):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'empress-l10n/1.0'})
            return json.load(urllib.request.urlopen(req, timeout=20))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(1)
        except Exception:
            time.sleep(1)
    return None

for slug in need:
    if slug in ab and ab[slug]:
        continue
    api = HYPHEN.get(slug, slug)
    d = fetch('https://pokeapi.co/api/v2/ability/%s/' % api)
    zh = None
    if d:
        zh = next((n['name'] for n in d.get('names', []) if n['language']['name'] == 'zh-hans'), None)
    if zh:
        ab[slug] = zh
        print('OK %s -> %s' % (slug, zh))
    else:
        print('MISS %s (api=%s)' % (slug, api))
    time.sleep(0.35)

json.dump(ab, open(DICT + r'\ab_ext.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
still = [s for s in need if s not in ab or not ab[s]]
print('done. 补齐 %d / %d，仍缺 %d: %s' % (len(need) - len(still), len(need), len(still), still[:50]))
