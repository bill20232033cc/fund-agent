# Correctness Golden Answer Template

> 说明：本文件为自动预填底稿，值来自当前 extractor 输出，只能用于人工复核；不能直接作为 correctness golden answer。

## Instructions

- 数据源：以 2024 年年报 PDF 原文为准，天天基金/官网做交叉验证
- `expected_value`：extractor 应返回的精确字符串值，与 PDF 原文一致
- `confidence`：`high`（PDF 明确）/ `medium`（需判断）/ `low`（PDF 模糊）
- `source`：标注来源页码，如 `年报§3 page-8`
- 当前 slice 未实现的字段标 `—`，不填 expected_value
- 每只基金独立一张表，填完后用于构建 golden set JSON

---

## 004393 安信企业价值优选混合A（国内股票类）

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| basic_identity | fund_name | 安信企业价值优选混合型证券投资基金 | high | 年报2024 §2 page-5 page-5-table-0 fund_name |
| basic_identity | fund_code | 004393 | high | 年报2024 §2 page-5 page-5-table-0 fund_code |
| basic_identity | management_company | 安信基金管理有限责任公司 | high | 年报2024 §2 page-5 page-5-table-0 management_company |
| basic_identity | custodian | 中国银行股份有限公司 | high | 年报2024 §2 page-5 page-5-table-0 custodian |
| basic_identity | inception_date | 2022 年 8 月 8 日 | high | 年报2024 §2 page-5 page-5-table-0 inception_date |
| product_profile | investment_objective | 本基金在有效控制组合风险并保持基金资产流动性的前提下，力争实现基金 资产的长期稳健增值。 | high | 年报2024 §2 page-5 page-5-table-1 investment_objective |
| product_profile | style_positioning | 资产的长期稳健增值。 | medium | 年报2024 §2 page-5 page-5-table-1 investment_objective |
| product_profile | investment_scope | 资产配置上，本基金以基于宏观、政策及市场分析的定性研究为主，同时结合定量分析的方法，对未来各大类资产的风险和预期收益率进行分析评估，制定股票、债券、现金等大类资产之间的配置比例、调整原则和调整范围。股票投资上，本基金的股票投资策略包括公司基本面分析、股票估值分析、港股通标的股票投资策略及存托凭证投资策略。债券投资上，在宏观经济运行态势分析、经济政策分析的基础上，分析基础利率的走势，研究利率期限结构和中长期收益率走势。此外，本基金还将适当参与衍生品和资产支持证券的投资。 | high | 年报2024 §2 page-5 page-5-table-1 investment_scope |
| benchmark | benchmark_name | 沪深300指数收益率×60%+恒生指数收益率（经汇率调整后）×20%+中债综 合（全价）指数收益率×20% | high | 年报2024 §2 page-5 page-5-table-1 benchmark |
| fee_schedule | — | — | — | 当前 slice 不处理 |
| classified_fund_type | fund_type | active_fund | high | 年报2024 §2 page-5 page-5-table-0 fund_name |
| nav_benchmark_performance | nav_growth_rate | 17.32% | high | 年报2024 §3 page-8 page-8-table-0 nav_growth_rate |
| nav_benchmark_performance | benchmark_return_rate | 14.45% | high | 年报2024 §3 page-8 page-8-table-0 benchmark_return_rate |
| investor_return | — | — | — | 当前 slice 不处理 |
| manager_strategy_text | strategy_summary | 本产品一直坚持自下而上的投资选股思路，在充分研究公司商业模式、竞争优势、公司成长 空间、行业竞争格局的背景下，结合估值水平，在“好价格”下买入并持有“好公司”，长期获得 企业内在价值增长的收益。 2024年国内GDP保持了5%的增长，季度间呈现两头高、中间低的特征。年底部分经济数据呈 现企稳回升态势，制造业PMI连续3个月保持在荣枯线以上，一线城市二手房成交量受益于9月 出台的增量政策持续回暖，新房销售四季度也有回暖迹象。2024年下半年开展的大规模消费补贴 政策带动了下游消费的回暖，特别是汽车家电等耐用消费品景气度回升明显。货币政策方面，社 融和M2数据体现流动性依然相对宽松，十年期国债收益率全年下行至1.6%左右，人民币兑美元 汇率全年小幅波动略有贬值。 2024年股票市场震荡上行，主要指数多数取得了 10%以上的涨幅。沪深300指数全年上涨 14.68%，结束了连续3年的下跌态势。分行业来看，全年银行、非银金融、通信、家电等行业表 现较好，医药、农业、美容护理、食品饮料等行业表现较差。2024年本产品净值跟随市场有所上 涨，跑赢沪深300指数。 第 13 页 安信企业价值优选混合2024年年度报告 2024年末仓位相比年初小幅减少，但整体仍在相对高位。相比年初主要增加了交运、建材、 银行等行业的配置，减少了地产、食品饮料、家电等行业的配置。目前相对看好的公司集中在银 行、纺织服饰、建材、煤炭、电力设备等细分行业。 | medium | 年报2024 §4 strategy_summary |
| manager_strategy_text | market_outlook | 近期来看，市场指数震荡调整，市场交易量维持在1万亿以上，显示市场情绪仍然不错。我 们判断当下还是预期先行的阶段，市场估值的波动大于基本面业绩的波动。从中长期维度来看， 个股基本面业绩会逐步跟上估值调整的步伐。当前股票市场估值总体处于历史平均偏低位置。2025 年随着宏观政策的落地，我们能够陆续看到更多优秀上市公司业绩触底回升，我们还是坚持精选 细分行业优秀公司，力求从未来2-3年业绩增长确定性的角度来挖掘当前估值具有性价比的公司。 宏观经济与政策展望方面，我们总体判断宏观经济在2025年会温和回升，我们看到年底中央 政治局会议和中央经济工作会议对2025年宏观经济政策做了总体指引。总的基调是政府会实施更 加积极的财政政策和适度宽松的货币政策。这表明财政政策2025年大概率会加大力度，会议提到 加强超常规逆周期调节，要大力提振消费，提高投资效益，全方位扩大国内需求。从2024年下半 年开始的消费品以旧换新补贴政策取得了不错效果，我们预计2025年大概率会延续。会议提到货 币政策要“适度宽松”，这是2011年以来首次提到，我们预计2025年货币政策在利率端和总量端 还有操作空间。 另外，港股市场2024年震荡上行，目前沪港AH溢价指数依然维持在150左右，整体港股估 值相比A股依然具有性价比。因此我们继续维持了一定港股持仓，我们相对看好港股估值较低而 预计两年内业绩还能保持平稳的公司，它们集中在金融、煤炭、石油、交运等行业。我们继续提 高了一些港股估值盈利双低，未来预期盈利能够触底回升公司的关注度。 | medium | 年报2024 §4 market_outlook |
| turnover_rate | — | — | — | 当前 slice 不处理 |
| manager_alignment | manager_holding | 项目 份额级别 持有基金份额总量的数量区间（万份） 本公司高级管理人员、 基金投资和研究部门 负责人持有本开放式 基金 安信企业价值优选混合A 50~100  安信企业价值优选混合C 0  合计 50~100 本基金基金经理持有 本开放式基金 安信企业价值优选混合A 10~50  安信企业价值优选混合C 0  合计 10~50 | medium | 年报2024 §9 page-63 page-63-table-2 manager_holding |
| manager_alignment | employee_holding | 项目 份额级别 持有份额总数（份） 占基金总份额比例（%） 基金管 理人所 有从业 人员持 有本基 金 安信企业价值优选混合A 1,285,751.43 0.86  安信企业价值优选混合C 0.55 0.00  合计 1,285,751.98 0.79 | medium | 年报2024 §9 page-63 page-63-table-1 employee_holding |
| holder_structure | institutional_holder | 86.46 | high | 年报2024 §9 page-63 page-63-table-0 institutional_holder |
| holder_structure | individual_holder | 13.54 | high | 年报2024 §9 page-63 page-63-table-0 individual_holder |
| holdings_snapshot | — | — | — | 当前 slice 不处理 |
| share_change | beginning_share | 27,666,410.41 | high | 年报2024 §10 page-64 page-64-table-0 share_change |
| share_change | ending_share | 149,565,740.00 | high | 年报2024 §10 page-64 page-64-table-0 share_change |
| share_change | net_change | 121,899,329.59 | high | 年报2024 §10 page-64 page-64-table-0 share_change |

