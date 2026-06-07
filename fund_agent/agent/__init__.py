"""Agent 执行内核入口，见基金分析模板第 1-6 章。

本包承载本项目内化的 Agent runner、ToolTrace、repair policy 和 body chapter
readiness。当前实现不得直接依赖 `dayu-agent` / `dayu.engine`，也不得导入
`fund_agent.host`。
"""

from fund_agent.agent.contracts import (
    AGENT_CONTRACTS_SCHEMA_VERSION,
    AgentAcceptedChapterConclusion,
    AgentRepairPolicy,
    AgentReportRun,
    AgentReportRunStatus,
    AgentSchedulerInterruption,
    AgentSchedulerInterruptionStatus,
    AgentTerminalState,
    ChapterAttempt,
    ChapterTask,
    FinalAssemblyReadiness,
    ToolCallRequest,
    ToolCallResult,
    ToolTrace,
)
from fund_agent.agent.repair import AgentRepairDecision, decide_repair, repair_context_from_audit
from fund_agent.agent.runner import (
    AgentLLMClients,
    AgentRunPolicy,
    AgentRunner,
    run_agent_body_chapters,
)

__all__ = [
    "AGENT_CONTRACTS_SCHEMA_VERSION",
    "AgentAcceptedChapterConclusion",
    "AgentRepairPolicy",
    "AgentReportRun",
    "AgentReportRunStatus",
    "AgentSchedulerInterruption",
    "AgentSchedulerInterruptionStatus",
    "AgentTerminalState",
    "ChapterAttempt",
    "ChapterTask",
    "FinalAssemblyReadiness",
    "ToolCallRequest",
    "ToolCallResult",
    "ToolTrace",
    "AgentRepairDecision",
    "decide_repair",
    "repair_context_from_audit",
    "AgentLLMClients",
    "AgentRunPolicy",
    "AgentRunner",
    "run_agent_body_chapters",
]
