# Plan Review: Share-Change Focused Implementation + Bond-Lens Contract Design Choice

> **Reviewer**: AgentGLM (independent plan reviewer)
> **Date**: 2026-05-27
> **Review target**: `docs/reviews/release-maintenance-share-change-focused-implementation-plan-20260527.md`
> **Truth sources**: `AGENTS.md`, `docs/design.md` current design, `docs/implementation-control.md` Startup Packet / current gate / next entry, accepted artifacts
> **Prior evidence**: Baseline triage evidence (`release-maintenance-baseline-coverage-source-taxonomy-bond-triage-evidence-20260527.md`) and controller judgment

---

## Findings

### F1 — INFO: Reconciliation 正确保守，不 overclaim 006597 quality-gate readiness

**Evidence**:
- Reconciliation 表格精确复述六项 accepted field classifications，仅 `share_change` 标记为 implementation-ready（lines 18-24）。
- "The next minimal implementation slice should not try to make 006597 fully quality-gate clean."（line 26）
- Test strategy 明确预期："Quality gate may still be `block` because `turnover_rate`, `holder_structure`, and `holdings_snapshot` are intentionally out of scope."（line 142）
- Acceptance criteria 要求 "any remaining block is attributable to out-of-scope fields"（line 237）。
- Golden corpus v1 remains ineligible（line 241）。

**Risk**: 无。Plan 对 quality-gate outcome 的预期完全诚实。

---

### F2 — INFO: share_change root cause 由 accepted evidence 同源支撑

**Evidence**:
- Root cause statement 引用 triage evidence artifact、controller judgment 和 public CLI snapshot row（lines 30-35）。
- 直接引用 snapshot note："§10 份额变动表存在多个份额列，当前规则无法可靠选择对应份额类别"（line 39）。
- Controller judgment classification 为 `extractor_gap`（line 40）。
- 正确排除三种误判："not a quality-gate threshold problem, not a golden-answer promotion problem, and not a source fallback problem."（line 42）。

**Risk**: 无。Root cause 与 triage evidence 完全同源。

---

### F3 — MINOR: Behavior contract 要求 `share_class_selection_reason` 输出字段，但 authorized file scope 未包含 extractor models

**Evidence**:
- Behavior contract 要求成功输出包含 `share_class_selection_reason`（line 91）。
- Authorized production file 仅列 `fund_agent/fund/extractors/holdings_share_change.py`（line 63），`fund_agent/fund/extractors/models.py` 未列入 allowed 或 conditionally allowed files。
- 若 share-change result dataclass 需要新增字段来承载 `share_class_selection_reason`，则需修改 models.py。若使用现有 `note` 字段或 dict 结构传递，则无需 models.py 变更。
- Plan 未讨论这一可能性。

**Risk**: Implementation worker 可能发现需要 models.py 变更但发现文件不在 authorized scope 中，导致不必要的 stop-and-ask。这是 scope 预见性不足，不是语义错误。

**Recommendation**: Plan 应将 `fund_agent/fund/extractors/models.py` 列为 conditionally allowed（类似 `extraction_snapshot.py` 的处理方式），条件为"仅在 share-change result dataclass 需要新增 share_class_selection_reason / share_class_column 字段时"。或者明确指定 `share_class_selection_reason` 使用现有 `note` 字段，避免 model 变更。不阻塞 plan acceptance，可在 controller judgment 或 implementation 阶段补强。

---

### F4 — INFO: Behavior contract 的 fail-closed 语义严格且无漏洞

**Evidence**:
- 确定性选择仅允许三种 evidence source：exact fund_code header、§2 subordinate mapping、§2 text mapping（lines 83-86）。每种都要求唯一匹配。
- 成功输出必须包含 extraction_mode="direct"、share values、share_class_column、share_class_selection_reason、§10 anchor（lines 87-92）。
- 失败必须 fail closed：extraction_mode="missing"、no anchor、explicit ambiguity note（lines 93-96）。
- 显式禁止四种常见错误默认："must not default to A class, first non-empty column, total-share column, or any column from a different fund code."（line 97）。
- "must not reduce P1 priority, FQ severity, or missing-field-rate behavior"（line 98）。

这与 `AGENTS.md` 的 fail-closed fallback 纪律在哲学上一致：宁可保持 ambiguity，也不选错列。 ✓

**Risk**: 无。

---

### F5 — INFO: Test strategy 可执行且覆盖充分