---

## 000216 华安黄金ETF联接A（黄金类）

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| basic_identity | fund_name | 华安易富黄金交易型开放式证券投资基金联接基金 | high | 年报2024 §2 page-5 page-5-table-0 fund_name |
| basic_identity | fund_code | 000216 | high | 年报2024 §2 page-5 page-5-table-0 fund_code |
| basic_identity | management_company | 华安基金管理有限公司 | high | 年报2024 §2 page-5 page-5-table-0 management_company |
| basic_identity | custodian | 中国建设银行股份有限公司 | high | 年报2024 §2 page-5 page-5-table-0 custodian |
| basic_identity | inception_date | 2013年8月22日 | high | 年报2024 §2 page-5 page-5-table-0 inception_date |
| product_profile | investment_objective | 本基金主要通过对目标ETF基金份额的投资，紧密跟踪中国黄金 现货价格的表现。 | high | 年报2024 §2 page-5 page-5-table-2 investment_objective |
| product_profile | investment_scope | — | — | 当前证据不足，人工复核后补充 |
| product_profile | style_positioning | 本基金是目标ETF的联接基金，目标ETF为黄金ETF，因此本基金的风险收益特征与国内黄金现货价格的风险收益特征相似，不同于股票基金、混合基金、债券基金和货币市场基金。 | high | 年报2024 §2 page-5 page-5-table-2 style_positioning |
| benchmark | benchmark_name | 国内黄金现货价格收益率×95%＋人民币活期存款税后利率×5% | high | 年报2024 §2 page-5 page-5-table-2 benchmark |
| fee_schedule | — | — | — | 当前 slice 不处理 |
| classified_fund_type | fund_type | index_fund | high | 年报2024 §2 page-5 page-5-table-0 fund_name |
| nav_benchmark_performance | nav_growth_rate | 25.96% | high | 年报2024 §3 page-8 page-8-table-1 nav_growth_rate |
| nav_benchmark_performance | benchmark_return_rate | 26.68% | high | 年报2024 §3 page-8 page-8-table-1 benchmark_return_rate |
| investor_return | — | — | — | 当前 slice 不处理 |
| manager_strategy_text | strategy_summary | 2024 年，伦敦现货黄金上涨 27.23%至 2624 美元/盎司；本基金所跟踪的 AU9999 黄金上涨 28.19%至614元/克。国内黄金价格再次刷新历史新高，全年维度明显跑赢其他大类资产。 黄金的良好表现基于三大因素。首先，2024年9月美联储开启降息，并在11月、12月议息 会议维持降息节奏，美联储点阵图显示2025年有望延续降息。海外货币环境宽松，对于黄金的影 响相对积极。其次，去美元化因素影响下，全球央行持续购金，2024年净购金量再度超过1000吨， 保持了2022年以来较高的购金力度。第三，全球政策变动加快，在大类资产不确定性加大的背景 下，黄金分散风险。 长期来看，美国当前面临高债务和高利率的双重压力，未来将加重美国财政负担，影响美元 信用。此外，当前国内利率水平偏低，黄金和股票、债券之间呈现低相关性，黄金的配置价值突 出，加入黄金或有望改善组合夏普比。 本基金主要投资于上海黄金交易所挂盘交易的黄金现货合约等黄金品种，力求获得我国黄金 现货市场收益率，为投资者提供一类管理透明、成本较低、有效跟踪国内黄金现货价格的投资工 具。 投资管理上，基金采取完全复制的管理方法跟踪指数，并利用量化工具进行精细化管理，从 而控制基金的跟踪误差和跟踪偏离度。 | medium | 年报2024 §4 strategy_summary |
| manager_strategy_text | market_outlook | 2025年全球宏观政策充满复杂性。第一，海外关税政策多变，对全球经济产生一定的负面冲 击，同时加剧了美国再通胀的担忧。第二，美联储在 1 月暂停降息，美国经济同时反映出衰退信 号和再通胀信号，滞胀环境导致货币政策面临两难抉择。 从证券市场维度，随着国内经济数据企稳回暖，权益类资产的吸引力明显提升，资金面出现 股债跷跷板效应。全球资金有望回流中国资产，无论是估值性价比，还是科技产业景气度，当前 中国在人工智能、机器人、算力芯片等产业链的话语权持续加强。 对黄金的中长期配置价值维持乐观。第一，黄金的定价本质依然是应对信用货币超发，全球 整体维持宽松的货币环境。第二，货币体系变革下，央行购金的延续性可期，成为黄金定价的重 要因素。第三，政策不确定性，导致海外资产波动加大，关注黄金在资产组合中的配置价值。当 前在黄金持续创新高的同时，也要关注COMEX溢价等交易因素带来的短期金价波动。 | medium | 年报2024 §4 market_outlook |
| turnover_rate | — | — | — | 当前 slice 不处理 |
| manager_alignment | manager_holding |  项目   份额级别   持有基金份额总量的数量区间（万份）  本公司高级管理人 员、基金投资和研究 部门负责人持有本开 放式基金   华安黄金易(ETF联接) A   0~10      华安黄金易(ETF联接) C   0~10      华安黄金易(ETF联接) I   -      合计   0~10   本基金基金经理持有 本开放式基金   华安黄金易(ETF联接) A   0~10      华安黄金易(ETF联接) C   0~10      华安黄金易(ETF联接) I   -      合计   0~10   | medium | 年报2024 §9 page-58 page-58-table-2 manager_holding |
| manager_alignment | employee_holding | 项目 份额级别 持有份额总数（份）  占基金总份额比例      （%）  基金管 理人所 有从业 人员持 有本基 金 华安黄金易(ETF联接) A 1,654,570.27 0.11    华安黄金易(ETF联接) C 656,631.88 0.01    华安黄金易(ETF联接) I 219,121.77 73.57    合计 2,530,323.92 0.04   | medium | 年报2024 §9 page-58 page-58-table-1 employee_holding |
| holder_structure | institutional_holder | 17.47 | high | 年报2024 §9 page-57 page-57-table-1 institutional_holder |
| holder_structure | individual_holder | 82.53 | high | 年报2024 §9 page-57 page-57-table-1 individual_holder |
| holdings_snapshot | — | — | — | 当前 slice 不处理 |
| share_change | beginning_share | 749,902,646.74 | high | 年报2024 §10 page-59 page-59-table-0 share_change |
| share_change | ending_share | 1,449,126,284.87 | high | 年报2024 §10 page-59 page-59-table-0 share_change |
| share_change | net_change | 699,223,638.13 | high | 年报2024 §10 page-59 page-59-table-0 share_change |

