# -*- coding: utf-8 -*-
"""
从桌面 Excel 导入荣誉数据
==========================

运行方式：
    python import_excel.py

作用：
    读取 EXCEL_FILE 指向的获奖信息表格，解析出荣誉数据并写出
    honors.json（供 generate_site.py 使用）。

说明：
    表格中「姓名」列存在竖向合并单元格（一个名字对应多条奖项），
    本脚本会先把合并单元格的值铺开到整个合并区域，再逐行读取，
    因此每条奖项都能正确对应到获得者。

    如表格内容有更新，先运行本脚本，再运行 generate_site.py 即可。
"""

import json
import re
import sys
from collections import Counter

import openpyxl

sys.stdout.reconfigure(encoding="utf-8")

# Excel 文件路径（按需修改）
EXCEL_FILE = r"C:/Users/lenovo/Desktop/团队获奖信息(1).xlsx"

OUT_FILE = "honors.json"


def build_value_map(ws):
    """读取工作表所有非空单元格，并把合并单元格的值铺开到整个区域。"""
    m = {}
    for row in ws.iter_rows():
        for c in row:
            if c.value is not None:
                s = str(c.value).strip()
                if s:
                    m[(c.row, c.column)] = s

    for mr in ws.merged_cells.ranges:
        top = (mr.min_row, mr.min_col)
        if top in m:
            val = m[top]
            for r in range(mr.min_row, mr.max_row + 1):
                for col in range(mr.min_col, mr.max_col + 1):
                    m.setdefault((r, col), val)
    return m


def extract(ws, m):
    def v(row, col):
        return m.get((row, col))

    def people(*coords):
        return [v(r, c) for (r, c) in coords if v(r, c)]

    honors = []

    # 论文发表 (C=期刊, E=标题, F..G=作者)
    for r in (4, 5, 6):
        j = v(r, 3)
        honors.append({'category': '论文发表', 'title': v(r, 5),
                       'subtitle': ('SCI' if j == 'sci' else j) or '',
                       'people': people((r, 6), (r, 7))})

    # 竞赛国赛 (C=标题, E=名字，E 列有竖向合并)
    #   标题带「河南省」的归入省赛
    national = []
    moved_to_provincial = []
    for r in range(18, 30):
        title = v(r, 3)
        item = {'category': '竞赛国赛', 'title': title,
                'subtitle': '', 'people': people((r, 5))}
        if '河南省' in (title or ''):
            item['category'] = '竞赛省赛'
            moved_to_provincial.append(item)
        else:
            national.append(item)
    honors.extend(national)

    # 软著 (C=名称, E..G=开发者)
    for r in range(36, 42):
        honors.append({'category': '软著', 'title': v(r, 3),
                       'subtitle': '', 'people': people((r, 5), (r, 6), (r, 7))})

    # 竞赛省赛 (C=标题, D=项目(可省), E..I=成员)
    for r in range(49, 57):
        honors.append({'category': '竞赛省赛', 'title': v(r, 3),
                       'subtitle': v(r, 4) or '',
                       'people': people((r, 5), (r, 6), (r, 7), (r, 8), (r, 9))})
    # 从国赛移入的带「河南省」条目，追加到省赛末尾
    honors.extend(moved_to_provincial)

    # 竞赛校赛 - spcp 项目 (D=标题, E..I=成员)
    for r in (68, 69, 70, 71):
        honors.append({'category': '竞赛校赛', 'title': v(r, 4),
                       'subtitle': '', 'people': people((r, 5), (r, 6), (r, 7), (r, 8), (r, 9))})

    # 竞赛校赛 - 气象大赛 (C=赛事, D=等级, E..O=成员)
    for r in (72, 73, 74):
        honors.append({'category': '竞赛校赛', 'title': '第二届气象大赛校赛',
                       'subtitle': v(r, 4) or '',
                       'people': people((r, 5), (r, 6), (r, 7), (r, 8), (r, 9),
                                        (r, 10), (r, 11), (r, 12), (r, 13), (r, 14), (r, 15))})

    # 竞赛校赛 - GIS 大赛 (C=标题, E=成员)
    for r in (75, 76):
        honors.append({'category': '竞赛校赛', 'title': v(r, 3),
                       'subtitle': '', 'people': people((r, 5))})

    # 其他证书 (C=名称, E=名字，E 列有竖向合并)
    for r in range(91, 94):
        honors.append({'category': '其他证书', 'title': v(r, 3),
                       'subtitle': '', 'people': people((r, 5))})

    # spcp 项目标注
    for h in honors:
        if h['category'] == '竞赛校赛' and re.match(r'^\d{4}\.', h['title'] or ''):
            h['subtitle'] = '大学生实践创新活动项目'

    return honors


def main():
    wb = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
    ws = wb['Sheet1']
    m = build_value_map(ws)
    honors = extract(ws, m)

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(honors, f, ensure_ascii=False, indent=2)

    print(f"[完成] 已生成 {OUT_FILE}，共 {len(honors)} 项：")
    for cat, n in Counter(h['category'] for h in honors).items():
        print(f"        {cat} {n} 项")
    missing = [h['title'] for h in honors if not h.get('people')]
    if missing:
        print(f"[提示] 以下 {len(missing)} 项没有对应名字：")
        for t in missing:
            print(f"        - {t}")


if __name__ == "__main__":
    main()
