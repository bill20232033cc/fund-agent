"""仓库默认路径配置守卫测试。"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from fund_agent.config import paths


REPO_ROOT = Path(__file__).resolve().parents[2]
HISTORICAL_QUALITY_GATE_SCORE = Path(
    "reports/extraction-snapshots/p4-s3b-004393-controller-final-score/score.json"
)
EXPECTED_DEFAULTS = {
    "DEFAULT_SELECTED_FUNDS_CSV": Path("docs/code_20260519.csv"),
    "DEFAULT_GOLDEN_TEMPLATE_PATH": Path("docs/golden-answer-template.md"),
    "DEFAULT_GOLDEN_PREFILL_OUTPUT": Path("reports/golden-answers/golden-answer-prefill.md"),
    "DEFAULT_GOLDEN_REVIEWED_MARKDOWN": Path(
        "reports/golden-answers/golden-answer-prefill-reviewed.md"
    ),
    "DEFAULT_GOLDEN_ANSWER_JSON": Path("reports/golden-answers/golden-answer.json"),
    "DEFAULT_EXTRACTION_SNAPSHOT_ROOT": Path("reports/extraction-snapshots"),
    "DEFAULT_QUALITY_GATE_OUTPUT_ROOT": Path("reports/quality-gate-runs"),
    "DEFAULT_REPRESENTATION_JSON_OUTPUT_ROOT": Path("reports/representation-json"),
    "DEFAULT_CACHE_ROOT": Path("cache"),
    "DEFAULT_DOCUMENT_CACHE_ROOT": Path("cache/documents"),
    "DEFAULT_PDF_CACHE_ROOT": Path("cache/pdf"),
    "DEFAULT_DOCLING_ARTIFACT_ROOT": Path("cache/docling-artifacts"),
    "DEFAULT_NAV_CACHE_ROOT": Path("cache/nav"),
    "DEFAULT_THERMOMETER_CACHE_ROOT": Path("cache/thermometer"),
}


def test_config_paths_are_relative_and_match_documented_defaults() -> None:
    """验证 `fund_agent.config.paths` 中的仓库默认路径。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当默认路径漂移或变成绝对路径时抛出。
    """

    for name, expected_path in EXPECTED_DEFAULTS.items():
        actual_path = getattr(paths, name)
        assert actual_path == expected_path
        assert not actual_path.is_absolute()


def test_paths_module_import_is_isolated_from_ui_and_service() -> None:
    """验证路径模块不反向导入 UI 或 Service。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当静态路径模块引入运行时装配依赖时抛出。
    """

    sys.modules.pop("fund_agent.ui.cli", None)
    sys.modules.pop("fund_agent.services.fund_analysis_service", None)
    sys.modules.pop("fund_agent.config.paths", None)

    __import__("fund_agent.config.paths")

    assert "fund_agent.ui.cli" not in sys.modules
    assert "fund_agent.services.fund_analysis_service" not in sys.modules


def test_ui_cli_imports_service_but_not_agent_internals() -> None:
    """验证 UI CLI 只依赖 Service 层入口。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 UI 跳过 Service 直接导入 Agent 层基金能力时抛出。
    """

    source_path = REPO_ROOT / "fund_agent/ui/cli.py"
    module = ast.parse(source_path.read_text(encoding="utf-8"))
    service_imports: list[str] = []
    forbidden_imports: list[str] = []
    for node in ast.walk(module):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            if node.module.startswith("fund_agent.services"):
                service_imports.append(f"{node.module}:{node.lineno}")
            if node.module.startswith("fund_agent.fund"):
                forbidden_imports.append(f"{node.module}:{node.lineno}")
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("fund_agent.services"):
                    service_imports.append(f"{alias.name}:{node.lineno}")
                if alias.name.startswith("fund_agent.fund"):
                    forbidden_imports.append(f"{alias.name}:{node.lineno}")

    assert service_imports
    assert forbidden_imports == []


def test_existing_path_aliases_point_to_config_defaults() -> None:
    """验证迁移前公开默认路径别名仍指向同一默认值。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 UI、Service 或 Agent 层基金能力默认路径别名漂移时抛出。
    """

    from fund_agent.fund import extraction_snapshot, golden_answer, golden_prefill
    from fund_agent.fund.data import nav_data, thermometer
    from fund_agent.fund.documents import cache as document_cache
    from fund_agent.fund.pdf import downloader
    from fund_agent.fund.documents.candidates import representation_export, representation_handlers
    from fund_agent.fund import quality_gate_integration
    from fund_agent.services import fund_analysis_service
    from fund_agent.ui import cli

    assert cli.DEFAULT_SELECTED_FUNDS_CSV == paths.DEFAULT_SELECTED_FUNDS_CSV
    assert cli.DEFAULT_GOLDEN_TEMPLATE == paths.DEFAULT_GOLDEN_TEMPLATE_PATH
    assert cli.DEFAULT_GOLDEN_PREFILL_OUTPUT == paths.DEFAULT_GOLDEN_PREFILL_OUTPUT
    assert cli.DEFAULT_GOLDEN_ANSWER_OUTPUT == paths.DEFAULT_GOLDEN_ANSWER_JSON
    assert fund_analysis_service.DEFAULT_GOLDEN_ANSWER_PATH == paths.DEFAULT_GOLDEN_ANSWER_JSON
    assert extraction_snapshot.DEFAULT_SELECTED_FUNDS_CSV == paths.DEFAULT_SELECTED_FUNDS_CSV
    assert extraction_snapshot.DEFAULT_SNAPSHOT_OUTPUT_ROOT == paths.DEFAULT_EXTRACTION_SNAPSHOT_ROOT
    assert golden_prefill.DEFAULT_GOLDEN_TEMPLATE_PATH == paths.DEFAULT_GOLDEN_TEMPLATE_PATH
    assert golden_prefill.DEFAULT_GOLDEN_PREFILL_OUTPUT == paths.DEFAULT_GOLDEN_PREFILL_OUTPUT
    assert golden_answer.DEFAULT_GOLDEN_REVIEWED_MARKDOWN == paths.DEFAULT_GOLDEN_REVIEWED_MARKDOWN
    assert golden_answer.DEFAULT_GOLDEN_ANSWER_JSON == paths.DEFAULT_GOLDEN_ANSWER_JSON
    assert (
        quality_gate_integration.DEFAULT_QUALITY_GATE_OUTPUT_ROOT
        == paths.DEFAULT_QUALITY_GATE_OUTPUT_ROOT
    )
    assert document_cache.DOCUMENT_CACHE_ROOT == paths.DEFAULT_DOCUMENT_CACHE_ROOT
    assert downloader.DEFAULT_CACHE_DIR == paths.DEFAULT_PDF_CACHE_ROOT
    assert representation_export.DEFAULT_OUTPUT_ROOT == paths.DEFAULT_REPRESENTATION_JSON_OUTPUT_ROOT
    assert representation_export.PRODUCTION_CACHE_ROOT == paths.DEFAULT_PDF_CACHE_ROOT
    assert (
        representation_handlers.CandidateHandlerConfig().docling_artifacts_path
        == paths.DEFAULT_DOCLING_ARTIFACT_ROOT
    )
    assert nav_data.NAV_CACHE_ROOT == paths.DEFAULT_NAV_CACHE_ROOT
    assert thermometer.THERMOMETER_CACHE_ROOT == paths.DEFAULT_THERMOMETER_CACHE_ROOT


def test_historical_quality_gate_score_stays_cli_local() -> None:
    """验证历史 P4 score fixture 路径没有进入仓库级默认路径模块。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当历史 fixture 路径被误提升为全局默认值时抛出。
    """

    from fund_agent.ui import cli

    assert cli.DEFAULT_QUALITY_GATE_SCORE == HISTORICAL_QUALITY_GATE_SCORE
    assert not hasattr(paths, "DEFAULT_QUALITY_GATE_SCORE")


def test_config_init_does_not_reexport_path_constants() -> None:
    """验证 `fund_agent.config.__init__` 不是路径常量重导出面。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 config 包入口重导出默认路径时抛出。
    """

    import fund_agent.config as config

    assert not hasattr(config, "DEFAULT_SELECTED_FUNDS_CSV")
    assert not hasattr(config, "__all__")


def test_no_independent_repository_path_defaults_outside_config_paths() -> None:
    """扫描 UI、Service、Fund 模块，防止新增散落仓库默认路径。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当允许范围外出现 `Path("docs|reports|cache/...")` 默认值时抛出。
    """

    offenders: list[str] = []
    for source_path in _python_sources_for_path_scan():
        module = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(module):
            if not isinstance(node, ast.Assign | ast.AnnAssign):
                continue
            target_names = _assignment_target_names(node)
            if source_path.name == "cli.py" and "DEFAULT_QUALITY_GATE_SCORE" in target_names:
                continue
            for call in [child for child in ast.walk(node) if isinstance(child, ast.Call)]:
                if _is_repository_path_call(call):
                    relative = source_path.relative_to(REPO_ROOT)
                    offenders.append(f"{relative}:{call.lineno}")

    assert offenders == []


def test_extraction_score_has_no_module_level_repository_path_default() -> None:
    """验证 extraction_score 没有需要迁移的模块级仓库路径默认值。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 extraction_score 新增散落路径默认值时抛出。
    """

    source_path = REPO_ROOT / "fund_agent/fund/extraction_score.py"
    module = ast.parse(source_path.read_text(encoding="utf-8"))
    offenders = []
    for node in module.body:
        if not isinstance(node, ast.Assign | ast.AnnAssign):
            continue
        for call in [child for child in ast.walk(node) if isinstance(child, ast.Call)]:
            if _is_repository_path_call(call):
                offenders.append(call.lineno)

    assert offenders == []


def _python_sources_for_path_scan() -> tuple[Path, ...]:
    """返回需要扫描散落默认路径的生产代码文件。

    Args:
        无。

    Returns:
        生产代码 Python 文件路径元组。

    Raises:
        无显式抛出。
    """

    roots = (
        REPO_ROOT / "fund_agent/ui",
        REPO_ROOT / "fund_agent/services",
        REPO_ROOT / "fund_agent/fund",
    )
    return tuple(path for root in roots for path in root.rglob("*.py"))


def _assignment_target_names(node: ast.Assign | ast.AnnAssign) -> set[str]:
    """提取赋值语句中的目标名称。

    Args:
        node: Python AST 赋值节点。

    Returns:
        赋值目标名称集合。

    Raises:
        无显式抛出。
    """

    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    names: set[str] = set()
    for target in targets:
        if isinstance(target, ast.Name):
            names.add(target.id)
    return names


def _is_repository_path_call(call: ast.Call) -> bool:
    """判断 AST 调用是否是仓库级默认路径构造。

    Args:
        call: Python AST 调用节点。

    Returns:
        命中 `Path("docs/...")`、`Path("reports/...")` 或 `Path("cache/...")` 时返回
        `True`。

    Raises:
        无显式抛出。
    """

    if not isinstance(call.func, ast.Name) or call.func.id != "Path":
        return False
    if not call.args or not isinstance(call.args[0], ast.Constant):
        return False
    value = call.args[0].value
    return isinstance(value, str) and value.startswith(("docs/", "reports/", "cache/"))