---

## 007721 天弘标普500发起(QDII-FOF)A（海外股票类）

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| basic_identity | fund_name | 天弘标普500发起式证券投资基金（QDII-FOF） | high | 年报2024 §2 page-5 page-5-table-0 fund_name |
| basic_identity | fund_code | 007721 | high | 年报2024 §2 page-5 page-5-table-0 fund_code |
| basic_identity | management_company | 天弘基金管理有限公司 | high | 年报2024 §2 page-5 page-5-table-0 management_company |
| basic_identity | custodian | 中信银行股份有限公司 | high | 年报2024 §2 page-5 page-5-table-0 custodian |
| basic_identity | inception_date | 2019年09月24日 | high | 年报2024 §2 page-5 page-5-table-0 inception_date |
| product_profile | investment_objective | 在严格控制组合风险的基础上，主要投资于跟踪标普5 00指数的基金（含ETF），力争实现对标普500指数走 势的有效跟踪。 | high | 年报2024 §2 page-5 page-5-table-1 investment_objective |
| product_profile | investment_scope | — | — | 当前证据不足，人工复核后补充 |
| product_profile | style_positioning | 本基金主要投资于境外跟踪标普500指数的相关基金（包括ETF），力争实现对标普500指数走势的有效跟 | medium | 年报2024 §2 page-5 page-5-table-1 style_positioning |
| benchmark | benchmark_name | 95%*标普500指数收益率（使用估值汇率折算）+5%* 人民币活期存款利率（税后）。 | high | 年报2024 §2 page-5 page-5-table-1 benchmark |
| fee_schedule | — | — | — | 当前 slice 不处理 |
| classified_fund_type | fund_type | qdii_fund | high | 年报2024 §2 page-5 page-5-table-0 fund_name |
| nav_benchmark_performance | nav_growth_rate | 19.51% | high | 年报2024 §3 page-9 page-9-table-0 nav_growth_rate |
| nav_benchmark_performance | benchmark_return_rate | 23.82% | high | 年报2024 §3 page-9 page-9-table-0 benchmark_return_rate |
| investor_return | — | — | — | 当前 slice 不处理 |
| manager_strategy_text | strategy_summary | 2024年美国经济依然保持了韧性，全年GDP增速为2.8%（2023年增速为2.9%）；居 民消费依然积极，同比为2.8%，失业率维持在4%附近，通胀同比有明显下行，从4.1% 降至3%（以上数据均来自于彭博）。目前美国就业和通胀处于风险相对均衡状态，就业 市场下行风险可控，但与此同时通胀也保持了黏性。 美联储于9月正式开启降息，9月、11月、12月3次降息累计降息100bps，政策利率 从5.5%降至4.5%。从主席鲍威尔讲话及官员指引来看，美联储可能仍处于降息周期，后 续的政策选择或仍将通过密切观察数据、平衡就业和通胀风险、适当继续降息以实现美 国经济软着陆。 2024年11月的美国大选是政治上的大事件，特朗普顺利获选并实现了两院横扫。年 末市场提前押注“特朗普交易”，并对特朗普正式就任后的内阁提名、政策顺序、执行 力度进行了多方分析。特朗普在其第二任期中的政策成为了市场关注最大的影响因素。 第15页 天弘标普500发起式证券投资基金（QDII-FOF）2024年年度报告 美股在2024年继续获得了不错的涨幅。标普500指数全年收益率23.3%（数据来源彭 博），连续第二年涨幅超过20%。从支撑因素来看，主要是经济韧性、美联储宽松、AI 进展推动。全年来看，市场回撤相对有限，冲击主要来自于美债利率上行、AI进展不及 预期、全球拥挤交易洗牌等。 作为追踪标普500指数的被动式海外指数基金，本基金的投资目标是通过投资于全 球范围内跟踪标普500指数的基金（含 ETF），综合运用股指期货等衍生品工具，力争 实现对标普500指数走势的有效跟踪。 | medium | 年报2024 §4 strategy_summary |
| manager_strategy_text | market_outlook | 展望2025年，几条主线值得密切关注。第一，美国经济走势和美联储政策选择。市 场对美国经济走向软着陆依然信心十足。核心在于居民、企业资产负债表依然稳健。但 通胀压力制约下的利率居高不下，可能也对一些脆弱部门形成了压力。美联储选择何时 降息、降息多少、如何平衡风险，非常关键。第二，特朗普政策选择。特朗普竞选过程 中宣称的各种政策存在左右博弈的现象，到底如何取舍，政策落实后会对经济和通胀形 成何种影响，是需要密切关注的主题。尤其关税政策，是全球都担忧的风险点。第三， AI主线的进展。AI是2023-2024年中投资的绝对热点。新的一年，投资人的诉求更进一 步，除了在投资端需要看到企业继续保持积极加大capex支出的态度，还希望在需求端看 到未来需求和应用的乐观指引，尤其是在AI商业化提升ROI方面。AI在应用端爆发尤为 重要。 在经历了连续两年的大涨之后，市场对标普500的上涨预期相对趋于理性和中性。 估值高位背景下，主流机构对标普500的涨幅预测主要依靠EPS增长驱动。软着陆背景加 美联储降息，有利于支撑美股的估值和盈利；但特朗普政策和AI进展的不确定性，可能 加大市场波动。 中长期来看，标普500成分股公司大都为各自细分领域的龙头公司，具有较强的盈 利能力和抗风险能力，并且能够在全球市场范围内获得利润，标普500指数具备较好的 配置价值。 第16页 天弘标普500发起式证券投资基金（QDII-FOF）2024年年度报告 | medium | 年报2024 §4 market_outlook |
| turnover_rate | — | — | — | 当前 slice 不处理 |
| manager_alignment | manager_holding | 项目 份额级别 持有基金份额总量的数量区 间（万份） 本公司高级管理人员、基金投资 和研究部门负责人持有本开放式 基金 天弘标普500发起 （QDII-FOF）A 10~50  天弘标普500发起 （QDII-FOF）C 50~100  天弘标普500发起 （QDII-FOF）D 0  合计 >100 本基金基金经理持有本开放式基 金 天弘标普500发起 （QDII-FOF）A 0~10  天弘标普500发起 （QDII-FOF）C 0  天弘标普500发起 0 | medium | 年报2024 §9 page-66 page-66-table-1 manager_holding |
| manager_alignment | employee_holding | 项目 份额级别 持有份额总数 （份） 占基金总份额 比例 基金管理人所有从业人 员持有本基金 天弘标普500发起（QDI I-FOF）A 707,562.79 0.06%  天弘标普500发起（QDI I-FOF）C 1,133,680.28 0.07%  天弘标普500发起（QDI I-FOF）D 5,011.61 0.01%  合计 1,846,254.68 0.07% | medium | 年报2024 §9 page-66 page-66-table-0 employee_holding |
| holder_structure | institutional_holder | 3.42% | high | 年报2024 §9 page-65 page-65-table-0 institutional_holder |
| holder_structure | individual_holder | 96.58% | high | 年报2024 §9 page-65 page-65-table-0 individual_holder |
| holdings_snapshot | — | — | — | 当前 slice 不处理 |
| share_change | beginning_share | 175,479,626.60 | high | 年报2024 §10 page-67 page-67-table-1 share_change |
| share_change | ending_share | 1,261,336,828.49 | high | 年报2024 §10 page-67 page-67-table-1 share_change |
| share_change | net_change | 1,085,857,201.89 | high | 年报2024 §10 page-67 page-67-table-1 share_change |

