# 研究计划草稿技能计划审核记录

## 当前状态：r12 判决记录与保存校验已通过

## r12 判决记录与保存校验（2026-11-28）

用户 2026 年 11 月 28 日回看前几轮判决记录，指出四类误判（实验结果、选题成立与优先推荐被当成同一个判决；低优先级被写成不成立；测量出错时照样判活或判停；用弱证据判活却把分数写得很确定）与三处记录丢失（题面版本、判决范围、同版条件不同的报告），并给出五点要求：判决记录按题面版本分开、未评与 0 分分开、待补范围按研究问题确定、`problem_invalid` 锁定同一目标与假设、保存程序校验判决记录。用户明确表示只有改一处时会先改判决记录。

据此修订执行计划为 `rp-plan-r12-verdict-record-2026-11-28`，需求 `rp-requirements-r8-verdict-record-2026-11-28`，目标分支 `feat/verdict-record`，基线 `97c1340`（PR #8 合并后的 `main`）。独立审核者为专用 `plan_reviewer` 代理，只读，未修改文件、未运行测试。

**首轮**（候选 SHA256 `f8a48ace…541b6e`）结论 `NEEDS_MODIFICATION`，P1–P4 均有阻断项，共八项：
- B-01（P1、P4）：`evidence` 被同时写成“可为空数组”的三项之一，又要求按评分项判断非空；实际形态是与 `scores` 同键的对象。
- B-02（P2）：`id` 在保存内唯一与“按题面版本保留旧记录”直接冲突，同一候选多版本必然重复 `id`。
- B-03（P2、P3）：硬门槛项为「未评」时没有规定 `gate`，且计划两处对「未评是否进入排序」写法相反；这正是“未评变成第三道硬门槛”的入口。
- B-04（P2）：五问收窄只展开三类证明，第 4 问（真零假设下必然拒绝或必然不拒绝）没有归属。
- B-05（P3、P4）：既有不合规记录按下新校验无法继续保存，而 `materials` 是整对象覆盖，拒绝会连带挡住本轮合规材料；计划却把用户工作版的 `C1` 称为“正确形态”，推论不成立。
- B-06（P4）：RP-18 的 `$RP_R18_RUNTIME` 从未定义、`nix build` 无 `--out-link`、`PYTHONPATH` 会命中工作树源码而非运行包模块，该必测项不可执行且验证对象错误。
- B-07（P4）：用户要求“一次列出全部问题”没有观察点，测试设计还明确排除了多问题并存的提交。
- B-08（P4）：`summary` 字段凭空出现，不在字段清单、校验项与 RP-18 中。

作者按最小修正全部处理，并统一了三处口径：`experiment`、`missing` 为数组，`evidence` 与 `scores` 同键；`id` 为候选身份、`(id, statement_version)` 唯一、`merged_into` 指向身份；硬门槛项为「未评」时一律 `pending`、不得 `pass` 或 `soft_stop`，其余项「未评」不阻止排序但不同表比较。另新增「旧记录怎么继续保存」四条路径（拒绝时不写入、按 `gate` 补齐且 `hard_stop` 补不出真实停因就按实际判据改判、不想补齐可先不带 `candidate_scores` 保存材料步骤、不做隐式迁移）。

**复审**（候选 SHA256 `f094b8f5…50d9db`）结论 `NEEDS_MODIFICATION`，三项残留：
- R-01（P2）：校验清单第 2 条仍写「`id` 在本次保存内唯一」，B-02 只在别处改了口径。
- R-02（P4）：旧记录处理四条只写进计划，`candidate-scoring.md` 与 `runtime.md` 均无对应内容，用户仍只会看到报错。
- R-03（P4）：RP-18 的「上一份材料记录不受影响」没有用例。

作者逐条修正：第 2 条改为 `(id, statement_version)` 唯一；`candidate-scoring.md` 的「保存」节新增「被拒绝时怎么办」小节、`runtime.md` 的 `materials` 行同步；新增 `test_rejected_save_leaves_previous_materials_record_untouched`，逐字节比对上一份 `步骤-materials-*.json`。

**定向复核**（候选 SHA256 `8810fa4e…543de43`）结论 `APPROVED`：

```text
Plan revision: rp-plan-r12-verdict-record-2026-11-28
Requirement revision: rp-requirements-r8-verdict-record-2026-11-28
Target repository revision: research-proposal 分支 feat/verdict-record，基线 97c1340
Relevant upstream/runtime revision: N/A（RP-18 按当前工作树构建运行包）

P1 Requirement & Reality Grounding: PASS
P2 Solution Validity & Ownership: PASS
P3 Impact, Safety & Counterexample: PASS
P4 Executability: PASS
Gate review completeness: COMPLETE

Critical assumptions: N/A
Unresolved impacts: N/A
Approved behavior changes: 「未评」不参与总分、硬门槛项未评一律 pending；pending 增加四类触发情形；save_revision 对 candidate_scores 新增拒绝行为；拒绝后按四条路径处理、不做隐式迁移
Required modifications: N/A

Plan conclusion: APPROVED
```

审核者核对的五处一致口径：`(id, statement_version)` 唯一在 `plan/implementation-plan.md:446`、`plan/test-plan.md:230,235`、`references/candidate-scoring.md:156`、`_state.py:738-757` 五处一致，全文已无「id 在本次保存内唯一」；拒绝路径在 `candidate-scoring.md:365-372`、`runtime.md:92`、`_state.py:1003` 校验、加锁在第 1004 行、`(id, statement_version)` 类型判定与唯一键在第 738–757 行、首次 `write_record` 在第 1035 行、本步骤的 `_persist_work` 在第 1063 与 1073 行、状态版本递增在 `_store_state` 第 109 行、`test_verdict_record.py:150-170` 五处一致。审核者另确认校验调用早于 `_locked` 与写入，因此「不落盘、状态版本不变」在实现上成立。

非阻断观察两项已处理：第 448 行的「见下」改为具名指向「旧记录怎么继续保存」；`pass` 带非空 `missing` 属允许形态，不改。第三项（`assertNotIn` 用序列化文本子串匹配）作为失败提示足够，保留。

**实现符合性审核触发的一处语义修订（IR-01）**。首轮实现符合性审核指出：交付文档里「空白成因 0 有两种」与计划/新节「0 分只留给有依据的否定」并存，同一情形两套记法；按旧写法“还没查够三篇”记 0 时，`空白成因 = 0` 与 `hard_stop`/`gap_zero` 仍可入库，正是本轮要消除的“没查齐→判停”。

需求裁定人按用户原话“证据未齐记未评、0 留给有依据的否定”裁定：**空白成因的 0 分收窄为“已证伪”，一种来源、两种情形**（伪空白；查证后确认没有相近工作），“还没查够三篇”改记「未评」并按 `pending` 处理。这条同时收窄了原先“九项 0/1/2 判据不变”的范围：2 分与 1 分判据不变，0 分的适用情形收窄。计划与测试计划相应修订，交定向复核。

**定向复核（R-04，SHA256 `75121892…efe227f`）**：结论 `NEEDS_MODIFICATION`，指出澄清引入「伪空白」的三套定义（第 41、62、129 行），「查证后确认没有相近工作」这一情形在 `gap_zero` 未覆盖时没有合法 `gate`。作者按审核首选方案统一为“一种来源、两种情形”，同步第 41、62、94、108、129、207 行与两份计划；并按审核建议在执行计划补「校验边界」一句（校验可覆盖 `candidate-scoring.md` 既有评分与字段规则，超出既有规则的新增拒绝项须另行批准），对 IR-02 选择保留更严校验而非收窄。

**最终定向复核（SHA256 `3891b47c…b4e0a3d`）**：结论 `APPROVED`。

