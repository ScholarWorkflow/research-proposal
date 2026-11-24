# 讲稿与想定问答交付

计划版本：`rp-plan-interview-2026-11-24`。本文件补充 `plan/implementation-plan.md`
（`rp-plan-r4-markdown-2026-11-04`）未覆盖的面试交付与写作完成度两条要求；冲突时以
`implementation-plan.md` 的既有要求为准，本文件只增加内容，不撤回其中任何条款。

本文件记录新增的 `script`、`qa` 两项交付及其生效条件，以及研究计划的完成度界线。
它只描述当前契约，不记录之前的工作流程。

## 依据

用户在本轮明确提出两项要求：研究计划要写到什么程度（区分“对某方向感兴趣所以想
学”与“说清要弄清什么、怎么做”），以及面试发表时讲稿与想定问答的准备方式。前者
落在 `references/research-design.md`，后者落在本文件的交付约定。这两项不是既有计划
的推论，因此单独记为本次批准范围。

## 生效条件

`begin_revision` 的 `inputs.deliverables` 是本稿交付文件的唯一来源。省略时只交付
Markdown 正文；列出 `script`（发表讲稿）或 `qa`（想定问答）时，对应文件成为本稿
的正式交付，随该稿保存、导出、核对和提交。`docx` 不能列入。

`delivery_formats` 仍记录状态层面的格式，讲稿与想定问答的加选从
`inputs.deliverables` 读取，因此没有该字段的历史稿件行为不变。

本版之前的稿件状态只有 `materials`、`question`、`scheme`、`body`、`docx`、`md`、
`review` 七个步骤。`_load` 读回状态时把缺失的 `interview`、`script`、`qa` 补成
未开始，不改已有步骤、确认和条件；这些新步骤没有保存件，摘要为 `None`，因此不会
被 `_fingerprints_changed` 判成内容变化。未加选讲稿或想定问答时，`interview`
也不是必经步骤，`next_steps` 不列出它。

## 保存与检查

讲稿与想定问答共用 `save_revision(stage="interview")` 保存步骤，内容分别为
该步骤保存件的 `script`、`qa` 字段。检查项：

| 对象 | 检查 |
|---|---|
| 讲稿 | 页数与 `timing.slides` 一致；页码从 1 连续；每页有标题、正时长、非空讲稿；各页时长合计与目标时长的差、以及按字数折算的时长与目标时长的差，都不超过 `tolerance_minutes` |
| 讲稿 | `chars_per_minute` 落在 100 至 700 |
| 想定问答 | 条目非空；每条答案按每分钟字数折算不超过 `max_answer_minutes`；`required_categories` 中每个类别至少一条问题；`category` 必须属于声明的类别 |

检查不通过时仍保存内容，并返回 `needs_input` 与逐条问题；补齐后再次保存即可，
不需要重写全部内容。两项共用一个保存件，后一次保存会沿用步骤里已有的另一项，
本次请求显式给出的那一项覆盖旧值；因此只补缺的那一项就能通过检查。字数按非空白
字符统计，与语言和空格习惯无关。

这条保存规则有三个后果，调用方需要知道：

- 讲稿步骤只能覆盖、不能删除单项。要撤掉已经保存过的某一项，只能建立新的工作
  版本后只保存要保留的内容；写成空值不会清除。
- 保存过的内容一律参与检查，即使那一项没有加选。未加选的内容不通过时，讲稿步骤
  保持未完成，并阻塞已加选文件的导出。
- 取消加选不会自动清掉旧内容，旧内容仍按上一条继续检查。

## 生成与核对

`export_revision` 省略 `formats` 时生成本稿全部已选加文件，也可按名只补一份。
Markdown 由已保存内容重新生成，`review_revision` 读回文件后与重新生成的文本逐字
比较，摘要记录在 `checks.deliverable_digests`。用户手改导出文件会让核对失败，
必须回到保存入口更新内容，不能直接改 Markdown 后提交。

## 失效规则

| 变化 | 受影响步骤 |
|---|---|
| 正文或引用变化 | 讲稿、想定问答、Markdown 与 Word 交付，需重新生成 |
| 讲稿或想定问答内容变化 | 只影响对应的交付文件与核对，正文与 Markdown 保持完成 |
| 研究问题、中文方案、材料变化 | 连同讲稿、想定问答一起重做 |
| 加选或取消 `deliverables` | 属于本稿输入变化，受影响的交付步骤按规则失效 |

前三行由 `_state._DEPENDENT` 与 `_delivery_stages` 实现；加选或取消 `deliverables`
由 `_sync_work` 的输入比较和各步骤 `dependencies` 比较处理。覆盖情况：
`test/test_interview.py` 覆盖渲染、检查、保存、生成、核对、提交和失效，
`LegacyStateTests` 覆盖旧状态读取，`test/test_recovery.InterviewRecoveryTests`
覆盖失败与失效分支。

## 尚未包含

- 幻灯片本身（.pptx）：只交付讲稿文本，不生成或编辑幻灯片。
- 面试稿的语音合成与录音：不涉及。
- 学校要求的提交封面、页数上限以外的排版：仍按学校要项记录在稿件要求中，
  不在这两项文件的检查范围。

## 研究计划的完成度界线

`references/research-design.md` 的「写完到什么程度」一节是本次批准的产品要求，适用于
所有稿件，不只是加选讲稿的稿件。它给出四条底线（一句话说清要弄清什么、方法能落到
对象与数据、至少两种相反的可能结果、方案最大的两个弱点）和对应的「不必有」清单，
并要求写明弱点。它不改变学校栏目优先的原则，也不新增正文结构要求。

## 既有计划条目的更新

本文件生效后，`plan/implementation-plan.md` 中下列描述由本文件与实现代码取代，其余
条款继续有效：

| 原条目 | 当前取值 |
|---|---|
| `save_revision` 的 `stage` 取值 | 增加 `interview`，共五个 |
| 每稿 `steps` 的条目 | 增加 `interview`、`script`、`qa`，共十项 |
| `export_revision` 省略 `formats` | 生成该稿全部已选加文件，不再固定为 Markdown 一份 |

另有两处执行记录需要测试计划负责人更新，不在本文件的取代范围内：
`plan/test-results.md` 的「四份参考文件」检查项应改为五份（新增
`references/interview.md`）；`plan/test-plan.md` 尚未包含讲稿与想定问答的必测项。