---

## 007360 易方达中短期美元债债券(QDII)A(人民币份额)（海外债券/稳健类）

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| basic_identity | fund_name | 易方达中短期美元债债券型证券投资基金（QDII） | high | 年报2024 §2 page-5 page-5-table-0 fund_name |
| basic_identity | fund_code | 007360 | high | 年报2024 §2 page-5 page-5-table-0 fund_code |
| basic_identity | management_company | 易方达基金管理有限公司 | high | 年报2024 §2 page-5 page-5-table-0 management_company |
| basic_identity | custodian | 招商银行股份有限公司 | high | 年报2024 §2 page-5 page-5-table-0 custodian |
| basic_identity | inception_date | 2019年6月5日 | high | 年报2024 §2 page-5 page-5-table-0 inception_date |
| product_profile | investment_objective | 本基金主要投资中短期美元债券，在严格控制风险和保持较高流动性的基 础上，力求获得超越业绩比较基准的投资回报。 | high | 年报2024 §2 page-5 page-5-table-1 investment_objective |
| product_profile | investment_scope | — | — | 当前证据不足，人工复核后补充 |
| product_profile | style_positioning | 本基金为债券基金，理论上其预期风险与预期收益水平低于股票基金、混合基金，高于货币市场基金。本基金投资境外市场，除了需要承担与境内证券投资基金类似的市场波动风险等一般投资风险之外，本基金还面临汇率风险、国家/地区风险等境外投资面临的特有风险。 | high | 年报2024 §2 page-6 page-6-table-0 style_positioning |
| benchmark | benchmark_name | 摩根大通 1-3 年全球投资级美元债总回报指数（J.P. Morgan Global Aggregate US IG 1-3 Total Return Index ）（按照估值汇率折算）收益率 | high | 年报2024 §2 page-5 page-5-table-1 benchmark |
| fee_schedule | — | — | — | 当前 slice 不处理 |
| classified_fund_type | fund_type | qdii_fund | high | 年报2024 §2 page-5 page-5-table-0 fund_name |
| nav_benchmark_performance | nav_growth_rate | 5.25% | high | 年报2024 §3 page-9 page-9-table-0 nav_growth_rate |
| nav_benchmark_performance | benchmark_return_rate | 5.73% | high | 年报2024 §3 page-9 page-9-table-0 benchmark_return_rate |
| investor_return | — | — | — | 当前 slice 不处理 |
| manager_strategy_text | strategy_summary | 2024年美债收益率维持高位震荡行情。一季度受美国就业、消费等经济数据偏强影响，市场调 整全年降息预期由6次降至 3次，10年期美债利率由年初 3.9%攀升至4.7%。二三季度美国经济基 本面大致平稳，但就业数据边际恶化，叠加美联储于9月降息50bp，开启本轮降息周期，10年期美 债利率一路下探至3.6%。四季度市场焦点转为特朗普当选总统对通胀预期抬升的担忧，利率再度上 第14页共68页 易方达中短期美元债债券型证券投资基金（QDII）2024年年度报告 行至4.5%。全年来看，2年期美债利率持平、10年期美债利率则升60bp，美债收益率曲线呈现陡峭 化态势。信用利差则表现不俗，全年来看，美国投资级债收窄20bp、美国高收益债收窄36bp。 尽管美联储货币政策已进入降息周期，市场定价降息节奏与经济数据韧性较强的预期差，导致 中长端美债呈现高位震荡行情。一方面，企业投资受益于人工智能设备和新工厂投资推动，消费者 支出在劳动力收入增长和股市财富效应外溢下表现强劲，另一方面，本轮周期企业部门和居民部门 整体均体现出杠杆率稳健、债务久期较长等特点，加息政策影响存在时滞效应。在此背景下，2024 年美国风险资产表现较优，美国国债指数回报为0.6%，美国投资级债和高收益债指数分别录得2.1%、 8.2%的回报，标普500股票指数表现强劲，收益达23.3%。 组合运作方面，1 季度我们大幅提高信用债配置比例，降低国债占比，提高组合静态收益率， 获取信用利差Carry和收窄回报，并重点配置金融、公用事业、汽车等行业债券。4季度跟随国债利 率上行，我们进一步提升组合久期至 3.3 年，达到组合成立以来较高位置，我们认为美元债存在较 高票息和潜在资本利得机会。 | medium | 年报2024 §4 strategy_summary |
| manager_strategy_text | market_outlook | 展望2025年，特朗普政策实施和美联储降息节奏为市场关注焦点。尽管特朗普的关税政策有推 高通胀倾向，我们认为市场定价已较为充分，目前市场仅预期全年降息 1 次，美债收益率或易下难 上。与此同时，美债收益率曲线已恢复正常化，投资者资金持续流入债券基金，预计期限利差将支 持久期策略表现。考虑到降息周期的曲线陡峭化行情，我们将重点配置中短端品种，并对长端品种 开展波段交易。信用策略方面，我们维持信用债较高比例配置，并关注信用波动带来的投资机会。 | medium | 年报2024 §4 market_outlook |
| turnover_rate | — | — | — | 当前 slice 不处理 |
| manager_alignment | manager_holding | 项目 份额级别 持有基金份额总量的数量区间（万份） 本公司高级管理人员、基 金投资和研究部门负责人 持有本开放式基金 易方达中短期美元债债 券（QDII）A >100  易方达中短期美元债债 券（QDII）C >100  合计 >100 本基金基金经理持有本开 放式基金 易方达中短期美元债债 券（QDII）A 0  易方达中短期美元债债 券（QDII）C 0  合计 0 | medium | 年报2024 §9 page-57 page-57-table-2 manager_holding |
| manager_alignment | employee_holding | 项目 份额级别 持有份额总数（份） 占基金总份额比例 基金管理人所有从业人 员持有本基金 易方达中短期美元债债 券（QDII）A 18,285,008.28 1.2079%  易方达中短期美元债债 券（QDII）C 2,671,880.18 0.6114%  合计 20,956,888.46 1.0743% | medium | 年报2024 §9 page-57 page-57-table-1 employee_holding |
| holder_structure | institutional_holder | 37.37% | high | 年报2024 §9 page-57 page-57-table-0 institutional_holder |
| holder_structure | individual_holder | 62.63% | high | 年报2024 §9 page-57 page-57-table-0 individual_holder |
| holdings_snapshot | — | — | — | 当前 slice 不处理 |
| share_change | beginning_share | 842,783,461.75 | high | 年报2024 §10 page-58 page-58-table-0 share_change |
| share_change | ending_share | 1,513,728,092.82 | high | 年报2024 §10 page-58 page-58-table-0 share_change |
| share_change | net_change | 670,944,631.07 | high | 年报2024 §10 page-58 page-58-table-0 share_change |