```text
Plan revision: rp-plan-r12-verdict-record-2026-11-28
Requirement revision: rp-requirements-r8-verdict-record-2026-11-28
Target repository revision: research-proposal 分支 feat/verdict-record，基线 97c1340
Relevant upstream/runtime revision: N/A

P1 Requirement & Reality Grounding: PASS
P2 Solution Validity & Ownership: PASS
P3 Impact, Safety & Counterexample: PASS
P4 Executability: PASS
Gate review completeness: COMPLETE

Critical assumptions: N/A
Unresolved impacts: N/A
Approved behavior changes: 空白成因 0 分收窄为“已证伪”（一种来源、两种情形），还没查够三篇改记「未评」并按 pending；「未评」不参与总分、硬门槛项未评一律 pending；pending 增加四类触发情形；save_revision 对 candidate_scores 新增拒绝行为；拒绝后按四条路径处理、不做隐式迁移
Required modifications: N/A

Plan conclusion: APPROVED
```

审核者核对六处同一定义：第 41、62、94、129 行属定义与引用，第 207 行是否定用法；全文 `伪空白` 命中 6 次，无第二套外延。并确认「查证后确认没有相近工作」现在能合法落到 `hard_stop` + `gap_zero`：分数记 0 而非 `null`，不受“未评须 pending”限制；硬门槛命中不得 `pass`/`soft_stop`；`gap_zero` 已覆盖该情形；校验只要求 `stop_reason` 取三个枚举之一，不会误拒。上一版“无合法 `gate`”的空档已消除。

非阻断观察已处理：r7 历史小节的 `gap_zero` 一行加「（r12 已收窄，见下文 r12 的「空白成因的 0 分收窄」条）」括注，避免被误引为现行规范。`research-design.md` 第 91、117 行的「伪空白」与第 41 行定义相容，属 r12 未触碰的既有文本，不改。

本结论覆盖 `3891b47c…b4e0a3d` 与 `4aae7a25…7b8144`；其后仅按非阻断观察加了一处括注（当前计划 SHA256 `a49343891cef7828ab5013be5aa86b7d9c5ab7ac8dde343d9f6ac7bb21f49688`），不触及 P1–P4 判断，按 Plan Reviewer Rule 第 6.3 节属等价局部修正，沿用 `APPROVED`。结论不代替测试第二、第三关口与合并批准。

## 当前状态历史：r11 方向判决口径已通过

## r11 方向判决口径（2026-11-27）

用户 2026 年 11 月 27 日就“一个方向还能不能继续做”提出四处缺口：判决词与停因没有闭集、待补与负结果没有落盘位置、证据进来之后没有改判规则、判决前缺少证据门槛。评估结论是四处都是现有规则未覆盖的真实缺口：`candidate-scoring.md` 只有两条硬门槛且唯一一条“不要因为 1 分判死”只针对准备档位（第 66 行），`gate` 只有 `pass`、`hard_stop`、`soft_stop` 三态（第 234 行）；`research-design.md` 对“证据推翻当前问题或方法”只有一句“返回受影响步骤调整和确认”（第 30 行）。据此修订执行计划为 `rp-plan-r11-verdict-2026-11-27`，需求 `rp-requirements-r7-verdict-2026-11-27`，目标分支 `feat/verdict-gate`，基线 `56369ad`（PR #7 合并后的 `main`）。独立审核者为专用 `plan_reviewer` 代理，只读，未修改文件、未运行测试。

**首轮**（候选 SHA256 `82f5db25…ec46e`）结论 `NEEDS_MODIFICATION`，两项 blocker：
- B-01（P2，连带 P3）：计划要求 `problem_invalid` 判停后“把新意落点或空白成因记 0”，但保留的 0 分判据只覆盖“四项都没有变化”和“伪空白/缺三篇”，不可识别与检验恒真并不必然使这两项为 0；该停因因此可能没有 0 分依据，却被“不允许 1/1/1 而停”禁止按实际记录。
- B-02（P3）：反例写“九项里七项 1 分、两项 2 分（总分 75）”，按保留公式最高只能 65，与“评分公式不变”矛盾。

作者按最小修正处理，并取得验收决定人两项确认：`problem_invalid` 只写 `stop_reason`、分数按既有判据照实记（B-01）；`pending` 增加第二触发条件“推荐所依赖的关键项只有摘要级证据”（审核观察 3）。反例改为“五项 2 分、四项 1 分（2 分项权重合计 50，总分 75）”。另按非阻断观察把“相对指代只有三处”改为“需要检查的三处”、把对称规则写成追加到「先过门槛，再算总分」末尾、把软门槛旧词“待补”改称“备选”、给 `merge` 固定 `merged_into`。

**第二轮复核**（候选 SHA256 `729d01fd…fbaa`）确认 B-01、B-02 正文已闭合，另提三项 blocker：
- R2-01（P3）、R2-02（P3）：文末第 443 行仍是旧反例“七项 1 分、两项 2 分（75 分）”与“恒等式判停时评分表须按事实记 0”，与正文第 400、422 行冲突，两项均未完全闭合。
- R2-03（P2，连带 P3/P4）：`pending` 第二触发条件与「推荐怎么写」第 180 行“补不了就把领先项从推荐理由里去掉”给出不同后果，“推荐所依赖的关键项”也未定义。

作者修正：文末摘要与正文逐字对齐；把“推荐所依赖的关键项”写死为“推荐语第 2 句点名的领先项”，写明新触发条件取代第 180 行那条保留总分与排序的路径，并把「推荐怎么写」列入改动点；`items` 字段清单补 `stop_reason` / `merged_into`；软门槛补法改为“按备选处理”。

**第三轮复核**（候选 SHA256 `b97d6341…ad68`）确认 R2-01、R2-02、R2-03 闭合，未发现新 blocker，结论 `APPROVED`。四条非阻断建议（改动计数措辞、“末段”改为第 180 行段末、反例补新触发条件情形、多项领先项口径）作者在批准后作为无判据变化的措辞与清单补全并入，计划文本更新为 SHA256 `c28fd0bc…a4843b`；未改停因、`gate` 枚举、字段名与改动范围。

```text
Plan revision: rp-plan-r11-verdict-2026-11-27
Requirement revision: rp-requirements-r7-verdict-2026-11-27（含 2026-11-27 审核问答两项追加：problem_invalid 只写 stop_reason；pending 第二触发条件）
Target repository revision: research-proposal 分支 feat/verdict-gate，基线/HEAD 56369ad（PR #7 合并后的 main）；源码 skills/research-proposal/
Relevant upstream/runtime revision: N/A（本次只改仓库内参考文档；固定依赖未变）
Candidate SHA256: b97d634138c0b094e67b3c1e6d41c9ef2515b0bd05a3e24bf6d29ae66741ad68（APPROVED 版本；其后仅措辞与清单补全，现为 c28fd0bcb8c7551ff8334dc9cf57903837a49bb25b4a6ec46e6f85e417a4843b）
P1 Requirement & Reality Grounding: PASS
P2 Solution Validity & Ownership: PASS
P3 Impact, Safety & Counterexample: PASS
P4 Executability: PASS
Gate review completeness: COMPLETE（首轮全量检查 r7 四处新增与连带引用；第二、三轮只复核 B/R2 修正及直接影响）
Critical assumptions: N/A
Unresolved impacts: N/A
Approved behavior changes: 五个判决词与 gate 一一对应；problem_invalid 只写 stop_reason、分数照既有判据记；pending 两个触发条件（三篇不足、推荐语第 2 句点名的领先项只有摘要级证据）；负结果与边界题可推进；merge 与 merged_into。来源 rp-requirements-r7-verdict-2026-11-27 与用户 2026-11-27 审核问答
Reused prior Plan Gate PASS: r10 的 P1–P4（37a0c8be…）用于未被 r7 触及的组件接口、状态字段、依赖、安装、交付与提交条款；r11 首轮的 P1 用于未变化的事实基础；P2、P3、P4 因 R2 修正重新检查
Required modifications: N/A
Missing evidence for PARTIAL review: N/A
Plan conclusion: APPROVED
```

本结论只表示当前方案适合实施，不表示实现正确、测试通过或可以合并；测试计划与合并审核由对应关口负责。

## r10 教授方向对齐（2026-11-27）

