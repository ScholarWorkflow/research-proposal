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

## r12 用户复核第二轮（三条）的计划审批（2026-11-28）

用户对 head `15bb375` 再次判 `NOT_READY`，提出三条，均由本地构造输入复现：①硬门槛分数与判决互相矛盾仍能写入；②`evidence` 可写空白、多键，且与 `scores` 的类型错误会互相遮蔽；③单候选免评分时无法同时做到“不评分”与“落判决记录”。

其中①、②是校验覆盖不足，属已批准校验在文档既有规则内的补全（`candidate-scoring.md` 第 118–130 行判决表、第 87–99 行硬门槛定义、第 238 行“每一项的分数后面必须跟一句依据”），不改变产品要求。③是**保存形态缺一种**，需要新增 `materials` 步骤的可选对象 `verdicts`，属语义级改动，按 `Plan Reviewer Rule.md` 第 5 节重新交审核。

**变更目的**：让“没有候选比较、因而不评分”的场合也能按题面版本落判决记录，解决 `SKILL.md` 第 58 行（单候选不评分）与第 59 行（要走完落判决记录）在同一场景下无法同时满足的问题。

**关键差异**：
1. 新增 `materials` 步骤的可选对象 `verdicts`（`{evidence_cutoff, items:[{id, statement_version, gate, experiment, missing, evidence}]}`），`gate` 限 `pass`、`pending`、`hard_stop` 三值，不写 `scores`、`weights`、`total`（写了被拒）。
2. `candidate_scores` 的 `pass` 仍要求数值总分，不放宽；两对象可同时出现，各按自己的规则校验。
3. 硬门槛分数与判决对齐：`gap_zero` 要求「空白成因 = 0」，`novelty_zero` 要求「新意落点 = 0」，`pass` 与 `soft_stop` 要求两道硬门槛都大于 0；`problem_invalid` 与 `merge` 不加入。
4. `evidence` 键集合须与 `scores` 完全一致（多键报错），每项须为去掉首尾空白后仍有内容的字符串；`scores` 与 `evidence` 各判各的类型、累积报错。

**受影响关口**：P2（新增 change point 与 owner 边界）、P3（新增可观察行为与兼容影响）、P4（可执行性）。P1 复用：三条问题均已用构造输入复现，事实来自基线 `97c1340` 之后的本分支代码，不涉及新的 requirement 或外部事实。

**未受影响结论的沿用理由**：r12 已批准的「判决记录怎么写」节、九项权重与 0/1/2 判据、五态判决词、三类停因、`candidate_scores` 既有校验项、汇总与计分口径、去标识化处理，均未被本次改动触及，直接沿用。

**变更记录**：计划新增「判决与硬门槛分数的对齐」「依据字段的结构与报错累积」「单候选免评分的保存形态选择」三段，RP-18 新增三条观察点（依据字段、分数与判决对齐、免评分 `verdicts`）并加严「一次报全」条；文档新增 `candidate-scoring.md` 的「只有一个候选、不评分时怎么存」节、`SKILL.md` 第 58 行入口、`runtime.md` 的 `verdicts` 说明。

**首轮结论 `NEEDS_MODIFICATION`（2026 年 11 月 28 日，`Gate review completeness: COMPLETE`）**，五项阻断，均为事实：

- **R-01**：计划两处仍把校验范围写成只有 `candidate_scores`（"校验只作用于…这一个可选对象"与实施顺序第 5 行），与新增的 `verdicts` 校验不自洽。
- **R-02**：本轮替换段落时把 r12 的**校验方案总体选择**整段删掉（"只改文档不校验""另建 `references/verdict-record.md`""给分数加 `unrated` 枚举"三条替代方向随之丢失），且 r7 段仍留"组件不校验 `candidate_scores`"的相反描述。这是本轮的回归。
- **R-03**：`evidence` 形态在通用「判决记录怎么写」节写"对象、键与 `scores` 一一对应"，在 `verdicts` 节写"数组"，两处未各自限定适用范围；计划里"文档第 363 行"所指位置已空，测试计划字段清单也未限定为 `candidate_scores`。
- **R-04**：RP-18 文档侧只覆盖「判决记录怎么写」与 `candidate_scores`，没有 `verdicts` 的文档观察点；计划"文档同步三处"实际为四处；执行步骤导入断言只验 `_check_candidate_scores`，测试清单未列 `verdicts` 测试类。
- **R-05**：两个可选对象同时有错时，`save_revision` 先校验 `candidate_scores`、失败即抛，`verdicts` 的问题不会一起列出——正是用户第 2 条所指"错误互相遮蔽"在对象层的复发。

