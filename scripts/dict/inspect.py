# -*- coding: utf-8 -*-
"""检查词典 CSV 结构 + 简体中文覆盖率。"""
import csv

def load(fn):
    rows = list(csv.DictReader(open(fn, encoding='utf-8')))
    print('== %s ==' % fn)
    print('  列:', list(rows[0].keys()))
    return rows

sp = load(r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port\scripts\dict\pokemon_species_names.csv')
mv = load(r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port\scripts\dict\move_names.csv')
ab = load(r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port\scripts\dict\ability_names.csv')
ty = load(r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port\scripts\dict\type_names.csv')

print()
print('=== 语言 id 分布（species） ===')
from collections import Counter
print(Counter(r['local_language_id'] for r in sp))
print('=== 简中样例（language 12?） ===')
# 常见 veekun 语言id：9=en 11=ja 12=zh-Hans 13=zh-Hant?
for r in sp:
    if r['local_language_id'] in ('12','13') and r['pokemon_species_id'] in ('1','25','6','150'):
        print('  lang=%s id=%s -> %s' % (r['local_language_id'], r['pokemon_species_id'], r['name']))
print()
print('=== moves 简中样例 ===')
for r in mv:
    if r['local_language_id'] in ('12','13') and r['move_id'] in ('1','85','200'):
        print('  lang=%s id=%s -> %s' % (r['local_language_id'], r['move_id'], r['name']))
print()
print('=== abilities 简中样例 ===')
for r in ab:
    if r['local_language_id'] in ('12','13') and r['ability_id'] in ('1','2','65'):
        print('  lang=%s id=%s -> %s' % (r['local_language_id'], r['ability_id'], r['name']))
print()
print('=== types 简中 ===')
for r in ty:
    print('  lang=%s id=%s -> %s' % (r['local_language_id'], r['type_id'], r['name']))
