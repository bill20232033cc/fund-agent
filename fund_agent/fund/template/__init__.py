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
    RenderedChapterBlock,
    get_template_chapter_heading,
    split_rendered_chapter_blocks,
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