---

## 006597 国泰利享中短债债券A（国内债券类）

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| basic_identity | fund_name | 国泰利享中短债债券型证券投资基金 | high | 年报2024 §2 page-5 page-5-table-0 fund_name |
| basic_identity | fund_code | 006597 | high | 年报2024 §2 page-5 page-5-table-0 fund_code |
| basic_identity | management_company | 国泰基金管理有限公司 | high | 年报2024 §2 page-5 page-5-table-0 management_company |
| basic_identity | custodian | 招商银行股份有限公司 | high | 年报2024 §2 page-5 page-5-table-0 custodian |
| basic_identity | inception_date | 2018年12月3日 | high | 年报2024 §2 page-5 page-5-table-0 inception_date |
| product_profile | investment_objective | 在严格控制风险的前提下，追求稳健的投资回报。 | high | 年报2024 §2 page-5 page-5-table-1 investment_objective |
| product_profile | investment_scope | — | — | 当前证据不足，人工复核后补充 |
| product_profile | style_positioning | 本基金为债券型基金，预期收益和预期风险高于货币市场基金，但低于混合型基金、股票型基金，属于较低预期风险和预期收益的产品。 | high | 年报2024 §2 page-5 page-5-table-1 style_positioning |
| benchmark | benchmark_name | 中债总财富（1-3年）指数收益率*80%＋一年期定期存款利率(税后)*20% | high | 年报2024 §2 page-5 page-5-table-1 benchmark |
| fee_schedule | — | — | — | 当前 slice 不处理 |
| classified_fund_type | fund_type | bond_fund | high | 年报2024 §2 page-5 page-5-table-0 fund_name |
| nav_benchmark_performance | nav_growth_rate | 2.57% | high | 年报2024 §3 page-11 page-11-table-1 nav_growth_rate |
| nav_benchmark_performance | benchmark_return_rate | 3.42% | high | 年报2024 §3 page-11 page-11-table-1 benchmark_return_rate |
| investor_return | — | — | — | 当前 slice 不处理 |
| manager_strategy_text | strategy_summary | 2024年债市整体表现震荡走牛，一季度，1月下旬超预期宣布降准，2 月春节后 5 年 LPR 利 率下调 25BP，叠加多地城商行存款利率调降，3 月初政府工作报告未给出超预期的刺激政策，债 市做多情绪强劲，各期限下行；随后市场止盈需求增加，叠加跨季因素扰动，各期限小幅调整后窄 幅波动。二季度，4月公布的一季度经济数据仍处于弱复苏状态，市场关注度较高的特别国债发行 节奏低于预期，手工补息禁止后资金面阶段性宽松等因素共同推动债市收益率持续下行。月末央行 提示超长债的久期风险，带动收益率转为上行。5月，超长期特别国债发行计划公布，节奏较市场 第20页共70页 国泰利享中短债债券型证券投资基金2024年年度报告 预期更为平缓，包括一线城市在内的多项地产政策落地，债市收益率小幅震荡。6月，非银主导的 流动性宽松延续，跨季资金面平稳；中旬公布的数据显示经济依然面临有效需求不足的挑战，债市 收益率进一步下行。三季度，7月央行宣布开展国债借入操作，此举旨在通过信用方式借入国债影 响长端利率，中旬央行宣布降息使得收益率转为下行。8月收益率先上后下，央行通过预期管理、 借入国债、强监管、卖出国债等方式修正利率单边下行预期，债市有所调整。信用债表现不及利率 债，后半段有一定修复。9月受宏观政策刺激以及股市提振影响，债市出现调整，在央行双降后公 布支持资本市场的结构性货币政策工具，股债跷跷板效应显现。四季度，10月初权益市场风险偏好 提升，整体收益率上行。伴随10月中旬权益市场回归震荡，债市恐慌情绪消退。11月，特朗普当 选下任美国总统，市场担忧25年贸易摩擦升级；增量财政政策细节公布，重点在于化债，年末两个 不确定因素落地后债市收益率稳步下行。11月下旬，地方债发行进入高峰期，央行加大对流动性的 投放以配合发债节奏，资金面总体平稳。月末非银同业自律倡议落地，短端带动收益率进一步下行。 12月，货币政策基调转为“适度宽松”，市场对于降准降息预期升温，年末抢跑行情提前启动，整体 收益率加速下行。 全年总体流动性合理充裕， DR007伴随公开市场降息稳步下降，四个季度均值分别为1.87%， 1.87%，1.81%，1.68%，略高于公开市场7天回购政策利率。 操作上，本基金坚持组合的风险收益特征，延续稳健的操作思路，根据市场变化灵活运用杠杆 和久期策略，主要配置短久期、中高等级品种，在严控组合信用风险和流动性风险的前提下为持有 人获取稳定回报，实现组合净值稳步增长。 4.4.2报告期内基金的业绩表现 本基金A类本报告期内的净值增长率为2.57%，同期业绩比较基准收益率为3.42%。 本基金C类本报告期内的净值增长率为2.37%，同期业绩比较基准收益率为3.42%。 本基金E类本报告期内的净值增长率为2.19%，同期业绩比较基准收益率为3.42%。 本基金F类自新增份额以来的净值增长率为0.60%，同期业绩比较基准收益率为0.97%。 | medium | 年报2024 §4 strategy_summary |
| manager_strategy_text | market_outlook | 国际方面，美国大选结果揭晓后外部环境不确定性增强，若美国对全球贸易伙伴均加征关税， 或促进中国在非美经济体的市场份额提升。欧央行、美联储虽已开启降息，但美国经济短期仍维持 韧性，叠加美国大选后财政、关税政策主张可能推升通胀，促使后续美联储降息节奏或放缓。 国内方面，预计 2025 年中国经济增长更注重质量和可持续性。政策对居民消费的扶持或延续。 在美国潜在关税政策下，整体出口或呈现前高后低的趋势。房地产方面，稳地产政策或继续推进， 第21页共70页 国泰利享中短债债券型证券投资基金2024年年度报告 地产销售降幅有望进一步收窄，但房价和地产投资的企稳仍面临商品房库存偏高、房企资金不足等 挑战，投资增速或继续底部徘徊。 债市正式进入“1%利率时代”，支持性的货币政策有望延续流动性宏观层面的“适度宽松”，总量 货币政策预计会持续发力，广谱利率仍有调降空间，流动性将保持充裕。 我们将采取稳健的投资策略，倾向于采用短久期、中高等级信用债的配置策略，辅以灵活的杠 杆策略、品种策略、波段操作等来增厚收益，坚持组合的风险收益特征，精细化管理组合，力求在 控制回撤的前提下提供持续稳定的组合净值表现。 | medium | 年报2024 §4 market_outlook |
| turnover_rate | — | — | — | 当前 slice 不处理 |
| manager_alignment | manager_holding | 项目 份额级别 持有基金份额总量的数量区间（万份） 本公司高级管理人员、基 金投资和研究部门负责人 持有本开放式基金 国泰利享中短债债券A 0  国泰利享中短债债券C 0~10  国泰利享中短债债券E 0  国泰利享中短债债券F 0  合计 0~10 本基金基金经理持有本开 放式基金 国泰利享中短债债券A 10~50  国泰利享中短债债券C 0~10  国泰利享中短债债券E 0  国泰利享中短债债券F 0  合计 10~50 | medium | 年报2024 §9 page-64 page-64-table-2 manager_holding |
| manager_alignment | employee_holding | 项目 份额级别 持有份额总数（份） 占基金总份额比例 基金管理人所有从业人员持 有本基金 国泰利享中短债债券A 1,415,888.97 0.02%  国泰利享中短债债券C 2,384,454.86 0.05%  国泰利享中短债债券E 0.00 0.00%  国泰利享中短债债券F 7,512.98 0.01%  合计 3,807,856.81 0.04% | medium | 年报2024 §9 page-64 page-64-table-1 employee_holding |
| holder_structure | institutional_holder | 44.56% | high | 年报2024 §9 page-63 page-63-table-1 institutional_holder |
| holder_structure | individual_holder | 55.44% | high | 年报2024 §9 page-63 page-63-table-1 individual_holder |
| holdings_snapshot | — | — | — | 当前 slice 不处理 |
| share_change | beginning_share | 7,699,969,800.13 | high | 年报2024 §10 page-65 page-65-table-0 share_change |
| share_change | ending_share | 5,711,224,267.09 | high | 年报2024 §10 page-65 page-65-table-0 share_change |
| share_change | net_change | -1,988,745,533.04 | high | 年报2024 §10 page-65 page-65-table-0 share_change |