另接受非阻断观察 O-01（补用户建议来源日期、"汇总代码"改为"汇总时"）、O-02（`soft_stop` 排除依据写准：它要求总分照算而该形态不算总分；无比较时软门槛问题用 `pending` 记、补法写进 `missing`）、O-03（非停判决不得带 `stop_reason`、数组项须非空字符串，补进计划与文档）、O-04（补 `verdicts` 停因字段与多问题一次报全的用例）、O-05（行号漂移，改用小节名或实际行号）。

**修正**：R-01 改计划两处为"作用于 `candidate_scores` 与 `verdicts` 两个可选对象，同时有错合并成一次 `ValueError`"；R-02 恢复 r12 校验方案选择整段（三条替代方向原样保留），并把 r7 旧句标注"r12 已改变这一状态，本条只说明 r7 当时为何不选该方向"；R-03 通用节改为"带 `scores` 的记录里 `evidence` 不是数组"、`verdicts` 节写明"没有 `scores` 可对应，所以是数组"，计划改指小节名，测试计划字段清单限定为 `candidate_scores` 的 item；R-04 新增 RP-18"免评分判决的文档部分"观察点、计划改"文档同步四处"并列出 `candidate-scoring.md` 开头入口、导入断言补 `_check_verdicts` 与 `_check_materials_records`、测试清单补 `VerdictWithoutScoresTests`；R-05 把免评分形态的校验抽成 `_verdicts_problems`（只返回问题列表、不抛），`_candidate_scores_problems` 沿用原有返回列表的实现，新增 `_check_materials_records` 把两者的问题合并后一次抛出；`save_revision` 改为调用它。

复验：`test_verdict_record` 62 项 `OK`；独立探针 10/10、9/9、11/11（原三条问题、单候选免评分场景、畸形输入拒绝且状态不变）；文档检查 `PASS 139 checks`、`ALL OK`，其中 N1–N14 为上述五项修正的专项检查，已用故意破坏验证能失败。

**变更记录补充**：除上述修正，本轮还（a）在 `candidate-scoring.md` 开头适用范围句补“不评分不等于不记判决”并指向新节；（b）把该文件「保存」节对 `evidence` 的描述限定为 `candidate_scores`，并新增 `verdicts` 的数组形态说明；（c）把「判决与三项内容的对齐」的总结句移到新增的分数对齐段之后，并把「保存」节里“三条对齐规则”的过期计数改为“判决对齐规则”；（d）在 `runtime.md` 的 `materials` 行补 `verdicts` 形态、校验范围与合并报错。

**定向复核第二轮结论 `NEEDS_MODIFICATION`（2026 年 11 月 28 日，`Gate review completeness: COMPLETE`）**：P2 通过（R-02 闭合），P1 沿用；P3、P4 各留修正未同步到相邻位置的残留，均为修正不完整、非新发现的产品要求：

- **R-01a**：计划实施顺序第 5 行仍只写 `candidate_scores` 校验。
- **R-03a**：计划「三样内容分开填」仍把 `evidence` 无条件写成对象，未限定为带 `scores` 的记录。
- **R-05a**：计划“互不合并、不互相顶替”与测试计划“互不影响”仍是合并报错前的旧措辞；测试计划测试清单未点名两对象同时报错的用例。

**修正**：三处全部改为与新行为一致（实施顺序补 `verdicts` 与三项校验；`evidence` 两套形态各自限定适用范围；两对象同时有错合并成一次 `ValueError`，测试清单点名 `test_both_objects_report_problems_together` 与 `test_both_objects_valid_still_save`）。同时处理非阻断项：测试计划的目标摘要与版本摘要补 `verdicts`（N-01）；计划里 `soft_stop`／`merge` 的不适用依据改为文档同一口径并补“`pass` 与 `pending` 不得写 `stop_reason`”（N-02）；计划影响段改写“没有未解决的关键影响”一句，说明两个对象的校验范围、依据字段两套形态与合并报错方式均已写死（N-04）；补本节变更记录（N-03、O-07）。

本轮修正后又发现 `candidate-scoring.md`「保存」节一处同类残留（仍无条件写“`evidence` 不是数组”），已一并限定。检索确认：在 `plan/implementation-plan.md`、`plan/test-plan.md` 与 `skills/research-proposal/references/*.md` 范围内，`互不合并`／`互不影响`／无条件的 `evidence 不是数组`／只写 `candidate_scores` 校验 四类表述均无残留。**该检索范围排除本记录自身**（`plan/implementation-plan-review.md`），因为本记录会引用这些旧措辞作为问题摘要，纳入检索必然误报；这也说明关键词检索的局限——它只能发现旧措辞，发现不了“缺失的正向表述”与“命令参数结构错误”。

