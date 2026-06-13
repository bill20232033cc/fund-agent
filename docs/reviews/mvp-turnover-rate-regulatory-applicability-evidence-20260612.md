# Turnover Rate Regulatory Applicability Evidence Gate

Date: 2026-06-12

Gate: `Turnover rate regulatory applicability evidence gate`

Classification: `standard`

Status: evidence artifact

## Verdict

Primary disposition: `REGULATORY_APPLICABILITY_SCORING_GAP_CONFIRMED`.

The accepted `turnover_rate` warning for `004393 / 2025` should not be treated
as an extractor miss by default. Official regulatory and AMAC template evidence
shows the explicit stock turnover-rate disclosure item is part of the new
disclosure/template regime effective from `2026-05-01`, and the template marks
the item as annual-report-only.

For the current `004393 / 2025` evidence chain, the more precise root cause is:

`turnover_rate` scoring/applicability is too broad for pre-effective-date annual
reports and for non-annual reports.

## Inputs

- User business assertion: 2025 annual reports, earlier annual reports and
  quarterly reports do not disclose turnover-rate data.
- Accepted quality issue identity:
  `docs/reviews/mvp-quality-warning-issue-identity-evidence-20260612.md`
- Accepted turnover root-cause evidence:
  `docs/reviews/mvp-turnover-rate-root-cause-evidence-controller-judgment-20260612.md`
- CSRC public rule page:
  `https://www.csrc.gov.cn/csrc/c101954/c7619929/content.shtml`
- AMAC XBRL template publication page:
  `https://www.amac.org.cn/xwfb/xhyw/202603/t20260313_27409.html`
- AMAC annual/semiannual XBRL template PDF:
  `https://www.amac.org.cn/xwfb/xhyw/202603/P020260326556375986137.pdf`
- AMAC quarterly XBRL template PDF:
  `https://www.amac.org.cn/xwfb/xhyw/202603/P020260508338766981977.pdf`

## Scope

This gate does not modify source, tests, runtime behavior, source acquisition
policy, fallback policy, provider/LLM behavior, release/readiness state or PR
state.

No live EID, fund annual-report PDF acquisition, FDR, analyze, checklist,
provider, LLM, golden, readiness, release, push, PR, merge, cleanup, delete,
archive, ignore or stage command was run.

Official regulatory HTML/PDF files were captured only as regulatory evidence for
this gate. They are not fund source documents and are not source-acquisition
policy evidence.

## Captured Official Materials

Temporary capture directory:

- `/tmp/fund-agent-regulatory-turnover/`

Captured material hashes:

| Local capture | Source URL | Size | SHA-256 |
| --- | --- | ---: | --- |
| `csrc-periodic-report-rule.html` | `https://www.csrc.gov.cn/csrc/c101954/c7619929/content.shtml` | `14619` | `9a1e0112fd2e5896898227e27ee19072eca2ba2c5c8bd56bd2d8360c7f73234e` |
| `amac-xbrl-publication.html` | `https://www.amac.org.cn/xwfb/xhyw/202603/t20260313_27409.html` | `334847` | `d6a5e44ca86760bd3c02f27a53062e451f02d16862cd87e6b3731e73e05e41ea` |
| `amac-annual-semiannual-xbrl-template.pdf` | `https://www.amac.org.cn/xwfb/xhyw/202603/P020260326556375986137.pdf` | `913596` | `4d2fba55180770865bdf061aa6b2bdd5816db4abb98a46399b5ec16098859839` |
| `amac-quarterly-xbrl-template.pdf` | `https://www.amac.org.cn/xwfb/xhyw/202603/P020260508338766981977.pdf` | `623000` | `9255466941640ee751384f4e0ba053497cc5291c7d5f8baa1c2c250d69844345` |

Capture command:

```bash
mkdir -p /tmp/fund-agent-regulatory-turnover
curl -L 'https://www.csrc.gov.cn/csrc/c101954/c7619929/content.shtml' -o /tmp/fund-agent-regulatory-turnover/csrc-periodic-report-rule.html
curl -L 'https://www.amac.org.cn/xwfb/xhyw/202603/t20260313_27409.html' -o /tmp/fund-agent-regulatory-turnover/amac-xbrl-publication.html
curl -L 'https://www.amac.org.cn/xwfb/xhyw/202603/P020260326556375986137.pdf' -o /tmp/fund-agent-regulatory-turnover/amac-annual-semiannual-xbrl-template.pdf
curl -L 'https://www.amac.org.cn/xwfb/xhyw/202603/P020260508338766981977.pdf' -o /tmp/fund-agent-regulatory-turnover/amac-quarterly-xbrl-template.pdf
shasum -a 256 /tmp/fund-agent-regulatory-turnover/*
```

## Evidence

### E1. Effective Date

The CSRC rule page for the revised public fund periodic-report content and
format guideline states that the revised guideline is effective from
`2026-05-01`.

The AMAC publication page for related XBRL templates also states that the
templates are effective from `2026-05-01`.

Directly reviewable captured-text evidence:

| Source | Captured line evidence | Meaning |
| --- | --- | --- |
| CSRC HTML raw lines 189 and 207 | `证监会公告〔2026〕5号`; guideline title; `自2026年5月1日起施行` split by source HTML spans | CSRC rule effective date is `2026-05-01` |
| AMAC HTML raw lines 4570-4577 | XBRL publication title; quarterly and annual/interim template names; `自2026年5月1日起施行` | AMAC XBRL templates effective date is `2026-05-01` |

