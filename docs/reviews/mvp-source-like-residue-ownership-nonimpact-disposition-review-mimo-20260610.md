# Source-like residue ownership / non-impact disposition — AgentMiMo review

Date: 2026-06-10

Reviewer: AgentMiMo

Gate: `source-like residue ownership / non-impact disposition gate`

## Review inputs

- `docs/reviews/mvp-source-like-residue-ownership-nonimpact-disposition-startup-judgment-20260610.md`
- `docs/reviews/mvp-source-like-residue-ownership-nonimpact-disposition-evidence-20260610.md`

## Independent verification

Reviewer ran all verification commands independently; results match the evidence artifact exactly.

### 1. Direct evidence: fund_agent/tools/ 和 scripts/claude_mimo_simple.py 均未 tracked/staged

**Verified — PASS.**

- `git status --branch --short` 确认两个路径显示为 `??`（untracked）。
- `git ls-files -- fund_agent/tools scripts/claude_mimo_simple.py` 返回空。
- `git diff --cached --name-only` 返回空，无文件被 staged。
- `git ls-files --others --exclude-standard` 正确列出 `fund_agent/tools/claude_mimo.py` 和 `scripts/claude_mimo_simple.py`。

Evidence artifact 的 working tree state、tracked-file ownership、staging state 三节声明完全准确。

### 2. Tracked source/tests/config 无依赖

**Verified — PASS.**

- `git grep -n -e 'claude_mimo' -e 'fund_agent\.tools' -e 'claude_mimo_simple' -- fund_agent tests pyproject.toml` 返回 exit code 1，无匹配。
- 扩展到全仓库 `*.py *.toml *.cfg *.txt *.yaml *.yml` 仍无匹配。

Tracked 代码、测试、配置对这两个路径无任何 import、reference 或字符串依赖。

### 3. pyproject package include 风险记录

**Verified — PASS，且存在额外缓解因素。**

Evidence artifact 正确指出：

- `include = ["fund_agent*"]` 会覆盖 `fund_agent/tools/`。
- `exclude = ["scripts*"]` 会排除 `scripts/`。

Reviewer 补充发现：`fund_agent/tools/` 目录内不存在 `__init__.py`。这意味着即使 `claude_mimo.py` 被意外提交，Python 仍无法将其作为常规包模块 import（除非启用了 implicit namespace packages）。Package include 规则会将其纳入分发包，但实际运行时 import 链路不通。这进一步降低了意外提交的实际影响面。

### 4. 降级为 non-impact residual 的判断

**支持降级 — PASS_WITH_RESIDUAL。**

理由：

- 路径完全 untracked、unstaged，且无 tracked 依赖。
- 即使意外提交，缺少 `__init__.py` 会阻断 import 链路。
- 文件内容为本地 Claude 配置助手，不参与 EID source policy、extractor、fixture、provider runtime 或 fallback。
- 证据链完整，非推测性结论。

唯一残留风险是 package-scope drift：如果未来有人在 `fund_agent/tools/` 添加 `__init__.py` 并提交，该目录会自动成为 package source。此风险通过 planning gate 的 explicit ignore boundary 可控。

### 5. 隐性阻断风险

**未发现 — PASS。**

- 两个文件不参与任何 tracked 运行时路径。
- 不影响 EID source policy 或 `FundDocumentRepository`。
- 不影响 extractor、fixture、provider、fallback 或 quality gate。
- 不影响 package build（无 `__init__.py`）。
- 不存在 import chain 隐性依赖（git grep 全仓库确认）。

## Verdict

**PASS_WITH_RESIDUAL**

Source-like residue 可安全降级为 non-impact residual。EID implementation planning 可在以下条件下继续：

- Planning gate 明确声明 `fund_agent/tools/` 和 `scripts/claude_mimo_simple.py` 为 ignored workspace residue。
- Planning gate 的 allowed files 列表排除这两个路径。
- 不得向 `fund_agent/tools/` 添加 `__init__.py` 或其他文件，除非经由独立 gate 审批。

## Residual risk

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| package-scope drift: `fund_agent/tools/` 被意外提交 | Low | Medium | Planning gate explicit ignore; no `__init__.py` prevents import |
| 路径内容变更后被 git add -A 意外 stage | Low | Low | `.gitignore` 可考虑覆盖；当前 untracked 状态已有保护 |
