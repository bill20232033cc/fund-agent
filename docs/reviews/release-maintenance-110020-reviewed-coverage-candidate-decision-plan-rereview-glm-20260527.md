# Targeted Re-Review: 110020 Reviewed Coverage Candidate Decision Plan

> **Reviewer**: AgentGLM (independent plan reviewer, not controller)
> **Date**: 2026-05-27
> **Target**: `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-20260527.md` (patched version)
> **Scope**: Targeted re-review only — verify closure of GLM initial findings and MiMo M1-M3/L1-L2; no new scope expansion
> **Verdict**: **PASS**

---

## GLM Initial Findings Closure

### GLM Finding 1 (Non-blocking): Index-specific evidence 评估缺少独立验证 step

**原问题**：Acceptance Matrix 没有独立 step 要求显式判定 `index_profile`、`tracking_error`、benchmark-methodology 的证据充分性分类。

**闭合状态**：已闭合。

Plan 新增以下内容：

1. **"Index-Lens Evidence Sufficiency Definition" 独立段落**（line 76-86）：为 `index_profile`、`tracking_error`、benchmark methodology/constituents/tracking 三项分别定义了 Required assessment、Sufficient means、Insufficient means、Out of scope means，并要求每项给出 `sufficient`/`insufficient`/`out_of_scope` 分类、理由和 source pointer。

2. **Acceptance Matrix 新增 "Index evidence assessment" step**（line 185）：独立 step，要求每项有分类和理由，并明确 `tracking_error` reviewed evidence 是成熟 index candidate 的具体前提。

3. **Stop condition**（line 185）：明确禁止将三项合并为泛化 "index evidence ok" 语句，禁止将缺失 tracking evidence 标记为 sufficient。

4. **Evidence artifact step**（line 186）：要求 artifact 包含 "index evidence assessment"。

5. **Independent reviews step**（line 187）：要求 reviewers 确认 "complete index evidence assessment"。

**判定**：远超原始 finding 要求。不仅增加了独立 step，还定义了完整的评估框架和防止合并的 stop condition。

### GLM Finding 2 (Non-blocking): `--source-csv` 路径版本一致性应显式声明

**原问题**：`--source-csv docs/code_20260519.csv` 的版本一致性未被显式记录。

**闭合状态**：已闭合。

Plan 新增以下内容：

1. **Public snapshot step Acceptance condition**（line 182）：要求 "artifact records `docs/code_20260519.csv` path plus git identity/version note"，并附具体 observed state：repo HEAD、CSV last commit、`git status` clean、mtime、size。

2. **Evidence artifact step Acceptance condition**（line 186）：要求 artifact 包含 "CSV identity/version note"。

3. **Public snapshot step Stop condition**（line 182）：增加 "or CSV identity cannot be recorded"。

**判定**：完全闭合。不仅声明了版本一致性要求，还附了当前 CSV 的具体 git identity 作为 baseline reference。

---

## MiMo M1-M3 / L1-L2 Closure

### M1 (medium): 缺少 index-lens evidence sufficiency 定义

**闭合状态**：已闭合。

与 GLM Finding 1 同源。Plan 新增的 "Index-Lens Evidence Sufficiency Definition" 段落直接回应了 MiMo 要求的 acceptance criteria。`tracking_error` reviewed evidence 被明确定义为 concrete prerequisite（line 83-84："`tracking_error` reviewed evidence is a concrete prerequisite for treating `110020` as a mature index fund coverage candidate"）。这与 `docs/design.md` §10 的 `tracking_error` 生产 golden row 前提一致。

### M2 (medium): strict golden not configured 缺少 concrete resolution path

**闭合状态**：已闭合。

Plan 的 "Strict golden not configured" risk row（line 71）已更新为："Carried-forward residual. Correctness cannot be reviewed until same-year strict golden coverage is established; the score must not be treated as strict correctness proof."。Disposition 明确为 carried-forward residual，不是模糊的风险观察。

### M3 (medium): Stop conditions 过窄

**闭合状态**：已闭合。

三项缺失的 stop condition 均已补充：

1. **New unresolved warnings**（line 113）："Stop and report if fresh public evidence introduces new P0/P1 warnings or blocks beyond the known `turnover_rate` P1 warn, `FQ2F` P1 field failure warn, and `FQ0` strict-golden-not-configured info."
2. **Source strategy regression**（line 114）："Stop if `source_strategy`, `resolved_source_name`, `fallback_used`, `primary_failure_category`, `fallback_eligibility`, `source_provenance_status`, or `source_provenance_reason` changes from the accepted tuple unless the controller explicitly accepts the changed evidence state."
3. **Review BLOCK**（line 187）："Stop if any reviewer returns `BLOCK` until fixed and re-reviewed."

### L1 (low): fund_type 缺失

**闭合状态**：已闭合。

Plan 的 Accepted Evidence Summary table（line 43-45）新增 `fund_type_slot: index_fund`、`source_strategy: primary_then_fallback`、`resolved_source_name: eastmoney`。Candidate A entry conditions（line 97）新增 "Accepted fund-type slot remains `index_fund`"。

### L2 (low): Independent review stop condition 不明确

**闭合状态**：已闭合。

"Independent reviews" step 的 Stop condition（line 187）现在显式声明："Stop if any reviewer returns `BLOCK` until fixed and re-reviewed"。

---

## New Issues Check

检查 patch 是否引入新的 scope creep 或 boundary violation：

| 新增内容 | 是否引入新问题 | 判断 |
|----------|---------------|------|
| Index-Lens Evidence Sufficiency Definition | 否 | 纯证据审查框架，不涉及 promotion 或 code change |
| CSV identity/version note | 否 | 记录性要求，不改变数据源或命令 |
| New stop conditions (new warnings / source regression / BLOCK) | 否 | 均为更保守的防护，不放松任何约束 |
| `fund_type_slot` / `source_strategy` / `resolved_source_name` 字段 | 否 | 与 provenance rerun 已接受证据一致，增加明确性 |
| Index evidence assessment 独立 step | 否 | bounded evidence review only，所有 terminal states 仍为 `not_promoted` |

未发现新问题。

---

## Verdict

**PASS**

GLM 两项 non-blocking findings 和 MiMo 五项 findings (M1-M3/L1-L2) 全部闭合。Plan patch 未引入新的 scope creep 或 boundary violation。Plan 可以进入 controller judgment。