复验（修正后未改产品代码，仅文档与计划；运行包与源码仍逐字节相同）：`test_verdict_record` 62 项 `OK`；独立探针 10/10、9/9、11/11；文档检查 `PASS 148 checks`、`ALL OK`，新增 N15–N23 覆盖本轮三处修正，已用故意破坏验证能失败（破坏 3 条报 3 条失败）。

**定向复核第三轮结论 `NEEDS_MODIFICATION`（2026 年 11 月 28 日，`Gate review completeness: COMPLETE`）**：P1、P2 沿用；P3、P4 各留一处直接连带残留。R-01a／R-03a／R-05a 与 N-01～N-05 均已闭合。新发现两项：

- **R-04b**：测试计划里导入检查的命令写成三段引号串，`python3 -c` 只消费第一个参数，后两段断言变成 `sys.argv` 被忽略，命令仍以 0 退出——**预检实际上不验证任何断言**。已实测确认：三段写法打印路径后 exit 0；同一断言写成单段则 exit 1。
- **R-05b**：`runtime.md` 的 `verdicts` 句只写"各按自己的规则校验"，缺"两个对象同时有不合规处时一次报错同时列出"，与详细文档、计划、代码不一致，也使本记录的变更记录 (d) 与文件不符。

**修正**：导入命令改为**单个** `-c` 参数（多行字符串），并在步骤里写明"整段必须是一个 `-c` 参数；拆成多段引号会被当作 `sys.argv` 忽略，命令仍以 0 退出而不验证任何断言"，同时把断言扩到三个函数；`runtime.md` 补"两个对象同时有不合规处时，一次报错会同时列出，不先报一个、补完再报另一个"；RP-18 的运行时文档观察点同步要求这句；本记录 (d) 已按实际内容修正。

**R-04b、R-05b 的修正与实证**：导入命令已改为单个 `-c` 多行参数，并用最小对照实证——同样的三个断言，写成三段引号时即使断言的是**必然不存在**的属性也 exit 0（被当作 `sys.argv` 忽略），写成单段 `-c` 时同一断言 exit 1；真实运行包单段执行 exit 0。改后的命令块已用 `bash` 实际执行通过。`runtime.md` 已补合并报错句，RP-18 的运行时文档观察点同步要求该句，计划的“文档同步四处”也写明 `runtime.md` 要写合并报错。

**检索方式的教训**：关键词检索只能发现旧措辞，发现不了"缺失的正向表述"和"命令参数结构错误"。因此除关键词检索外补两类正向检查：①`runtime.md` 的 `verdicts` 行必须包含合并报错句；②导入命令必须是单个 `-c` 参数：检查块内 `-c` 之后不再出现“独立成段、以引号开头并以引号结尾”的参数行，并断言三个函数名都在同一段里——仅靠 `grep` 或 `bash -n` 不够，因为三段引号在 `bash -n` 下也合法。两项已加入仓库外检查脚本（P1–P5），其中 P3 的结构判定已用“好写法 / 坏写法”最小对照单独验证：好写法 0 段独立参数、坏写法 3 段。

**最终结论 `APPROVED`（2026 年 11 月 28 日，第四轮，`Gate review completeness: COMPLETE`）**：

```text
Plan revision: rp-plan-r12-verdict-record-2026-11-28（SHA256 3a3a9956…839df1d6a）
Requirement revision: rp-requirements-r8-verdict-record-2026-11-28
Target repository revision: research-proposal 分支 feat/verdict-record，基线 97c1340，head 15bb375

P1 Requirement & Reality Grounding: PASS（沿用）
P2 Solution Validity & Ownership: PASS（沿用第二轮）
P3 Impact, Safety & Counterexample: PASS
P4 Executability: PASS
Gate review completeness: COMPLETE

Approved behavior changes: materials 新增可选 verdicts 对象（evidence_cutoff + items，gate 限 pass/pending/hard_stop，
不写 scores/weights/total，evidence 为数组）；candidate_scores 硬门槛分数与 gate 对齐；evidence 键集合与 scores 一致、
空白/布尔/数字不计依据；两个对象同时有错合并成一次 ValueError；runtime.md 的 materials 行补合并报错
Unresolved impacts: N/A

Plan conclusion: APPROVED
```

审核者确认：R-04b（导入命令三段引号导致断言不执行）已闭合，命令现为单个 `-c` 多行参数且步骤写明失败方式；R-05b（`runtime.md` 缺合并报错句）已闭合；直接连带项（计划 `:435`／`:497`／`:500`／`:544`／`:556`，测试计划 `:240`／`:241`／`:320`，文档 `:170`／`:370`／`:385`，代码 `_check_materials_records`）均未回退；检索范围限定与两类正向检查的处理被确认为正确。

