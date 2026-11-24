# 讲稿与想定问答交付

本文件记录新增的 `script`、`qa` 两项交付及其生效条件。它只描述当前契约，不记录之前的工作流程。

## 生效条件

`begin_revision` 的 `inputs.deliverables` 是本稿交付文件的唯一来源。省略时只交付
Markdown 正文；列出 `script`（发表讲稿）或 `qa`（想定问答）时，对应文件成为本稿
的正式交付，随该稿保存、导出、核对和提交。`docx` 不能列入。

`delivery_formats` 仍记录状态层面的格式，讲稿与想定问答的加选从
`inputs.deliverables` 读取，因此没有该字段的历史稿件行为不变。

## 保存与检查

讲稿与想定问答共用 `save_revision(stage="interview")` 保存步骤，内容分别为
该步骤保存件的 `script`、`qa` 字段。检查项：

| 对象 | 检查 |
|---|---|
| 讲稿 | 页数与 `timing.slides` 一致；页码从 1 连续；每页有标题、正时长、非空讲稿；各页时长合计与目标时长的差、以及按字数折算的时长与目标时长的差，都不超过 `tolerance_minutes` |
| 讲稿 | `chars_per_minute` 落在 100 至 700 |
| 想定问答 | 条目非空；每条答案按每分钟字数折算不超过 `max_answer_minutes`；`required_categories` 中每个类别至少一条问题；`category` 必须属于声明的类别 |

检查不通过时仍保存内容，并返回 `needs_input` 与逐条问题；补齐后再次保存即可，
不需要重写全部内容。字数按非空白字符统计，与语言和空格习惯无关。

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

`_state._DEPENDENT` 是这些关系的唯一实现位置；`test/test_interview.py` 与
`test/test_recovery.InterviewRecoveryTests` 覆盖保存、生成、核对、提交和失效。

## 尚未包含

- 幻灯片本身（.pptx）：只交付讲稿文本，不生成或编辑幻灯片。
- 面试稿的语音合成与录音：不涉及。
- 学校要求的提交封面、页数上限以外的排版：仍按学校要项记录在稿件要求中，
  不在这两项文件的检查范围。
