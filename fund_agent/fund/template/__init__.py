"""基金模板公共入口。"""

from fund_agent.fund.template.contracts import (
    ChapterContract,
    TemplateContractManifest,
    TemplateLensRule,
    get_chapter_contract,
    load_template_contract_manifest,
    resolve_preferred_lens,
    validate_template_contract_manifest,
)
from fund_agent.fund.template.chapter_blocks import (
    EVIDENCE_APPENDIX_HEADING,
    RenderedChapterBlock,
    get_template_chapter_heading,
    split_rendered_chapter_blocks,
)
from fund_agent.fund.template.item_rules import (
    TemplateItemRule,
    TemplateItemRuleDecision,
    TemplateItemRuleDecisionStatus,
    TemplateItemRuleManifest,
    TemplateItemRuleMissingBehavior,
    TemplateItemRuleMode,
    evaluate_template_item_rule,
    evaluate_template_item_rules,
    get_template_item_rule,
    load_template_item_rule_manifest,
    rendered_segment_present,
    validate_template_item_rule_manifest,
)
from fund_agent.fund.template.lens_application import (
    LensApplicationPlan,
    LensChapterApplication,
    build_lens_application_plan,
)

_RENDERER_EXPORTS = {
    "TemplateFinalJudgment",
    "TemplateRenderInput",
    "TemplateRenderResult",
    "build_programmatic_audit_input",
    "render_template_report",
}


def __getattr__(name: str) -> object:
    """按需加载模板渲染器导出对象。

    Args:
        name: 待读取的导出名称。

    Returns:
        渲染器导出对象。

    Raises:
        AttributeError: 名称不属于本模块公开导出时抛出。
    """

    if name not in _RENDERER_EXPORTS:
        raise AttributeError(f"module 'fund_agent.fund.template' has no attribute {name!r}")

    from fund_agent.fund.template import renderer

    return getattr(renderer, name)

__all__ = [
    "ChapterContract",
    "EVIDENCE_APPENDIX_HEADING",
    "RenderedChapterBlock",
    "LensApplicationPlan",
    "LensChapterApplication",
    "TemplateContractManifest",
    "TemplateFinalJudgment",
    "TemplateItemRule",
    "TemplateItemRuleDecision",
    "TemplateItemRuleDecisionStatus",
    "TemplateItemRuleManifest",
    "TemplateItemRuleMissingBehavior",
    "TemplateItemRuleMode",
    "TemplateLensRule",
    "TemplateRenderInput",
    "TemplateRenderResult",
    "build_programmatic_audit_input",
    "build_lens_application_plan",
    "evaluate_template_item_rule",
    "evaluate_template_item_rules",
    "get_chapter_contract",
    "get_template_chapter_heading",
    "get_template_item_rule",
    "load_template_contract_manifest",
    "load_template_item_rule_manifest",
    "render_template_report",
    "rendered_segment_present",
    "resolve_preferred_lens",
    "split_rendered_chapter_blocks",
    "validate_template_contract_manifest",
    "validate_template_item_rule_manifest",
]