审核者另确认两点：`test-plan-review.md` 仍无本轮 RP-18 观察点的测试计划复核记录属测试计划关口材料，本计划的 `APPROVED` 不代替它；固定检查清单不必作为批准前提，若写入计划应标为“执行自查”，不计入必测清单、不新增第三关通过条件。

本结论只表示当前设计版本适合实施，不表示实现正确、测试全部通过或可以合并。

`Proposed review status`：`pending`。正式结论由独立 `plan_reviewer` 给出。

审核对象校验值（第三轮修正后）：`implementation-plan.md` SHA256 `3a3a99563099fcc77d00e420c243ce032a37188191c83e5401b95bd839df1d6a`（最终批准版，未再变动）；`test-plan.md` 当时为 `0fc1848981ce27861f02d9e3d1b69e901912982570699b2b55ec98ddfb2fd090`——该值只表示本计划审核读取时的测试计划版本；测试计划其后经独立审核修订为 `c81d68b39258cf12d7b803b858a684dcd13d7ff7ac4c392472d1d802c9e15028` 并单独获批（见 `plan/test-plan-review.md` 最后一节），本计划审核不覆盖测试计划的批准。

## r12 用户复核第三轮（四条）的计划审批（2026-11-28）

用户对 head `de1e42f` 第四次判 `NOT_READY`，提出四条，全部用构造输入复现（6 组探针，修前 0/6 符合预期）：

1. **同一题面能保存两条相反判决**：`candidate_scores` 与 `verdicts` 各自查重，同一 `(id, statement_version)` 可一处记 `pass`、另一处记 `hard_stop`，两条都落盘。现有测试还断言这种写法可以保存。
2. **非法停因打断整份报错**：两道硬门槛已评分时，`hard_stop` 带 `stop_reason: []` 或 `{}` 在停因表字典查找处抛 `TypeError`，已收集的问题与另一对象的问题都无法返回。
3. **可独立判断的依据错误仍漏报**：`scores: []` 配含空白值的 `evidence` 对象时只报分数形态错误。
4. **允许的权重配置让总分公式除以零**：整表只留一项正权重、该项恰好未评时，剔除未评项后分母为零，仍可记 `pass`。

其中第 1、4 项是**语义变更**（新增拒绝项与新的记录规则），按 `Plan Reviewer Rule.md` 第 5 节重新交审核；第 2、3 项是既有「一次列出全部问题」规则在畸形输入下的执行不完整，不新增产品要求。

**变更目的**：让「同一题面只留一条判决」这条既有唯一性规则在整次保存范围内成立，并给“分母为零”这种合法权重配置一个确定的记录方式。

**关键差异**：
1. 新增跨对象查重：整次保存内 `(id, statement_version)` 唯一，`candidate_scores` 与 `verdicts` 之间重复时拒绝并一次报出两个对象名称；同候选不同版本、不同候选之间仍可并存。
2. 新增分母下限检查：`pass`、`soft_stop` 要求至少有一项「权重大于 0 且该项不是未评」；否则拒绝并提示改记 `pending`。`hard_stop`、`merge` 不给总分，不加入。
3. 文档「按题面版本分开记」补“唯一性适用范围是整次保存”；「未评」记法补“剔除后没有正权重项时分母为零、不得记 `pass`／`soft_stop`”。
4. 健全性修正：停因先判字符串类型再查表；`evidence` 取值检查与 `scores` 类型判断拆开。

**受影响关口**：P2（新增拒绝项的 owner 仍在校验入口，机制不变）、P3（新增可观察拒绝行为与兼容影响）、P4（可执行性）。P1 复用：四条均已用构造输入复现，事实来自本分支当前代码与已批准文档。

**未受影响结论的沿用理由**：r12 已批准的判决记录字段、未评记法、待补范围、`problem_invalid`、`candidate_scores` 既有校验项、`verdicts` 形态与三值 `gate`、合并报错、去标识化处理均未被本次触及。

**变更记录**：计划新增「整次保存的判决身份与分母下限」一段并在校验清单补两条；RP-18 新增四组观察点（整次保存的判决身份、分母下限、非法停因不打断报错、依据取值可独立判断）；文档 `candidate-scoring.md` 两处补规则；测试文件增至 75 项。

复验：`test_verdict_record` 75 项 `OK`；四条缺陷探针 6/6 符合预期。

审核对象校验值：`implementation-plan.md` SHA256 `63fd6cf0cea873679f1285a2de629351843b7a2c752a26b72d714f8cc3bb8697`，`test-plan.md` SHA256 `f8e0d47b690da7048e6917ed32340b0ab228642365c72b3819ea637d5b3a7f24`。