---

## 001548 天弘上证50ETF联接A（国内股票类）

| field | sub_field | expected_value | confidence | source |
|---|---|---|---|---|
| basic_identity | fund_name | 天弘上证50交易型开放式指数证券投资基金联 接基金 | high | 年报2024 §2 page-5 page-5-table-0 fund_name |
| basic_identity | fund_code | 001548 | high | 年报2024 §2 page-5 page-5-table-0 fund_code |
| basic_identity | management_company | 天弘基金管理有限公司 | high | 年报2024 §2 page-5 page-5-table-0 management_company |
| basic_identity | custodian | 广发证券股份有限公司 | high | 年报2024 §2 page-5 page-5-table-0 custodian |
| basic_identity | inception_date | 2015年07月16日 | high | 年报2024 §2 page-5 page-5-table-0 inception_date |
| product_profile | investment_objective | 紧密跟踪标的指数，追求跟踪偏离度和跟踪误差的最 小化，本基金力争将日均跟踪偏离度控制在0.2%以 内，年化跟踪误差控制在2%以内。 | high | 年报2024 §2 page-6 page-6-table-1 investment_objective |
| product_profile | investment_scope | — | — | 当前证据不足，人工复核后补充 |
| product_profile | style_positioning | 本基金为ETF联接基金，且目标ETF为股票型指数基金，因此本基金的预期风险与预期收益高于混合型基金、债券型基金与货币市场基金。本基金主要通过投资于目标ETF实现对标的指数的紧密跟踪，具有与标的指数相似的风险收益特征。 | high | 年报2024 §2 page-6 page-6-table-0 style_positioning |
| benchmark | benchmark_name | 上证50指数收益率×95%＋银行活期存款利率（税后） ×5% | high | 年报2024 §2 page-6 page-6-table-0 benchmark |
| fee_schedule | — | — | — | 当前 slice 不处理 |
| classified_fund_type | fund_type | index_fund | high | 年报2024 §2 page-5 page-5-table-0 fund_name |
| nav_benchmark_performance | nav_growth_rate | -2.33% | high | 年报2024 §3 page-9 page-9-table-1 nav_growth_rate |
| nav_benchmark_performance | benchmark_return_rate | -2.40% | high | 年报2024 §3 page-9 page-9-table-1 benchmark_return_rate |
| investor_return | — | — | — | 当前 slice 不处理 |
| manager_strategy_text | strategy_summary | 本基金由原天弘上证50指数型发起式证券投资基金转型而来。 截至本报告期末，本基金主要持有天弘上证50ETF及指数成分股，仍采用被动复制 策略，其目标为跟踪效果与直接持有指数成分股的效果一致。 报告期内本基金秉承合规第一、风控第一的原则，在运作过程中严格遵守基金合同， 对指数基金采取被动复制的方式跟踪指数，追求基金净值增长率与基准指数间的高度正 相关和跟踪误差最小化。 出于基金充分投资、减少交易成本、降低跟踪误差的需要，基于谨慎原则，报告期 内本基金运用股指期货工具对基金投资组合进行管理。根据风险管理的原则，本基金在 报告期内运用股指期货工具旨在提高投资效率，控制基金投资组合风险水平，力求更好 地实现本基金的投资目标。 控制联接基金跟踪误差的前提是控制ETF基金的跟踪误差，报告期内，本基金跟踪 误差的来源主要是申购赎回、打新、成分股调整以及ETF对指数的跟踪误差。当由于申 赎等情况可能对指数跟踪效果带来影响时，本基金坚持既定的指数化投资策略，对指数 基金采取被动复制与组合优化相结合的方式跟踪指数。在ETF的跟踪误差管理上，我们 坚持指数化投资原则，同时紧密跟踪成分股的权息事件，及时有效处理，避免权重偏离 造成跟踪误差的扩大，争取保障联接基金的跟踪效果。 报告期内，本联接基金整体运行平稳。 第16页 天弘上证50交易型开放式指数证券投资基金联接基金2024年年度报告 | medium | 年报2024 §4 strategy_summary |
| manager_strategy_text | market_outlook | 2025年中国经济GDP增速目标可能维持在5%左右。尽管全球经济地缘政治的不确定 性增加，但中国经济基本面修复的弹性仍存，当前基建投资保持稳定，房地产市场的止 跌回稳初现迹象，消费修复依然是2025年的主要看点。政策方面，预计宏观政策基调整 体仍维持宽松，政策核心仍是稳增长。财政政策方面，预计2025年广义财政赤字率有可 能提升，货币政策适度宽松，降息和降准的概率仍然存在。 对股票市场而言，2025年仍然存在一定不确定因素，包括中美关系博弈、经济基本 面修复的成色、政策预期的波动等。短期来看，市场整体的情绪在年初偏保守防御，市 场关注的焦点在于美国关税政策和国内的政策应对，如两会的政策窗口期。中长期来看， 驱动股票市场表现更为核心的变量来自于经济基本面的实质改善，而在此之前，市场也 会重点关注稳增长政策的发力情况。因此2025年，我们认为股票市场与政策的联动性仍 然较高。我们认为2025年仍有政策窗口期值得期待，同时也期待基本面数据去验证政策 的实施效果。 | medium | 年报2024 §4 market_outlook |
| turnover_rate | — | — | — | 当前 slice 不处理 |
| manager_alignment | manager_holding | 项目 份额级别 持有基金份额总量的数量区间（万份） 本公司高级管理人员、基金投资和研究部门负责人持有本开放式基金 天弘上证50ETF联接A 0  天弘上证50ETF联接C 0  天弘上证50ETF联接Y 0  合计 0 本基金基金经理持有本开放式基金 天弘上证50ETF联接A 0~10  天弘上证50ETF联接C 0  天弘上证50ETF联接Y 0  合计 0~10 | medium | 年报2024 §9 page-76 page-76-table-2 + page-77 page-77-table-0 manager_holding |
| manager_alignment | employee_holding | 项目 份额级别 持有份额总数 （份） 占基金总份额比 例 基金管理人所有从业人员持 有本基金 天弘上证50ETF 联接A 131,120.15 0.01%  天弘上证50ETF 联接C 153,098.04 0.02%  天弘上证50ETF 联接Y 36,797.61 8.79%  合计 321,015.80 0.02% | medium | 年报2024 §9 page-76 page-76-table-1 employee_holding |
| holder_structure | institutional_holder | 12.40% | high | 年报2024 §9 page-75 page-75-table-1 institutional_holder |
| holder_structure | individual_holder | 87.60% | high | 年报2024 §9 page-75 page-75-table-1 individual_holder |
| holdings_snapshot | — | — | — | 当前 slice 不处理 |
| share_change | beginning_share | 980,186,937.75 | high | 年报2024 §10 page-77 page-77-table-1 share_change |
| share_change | ending_share | 909,956,981.34 | high | 年报2024 §10 page-77 page-77-table-1 share_change |
| share_change | net_change | -70,229,956.41 | high | 年报2024 §10 page-77 page-77-table-1 share_change |
