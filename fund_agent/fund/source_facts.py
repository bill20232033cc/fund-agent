"""Fund 层 atomic source fact 契约。

本模块定义基金结构化提取的原子事实存储和复合分析视图，见模板第 2 章
R=A+B-C 与第 3 章“基金经理画像”。它只承载 Processor / Extractor 输出的受控
事实，不读取文档仓库、PDF/cache/source helper、provider、LLM、Service/UI/Host。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from fund_agent.fund.extractors.models import EvidenceAnchor


@dataclass(frozen=True, slots=True)
class FactDependencyMetadata:
    """事实依赖元数据。

    Attributes:
        dependency_fact_ids: 当前事实或视图依赖的原子事实 ID。
        dependency_policy: 依赖满足策略，例如 `none`、`all_required` 或
            `compatible_view`。
        derived_from_view_id: 派生来源视图 ID；原子事实为 `None`。
        notes: 额外说明。
    """

    dependency_fact_ids: tuple[str, ...] = ()
    dependency_policy: str = "none"
    derived_from_view_id: str | None = None
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """校验依赖元数据形状。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当依赖策略为空、依赖 ID 为空字符串或重复时抛出。
        """

        if not self.dependency_policy:
            raise ValueError("dependency_policy 不能为空")
        _validate_non_empty_unique_ids(self.dependency_fact_ids, "dependency_fact_ids")


@dataclass(frozen=True, slots=True)
class AtomicSourceFact:
    """单个披露来源原子事实。

    Attributes:
        fact_id: 稳定事实 ID，必须等于 `source_field_path`。
        family_id: 所属字段族 ID。
        value: 原子事实值；缺失时为 `None`。
        status: 抽取状态。
        extraction_mode: 抽取模式。
        anchors: 直接证明该事实的证据锚点。
        provenance: 来源 provenance；S1 不限定具体类型。
        gaps: 当前事实缺口说明。
        source_field_path: 来源字段路径，必须等于 `fact_id`。
        dependency_metadata: 依赖元数据；原子事实不得依赖 sibling fact。
    """

    fact_id: str
    family_id: str
    value: object | None
    status: str
    extraction_mode: str
    anchors: tuple[EvidenceAnchor, ...]
    provenance: object | None
    gaps: tuple[str, ...]
    source_field_path: str
    dependency_metadata: FactDependencyMetadata = field(default_factory=FactDependencyMetadata)

    def __post_init__(self) -> None:
        """校验 atomic source fact 的最小不变量。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当事实 ID、family、状态、抽取模式、source path 或原子依赖非法时抛出。
        """

        if not self.fact_id:
            raise ValueError("fact_id 不能为空")
        if not self.family_id:
            raise ValueError("family_id 不能为空")
        if not self.status:
            raise ValueError("status 不能为空")
        if not self.extraction_mode:
            raise ValueError("extraction_mode 不能为空")
        if self.source_field_path != self.fact_id:
            raise ValueError("AtomicSourceFact.fact_id 必须等于 source_field_path")
        if self.dependency_metadata.dependency_fact_ids:
            raise ValueError("AtomicSourceFact 不得依赖 sibling source facts")


@dataclass(frozen=True, slots=True)
class CompositeAnalysisView:
    """由 atomic source facts 组合得到的分析视图。

    Attributes:
        view_id: 稳定视图 ID。
        value: 视图值；缺失时为 `None`。
        status: 视图状态。
        anchors: 从依赖事实聚合的证据锚点。
        gaps: 视图级缺口说明。
        dependency_fact_ids: 构成该视图的 atomic source fact IDs。
    """

    view_id: str
    value: object | None
    status: str
    anchors: tuple[EvidenceAnchor, ...]
    gaps: tuple[str, ...]
    dependency_fact_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        """校验复合分析视图形状。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当视图 ID、状态或依赖事实 ID 非法时抛出。
        """

        if not self.view_id:
            raise ValueError("view_id 不能为空")
        if not self.status:
            raise ValueError("status 不能为空")
        _validate_non_empty_unique_ids(self.dependency_fact_ids, "dependency_fact_ids")


@dataclass(frozen=True, slots=True)
class AtomicSourceFactStore:
    """不可变 atomic source fact 存储。

    Attributes:
        facts: 按 `fact_id` 索引的不可变事实映射。
    """

    facts: Mapping[str, AtomicSourceFact]

    def __init__(self, facts: Mapping[str, AtomicSourceFact] | tuple[AtomicSourceFact, ...] = ()):
        """初始化不可变事实存储。

        Args:
            facts: 事实映射或事实序列。序列按 `fact_id` 建立索引。

        Returns:
            无返回值。

        Raises:
            ValueError: 当映射 key 与 fact id 不一致或存在重复 fact id 时抛出。
        """

        normalized: dict[str, AtomicSourceFact] = {}
        if isinstance(facts, Mapping):
            iterable = tuple(facts.items())
        else:
            iterable = tuple((fact.fact_id, fact) for fact in facts)
        for fact_id, fact in iterable:
            if fact_id != fact.fact_id:
                raise ValueError("AtomicSourceFactStore key 必须等于 fact.fact_id")
            if fact_id in normalized:
                raise ValueError(f"AtomicSourceFactStore 存在重复 fact_id: {fact_id}")
            normalized[fact_id] = fact
        object.__setattr__(self, "facts", MappingProxyType(normalized))

    def get_required(self, fact_id: str) -> AtomicSourceFact:
        """读取必需事实。

        Args:
            fact_id: 稳定事实 ID。

        Returns:
            对应的 atomic source fact。

        Raises:
            KeyError: 当事实不存在时抛出。
        """

        return self.facts[fact_id]

    def get_optional(self, fact_id: str) -> AtomicSourceFact | None:
        """读取可选事实。

        Args:
            fact_id: 稳定事实 ID。

        Returns:
            存在时返回事实，否则返回 `None`。

        Raises:
            无显式抛出。
        """

        return self.facts.get(fact_id)

    def by_family(self, family_id: str) -> tuple[AtomicSourceFact, ...]:
        """按字段族读取事实。

        Args:
            family_id: 字段族 ID。

        Returns:
            属于该字段族的事实，按 `fact_id` 排序。

        Raises:
            无显式抛出。
        """

        return tuple(
            self.facts[fact_id]
            for fact_id in sorted(self.facts)
            if self.facts[fact_id].family_id == family_id
        )

    def merge_strict(self, other: "AtomicSourceFactStore") -> "AtomicSourceFactStore":
        """严格合并两个事实存储。

        Args:
            other: 待合并事实存储。

        Returns:
            合并后的新事实存储；相同 fact id 且事实完全相等时保留一份。

        Raises:
            ValueError: 当相同 fact id 对应不同事实时抛出。
        """

        merged = dict(self.facts)
        for fact_id, fact in other.facts.items():
            existing = merged.get(fact_id)
            if existing is not None and existing != fact:
                raise ValueError(f"AtomicSourceFactStore fact_id 冲突: {fact_id}")
            merged[fact_id] = fact
        return AtomicSourceFactStore(merged)


def empty_atomic_source_fact_store() -> AtomicSourceFactStore:
    """构造空 atomic source fact store。

    Args:
        无。

    Returns:
        空事实存储。

    Raises:
        无显式抛出。
    """

    return AtomicSourceFactStore()


def build_composite_analysis_view(
    *,
    view_id: str,
    source_facts: AtomicSourceFactStore,
    dependency_fact_ids: tuple[str, ...],
    required_fact_ids: tuple[str, ...] | None = None,
) -> CompositeAnalysisView:
    """根据 atomic source facts 构造复合分析视图。

    Args:
        view_id: 稳定视图 ID。
        source_facts: 原子事实存储。
        dependency_fact_ids: 参与视图组装的事实 ID。
        required_fact_ids: 必需事实 ID；缺省时全部依赖都必需。

    Returns:
        复合分析视图。视图值只由存在的依赖事实派生为 `{fact_id: fact.value}`；
        缺少依赖时返回 `partial` 或 `missing` 并记录缺口，不信任调用方提供的复合值。

    Raises:
        ValueError: 当依赖 ID 为空字符串、重复，或 `required_fact_ids` 不是
            `dependency_fact_ids` 子集时抛出。
    """

    required = dependency_fact_ids if required_fact_ids is None else required_fact_ids
    _validate_non_empty_unique_ids(dependency_fact_ids, "dependency_fact_ids")
    _validate_non_empty_unique_ids(required, "required_fact_ids")
    dependency_fact_id_set = set(dependency_fact_ids)
    missing_required = tuple(
        fact_id for fact_id in required if fact_id not in dependency_fact_id_set
    )
    if missing_required:
        raise ValueError("required_fact_ids 必须是 dependency_fact_ids 的子集")

    facts_by_id = {
        fact_id: source_facts.get_optional(fact_id) for fact_id in dependency_fact_ids
    }
    facts = tuple(fact for fact in facts_by_id.values() if fact is not None)
    missing_fact_ids = tuple(
        fact_id for fact_id, fact in facts_by_id.items() if fact is None
    )
    required_facts = tuple(
        facts_by_id[fact_id] for fact_id in required if facts_by_id[fact_id] is not None
    )
    missing_required_fact_ids = tuple(
        fact_id for fact_id in required if facts_by_id[fact_id] is None
    )
    gaps = tuple(gap for fact in facts for gap in fact.gaps)
    dependency_gaps = tuple(
        f"missing dependency fact: {fact_id}" for fact_id in missing_fact_ids
    )
    anchors = tuple(anchor for fact in facts for anchor in fact.anchors)
    if not dependency_fact_ids or not facts:
        status = "missing"
    elif (
        not missing_fact_ids
        and not missing_required_fact_ids
        and len(required_facts) == len(required)
        and all(fact.status == "accepted" for fact in facts)
    ):
        status = "accepted"
    else:
        status = "partial"
    value = (
        {fact_id: fact.value for fact_id, fact in facts_by_id.items() if fact is not None}
        if facts
        else None
    )
    return CompositeAnalysisView(
        view_id=view_id,
        value=value,
        status=status,
        anchors=anchors,
        gaps=gaps + dependency_gaps,
        dependency_fact_ids=dependency_fact_ids,
    )


def _validate_non_empty_unique_ids(values: tuple[str, ...], field_name: str) -> None:
    """校验 ID 序列没有空值或重复值。

    Args:
        values: 待校验 ID 序列。
        field_name: 报错时使用的字段名。

    Returns:
        无返回值。

    Raises:
        ValueError: 当存在空字符串或重复 ID 时抛出。
    """

    if any(not value for value in values):
        raise ValueError(f"{field_name} 不能包含空字符串")
    if len(set(values)) != len(values):
        raise ValueError(f"{field_name} 不能包含重复 ID")
