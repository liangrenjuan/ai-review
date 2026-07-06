# -*- coding: utf-8 -*-
"""把 sentiment_pdfs/ 下的每个 PDF 提取为纯文本，放进 ./data/articles/。

一篇 PDF 对应一个 txt（不再切割），文件名沿用 PDF 名。
"""
import os
import glob
import pdfplumber

SRC_DIR = "./sentiment_pdfs"
DATA_DIR = "./data/articles"
os.makedirs(DATA_DIR, exist_ok=True)


def extract_one(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    return "\n".join(pages).strip(), len(pages)


def main():
    pdfs = sorted(glob.glob(os.path.join(SRC_DIR, "*.pdf")))
    if not pdfs:
        print(f"未在 {SRC_DIR} 找到 PDF")
        return
    for i, pdf_path in enumerate(pdfs, 1):
        text, npages = extract_one(pdf_path)
        base = os.path.splitext(os.path.basename(pdf_path))[0]
        out = os.path.join(DATA_DIR, f"{base}.txt")
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[{i}/{len(pdfs)}] {base[:50]}...  {len(text)} 字符, {npages} 页")
    print(f"\n完成，共 {len(pdfs)} 篇写入 {DATA_DIR}")


if __name__ == "__main__":
    main()
