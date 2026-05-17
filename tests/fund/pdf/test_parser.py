"""章节定位器测试。"""

from __future__ import annotations

from pathlib import Path

from fund_agent.fund.pdf.parser import extract_section, locate_sections

_FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "fund" / "pdf_sections"
_REQUIRED_SECTION_IDS = ("§1", "§2", "§3", "§4", "§8", "§9", "§10")


def _load_fixture_text(filename: str) -> str:
    """读取章节定位测试夹具。

    Args:
        filename: 夹具文件名。

    Returns:
        夹具全文文本。

    Raises:
        FileNotFoundError: 夹具文件不存在时抛出。
        OSError: 夹具文件无法读取时抛出。
    """

    return (_FIXTURE_DIR / filename).read_text(encoding="utf-8")


def test_locate_sections_finds_required_sections_for_110011_2024_fixture() -> None:
    """验证 `110011/2024` 事实夹具能稳定定位所需章节。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当必需章节未被定位时抛出。
    """

    text = _load_fixture_text("110011_2024_excerpt.txt")

    sections = locate_sections(text)

    assert tuple(section_id for section_id in sections if section_id in _REQUIRED_SECTION_IDS) == (
        "§1",
        "§2",
        "§3",
        "§4",
        "§8",
        "§9",
        "§10",
    )
    assert extract_section(text, "§3") == "§3 主要财务指标、基金净值表现及利润分配情况\n第三章正文"


def test_locate_sections_skips_toc_entries_without_relying_on_dot_leader_only() -> None:
    """验证目录误识别过滤不依赖单一 `...` 规则。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当目录行被误识别为正文标题时抛出。
    """

    text = _load_fixture_text("110011_2024_excerpt.txt")

    sections = locate_sections(text)

    assert sections["§3"][0] == text.index("§3 主要财务指标、基金净值表现及利润分配情况\n")
    assert sections["§4"][0] == text.index("§4 管理人报告\n")
    assert sections["§8"][0] == text.index("§8 投资组合报告\n")


def test_locate_sections_returns_monotonic_offsets_for_required_sections() -> None:
    """验证关键章节偏移严格单调递增。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当章节偏移逆序或区间非法时抛出。
    """

    text = _load_fixture_text("110011_2024_excerpt.txt")

    sections = locate_sections(text)
    ordered_offsets = [sections[section_id] for section_id in _REQUIRED_SECTION_IDS]

    previous_start = -1
    for start_offset, end_offset in ordered_offsets:
        assert start_offset < end_offset
        assert start_offset > previous_start
        previous_start = start_offset