用户 2026 年 11 月 27 日就“研究方向怎么和教授对齐”提出三处缺口，要求先判断是否需要更新技能：研究室“轴”的判断方法（缺口 A）、学术脉络定位（缺口 B）、多课题点合并（缺口 C）。评估结论是三处都是现有规则未覆盖的真实缺口：`candidate-scoring.md` 的「范围连接」只有主线 2／邻近 1／无关 0 三档，判据是“教授近年论文或学生论文在做的问题”，不含指标组；`research-design.md` 的「空白成因」查的是同一层级的三篇最接近工作，给不出换层重新定位的动作；撞车一节的四种切口不含“把多个已承认缺口合并成一次解决”。据此修订执行计划为 `rp-plan-r10-direction-alignment-2026-11-27`，需求 `rp-requirements-r6-direction-alignment-2026-11-27`，目标分支 `feat/direction-alignment`，基线 `61257df`（PR #6 合并后的 `main`）。独立审核者为专用 `plan_reviewer` 代理，只读，未修改文件、未运行测试。

**首轮**（候选 SHA256 `a42fe942…`）结论 `NEEDS_MODIFICATION`，两项 blocker：
- R-01（P2，连带 P4）：`candidate-scoring.md` 的授权改动集自相矛盾。「三种常见打错」只存在于该文件，但计划把它写在以 `research-design.md` 为对象的段落里，未指名文件；同段又写该文件“只在「范围连接」末尾加一行指针”，变更清单未列该项，实现者须临场决定改哪个文件、改几处。
- R-02（P3）：新增「学术脉络怎么定位」插在「新颖性写在哪里」之后，会使 `research-design.md` 现有的“完全没有相近先行研究是危险信号，理由见上一节”指向错误——该“上一节”目前指「新颖性写在哪里」，插入后落空。

作者按最小修正处理：第 388 行指名 `candidate-scoring.md`、要求「三种常见打错」加第 4 条并同步改名为「四种常见打错」、统一计数，并把该文件本轮改动限定为两处；第 400 行变更清单补入；第 382 行的“只在”限定改为只针对轴节。第 384 行写明插入会改变指代、须把该句改为具名指向「新颖性写在哪里」，并列入变更清单。首轮的非阻断观察一并处理：把“第五种安全做法”改为“四种切口之外的安全做法”并写明不计入切口计数；把原文无逐字对应的引号引用改为间接表述；消解“r6”在旧计划修订号与本次需求号之间的歧义；补“稳定报告”的可判断口径、非计算类学科的同一原则、适用范围边界与入口归属。

**第二轮复核**（候选 SHA256 `4884f4d2…`）确认 R-01、R-02 均已闭合，另提出两项新 blocker：
- B-01（P1，连带 P3）：需求记录写“数该脉络里已有多少工作”，计划正文却改成“只作定性判断，不数篇数”，同一计划对同一已确认要求给出相反义务。
- B-02（P3，连带 P2）：计划让轴判断“决定「范围连接」权重”，与 `candidate-scoring.md` 的既有规则冲突——该权重默认 0，只在用户明确要求把“导师能不能带”纳入比较时才调整；这会把权重的 owner 从用户移到新节。

作者修正：第 384 行恢复数量义务（写明已有多少工作，给篇数或量级），并写明“说明规模”不是新的停止条件，阅读篇数不设上限、不按固定篇数停手，r5 的篇数口径不变；第 382 行改为“作为判断「范围连接」2/1/0 的输入”，权重仍默认 0、只在用户明确要求时调整，该节不自行启用或提高权重。另按非阻断观察补了“篇名属于对用户分析输出的要求，不写进技能文档正文”的半句。

**第三轮复核**（候选 SHA256 `37a0c8be…`）确认 B-01、B-02 闭合，未发现新矛盾，结论 `APPROVED`。两条非阻断措辞建议（影响记录补「范围连接」默认权重规则、正文补“三篇是最低证据不是阅读上限”）作者评估后**未采纳**，理由是 `APPROVED` 已按 `37a0c8be…` 给出，采纳会使计划正文脱离被批准文本；这两点已分别由 `candidate-scoring.md` 的第 58–60 行与第 202、210 行原文生效，无需在新计划里复述。计划正文保持在 `37a0c8be…`。

```text
Plan revision: rp-plan-r10-direction-alignment-2026-11-27
Requirement revision: rp-requirements-r6-direction-alignment-2026-11-27
Target repository revision: research-proposal 分支 feat/direction-alignment，基线/HEAD 61257df（PR #6 合并后的 main），源码 skills/research-proposal/
Candidate SHA256: 37a0c8be6c93edd9d188c1c78f1f05731ee771fddb1a7f2ae95b3da253e6e742
P1 Requirement & Reality Grounding: PASS
P2 Solution Validity & Ownership: PASS
P3 Impact, Safety & Counterexample: PASS
P4 Executability: PASS
Gate review completeness: COMPLETE（首轮全量检查 r6 三处新增与直接连带的既有文档引用；第二、三轮只复核 B-01、B-02 及修正的连带影响）
Critical assumptions: N/A
Unresolved impacts: N/A
Approved behavior changes: 新增研究室轴判断、学术脉络定位、多课题点合并三项写作与面试判断，并在 SKILL.md、interview.md、candidate-scoring.md 的相关入口接入；不新增评分项、不改九项权重、两项硬门槛、评分公式、「范围连接」2/1/0 判据（来源：rp-requirements-r6-direction-alignment-2026-11-27，用户 2026-11-27）
Reused prior Plan Gate PASS: P2、P4 复用第二轮对 4884f4d2… 的 PASS；第三轮只改第 382、384 行措辞，未触及核心方案、owner、change point、接口、状态、依赖与交付路径。r9 关于组件接口、状态字段、依赖、安装、交付与测试口径的结论未受本次文档增补影响，不作重新审核
Required modifications: N/A
Missing evidence for PARTIAL review: N/A
Plan conclusion: APPROVED
```

本结论只表示当前方案适合实施，不表示实现正确、测试通过或可以合并；测试计划与合并审核由对应关口负责。

## r9 撞车评分映射与篇数上限（2026-11-26）

用户 2026 年 11 月 26 日追加两点：评估评分细则是否需要新增维度；去掉“五篇左右”的篇数上限。评估结论是不新增第十个评分项，改为在 `candidate-scoring.md` 增加撞车类型到既有评分项的映射；三步诊断改为篇数不设上限。执行计划为 `rp-plan-r9-collision-scoring-2026-11-26`，需求 `rp-requirements-r5-collision-scoring-2026-11-26`，目标分支 `feat/collision-guidance`，基线 `8032701`，当前 head `1bddb0c`。独立审核者为专用 `plan_reviewer`，只读，未修改文件、未运行测试。

首次审核提出 P3-01：新映射把方法置换、对象置换、同结论不同路径统一写成“按 1 分”，并给方法置换增加“多回答什么”，比既有「空白成因 1 分」的方法判据更严，属于改变评分判据而不是映射。计划作者改为“只说明落到哪一项，不重述、不收紧判据”，映射表按既有判据引用，不固定分数、不新增条件；计划第 373、396 行同步写明九项权重、两项硬门槛和九项 0/1/2 判据不变，第 396 行另写评分公式不变。复审 P3-01 关闭，结论 `APPROVED`。

```text
Plan revision: rp-plan-r9-collision-scoring-2026-11-26
Requirement revision: rp-requirements-r5-collision-scoring-2026-11-26
Target repository revision: research-proposal 分支 feat/collision-guidance，HEAD 1bddb0c，基线 8032701
Candidate SHA256: d49b9135a67acda9a5442f173e28566e4d21d763c5e919827040c09ea288966c
P1 Requirement & Reality Grounding: PASS
P2 Solution Validity & Ownership: PASS
P3 Impact, Safety & Counterexample: PASS
P4 Executability: PASS
Gate review completeness: COMPLETE（r9 修正及直接影响；r8 未触及条款复用）
Critical assumptions: N/A
Unresolved impacts: N/A
Approved behavior changes: 不新增第十个评分项；candidate-scoring.md 增加撞车类型到既有评分项的映射；去掉“五篇左右”，改为篇数不设上限；九项权重、两项硬门槛、评分公式和九项 0/1/2 判据不变
Reused prior Plan Gate PASS: r9 的 P1、P2、P4；P3 原残留已由第 396 行修正关闭
Required modifications: N/A
Missing evidence: N/A（测试计划与执行不在本轮范围）
Plan conclusion: APPROVED
```

