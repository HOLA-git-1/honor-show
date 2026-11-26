# -*- coding: utf-8 -*-
"""
课题组荣誉展示页面生成器
=========================

运行方式：
    python generate_site.py

作用：
    读取同目录下的荣誉数据文件 honors.json 以及校徽图 logo.png，
    生成一个自包含的 index.html 网页（HTML + CSS + JavaScript + 校徽
    全部内嵌在一个文件里），双击即可在浏览器中打开，无需联网、无需服务器。

风格说明：
    参考实验室 / 课题组网站的介绍页，整体简洁克制——单色系、细分割线、
    按类别分栏的列表，右上角放置校徽。

如何修改内容：
    1. 修改 SITE_NAME / INTRO 等顶部常量；
    2. 替换同目录下的 logo.png（校徽，文件名保持不变）；
    3. 编辑 honors.json 中的荣誉数据（每条含 category / title /
       subtitle / people 字段）；
    4. 重新运行本脚本即可。
"""

import base64
import json
import os
import sys
from datetime import date

# 让 Windows 控制台用 UTF-8 输出，避免打印中文/emoji 时出现 GBK 编码报错
sys.stdout.reconfigure(encoding="utf-8")


# ----------------------------------------------------------------------
# 一、站点基础信息（可改）
# ----------------------------------------------------------------------
SITE_NAME = "气溶胶与气候变化课题组"   # 左上角课题组名称
SITE_EN = "Aerosol & Climate Change Research Group"  # 英文名
PAGE_TITLE = "荣誉展示"               # 页面主标题
INTRO = (                             # 标题下方的一段简介
    "本页面汇总课题组近年来发表的论文、获得的竞赛奖项、"
    "软件著作权与相关证书。"
)
LOGO_FILE = "logo.png"                # 校徽文件名（放在本脚本同目录）
DATA_FILE = "honors.json"             # 荣誉数据文件（放在本脚本同目录）


# ----------------------------------------------------------------------
# 二、分类与成员称谓
# ----------------------------------------------------------------------
# 顶部筛选栏按此顺序生成；第一项「全部」表示不筛选。
CATEGORIES = [
    "全部",
    "论文发表",
    "竞赛国赛",
    "软著",
    "竞赛省赛",
    "竞赛校赛",
    "其他证书",
]

# 各类别下成员列表的前缀称谓。
PEOPLE_LABEL = {
    "论文发表": "作者",
    "软著": "开发者",
    "竞赛国赛": "获得者",
    "竞赛省赛": "获得者",
    "竞赛校赛": "获得者",
    "其他证书": "获得者",
}


# ----------------------------------------------------------------------
# 三、读取荣誉数据（honors.json）
# ----------------------------------------------------------------------
# honors.json 中每条记录字段：
#   category : 类别，须与 CATEGORIES 中一致
#   title    : 标题（论文题目 / 奖项名称 / 软件名称 / 证书名称）
#   subtitle : 补充信息（期刊名 / 获奖等级 / 项目名称，可省略）
#   people   : 成员姓名列表（可省略）
# ----------------------------------------------------------------------
def load_honors():
    if not os.path.exists(DATA_FILE):
        print(f"[警告] 未找到 {DATA_FILE}，页面将没有任何荣誉条目。")
        return []
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


HONORS = load_honors()


# ----------------------------------------------------------------------
# 四、为每条数据补全展示字段
# ----------------------------------------------------------------------
def prepare(honors):
    """把每条的 subtitle / people 转成展示用字段 meta / people / people_label。"""
    result = []
    for h in honors:
        people = h.get("people") or []
        label = PEOPLE_LABEL.get(h.get("category"), "获得者")
        result.append({
            "category": h["category"],
            "title": h["title"],
            "meta": h.get("subtitle") or "",
            "people": people,
            "people_label": label,
        })
    return result


