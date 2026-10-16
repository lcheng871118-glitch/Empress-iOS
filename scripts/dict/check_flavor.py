# -*- coding: utf-8 -*-
"""检查 move_flavor_text 简中覆盖。"""
import csv
from collections import Counter
rows = list(csv.DictReader(open(r'D:\下载地方\宝可梦竞技场2D\Empress-iOS-Port\scripts\dict\move_flavor_text.csv', encoding='utf-8')))
print('COLUMNS', list(rows[0].keys()))
print('LANGDIST', Counter(r['language_id'] for r in rows).most_common(18))
for r in rows:
    if r['language_id'] == '12' and r['move_id'] in ('1', '85'):
        print('MOVE', r['move_id'], 'VG', r['version_group_id'], r['flavor_text'][:80])
# 简中各 move 的 flavor 条数（按 version_group 取最新的）
zh = [r for r in rows if r['language_id'] == '12']
vg = Counter(r['version_group_id'] for r in zh)
print('ZHVG', vg)
