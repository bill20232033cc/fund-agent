"""Service LLM ExecutionContract 边界测试，见模板第 0-7 章。"""

from __future__ import annotations

import inspect
from collections.abc import Mapping as CollectionsMapping
from dataclasses import fields, is_dataclass
from typing import Any, Mapping, get_args, get_origin

import pytest

from fund_agent.services import (
    ChapterOrchestrationPolicy,
    FinalAssemblyPolicy,
    FundAnalysisRequest,
    FundLLMAnalysisInput,
    FundLLMExecutionContract,
    FundLLMExecutionRequest,
    FundLLMRuntimePlan,
    ProviderRuntimeBudget,
    QualityFailClosedPolicy,
    QualityPolicyDeclaration,
    SafeDiagnosticPolicy,
    build_fund_llm_execution_request,
    derive_host_timeout_seconds,
    normalize_fund_llm_analysis_input,
)
from fund_agent.services.chapter_orchestrator import ChapterOrchestratorLLMClients


def test_valid_contract_from_normalized_fund_analysis_request() -> None:
    """验证 `FundAnalysisRequest` 可归一化为稳定 LLM 业务契约。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当规范化输入或契约字段不符合 Slice 1 计划时抛出。
    """

    analysis_input = normalize_fund_llm_analysis_input(
        FundAnalysisRequest(fund_code="110011", report_year=2024, command_source="analyze")
    )
    quality_policy = QualityPolicyDeclaration(
        quality_gate_policy="block",
        deterministic_fallback_allowed=False,
    )

    contract = FundLLMExecutionContract(
        fund_code="110011",
        report_year=2024,
        analysis_input=analysis_input,
        quality_policy=quality_policy,
    )

    assert analysis_input == FundLLMAnalysisInput(
        fund_code="110011",
        report_year=2024,
        command_source="analyze",
    )
    assert contract.schema_version == "fund_llm_execution_contract.v1"
    assert contract.report_mode == "llm_report"
    assert contract.llm_opt_in_mode == "explicit_cli_flag"
    assert contract.quality_policy.deterministic_fallback_allowed is False


@pytest.mark.parametrize(
    ("fund_code", "report_year", "message"),
    [
        ("110012", 2024, "fund_code"),
        ("110011", 2023, "report_year"),
    ],
)
def test_contract_rejects_identity_or_report_year_mismatch(
    fund_code: str,
    report_year: int,
    message: str,
) -> None:
    """验证契约拒绝 fund identity 或 report year 不同源。

    Args:
        fund_code: 传入契约的基金代码。
        report_year: 传入契约的年报年份。
        message: 预期错误信息片段。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当契约未阻断身份漂移时抛出。
    """

    analysis_input = FundLLMAnalysisInput(fund_code="110011", report_year=2024)

    with pytest.raises(ValueError, match=message):
        FundLLMExecutionContract(
            fund_code=fund_code,
            report_year=report_year,
            analysis_input=analysis_input,
            quality_policy=QualityPolicyDeclaration(),
        )


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        ("report_mode", "deterministic_report", "report_mode"),
        ("llm_opt_in_mode", "implicit", "llm_opt_in_mode"),
    ],
)
def test_contract_rejects_invalid_report_mode_or_opt_in_mode(
    field_name: str,
    value: str,
    message: str,
) -> None:
    """验证契约固定 report mode 与 LLM opt-in mode。

    Args:
        field_name: 要覆盖的契约字段名。
        value: 非法字段值。
        message: 预期错误信息片段。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法固定枚举值未被拒绝时抛出。
    """

    kwargs = {
        "fund_code": "110011",
        "report_year": 2024,
        "analysis_input": FundLLMAnalysisInput(fund_code="110011", report_year=2024),
        "quality_policy": QualityPolicyDeclaration(),
        field_name: value,
    }

    with pytest.raises(ValueError, match=message):
        FundLLMExecutionContract(**kwargs)  # type: ignore[arg-type]


def test_quality_policy_rejects_deterministic_fallback_allowed() -> None:
    """验证 LLM 契约禁止 deterministic fallback。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当允许 fallback 未被拒绝时抛出。
    """

    with pytest.raises(ValueError, match="deterministic fallback"):
        QualityPolicyDeclaration(deterministic_fallback_allowed=True)


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        ("writer_timeout_seconds", 0, "writer_timeout_seconds"),
        ("auditor_timeout_seconds", -1, "auditor_timeout_seconds"),
        ("repair_timeout_seconds", 0, "repair_timeout_seconds"),
        ("timeout_max_attempts", 0, "timeout_max_attempts"),
    ],
)
def test_provider_runtime_budget_rejects_zero_or_negative_timeout_or_attempts(
    field_name: str,
    value: int,
    message: str,
) -> None:
    """验证 provider runtime budget 拒绝非法 timeout 或 attempts。

    Args:
        field_name: 要覆盖的预算字段名。
        value: 非法字段值。
        message: 预期错误信息片段。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法预算未被拒绝时抛出。
    """

    kwargs = _budget_kwargs()
    kwargs[field_name] = value

    with pytest.raises(ValueError, match=message):
        ProviderRuntimeBudget(**kwargs)


