"""Fund Processor 注册表。

本模块只提供 processor class 的纯内存注册和解析，不触碰年报仓库、PDF/cache/source
helper、Docling、network、provider、LLM、Service/UI/Host 或 filesystem。
"""

from __future__ import annotations

from dataclasses import dataclass

from fund_agent.fund.processors.contracts import (
    FundProcessorDispatchKey,
    FundProcessorProtocol,
)


class UnsupportedFundProcessorError(LookupError):
    """没有可用 processor 时的 fail-closed 异常。"""


@dataclass(frozen=True, slots=True)
class _ProcessorRegistration:
    """单条 processor 注册记录。

    Args:
        无。

    Attributes:
        processor_cls: Processor 类。
        priority: 注册优先级，数值越大越优先。
        order: 注册顺序，用于同优先级稳定排序。

    Raises:
        无显式抛出。
    """

    processor_cls: type[FundProcessorProtocol]
    priority: int
    order: int


class FundProcessorRegistry:
    """Fund Processor 注册表。

    注册表按 priority 降序、注册顺序升序解析 processor。没有 processor 支持
    当前 dispatch key 时，必须 fail-closed，不能 fallback 到原始 parser dump。
    """

    def __init__(self) -> None:
        """初始化空注册表。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._registrations: list[_ProcessorRegistration] = []
        self._processor_ids: set[str] = set()

    def register(
        self,
        processor_cls: type[FundProcessorProtocol],
        priority: int | None = None,
    ) -> None:
        """注册 processor 类。

        Args:
            processor_cls: 待注册的 processor 类。
            priority: 可选覆盖优先级；缺省使用类属性 `priority`。

        Returns:
            无返回值。

        Raises:
            TypeError: 当 priority 不是整数时抛出。
            ValueError: 当 processor_id 缺失或重复时抛出。
        """

        processor_id = getattr(processor_cls, "processor_id", None)
        if not isinstance(processor_id, str) or not processor_id:
            raise ValueError("processor_cls.processor_id 必须是非空字符串")
        if processor_id in self._processor_ids:
            raise ValueError(f"processor_id 已注册：{processor_id}")
        resolved_priority = getattr(processor_cls, "priority", 0) if priority is None else priority
        if not isinstance(resolved_priority, int):
            raise TypeError("priority 必须是整数")

        self._processor_ids.add(processor_id)
        self._registrations.append(
            _ProcessorRegistration(
                processor_cls=processor_cls,
                priority=resolved_priority,
                order=len(self._registrations),
            )
        )

    def resolve(self, context: FundProcessorDispatchKey) -> FundProcessorProtocol:
        """解析第一个支持 dispatch key 的 processor。

        Args:
            context: Processor 路由键。

        Returns:
            Processor 实例。

        Raises:
            UnsupportedFundProcessorError: 当没有 processor 支持当前路由键时抛出。
        """

        ordered = sorted(
            self._registrations,
            key=lambda registration: (-registration.priority, registration.order),
        )
        for registration in ordered:
            processor = registration.processor_cls()
            if processor.supports(context):
                return processor
        raise UnsupportedFundProcessorError(
            "unsupported_processor: no registered processor supports "
            f"fund_type={context.fund_type}, report_type={context.report_type}, "
            f"intermediate_kind={context.intermediate_kind}"
        )

    @classmethod
    def create_default(cls) -> "FundProcessorRegistry":
        """创建默认 processor 注册表。

        Args:
            无。

        Returns:
            注册了当前 S1 active annual processor 的注册表。

        Raises:
            ValueError: 当默认 processor 注册冲突时抛出。
        """

        from fund_agent.fund.processors.active_annual import ActiveFundAnnualProcessor

        registry = cls()
        registry.register(ActiveFundAnnualProcessor)
        return registry
