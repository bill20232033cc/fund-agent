"""基金模板渲染章节块切分工具。

本模块属于基金 Capability 层，服务 `docs/design.md` 第 3.1 节 8 章模板。
它只依赖 CHAPTER_CONTRACT manifest，不依赖模板渲染器或程序审计实现。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from fund_agent.fund.template.contracts import ChapterContract, get_chapter_contract

_EXPECTED_CHAPTER_IDS: Final[tuple[int, ...]] = tuple(range(8))
_TEMPLATE_HEADING_RE: Final[re.Pattern[str]] = re.compile(r"(?m)^#\s+(\d+)\.\s+(.+?)\s*$")
_TOP_LEVEL_HEADING_RE: Final[re.Pattern[str]] = re.compile(r"(?m)^#(?!#).*$")
EVIDENCE_APPENDIX_HEADING: Final[str] = "## 证据与出处"
_EVIDENCE_APPENDIX_HEADING_RE: Final[re.Pattern[str]] = re.compile(
    rf"(?m)^{re.escape(EVIDENCE_APPENDIX_HEADING)}\s*$"
)


@dataclass(frozen=True, slots=True)
class RenderedChapterBlock:
    """已渲染的模板单章块。

    Attributes:
        chapter_id: 模板章节编号，必须来自公开 `ChapterContract`。
        title: 模板章节标题，必须来自公开 `ChapterContract`。
        heading: 报告中的原始 Markdown 一级标题行。
        markdown: 单章 Markdown 块，包含标题但不包含证据附录。
        body_markdown: 单章正文 Markdown，不包含标题和证据附录。
        contract: 与当前章节编号一致的 `ChapterContract`。
    """

    chapter_id: int
    title: str
    heading: str
    markdown: str
    body_markdown: str
    contract: ChapterContract


def get_template_chapter_heading(chapter_id: int) -> str:
    """读取模板章节 Markdown 标题。

    Args:
        chapter_id: 模板章节编号，必须为 0-7。

    Returns:
        使用 CHAPTER_CONTRACT 标题生成的一级 Markdown 标题。

    Raises:
        ValueError: 章节编号不存在或契约清单校验失败时抛出。
    """

    contract = get_chapter_contract(chapter_id)
    return f"# {contract.chapter_id}. {contract.title}"


def split_rendered_chapter_blocks(report_markdown: str) -> tuple[RenderedChapterBlock, ...]:
    """按 CHAPTER_CONTRACT 切分已渲染的 8 章报告。

    Args:
        report_markdown: `render_template_report()` 生成的完整 Markdown 报告。

    Returns:
        按章节编号 0-7 排序的渲染章节块。

    Raises:
        ValueError: 当文本为空、缺章、重复、乱序、越界、标题不匹配，
            或出现非模板一级标题时抛出。
    """

    if not report_markdown.strip():
        raise ValueError("渲染报告为空，无法切分模板章节")

    heading_matches = _collect_template_heading_matches(report_markdown)
    blocks = _build_rendered_chapter_blocks(report_markdown, heading_matches)
    _validate_rendered_chapter_sequence(blocks)
    return tuple(blocks)


def _collect_template_heading_matches(report_markdown: str) -> tuple[re.Match[str], ...]:
    """收集并校验报告中的模板一级标题。

    Args:
        report_markdown: 完整 Markdown 报告。

    Returns:
        模板章节一级标题的正则匹配结果。

    Raises:
        ValueError: 出现非模板一级标题或没有模板章节标题时抛出。
    """

    matches: list[re.Match[str]] = []
    for heading_match in _TOP_LEVEL_HEADING_RE.finditer(report_markdown):
        heading_line = heading_match.group(0)
        template_match = _TEMPLATE_HEADING_RE.match(
            report_markdown,
            heading_match.start(),
            heading_match.end(),
        )
        if template_match is None:
            raise ValueError(f"报告出现非模板一级标题：{heading_line}")
        matches.append(template_match)

    if not matches:
        raise ValueError("渲染报告缺少模板章节标题")
    return tuple(matches)


def _build_rendered_chapter_blocks(
    report_markdown: str,
    heading_matches: tuple[re.Match[str], ...],
) -> list[RenderedChapterBlock]:
    """根据模板标题位置构造章节块。

    Args:
        report_markdown: 完整 Markdown 报告。
        heading_matches: 已校验为模板一级标题的匹配结果。

    Returns:
        渲染章节块列表。

    Raises:
        ValueError: 章节编号越界或标题与契约不一致时抛出。
    """

    blocks: list[RenderedChapterBlock] = []
    for index, heading_match in enumerate(heading_matches):
        chapter_id = _parse_heading_chapter_id(heading_match)
        contract = get_chapter_contract(chapter_id)
        heading = heading_match.group(0)
        expected_heading = get_template_chapter_heading(chapter_id)
        if heading != expected_heading:
            raise ValueError(f"模板第{chapter_id}章标题不匹配：{heading}")

        next_start = _next_chapter_or_appendix_start(report_markdown, heading_matches, index)
        markdown = report_markdown[heading_match.start() : next_start].strip()
        _, _, body = markdown.partition("\n")
        blocks.append(
            RenderedChapterBlock(
                chapter_id=contract.chapter_id,
                title=contract.title,
                heading=heading,
                markdown=markdown,
                body_markdown=body.strip(),
                contract=contract,
            )
        )
    return blocks


def _parse_heading_chapter_id(heading_match: re.Match[str]) -> int:
    """解析章节标题中的模板章节编号。

    Args:
        heading_match: 模板一级标题匹配结果。

    Returns:
        章节编号。

    Raises:
        ValueError: 章节编号不在 0-7 范围内时抛出。
    """

    chapter_id = int(heading_match.group(1))
    if chapter_id not in _EXPECTED_CHAPTER_IDS:
        raise ValueError(f"模板章节编号越界：chapter_id={chapter_id}")
    return chapter_id


def _next_chapter_or_appendix_start(
    report_markdown: str,
    heading_matches: tuple[re.Match[str], ...],
    current_index: int,
) -> int:
    """定位当前章节块结束位置。

    Args:
        report_markdown: 完整 Markdown 报告。
        heading_matches: 模板章节一级标题匹配结果。
        current_index: 当前章节在匹配结果中的索引。

    Returns:
        当前章节 Markdown 块的结束偏移。

    Raises:
        无显式抛出。
    """

    if current_index + 1 < len(heading_matches):
        return heading_matches[current_index + 1].start()

    appendix_match = _EVIDENCE_APPENDIX_HEADING_RE.search(
        report_markdown,
        heading_matches[current_index].end(),
    )
    if appendix_match is not None:
        # 第 7 章边界优先截到证据附录前，避免把附录吞进正文。
        return appendix_match.start()
    return len(report_markdown)


def _validate_rendered_chapter_sequence(blocks: list[RenderedChapterBlock]) -> None:
    """校验渲染章节块严格覆盖模板第 0-7 章。

    Args:
        blocks: 已构造的章节块列表。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 章节缺失、重复或乱序时抛出。
    """

    chapter_ids = tuple(block.chapter_id for block in blocks)
    if len(set(chapter_ids)) != len(chapter_ids):
        raise ValueError("渲染报告存在重复模板章节")
    if chapter_ids != _EXPECTED_CHAPTER_IDS:
        raise ValueError(f"渲染报告章节必须按 0..7 顺序完整出现，实际为 {chapter_ids}")