本结论只表示当前方案适合实施，不表示实现正确、测试通过或可以合并。

## r8 撞车判断文档增补（2026-11-26）

用户 2026 年 11 月 26 日要求在技能中增加一节“研究方向撞车”的判断标准和建议，只改文档，不改产品接口、状态、依赖和交付行为。执行计划改为 `rp-plan-r8-collision-2026-11-26`，需求为 `rp-requirements-r4-collision-2026-11-26`，目标为分支 `feat/collision-guidance`、基线 `8032701`。独立审核者为专用 `plan_reviewer` 代理，只读审核计划修订及直接影响，未修改文件、未运行测试。

首次审核（候选 SHA256 `984e3b23fcd5cec08f6291601b6a0936866208e4cfa6ed0e28109af3b0a9b7b3`）结论为 `NEEDS_MODIFICATION`，提出四项阻塞：面试三句只从研究步骤可达；新节与既有新颖性、空白成因评分、矛盾处理规则没有优先级；计划未写隐私边界；未把保留行为和本次获批变化记全。计划作者据此修订为 r8，并在第 366、368、382、391 行补入面试指针、诊断层兼容说明、隐私禁止项和保留行为；复审结论为 `APPROVED`。

复审后按非阻断文案建议修正四处（断链、措辞、范围摘要、状态措辞），候选 SHA256 变为 `18113696a3a292d33ee7adf19be8edcee1de30a867b53c16a2d474b29c646ab6`。审核者确认这四处只涉及文案、指针和路径，未改变需求、owner、change point、保留行为、隐私边界或测试范围，原 `APPROVED` 继续适用，不需要重开 P2/P3。

```text
Plan revision: rp-plan-r8-collision-2026-11-26
Requirement revision: rp-requirements-r4-collision-2026-11-26
Target repository revision: research-proposal 分支 feat/collision-guidance，HEAD 8032701（PR #5 合并后的 main）
Candidate SHA256: 18113696a3a292d33ee7adf19be8edcee1de30a867b53c16a2d474b29c646ab6
P1 Requirement & Reality Grounding: PASS
P2 Solution Validity & Ownership: PASS
P3 Impact, Safety & Counterexample: PASS
P4 Executability: PASS
Gate review completeness: COMPLETE（r8 修正及直接影响；r6 未触及条款复用）
Critical assumptions: N/A
Unresolved impacts: N/A
Approved behavior changes: 在研究设计中增加撞车判断，并在 SKILL.md 相关研究步骤与 interview.md 三类追问末尾接入；来源 rp-requirements-r4-collision-2026-11-26
Reused prior Plan Gate PASS: P1、P4 复用 r7 的结论；P2、P3 针对 r8 修正重新检查后 PASS
Required modifications: N/A
Missing evidence: N/A（测试计划与执行不在本轮范围）
Plan conclusion: APPROVED
```

本结论只表示当前方案适合实施，不表示实现正确、测试通过或可以合并；测试计划与合并审核由对应关口负责。

## r4 第 177 行依赖基线的文字更正（不升版）

2026 年 11 月 24 日，`flake.nix` 改为顶层声明 `nixpkgs`、`agent-env-nix` 与 `professor-contact` 三个输入（原先只声明 `professor-contact`，另两项经其转借），使使用方可以对这三个输入写 `follows`。计划第 177 行原文「新仓库只新增一个直接的上游 flake 输入」随之与实现不符，已改为按实际三输入表述，并补回 `contact` 简写指代 `professor-contact`。

按 `Plan Reviewer Rule.md` 中「纯 rename、format、review metadata 或等价局部重构无需 amendment」的范围，本次只更正对现有实现的文字描述：需求、方案、owner、机制、接口语义、兼容要求、失败处理与必测范围均未变化；四个构建输出与更正前逐字节相同（`msvk71zx…` runtime、`3a95vpr8…` package、`cnskyah9…` environment、`7576fsl5…` activate），已由实现方与独立审核分别求值确认。因此不提高计划修订编号，`Plan revision` 仍为 `rp-plan-r4-markdown-2026-11-04`。

更正后计划 SHA256 为 `d5a5777e12cf0972473b8779b499497f0ea56f78c6b9118971b747f15422f2b2`。本记录此前各节的 `4776b1d7…` 是更正前正文的校验值，作为当时审核对象保留；当前有效正文以本节记录的最新校验值 `d5a5777e…` 和仓库实际文件为准，r4 的 P1–P4 批准结论及未受影响范围的复用不变。`plan/test-plan.md` 第 9 行与 `plan/test-results.md`、`plan/implementation-review.md` 中对 `4776b1d7…` 的引用同属更正前校验值，指的都是同一份 r4 计划；本次不修改这些文件中的该引用，以免为纯文字更正产生不必要的连锁校验值变化。若后续再改需求、方案、接口语义或必测范围，仍按原规则重开受影响关口。


2026 年 11 月 4 日，用户明确撤掉 LibreOffice 测试，Word 交付和调试延后，先完成 Markdown。完整候选已合入 [implementation-plan.md](implementation-plan.md)，版本 `rp-plan-r4-markdown-2026-11-04`，需求 `rp-requirements-r2-markdown-2026-11-04`，SHA256 `4776b1d75a6763608a788166e0aa74719ac9c88c0bf2ae5459c66a17b35b5f9a`。独立审核者为专用 `plan_reviewer` 代理，只读审核完整候选 344 行及本轮变化与直接影响，未修改文件、未运行产品或测试。主对话已核对其依据、覆盖范围和最终校验值，审核前后计划 SHA256 不变。

本次变化来自用户主动精简，无需证明旧 Word 方案错误。当前不执行 Word、页面或 LibreOffice 调试；旧核对要求不覆盖用户的新决定。下文 r3 批准记录保留为历史及未受影响方案的依据。

```text
Plan revision: rp-plan-r4-markdown-2026-11-04
Requirement revision: rp-requirements-r2-markdown-2026-11-04
Target repository revision: feat/research-proposal，文档基线 1b6c462b23e5bc736d80ba15fa7a2106643ebfbd（产品基线 b983497308157dedec6b4d97f16c95dc0b0f60f9）
Candidate SHA256: 4776b1d75a6763608a788166e0aa74719ac9c88c0bf2ae5459c66a17b35b5f9a
P1 Requirement & Reality Grounding: PASS
P2 Solution Validity & Ownership: PASS
P3 Impact, Safety & Counterexample: PASS
P4 Executability: PASS
Gate review completeness: COMPLETE（完整候选 344 行及本轮 Markdown 交付变化、直接影响）
Critical assumptions: N/A
Unresolved impacts: N/A
Approved behavior changes: 当前只交付 Markdown；Word 导出、学校表格填入、LibreOffice 预览与页面核对延后，不作为本轮完成条件（来源：用户 2026-11-04 指令，计划第 7、342 行）
Reused prior Plan Gate PASS: P1/P2 中未受本次变化影响的既有事实（上游前置顺序、依赖固定值、材料读写、两处用户决定）沿用 r3 已核结论；P3/P4 按完整候选重新核对
Required modifications: N/A
Missing evidence: N/A（只读检查边界见下文，不影响结论）
Plan conclusion: APPROVED
```

### 审核核对的关键现状事实