**定向复核结论 `NEEDS_MODIFICATION`（2026 年 11 月 28 日，`Gate review completeness: COMPLETE`）**：P1、P2 通过（P1 确认四条缺陷证据链成立；P2 确认两个新增拒绝项的 owner 仍在校验入口、跨对象唯一性是既有规则的执行、分母下限是既有“总分照算”与“未评剔除”的必然条件），P3、P4 各留修正未同步：

- **M-01**：计划两处、测试计划一处、产品文档两处仍写“两个对象各按自己的规则校验／各存各的”，没有写整次保存的 `(id, statement_version)` 唯一；`runtime.md` 与「被拒绝时怎么办」都没写跨对象重复的补救路径。
- **M-02**：影响段与批准行为清单没列入两项新拒绝与两项健全性修正；旧记录处理、兼容路径与实施顺序仍只覆盖 `candidate_scores`。

**修正**：统一在计划两处、`candidate-scoring.md` 的并存段与「被拒绝时怎么办」、`runtime.md` 的 `materials` 行、测试计划三处补同一句“整次保存内 `(id, statement_version)` 唯一；两对象之间重复也拒绝，报错列出两个对象名称；保留一条，删掉或移走另一条”，并新增「被拒绝时怎么办」第 5 条与旧记录处理第 5 条（明确组件不替你选、不自动删，旧记录下次保存会被拒直到按此处理）；旧记录处理由四条改五条；影响段、批准行为清单、实施顺序第 5 行、测试计划兼容路径同步补入两项新拒绝。

另接受非阻断观察：O-01（停因观察点与用例对应关系，`verdicts` 侧本就不会抛 `TypeError`，真正会抛的是候选侧；已在测试计划写明并让候选侧覆盖列表与对象两种形态）、O-02（测试计划版本摘要与步骤 4 清单补本轮四组）、O-03（同对象内重复不再被写成跨对象错误）、O-04（`merge` 可指向只记在 `verdicts` 里的候选，候选身份集合并入 `verdicts` 的 id）。

复验：`test_verdict_record` 77 项 `OK`（含新增 `test_merge_may_target_candidate_only_in_verdicts`、`test_same_object_duplicate_not_reported_as_cross_object`）；`test_interview` 27 项 `OK`；四条缺陷探针 6/6；旧探针 10/10、9/9；文档检查 `PASS 205 checks`、`ALL OK`。

审核对象校验值（M-01／M-02 修正后）：`implementation-plan.md` SHA256 `93d7f9122721544fa150fd0d1315fbe184f0f6ea21b3d8730cf421505f0700bc`，`test-plan.md` SHA256 `32ac2e81562b12dbf3b1555797f7f42b07204e59b855dddf7e312e9560f695ca`。

**定向复核第二轮结论 `NEEDS_MODIFICATION`（2026 年 11 月 28 日，`Gate review completeness: COMPLETE`）**：M-01 大部分闭合、M-02 主体闭合，O-01／O-03／O-04 闭合，O-02 部分闭合；留下三处「收束句与计数没一起改」的残留：

- **R-01**：计划旧记录处理的收束句仍写“以上处理只覆盖 `materials` 步骤的 `candidate_scores`”，把同节新增第 5 条要覆盖的 `verdicts` 与跨对象情形排除在外；同节第 3 条的“先不带 `candidate_scores`”也只写一个对象；测试计划兼容路径括注同样只举 `candidate_scores`。
- **R-02**：`candidate-scoring.md`「被拒绝时怎么办」写“四条规则”而实际五条；测试计划步骤 4 写“另含本轮新增的四类”而实际列了六类。
- **O-05**（非阻断）：测试计划要求跨对象报错指向“保留一条，删掉或移走另一条”，但实现报错文本是“删掉其中一条再保存”，两者不一致。

**修正**：R-01 把收束句改为覆盖两个对象、第 3 条改为“先不带相应对象／两个对象都不带时行为与之前一致”、测试计划兼容路径注明覆盖两个对象；R-02 计数改为“五条规则”与“六类”；O-05 把实现报错文本改为与文档同句（“同一题面版本的判决只能有一条：保留一条，删掉或移走另一条”），并新增 `test_cross_object_error_points_to_remedy` 断言该句。另按测试计划审核的补充意见，把整表权重全为 0 的用例扩到 `pass` 与 `soft_stop` 两种判决，把同对象重复不误报的用例扩到 `verdicts` 侧。

**计数专项核查**（本轮反复出问题的类型）：逐处核对三个计数词与实际条目数——`candidate-scoring.md`“五条规则”对应 5 条、计划旧记录处理“五条”对应 5 条、测试计划“六类”对应 6 项；另检索 `四条规则／四类相关／同步三处／两条处理／三条处理` 等过期计数，`plan/` 与产品文档内已无命中（仅复核记录引用旧措辞）。

