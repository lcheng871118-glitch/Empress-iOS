# -*- coding: utf-8 -*-
"""对仍缺的 28 个特性：拉全量列表按英文名规范化匹配 -> 按 id 取 zh-hans。"""
import json, time, re, urllib.request

DICT = r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port\scripts\dict'
catalog = json.load(open(r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port\game\client\data\catalog.json', encoding='utf-8'))
ab_ext = json.load(open(DICT + r'\ab_ext.json', encoding='utf-8'))

def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

def fetch(url, tries=3):
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

# 仍缺的能力
need = [s for s in catalog['abilities'] if s not in ab_ext or not ab_ext[s]]
print('仍缺 %d: %s' % (len(need), need))

# 全量列表
lst = fetch('https://pokeapi.co/api/v2/ability?limit=2000')
all_ab = {norm(r['name']): r['url'] for r in lst['results']}
print('API 全量能力数:', len(all_ab))

for slug in need:
    en_name = catalog['abilities'][slug].get('name', slug)
    key = norm(en_name)
    url = all_ab.get(key)
    if not url:
        print('MISS %s (en=%r 列表无匹配)' % (slug, en_name))
        continue
    d = fetch(url)
    zh = None
    if d:
        zh = next((n['name'] for n in d.get('names', []) if n['language']['name'] == 'zh-hans'), None)
    if zh:
        ab_ext[slug] = zh
        print('OK %s (%s) -> %s' % (slug, en_name, zh))
    else:
        print('MISS %s (%s) 详情无 zh-hans' % (slug, en_name))
    time.sleep(0.3)

json.dump(ab_ext, open(DICT + r'\ab_ext.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
still = [s for s in need if s not in ab_ext or not ab_ext[s]]
print('done, 仍缺 %d: %s' % (len(still), still))