**Evidence**:
- 7 项 focused unit tests 覆盖：正确选择、无 mapping 时保持 missing、多匹配时保持 missing、reject total-share、reject other fund code header、existing tests regression（lines 126-131）。
- Implementation strategy 要求 test-first with synthetic fixtures（line 104），不使用 production PDF/cache ✓。
- 006597 public CLI rerun 有明确的两路径预期：成功直接抽取或保持显式 ambiguity（lines 139-141）。
- Full pytest conditional trigger 清晰（lines 157-164）——仅在 snapshot/score/gate/models 被触碰时要求。
- Focused commands 可直接复制执行（lines 147-155）。

**Risk**: 无。Test strategy 的两路径预期（直接抽取 vs 保持 ambiguity）与 plan 的保守定位完全一致。

---

### F6 — INFO: holdings_snapshot 正确 deferred 至独立 bond-lens contract design gate

**Evidence**:
- "Decision: do not implement holdings_snapshot in the share_change slice."（line 169）。
- 理由引用 accepted `bond_lens_contract_gap` classification ✓。
- 列出 5 项 required design questions 供未来 gate 使用（lines 182-186）。
- "Current share_change slice can ignore holdings_snapshot because it neither changes the accepted classification nor tries to clear the whole 006597 quality gate."（line 188）。
- Non-goals 显式列出 "No holdings_snapshot implementation in this slice."（line 249）。

**Risk**: 无。Defer 决策正确且理由充分。

---

### F7 — INFO: Stop conditions 和 verifier matrix 全面

**Evidence**:
- Stop conditions 覆盖 7 类阻断场景（lines 205-213）：forbidden access、unprovable deterministic choice、source fallback changes、FQ changes、broad bond analytics、service/CLI/Host changes、no-progress after fix。
- Verifier matrix 7 行覆盖：plan closeout、unit tests、focused regression、lint、public smoke × 3、final hygiene（lines 217-226）。
- Acceptance criteria 6 条覆盖：deterministic selection tests、fail-closed preservation、006597 two-path rerun、FQ strictness unchanged、no forbidden mutations、git diff --check（lines 230-239）。
- 所有 stop conditions 与 Non-Goals 无矛盾。

**Risk**: 无。

---

### F8 — INFO: Implementation 应被授权；plan 是合格的 implementation gate candidate

**Evidence**:
- share_change 是 baseline triage 中唯一有 concrete same-source root cause 的字段 ✓
- Behavior contract 的 fail-closed 语义覆盖了主要错误模式 ✓
- File scope 最小（1 primary + 1 conditional + 1 conditional for models）✓
- holdings_snapshot 正确 defer ✓
- Test strategy 有可执行的 pass/fail 标准 ✓
- Plan 不 overclaim quality-gate readiness ✓

**Risk**: 无。Plan 的保守定位和严格 fail-closed 语义使其成为安全的 implementation gate candidate。

---

## Verdict

**PASS_WITH_FINDINGS**

Plan 的 reconciliation、root cause、behavior contract、test strategy 和 defer 决策均达到高质量。一个 MINOR finding 不阻塞 closeout：

- **F3**: `share_class_selection_reason` 可能需要 extractor model 变更，plan 应预授权 `fund_agent/fund/extractors/models.py` 或指定使用现有 note 字段。

Controller 可在 judgment 中补强 F3 后授权 implementation。

| Finding | Severity | Blocks gate? |
|---------|----------|-------------|
| F1: Reconciliation conservative | INFO | No |
| F2: Root cause same-source | INFO | No |
| F3: share_class_selection_reason model scope | MINOR | No |
| F4: Fail-closed semantics strong | INFO | No |
| F5: Test strategy executable | INFO | No |
| F6: holdings_snapshot correctly deferred | INFO | No |
| F7: Stop conditions comprehensive | INFO | No |
| F8: Implementation should be authorized | INFO | No |

---

## Truth Source Alignment Confirmation

- [x] Plan 不违反 `AGENTS.md` 硬约束：四层边界未突破、无 FundDocumentRepository 直访、无 fallback 语义变更、root cause 同源、无 extra_payload。
- [x] Plan 不违反 `docs/design.md` 非目标：不改 renderer/FQ0-FQ6 阈值或 severity、不引入 Host/Agent/dayu、不改 Service/CLI defaults。
- [x] Plan 与 accepted triage evidence 和 controller judgment 完全一致。
- [x] Non-goals 完整覆盖所有禁止项，包括 6 个 out-of-scope fields 的显式排除。
