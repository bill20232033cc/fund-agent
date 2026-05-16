"""解析基金年报 PDF，提取文本和表格。"""

import logging
import re
from pathlib import Path

import pdfplumber

logger = logging.getLogger(__name__)

# 年报正文章节匹配（§N 格式，匹配实际章节标题行，非目录行）
SECTION_PATTERNS = {
    "§1": [r"^§1\s+重要提示及目录", r"^§1\s+基金(?:基本)?简介"],
    "§2": [r"^§2\s+基金简介", r"^§2\s+主要财务指标"],
    "§3": [r"^§3\s+基金(?:主要财务指标|净值表现)", r"^§3\s+基金净值"],
    "§4": [r"^§4\s+管理人报告"],
    "§5": [r"^§5\s+托管人报告"],
    "§8": [r"^§8\s+投资组合报告"],
    "§9": [r"^§9\s+基金份额持有人信息", r"^§9\s+持有人"],
    "§10": [r"^§10\s+(?:开放式)?基金份额变动", r"^§10\s+基金份额"],
}


def _normalize_text(text: str) -> str:
    """Normalize extracted text: collapse whitespace, remove page numbers."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    return text.strip()


def extract_text(pdf_path: Path) -> str:
    """提取 PDF 全文文本。

    Args:
        pdf_path: 本地 PDF 文件路径。

    Returns:
        合并后的全文文本。
    """
    texts: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        logger.info("PDF has %d pages", len(pdf.pages))
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                texts.append(page_text)

    return _normalize_text("\n".join(texts))


def extract_tables(pdf_path: Path) -> list[dict]:
    """提取 PDF 中所有表格。

    Returns:
        表格列表，每项包含 page_number, headers, rows。
    """
    tables: list[dict] = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_tables = page.extract_tables()
            for table in page_tables:
                if not table or len(table) < 2:
                    continue
                headers = [str(h).strip() if h else "" for h in table[0]]
                rows = [
                    [str(cell).strip() if cell else "" for cell in row]
                    for row in table[1:]
                    if any(cell for cell in row)
                ]
                tables.append({
                    "page_number": i + 1,
                    "headers": headers,
                    "rows": rows,
                })

    logger.info("Extracted %d tables from %s", len(tables), pdf_path)
    return tables


def locate_sections(text: str) -> dict[str, tuple[int, int]]:
    """在全文中定位年报正文章节位置（跳过目录）。

    Matches §N headers in the body text, skipping TOC entries
    (which contain dot-leader patterns like ".....  10").

    Returns:
        章节编号到 (start, end) 字符偏移的映射。
    """
    sections: dict[str, tuple[int, int]] = {}
    matches: list[tuple[str, int]] = []

    for section_id, patterns in SECTION_PATTERNS.items():
        for pattern in patterns:
            for m in re.finditer(pattern, text, re.MULTILINE):
                line_end = text.find("\n", m.start())
                line = text[m.start():line_end] if line_end != -1 else text[m.start():]
                # Skip TOC entries: they contain dot-leader "..."
                if "..." in line:
                    continue
                matches.append((section_id, m.start()))
                break
            else:
                continue
            break

    # Sort by position
    matches.sort(key=lambda x: x[1])

    for i, (section_id, start) in enumerate(matches):
        end = matches[i + 1][1] if i + 1 < len(matches) else len(text)
        sections[section_id] = (start, end)

    logger.info("Located %d sections: %s", len(sections), list(sections.keys()))
    return sections


def extract_section(text: str, section_id: str) -> str | None:
    """提取指定章节的文本。

    Args:
        text: 全文文本。
        section_id: 章节编号，如 "§4"。

    Returns:
        章节文本，未找到返回 None。
    """
    sections = locate_sections(text)
    if section_id not in sections:
        logger.warning("Section %s not found", section_id)
        return None

    start, end = sections[section_id]
    return text[start:end].strip()
