# -*- coding: utf-8 -*-
"""探查游戏文本量：UI 文案 / 数据名称 / 剧情文本分布。"""
import json, re, os, glob

ROOT = r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port\game'

def count_strings(text, lang='en'):
    """粗略统计可读英文文本字符串数量（引号内的英文长串 + 常见 UI 词）"""
    # 引号内内容，长度>=2，含字母
    quoted = re.findall(r"['\"]([A-Za-z][A-Za-z 0-9'?!.,:;()\-/&%]{1,})['\"]", text)
    return len(quoted)

print('=== client/ 文件 ===')
for f in sorted(glob.glob(os.path.join(ROOT, 'client', '*'))):
    if os.path.isfile(f):
        sz = os.path.getsize(f)
        print('  %-28s %8.1f KB' % (os.path.basename(f), sz / 1024))

print()
print('=== 各文件可读英文字符串数量（引号内英文，粗略） ===')
total = 0
for f in sorted(glob.glob(os.path.join(ROOT, 'client', '*')) + glob.glob(os.path.join(ROOT, 'server', '*.cjs'))):
    if os.path.isfile(f) and f.endswith(('.js', '.mjs', '.html', '.cjs')):
        try:
            txt = open(f, encoding='utf-8').read()
        except Exception as e:
            txt = open(f, encoding='utf-8', errors='replace').read()
        n = count_strings(txt)
        total += n
        print('  %-32s %6d 条' % (os.path.basename(f), n))
print('  合计: %d 条' % total)

print()
print('=== catalog.json 数据结构 ===')
catalog = json.load(open(os.path.join(ROOT, 'client', 'data', 'catalog.json'), encoding='utf-8'))
print('  keys:', list(catalog.keys())[:20])
if 'species' in catalog:
    sp = catalog['species']
    print('  species 数量:', len(sp))
    if sp:
        print('  样例条目:', json.dumps(sp[0], ensure_ascii=False)[:300])
# 其他顶层结构
for k in catalog:
    if isinstance(catalog[k], list) and k != 'species':
        print('  %s: %d 条' % (k, len(catalog[k])))
        if catalog[k]:
            print('    样例:', json.dumps(catalog[k][0], ensure_ascii=False)[:200])
    elif isinstance(catalog[k], dict) and k != 'speciesById':
        print('  %s: dict keys=%s' % (k, list(catalog[k].keys())[:10]))

print()
print('=== story.cjs / campaign.cjs 剧情文本量 ===')
for f in ['story.cjs', 'campaign.cjs']:
    p = os.path.join(ROOT, 'server', f)
    if os.path.exists(p):
        txt = open(p, encoding='utf-8').read()
        # 找长文本（>40 字符的引号内英文，剧情/描述）
        long = re.findall(r"['\"]([A-Za-z][^'\"]{40,})['\"]", txt)
        print('  %s: 长文本 %d 条' % (f, len(long)))
        for s in long[:3]:
            print('    -', s[:120])
