"""仓库默认路径常量。

本模块只提供静态默认路径，方便 UI、Service 和 Agent 层基金能力复用同一份
路径真源；它不读取环境变量、workspace 配置、prompt manifest 或运行时配置。
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

DEFAULT_SELECTED_FUNDS_CSV: Final[Path] = Path("docs/code_20260519.csv")
DEFAULT_GOLDEN_TEMPLATE_PATH: Final[Path] = Path("docs/golden-answer-template.md")
DEFAULT_GOLDEN_PREFILL_OUTPUT: Final[Path] = Path(
    "reports/golden-answers/golden-answer-prefill.md"
)
DEFAULT_GOLDEN_REVIEWED_MARKDOWN: Final[Path] = Path(
    "reports/golden-answers/golden-answer-prefill-reviewed.md"
)
DEFAULT_GOLDEN_ANSWER_JSON: Final[Path] = Path("reports/golden-answers/golden-answer.json")
DEFAULT_EXTRACTION_SNAPSHOT_ROOT: Final[Path] = Path("reports/extraction-snapshots")
DEFAULT_EXTRACTOR_OUTPUT_ROOT: Final[Path] = Path("reports/extractor-outputs")
DEFAULT_QUALITY_GATE_OUTPUT_ROOT: Final[Path] = Path("reports/quality-gate-runs")
DEFAULT_LLM_RUN_ARTIFACT_ROOT: Final[Path] = Path("reports/llm-runs")
DEFAULT_REPRESENTATION_JSON_OUTPUT_ROOT: Final[Path] = Path("reports/representation-json")
DEFAULT_CACHE_ROOT: Final[Path] = Path("cache")
DEFAULT_DOCUMENT_CACHE_ROOT: Final[Path] = DEFAULT_CACHE_ROOT / "documents"
DEFAULT_PDF_CACHE_ROOT: Final[Path] = DEFAULT_CACHE_ROOT / "pdf"
DEFAULT_DOCLING_ARTIFACT_ROOT: Final[Path] = DEFAULT_CACHE_ROOT / "docling-artifacts"
DEFAULT_NAV_CACHE_ROOT: Final[Path] = DEFAULT_CACHE_ROOT / "nav"
DEFAULT_THERMOMETER_CACHE_ROOT: Final[Path] = DEFAULT_CACHE_ROOT / "thermometer"
