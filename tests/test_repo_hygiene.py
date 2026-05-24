"""仓库发布卫生守卫测试。"""

from __future__ import annotations

from pathlib import Path

import tomllib


REPO_ROOT = Path(__file__).resolve().parents[1]
CI_COVERAGE_COMMAND = (
    "uv run pytest --cov=fund_agent --cov-report=term-missing "
    "--cov-fail-under=50 -q"
)


def test_license_and_package_metadata_are_declared() -> None:
    """验证根许可证和包元数据保持一致。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 LICENSE 或 pyproject license 缺失时抛出。
    """

    license_text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8")
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert "MIT License" in license_text
    assert "Copyright (c) 2026 bill20232033cc" in license_text
    assert pyproject["project"]["license"] == "MIT"


def test_ci_workflow_runs_release_readiness_checks() -> None:
    """验证 CI workflow 覆盖当前发布就绪检查。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CI 命令或 Python 版本不符合契约时抛出。
    """

    workflow = (REPO_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert 'python-version: "3.11"' in workflow
    assert "uv sync --extra dev --frozen" in workflow
    assert "uv run ruff check ." in workflow
    assert CI_COVERAGE_COMMAND in workflow
    assert "--cov=fund_agent" in workflow
    assert "--cov-report=term-missing" in workflow
    assert "--cov-fail-under=50" in workflow


def test_gitignore_keeps_generated_outputs_local_without_hiding_fixtures() -> None:
    """验证生成物忽略策略保持窄口径。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 `.gitignore` 缺少必要条目或误忽略整个 reports 时抛出。
    """

    gitignore_lines = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert "cache/" in gitignore_lines
    assert "reports/extraction-snapshots/" in gitignore_lines
    assert "reports/quality-gate-runs/" in gitignore_lines
    assert "docs/*.docx" in gitignore_lines
    assert ".pytest_cache/" in gitignore_lines
    assert ".ruff_cache/" in gitignore_lines
    assert "dist/" in gitignore_lines
    assert "build/" in gitignore_lines
    assert "reports/" not in gitignore_lines
    assert "reports/golden-answers/" not in gitignore_lines
    assert any("reports/golden-answers/" in line for line in gitignore_lines)