@pytest.mark.parametrize("host_timeout_seconds", [0, -1])
def test_runtime_plan_rejects_nonpositive_host_timeout(
    host_timeout_seconds: int,
) -> None:
    """验证 runtime plan 拒绝非正 Host timeout。

    Args:
        host_timeout_seconds: 非法 Host timeout 秒数。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法 Host timeout 未被拒绝时抛出。
    """

    with pytest.raises(ValueError, match="host_timeout_seconds"):
        _runtime_plan(host_timeout_seconds=host_timeout_seconds)


@pytest.mark.parametrize("target_chapter_ids", [(0,), (7,), (1, 2, 8)])
def test_runtime_plan_rejects_invalid_target_chapter_ids(
    target_chapter_ids: tuple[int, ...],
) -> None:
    """验证 runtime plan 只允许模板第 1-6 章。

    Args:
        target_chapter_ids: 非法目标章节集合。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法章节范围未被拒绝时抛出。
    """

    with pytest.raises(ValueError, match="第 1-6 章"):
        _runtime_plan(
            chapter_policy=_chapter_policy_with_unchecked_ids(target_chapter_ids)
        )


def test_host_timeout_derivation_uses_plan_formula() -> None:
    """验证 Host timeout 推导使用 Slice 1 公式。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当推导结果偏离计划公式时抛出。
    """

    budget = ProviderRuntimeBudget(
        writer_timeout_seconds=11,
        auditor_timeout_seconds=22,
        repair_timeout_seconds=33,
        timeout_max_attempts=2,
        timeout_backoff_seconds=1,
        max_output_chars=12000,
        prompt_payload_mode="compact",
    )

    assert derive_host_timeout_seconds(budget, chapter_count=6) == (11 + 22 + 33) * 2 * 6


def test_execution_contract_fields_exclude_runtime_and_host_fields() -> None:
    """验证稳定业务契约不携带 runtime-only 或 Host 生命周期字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当契约泄漏 runtime-only 或 Host 字段时抛出。
    """

    contract_field_names = {field.name for field in fields(FundLLMExecutionContract)}
    forbidden_names = {
        "chapter_policy",
        "assembly_policy",
        "provider_runtime_budget",
        "safe_diagnostic_policy",
        "llm_clients",
        "host_context",
        "host_timeout_seconds",
        "session_id",
        "run_id",
        "timeout_state",
        "cancel_state",
        "lifecycle_state",
        "extra_payload",
    }

    assert contract_field_names == {
        "fund_code",
        "report_year",
        "analysis_input",
        "quality_policy",
        "schema_version",
        "report_mode",
        "llm_opt_in_mode",
    }
    assert contract_field_names.isdisjoint(forbidden_names)


def test_execution_request_may_contain_runtime_plan_but_contract_does_not() -> None:
    """验证 runtime-only 字段只存在于 Service 内部 request/runtime plan。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 contract 与 runtime plan 边界漂移时抛出。
    """

    contract = FundLLMExecutionContract(
        fund_code="110011",
        report_year=2024,
        analysis_input=FundLLMAnalysisInput(fund_code="110011", report_year=2024),
        quality_policy=QualityPolicyDeclaration(),
    )
    runtime_plan = _runtime_plan()
    execution_request = FundLLMExecutionRequest(
        contract=contract,
        runtime_plan=runtime_plan,
        llm_clients=ChapterOrchestratorLLMClients(writer=None, auditor=None),
    )
    contract_field_names = {field.name for field in fields(execution_request.contract)}

    assert execution_request.runtime_plan.provider_runtime_budget == _provider_runtime_budget()
    assert execution_request.runtime_plan.host_timeout_seconds == 396
    assert "runtime_plan" not in contract_field_names
    assert "provider_runtime_budget" not in contract_field_names
    assert "llm_clients" not in contract_field_names


def test_new_dataclasses_and_public_signatures_exclude_open_business_bags() -> None:
    """验证新增类型和函数签名不引入开放业务参数袋。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当字段或签名出现 extra_payload、**kwargs 或 Any 映射袋时抛出。
    """

    public_objects = (
        FundLLMAnalysisInput,
        QualityPolicyDeclaration,
        ProviderRuntimeBudget,
        QualityFailClosedPolicy,
        SafeDiagnosticPolicy,
        FundLLMRuntimePlan,
        FundLLMExecutionContract,
        FundLLMExecutionRequest,
        build_fund_llm_execution_request,
        normalize_fund_llm_analysis_input,
        derive_host_timeout_seconds,
    )
    forbidden_parameter_names = {"extra_payload", "kwargs", "payload", "metadata", "context"}

    for public_object in public_objects:
        if is_dataclass(public_object):
            for field in fields(public_object):
                assert field.name not in forbidden_parameter_names
                assert not _is_open_business_bag(field.type)
        signature = inspect.signature(public_object)
        for parameter in signature.parameters.values():
            assert parameter.name not in forbidden_parameter_names
            assert parameter.kind is not inspect.Parameter.VAR_KEYWORD
            assert not _is_open_business_bag(parameter.annotation)


