"""基金模板渲染公共入口。"""

from fund_agent.fund.template.renderer import (
    TemplateFinalJudgment,
    TemplateRenderInput,
    TemplateRenderResult,
    build_programmatic_audit_input,
    render_template_report,
)

__all__ = [
    "TemplateFinalJudgment",
    "TemplateRenderInput",
    "TemplateRenderResult",
    "build_programmatic_audit_input",
    "render_template_report",
]
