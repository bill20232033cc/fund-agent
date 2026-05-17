# P1-S4 Implementation Artifact

> 日期：2026-05-17
> gate：`P1-S4 implementation`
> slice：`P1-S4 基础画像与基金类型识别`
> 分支：`chore/reconcile-baseline`

## Scope / Non-Goals

### Scope

- 落地 `basic_identity`、`product_profile`、`benchmark`、`fee_schedule` 的最小 extractor 边界。
- 让 `classified_fund_type` 与 `classification_basis` 成为 P1 的稳定输出。
- 让基金类型判断先于通用画像抽取执行。
- 为费率、基准、规模、经理信息输出 `EvidenceAnchor`。

### Non-Goals

- 不修改 `data_extractor.py`。
- 不触碰 `documents/**`、`pdf/**`、`nav_data.py` 或上层目录。
- 不进入 `§3/§4/§8/§9/§10` 抽取。
- 不做 preferred_lens 应用，不做任何投资结论。

## Changed Files

- `fund_agent/fund/fund_type.py`
- `fund_agent/fund/extractors/__init__.py`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/profile.py`
- `tests/fund/extractors/test_profile.py`
- `tests/fixtures/fund/extractors/profile/active_fund_profile.txt`
- `tests/fixtures/fund/extractors/profile/index_enhanced_profile.txt`
- `tests/fixtures/fund/extractors/profile/bond_fund_profile.txt`

## Implemented Items

1. 新增 `fund_agent/fund/fund_type.py`
   - 定义标准化基金类型标签：
     - `index_fund`
     - `active_fund`
     - `bond_fund`
     - `enhanced_index`
     - `qdii_fund`
     - `fof_fund`
   - 基于 `§1/§2` 可得信息实现分类规则：
     - `QDII` / `FOF`
     - 基金类别显式为混合型/股票型时优先归为主动权益基金
     - 指数型与增强指数识别
     - 债券型识别
   - 输出 `FundTypeClassification(classified_fund_type, classification_basis)`，避免只返回标签不返回依据。
2. 新增 `fund_agent/fund/extractors/models.py`
   - 定义 `EvidenceAnchor`
   - 定义泛型 `ExtractedField`
   - 定义 `ProfileExtractionResult`
3. 新增 `fund_agent/fund/extractors/profile.py`
   - 仅基于 `§1/§2` 做 profile 抽取
   - `extract_profile(report)` 执行顺序：
     1. `classify_fund_type(report)`
     2. 生成 `basic_identity`
     3. 生成 `product_profile`
     4. 生成 `benchmark`
     5. 生成 `fee_schedule`
   - `basic_identity.value` 包含：
     - `fund_name`
     - `fund_code`
     - `fund_category`
     - `fund_scale`
     - `fund_manager`
     - `classified_fund_type`
     - `classification_basis`
   - `benchmark`、`fee_schedule`、`fund_scale`、`fund_manager` 都通过 `EvidenceAnchor` 携带 `section_id`、`row_locator` 与原始命中行。
4. 新增最小 extractor fixture 与测试
   - 三个最小文本夹具分别覆盖：
     - 主动权益基金
     - 增强指数基金
     - 债券基金
   - `tests/fund/extractors/test_profile.py` 覆盖：
     - 分类先于通用画像字段构造
     - `classified_fund_type` 与 `classification_basis` 存在
     - 费率、基准、规模、经理信息带 anchor
     - 多基金类型识别不依赖基金代码特判

## Classification-First Closure

- 已显式关闭“先抽字段、后补分类”的顺序风险：
  - `extract_profile()` 在任何画像字段构造前，先调用 `classify_fund_type(report)`
  - 顺序由测试 `test_extract_profile_classifies_before_general_field_builders()` 直接锁定
- `classified_fund_type` 已成为 `basic_identity` 的稳定输出
- `classification_basis` 已与分类标签一起输出，不存在只给标签不给依据的情况
- 当前分类规则不依赖基金代码特判，只基于 `§1/§2` 的名称、类别、基准、投资范围等披露事实

## Validation

执行命令：

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py -q
```

结果：

```text
4 passed in 0.64s
```

## Residual Risks

### Fixed Later Slice

- 当前分类规则只覆盖 P1-S4 当前需要的最小类型集合；若后续样本出现更复杂的偏债混合、二级债基细分，需要在后续 slice 增补规则与 fixture。

### Later Phase

- 当前只抽 `§1/§2`，未进入 `§3/§4/§8/§9/§10`，因此不包含业绩表现、换手率、利益一致性、持仓快照等字段。
- 当前 extractor 结果尚未通过 `data_extractor.py` façade 对外装配，符合当前 slice 边界。

### User Decision

- 无。

## Completion Status

- `P1-S4` completion signal：`reached`
- 判断依据：
  - 已建立最小 extractor 边界
  - `classified_fund_type` 与 `classification_basis` 已成为稳定输出
  - 基金类型判断先于通用抽取输出，且有测试锁定
  - 费率、基准、规模、经理信息均带 `EvidenceAnchor`
