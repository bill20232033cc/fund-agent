# DS Access-Preflight Review — 004393 / 2025 Controlled Source-body Verification Gate

Date: 2026-06-13
Reviewer: DS (access-preflight role)
Reviewed target: `docs/reviews/mvp-004393-2025-controlled-source-body-verification-access-preflight-20260613.md`
Verdict: **PASS_WITH_FINDINGS**

## 1. Reviewed Target and Scope

Target is the access preflight artifact that determines whether the `004393 / 2025
Controlled Source-body Verification Gate` may proceed to source-body verification
without live EID/network/PDF/FDR commands.

Scope of this review:
- Challenge whether preflight has enough evidence to block or whether a safe
  no-new-live repository/cache path already exists.
- Check if internal cache methods can be used without violating repository boundary.
- Check if recommended live authorization decision is correctly separated from this gate.
- Check residual owner and next-entry wording.

## 2. Assumptions Tested

| # | Preflight assumption | Tested against | Result |
|---|---|---|---|
| A1 | `load_annual_report()` unconditionally risks live fetch on cache miss. | `repository.py:350-399` | **Confirmed.** Parsed cache miss + PDF cache miss → `fetch_pdf()` call. |
| A2 | No public cache-only check method exists on `FundDocumentRepository`. | `repository.py:294-418` (full class surface) | **Confirmed.** Only public method is `load_annual_report()`. |
| A3 | Internal cache methods are not usable without violating repository boundary. | `AGENTS.md` boundary rules; `cache.py` method signatures | **Partially confirmed** — see Finding 1. |
| A4 | Cache status for `004393 / 2025` is unknown and cannot be determined without risk. | `cache.py:get_pdf_entry()` implementation | **Not confirmed** — see Finding 1. |

## 3. Findings

### F1-未修复-中-preflight 未利用 `get_pdf_entry()` 做零风险缓存可用性检查

- **位置**: Preflight §3 PF1–PF3, §4 Access Decision
- **问题类型**: 证据不足 / 过度封锁
- **当前写法**: Preflight 通过静态分析得出 `load_annual_report()` 可能触发 live fetch，结论为 `ACCESS_PREFLIGHT_BLOCKED_NEEDS_AUTHORIZATION_NOT_READY`。未尝试任何运行时缓存状态检查。
- **反例/失败场景**: 若前序 gate 已通过 `load_annual_report("004393", 2025)` 创建了 parsed cache 和 PDF cache 条目（例如 accepted live evidence run `004393 / 2021-2025`），则当前调用 `load_annual_report("004393", 2025)` 会走纯缓存路径：命中 parsed cache → 直接返回（`repository.py:351-364`），不触发任何 live/network/PDF 访问。Preflight 因未检查而可能错误封锁了一条实际安全的路径。
- **为什么有问题**: Preflight 的结论「Repository-bounded no-new-live access is not proven」在技术上等价于「未检查，故未证明」。但 `AnnualReportDocumentCache.get_pdf_entry()` 是纯 SQLite 读取操作（`cache.py:327-359`），不访问 PDF 文件、不发起网络请求、不反序列化 report body。调用它检查 `004393 / 2025` 是否存在缓存条目不会触发任何 live 行为，且返回的 `AnnualReportPdfCacheEntry` 只含 `pdf_path`、`source_metadata`、`updated_at` 三个元数据字段，不含 report body。
- **直接证据**:
  - `cache.py:295-309`：`get_pdf_entry()` 只执行 `SELECT pdf_path, source_metadata_json, updated_at FROM documents WHERE document_key = ?`，零网络/PDF/body 访问。
  - `cache.py:327-359`：`_get_pdf_entry_sync()` 仅检查 PDF 路径是否存在（`pdf_path.exists()`），不打开或读取 PDF 内容。
  - `repository.py:370-377`：若 `get_pdf_entry()` 返回有效 EID 条目，`load_annual_report()` 会直接走 `parse_pdf(pdf_path)` 而不调用 `fetch_pdf()`，即只做本地 PDF→text 解析，不做网络下载。
- **影响**: 可能导致不必要的 live authorization 请求，而实际缓存已满足需求；增加用户决策负担和 gate 延迟。
- **建议改法和验证点**:
  1. Preflight 补充一步：通过 `repository._cache.get_pdf_entry(DocumentKey("004393", 2025))` 检查 SQLite documents 表是否存在 `004393 / 2025` 条目且 `source_metadata` 满足 `_is_current_eid_single_source_metadata()`。
  2. 若条目存在：`load_annual_report("004393", 2025)` 可安全调用（走纯缓存路径）；preflight 结论应改为 `ACCESS_SAFE_VIA_CACHE`。
  3. 若条目不存在：当前 `BLOCKED` 结论成立，但证据更充分（从「未检查」升级为「已检查且确认缺失」）。
  4. 验证点：检查 SQLite 后确认 `pdf_path` 指向的文件仍存在（`cache.py:353` 已有此检查）。
