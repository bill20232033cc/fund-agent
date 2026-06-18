"""Docling candidate no-consumption guard 测试。"""

from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_IMPORT_PREFIXES = (
    "docling",
    "fund_agent.fund.documents.candidates",
    "fund_agent.fund.documents.adapters.annual_report_pdf",
    "fund_agent.fund.documents.cache",
)
GUARDED_PATHS = (
    Path("fund_agent/services"),
    Path("fund_agent/ui"),
    Path("fund_agent/host"),
    Path("fund_agent/fund/template"),
    Path("fund_agent/fund/audit"),
    Path("fund_agent/fund/extractors"),
    Path("fund_agent/fund/report_quality_validation.py"),
)


def test_service_ui_host_renderer_audit_quality_and_extractors_do_not_import_candidates() -> None:
    """验证 consumer 层不直接 import candidate、Docling、PDF adapter/cache。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 发现禁止 import 时抛出。
    """

    violations: list[str] = []
    for path in _iter_python_files(GUARDED_PATHS):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            module = _imported_module_name(node)
            if module is None:
                continue
            if module.startswith(FORBIDDEN_IMPORT_PREFIXES):
                violations.append(f"{path}:{module}")
    assert violations == []


def test_documents_public_init_does_not_export_candidate_internals() -> None:
    """验证 documents public __init__ 未导出 candidate internals。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: public surface 出现 candidate internals 时抛出。
    """

    content = Path("fund_agent/fund/documents/__init__.py").read_text(encoding="utf-8")
    assert "candidates" not in content
    assert "Candidate" not in content


def _iter_python_files(paths: tuple[Path, ...]) -> tuple[Path, ...]:
    """展开待检查 Python 文件。

    Args:
        paths: 文件或目录路径。

    Returns:
        Python 文件路径元组。

    Raises:
        无显式抛出。
    """

    files: list[Path] = []
    for path in paths:
        if path.is_file():
            files.append(path)
        else:
            files.extend(sorted(path.rglob("*.py")))
    return tuple(files)


def _imported_module_name(node: ast.AST) -> str | None:
    """提取 import 节点的模块名。

    Args:
        node: AST 节点。

    Returns:
        import 模块名；非 import 节点返回 ``None``。

    Raises:
        无显式抛出。
    """

    if isinstance(node, ast.Import):
        return node.names[0].name
    if isinstance(node, ast.ImportFrom):
        return node.module
    return None