审核者独立复算了本计划依赖的 b983 事实，结论与计划一致：`_state.py` 第 637–639 行直接取 `request["page_review"]` 并校验 `passed` 与 `notes`；`_documents.py` 第 502–508 行计算 `pages_ok`；`_commit_problems` 第 675、678、685 行分别要求 `docx` 步骤、`pages_ok` 及 `docx`/`preview_pdf`/`page_images`；`STAGES`（第 26 行）含 `docx`，`_next_steps`（第 417–418 行）遍历它，故“下一步”会把 Word 列为未完成。`export_revision`（第 585–586 行）与 `export_documents`（第 333–334 行）确实只校验非空子集，`["md"]` 可通过；但第 346–368 行在 `template_path`／`mapping` 存在时仍走模板分支，所以“仅 md 独立于模板”确需改代码。审核者另用 `git diff b983 1b6c462 -- skills/ nix/ flake.nix flake.lock` 确认两基线之间产品代码未变，计划并列两个基线不矛盾；依赖固定值与 `flake.lock` 各节点 `locked.rev` 一致。

### 非阻断观察

审核者列出若干证据位置偏差，均不影响设计判断，不要求修改、不作为通过条件：计划第 338 行 `_documents.py#L387` 指的是导出循环行，允许 md 子集的校验实际在第 333–334 行；`_state.py#L652` 支撑“核对要求 docx+md”，而提交／下一步／指纹分别在第 675、685 行与第 26、417 行。第 310、312 行 `artifacts.md` 是点记法，易被读成文件名，但实现不歧义。第 257 行“篇幅”若以页数表达，Markdown 阶段无法逐页核实，属已批准延期范围，实现时把页数类限制记为待确认。第 230、239 行运行包仍保留 `libreoffice-bin`，用户要求是撤掉用它做测试，不是移除依赖。

### 只读检查边界

Q6–Q16 原始决定清单不在仓库内，本轮变化的权威是用户 2026-11-04 原话（计划第 7 行逐字引用），未改部分复用 r3 已批准记录。既有未提交稿“已保存问题、方案与正文”的判断取自 [test-results.md](test-results.md) 中的 `paper-04`、`nonpaper-03` 记录（状态 9／10、`current=null`），按已认可方法产生，直接采用。本轮未执行构建、安装、测试或任何产品调用，未审核测试计划、实现符合性与合并条件。

## 实施前的发布信息整理

2026 年 11 月 3 日，首次提交前移除本机用户名、私人参考文件路径和具体临时目录名；既有上游链接改为同一固定版本的公开链接或工作区相对引用，并去除文件末尾多余空行。需求、接口、数据字段、实现顺序、失败处理与必测范围均未改变，`Plan revision` 仍为 r3。依据计划规则第 6.3 节，复用下文 P1–P4 的批准结论，不为路径和校验值变化重做方案审核或测试。

当前计划 SHA256 为 `edf6692023be0e717ff454482c10763cc74c42885cc41ea8458fd1915fb69bcf`；整理前已审 SHA256 为 `963e3c8a83d6bc2196ecff3382861eb6b139481c00f22483ebbe598bf060864e`。具体本地准备路径继续由仓库外受控交接提供。

## 历史结论：r3 接口约定补充

2026 年 11 月 3 日，用户明确：产品尚未实现也可以先准备测试 Recipe，入口与用法应与执行计划规定要实现的一致。计划作者补齐安装用法、主技能与组件的公开调用，以及材料和稿件状态的必要字段；原独立审核者 `/root/plan_plugin_review` 使用 `personal-code-review:review-execution-plan` 对这些补充及直接影响完成只读复核。

当前完整计划为 [implementation-plan.md](implementation-plan.md)，`rp-plan-r3-2026-11-03`。结论为 **APPROVED**；主对话已核对返回意见、覆盖和最终校验值。没有执行产品实现、构建、安装或测试，本结论不代替第二测试关口。

```text
Plan revision: rp-plan-r3-2026-11-03
Requirement revision: rp-requirements-2026-11-02-q6-q16
Target repository revision: feat/research-proposal，尚无提交
Candidate SHA256: 963e3c8a83d6bc2196ecff3382861eb6b139481c00f22483ebbe598bf060864e
P1 Requirement & Reality Grounding: PASS
P2 Solution Validity & Ownership: PASS
P3 Impact, Safety & Counterexample: PASS
P4 Executability: PASS
Gate review completeness: COMPLETE（本次补充、修正及直接影响）
Critical assumptions: N/A
Unresolved impacts: N/A
Required modifications: N/A
Missing evidence: N/A
Plan conclusion: APPROVED
```

初次补充候选 `2d79011d18cc7a3e1c9054a95462c67c0c383c422161765703c30898dcfd6413` 的受影响范围检查已完成。P1、P2 通过；P3、P4 发现一项缺口：创建与恢复可能写状态，却没有统一要求版本基准。修正后，两个入口都声明 `expected_state_version`；首次创建使用 `null` 并在锁内确认状态不存在，既有稿和恢复读取正式状态的当前版本，过期请求返回冲突。工作版本还要核对提交基准，已提交的同一修订只重报结果。原代理仅复核该修正及连带影响，问题已关闭。

安装命令及激活器命名已对照固定 `agent-env-nix@c368871942435bdc178a1063ce9c677acaf8cabc` 源码；新增组件接口用于主技能实际业务，没有新增测试专用开关、独立服务或业务要求。未实现的产品提交和运行生成物属于实施顺序，不构成设计缺陷。

P1、P2 复用本轮初次补充检查；P3、P4 采用修正复核。r2 中未变化的论文前置顺序、原代理职责、固定依赖、材料范围、两处用户决定、模板处理、统一正文及双格式提交顺序继续复用此前结论，不重新审核。以下 r2 内容只保留为历史记录。

## 存放位置更正

2026 年 11 月 3 日，用户指出计划应放在对应仓库的开发工作树中。此前计划仍在总目录，目标仓库也尚未建立；历史记录把“以后迁入”以及“用户提供文件路径”视为允许暂存的依据，这个判断不成立，现予更正。

本地仓库 `research-proposal` 及 `feat/research-proposal` 开发工作树现已建立。唯一完整计划是本工作树的 [plan/implementation-plan.md](implementation-plan.md)，本文件为同目录的审核记录；总目录原文件只保留链接入口。

本次只更正存放位置、仓库建立状态和相关链接；业务要求、依赖版本、组件职责、失败处理和实施顺序均未改变，`Plan revision` 保持 `rp-plan-r2-2026-11-02`。

原审核者 `/root/plan_plugin_review` 已只读复核 Git 归属、完整文件差异和入口链接，并撤回此前的位置豁免判断。主工作树为 `main`，开发工作树为 `feat/research-proposal`，共用 Git 目录指向 `research-proposal/.git`；两个分支均尚无提交，计划及审核记录当前为本地未提交文件。

| 关口 | 位置更正后的结论及复用范围 |
|---|---|
| P1 | 仓库状态和计划位置重新核对通过；此前业务事实结论复用。 |
| P2 | 方案及职责未变，复用此前 PASS。 |
| P3 | 兼容、状态、失败处理和副作用边界未变，复用此前 PASS。 |
| P4 | 当前位置符合目标仓库 `plan/` 要求；实施第一项只移除已完成的建仓、迁移动作。位置部分重新核对通过，其余结论复用。 |

```text
Plan revision: rp-plan-r2-2026-11-02
Requirement revision: rp-requirements-2026-11-02-q6-q16
Target repository revision: feat/research-proposal，尚无提交
Current candidate SHA256: 2241a5e7c992b93b838c8755464546a897501b1ac7fc6634fab45291e91adfb5
Prior reviewed candidate SHA256: 0ca6dd97b6cf45d9c02debe3dc6fcbc5860157c3839c1a4cf3f687d0c8f8c77e
P1: PASS
P2: PASS
P3: PASS
P4: PASS
Gate review completeness: COMPLETE（本次迁移及直接影响）
Required modifications: N/A
Missing evidence: N/A
Plan conclusion: APPROVED
```

当前结论指向迁移后的计划及上述新校验值。按计划规则第 6.3 节，此次不提高计划修订编号，也不重新审核未变化的业务方案。本次未执行构建或测试。以下保留迁移前的审核记录、校验值和行号，其中关于暂存总目录获准的判断已由本节撤回。