- **修复风险**: 低 — `get_pdf_entry()` 是纯读操作，调用不改变任何状态。
- **严重程度**: 中

### F2-未修复-低-PF3 将 `load_parsed_report()` 与 `get_pdf_entry()` 的风险混为一谈

- **位置**: Preflight §3 PF3
- **问题类型**: 证据描述不精确
- **当前写法**: PF3 声明「Internal parsed cache can prove a parsed report only by loading a `ParsedAnnualReport` payload」并标记为 `DO_NOT_USE_AS_CURRENT_GATE_PROOF`。该描述仅覆盖 `load_parsed_report()`（反序列化完整 JSON body），但未区分 `get_pdf_entry()`（仅返回元数据，不含 body）。
- **反例/失败场景**: 若后续 reviewer 或 controller 将 PF3 理解为「所有内部缓存方法都会暴露 report body 因此都不可用」，可能错误排除 `get_pdf_entry()` 这一零风险检查路径。
- **为什么有问题**: `get_pdf_entry()` 返回 `AnnualReportPdfCacheEntry(pdf_path, source_metadata, updated_at)`，不经过 `ParsedAnnualReport.from_dict()` 反序列化，不触碰 report body。将其与 `load_parsed_report()` 归入同一风险等级会误导后续决策。
- **直接证据**:
  - `cache.py:31-43`：`AnnualReportPdfCacheEntry` 只含 `pdf_path: Path`、`source_metadata: AnnualReportSourceMetadata | None`、`updated_at: str`，无 body 字段。
  - `cache.py:452-492`：`_load_parsed_report_sync()` 读取 JSON 文件并通过 `ParsedAnnualReport.from_dict(payload)` 反序列化完整 body，与 `get_pdf_entry()` 的行为完全不同。
- **影响**: 信息不精确，可能导致后续决策排除实际可用的检查手段。
- **建议改法和验证点**: 将 PF3 拆分为两条：一条覆盖 `load_parsed_report()`（反序列化 body），一条覆盖 `get_pdf_entry()` / `get_pdf_path()`（仅元数据，可作为缓存可用性信号）。
- **修复风险**: 低 — 仅需修改 preflight artifact 中的文字描述。
- **严重程度**: 低

### F3-未修复-低-推荐路径排序未考虑缓存可用性检查优先

- **位置**: Preflight §6 Required Next Authorization
- **问题类型**: 非最优方案
- **当前写法**: 三条推荐路径排序为 1) Live EID sub-slice → 2) Cache-only contract gate → 3) Data-source artifact authorization。Live 路径排在首位。
- **反例/失败场景**: 若缓存已存在（见 F1），走路径 1 是多余的 — 用户授权了一次不必要的 live access；走路径 2 需要先实施代码变更再使用，增加了不必要的往返。
- **为什么有问题**: 按最小权限原则，应先尝试零风险路径（检查缓存可用性），再按需 escalation 到 live authorization 或代码变更。Preflight 将最重的手段排在首位。
- **直接证据**: 前序 live evidence run `004393 / 2021-2025` 已通过 `FundDocumentRepository` 执行并被 controller 接受（`docs/current-startup-packet.md` §4: `271a052`），该 run 极可能已为 `004393 / 2025` 创建了缓存条目。
- **影响**: 增加不必要的用户决策负担；可能导致跳过更简单、更安全的路径。
- **建议改法和验证点**: 步骤 0：先通过 `get_pdf_entry()` 检查缓存可用性。若缓存存在 → 走纯缓存验证。若缓存不存在 → 再呈现三条路径供选择。将路径 2（cache-only contract）提升为无缓存时的首选（架构上更干净），live sub-slice 作为 fallback。
- **修复风险**: 低 — 仅调整 preflight 章节顺序和优先级表述。
- **严重程度**: 低

### F4-未修复-低-preflight 缺少显式 residual owner 表

- **位置**: Preflight 全文
- **问题类型**: 契约缺失
- **当前写法**: Preflight 在 §5 列出 row verification status，在 §6 列出三条推荐路径，但没有显式的 residual owner 表。
- **反例/失败场景**: Controller 在后续 handoff 时无法直接确定「谁负责执行缓存检查」「谁负责请求 live authorization」「谁负责实现 cache-only contract」。责任模糊可能导致 gate 停滞。
- **为什么有问题**: Controller judgment（`docs/reviews/mvp-004393-2025-tracked-golden-content-write-plan-controller-judgment-20260613.md` §6）已定义了 residual owner：`Golden content/source owner` 和 `Controller / evidence owner`。Preflight 应继承并细化这些 owner，而不是静默省略。
- **直接证据**: Controller judgment §6 Residuals 表明确列出了「Seven candidate rows need source-body verification before tracked truth」的 owner 为 `Golden content/source owner`，destination 为本 gate。
- **影响**: 下一 gate 启动时需额外查找 owner 信息，增加 handoff 摩擦。
- **建议改法和验证点**: 增加 Residual Owner 章节，显式列出：
  - 缓存可用性检查 → Controller / evidence owner
  - Live EID authorization 决策 → User
  - Cache-only contract 实现（如选择）→ Fund/documents owner
  - 7 行 source-body 验证执行 → Golden content/source owner
