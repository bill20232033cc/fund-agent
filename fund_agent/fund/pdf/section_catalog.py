"""年报章节定位配置目录表。

本模块只承载章节别名与目录页误识别信号，不承载具体定位算法，
用于支撑 P1-S2 的可配置章节定位器。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class SectionCatalogEntry:
    """章节目录规则条目。

    Attributes:
        section_id: 章节编号，如 ``§3``。
        heading_patterns: 该章节允许匹配的标题正则列表。
    """

    section_id: str
    heading_patterns: tuple[str, ...]


SECTION_CATALOG: Final[tuple[SectionCatalogEntry, ...]] = (
    SectionCatalogEntry(
        section_id="§1",
        heading_patterns=(
            r"^§1\s+重要提示及目录\s*$",
            r"^§1\s+基金(?:基本)?简介\s*$",
        ),
    ),
    SectionCatalogEntry(
        section_id="§2",
        heading_patterns=(
            r"^§2\s+基金简介\s*$",
            r"^§2\s+主要财务指标(?:及基金净值表现)?\s*$",
        ),
    ),
    SectionCatalogEntry(
        section_id="§3",
        heading_patterns=(
            r"^§3\s+主要财务指标.*基金净值表现.*$",
            r"^§3\s+基金主要财务指标.*$",
            r"^§3\s+基金净值表现.*$",
        ),
    ),
    SectionCatalogEntry(
        section_id="§4",
        heading_patterns=(
            r"^§4\s+管理人报告\s*$",
        ),
    ),
    SectionCatalogEntry(
        section_id="§5",
        heading_patterns=(
            r"^§5\s+托管人报告\s*$",
        ),
    ),
    SectionCatalogEntry(
        section_id="§8",
        heading_patterns=(
            r"^§8\s+投资组合报告\s*$",
        ),
    ),
    SectionCatalogEntry(
        section_id="§9",
        heading_patterns=(
            r"^§9\s+基金份额持有人信息.*$",
            r"^§9\s+持有人.*$",
        ),
    ),
    SectionCatalogEntry(
        section_id="§10",
        heading_patterns=(
            r"^§10\s+(?:开放式)?基金份额变动.*$",
            r"^§10\s+基金份额.*$",
        ),
    ),
)

TOC_LINE_PATTERNS: Final[tuple[str, ...]] = (
    r"[\.·•…⋯]{2,}\s*\d+\s*$",
    r"\s{2,}\d+\s*$",
)