复验：`test_verdict_record` 78 项 `OK`、`test_interview` 27 项 `OK`（合计 105 项）；四条缺陷探针 6/6；文档检查 `PASS 213 checks`、`ALL OK`。

审核对象校验值（最终）：`implementation-plan.md` SHA256 `6a9353c307a3433eea715cfcb05ec42432831ecf841613e9f9a014f922a64655`，`test-plan.md` 当时为 `97b91abb2ef8e253fd6588262a73f43f0f0c7cf9468fe239f2806c10702b6181`（本计划审核读取时的版本；测试计划其后经独立审核修订为 `1fb92e33016b01c575e2056b9e1189d2010b2e5d60f16ce41133fdc00343356a` 并单独获批，见 `plan/test-plan-review.md` 最后一节；本计划审核不覆盖测试计划的批准），`_state.py` SHA256 `3054f0936ec3b392fe4921015777cd74b6410691c96be4e26835c6df6e746a9d`，`test_verdict_record.py` SHA256 `b7024d5d1845e548327dcbad8412dd5445cdda60e3a3f8c190bcdb53d7b1fbb2`。

**最终结论 `APPROVED`（2026 年 11 月 28 日，第五轮，`Gate review completeness: COMPLETE`）**：

```text
Plan revision: rp-plan-r12-verdict-record-2026-11-28（SHA256 6a9353c3…a64655）
Requirement revision: rp-requirements-r8-verdict-record-2026-11-28
Target repository revision: research-proposal 分支 feat/verdict-record，基线 97c1340，head de1e42f

P1 Requirement & Reality Grounding: PASS（沿用）
P2 Solution Validity & Ownership: PASS（沿用）
P3 Impact, Safety & Counterexample: PASS（沿用）
P4 Executability: PASS（R-01a 三处及直接位置已闭合）
Gate review completeness: COMPLETE

Unresolved impacts: N/A
Required modifications: N/A

Plan conclusion: APPROVED
```

审核者确认：R-01a 三处已闭合（`candidate-scoring.md:393` 写明两个可选对象与“甚至两个都不传”、`runtime.md:92` 改为“相应对象（`candidate_scores` 与／或 `verdicts`）”、`test-plan.md:250` 括注同步）；R-01、R-02、O-01、O-02、O-03、O-04、O-05 均已闭合且未回退；计数五条／五条／六类与实际条目一致；`test-results.md` 的 r28 历史表加时点说明不构成残留，因为没有改写历史结果、也没有把旧计数冒充当前状态。

获批行为变化：`materials` 新增可选 `verdicts` 对象；`candidate_scores` 硬门槛分数与 `gate` 对齐；`evidence` 键集合与空白/布尔/数字检查；两个对象同时有错合并成一次 `ValueError`；整次保存内 `(id, statement_version)` 唯一、跨对象重复拒绝并给出补救；`pass`／`soft_stop` 在没有可计入的正权重项时拒绝；停因类型与依据取值独立报错。

本结论只表示当前设计版本适合实施，不表示实现正确、测试全部通过或可以合并。

## r12 用户复核第四轮（两条）的计划审批（2026-11-28）

用户第五次复核提出两条，都是“规则缺少区分、保存程序识别不出”的类型：

1. **三篇找齐仍可能把“没查清”写成 0 分**。「空白成因的硬要求」写“打 1 还要按四位置写清变化；用来支撑 1 分的那一项写不出，按 0 分”。三篇近邻找齐、但其中一篇只能读到摘要、无法核对该篇是否已用本稿方法时，模型照这句话只能写 0，再填 `hard_stop` 与 `gap_zero`；保存程序只核对分数、停因与证据字段，识别不出“证据其实还没查清”。用户同时指出：历史上有过「待核被汇总成停」，但没有记录证明是由这句话触发的——因此本轮按“规则在缺少区分时必然被误用”处理，**不声称已证明因果**。
2. **续做旧稿可能把旧判决挂到新题面**。旧评分评的是 `q1`，当时记录里没有 `statement_version`；题面后改成 `q2`。原补救说明让“缺 `statement_version` 的写当前题面版本”，而保存程序只检查版本号是否为非空字符串，判断不了它属于哪一版，旧停因可能被当作 `q2` 的结论。项目里确实已有缺版本号的旧评分，是否已被这样错挂尚未查到，同样不声称已证明。

**变更目的**：给“写不出”这个输入一个按原因区分的落点（未评 vs 0 分），并让旧记录补版本号之前先核对实际题面，而不是默认当前版本。