# ----------------------------------------------------------------------
# 五、读取校徽并转成 base64（内嵌进 HTML，避免图片路径失效）
# ----------------------------------------------------------------------
def load_logo():
    """读取 logo.png，返回 base64 数据。若文件不存在则返回空字符串。"""
    if not os.path.exists(LOGO_FILE):
        print(f"[警告] 未找到 {LOGO_FILE}，页面将不显示校徽。")
        return ""
    with open(LOGO_FILE, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


# ----------------------------------------------------------------------
# 六、CSS 样式（内嵌）
# ----------------------------------------------------------------------
CSS = """
:root {
    --text: #1f2328;      /* 正文 */
    --muted: #6b7280;     /* 次要文字 */
    --accent: #1f4e79;    /* 主色：学术深蓝，仅用于标题下划线与选中态 */
    --line: #e5e7eb;      /* 分割线 */
    --hover: #f6f8fa;     /* 行悬停底色 */
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: var(--text);
    background: #d8e6f3;    /* 学术浅蓝背景 */
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
}

/* 页面容器：限宽、左对齐 */
.page { max-width: 880px; margin: 0 auto; padding: 40px 24px 64px; }

/* 顶部单位条：左侧课题组名 + 英文名，右侧校徽，下方一道深蓝粗线 */
.masthead {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 14px;
    border-bottom: 2px solid var(--accent);
}
.masthead .brand { display: flex; flex-direction: column; }
.masthead .site-name { font-size: 18px; font-weight: 600; letter-spacing: 1px; }
.masthead .site-en  { font-size: 12px; color: var(--muted); margin-top: 2px; }
.masthead .logo { height: 52px; width: auto; }

/* 标题区 */
.heading { margin-top: 36px; }
.heading h1 { font-size: 28px; font-weight: 600; }
.heading .intro { color: var(--muted); font-size: 14px; margin-top: 8px; max-width: 640px; }

/* 搜索框 */
.search {
    width: 100%; margin-top: 26px;
    padding: 9px 14px; font-size: 14px; color: var(--text);
    border: 1px solid var(--line); border-radius: 4px;
    outline: none; background: #fff;
}
.search:focus { border-color: var(--accent); }

/* 分类筛选：文字标签，选中项加下划线（横向 tab 风格） */
.toolbar {
    display: flex; align-items: center; justify-content: space-between;
    margin-top: 20px; border-bottom: 1px solid var(--line);
}
.filters { display: flex; gap: 22px; flex-wrap: wrap; }
.filter-btn {
    background: none; border: none; cursor: pointer;
    padding: 8px 0; margin-bottom: -1px;
    font-size: 14px; color: var(--muted);
    border-bottom: 2px solid transparent;
}
.filter-btn:hover { color: var(--text); }
.filter-btn.active { color: var(--accent); border-bottom-color: var(--accent); font-weight: 600; }
.count { font-size: 13px; color: var(--muted); flex-shrink: 0; margin-left: 12px; }

/* 荣誉列表：行间细线分隔 */
.list { list-style: none; margin-top: 4px; }
.item { padding: 16px 4px; border-bottom: 1px solid var(--line); }
.item:hover { background: var(--hover); }
.item .title { font-size: 16px; font-weight: 600; }
.item .meta { color: var(--accent); font-size: 13px; margin-top: 2px; }

/* 成员姓名：每个名字一枚标签徽章，逐条一一对应 */
.item .desc { display: flex; align-items: center; flex-wrap: wrap; margin-top: 8px; }
.item .people-label { color: var(--muted); font-size: 13px; margin-right: 6px; }
.item .name-tag {
    display: inline-block;
    padding: 2px 12px;
    margin: 3px 8px 3px 0;
    font-size: 13px;
    font-weight: 500;
    color: #ffffff;
    background: var(--accent);
    border: 1px solid var(--accent);
    border-radius: 999px;
}

/* 类别分组标题（仅「全部」视图显示） */
.section {
    list-style: none;
    padding: 30px 4px 10px;
}
.section h2 {
    font-size: 15px; font-weight: 600;
    color: var(--accent); letter-spacing: 1px;
    padding-left: 10px; border-left: 3px solid var(--accent);
}

/* 空状态 */
.empty {
    display: none; text-align: center; color: var(--muted);
    padding: 48px 0; font-size: 14px;
}

/* 页脚 */
.footer {
    margin-top: 48px; padding-top: 16px;
    border-top: 1px solid var(--line);
    text-align: center; color: var(--muted); font-size: 12px;
}

@media (max-width: 600px) {
    .page { padding: 28px 18px 48px; }
    .heading h1 { font-size: 22px; }
    .masthead .logo { height: 40px; }
    .filters { gap: 16px; }
}
"""


# ----------------------------------------------------------------------
# 七、JavaScript 脚本（内嵌）
# ----------------------------------------------------------------------
# {{DATA}} / {{CATS}} 为占位符，稍后由 Python 用 JSON 数据替换。
JS = """
const HONORS = {{DATA}};      // 荣誉数据，由 Python 注入
const CATEGORIES = {{CATS}};  // 分类列表，由 Python 注入

const listEl  = document.getElementById('list');
const emptyEl = document.getElementById('empty');
const countEl = document.getElementById('count');
const searchEl = document.getElementById('search');
const filtersEl = document.getElementById('filters');

let currentCategory = '全部';
let keyword = '';

// 生成单条荣誉的 HTML（成员名字渲染为独立标签徽章）
function itemHTML(h) {
    const tags = (h.people || []).map(p => `<span class="name-tag">${p}</span>`).join('');
    const peopleHtml = tags
        ? `<div class="desc"><span class="people-label">${h.people_label}</span>${tags}</div>`
        : '';
    return `
        <li class="item">
            <div class="body">
                <div class="title">${h.title}</div>
                ${h.meta ? `<div class="meta">${h.meta}</div>` : ''}
                ${peopleHtml}
            </div>
        </li>`;
}

// 按当前分类 + 关键词过滤并渲染列表
function render() {
    const filtered = HONORS.filter(h => {
        const okCat = currentCategory === '全部' || h.category === currentCategory;
        const text  = (h.title + h.meta + (h.people || []).join('')).toLowerCase();
        const okKey = text.includes(keyword.toLowerCase());
        return okCat && okKey;
    });

    let html = '';
    if (currentCategory === '全部') {
        // 按类别分组展示，各组之间加标题
        for (const cat of CATEGORIES.filter(c => c !== '全部')) {
            const group = filtered.filter(h => h.category === cat);
            if (!group.length) continue;
            html += `<li class="section"><h2>${cat}</h2></li>`;
            html += group.map(itemHTML).join('');
        }
    } else {
        html = filtered.map(itemHTML).join('');
    }

    listEl.innerHTML = html;
    emptyEl.style.display = filtered.length ? 'none' : 'block';
    countEl.textContent = `共 ${filtered.length} 项`;
}

// 生成分类筛选标签
function buildFilters() {
    filtersEl.innerHTML = CATEGORIES.map(c =>
        `<button class="filter-btn${c === '全部' ? ' active' : ''}" data-cat="${c}">${c}</button>`
    ).join('');

    filtersEl.addEventListener('click', e => {
        const btn = e.target.closest('.filter-btn');
        if (!btn) return;
        currentCategory = btn.dataset.cat;
        filtersEl.querySelectorAll('.filter-btn')
                .forEach(b => b.classList.toggle('active', b === btn));
        render();
    });
}

// 搜索框输入（防抖 150ms）
function buildSearch() {
    let timer;
    searchEl.addEventListener('input', e => {
        clearTimeout(timer);
        timer = setTimeout(() => { keyword = e.target.value; render(); }, 150);
    });
}

buildFilters();
buildSearch();
render();
"""


# ----------------------------------------------------------------------
# 八、HTML 页面模板
# ----------------------------------------------------------------------
# {logo} 为校徽的 base64 数据（若没有校徽则为空字符串，不渲染 <img>）。
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title} · {site_name}</title>
<style>
{css}
</style>
</head>
<body>
<div class="page">

    <div class="masthead">
        <div class="brand">
            <span class="site-name">{site_name}</span>
            <span class="site-en">{site_en}</span>
        </div>
        <img class="logo" src="data:image/png;base64,{logo}" alt="校徽">
    </div>

    <div class="heading">
        <h1>{page_title}</h1>
        <p class="intro">{intro}</p>
    </div>

    <input class="search" id="search" type="text" placeholder="搜索奖项、论文、软件或成员姓名…">

    <div class="toolbar">
        <div class="filters" id="filters"></div>
        <span class="count" id="count"></span>
    </div>

    <ul class="list" id="list"></ul>
    <div class="empty" id="empty">没有找到匹配的内容，换个关键词试试。</div>

    <div class="footer">© {year} {site_name} · 荣誉展示</div>

</div>
<script>
{js}
</script>
</body>
</html>
"""


# ----------------------------------------------------------------------
# 九、生成网页
# ----------------------------------------------------------------------
def main():
    """主流程：准备数据 -> 读取校徽 -> 填充模板 -> 写出 index.html"""
    honors = prepare(HONORS)
    logo_b64 = load_logo()

    # 把 JS 里的占位符替换成真实 JSON 数据
    js = JS.replace("{{DATA}}", json.dumps(honors, ensure_ascii=False))
    js = js.replace("{{CATS}}", json.dumps(CATEGORIES, ensure_ascii=False))

    html = HTML_TEMPLATE.format(
        page_title=PAGE_TITLE,
        site_name=SITE_NAME,
        site_en=SITE_EN,
        intro=INTRO,
        css=CSS,
        js=js,
        logo=logo_b64,
        year=date.today().year,
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    from collections import Counter
    counts = Counter(h["category"] for h in honors)
    print(f"[完成] 生成成功！共 {len(honors)} 项：")
    for cat in CATEGORIES[1:]:
        print(f"        {cat} {counts.get(cat, 0)} 项")
    print("       请用浏览器打开 index.html 查看效果。")


if __name__ == "__main__":
    main()
