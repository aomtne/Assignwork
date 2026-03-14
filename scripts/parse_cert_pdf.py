#!/usr/bin/env python3
"""
parse_cert_pdf.py — 解析 NDT 人員證照 PDF，輸出 personnel.json

表格結構（24欄）：
  col 0=序號, 1=姓名, 2=檢測類別
  col 3,4,5   = PT (Ⅰ,Ⅱ,Ⅲ)
  col 6,7,8   = MT (Ⅰ,Ⅱ,Ⅲ)
  col 9,10,11  = UT (Ⅰ,Ⅱ,Ⅲ)
  col 12,13,14 = ET (Ⅰ,Ⅱ,Ⅲ)
  col 15,16,17 = RT (Ⅰ,Ⅱ,Ⅲ)
  col 18,19,20 = VT (Ⅰ,Ⅱ,Ⅲ)
  col 21,22,23 = LT (Ⅰ,Ⅱ,Ⅲ)

每位人員佔 2 行：TPC 行 + 協會證照行，只取 TPC 行。

用法：
    python scripts/parse_cert_pdf.py data/證書級數.pdf data/personnel.json
"""

import pdfplumber
import json
import re
import sys
import os

METHODS = ['PT', 'MT', 'UT', 'ET', 'RT', 'VT', 'LT']

METHOD_COLS = {
    'PT': (3, 4, 5),
    'MT': (6, 7, 8),
    'UT': (9, 10, 11),
    'ET': (12, 13, 14),
    'RT': (15, 16, 17),
    'VT': (18, 19, 20),
    'LT': (21, 22, 23),
}


def get_level(row, method):
    cols = METHOD_COLS[method]
    level = 0
    for i, col_idx in enumerate(cols):
        if col_idx < len(row):
            cell = str(row[col_idx] or '').strip()
            if cell:
                level = max(level, i + 1)
    return level


def extract_name(cell_text):
    if not cell_text:
        return ''
    lines = str(cell_text).strip().split('\n')
    for line in lines:
        line = line.strip()
        if 'CQ' in line:
            continue
        # Remove spaces between Chinese chars, then check
        cleaned = re.sub(r'\s+', '', line)
        if re.search(r'[\u4e00-\u9fff]{2,}', cleaned):
            return cleaned
    return ''


def parse_pdf(pdf_path, start_id=2, end_id=30):
    personnel = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if not tables:
                continue
            for table in tables:
                for row in table[2:]:
                    if not row or len(row) < 24:
                        continue
                    category = str(row[2] or '').strip()
                    if category != 'TPC':
                        continue
                    seq_str = str(row[0] or '').strip()
                    if not seq_str:
                        continue
                    try:
                        seq_id = int(seq_str)
                    except ValueError:
                        continue
                    if seq_id < start_id or seq_id > end_id:
                        continue
                    name = extract_name(row[1])
                    if not name:
                        continue
                    person = {'id': seq_id, 'name': name}
                    for method in METHODS:
                        person[method] = get_level(row, method)
                    personnel.append(person)
    personnel.sort(key=lambda x: x['id'])
    return personnel


def main():
    if len(sys.argv) < 3:
        print("用法: python parse_cert_pdf.py <input.pdf> <output.json>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    output_path = sys.argv[2]
    if not os.path.exists(pdf_path):
        print(f"ERROR: 找不到 PDF: {pdf_path}")
        sys.exit(1)
    print(f"Parsing: {pdf_path}")
    personnel = parse_pdf(pdf_path, start_id=2, end_id=30)
    if not personnel:
        print("ERROR: 未能提取任何資料")
        sys.exit(1)
    output = {
        "version": "auto-generated",
        "source": os.path.basename(pdf_path),
        "count": len(personnel),
        "personnel": personnel
    }
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(personnel)} records -> {output_path}")
    header = f"{'#':>3} {'Name':<6}" + ''.join(f" {m:>3}" for m in METHODS)
    print(header)
    print('-' * len(header))
    for p in personnel:
        lvls = ''.join(f" {'III' if p[m]==3 else 'II' if p[m]==2 else 'I' if p[m]==1 else '  -':>3}" for m in METHODS)
        print(f"{p['id']:>3} {p['name']:<6}{lvls}")


if __name__ == '__main__':
    main()