Disposition:

- report-year `2025` annual reports were produced under the old disclosure
  regime for the accepted sample path;
- the new turnover-rate template item cannot be used as a mandatory disclosure
  expectation for `004393 / 2025`.

### E2. Turnover-rate Item Is Annual-report-only

The AMAC annual/semiannual XBRL template includes section `8.4.4 股票换手率`,
with explanatory text:

- stock turnover-rate is disclosed by active stock funds and mixed funds;
- the item applies only to annual reports;
- it does not apply to interim reports.

Directly reviewable template evidence from the annual/semiannual PDF text:

| PDF location | Evidence | Meaning |
| --- | --- | --- |
| local extracted PDF text around section `8.4.4`, lines `3695-3703` | section `8.4.4 股票换手率`; row `股票换手率` | The template has an explicit turnover-rate item |
| local extracted PDF text around section `8.4.4`, line `3698` | item `248` says it applies only to annual reports and not interim reports | Annual-only; interim reports are not applicable |
| local extracted PDF text around section `8.4.4`, lines `3734-3735` | formula continuation and statement that the table applies to actively managed stock and mixed funds | Fund-type applicability is active stock/mixed funds |

Disposition:

- quarterly reports are outside the turnover-rate disclosure item;
- interim reports are also outside the turnover-rate disclosure item;
- `turnover_rate` quality scoring must be period-aware, not only fund-type-aware.

### E3. Quarterly Template Search

The AMAC quarterly-report XBRL template did not expose a `股票换手率` item in the
queried text.

Local search evidence:

```bash
strings /tmp/fund-agent-regulatory-turnover/amac-quarterly-xbrl-template.pdf | rg -n "股票换手率|换手率"
```

Observed result: exit code `1` with no output.

Disposition:

- the current gate has no evidence that quarterly reports should be scored for
  `turnover_rate`;
- quarterly reports should not be treated as missing `turnover_rate` P1 evidence
  under the new template item.

## Repo Impact

Accepted local evidence already proved:

- snapshot row:
  - `field_group=manager`
  - `field_name=turnover_rate`
  - `extraction_mode=missing`
  - `value_present=false`
  - `anchor_present=false`
- score row:
  - `priority=P1`
  - `coverage_rate=0.0`
  - `traceability_rate=0.0`
  - `status=fail`
- quality gate:
  - `FQ2/warn turnover_rate`
  - derivative `FQ2F/warn 004393`

Regulatory applicability evidence changes the root-cause classification:

| Previous candidate | Current disposition |
| --- | --- |
| Source disclosure absent | `NOT_PRIMARY_ROOT_CAUSE` for 2025 and earlier annual reports, because absence is expected under the pre-effective-date regime unless voluntarily disclosed |
| Extractor missed disclosed value | `NOT_SUPPORTED` without same-source source body, and no longer the default next branch for 2025/earlier reports |
| Mapping/anchor loss | `NOT_SUPPORTED_IN_ACCEPTED_SNAPSHOT_TO_SCORE_CHAIN` |
| Score interpretation issue | `REOPEN_AS_APPLICABILITY_SCORING_GAP` |

## Applicability Rule Direction

The next code gate should define an explicit applicability rule before scoring
`turnover_rate`.

Minimum rule direction:

- `turnover_rate` applies only to annual reports;
- `turnover_rate` does not apply to quarterly reports;
- `turnover_rate` does not apply to interim reports;
- `turnover_rate` should not be required for report years before the new
  effective regime, including `2025` and earlier annual reports;
- active stock and mixed funds may become applicable for annual reports under
  the new regime, subject to exact report-year/report-date semantics.

Open design detail for the implementation planning gate:

- choose whether the cutoff should use `report_year >= 2026`, actual report
  publication date, or explicit source/template version when available.

For the current accepted sample `004393 / 2025`, the report-year cutoff clearly
classifies it as pre-effective. Actual publication-date or source-template
version semantics remain implementation-planning decisions and should be handled
explicitly in the narrow fix plan.

## Finding Disposition

| Finding | Disposition | Basis |
| --- | --- | --- |
| `FQ2/warn turnover_rate` for `004393 / 2025` | `ACCEPT_AS_CURRENT_WARNING_IDENTITY_BUT_RECLASSIFY_ROOT_CAUSE` | The warning exists in accepted evidence, but the root cause is applicability/scoring scope, not extractor failure. |
| `FQ2F/warn 004393` | `DERIVATIVE_OF_TURNOVER_RATE` | Fund-level warning derives from `turnover_rate` P1 fail. |
| `FQ0/info year_not_covered` | `DEFER` | Strict golden coverage issue remains separate. |
| Source disclosure absence vs extractor miss | `DEFER_FOR_NON_2025_OR_POST_EFFECTIVE_SAMPLES` | Same-source disclosure evidence may still be needed for future applicable reports. |

## Next Entry Recommendation

Recommended next entry:

`Turnover rate regulatory applicability narrow fix planning gate`

Objective:

- plan the smallest code change that prevents pre-effective-date annual reports
  and non-annual reports from being scored as missing P1 `turnover_rate`;
- preserve the accepted `FQ2/FQ2F` warning semantics for fields that are truly
  applicable and still fail coverage/traceability;
- keep source acquisition policy unchanged.

Implementation must not start from this evidence artifact alone unless the
controller explicitly opens the narrow fix planning/implementation gate.
