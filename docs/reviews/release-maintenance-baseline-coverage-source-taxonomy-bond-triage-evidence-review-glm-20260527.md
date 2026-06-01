# Evidence Review: Baseline Coverage / Source Recovery / Taxonomy + Bond Triage

> **Reviewer**: AgentGLM (independent evidence reviewer)
> **Date**: 2026-05-27
> **Review target**: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-evidence-20260527.md`
> **Accepted plan**: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-20260527.md` (revised)
> **Controller judgment**: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-controller-judgment-20260527.md`
> **Truth sources**: `AGENTS.md`, `docs/design.md` current design, `docs/implementation-control.md` Startup Packet / current gate / next entry

---

## Findings

### F1 — INFO: Evidence run 严格保持在 authorized public-output scope 内

**Evidence**:
- Scope recap 正确引用 accepted plan 和 controller judgment（lines 5-9）。
- 显式声明禁止行为："does not use direct production PDF reads, cache inspection, source-helper/downloader calls, or ad hoc annual-report parsing."（line 11）
- 全部 command results 均为 public CLI：extraction-snapshot、extraction-score、quality-gate、git diff --check（lines 15-20）。
- Field-level classification 的 "Allowed evidence source" 列仅引用 public snapshot notes、score.json 输出、accepted design/template rules（lines 38-44）。
- 无任何命令触及 PDF/cache/source-helper/direct-file-access 层。

**Risk**: 无。

---

### F2 — INFO: Command results 和 scratch/tracked boundaries 充分

**Evidence**:
- 4 条 command results 全部附带 exit code、result status 和 scratch evidence paths（lines 15-20）。
- Scratch paths 与 plan 规定一致：`/tmp/fund-agent-baseline-coverage-triage-20260527/` 和 `reports/extraction-snapshots/baseline-coverage-triage-006597-2024/`（lines 60-61）。
- Tracked artifact 仅一个文件（line 56），与 plan 的 "Write one tracked evidence artifact under docs/reviews/" 一致。
- 大型 CLI outputs 保留在 scratch，tracked artifact 仅含 summaries、classifications 和 evidence paths（line 63）。
- Public CLI observations 准确提取了 snapshot/score/quality-gate 关键数据（lines 24-31），数值可从 scratch paths 交叉验证。

**Risk**: 无。

---

### F3 — INFO: 六项 field classifications 均由 allowed evidence 充分支撑

逐一检查：

**turnover_rate → `needs_more_evidence`**
- 支撑证据：public snapshot note（extraction mode `missing`，§8 未披露）+ score.json P1 failed + accepted design 将 turnover 映射到 manager consistency。
- 关键判断："allowed public evidence shows the current extractor did not produce a value... It does not prove whether the annual report contains a bond-applicable turnover fact... Under the no-direct-PDF rule, do not infer from absence alone."
- 正确性：对齐 plan 规则 "If the allowed evidence cannot prove whether an annual-report fact exists, classify the field as `needs-more-evidence` rather than inferring presence or absence." ✓

**holder_structure → `needs_more_evidence`**
- 支撑证据：public snapshot note（§9 未披露）+ accepted design 将 holder structure 映射到 chapters 3/6（非 equity-only）。
- 关键判断："the public CLI output cannot distinguish actual disclosure absence from extractor limitation."
- 正确性：Holder structure 在 accepted design 中不限于 equity，且 CLI output 无法区分"报告未披露"和"extractor 未提取"，`needs_more_evidence` 是唯一安全分类。 ✓

**holdings_snapshot → `bond_lens_contract_gap`**
- 支撑证据：public snapshot note（"no rule-extractable stock holding details or industry distribution table"）+ accepted design §6.4 描述 holdings_share_change 为"前十大重仓、行业分布"（equity-oriented）+ accepted template bond lens 强调 duration/credit/leverage/drawdown。
- 关键判断："The field name and current scoring expectation are equity-holdings shaped, while the fund is `bond_fund`. The observed block exposes that the bond lens needs a bond-specific holdings/risk evidence contract."
- 正确性：这是六项分类中最强的一个。snapshot note 自身已说明在寻找 stock holding details，而 bond fund 需要 bond-specific 风险证据。这不是 missing value，是 lens 不匹配。 ✓

**share_change → `extractor_gap`**
- 支撑证据：public snapshot note（"§10 contains multiple share columns and current rules cannot reliably choose the corresponding share class"）+ accepted template Chapter 4 要求 share-change trend。
- 关键判断："the public CLI note identifies a concrete current-rule limitation: share-class selection ambiguity."
- 正确性：唯一一个 public CLI output 提供了具体 root cause 的字段。Extractor 自身报告了 share-class 选择歧义，且 accepted design 确认 share-change 对 bond fund 有意义。`extractor_gap` 分类有 same-source 支撑。 ✓

**investor_return → `score_contract_gap`**
- 支撑证据：public snapshot note（"§3 does not directly disclose investor return and fallback is pending a later slice"）+ score.json P2（非 P1 block）+ accepted design 定义 fallback by share change × NAV estimate。
- 关键判断："Investor return is not equity-only and must not be marked inapplicable for bond_fund... a known score/extractor contract gap around direct disclosure vs fallback/projection."
- 正确性：正确遵守 plan 禁止将 investor_return 分类为 `field_applicability_policy` 的约束。`score_contract_gap` 符合 plan bond triage checklist 的 allowed classifications。P2 非立即 blocker 的判断正确。 ✓

**nav_data anchor → `score_contract_gap`**
- 支撑证据：public snapshot（value present, source `nav_cache`, 1802 records, but anchor absent）+ accepted design 将 NAV 定位为 external adapter/cache source。
- 关键判断："The evidence anchor is not an annual-report anchor. This is a score/report evidence contract issue for external NAV provenance."
- 正确性：NAV 来自外部 cache，非年报解析。缺失 anchor 是 evidence provenance 问题，不是 extractor 问题。与 `docs/design.md` §5.4.2 的 `nav_data` exclusion 对齐。 ✓

所有六项分类均为 allowed evidence 直接支撑，无推断或外部假设。 ✓

---

### F4 — INFO: Track 1B closure 合规

**Evidence**:
- Status: `not_run_no_approved_candidates`（line 48），与 plan Track 1B closure state 一致。
- "The controller did not supply replacement candidates for index/QDII/FOF probing."（line 49）
- "Per the accepted plan and judgment, this worker did not browse, search, or select ad hoc replacement candidates."（line 50）
- "This track is independently closeable and has no command output."（line 50）
- Plan 授权的 Track 1B closure 语义："If no controller-approved candidate list exists, close this track as `not_run_no_approved_candidates` and keep source/taxonomy blockers open without blocking Track 1A."

Closure 完全合规：状态正确、禁止行为未违反、Track 1A 不受影响、source/taxonomy blockers 保持 open。 ✓

**Risk**: 无。

---

### F5 — INFO: Next recommendation 保守且充分 justified

**Evidence**:
- Recommendation: "more evidence before authorizing implementation"（line 67）。
- 理由分层清晰（lines 69-75）：
  - share_change 有最强 public evidence → candidate for focused implementation
  - holdings_snapshot 是 bond-lens contract gap → 需 design before code
  - turnover_rate / holder_structure 是 needs_more_evidence → 保持 evidence-only
  - investor_return / nav_data 是 score-contract issue → 非 P1 blocker，defer
- Conditional split（lines 77-81）：如果 controller 选择继续，split 为三个独立 slice 而非 big-bang fix。
- Golden corpus v1 仍 blocked（line 83）：coverage 不足 + 006597 quality-gate block 未解决。

推荐策略正确：不阻塞 controller 授权 narrow share_change slice，但指出其他字段需要更多 evidence 或 design gate。 ✓

**Risk**: 无。

---

### F6 — INFO: 无 finding 需要artifact correction、rerun 或 block closeout

**Evidence**:
- `git diff --check` passed（line 93）。
- 无 forbidden access 发生。
- 无 classification 依赖推断或外部假设。
- 无 scratch output 被 promoted 为 tracked artifact。
- Blocker status 准确区分 execution blocker（none）和 implementation blocker（by design, mixed root causes）。

**Risk**: 无。

---

## Verdict

**PASS**

Evidence run 严格遵守 authorized scope，六项 field classifications 均由 allowed evidence 直接支撑，Track 1B closure 合规，next recommendation 保守且分层合理，无 finding 需要修正、rerun 或阻断 closeout。

| Finding | Severity | Blocks closeout? |
|---------|----------|-------------------|
| F1: Scope adherence clean | INFO | No |
| F2: Command/boundary sufficient | INFO | No |
| F3: Six classifications well-supported | INFO | No |
| F4: Track 1B closure compliant | INFO | No |
| F5: Recommendation conservative and justified | INFO | No |
| F6: No correction/rerun needed | INFO | No |

---

## Truth Source Alignment Confirmation

- [x] Evidence run 不违反 `AGENTS.md` 硬约束：无 FundDocumentRepository 直访、无 fallback policy 修改、root cause 同源（public CLI output + accepted design）。
- [x] Evidence run 不违反 `docs/design.md` 非目标：未改 renderer/FQ0-FQ6/Host-Agent/dayu/extractor。
- [x] Evidence run 与 accepted plan scope 完全一致：仅 public CLI commands、禁止 direct PDF/cache/source-helper。
- [x] Evidence run 不引入 source/test/product-flow 变更。