@pytest.mark.parametrize(
    "annotation",
    [
        "dict[str, Any]",
        '"dict[str, Any]"',
        "Mapping[str, Any]",
        "typing.Mapping[str, Any]",
    ],
)
def test_open_business_bag_guard_detects_future_annotation_strings(
    annotation: str,
) -> None:
    """验证开放参数袋 guard 可识别 postponed annotations 字符串。

    Args:
        annotation: future annotations 下可能出现在 field.type 或签名里的字符串注解。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当字符串形式开放业务参数袋未被识别时抛出。
    """

    assert _is_open_business_bag(annotation)


def _provider_runtime_budget() -> ProviderRuntimeBudget:
    """构造测试用 provider runtime 预算。

    Args:
        无。

    Returns:
        合法 provider runtime 预算。

    Raises:
        无显式抛出。
    """

    return ProviderRuntimeBudget(**_budget_kwargs())


def _runtime_plan(
    *,
    chapter_policy: ChapterOrchestrationPolicy | None = None,
    host_timeout_seconds: int = 396,
) -> FundLLMRuntimePlan:
    """构造测试用 Service runtime plan。

    Args:
        chapter_policy: 可选章节策略。
        host_timeout_seconds: Host timeout 秒数。

    Returns:
        合法 Service runtime plan。

    Raises:
        ValueError: 当传入策略或 Host timeout 非法时抛出。
    """

    return FundLLMRuntimePlan(
        chapter_policy=chapter_policy
        or ChapterOrchestrationPolicy(prompt_payload_mode="compact"),
        assembly_policy=FinalAssemblyPolicy(),
        provider_runtime_budget=_provider_runtime_budget(),
        quality_fail_closed_policy=QualityFailClosedPolicy(),
        safe_diagnostic_policy=SafeDiagnosticPolicy(),
        host_timeout_seconds=host_timeout_seconds,
    )


def _chapter_policy_with_unchecked_ids(
    target_chapter_ids: tuple[int, ...],
) -> ChapterOrchestrationPolicy:
    """构造绕过自身校验的章节策略以测试 runtime plan 边界。

    Args:
        target_chapter_ids: 需要注入的章节编号集合。

    Returns:
        带有测试章节编号的章节编排策略。

    Raises:
        无显式抛出。
    """

    policy = object.__new__(ChapterOrchestrationPolicy)
    object.__setattr__(policy, "target_chapter_ids", target_chapter_ids)
    object.__setattr__(policy, "max_repair_attempts", 1)
    object.__setattr__(policy, "max_output_chars", 12000)
    object.__setattr__(policy, "prompt_payload_mode", "compact")
    object.__setattr__(policy, "fail_fast", False)
    object.__setattr__(policy, "run_programmatic_audit", True)
    object.__setattr__(policy, "run_llm_audit", True)
    return policy


def _budget_kwargs() -> dict[str, object]:
    """构造 provider runtime budget 的显式测试参数。

    Args:
        无。

    Returns:
        可传入 `ProviderRuntimeBudget` 的字段参数。

    Raises:
        无显式抛出。
    """

    return {
        "writer_timeout_seconds": 11,
        "auditor_timeout_seconds": 22,
        "repair_timeout_seconds": 33,
        "timeout_max_attempts": 2,
        "timeout_backoff_seconds": 1,
        "max_output_chars": 12000,
        "prompt_payload_mode": "compact",
    }


def _is_open_business_bag(annotation: object) -> bool:
    """判断类型注解是否为开放业务参数袋。

    Args:
        annotation: 字段或参数注解。

    Returns:
        若注解是 `dict[str, Any]` 或 `Mapping[str, Any]` 则返回 True。

    Raises:
        无显式抛出。
    """

    if isinstance(annotation, str):
        return _is_open_business_bag_annotation_text(annotation)

    origin = get_origin(annotation)
    args = get_args(annotation)
    return bool(
        origin in {dict, Mapping, CollectionsMapping}
        and len(args) == 2
        and args[0] is str
        and args[1] is Any
    )


def _is_open_business_bag_annotation_text(annotation: str) -> bool:
    """判断字符串注解是否为开放业务参数袋。

    Args:
        annotation: future annotations 下保留的字符串注解。

    Returns:
        若字符串注解是 `dict[str, Any]`、`Mapping[str, Any]`
        或 `typing.Mapping[str, Any]` 则返回 True。

    Raises:
        无显式抛出。
    """

    normalized_annotation = annotation.strip()
    while (
        len(normalized_annotation) >= 2
        and normalized_annotation[0] == normalized_annotation[-1]
        and normalized_annotation[0] in {"'", '"'}
    ):
        normalized_annotation = normalized_annotation[1:-1].strip()
    normalized_annotation = normalized_annotation.replace(" ", "")
    return normalized_annotation in {
        "dict[str,Any]",
        "Mapping[str,Any]",
        "typing.Mapping[str,Any]",
    }
