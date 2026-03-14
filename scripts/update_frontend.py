#!/usr/bin/env python3
"""
update_frontend.py — 將 personnel.json 資料注入 index.html

用法：
    python scripts/update_frontend.py data/personnel.json index.html
"""

import json
import re
import sys


def main():
    if len(sys.argv) < 3:
        print("用法: python update_frontend.py <personnel.json> <index.html>")
        sys.exit(1)

    json_path = sys.argv[1]
    html_path = sys.argv[2]

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    personnel = data['personnel']

    # 產生 JS 陣列字串
    js_entries = []
    for p in personnel:
        entry = (
            f'  {{id:{p["id"]},name:"{p["name"]}",'
            f'PT:{p["PT"]},MT:{p["MT"]},UT:{p["UT"]},'
            f'ET:{p["ET"]},RT:{p["RT"]},VT:{p["VT"]},LT:{p["LT"]}}}'
        )
        js_entries.append(entry)

    js_array = 'let personnelData = [\n' + ',\n'.join(js_entries) + '\n];'

    # 讀取 HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 替換 personnelData 陣列（從 "let personnelData = [" 到 "];"）
    pattern = r'let personnelData = \[.*?\];'
    replacement = js_array

    new_html, count = re.subn(pattern, replacement, html, flags=re.DOTALL)

    if count == 0:
        print("⚠ 在 index.html 中找不到 personnelData 陣列，跳過更新")
        sys.exit(0)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f"✅ 已將 {len(personnel)} 筆人員資料注入 {html_path}")


if __name__ == '__main__':
    main()