## 本轮完整计划审核

审核日期：2026 年 11 月 3 日。

用户本轮明确要求另开子代理，使用已安装的 `personal-code-review:review-execution-plan` 技能（插件版本 `1.1.0`）审核计划，再根据返回判断是否修改。审核者为未参与编写的 `/root/plan_plugin_review`；以下转存其结论。主代理核对了覆盖范围和最终文件校验值，未修改计划正文。

审核对象：[研究计划草稿技能执行计划](implementation-plan.md)，覆盖迁移前候选第 1–314 行。此次审核覆盖完整候选，没有使用前次三项修订的通过结论代替完整检查。该次结论为 **APPROVED**，必须修改项为 **0**。

```text
Plan revision: rp-plan-r2-2026-11-02
Requirement revision: rp-requirements-2026-11-02-q6-q16
Target repository revision: research-proposal 尚未建立，无产品提交
Candidate SHA256: 0ca6dd97b6cf45d9c02debe3dc6fcbc5860157c3839c1a4cf3f687d0c8f8c77e

P1 Requirement & Reality Grounding: PASS
P2 Solution Validity & Ownership: PASS
P3 Impact, Safety & Counterexample: PASS
P4 Executability: PASS
Gate review completeness: COMPLETE

Critical assumptions: N/A
Unresolved impacts: N/A
Approved behavior changes: N/A；本轮落实已确认要求
Reused prior Plan Gate PASS: N/A
Required modifications: N/A
Missing evidence for PARTIAL review: N/A

Plan conclusion: APPROVED
```

审核者独立读取了指定技能、其引用的三份 Notion 正文，以及工作区的共识、计划、测试和 Nix 规则，未发现影响本案判断的规则冲突。计划暂存在当前文件是用户指定的安排；计划第 11 行要求建仓时迁入唯一的 `plan/implementation-plan.md`。

| 关口 | 已检查内容与判断 |
|---|---|
| P1 | 已确认要求、非目标、平台及安装边界明确。原始 `RP.docx` 支持“背景与动机—目标—方法—预期成果”的写作顺序，计划没有把示例经历、方法或选题当作申请者事实。上游前置条件、包导出和材料工具有对应源码或官方文档依据。 |
| P2 | 新技能负责材料发现、研究设计、写作和稿件状态，上游负责自身产物和原有检查。论文与非论文路线分工明确，不靠手写上游状态补偿缺项；固定包复用与单份正文方案可以实现目标，替代方向及取舍已说明。 |
| P3 | 已检查缺少目标与第一阶段快照、关键研究条件未解决、修改稿带实质变化、部分导出失败、提交前后中断及跨校复用。计划保留真实用户决定、未受影响成果、旧稿和导入原件；稿件编号及当前版本入口可避免按文件名或修改时间误认稿件。 |
| P4 | 第 298 行起明确组件职责和实施顺序；材料定位、Word 修订处理、学校栏目映射、统一正文、导出核对及恢复已有可执行路径。未来产品和测试尚未完成属于后续工作，不构成本计划设计缺陷。 |

影响判断的固定来源如下：

