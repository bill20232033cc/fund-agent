"""解析基金年报 PDF，提取文本、表格与章节位置。"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import pdfplumber

from fund_agent.fund.pdf.section_catalog import SECTION_CATALOG, TOC_LINE_PATTERNS

logger = logging.getLogger(__name__)

_COMPILED_SECTION_PATTERNS: Final[dict[str, tuple[re.Pattern[str], ...]]] = {
    entry.section_id: tuple(re.compile(pattern) for pattern in entry.heading_patterns)
    for entry in SECTION_CATALOG
}
_COMPILED_TOC_PATTERNS: Final[tuple[re.Pattern[str], ...]] = tuple(
    re.compile(pattern)
    for pattern in TOC_LINE_PATTERNS
)


@dataclass(frozen=True, slots=True)
class _TextLine:
    """文本行与偏移信息。

    Attributes:
        raw_text: 原始行文本，不含换行符。
        normalized_text: 去掉首尾空白后的行文本。
        start_offset: 原始行在全文中的起始偏移。
        normalized_start_offset: 去掉行首空白后的起始偏移。
    """

    raw_text: str
    normalized_text: str
    start_offset: int
    normalized_start_offset: int


@dataclass(frozen=True, slots=True)
class _SectionCandidate:
    """章节候选命中。

    Attributes:
        section_id: 章节编号。
        start_offset: 命中行在全文中的起始偏移。
        matched_pattern: 命中的章节规则。
        line_text: 命中的标准化行文本。
    """

    section_id: str
    start_offset: int
    matched_pattern: str
    line_text: str


def _normalize_text(text: str) -> str:
    """规范化提取后的全文文本。

    Args:
        text: 原始提取文本。

    Returns:
        去除多余空行和孤立页码后的文本。

    Raises:
        无显式抛出。
    """

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    return text.strip()


def _iter_text_lines(text: str) -> list[_TextLine]:
    """把全文切成带偏移信息的文本行。

    Args:
        text: 待定位章节的全文文本。

    Returns:
        按原始顺序排列的文本行列表。

    Raises:
        无显式抛出。
    """

    lines: list[_TextLine] = []
    cursor = 0
    for chunk in text.splitlines(keepends=True):
        raw_text = chunk.rstrip("\r\n")
        normalized_text = raw_text.strip()
        leading_padding = len(raw_text) - len(raw_text.lstrip())
        lines.append(
            _TextLine(
                raw_text=raw_text,
                normalized_text=normalized_text,
                start_offset=cursor,
                normalized_start_offset=cursor + leading_padding,
            )
        )
        cursor += len(chunk)
    return lines


def _is_toc_line(line_text: str) -> bool:
    """判断命中行是否更像目录项而非正文标题。

    Args:
        line_text: 去掉首尾空白后的命中行文本。

    Returns:
        命中目录过滤信号时返回 ``True``，否则返回 ``False``。

    Raises:
        无显式抛出。
    """

    return any(pattern.search(line_text) for pattern in _COMPILED_TOC_PATTERNS)


def _collect_section_candidates(text: str) -> list[_SectionCandidate]:
    """收集全文中所有章节标题候选。

    Args:
        text: 待定位章节的全文文本。

    Returns:
        所有非目录章节候选，保持正文中的出现顺序。

    Raises:
        无显式抛出。
    """

    candidates: list[_SectionCandidate] = []
    for line in _iter_text_lines(text):
        if not line.normalized_text:
            continue
        for section_id, patterns in _COMPILED_SECTION_PATTERNS.items():
            for pattern in patterns:
                if not pattern.match(line.normalized_text):
                    continue
                if _is_toc_line(line.normalized_text):
                    break
                candidates.append(
                    _SectionCandidate(
                        section_id=section_id,
                        start_offset=line.normalized_start_offset,
                        matched_pattern=pattern.pattern,
                        line_text=line.normalized_text,
                    )
                )
                break
            else:
                continue
            break
    return candidates


def _select_section_starts(candidates: list[_SectionCandidate]) -> list[tuple[str, int]]:
    """为每个章节选择正文中的首个有效命中。

    Args:
        candidates: 全文扫描得到的章节候选。

    Returns:
        章节起始偏移列表，按正文位置升序排列。

    Raises:
        无显式抛出。
    """

    first_hit_by_section: dict[str, int] = {}
    for candidate in candidates:
        if candidate.section_id in first_hit_by_section:
            continue
        first_hit_by_section[candidate.section_id] = candidate.start_offset
    return sorted(first_hit_by_section.items(), key=lambda item: item[1])


def extract_text(pdf_path: Path) -> str:
    """提取 PDF 全文文本。

    Args:
        pdf_path: 本地 PDF 文件路径。

    Returns:
        合并后的全文文本。

    Raises:
        OSError: PDF 文件无法读取时抛出。
    """

    texts: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        logger.info("PDF has %d pages", len(pdf.pages))
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                texts.append(page_text)

    return _normalize_text("\n".join(texts))


def extract_tables(pdf_path: Path) -> list[dict[str, object]]:
    """提取 PDF 中所有表格。

    Args:
        pdf_path: 本地 PDF 文件路径。

    Returns:
        表格列表，每项包含 page_number, headers, rows。

    Raises:
        OSError: PDF 文件无法读取时抛出。
    """

    tables: list[dict[str, object]] = []
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
    """在全文中定位年报正文章节位置。

    本函数只返回正文中的章节标题，目录页同名条目会依据配置化目录信号过滤。

    Args:
        text: 待定位章节的全文文本。

    Returns:
        章节编号到 (start, end) 字符偏移的映射。

    Raises:
        无显式抛出。
    """

    sections: dict[str, tuple[int, int]] = {}
    matches = _select_section_starts(_collect_section_candidates(text))

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

    Raises:
        无显式抛出。
    """

    sections = locate_sections(text)
    if section_id not in sections:
        logger.warning("Section %s not found", section_id)
        return None

    start, end = sections[section_id]
    return text[start:end].strip()
