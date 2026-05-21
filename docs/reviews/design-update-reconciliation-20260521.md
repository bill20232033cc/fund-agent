# Design Update Reconciliation（2026-05-21）

## Reviewed Inputs

- Current design truth: `docs/design.md`
- Candidate update: `docs/design-update.md`
- Related audit: `docs/fund-agent-audit-20260521---b5101bb0-fa2d-4904-8c83-0bbf25c82334.md`

## Controller Judgment

`docs/design-update.md` cannot replace `docs/design.md` wholesale. It mixes useful current-code facts with implementation-guide detail, line-count noise, future-looking pseudo rules, and several stale decisions. The design truth should stay concise and durable: design goals, architecture boundaries, stable contracts, accepted mechanisms, and explicit non-goals.

## Accepted For Fusion

| Topic | Decision | Reason |
|---|---|---|
| Deterministic MVP pipeline | accepted | Current main path is Python deterministic extraction, analysis, rendering, audit, and quality gate. LLM/Dayu runtime remains a v2 candidate. |
| UI / Service / Capability current architecture | accepted | This matches current code and prevents stale Host/Engine claims from being treated as implemented. |
| Service and contract additions | partially accepted | Stable contracts such as `FundAnalysisResult`, `ValuationState`, `MoneyHorizon`, `ProgrammaticAuditInput`, and `ProgrammaticAuditResult` belong in the design truth. File counts and line counts do not. |
| CHAPTER_CONTRACT / ITEM_RULE / preferred_lens mechanism details | partially accepted | Stable mechanisms and current deterministic scope should be preserved. Internal line counts and exhaustive code-guide detail should stay in package README. |
| C2 deterministic audit subset | accepted | It clarifies what programmatic audit can prove today versus what remains v2 semantic/evidence work. |
| Document repository and source metadata | accepted | Unified `FundDocumentRepository`, PDF/parsed cache, source metadata, and P8-S3 fallback taxonomy are stable design facts. |
| Quality gate FQ0-FQ6 summary | accepted | A concise rule table belongs in design truth; detailed implementation remains in `fund_agent/fund/README.md` and tests. |
| Golden Answer pipeline | accepted | It is part of the current quality loop and should be recorded at mechanism level. |
| Dayu-agent dependency status | accepted with correction | The design truth should say the current main path does not use Dayu Host/Engine/tool loop; Dayu remains dependency/candidate, not implemented runtime. |

## Rejected Or Deferred

| Topic | Decision | Reason |
|---|---|---|
| Full project tree | rejected | This belongs in developer README and quickly goes stale in a design truth document. |
| File line counts | rejected | Line counts are not design facts. |
| EID “巨潮” wording | rejected | Current accepted wording is EID/CSRC unified disclosure platform as primary, Eastmoney/akshare fallback. |
| Detailed fund subtype pseudo rules | rejected | Current `FundType` has six stable types; style/subtype inference is not accepted as implemented design. |
| Peer-median fallback pseudo code | rejected | It risks documenting unimplemented or evidence-weak estimation as design truth. Missing data should remain explicit unless current code proves a traceable derived path. |
| Critical-section report suppression pseudo policy | deferred | It may be useful product design, but it is not current behavior and needs a separate design slice. |
| Dayu toolset registrar / scene prompt decisions | rejected | Current main path does not use Dayu Engine/Host/Prompting. |
| SQLite cache decision | rejected | Current document repository design truth is PDF cache plus parsed-report materialization and source metadata, not a SQLite-first design. |

## Applied Update Scope

`docs/design.md` should be updated only to:

- state the current deterministic UI -> Service -> Capability main path;
- preserve Dayu as v2 candidate instead of implemented Host/Engine;
- add stable Service/Capability contract rows;
- keep P8-S3 source fallback taxonomy;
- summarize quality gate and golden answer mechanisms;
- remove or replace stale/future-looking sections that claim unimplemented fund-type subtype inference, pseudo estimation rules, full project tree, and Dayu/SQLite implementation decisions.

## Residual Follow-Ups

- Product contract discussion remains open: decide the minimal user-facing `analyze` inputs versus dev/override parameters.
- A separate design slice should decide whether missing critical data should suppress final judgment, warn, or block via quality gate.
- A separate infra slice should decide whether Dayu dependency remains required, optional, mirrored, or removed.