**关键差异**：
1. 硬要求改为“写不出时先分清为什么写不出”：只有已有证据满足既定 0 分条件（已证伪）才记 0；材料不足以判断时记 `null`（未评）并按 `pending`，写明待核的文献或方法。
2. 明确**全文是否查清独立于文献篇数判断**：三篇凑够但关键一篇只读到摘要、无法核对是否已用本稿方法，仍记「未评」。
3. 四处同口径（最初计数；后经更正为七处，见本文件最后的定向确认）改口：1 分判据的「基底或指标」句、硬要求段、「未评」段、「四种常见打错」第 1 条——避免只改一句、留下三处同义的反向说法。
4. 旧记录补救改为“先核对再补”：用旧记录里的 `question` 文字与当时保存的题面逐个比对，能对上某一版就补那一版，对不上就保留旧档、按当前题面重新判；并写明程序只查非空字符串、判断不了属于哪一版。

**不影响**：0 分判据本身（仍是“已证伪”一种来源两种情形）、三篇最低证据要求、九项权重与评分公式、`candidate_scores` 与 `verdicts` 的全部校验规则、组件代码（本轮不改 `_state.py`）。

**受影响关口**：P2（规则落点与 owner）、P3（误用风险与兼容影响）、P4（可执行性：执行者能否按文字完成核对）。P1 复用：两条均来自用户复核与对现行文本的直接引用。

**检查方式的更正（同一轮内）**：此前 RP-18 的文档部分用仓库外一次性脚本判定并以 `PASS n checks` 计数作为通过条件。按 `Test Engineer Rule.md` 第 3 节，文档类目标直接阅读足以判断时不得新增专用采集器、自定义判定器或逐项证据账本，该做法属禁止事项。本轮起改为**直接阅读并按观察点逐条记录结论与依据**；测试计划已同步删除脚本判定器与 `PASS n checks` 通过条件。各轮历史记录里的脚本计数保留为历史，不再作为现行判定依据。本计划的本轮改动不含产品代码。

审核对象校验值：`implementation-plan.md` SHA256 `cfeaed144d680ae30f5ad042f9f77bea6032d3a2ab31cb303958a18d775f9b9d`，`test-plan.md` SHA256 `b3af79818c85c3b62ea9bbdac54be97af4f9dee52e117166b41a4a639eab258f`（本轮补两条观察点，并删除脚本判定器与 `PASS n checks` 通过条件），`skills/research-proposal/references/candidate-scoring.md` SHA256 `f213cc4010294ef727afc608c0bb403fa8866b4b3c928cfd1905eb5f63f5d868`。

**定向修正与结论 `APPROVED`（2026 年 11 月 28 日，第六轮）**。审核者对 `8d799819…` 给出 `APPROVED`（P1–P4 全 PASS、`Gate review completeness: COMPLETE`），并确认：两条缺陷原文确实存在于上一版（`:58` 的“写不出，按 0 分”与 `:391` 的“写当前题面版本”）；保存入口只判非空字符串（`_state.py:760-766`）；本轮属既有规则的表达修正，不是新增产品要求；六处改口一致、未出现“把已确认没有变化也记成永远 pending”的新误用；计划没有把“历史误判由这句话触发”写成已证事实，表述恰当；把文档检查从脚本计数改为直接阅读记录**不削弱覆盖**，删除被禁止的判定设施是从禁止做法回退到合规基线，不需要新批准。

审核者另提四项非阻断观察，本轮一并处理：

1. **“四处”与实际六处不符**：计划与记录写“四处”，实际改了六处（`:54`、`:58`、`:62`、`:94`、`:108`、`:399`）——未计入的两处正是原先只写“还没查够三篇”的门槛表与解释段。已改为“六处”，并分别说明“四处是原因写不出→0 的地方，两处是只写篇数不够的地方”。
2. **仍有只提篇数的摘要**：`SKILL.md` 第 59 行的判停摘要原只写“还没查够三篇记「未评」”，已补“或篇数够了但关键一篇只读到摘要、无法核对是否已用本稿方法，都记「未评」——篇数只是最低证据要求，读没读清要单独看”；`candidate-scoring.md` 的 `pending` 触发第一条也补了同一情形。
3. **旧记录核对未点名保存件位置**：文档与计划各补一句“旧题面在各修订目录的 `步骤-question-*.json` 里，可按本稿状态记录的路径找”，让 P4 的核对步骤可执行。
4. **测试计划文案重复**：RP-16 执行步骤末尾重复句已去重；“四处”同步为“六处”。

修正后对象：`implementation-plan.md` SHA256 `cfeaed144d680ae30f5ad042f9f77bea6032d3a2ab31cb303958a18d775f9b9d`、`test-plan.md` SHA256 `b3af79818c85c3b62ea9bbdac54be97af4f9dee52e117166b41a4a639eab258f`、`candidate-scoring.md` SHA256 `f213cc4010294ef727afc608c0bb403fa8866b4b3c928cfd1905eb5f63f5d868`、`SKILL.md` SHA256 `165d86e1eaa2044dac60c902937d908728adca18aca722ba49ff29c8283401f1`。前一轮 `8d799819…` 的批准按 `Plan Reviewer Rule.md` 第 6.3 节做影响分析后由本版沿用：只改计数、摘要措辞与保存件位置说明，未改 requirement、owner、机制、兼容性或失败策略。

