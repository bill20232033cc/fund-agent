# MVP Real LLM Smoke Re-baseline Gate Plan — DS Review

**Reviewer**: AgentDS
**Review target**: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-20260604.md`
**Review date**: 2026-06-04
**Review lens**: verifier matrix, preflight/no-secret protocol, direct evidence requirements, blocker/residual classification, stop conditions, boundary guardrails, historical evidence substitution prevention

## Findings

### Finding 1 — NON-BLOCKING RESIDUAL: Preflight variable name recording boundary is conservative but unambiguous

**Reference**: Plan §5.1 lines 67-71

The preflight protocol lists `FUND_AGENT_LLM_PROVIDER` and `FUND_AGENT_LLM_MODEL` as "required env presence" checks, and states "只输出布尔 presence 和变量名，不得输出 API key 值、base URL 值、Authorization header、完整 config dump 或 shell environment"。The protocol correctly treats provider/model names as presence-only at plan level. In practice, provider and model names are non-secret configuration that may be useful for diagnostics. The conservative stance here is safe but may force the evidence step to omit diagnostically useful non-secret information. This is a residual, not a blocker — the evidence owner can confirm this is intentional and optionally relax it via controller judgment without changing the plan's safety guarantees. The redaction rules for API key, base URL, and Authorization are correctly absolute.

**Classification**: Non-blocking residual. Does not require plan fix.

---

### Finding 2 — NON-BLOCKING RESIDUAL: Captured temp file lifecycle after secret detection is implicit

**Reference**: Plan §5.2 line 88

The plan allows evidence owner to capture stdout/stderr to local temp files with shell redirection, then states "若捕获文件中含 secret/raw provider/prompt，必须作为 blocker 处理并不得提交"。The blocker classification is correct, but the plan does not explicitly instruct deletion of the temp file after secret detection. The temp file on disk containing secrets is a local risk even if never committed. The evidence step can handle this by adding an explicit "delete temp capture files after scan confirms secrets" step; this is within evidence-owner judgment and does not require a plan amendment.

**Classification**: Non-blocking residual. Addressable in evidence step without plan change.

---

### Finding 3 — NON-BLOCKING RESIDUAL: Local non-live validation commands are listed but gating semantics are deferred to controller

**Reference**: Plan §6 line 152

The plan lists 6 local non-live pytest validation commands and states that if any fail, the evidence owner must classify as "harness blocker 或 unrelated test failure" and "不得绕过失败直接运行 live smoke，除非 controller 明确裁决该失败与 smoke evidence safety 无关"。This correctly prevents running live smoke over a broken test harness. However, the "unless controller explicitly rules" escape hatch could be tightened — a test failure in `test_llm_run_artifacts.py` or `test_llm_provider.py` is more directly relevant to smoke evidence safety than a failure in `test_cli.py`. The plan currently treats all 6 commands with uniform gating semantics. The controller judgment at evidence time can apply differential weighting; this is not a plan defect.

**Classification**: Non-blocking residual. Controller can apply differential weighting at evidence time.

---

## Verifier Matrix Coverage Audit

以下逐条审计 A1-A9 的完整性：

| AC | Evidence specified | Command/artifact | Blocker vs residual | Next entry point | 判定 |
|----|-------------------|-----------------|---------------------|------------------|------|
| A1 | Plan artifact + DS/MiMo reviews + controller judgment | Explicit | Provider/default/runtime/live execution smuggled = blocker | Evidence execution; no calibration | PASS |
| A2 | Preflight command, exit code, presence booleans, redaction statement | Explicit | env/config absent = environment_blocked or blocker; no fake smoke | Exactly one reviewed smoke command | PASS |
| A3 | Full command, exit code, stdout/stderr summary, artifact path | Explicit | Multi-command, param drift, timeout/default override = blocker | stdout/artifact/fail-closed verification | PASS |
| A4 | Smoke command output + retained artifact manifest/summary/chapter | Explicit | stdout half-report, exit 0 on incomplete, fallback, missing artifact = blocker; artifact write warning = residual | diagnostics/redaction verification | PASS |
| A5 | Smoke stdout/stderr + optional retained evidence summary | Explicit | Missing chapters, Ch2 public split, quality gate bypass, incomplete stdout = blocker | Evidence review; no promotion/golden/readiness | PASS |
| A6 | Evidence artifact + secret/redaction scan summaries | Explicit | Secret/raw provider/prompt leakage = blocker; diagnostic wording = residual | Review | PASS |
| A7 | git branch/status/diff, command list, pre/post file changes, artifact path | Explicit | Source/test/config/runtime diff, unreviewed promotion, old log substitution = blocker | Controller judgment | PASS |
| A8 | Smoke result + retained artifact + failure category matrix | Explicit | Modifying timeout/default for pass, misreporting timeout as accepted, fake smoke = blocker | Residual classification/calibration planning; not runtime change | PASS |
| A9 | Forbidden-scope checklist + git diff integrity | Explicit | Any boundary bypass = blocker | Independent review of evidence execution | PASS |

所有 9 条 acceptance criteria 均有明确的 direct evidence 要求、验证命令/artifact、blocker/residual 分类和 next entry point。无缺口。

## Stop Conditions Audit

Plan §10 中的 hard stop / blocker 清单完整覆盖：
- Plan/evidence 阶段修改 source/test/config/runtime behavior、provider default/runtime/budget ✓
- Plan 阶段运行 live provider / real LLM smoke / secret check ✓
- env/config absent 但伪造 smoke 或使用历史 retained run ✓
- 多于一条 reviewed smoke command 或加入 unreviewed overrides ✓
- incomplete/blocked/timeout 时 stdout 非空、exit 0、半成品报告、deterministic fallback ✓
- retained artifact 泄漏 secret ✓
- 通过修改 default/runtime/budget 追求 pass ✓
- public chapter ids 偏离 `0-7` 或 Ch2 公开化 ✓
- dayu 直接依赖、绕过 FundDocumentRepository、直接读 PDF/cache、extra_payload ✓
- 使用旧日志/旧 review/旧 retained artifact 作为当前证据 ✓
- golden/readiness、snapshot refresh、fixture promotion、score-loop、Agent runtime、multi-year runtime、PR/push/release ✓

Residual owners 分类完整：environment_blocked、provider_runtime_residual、content_contract_residual、code_contract_blocker、secret_redaction_blocker、Agent runtime/multi-year/score-loop、golden/readiness/release/PR。每个 residual owner 均绑定明确的 disposition gate，不在本 gate 消化。

## Boundary And Forbidden-Scope Audit

逐一核实：

1. **Provider default/runtime/budget change**: §3 non-goals 与 §10 stop conditions 均明确禁止。§5.2 smoke command 不加任何 override。✓
2. **Agent runtime / tool-loop / ToolRegistry / ToolTrace**: §3 列为 non-goal，§10 列为 hard stop。✓
3. **Multi-year runtime / score-loop / golden/readiness**: §3 列为 non-goal，§10 列为 hard stop。✓
4. **Snapshot refresh / fixture promotion / strict correctness rerun**: §3 列为 non-goal，§10 列为 hard stop。✓
5. **PR / push / release / external state**: §3 列为 non-goal，§10 列为 hard stop。✓
6. **Dayu runtime 直接依赖**: §3 non-goals 明确禁止，与 AGENTS.md 和 design.md 一致。✓
7. **FundDocumentRepository 绕过**: §3 明确禁止直接读 PDF/cache/source helper。✓
8. **extra_payload**: §3 明确禁止。✓
9. **旧日志/旧 retained run 替代**: §2 声明历史记录只能作为背景，§3 和 §10 明确禁止替代。✓
10. **Ch2 public split**: §2 明确 Ch2 只能是第 2 章内部 typed subcontracts，§10 列为 hard stop。✓

## Preflight Secret-Safety Audit

Plan §5.1 协议逐项核实：
- Required env presence：只输出布尔 presence ✓
- Key env var name：只输出变量名，不输出 value ✓
- Key env var value present：只输出 `api_key_present=true/false` ✓
- Optional runtime env：只输出是否 explicitly set ✓
- 不校验 endpoint 可达性、不做 HTTP request、不调用 provider、不打印 base URL ✓
- env/config absent → environment_blocked 或 blocker，不伪造 smoke ✓

无 secret 泄漏风险。

## Smoke Command Scoping Audit

Plan §5.2 唯一命令 `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`：
- 无 timeout/attempt/backoff/model/endpoint/provider/max-output/repair-budget/prompt/debug override ✓
- 不运行第二个基金、第二个年份、第二个 provider probe、PASS-only timing probe、chapter-only live command ✓
- 不运行 deterministic fallback command ✓
- 捕获文件中的 secret 作为 blocker ✓

命令 scoping 正确。

## Verdict

**PASS** — no blocking findings.

3 个 non-blocking residuals 已记录（Finding 1-3），均可在 evidence step 中解决，不需要 plan fix：
- Finding 1: Preflight variable name recording boundary（保守但安全的 presence-only 语义）
- Finding 2: Captured temp file lifecycle after secret detection（evidence step 可补充删除指令）
- Finding 3: Local non-live validation gating semantics deferred to controller（controller 可做差异权重裁决）

Plan 的 verifier matrix A1-A9 完整、stop conditions 充分、preflight secret-safe、smoke command singular/scoped、fail-closed/no-fallback/stdout-empty 语义保持、边界 guardrails 无缺口、forbidden scope 无夹带。下一入口 `Real LLM smoke re-baseline evidence execution` 在 plan accepted 后可以进入。