- **修复风险**: 低
- **严重程度**: 低

## 4. Review Lens 专项回答

### Lens: 内部缓存方法是否可在不违反 repository 边界的情况下使用？

**结论：部分可用，但需要区分方法。**

- `get_pdf_entry()` / `get_pdf_path()`：纯 SQLite 读取，不触碰 PDF 文件、不发起网络、不反序列化 report body。作为缓存可用性的**元数据信号**使用，不违反「年报访问必须经过 FundDocumentRepository」的规则（因为没有发生年报访问）。但直接调用 `repository._cache` 确实穿透了 repository 的 public API 边界。
- `load_parsed_report()`：反序列化完整 `ParsedAnnualReport` body。即使是内部方法，这构成了对年报内容的访问，应通过 repository 公共接口进行。
- 架构上正确的做法：在 `FundDocumentRepository` 上增加一个 public `has_usable_cache(fund_code, year) -> bool` 方法，封装 `get_pdf_entry()` 检查。这需要单独的 cache-only contract gate（Preflight §6 路径 2），但检查成本低、风险小。

### Lens: 推荐 live authorization 决策是否正确与当前 gate 分离？

**结论：正确分离。** Preflight 未授权任何 live 操作；它只在 §6 列出了需要用户显式授权的路径。§7 Boundary Confirmation 明确声明未执行 live/network/PDF 命令。Live authorization 被正确地推迟到用户决策之后的下一个 sub-slice gate。

### Lens: Residual owner 和 next-entry 措辞

**结论：next-entry 措辞可改进。** 「Controlled live EID source-body verification authorization decision」未说明：
- 谁做这个决策（User）
- 决策的范围（仅 `004393 / 2025`，仅 7 个 accepted candidate rows）
- 决策后下一步是什么

建议改为：
```
004393 / 2025 cache availability check (zero-risk, using get_pdf_entry)
→ if cache exists: proceed to repository-bounded source-body verification
→ if cache missing: user decision on live EID sub-slice authorization
  or cache-only contract implementation gate
```

## 5. Open Questions

| # | Question |
|---|---|
| Q1 | 前序 `004393 / 2021-2025` live evidence run 是否为 `004393 / 2025` 创建了 parsed cache 和 PDF cache 条目？这决定了 `load_annual_report("004393", 2025)` 是否会走纯缓存路径。 |
| Q2 | 若缓存已存在但其 `source_metadata` 不满足 `_is_current_eid_single_source_metadata()`（例如旧格式），preflight 是否应将此视为需要刷新的信号？ |

## 6. Residual Risks

| Residual | Severity | Suggested destination |
|---|---|---|
| Preflight 在未检查缓存状态的情况下封锁，可能引入不必要的 live authorization 往返 | 低 | 由 Controller 在下一步 handoff 前裁决：是否先执行 F1 建议的缓存可用性检查 |
| `get_pdf_entry()` 检查虽零风险但穿透了 `_cache` 私有成员 | 低 | 接受为 preflight 特殊需要；或走 cache-only contract gate 将其正规化 |
| 若缓存存在但 PDF 文件已被删除（`pdf_path.exists()` 返回 False），`get_pdf_entry()` 返回 None，结论回到 BLOCKED | 低 | 属于正确行为；preflight 应记录此情况 |

## 7. Final Verdict

**PASS_WITH_FINDINGS**

Preflight 的核心结论——`load_annual_report()` 在缓存缺失时会 fall through 到 live fetch，因此不能无条件下安全调用——是代码事实，分析准确。

但 preflight 未区分内部缓存方法的风险等级：`get_pdf_entry()`（纯 SQLite 元数据读取）被与 `load_parsed_report()`（完整 body 反序列化）混为一谈，导致错过了一次零风险的缓存可用性检查。在已有前序 live evidence run 可能已创建缓存的前提下，这可能导致不必要的 live authorization 请求。

四项 findings 均为低到中等严重程度，均可在不推翻 preflight 整体结论的前提下修正。无 blocking 级 finding。

## 8. Next Entry Recommendation

建议 preflight 修订后的下一步：

1. **立即**：执行 `get_pdf_entry(DocumentKey("004393", 2025))` 检查缓存可用性（零风险操作）。
2. **若缓存存在且满足 EID policy**：preflight 结论更新为 `ACCESS_SAFE_VIA_CACHE`，gate 可直接进入 repository-bounded source-body verification。
3. **若缓存不存在**：维持 `BLOCKED`，推荐路径排序调整为：cache-only contract gate（架构最优）→ live EID sub-slice authorization → data-source artifact authorization。
