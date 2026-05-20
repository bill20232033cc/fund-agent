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
from fund_agent.fund.template.renderer import (
    RenderedChapterBlock,
    TemplateFinalJudgment,
    TemplateRenderInput,
    TemplateRenderResult,
    build_programmatic_audit_input,
    get_template_chapter_heading,
    render_template_report,
    split_rendered_chapter_blocks,
)

__all__ = [
    "ChapterContract",
    "RenderedChapterBlock",
    "TemplateContractManifest",
    "TemplateFinalJudgment",
    "TemplateLensRule",
    "TemplateRenderInput",
    "TemplateRenderResult",
    "build_programmatic_audit_input",
    "get_chapter_contract",
    "get_template_chapter_heading",
    "load_template_contract_manifest",
    "render_template_report",
    "resolve_preferred_lens",
    "split_rendered_chapter_blocks",
    "validate_template_contract_manifest",
]
