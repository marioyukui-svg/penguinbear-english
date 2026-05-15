#!/usr/bin/env python3
"""将 语法_副本/ 中的 md 文件批量转为统一风格的 HTML"""
import os, re, html as htmlmod

SRC = "/Users/xuan/Desktop/OH-WorkSpace/语法_副本"
DST_BASE = "/Users/xuan/Desktop/OH-WorkSpace/penguinbear-english"

# 分类映射：文件名 → 目标子目录
CATEGORY = {
    # 小学
    "小学语法 be动词的用法.md": "elementary/be动词的用法.html",
    "小学语法 can的用法 翻译.md": "elementary/can的用法.html",
    "小学语法 have got 的用法.md": "elementary/have_got的用法.html",
    "小学语法 like doing类动词.md": "elementary/like_doing类动词.html",
    "小学语法 一般现在时态.md": "elementary/一般现在时态.html",
    "小学语法 主语为第三人称单数时动词+s的规则.md": "elementary/第三人称单数.html",
    "小学语法 正在进行时态.md": "elementary/正在进行时态.html",
    "小学语法 过去式专项训练.md": "elementary/过去式专项训练.html",
    "小学语法 动词的过去式练习.md": "elementary/动词的过去式练习.html",
    "小学高年级语法 将来时态中be going to 和will 的区别.md": "elementary/将来时态_begoingto_will.html",
    "小学语法 比较级别和最高级.md": "elementary/比较级和最高级.html",
    "小学语法 形容词性物主代词和名词性物主代词.md": "elementary/物主代词.html",
    "小学语法 反身代词练习.md": "elementary/反身代词练习.html",
    "小学语法 介词专项训练.md": "elementary/介词专项训练.html",
    "小学语法 词性转换.md": "elementary/词性转换.html",
    "频率副词.md": "elementary/频率副词.html",
    "疑问词专项训练.md": "elementary/疑问词专项训练.html",
    "移动介词prepositions of movement.md": "elementary/移动介词.html",
    # 中学
    "中学语法 定语从句练习.md": "middle/定语从句练习.html",
    "中学语法 被动.md": "middle/被动语态.html",
    "状语从句练习.md": "middle/状语从句练习.html",
    "一般过去时和过去进行时的区别.md": "middle/一般过去时和过去进行时.html",
    "and和but 的区别.md": "middle/and和but的区别.html",
}

def esc(s):
    return htmlmod.escape(s)