**追加影响分析（第六轮后两处纯文字修正）**。在 `8d799819…` 获批后，计划又改了两处，均来自审核者自己的非阻断观察与测试计划关口的阻断项：①计数从“四处”更正为更准确的处数（审核者指出实际改动多于四处，未计入的是原先只写“还没查够三篇”的门槛表与硬门槛解释段；定稿口径为 `candidate-scoring.md` 七处加 `SKILL.md` 一处，见下）；②「旧记录怎么继续保存」第 2 条补 `步骤-question-*.json` 定位句——该句原先只出现在本轮新段、第 2 条没有，观察点指向第 2 条，故两处都补。两处都只改计数措辞与核对步骤的可定位性，未改 requirement、owner、change point、机制、兼容性、失败策略或 observability。**产品文档相对已审版本确有增加**：审核者审的是 `candidate-scoring.md` `68d42f76…`，定稿 `796288b5…` 在其上多了 `pending` 触发第一条的“或三篇虽已找齐但关键一篇只读到摘要”与 `步骤-question-*.json` 定位句，`SKILL.md` 也补了判停摘要；这两处正是审核记录 O-2、O-3 的处理，审核者重读后判无设计影响。`_state.py` 未变。按 `Plan Reviewer Rule.md` 第 6.3 节提交定向确认。


**定向确认（第 6.3 节影响分析）**：审核者复核后确认这两类修改属等价修正，可沿用 `8d799819…` 上的 P1–P4 `PASS` 与 `APPROVED`，未触及任何已审决定、无需重开 Gate；同时指出三处记录残留（计划观察点段仍写“文档四处”、计数未含 `pending` 触发第一条、以及“原先只在新段有”“产品文档未变”两处措辞与已审版本不符），均已按上段更正。
**最终对象**：`implementation-plan.md` SHA256 `cfeaed144d680ae30f5ad042f9f77bea6032d3a2ab31cb303958a18d775f9b9d`，`test-plan.md` SHA256 `b3af79818c85c3b62ea9bbdac54be97af4f9dee52e117166b41a4a639eab258f`（计划侧结论沿用，测试计划由测试计划关口单独确认）。

**定向确认（R-3 描述更正后）**：审核者逐处核对基线 `0e4eec7` 后确认计划的历史描述已与实际原文一致——①「基底或指标」句原为“说不出，按 0”、②硬要求段原为“写不出，按 0 分”、④「四种常见打错」原为“写不出按 0”这三处确属“写不出→0”；③原只写“还没查够三篇”；⑤门槛表与⑥解释段在伪空白分支外只写“还没查够三篇”；⑦`pending` 触发第一条原只写“近邻不足三篇”。并确认产品文档 O-1 的措辞（“未评项的 `evidence` 是必填的，并把同一项写进 `missing`”）与本组件行为一致，只是把既有校验写成执行者看得懂的步骤，不新增校验、不改判据或失败路径。**结论：`7b17bcbc…` 可沿用 P1–P4 `PASS` 与 `APPROVED`**，两处属 `Plan Reviewer Rule.md` 第 6.3 节等价修正，无需重开 Gate。

审核者另提一处可选措辞（`:537` 写“按原文性质分三类”而实际列四组），并明确“改与不改都不重开 Gate”。本轮**不改**：避免再次变更已确认的对象与 head，留待下次文字整理；已在此记录该项，不影响结论。

**可选措辞已采纳（同一轮内）**：审核者指出的“分三类、实际列四组”一项，其原话为“改与不改都不重开 Gate；若要改，改后重新取 SHA 并更新审核记录即可”。为使计划内部自洽，本轮采纳：把“按原文性质分三类”改为“分四组”，并同步 `implementation-review.md` 与 `test-results.md` 的分组口径（三处①②④原写“写不出→0”；③⑥⑤原只写“还没查够三篇”，其中⑤⑥在伪空白分支之外；⑦原只写“近邻不足三篇”）。该改动只影响描述措辞，不涉任何要求、观察点或判据。

**最终对象**：`implementation-plan.md` SHA256 `cfeaed144d680ae30f5ad042f9f77bea6032d3a2ab31cb303958a18d775f9b9d`；上一确认版 `7b17bcbc…` 的 P1–P4 `PASS` 与 `APPROVED` 结论按审核者授权沿用。`test-plan.md` 仍 `b3af7981…`，未变。
