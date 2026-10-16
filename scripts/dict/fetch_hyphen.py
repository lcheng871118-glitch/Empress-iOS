# -*- coding: utf-8 -*-
"""对 404 的特性用连字符 slug 重查 PokéAPI，合并进 ab_ext.json。"""
import json, time, urllib.request, re

DICT = r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port\scripts\dict'
ab_ext = json.load(open(DICT + r'\ab_ext.json', encoding='utf-8'))

def fetch(url, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'empress-l10n/1.0'})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            time.sleep(2 + i * 3)
    return None

# 游戏 slug -> PokéAPI 连字符 slug
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
}
missing = [k for k in ab_ext if not ab_ext[k] or ab_ext[k] == '']
for slug in missing:
    api = HYPHEN.get(slug, slug)
    d = fetch('https://pokeapi.co/api/v2/ability/%s/' % api)
    if d:
        zh = next((n['name'] for n in d.get('names', []) if n['language']['name'] == 'zh-hans'), None)
        if zh:
            ab_ext[slug] = zh
            print('OK %s -> %s' % (slug, zh))
        else:
            print('!! %s(api %s) 无 zh-hans' % (slug, api))
    else:
        print('!! %s(api %s) 请求失败' % (slug, api))
    time.sleep(0.5)

json.dump(ab_ext, open(DICT + r'\ab_ext.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('done, 剩余缺失:', [k for k, v in ab_ext.items() if not v or v == ''])