def convert_file(src_path, dst_rel):
    dst_path = os.path.join(DST_BASE, dst_rel)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

    with open(src_path, "r", encoding="utf-8") as f:
        md = f.read()

    # 提取标题（第一个 # 或第一个 --- 之间的文字）
    title = "语法练习"
    lines = md.split("\n")
    for line in lines:
        m = re.match(r"^#\s+(.+)$", line)
        if m:
            title = m.group(1).strip()
            break
        m = re.match(r"^\*\*(.+)\*\*$", line.strip())
        if m and not title:
            title = m.group(1).strip()

    # 如果没有标题，用文件名
    if not title or title == "语法练习":
        title = os.path.basename(dst_rel).replace(".html", "")

    # 转 HTML 正文
    html_parts = []
    in_table = False
    in_code = False
    in_list = False
    list_type = None

    def close_table():
        nonlocal in_table
        if in_table:
            html_parts.append("</table>")
            in_table = False

    def close_list():
        nonlocal in_list
        if in_list:
            html_parts.append(f"</{list_type}>")
            in_list = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # 跳过空行
        if line.strip() == "":
            close_table()
            i += 1
            continue

        # --- / --- 分隔线
        if re.match(r"^---+\s*$", line):
            close_table()
            close_list()
            html_parts.append("<hr>")
            i += 1
            continue

        # 标题
        m = re.match(r"^(#{1,4})\s+(.+)$", line)
        if m:
            close_table()
            close_list()
            level = min(len(m.group(1)) + 1, 4)
            html_parts.append(f"<h{level}>{esc(m.group(2).strip())}</h{level}>")
            i += 1
            continue

        # 代码块
        if line.startswith("```"):
            close_table()
            close_list()
            if in_code:
                html_parts.append("</pre>")
                in_code = False
            else:
                html_parts.append("<pre>")
                in_code = True
            i += 1
            continue
        if in_code:
            html_parts.append(esc(line))
            i += 1
            continue

        # 表格
        if re.match(r"^\|.+\|$", line):
            close_list()
            if re.match(r"^[\s\|:\-]+$", line) and "-" in line:
                i += 1
                continue
            parts = [c.strip() for c in line.split("|") if c.strip() != ""]
            if not in_table:
                html_parts.append("<table>")
                html_parts.append("<tr><td>" + "</td><td>".join(esc(p) for p in parts) + "</td></tr>")
                in_table = True
            else:
                html_parts.append("<tr><td>" + "</td><td>".join(esc(p) for p in parts) + "</td></tr>")
            i += 1
            continue
        else:
            close_table()

        # 列表
        m = re.match(r"^(\d+)\.\s+(.*)$", line)
        if m:
            if not in_list or list_type != "ol":
                close_list()
                html_parts.append("<ol>")
                in_list = True
                list_type = "ol"
            html_parts.append(f"<li>{esc(m.group(2))}</li>")
            i += 1
            continue

        m = re.match(r"^[-*]\s+(.*)$", line)
        if m:
            if not in_list or list_type != "ul":
                close_list()
                html_parts.append("<ul>")
                in_list = True
                list_type = "ul"
            html_parts.append(f"<li>{esc(m.group(1))}</li>")
            i += 1
            continue

        # 其他
        close_list()
        # 处理内联格式
        text = esc(line)
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"_(.+?)_", r"<em>\1</em>", text)
        if text.strip():
            html_parts.append(f"<p>{text}</p>")
        i += 1

    close_table()
    close_list()
    if in_code:
        html_parts.append("</pre>")

    body = "\n".join(html_parts)

    # 包裹完整 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} · PenguinBear English</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: #faf8f5; color: #2d2d2d; line-height: 1.9; font-size: 15px;
    max-width: 780px; margin: 0 auto; padding: 40px 28px 80px;
  }}
  .top-bar {{
    margin-bottom: 24px; padding-bottom: 16px;
    border-bottom: 2px solid #e8d5c4;
    display: flex; justify-content: space-between; align-items: center;
  }}
  .top-bar a {{ color: #4a7c5e; text-decoration: none; font-size: 14px; }}
  .top-bar a:hover {{ text-decoration: underline; }}
  h1 {{ font-size: 24px; color: #5a3e2b; margin: 20px 0 16px; }}
  h2 {{ font-size: 20px; color: #6b4f3a; margin: 28px 0 12px; border-bottom: 2px solid #ecd9cb; padding-bottom: 6px; }}
  h3 {{ font-size: 17px; color: #7a604a; margin: 22px 0 10px; }}
  h4 {{ font-size: 15px; color: #7a604a; margin: 18px 0 8px; }}
  p {{ margin: 10px 0; }}
  table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }}
  td {{ padding: 8px 12px; border: 1px solid #e0d5c8; vertical-align: top; }}
  table tr:first-child td {{ background: #f5ede6; font-weight: 600; }}
  ol, ul {{ padding-left: 24px; margin: 10px 0; }}
  li {{ margin: 5px 0; }}
  pre {{ background: #f5f0eb; padding: 14px 18px; border-radius: 8px; overflow-x: auto; margin: 12px 0; font-size: 13px; }}
  hr {{ border: none; border-top: 2px solid #e8d5c4; margin: 30px 0; }}
  .back {{ display: inline-block; margin-top: 30px; color: #4a7c5e; text-decoration: none; font-size: 14px; }}
  .back:hover {{ text-decoration: underline; }}
  strong {{ color: #8b4513; }}
  @media (max-width: 600px) {{ body {{ padding: 24px 16px 60px; }} }}
</style>
</head>
<body>

<div class="top-bar">
  <a href="../index.html">🐻 🐧 PenguinBear English</a>
  <a href="../index.html">← 返回首页</a>
</div>

{body}

<a class="back" href="../index.html">← 返回首页</a>

</body>
</html>"""

    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✅ {dst_rel}")

def main():
    for fname, dst_rel in sorted(CATEGORY.items()):
        src_path = os.path.join(SRC, fname)
        if not os.path.exists(src_path):
            print(f"  ⚠️  {fname} 不存在，跳过")
            continue
        convert_file(src_path, dst_rel)

    print(f"\n完成！共转换 {len(CATEGORY)} 个文件")

if __name__ == "__main__":
    main()