- `professor-contact@ad096fe31a4b5694cbe47a40f37b621435e1eeec`：本地版本一致。[第二阶段预检](../../../professor-contact/.apm/skills/professor-contact/scripts/_stage2_preflight.py)第 877 行起先读目标和第一阶段快照，缺失时停止；计划第 65、75–86 行的顺序与原代理职责一致。第三阶段输入限制、`direction_id`、校验收尾和套磁选择边界也已核对。
- `professor-research@bb27533540715c44039c108302f11d3e00d6b62e`：[固定导出](https://github.com/ScholarWorkflow/professor-research/blob/bb27533540715c44039c108302f11d3e00d6b62e/flake.nix)提供采集和方向预筛包，相应代理支持计划使用的 `folder_path`、教授范围、`skip_pdf:true` 和 `preview:true`。
- `agent-env-nix@c368871942435bdc178a1063ce9c677acaf8cabc`：[组合代码](https://github.com/RekiDunois/agent-env-nix/blob/c368871942435bdc178a1063ce9c677acaf8cabc/lib/project.nix)支持递归依赖去重和冲突报错。计划复用原输入图中的包，没有另造安装器或分别激活后覆盖配置。
- `base-skills@3ab2ac188e625b8a8ae37b5fa318c579787c3d1e`、`source-access-skills@2fb5c2f1d7a5f5eb53d389bdb1853cdb525700d8`：已读取视觉程序、搜索包、服务名称和工具入口。
- `nixpkgs@6510408d147d8c5e6d76043e899e9251756f6a75`：材料程序版本已按固定源码核对。Word 修订处理符合 [Pandoc 3.7.0.2 文档](https://github.com/jgm/pandoc/blob/3.7.0.2/MANUAL.txt#L699)，计划没有将 `--reference-doc` 当作填表入口；LibreOffice 应用内实际程序及独立配置目录的安排符合[启动参数文档](https://help.libreoffice.org/latest/en-US/text/shared/guide/start_parameters.html)。

模板范围没有形成阻断。已确认交付是 `.docx` 与 Markdown，原要求允许无法直接填写时交付按学校栏目组织的 Word 草稿并说明转填。计划第 253–269 行区分了直接填写 `.docx` 与其他格式的后备路径，没有宣称 PDF 或旧 `.doc` 已完成原表填写。现有要求未单独承诺填写 PDF 表单或转换旧 `.doc`，因此不新增这两项能力或测试义务。

本轮必须修改的计划缺陷为 0；实现偏离不适用，目标产品尚未建立；影响结论的材料缺口为 0。未另列可选改进作为通过条件，未运行构建、安装或业务测试。

结论仅表示上述版本方案适合实施，不代表安装可用、测试通过或可以合并。当前无需修改计划正文。后续实现负责人按计划第 298 行起的顺序推进，测试负责人另按既有规则准备适用测试。本轮只更新本审核记录，以下前次记录保留为历史。

## 前次三项修订审核（历史记录）

审核日期：2026 年 11 月 3 日。

审核者：独立 `plan_reviewer` 代理 `/root/plan_reviewer_r2`。本记录转存其结论；计划作者未自行批准计划。

审核对象：[研究计划草稿技能执行计划](implementation-plan.md)。审核者通读完整候选、对照修订前快照并核对相关源码。本次批准范围为用户提出的三项修订及必要的直接影响，不将未改业务段视为此前已经批准。

```text
Plan revision: rp-plan-r2-2026-11-02
Requirement revision: rp-requirements-2026-11-02-q6-q16
Target repository revision: research-proposal 尚未建立，无产品提交
Candidate SHA256: 0ca6dd97b6cf45d9c02debe3dc6fcbc5860157c3839c1a4cf3f687d0c8f8c77e

P1 Requirement & Reality Grounding: PASS
P2 Solution Validity & Ownership: PASS
P3 Impact, Safety & Counterexample: PASS
P4 Executability: PASS
Gate review completeness: COMPLETE

Critical assumptions: N/A
Unresolved impacts: N/A
Approved behavior changes: N/A；本轮落实既有要求，未增加业务范围
Reused prior Plan Gate PASS: N/A；没有引用此前完整通过结论
Required modifications: N/A
Missing evidence for PARTIAL review: N/A

Plan conclusion: APPROVED
```

### 核对结果

1. **第二阶段前置条件已修正**。计划第 65 行及第 75 行起规定先处理教授本地目标和第一阶段快照，再交原代理检查和复用分析。contact `ad096fe31a4b5694cbe47a40f37b621435e1eeec` 的[预检源码](../../../professor-contact/.apm/skills/professor-contact/scripts/_stage2_preflight.py)第 877 行起及 Codex 分析代理第 98–152 行支持此顺序。已有正式输入包的直接复用路径也已保留。

2. **固定依赖与职责成立**。计划第 177 行起明确 contact 输入、递归锁定图、六项直接依赖和组合安装方式。审核者独立读取固定版本的 [research 导出](https://github.com/ScholarWorkflow/professor-research/blob/bb27533540715c44039c108302f11d3e00d6b62e/flake.nix)、[搜索包](https://github.com/StudyCoachWorkflow/source-access-skills/blob/2fb5c2f1d7a5f5eb53d389bdb1853cdb525700d8/flake.nix)、[图片入口](https://github.com/ScholarWorkflow/base-skills/blob/3ab2ac188e625b8a8ae37b5fa318c579787c3d1e/nix/vision-tools.nix)及[共享组合代码](https://github.com/RekiDunois/agent-env-nix/blob/c368871942435bdc178a1063ce9c677acaf8cabc/lib/project.nix)，确认所列能力已有正式导出；此次接线无需新增上游接口。Nix 完整环境与 npx skills 资源安装的边界明确。

3. **材料读写与恢复安排可实施**。计划第 239 行起明确材料定位、识别缺项、用户修改稿原件保留、实质变化确认和模板兜底。固定 [Pandoc 3.7.0.2 文档](https://github.com/jgm/pandoc/blob/3.7.0.2/MANUAL.txt#L699)支持保留修订信息；模板填写没有误用 `--reference-doc`。审核者静态检查了部分导出失败、目录改名后未切换状态、切换后中断及输入变化等代表情况：两种成品从同一正文生成，提交前保留旧版，恢复依据明确记录，不靠文件时间猜测当前稿。

### 适用范围与交接

以上是计划审核结论。目标产品尚不存在，本轮没有运行构建、安装或业务测试，也没有审核正式测试计划及合并条件。

后续实现负责人按计划第 298 行起的顺序实施，建立目标仓库时将计划迁入 `plan/implementation-plan.md`，并一并迁移本审核记录、保留版本和校验值。测试负责人另按既有规则准备适用测试。计划正文若发生实质变化，应按受影响范围重新审核；本记录只对应上述校验值。

## r5：讲稿与想定问答交付（2026-11-25）

审核类型：执行计划审核。审核者：专用 `plan_reviewer` 代理（只读，`~/.codex/agents/plan-reviewer.toml`）。

- `Requirement revision`：`rp-requirements-r3-interview-2026-11-25`。
- `Plan revision`：`rp-plan-r5-interview-2026-11-25`，取代 `rp-plan-r4-markdown-2026-11-04`。
- `Candidate SHA256`：`aec2492a0b3d655a3e6797f222f4ea32782610a6bd9bc24352b4abe34a59d5f3`（382 行）。
- `Target repository revision`：`feat/interview-script-artifacts`，base `786d1402929f25ca91f8cdaa4090e8bd73d6989b`；审阅时 HEAD `50651c9a770d517869db199280cb4dc1a5e7a9db`。
- 审核轮次：三轮。首轮提出 P-01 至 P-10；第二轮提出 P-11 至 P-14，并确认 P-01、P-02、P-03、P-06、P-07、P-08 闭合；第三轮复核 P-04a–d、P-09a、P-13、P-14 并给出批准结论。

| 关口 | 结论 |
|---|---|
| P1 Requirement & Reality Grounding | PASS |
| P2 Solution Validity & Ownership | PASS |
| P3 Impact, Safety & Counterexample | PASS |
| P4 Executability | PASS |
| Gate review completeness | COMPLETE |

**Plan conclusion: APPROVED**

`Approved behavior changes`：当前交付 Markdown 正文，并按用途加选发表讲稿与想定问答（`implementation-plan.md` 的「本轮新增与延期」一节）；Word、学校表格填入、页面调试延期，LibreOffice 不参与测试与完成判断。来源为 `rp-requirements-r3-interview-2026-11-25` 与用户 2026 年 11 月 25 日「两项都算本次范围」的决定。

**问题闭合情况**：

| 编号 | 内容 | 状态 |
|---|---|---|
| P-01 | 需求授权没有可引用修订 | 闭合（第三轮确认） |
| P-02 | 完成度四条底线超出本轮范围 | 闭合（第三轮确认） |
| P-03 | 缺少 revision 标识 | 闭合（第三轮确认） |
| P-04、P-04a–d | 权威依据不唯一、残留「只交付 Markdown」表述 | 闭合（第三轮） |
| P-05 | 删除单项的补救路径不可执行 | 闭合（第二轮） |
| P-06 | 「只影响对应交付文件」不成立 | 闭合（第二轮） |
| P-07 | 加选连带正文失效未写清 | 闭合（第二轮） |
| P-08 | 失效规则把 Word 写成需重新生成 | 闭合（第二轮） |
| P-09、P-09a | 契约细节缺失、权威次序倒置 | 闭合（第三轮） |
| P-10、P-13 | 计划与记录未对齐、证据指向不一致 | 闭合（第三轮） |
| P-11 | 空对象与 `null` 会丢失已保存讲稿 | 闭合（实现改为拒绝，第二轮） |
| P-12 | 条件表写了不存在的保存门 | 闭合（第二轮） |
| P-14 | 非对象入参报 `TypeError` | 闭合（第三轮） |

**未闭合但非阻断**：

| 编号 | 内容 | 负责人 | 处理 |
|---|---|---|---|
| P-15 | `test-plan.md` 的执行说明段仍写 `rp-recipe-r14-markdown-2026-11-04`、指向 r5 业务清单，未含 RP-14 步骤 | 测试计划负责人 | 已在 `50651c9` 之后的提交中处理：执行说明升为 `rp-recipe-r15-interview-2026-11-25`，范围句加入 RP-14，并补 RP-14 的执行步骤；`test-plan-review.md` 与 `test-preparation-review.md` 是历史记录，保留原文 |

**限定**：该结论只表示当前方案适合实施，不代表实现正确、第三关通过或可以合并。本轮审核未运行代码与测试，未审 Nix 构建与真实会话。

## r6：新颖性、先行研究关系与准备程度（2026-11-25）

审核类型：执行计划审核（r6 修订复核）。审核者：专用 `plan_reviewer` 代理（只读）。

- `Requirement revision`：`rp-requirements-r3-interview-2026-11-25`（含第一批与第二批追加条目）
- `Plan revision`：`rp-plan-r6-novelty-2026-11-25`，取代 r5
- `Candidate SHA256`：`5c5c79e8fccfb5546430ec4b49e1d5c273e4b719309243be43819943cd4bf8ff`
- `Target repository revision`：分支 `feat/novelty-guidance`，HEAD `36d537e`（审阅时计划正文来源为 `06ea2a9`），基线 `f5c140f`
- `Relevant upstream/runtime revision`：N/A（只改技能文档，不改变上游、依赖或运行版本）

| 关口 | 结论 |
|---|---|
| P1 Requirement & Reality Grounding | PASS |
| P2 Solution Validity & Ownership | PASS |
| P3 Impact, Safety & Counterexample | PASS |
| P4 Executability | PASS |
| Gate review completeness | COMPLETE |

**Plan conclusion: APPROVED**

`Approved behavior changes`：新增写作与面试判断（四节参考规则、三类追问、`SKILL.md` 相关研究与中文方案两步接入），来源为用户 2026 年 11 月 25 日两批材料。这些是指导内容，不改变组件行为；r4、r5 的 Markdown 与讲稿交付变化继续有效。

**审核发现（均为非阻断，已处理）**：

| 编号 | 内容 | 处理 |
|---|---|---|
| N-01 | `Requirement revision` 只列第一批，第二批修正只在正文出现 | 已把两批合并为一条需求记录，同时列明四项要求与第二批的修正来源，不再按批次归属 |
| N-02 | 两处把第三落点简写为「对象」，权威表述是「对象或数据」 | 已统一为「对象或数据」（含「有限补查」证据表一处） |
| N-03 | 计划只列两份 references，漏 `SKILL.md` 的文件级变化 | 已在第 11 行补记 |
| N-04 | 第 364 行「此前」指代不明 | 已改为「本分支上一版草稿（`da1ea06`）」，并注明该句不在 r5 内 |
| N-05 | `test-plan-review.md` 尚无 r7 的关口记录 | 交测试计划负责人；r7 只改版本与指针，未新增必测项 |

**审计说明**：本记录审核的是 `06ea2a9` 上的计划正文（当时 SHA256 `d8a31354…`）。审核提出 N-01 至 N-04 后，计划做了编辑性修订：`plan/implementation-plan.md:11` 合并两批需求记录、补第二批来源与 `SKILL.md` 文件级接入；`:364` 把「此前」明确为 `da1ea06`，并注明该句不在 r5 内。第三落点称谓的修订在 `skills/research-proposal/references/research-design.md:27`，并同步同文件 `:176` 与 `SKILL.md:59`，不在计划正文。修正后计划 SHA256 为 `5c5c79e8…`。

审核者已对 `d8a31354…` 与 `5c5c79e8…` 做 diff 级适用性确认：两者之间只有需求记录与措辞的编辑性修订，行为范围、必测范围、接口、依赖、owner 与 P1–P4 结论不变，原 `APPROVED` 继续适用于 `5c5c79e8…`，不需要重开任何关口。

**限定**：该结论只表示当前方案适合实施，不代表实现正确、测试关口通过或可以合并。审核未运行构建、测试或产品入口；测试计划关口与合并条件不在本结论内。

## r12 实现符合性审核触发修订后的计划审批（2026-11-28）

实现符合性审核的 IR-01、IR-02 处理后，两份计划出现新哈希，按 Plan Reviewer Rule 第 6.3 节做影响分析。

**受审版本**：执行计划 `73230e9ef73c27f5630eb1c55abbf56881c2993f0af09a4c14d5d71935d14933`；测试计划 `8ef08f6c6a8e41de244523c2ece4aaa00619d4d55f9145a5fe187003192ec38a`。

**差异与定性**（相对上一次 `APPROVED`）：

| 差异 | 定性 |
|---|---|
| 第 405 行 r7 历史小节加括注 | 记录性，不改现行规范 |
| 第 439 行补记「空白成因的硬要求」第 58 行同属该口径改写 | 落实已批准口径，不新增语义 |
| 第 457 行校验边界补「`id` 与 `statement_version` 为非空字符串」 | **触及 contract 与 identity，需重新批准** |
| 测试计划第 236 行「不扩散」措辞 | 意图正确但一度保留「两条硬门槛原文……未改」造成内部矛盾（R-05），已改 |

审核者判断：前两项可复用原 `APPROVED`；第三项因新增了一条计划文本原先没有的可拒绝条件、且 `id` 是候选身份，不能按纯第 6.3 节复用，须重新批准；测试计划还有 R-05。

**R-05 修正**：测试计划第 236 行改为「硬门槛仍为两条且含义不变（新意落点判据行与基线相同；空白成因 0 分判据按 IR-01 收窄为“已证伪”一种来源两种情形，1 分判据行与基线相同，「空白成因的硬要求」里的“缺这三项也按 0 分”同步改为“还没查够三篇记未评”）」，删去与第 232 行冲突的旧短语。

**复核结论**：

```text
Plan revision: rp-plan-r12-verdict-record-2026-11-28
Requirement revision: rp-requirements-r8-verdict-record-2026-11-28
Target repository revision: research-proposal 分支 feat/verdict-record，基线 97c1340

P1 Requirement & Reality Grounding: PASS（复用首轮结论）
P2 Solution Validity & Ownership: PASS（第 3 项重审：owner 仍为 save_revision 入参校验，机制不变）
P3 Impact, Safety & Counterexample: PASS（第 3 项不改变既有记录可接受性）
P4 Executability: PASS（第 3 项可执行；文档与计划同轮对齐）
Gate review completeness: COMPLETE

Approved behavior changes: 空白成因 0 分收窄为“已证伪”（一种来源、两种情形）、还没查齐记「未评」并按 pending；「未评」不参与总分、硬门槛项未评一律 pending；pending 增加四类触发情形；save_revision 对 candidate_scores 新增拒绝行为；拒绝后按四条路径处理、不做隐式迁移；新增：id 与 statement_version 须为非空字符串

Plan conclusion: APPROVED
```

审核者对第三项的复核依据：owner 仍是 `save_revision` 的入参校验，机制、change point、失败策略均未变；`_state.py` 在上一轮批准前已有该判断，本次只是补依据、未扩大代码行为；计划第 457 行的「校验边界」现在自洽——校验只拒绝文档本来就禁止或明确要求的写法，而文档同轮已写明该要求。兼容影响可忽略：用户工作版记录的 `id`（`C1`、`C2`、`C-version`）与 `statement_version` 均为字符串，旧记录按已批准口径本不迁移。

**非阻断观察已处理**：`test_malformed_id_types_raise_value_error` 的 `bad` 列表补上空字符串与纯空白；「旧记录怎么继续保存」第 1 条补一句“`id`、`statement_version` 要写成字符串；旧记录把编号写成数字时改成同名文本，不要改编号本身”。

**审核者的证据限制**：旧版本 `3891b47c…` 与 `a4934389…` 的文件内容不在 git 对象中，审核者只能核对当前内容与基线 `97c1340` 的差异以及交接说明列出的四处；若有未列出的改动，不在该结论覆盖范围内。本条如实保留。

结论不代替测试第二、第三关口与合并批准。

## r12 用户复核四条件后的计划审批（2026-11-28）

用户复核 PR #9 判 `NOT_READY`，提出四条（保存放行缺依据的记录、一次报错漏掉独立问题、汇总与计分冲突、公开差异含用户数值与本机路径）。修正后计划新增「结构校验补齐」「汇总与计分口径统一」「示例与路径去标识化」三段，测试计划新增四组观察点，属语义级改动，重新交审核。

**审核过程**：首轮结论 `NEEDS_MODIFICATION`，两项阻断——M-01（计划第 436 行仍写五字段窄枚举，与第 477 行的全字段口径互斥）、M-02（测试计划第 231 行同样窄枚举，与第 240 行互斥）。两处都是「只改了一处、漏了紧邻的另一处」，与快审 C1 同一类问题。

**修正**：第 436 行与测试计划第 231 行改为全字段集合，并写明「字段集合由下文『汇总与计分的口径统一』条同口径规定，不是只取前五个」；文档第 285 行改为引用式，只保留行为要求，避免同源漂移。检查脚本新增 I4v、I4w 检索窄枚举，命中即失败。

**定向复核**结论 `APPROVED`：

```text
Plan revision: rp-plan-r12-verdict-record-2026-11-28（SHA256 086e111e…da8587b）
Requirement revision: rp-requirements-r8-verdict-record-2026-11-28
Target repository revision: research-proposal 分支 feat/verdict-record，基线 97c1340

P1 Requirement & Reality Grounding: PASS（复用）
P2 Solution Validity & Ownership: PASS（复用）
P3 Impact, Safety & Counterexample: PASS（复用）
P4 Executability: PASS
Gate review completeness: COMPLETE

Approved behavior changes: 沿用上一版全部，另加 evidence_cutoff 非空、experiment/missing 每项非空字符串、scores 键集合等于 weights 且必含两道硬门槛、evidence 覆盖每个已评项、权重非负、gate 非法时不提前返回、汇总字段扩为全部判决字段、报表第 3 条引用「怎么算总分」

Plan conclusion: APPROVED
```

审核者确认六处只剩一套字段集合（计划 436／477、测试计划 231／240、文档 174／285），全仓无窄枚举残留；并确认新增结构校验没有超出「只拒绝文档本来就禁止或明确要求的写法」这条边界——`scores` 必含硬门槛有第 89–94 行「两项硬门槛」与第 33 行「每项 0、1、2 分」为据，`evidence` 逐项有依据有第 238 行「每一项的分数后面必须跟一句依据」与第 250 行「0 分也要写依据」为据，其余各项也各有出处。

审核者另记录两项未独立核实：远端分支历史重写后的实际状态无法从本地核实；新增检查项 I4v、I4w 位于仓库外脚本，只能确认现行文本已无窄枚举。两处均不影响计划正确性。

结论不代替测试关口与合并批准。
