# 本地实现与正式测试结果

角色：本地执行工程师。当前执行进度见下表；正式第三关结论见 [test-plan-review.md](test-plan-review.md)，本记录不代作关口决定。

用户最新明确要求当前只把 Markdown 做对，停止 Word/LibreOffice 测试与排版调试。执行者已停止新增请求、转换和诊断，当前无活动请求。下文 r13 的双格式观察与未完成项是本次变更前的实际记录，不再据此继续 Word 测试，也不改写已有失败为成功。

**r21（2026-11-21）最新逐项结果见文末「r21：环境重建后的真实会话执行」一节。** 本文中 r15、r20 各节及其结果表是历史记录，不再作为本轮通过依据；r21 一节另列输入偏离、执行偏离与显示层瑕疵。

## r15：Markdown 单格式产品与正式执行

当前适用产品提交为 `e6ebaa4224e8d12f3ba7d9e6c60e2c31b4d4254c`（`feat/research-proposal`）。该线按已批准的 `rp-plan-r4-markdown-2026-11-04` 第 4、5 项把产品从双格式改为 Markdown 单格式；计划正文校验值保持 `4776b1d7…b5f9a`，测试计划保持 `bc8cd431…ec259`，均未修改。

提交沿革：

| 提交 | 作用 |
|---|---|
| `085a601` | 实现 Markdown 单格式交付、核对、提交与旧稿迁移 |
| `0a1c12f` | 记录已通过的 r4 执行计划与 r5/r14 测试计划 |
| `03f75f5` | 修正材料原文摘要未纳入失效判断 |
| `aade030`、`3c8d327` | 记录本轮执行结果；旧结果表加历史标注 |
| `9791023` | 按实现审核意见修正 IR-03、IR-04、IR-05、IR-06、IR-10、IR-11 |
| `3240c25` | 待确认事项先列本版交付格式；修正 RP-10 口径与字数测量方法 |
| `521792c` | 结果记录改为最终构建与 r18 结果根，补审核修正复验 |
| `bb0efb4` | 按 IR-12 修正：延期 Word 单独失效不再清空 Markdown 核对；补 r19 文字核对记录与字数口径说明 |
| `9fa15a8` | 结果记录改为 r19 构建与结果根 |
| `e6ebaa4` | 按 IR-12 残留修正：已提交稿按交付依赖键比较摘要；补 r20 文字核对记录（本次安装版本） |

当前结果根为 `RP_RUN=/private/tmp/research-proposal-r20-run.nERfV9`；消费者仍为 `RP_CONSUMER=/private/tmp/research-proposal-run.Ts9A0m/consumers/nix`，换版前完整归档在 `RP_RUN/archive/consumer-before`。四个 Nix 输出均从 `e6ebaa4` 的固定远端提交构建，退出 0，实际 store 路径为 `vm2r16fl…runtime`、`scg0qhbs…package`、`ngyk49dg…environment`、`kxbqgx6q…activate`；日志为 `logs/build-*.log` 与 `.exit`。激活器 `logs/activate.log` 退出 0。原样恢复的 `input` 与 `.test-runtime` 与换版前快照 `diff -r` 无差异。

两份真实稿件的状态在本次执行中经历两个不同节点，须分开记：换版安装与资料恢复后的归档状态是非论文 `state_version` 15、论文 14，两份的 `current` 均指向已提交版本目录；上一轮 RP-08 运行前曾把两份稿件重置为可重新走提交的基线，即非论文 10、论文 9 且 `current` 均为 `null`，该重置基线见两份旧 `requests/rp08-*/resume.json` 的 `expected_state_version`。该次重置属上一轮执行，本轮未重复，也没有把任何稿件的 `current` 重置回 `null`；本轮全部改稿都从磁盘上已提交的当前版本继续。

本轮（r20 纠正执行）经评估服务发真实写作与改稿请求，由主技能自己完成保存、导出、核对与提交，状态经多次递增而非从零重建。请求、响应与业务观察分别保存在 `RP_RUN/requests/` 下，逐项结果见下文「r20 真实会话纠正执行」。当前磁盘终态：论文 `state_version` 26、`current=r-20261104T134308-ac18eee9fd46`；非论文甲项目 72、`current=r-20261104T165248-ed68cb7c11d7`（场景 3 补做后）；RP-12 另建的乙项目稿 9、`current=r-20261104T132940-4c26fb1c72e0`。三份 `delivery_formats` 均为 `["md"]`、`committed=true`、`checks.content_consistent=true`；此后压缩请求另建了 `压缩稿/`（9 / `r-20261105T053247-76beb5300748`，同样 `["md"]`/`committed=true`/`content_consistent=true`），它不是甲稿的新提交版，见下文「压缩请求」；随后为在甲稿上生成新版本而按修正措辞重发的请求（`requests/rp08-length-compress-v2/`）因 provider 额度耗尽在模型产出前失败，未产生任何写入，故当前磁盘终态与上述相同（甲项目仍 72 / `r-20261104T165248-ed68cb7c11d7` / 8 项 / 1687 字），见下文「压缩请求 v2」；各稿历史版本目录全部保留，本轮未覆盖或删除任一已提交版本。RP-08 与 RP-12 判为通过；RP-10 四个场景均已取得有效通过结果，记「通过」，其中场景 3 的首次失败与补做过程保留在同一行内。

**早前结果根说明**：更换产品提交后，r15（`QznIep`）、r16（`jKCQmg`）、r17（`b802l1`）、r18（`sSVUTo`）、r19（`VtBIUl`，均在 `/private/tmp/research-proposal-r1*-run.*` 下）的构建、请求与日志均保留不动。下表的当前结论来自 r20 结果根；更早各根的同期结果只作过程记录，不重复计入通过。

审核修正项的复验记录：IR-03（已提交稿只比对交付格式内步骤）在 r18 构建上对两份真实已提交稿调用 `resume_revision` 均返回 `committed` 且无问题；IR-04（迁移不改写迁移前摘要）用「迁移前修改正文再迁移」的构造验证，`body` 与 `md` 均变为 `pending` 且 `content_consistent` 为 false；IR-05 提交返回只含 `md`；IR-06 用 `read_material` 实际写出的扁平 `材料.json` 验证，替换原件后返回 `committed_content_changed`；IR-10 省略 `template_path` 可正常建立工作版；IR-11 交付目录的 `研究计划待确认事项.md` 首列本版交付格式与已延期格式，并对先前记录条目注明格式承诺以本版为准。IR-09 已在 `logs/rp01-install-inspection.txt` 补齐配置条目检查。RP-10 的口径修正见下表。

第二轮定向复核新增 IR-12 与记录问题，已在 `bb0efb4` 处理：IR-12 把 `_invalidate` 的清空条件改为只在本版交付步骤失效时成立，使延期 Word 模板或映射变化不再清掉 Markdown 的 `checked_formats`；用生产包装器在 r19 构建上验证：仅改模板文件后 `resume_revision` 返回 `ready`、无问题，`review`/`md` 保持 `complete`，`commit_revision` 返回 `committed` 且 `artifacts` 只含 `md`；反向验证 Markdown 文件被改时 `md`/`review` 转 `pending`、`checks` 清空、提交被拒。IR-13 在 r19 结果根补了本根的 `logs/rp04-handoff-review.md`。IR-07 的字数口径补明「栏目标题计入、文献列表内容不计入」。

第三轮定向复核指出 IR-12 只修好未提交路径：已提交稿的恢复仍用整份快照比较，历史 `template_path` 的模板文件变化会误报 `committed_content_changed`。已在 `e6ebaa4` 修正：`_fingerprints_changed` 增加可选键过滤，`_committed_response` 只比对本版交付依赖键并纳入 `stage_files`。用生产包装器在 r20 构建上验证：已提交稿仅改模板文件后 `resume_revision` 返回 `committed`、无问题；改 Markdown 文件返回 `needs_input`/`committed_content_changed`；改正文、改已保存步骤文件同样返回 `needs_input`，检测能力未削弱。两份真实稿件提交后重报均为 `committed`。

### 实现符合性审核结论（第三轮定向复核后）

审核者：专用 `implementation_reviewer` 代理（`~/.codex/agents/implementation-reviewer.toml`，只读）。三轮审核所审 HEAD 依次为 `aade030`／`3c8d327`、`521792c`、`d84e305`。

已闭合（沿用）：IR-03、IR-04、IR-05、IR-06、IR-07、IR-08、IR-09、IR-10、IR-11、IR-12（含残留）、IR-13。审核者确认产品侧未发现仍在闭合的代码偏差；计划第 4、5、6、7、8 项主要行为已在生产入口实际落实，与 RP-01 至 RP-07、RP-11、RP-13 的当前结果一致。

未闭合项（均不属于产品修正缺陷）：

| 项 | 性质 | 负责人 |
|---|---|---|
| IR-14：`test-plan.md:406` 对 `reading-room.docx` 断言既写“不重跑”又给出会运行它的命令 | 计划文字口径冲突；修订会使已审计划校验值变化，需计划负责人出修订版 | 测试计划负责人 |
| RP-08 论文稿栏目与篇幅业务失败 | 已由本轮真实写作会话纠正（见下文 r20 记录）；原失败保留，不再作为未闭合阻断项 | — |
| RP-10 实际改稿会话（场景 3 首次失败、场景 4b 超篇幅） | 场景 3 已在正确基线上补做并取得有效通过结果（见下文 r20 记录与 RP-10 行）；首次整稿回退的原失败与根因保留，不再作为未闭合阻断项。场景 4b 篇幅见下行 | 场景 3 已闭合；场景 4b 负责人不变 |
| RP-12 第二项目会话（已执行） | 已核对通过（见下文 r20 记录），无未闭合偏差 | — |
| RP-10 场景 4b 正文超 1200–1600 字（上一版 1689 字、当前有效版 1687 字） | **仍未闭合**。已按决定人决定发 1 次真实压缩请求（`requests/rp08-length-compress/`），甲稿当前有效稿未变，仍 1687 字超上限；压缩成稿出在另建的独立编号稿件 `压缩稿/`（1215 字，在范围内），但甲稿篇幅问题未解决。该次记业务失败。根因为执行者提示词把「保留旧稿」与「单独交付」混写；主技能据此另建了独立稿件目录，并把这次 `begin_revision` 的 `inputs` 直接写成 `application_id=合成甲项目-联系教授-压缩稿`、`purpose=联系教授（甲项目压缩版本）`，该目录由此从一开始就是独立稿件（`_state.py:557–559` 在 `state is None` 时直接用本次 `inputs` 生成 `binding`）。`_state.py:502–505` 的 `different_proposal` 只在同一目录已有 `binding` 且本次输入不同时才提示另建，本次未触发（请求响应全文无该提示）。技能中「跨校另建稿件编号」以换学校为前提，本轮是同项目压缩，不属该情形，故该分支是执行端的绑定变更，不是产品按跨校规则产生的行为。另有 IR-25 至 IR-27 三项：该独立稿把「尚无系统古文书训练」改写成「不要求古文书训练」、材料步骤缺 `applicant_profile` 与 `application_requirements`、`引用定位.json` 的 `body_blocks` 未重映射且 `14` 越界，详见下文「压缩请求」。**其后按交接说明以修正措辞重发 1 次**（`requests/rp08-length-compress-v2/`），该次在模型产出任何内容之前因 provider 额度耗尽失败（`codexErrorInfo=usageLimitExceeded`，`turn.status=failed`、`durationMs=8307`、`items=[]`，仅 `thread.started`/`turn.started` 两条事件、无任何工具调用），**未取得业务结果、无业务副作用**（甲稿状态摘要请求前后同为 `4f744ddb…`，仍 72/`r-20261104T165248…`/8 项/8 个版本目录，其余四份稿件状态亦未变），属外部故障，既不记通过也不记业务失败。错误原文标明的额度恢复时间为 2026-11-10 16:05，恢复条件未成立，故按 `PROJECT_CONSENSUS.md` 与 `test-plan.md:472` **未再补发第二次请求**；本次建了线程但轮次在模型产出前失败，未取得业务结果，故不计为一次有效业务尝试。详见下文「压缩请求 v2」与 `RP_RUN/requests/rp08-length-compress-v2/business-observation.md`。 | 决定人：是否接受该独立稿，或待额度恢复后按已备的 v2 提示词重发；本地执行工程师已按一次请求即停的约定停止 |
| RP-10 场景 3 补做中观察到的三处记录偏差（差异描述与事实不符、`inputs.user_choices` 被清空、`研究计划待确认事项.md` 引号字形变化未列） | 不影响本场景判定（实际未回退、确认与正文未受影响）；如实记入 RP-10 行与请求观察记录，供后续改进，不另立必测项 | 本地执行工程师（已记录）；如需修复交产品实现负责人按计划判断 |

该段审核者结论为**部分完成**，针对第三轮定向复核范围（IR-12 及直接影响），不是本轮 r20 的结论；本轮 r20 的实现符合性审核结论见下文「r20 实现符合性审核」。两者都只说明实现落实情况，不构成计划关口、测试第三关或合并批准。

### 结果表（四状态）

| 编号 | 结果 | 说明与日志 |
|---|---|---|
| RP-01 | 通过 | 四输出构建与共享激活均退出 0。新产品提交的主技能、四份参考文件、模板、两个脚本、六项直接依赖、17 份原代理、无关示例技能 `unrelated-note` 及配置条目逐项存在，见 `logs/rp01-install-inspection.txt`、`logs/activate.log`、`logs/build-*.log`。 |
| RP-02 | 通过（沿用） | 本次提交未改技能资源布局，安装入口与文件集合同前。按 r14 只复核改写后的文档观察：README 明确 Nix 提供依赖与运行程序、npx skills 只装技能与资源且不提供上游代理和工具服务，实际文件见消费者内技能包与仓库 README。npx 安装命令未重跑。 |
| RP-03 | 通过 | `test_inputs.DiscoveryTests` 3 个方法退出 0，覆盖四种入口、缺候选及多对象/方向选择。见 `logs/rp03-components.log`、`.exit`。 |
| RP-04 | 通过 | `test_inputs.UpstreamRoutingTests` 退出 0，覆盖 collect、preview、stage0–stage2；stage3 采用 RP-03 同一次结果。安装后三份文件的逐分支文字核对符合，见 `logs/rp04-components.log`、`.exit`、`logs/rp04-handoff-review.md`。未调用上游代理。 |
| RP-05 | 通过 | `test_inputs.AnalysisRoutingTests` 退出 0，三个副本分别返回 stage0、stage1、stage2。见 `logs/rp05-components.log`、`.exit`。 |
| RP-06 | 通过（沿用） | 本次未改材料读取。载体与定位按 r14 复用既有结果；本轮 `test_inputs.MaterialTests` 退出 0（2 个方法），其中 `reading-room.docx` 断言按用户 2026-11-04 “保持现状”决定只作历史资产，不作本项通过条件。见 `logs/rp06-components.log`、`.exit`。 |
| RP-07 | 通过（沿用） | 两条路线的问题、条件与中文方案确认均保存在真实稿件状态中，本次未改研究设计、确认或条件判断；上一轮论文 `state_version` 9、非论文 10 的确认与条件在换版后原样保留，本轮在其之上继续改稿，未重置确认。 |
| RP-08 | 通过 | 本轮按计划第 102、158 行纠正执行方式：论文路线发了 3 次真实写作请求（`rp08-paper-writing` 首次未产生新稿，`-2` 产出新稿，`-3` 修正栏目标题用词），非论文路线发 1 次；每次都是对同一隔离消费者目录的新请求，明确点名已安装的 `research-proposal` 主技能，不预先灌入答案、不补写内部工具或保存步骤，由主技能自己走 `save_revision`→`export_revision`→`review_revision`→`commit_revision`。**论文日文路线**：`requests/rp08-paper-writing-2/` 产出 7 栏目、1854 字符的新提交版；随后 `requests/rp08-paper-writing-3/` 把第五栏标题「進度・可行性」中的中文词改为日文「進度・実現可能性」，新提交版 `state_version` 26、`current=r-20261104T134308-ac18eee9fd46`；七个栏目标题全为日文，正文 1856 字符（排除题目、含「参考文献」标题；再排除为 1852），在 1800–2400 内。该标题的 Pandoc 自动标识符仍沿用旧标题生成的 `進度可行性`，显示文本与栏目不受影响，未另作改动。**非论文中文路线**：`requests/rp08-nonpaper-writing/`，`state_version` 31、`current=r-20261104T125413-7d9cda35a792`；七个栏目齐全，正文 1465 字（同一口径；再排除「参考文献」标题为 1461），在 1200–1600 内。两条路线的 Markdown 与 `正文.json` 均经 `shasum -a 256` 与状态内 `checks.digests` 独立核对一致，`checks.content_consistent=true`、`checked_formats=["md"]`、`artifacts` 只含 `md`。上一轮用组件序列直接提交的旧稿（`requests/rp08-paper/`、`rp08-nonpaper/`，正文 2432 字、0 个栏目标题）原样保留为失败记录，未被覆盖。第 1 次真实请求 `requests/rp08-paper-writing/` 与两份 `attempt0-prepfail` 目录同样保留。**判定时点须分清**：RP-08 的通过结论针对该次交付版（非论文 `r-20261104T125413…` 1465 字、论文 `r-20261104T134308…` 1856 字符）。其后 RP-10 场景继续改稿，非论文甲稿当时 `current` 为 `r-20261104T132243…`（该版 1689 字；场景 3 补做后现 `current` 已推进到 `r-20261104T165248-ed68cb7c11d7`、1687 字），两版均超出 1200–1600，属 RP-10 场景 4b 的内容层结果，不回写为 RP-08 失败，也不掩盖。该超限随后经 1 次真实压缩请求处理（`requests/rp08-length-compress/`），成稿 1215 字在范围内但落在另建的独立编号稿件 `压缩稿/`，甲稿当前有效稿仍 1687 字；该次记业务失败，见下文「压缩请求」与未闭合项表。其后按修正措辞重发 1 次（`requests/rp08-length-compress-v2/`），该次因 provider 额度耗尽在模型产出前失败、无业务副作用，未取得业务结果，见下文「压缩请求 v2」。 |
| RP-09 | 未执行 | 用户已延期；本轮不运行 Word 模板、转填或页面检查。 |
| RP-10 | 通过 | 四个场景均取得有效通过结果（场景 4 另有一次选定后的后续请求，场景 3 另有一次以正确基线补做的请求与一次确认请求；含首次失败请求在内共 7 次），每次明确点名 `research-proposal` 主技能，提示词不写内部工具、参数或保存步骤。**场景 1、2、4、4b 的修改稿**由 RP-08 非论文交付稿的真实副本制作（原件 SHA-256 已逐份核对）；**场景 3 补做的修改稿**改由当时有效提交版 `r-20261104T132243-578af7cd25fe` 的真实副本制作，不再使用任何过期基线。**场景 1 纯措辞**（`requests/rp10-s1-wording/`）：正文逐行 diff 为 2 处段落、3 处措辞替换（道德裁决→不作简单的道德评判、力量差异改写、预期完成→预计完成），`question` 仍 `Q2-2`、`scheme` 仍 `scheme-2` 且 `confirmation_bindings` 与上一版完全相同，原确认被复用。**场景 2 核心方法改读者调查并改英文**（`rp10-s2-method-english/`）：`question` 确认复用（binding 不变），`scheme` 改为 `scheme-3-reader-response` 并重新确认，`decision.text` 记录用户明确要求；正文七个英文栏目、全英文，招募与伦理审查在正文和 `pending_items` 中写为待定，未夸大为已获批准。**场景 3 文件自行写成已取得**：首次尝试（`rp10-s3-unverified-condition/`）**业务失败**，**已由补做闭合**，原失败与根因保留，未被覆盖。主技能确实识别出「已取得手稿许可、已完成版本比对」与已保存记录冲突、保留了原件、没有把条件改成已取得；但该次提交版 `r-20261104T131559-ad231a209f02` 的 `研究计划草稿.md`（`453ce3ae…`）与 `正文.json`（`c536b9d5…`）和 RP-08 交付版 `r-20261104T125413-7d9cda35a792` 逐项相同，`confirmation_bindings` 也回到 `Q2-2`/`scheme-2`。即相对真正的上一提交版 `r-20261104T131001-71b8523f8b64`（英文、读者调查）是整稿回退，丢弃了场景 1 的措辞改动、场景 2 的授权方法改动与英文交付、以及场景 2 的方案重新确认，与 `test-plan.md:114` 要求的「未受影响成果继续使用」「实际差异进入正式正文与新版本」相反。根因可定位：执行者用过期的 `修改稿/base-rp08-交付稿.md` 制作该场景修改稿，主技能以 `/tmp/rp-base.json` 作 `baseline_body`（`baseline_digest=cf97eefa…`），回退未被发现。另技能参考要求「意图不明的实质变化先展示改变及影响，再取得决定」，该次也没有把该项交回用户。该失败属测试准备层的错误基线，不是产品在给定错误基线时的行为违规（`plan/test-plan.md:114` 要求未受影响成果继续使用、实际差异进入正式正文，产品在错误基线下并未违反）；按 `Test Engineer Rule.md` 第 6 节的修订复核，以正确基线补做一次。**补做（`rp10-s3-retry/` 与 `rp10-s3-retry-confirm/`，两次请求）**：基线取自当时有效提交版 `r-20261104T132243-578af7cd25fe`（`state_version` 63，正文 `69e8d952…`、Markdown `6d7acc1f…`，摘要与状态内 `checks.digests` 逐项核对相同），修改稿由该版 Markdown 复制后只把「进度与可行性」第二段改成「已取得私人手稿许可、已完成版本比对」，不附说明（`9caa30d1…`）。第一次请求中主技能以该版正文为 `baseline_body` 导入（`baseline_digest=69e8d952…`，原件副本 `9caa30d1…` 保留），识别出冲突与「待核、手稿不是必要条件」的旧记录相冲突，**未写入正式正文**，状态保持 63/`r-20261104T132243…`/7 项稿件、确认仍 `Q2-B-1`/`scheme-B-2`，并向用户提出修改范围与新增条件两项选择。第二次请求由执行者扮演合成申请者作答（只授权进度段、删除未证实说法、不以 `原件/rp08-交付稿.md` 为基准），主技能据此只改第 12 块并提交新版：`state_version` 72、`current=r-20261104T165248-ed68cb7c11d7`、`works` 8 项、`committed=true`、`delivery_formats=["md"]`、`checks.content_consistent=true`，Markdown `b826206b…` 与正文 `aea0ad4e…` 均等于状态内 `checks.digests`。逐块比对：17 块中 16 块逐字节相同，只有第 12 块变化；七个栏目、题目、背景、问题、方法、预期成果、参考文献及进度第一段均未动；正式正文中「获批／已取得／已完成版本／逐处核对一致／三者可互相印证／研究条件完全具备」出现次数均为 0，原典待核与替代办法保留，末句改为「研究将以可取得的公开文本和校注本为基础」；`question` 仍 `Q2-B-1`、`scheme` 仍 `scheme-B-2`，`decision.text` 与 `source` 与上一版逐字相同；上一版目录全部保留且摘要未变，`原件/` 未改。据此该场景判定**通过**：原件保留、只确认受影响部分、未受影响成果继续使用、导入事实无材料依据者未进入正文、未只改 Markdown 而声称正文同步。补做中另观察到三处不影响本场景判定的记录偏差，如实保留：其一，第一次请求把修改稿差异描述为「题目、相关研究、问题、方法、外围语料、成果、参考文献等也都变了」，实际只有第 12 块一段变化（另第 4 块为 `“`→`”` 引号字形），该清单与上一次失败请求留下的过期导入记录逐项吻合，且它把等于 RP-08 交付版的 `原件/rp08-交付稿.md` 列为可选基准，属汇报环节偏差，实际未造成回退；其二，新版的 `inputs.user_choices` 由 `{"comparison_method": "跨文本互文对照；用户本轮明确选择B"}` 变为 `{}`，权威决定记录与正文未受影响；其三，新版 `研究计划待确认事项.md` 的「连续场景链」引号由单弯引号 `‘’`（`6f130128…`）变为双弯引号 `“”`（`0f0ae027…`），`pending_items` 元数据同形变化，文字与条目含义不变，该文件不在正文 17 块之内。两版 Markdown 反向转正文时第 4 块引号字形均与各自 `正文.json` 不同，该差异在本次请求之前即已存在，非本次引入。**场景 2 成果当前已不在有效稿中**：场景 3 首次尝试的提交版把甲稿 `current` 指回 `r-20261104T131559-ad231a209f02`（内容等于 RP-08 交付版），此后场景 4b 又在其上重写；场景 2 的英文正文与 `scheme-3-reader-response` 只留在 `r-20261104T131001-71b8523f8b64` 目录内，不再存于当前提交稿，记录不得据此声称该成果仍在有效稿中；场景 3 补做以当前有效版为基线，未恢复该英文成果，也未声称恢复。**场景 4 两份冲突方法稿**（`rp10-s4-conflict/`）：基准是场景 3 的提交版（内容等于 RP-08 交付版，见上），两份均只替换「方法与判断办法」段；两份均导入并保留（A `9c9603f3…`、B `dc30f9d3…`），保存 `修改稿/比较/差异说明.md` 并列明差别，状态版本与 `current` 在请求前后不变、`works` 未增加，未按修改时间自动合并。执行者随后扮演合成申请者选定 B（`rp10-s4b-select-b/`），主技能按选择更新 `question`→`Q2-B-1`、`scheme`→`scheme-B-2` 并单独确认，正文七栏目同步改写；该版正文 1689 字超 1200–1600，属内容层结果，不影响本场景对「冲突选择与受影响确认」的判定；篇幅本身未按当场改稿请求压缩，作为未完成项保留。 |
| RP-11 | 通过 | `test_recovery.RecoveryTests` 8 个方法全部退出 0，覆盖首次导出失败无当前稿、Markdown 导出失败后恢复、内容不一致不提交、步骤中断续接、目录改名与指针替换两种提交中断、材料/正文/选择变化失效、另一轮先更新基准。见 `logs/rp11-components.log`。 |
| RP-12 | 通过 | 按计划先复制 `test/fixtures/applications/program-b.md` 到消费者 `input/nonpaper/` 并 `test -r` 成功后，从甲项目已提交稿发第二项目请求（`requests/rp12-program-b/`），明确复用文献与通用方案。新建独立稿件 `input/nonpaper/研究计划/乙项目-面试准备`：`proposal_id=proposal-cd05aa50…`（与甲 `proposal-f6f5fff7…` 不同）、`binding={合成乙项目, 面试准备, Q2-B-乙}`（甲为 `{合成甲项目, 联系教授, Q2}`）、`state_version` 9、`current=r-20261104T132940-4c26fb1c72e0`；五栏目（拟研究的问题／选题依据／实施步骤／条件与替代办法／参考文献）与 830 字（同一口径；再排除「参考文献」标题为 826）均按乙项目要求，未沿用甲的七栏目与 1200–1600 字。复用来源记录在 `inputs.material_paths`，乙稿内 `confirmations` 为 `乙-Q2-B-1`／`乙-scheme-B-1` 独立确认。请求前后甲项目状态与 7 个版本目录内容一致（创建乙稿未改动甲稿）。林安稿在 RP-12 请求窗口（13:27:30–13:31:31 UTC）内未变：该稿在窗口前后同为 `state_version` 20 / `r-20261104T130101-eb70c825dea3`；其后该稿推进到 26 / `r-20261104T134308-ac18eee9fd46` 来自 13:41:57 的独立请求 `requests/rp08-paper-writing-3/`，与 RP-12 无关，不能算作 RP-12 的影响，也不能据此声称当前磁盘值与 RP-12 前快照相同。 |
| RP-13 | 通过（沿用） | 缺资料与缺视觉配置分支原结果保存在旧结果根，本次未改发现、材料或缺项路径。 |

### 本轮实际命令

组件检查均从 `$RP_WORKTREE/test` 用固定运行包解释器执行，实际命令形如：

```bash
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v test_inputs.DiscoveryTests
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v test_inputs.UpstreamRoutingTests
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v test_inputs.AnalysisRoutingTests
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v test_inputs.MaterialTests
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v test_inputs.RevisionImportTests
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v test_recovery.RecoveryTests
```

RP-08 上一轮通过安装后的公共包装器 `$RP_CONSUMER/.agents/skills/research-proposal/scripts/proposal-runtime <操作> --request <JSON>` 执行，请求与结果按操作分别保存在 `requests/rp08-paper/` 与 `requests/rp08-nonpaper/`。该序列只有四个组件调用、没有评估请求，与本轮计划要求不符，已作为执行偏离保留，不据此计为通过。

### r20 真实会话纠正执行

本轮按计划第 102、158 行与 Test Engineer Rule 重新执行 RP-08、RP-10、RP-12。三条硬约束逐条落实：所有业务结果都经评估服务发真实请求，由主技能自己写作与保存；未把任何稿件状态重置回 `current=null`；未手改任何 `正文.json` 或 Markdown（三份当前稿的 `研究计划草稿.md` 与 `正文.json` 用 `shasum -a 256` 复核，都与状态内 `checks.digests` 相符）。

**请求方式**：`EVAL_PORT` 从 `/Users/rekidunois/code/skill-repos-dev/eval-server` 用 `direnv exec . bash -c 'echo $EVAL_PORT'` 取得，实际值 `17902`，请求前 `lsof` 确认 LISTENING。每个请求按 `requests/rp13-school/` 的结构保存，含 `eval-request.json`、`prompt.txt`、`preparation.json`、`curl.exit`、`http-status.txt`、`response.json`、`times.txt` 与 `business-observation.md`。全部请求 `command` 形如：

```bash
--cd $RP_CONSUMER --model gpt-6-luna --sandbox workspace-write -- '<prompt>'
curl -sS -X POST http://127.0.0.1:17902/eval -H 'Content-Type: application/json' \
  --data-binary @<run_dir>/eval-request.json
```

发送脚本与提示词原文在仓库外 `/private/tmp/research-proposal-r20-exec-scripts/`，未写入工作树。各请求的总索引另存在 `RP_RUN/requests/INDEX.md`。

**逐请求结果**（前 12 行全部 HTTP 200、`curl.exit=0`、`passed=true`、`backend=app-server`、`termination_reason=completed`；末尾三行为压缩相关请求，逐行另注 HTTP 状态与判定）：

| 目录 | 项 | 结果 | 关键证据 |
|---|---|---|---|
| `rp08-paper-writing` | RP-08 论文第 1 次 | 未生成新稿，作执行问题保留 | 主技能误判「已完整交付」直接答复；状态仍 14、`works` 仍 1 项、Markdown 摘要仍 `e4b863a2…` |
| `rp08-paper-writing-2` | RP-08 论文第 2 次 | 通过 | 新提交 `r-20261104T130101-eb70c825dea3`，7 栏目、1854 字符 |
| `rp08-paper-writing-3` | RP-08 论文栏目用词 | 通过 | 新提交 `r-20261104T134308-ac18eee9fd46`，七栏目全为日文、1856 字符 |
| `rp08-nonpaper-writing` | RP-08 非论文 | 通过 | 新提交 `r-20261104T125413-7d9cda35a792`，7 栏目、1465 字 |
| `rp10-s1-wording` | RP-10 场景 1 | 通过 | 2 处段落、3 处措辞替换；`confirmation_bindings` 与旧版完全相同 |
| `rp10-s2-method-english` | RP-10 场景 2 | 通过 | `scheme`→`scheme-3-reader-response` 并重新确认，正文七英文栏目 |
| `rp10-s3-unverified-condition` | RP-10 场景 3 首次 | 业务失败（已闭合） | 识别「已取得」并恢复真实状态、原件保留；但提交版整稿回退到 RP-08 交付版，丢弃场景 1/2 成果（IR-15）。根因为执行者用过期基线，见 RP-10 行 |
| `rp10-s3-retry` | RP-10 场景 3 补做（以当前提交版为基线） | 有效：识别冲突并暂停，未回退 | 基线 `r-20261104T132243…`（正文 `69e8d952…`、Markdown `6d7acc1f…`）；`import_revision` 以该正文为 `baseline_digest`，原件副本 `9caa30d1…` 保留；未写正式正文，状态仍 63/7 项、确认未变；提出修改范围与新增条件两项选择 |
| `rp10-s3-retry-confirm` | RP-10 场景 3 补做（答复产品选项后提交） | 通过 | `state_version` 72、`current=r-20261104T165248-ed68cb7c11d7`；17 块中 16 块未动、只改第 12 块；未证实许可与比对表述出现次数为 0；`Q2-B-1`/`scheme-B-2` 逐字沿用；旧版保留 |
| `rp10-s4-conflict` | RP-10 场景 4 | 通过 | 两份均导入保留，状态版本与 `current` 前后不变，未自动合并 |
| `rp10-s4b-select-b` | RP-10 场景 4 选择 | 通过 | 用户选 B 后 `question`→`Q2-B-1`、`scheme`→`scheme-B-2` 单独确认 |
| `rp12-program-b` | RP-12 | 通过 | 独立 `proposal_id`、`binding`、五栏目、830 字，甲稿与林安稿未变 |
| `rp08-length-compress-attempt0-requestformat` | 压缩第 0 次 | 未发出（HTTP 400） | `command` 中 prompt 未加引号，评估服务在任何 Codex side effect 前返回 400；基线摘要未变，未消耗业务尝试 |
| `rp08-length-compress` | 压缩第 1 次 | 业务失败 | 甲稿未变（仍 72/`r-20261104T165248…`/1687 字）；成稿出在另建独立编号稿件 `压缩稿/`（9/`r-20261105T053247…`、1215 字、七栏目、确认沿用）；根因为提示词末句暗示另建稿件（IR-24），另有 IR-25 至 IR-27 |
| `rp08-length-compress-v2` | 压缩第 2 次（修正措辞） | 外部故障，未取得业务结果 | provider 额度耗尽（`usageLimitExceeded`），`turn.status=failed`、`durationMs=8307`、`items=[]`，仅 `thread.started`/`turn.started`，无工具调用；甲稿状态前后同为 `4f744ddb…`（72/`r-20261104T165248…`/8 项），无业务副作用；恢复时间标为 2026-11-10，未补发 |

**RP-08 论文第 1 次的处理**：该次提示词只描述「按 program-a.md 交付」，未指出已提交稿的实际缺口，主技能核对状态后按「已提交且核对一致」作了答复，没有重写正文。这不是产品缺陷，而是执行者提示词未提供用户可见的真实缺口。记录保留在 `requests/rp08-paper-writing/business-observation.md`；第 2 次请求改为把「无栏目标题、排除题目 2456 字符超上限」作为用户反馈给出，不含任何内部工具或保存步骤，一次通过。两次请求各保留，未覆盖。

**篇幅口径**：统一按 `正文.json` 的 `Para`/`Header` 顶层块拼接全部 `Str` 文本，排除题目块（第 0 块），文献列表内容不计入（栏目标题本身计入），与上一轮记录口径相同，不因结果变化改口径。

**清理与基线**：`原件/` 目录建于 21:18:02（北京时间），即场景 3（13:14:06–13:16:52 UTC = 21:14:06–21:16:52）**结束后**才把 `base-rp08-交付稿.md` 从 `修改稿/` 移到 `原件/`。该文件在场景 3 期间仍在 `修改稿/` 并被转成基线，正是 IR-15 整稿回退的直接原因；「RP-10 开始前已清理」的说法与时间线不符，已更正。场景 4 的两份冲突稿随后从当时的当前交付稿重建，保证只改方法段。RP-12 快照先于请求采集时 RP-10 场景 4b 仍在运行，采集到的甲项目状态属中间态（54 / `r-20261104T131559-ad231a209f02`）；按 mtime 核实请求发出时刻（13:27:30 UTC）的基线为 63 / `r-20261104T132243-578af7cd25fe`，且该状态在请求后未被再次写入，故以磁盘当前值作对照成立。说明见 `RP_RUN/snapshots/pre-rp12/BASELINE-NOTE.md`。

**未改变的环境**：评估服务未启停，消费者 `.codex/config.toml` 未修改，未新增依赖或环境变量；每个请求都以 `--model gpt-6-luna --sandbox workspace-write` 同一配置发出，未因结果不满意重采样或改输入。

### 正式尝试与失败保留

1. 首次换版把提交 `0a1c12f` 的四个输出构建到 `r15` 结果根，退出 0。随后发现该提交的产品实现不足以通过 RP-11 的“恢复前原文改变”分支：状态摘要只覆盖材料读取记录本身，记录指向的原件被替换时不会使既有正文与 Markdown 失效。该次结果不再作为最终依据，日志保留在 r15 结果根 `/private/tmp/research-proposal-r15-run.QznIep`。
2. 针对上述产品缺陷提交 `03f75f5`：按记录内 `original_path` 计算原文摘要并纳入依赖与失效判断，旧记录缺该摘要项时按原样处理，不把历史已提交稿判为改动。重建 r16 结果根后复跑受影响项；后续两轮审核修正再重建 r17、r18 结果根。
3. r16 首次执行 RP-11 时因本机未导出 `RP_TEST_OUTPUT` 等绑定，8 个方法在 `setUp` 报 `执行前须绑定`，未进入任何产品断言。该次输出保留在 r15 结果根 `/private/tmp/research-proposal-r15-run.QznIep/logs/rp11-components-attempt1-envbind.log`，属执行绑定错误而非产品结果；修正绑定后重跑取得上表结果。
4. 论文路线第一次 `resume_revision` 后 `md` 步骤失效。核对原因为该稿 Markdown 在 r13 被手工改写过（现文件摘要 `e5a1de08…`，导出记录摘要 `e4b863a2…`，即既有 `paper-05` 事实），产品判为导出后修改并要求重做导出与核对属预期行为；重新导出、核对、提交成功，原手改稿未被覆盖为成功状态。
5. RP-08 论文日文稿的栏目与篇幅失败不是本轮产品改动造成的：正文 2432 字超上限、`Header` 块为 0 的事实自 r13 `paper-04` 起就存在，本轮产品改动只涉及交付格式、核对、提交与恢复，不生成正文内容。该失败已在 r20 真实写作会话中按真实改稿请求纠正（新提交 7 栏目、1854 字符），原失败与其记录保留，不改写为成功，也不以重新采样或修改测试取得通过。
6. r20 首轮由执行者直接写提示词、未指出用户可见的正文缺口，论文路线第一次请求因此没有重写正文（`requests/rp08-paper-writing/`）。该次属执行偏离，不记为产品业务失败，也不删除；改为把实际缺口作为用户反馈后重发一次并通过。保存的旧 `requests/rp08-paper/`、`rp08-nonpaper/` 四组件序列同样保留为执行偏离证据，不再作为 RP-08 通过依据。

### r20 实现符合性审核

审核者：专用 `implementation_reviewer` 代理（`~/.codex/agents/implementation-reviewer.toml`，只读）。首审 HEAD `738766d`，定向复核 HEAD `ad95324`；产品 `e6ebaa4224e8d12f3ba7d9e6c60e2c31b4d4254c` 未改动（`git diff e6ebaa4..HEAD -- skills test flake.nix` 为 0 行），计划校验值 `4776b1d7…` 与 `bc8cd431…` 实测一致。

结论：**部分完成**。RP-08 与 RP-12 已核对齐全、判为通过；RP-10 场景 1、2、4、4b 的确认与版本选择可核对，场景 3 业务失败并不成立为通过。审核提出四项：

| 编号 | 问题 | 处理 |
|---|---|---|
| IR-15 | RP-10 场景 3 提交版整稿回退到 RP-08 交付版，丢弃场景 1/2 成果与场景 2 的方案重新确认；记录当时写成「其余文本不变」 | 已按四状态把场景 3 改记业务失败，在 RP-10 行写明回退范围与根因；补做范围交测试计划负责人 |
| IR-16 | 「RP-10 开始前已清理 `base-rp08-交付稿.md`」与时间线不符，该文件在场景 3 期间仍在 `修改稿/` 并被当作基线 | 已改为按 mtime 核实的真实时序，并注明它正是 IR-15 的直接原因 |
| IR-17 | 场景 1 记为「两处措辞」，实际为 2 处段落、3 处措辞替换；RP-08 行写「各发一次」，实际论文路线发 3 次 | 已按实际计数改写两处表述 |
| IR-18 | 未闭合项表与 RP-10 行状态不一致，场景 4b 超篇幅与场景 3 回退未入表；旧结论段落未标注适用范围 | 已补两项未闭合项，并把旧结论标注为第三轮定向范围；两行标题「未执行」句式亦已按实际执行状态改写 |

审核者定向复核结论（文字残留修正于 `6211a9e`、`6c8b4bc`、`3bb7455`）：IR-15、IR-16 已闭合；IR-17、IR-18 在 `test-results.md` 内已闭合，但结果根的 `INDEX.md`、`requests/rp10-s1-wording/business-observation.md` 与两行表标题仍有文字残留，已按同一编号修正（本表所列处理即修正后状态）。复核仍判**部分完成**，原因由「记录未反映回退」变为「文字层残留」，不构成重跑任何请求的理由。

审核者同时确认：该次审核时所见的三份稿件（论文、甲项目非论文、乙项目）的 `delivery_formats=["md"]`、`committed=true`、`checks.content_consistent=true`、`artifacts` 只含 `md`；10 个请求 `thread_id` 互不相同、`prompt.txt` 均点名主技能且不含内部工具名；`base_revision` 链与 `works`/`版本` 目录集合逐项相等，`current` 始终非空，无重置；各版本 `研究计划草稿.md`、`正文.json`、`引用定位.json` 的 SHA-256 全部等于状态内 `checks.digests`。该结论不代表计划关口、测试第三关或合并批准。上述「10 个请求」指该次审核覆盖的请求范围；本轮随后为场景 3 补做另发 2 次请求（`rp10-s3-retry`、`rp10-s3-retry-confirm`，`thread_id` 分别为 `01a1a76a-9fd5-7e73-a960-67d411c7a21f` 与 `01a1a779-8acd-7b71-8e3f-ce45c0a7ce88`，互不相同），请求总数变为 12 次，其后又发出 1 次压缩请求（`requests/rp08-length-compress/`，`thread_id` `01a1aa30-9485-7012-aa9a-311d05f6395e`，与前 12 次互不相同），本轮业务请求合计 13 次；再随后发出 1 次修正措辞的压缩请求（`requests/rp08-length-compress-v2/`，`thread_id` `01a1abd3-33c8-7a70-9ded-16b916b83178`，与前 13 次互不相同，该次建了线程但轮次在模型产出前因 provider 额度耗尽失败，未取得业务结果）；实测 HTTP 请求合计 15 次（14 次 200、1 次 400），其中 13 次以 `termination_reason=completed` 结束、1 次为 `turn_failed`，另有 4 个无 HTTP 状态的目录属上一轮执行偏离与准备报错；新增事实见 RP-10 行、「场景 3 补做」小节、「压缩请求」与「压缩请求 v2」小节。

### 场景 3 补做（以当前有效提交版为正确基线）

按 `Test Engineer Rule.md` 第 6 节，本次只复核受影响项：场景 3 因测试准备层的错误基线未取得有效结果，以当时有效提交版补做一次；其余项目未重跑，原结果继续复用。

- **基线来源**：`RP_RUN/requests/rp10-s3-retry/baseline/` 内 `正文.json`（`69e8d952…`）、`研究计划草稿.md`（`6d7acc1f…`）、`导出记录.json`（`52b7fd23…`）、`研究计划待确认事项.md`（`6f130128…`）直接复制自 `版本/r-20261104T132243-578af7cd25fe/`，与状态内 `checks.digests` 逐项相同；未使用 `base-rp08-交付稿.md`，未使用 `/tmp` 下任何旧基线 JSON。
- **修改稿**：`修改稿/scenario-3-retry-unverified-condition.md`（`9caa30d1…`），由上述当前 Markdown 复制后只改「进度与可行性」第二段，写入「已取得私人手稿许可、已完成逐处版本比对」等与材料记录冲突的表述，文件内不解释意图。与当版正文逐块比对：17 块中 15 块相同，差异仅第 4 块（引号字形）与第 12 块。
- **两次请求的实际结果**：见「逐请求结果」表中 `rp10-s3-retry` 与 `rp10-s3-retry-confirm` 两行，以及 `RP_RUN/requests/rp10-s3-retry/business-observation.md`、`.../rp10-s3-retry-confirm/business-observation.md`。
- **观察点逐项**（`plan/test-plan.md:114`）：原件保留（满足，副本摘要与源文件相同）；意图不明的实质变化只确认受影响部分（满足，先暂停并只就把两项提问，用户只授权进度段与删除未证实陈述）；未受影响成果继续使用（满足，确认为 `Q2-B-1`/`scheme-B-2`、七栏目与其余 16 块逐字节未动）；导入事实要有材料依据（满足，未证实表述进入正式正文的次数为 0）；不得只改 Markdown 后声称正文同步（满足，走完整导出、核对、提交，`content_consistent=true`）。
- **结论**：场景 3 通过，RP-10 四个场景均取得有效结果，结果表记「通过」。首次失败与其全部产物原样保留，未覆盖。
- **定向复核**：专用 `implementation_reviewer` 代理（只读）复核 HEAD `5df4e45`，逐项核对 14 个要点，结论**完整**。审核独立确认：基线 `baseline/` 四文件与 `版本/r-20261104T132243-578af7cd25fe/` 逐字节相同、导入记录 `baseline_digest=69e8d952…` 且未指向 `/tmp`、第一次请求结束时正文与 `state_version` 63 未变、第二次请求走完 `resume`→`begin`→`save`→`export`→`review`→`commit` 并返回 `committed`、8 个版本目录摘要全部等于各自 `checks.digests`、确认与 `conditions`/`mapping` 两版 JSON 完全相等、未证实表述出现次数为 0、12 次请求 `thread_id` 互不相同、本轮只改 `plan/test-results.md`（+19/−6）且未改产品与消费者配置、另两份稿件未被牵连。审核另提出两项记录层问题并已在本次落实：IR-19（场景 4b 行首只写 1689 字，与当前有效版 1687 字并存易被误读）已改为同时列明两版数字与两种口径；IR-20（`rp10-s3-retry-confirm/business-observation.md` 把第 12 块写成「进度与可行性第三段」）已改为「第二段」并注明该栏目标题在第 10 块、学年安排段在第 11 块。审核同时接受前两项已记录偏差不影响本场景判定，并备案 `待采用正文.json`/`待采用正文.md` 为中间产物、不在 `checks.digests` 与 `artifacts` 内。两次复核结论均为**完整**：首轮（HEAD `5df4e45`）核对 14 项要点并提出 IR-19、IR-20；次轮（HEAD `59490da`）确认 IR-19、IR-20 闭合并提出 IR-21..IR-23；第三轮（HEAD `f4c4a8d`）确认 IR-21..IR-23 闭合、未引入新偏差，IR-15..IR-23 在本轮范围内全部闭合。本结论只说明实现与记录落实情况，不构成计划关口、测试第三关或合并批准。

## 压缩请求（甲项目非论文稿压到 1200–1600 字，2026-11-05）

按决定人决定发一次真实压缩请求，不修改项目要求、不换字数统计口径、不手改正文或 Markdown、不重置 `current`。结果：**业务失败**，阻断项未闭合。

- **基线核对（请求前实测，非副本、非 `/tmp`）**：甲项目 `current=r-20261104T165248-ed68cb7c11d7`、`state_version` 72、`works` 8 项、7 个栏目标题。四文件摘要与状态内 `checks.digests` 逐项相同——Markdown `b826206b…`、正文 `aea0ad4e…`、引用定位 `071e3151…`，`导出记录.json` 的 `formats.md.digest=b826206b…`、`body_digest=aea0ad4e…`。请求前状态快照 `RP_RUN/snapshots/pre-rp08-compress/state.json`（`4f744ddb…`）。
- **请求** `requests/rp08-length-compress/`：`prompt.txt` 只写业务要求（七栏目不变、压回 1200 至 1600 字、保留方案 B 的两则说话/连续场景链/相对前田的增量限定与逐页核读后再限定贡献、保留已提交稿），不写内部工具名、参数或保存步骤，不预先灌入压缩后正文。HTTP 200、`curl.exit=0`、`passed=true`、`backend=app-server`、`termination_reason=completed`、`exit_code=0`、`cleanup_status=unsubscribed`，线程 `01a1aa30-9485-7012-aa9a-311d05f6395e`，05:31:12→05:34:29 UTC。
- **业务结果**：请求结束时甲项目状态与请求前逐字节相同（`4f744ddb…`，仍 72/`r-20261104T165248…`/8 项/8 个版本目录），**甲稿当前有效正文仍 1687 字**（计划口径），超 1200–1600。主技能未在甲稿上新增提交版，改为新建独立稿件 `压缩稿/`：`proposal_id=proposal-8dc2bcd4…`、`binding={合成甲项目-联系教授-压缩稿, …}`、`state_version` 9、`current=r-20261105T053247-76beb5300748`，`committed=true`、`delivery_formats=["md"]`、`checks.content_consistent=true`，Markdown `11dfa75f…`、正文 `97936c74…`、引用定位 `da597987…` 均等于 `checks.digests`。
- **独立稿篇幅（三种口径）**：1215 字（计划口径，排除题目、含「参考文献」标题）；1211 字（再排除该标题）；1490 字（全块，含参考文献列表、去题目）；1494 字（含题目）。主技能自报「1231 字（去空白字符、参考文献不计）」为其自有口径，不替代计划口径。
- **实质内容保留**：七栏目齐全；`question` 仍 `Q2-B-1`、`scheme` 仍 `scheme-B-2` 且均 `confirmed`，两份步骤文件与甲稿当前版 `diff` 无差异；两则说话题名各出现 2 次、「连续场景链」2 次、夺衣 6 次、「逐页核读」3 次、「不主张首次发现双源」保留；未证实表述（已取得／已获批／已完成版本／逐处核对一致）出现 0 次；参考文献 5 条与甲稿当前版逐字相同；题目逐字节相同。**但该独立稿有三处不能算作「实质内容保留」的完整实现，如实列出**：其一（IR-25），申请者能力句被改写——甲稿「尚无系统古文书训练」在压缩稿出现 0 次，改为「不要求古文书训练」1 次，把「个人欠缺」写成「本题不要求」，未经授权改动事实陈述；其二（IR-26），该稿 `步骤-materials` 实际只保存 3 项材料（`work`／`research_paper`／`research_paper`，即 `material-96aa5376…`、`material-4a217bfd…`、`material-d652c034…`），缺 `applicant_profile`（`material-f9f7e449…`）与 `application_requirements`（`material-7bd03c03…`），而 `inputs.material_paths` 声明的 3 条是 `rashomon-read.json`／`applicant-read.json`／`program-read.json`，二者不对应，故正文关于申请者能力与篇幅栏目判断在该稿内没有对应已保存材料；其三（IR-27），该稿 `引用定位.json` 三条记录的 `body_blocks` 未按 14 块正文重映射，`[4,6,8,10,12,14]` 中的 `14` 越界（正文 0–13），所列块均为栏目标题而非论断所在 `Para`，故「引用及定位支持论断」在该独立稿上不成立。摘要 `da597987…` 与状态内 `checks.digests` 相等只说明文件未被改动，不说明定位有效。
- **根因（执行者侧，IR-24）**：提示词末句「现在这份已提交的稿子请保留，压缩后的版本单独交付」把「保留旧稿」与「另出交付」混写。主技能据此另建 `压缩稿/` 目录，并把这次 `begin_revision` 的 `inputs` 写成 `application_id=合成甲项目-联系教授-压缩稿`、`purpose=联系教授（甲项目压缩版本）`，该目录从一开始就是独立稿件：`_state.py:557–559` 在 `state is None` 时直接用本次 `inputs` 生成 `binding`，故本次 `begin_revision` 未触发 `_state.py:502–505` 的 `different_proposal` 提示（请求响应全文无该提示）。技能 `SKILL.md:76` 与 `implementation-plan.md:272` 的「跨校另建稿件编号」以换学校为前提；本轮是同项目压缩，不满足该前提。执行记录中可见 `mkdir -p …/压缩稿` 与随后的 `begin_revision` 由主技能自己发出，故这是执行端的绑定变更与其分支选择，不是产品按跨校规则的行为。产品在本轮未改写甲稿、未违反保护逻辑，故不计产品业务失败；但验收标准要求甲项目有效稿落在范围内，故本次记业务失败。
- **按约定停止**：按交接说明「一次请求后仍超限则保留结果、记业务失败、不连续重发」，本次未再发第二个压缩请求；改提示词属方案修订，须由决定人批准。
- **保留的格式错误尝试** `requests/rp08-length-compress-attempt0-requestformat/`：`command` 里 prompt 未加引号，评估服务在**任何 Codex side effect 之前**返回 HTTP 400（`-- 之后只支持一个 prompt 参数`）。实测甲稿状态摘要未变，未产生业务结果，未消耗业务尝试；随后按引号要求重组 `command` 发出，提示词原文逐字未变（`shlex.split` 后与 `argv` 末项完全相同，379 字符）。
- **未改变的环境与对象**：未启停评估服务、未改消费者配置、未改产品代码、未改 `plan/test-plan.md` 与 `plan/implementation-plan.md`；`原件/rp08-交付稿.md`（`453ce3ae…`）、`修改稿/` 与 8 个版本目录均未动；乙项目面试准备稿（9/`r-20261104T132940…`）与林安稿（26/`r-20261104T134308…`）状态未变。

## 压缩请求 v2（修正措辞后在甲稿上生成新版本，2026-11-05）

按交接说明以「在原稿件上演进为新版本」的措辞重发一次，仍不改项目要求、不换字数统计口径、不手改正文或 Markdown、不重置 `current`。结果：**外部故障，未取得业务结果**，阻断项仍未闭合。

- **基线核对（请求前实测，非副本、非 `/tmp` 旧基线 JSON）**：甲项目 `current=r-20261104T165248-ed68cb7c11d7`、`state_version` 72、`works` 8 项、7 个栏目（研究题目／研究背景与相关研究／研究问题与目标／研究方法与判断办法／研究进度与可行性／预期成果／参考文献）。四文件摘要与状态内 `checks.digests` 逐项相同——Markdown `b826206b…`、正文 `aea0ad4e…`、引用定位 `071e3151…`，`导出记录.json`（`8b440f9d…`）的 `formats.md.digest=b826206b…`、`body_digest=aea0ad4e…`。请求前状态快照 `RP_RUN/snapshots/pre-rp08-length-compress-v2/研究计划状态.json`（`4f744ddb…`）。
- **请求** `requests/rp08-length-compress-v2/`：提示词只写业务要求，不含内部工具名、参数或保存步骤，不预先灌入压缩后正文。相对上一轮共改四处（按 `diff` 实测）：其一，首句「继续」改为「继续修改」；其二，把「现在提交的正文超了上限」改为用户可见事实「现在这份已提交的正文是 1687 字，超了上限」，未指定压缩后的目标字数；其三，把「已经确认的研究问题与方案」点明为 `Q2-B-1` 与 `scheme-B-2`，使确认对象无歧义；其四，末句由「现在这份已提交的稿子请保留，压缩后的版本单独交付」改为「请在当前这份甲项目稿件上继续修改，生成一个新的版本，旧版本按原规则保留。不要另建稿件，也不要另立编号，新版本要落在这份甲项目原有稿件的目录里」，直接对应 IR-24 的根因，并另起一段显式写出「这次只做压缩篇幅的编辑，已有的内容陈述按原意保留：申请者的能力与条件、核读后再限定贡献的说法、参考文献条目都不改写」，对应上一轮 IR-25 与 IR-27 两项偏差。
- **请求格式**：`command` 按 `requests/rp13-school/` 结构由 `@sh` 单引号转义组装；实测 `shlex.split` 后 `--` 之后只有 1 个 token 且与 `argv` 末项逐字相同（519 字符），未重犯 `attempt0-requestformat` 的 HTTP 400。
- **传输**：`POST http://127.0.0.1:17902/eval`，HTTP 200、`curl.exit=0`、`curl.stderr` 空，`version=codex-cli 0.166.0-alpha.5.1`；`passed=false`、`output.backend=app-server`、`termination_reason=turn_failed`、`exit_code=1`、`cleanup_status=unsubscribed`、`runtime_generation=1`；线程 `01a1abd3-33c8-7a70-9ded-16b916b83178`（`turn_id` `01a1abd3-35c5-7280-8240-9d8f50bc86b4`），13:08:27→13:08:36 UTC（约 8.3 秒）。生效配置 `approvalPolicy=on-request`、`sandbox.type=workspaceWrite`、`networkAccess=true`，与 `--sandbox workspace-write` 一致。
- **失败性质（外部故障，非业务失败）**：`error` 原文「You've hit your usage limit. … try again at Nov 10th, 2026 4:05 PM.」，`codexErrorInfo=usageLimitExceeded`、`willRetry=false`。请求在模型产出任何内容之前终止：`output.events` 只有 `thread.started` 与 `turn.started`，`app_server_events` 的 `item/started` 只有 `userMessage`，`turn/completed` 为 `status=failed`、`durationMs=8307`、`items=[]`，无任何工具调用、shell 命令或技能读取。主技能未读取甲稿，未调用保存／导出／核对／提交，未新建或修改任何稿件目录，故本项没有任何业务观测点被触达。
- **无副作用核对**：甲稿 `研究计划状态.json` 请求前后同为 `4f744ddb3c9a2a50e2698461a1487f5f13839639003f74f4f6ed26fcd6ab7a63`，`state_version` 仍 72、`current` 仍 `r-20261104T165248-ed68cb7c11d7`、`works` 仍 8 项、`版本/` 仍 8 个目录、mtime 仍 `Nov 5 00:55:27`；其余四份稿件状态同样未变（乙项目 `a215e8ea…`、`压缩稿/` `c85a8a98…`、林安稿 `115ec737…`、`input/研究计划/联系教授草稿` `fdb54914…`）；甲稿目录下无 20:00 之后写入的文件，`工作版本/` 仍为空，`原件/rp08-交付稿.md` 仍 `453ce3ae…`。
- **按约定停止**：按 `PROJECT_CONSENSUS.md`「基础设施重试与停止」与 `test-plan.md:472`，已确认且未变化的额度不足不触发连续完整运行；错误原文标明的恢复时间为 2026-11-10 16:05（原文未标时区），恢复条件尚未成立，**未补发第二次请求**。换用其它 profile／模型属方案修订，须决定人批准；`test-plan.md:188` 规定未获批准的其他模型候选不加载，本次未做。
- **业务尝试计数**：本次确实到达评估服务并建立线程（`thread.started`），但轮次在模型产出前 `failed`、`items=[]`，未产生任何业务结果，故不作一次有效业务尝试，也不计入 13 次业务请求。与上一轮 HTTP 400 的 `attempt0-requestformat` 的区别须写明：那一次在评估服务层就被拒（未建线程），本次建了线程但轮次失败。按 `test-plan.md:472` 的「最多补一次（总计两次）」上限，本次后仍可再补一次，但补发前提是「环境确已恢复」，而错误原文标明的恢复时间为 2026-11-10，该前提未成立，故本次不补发。若额度恢复后重发，应沿用本目录 `eval-request.json` 原文与同一基线（72／`r-20261104T165248…`），其余条件不变。
- **未改变的环境与对象**：未启停评估服务（`127.0.0.1:17902` 仍由 PID 34001 监听）、未改消费者配置、未改产品代码、未改 `plan/test-plan.md` 与 `plan/implementation-plan.md`；`原件/`、`修改稿/` 与 8 个版本目录均未动；未重置任何 `current`；未手改任何正文或 Markdown。
- **定向复核**：专用 `implementation_reviewer` 代理（只读）复核 HEAD `fe5d3b2`，逐项核对 9 个要点，结论**部分完成**。审核独立确认：v2 响应确为 `turn_failed`/`items=[]`/`codexErrorInfo=usageLimitExceeded`，且 7 条 `rawResponseItem/completed` 全为 developer/user 输入、无 assistant 输出（即无任何工具调用）；甲稿摘要 `4f744ddb…` 与另四份稿件摘要、`state_version` 72、`current`、`works` 8 项、`版本/` 8 个目录均与记录一致；当前版本三文件摘要逐项等于 `checks.digests`，七栏目、`Q2-B-1`/`scheme-B-2` 均 `confirmed`；字数复算 1687（锚点 1465、1215），且脚本「排除全部列表块」与口径文案等价（三份正文的列表块只有末尾参考文献 `OrderedList`，块内 `Space`/`SoftBreak`/`LineBreak` 均为 0）；提示词确已替换末句、不含内部工具名/参数/保存步骤、未灌入压缩后正文；`shlex.split` 后 `--` 之后 1 个 token 且等于 `argv` 末项；停止处置合乎 `PROJECT_CONSENSUS.md:134` 与 `test-plan.md:472`（未误用「最多补一次」余量），不记通过也不记业务失败的处理合规，未闭合项仍如实标「仍未闭合」；两次提交只改 `plan/test-results.md`，`plan/test-plan.md` 与 `plan/implementation-plan.md` 最后改动仍为 `0a1c12f`，消费者配置 mtime 未变，无 `20:00` 之后写入。该结论只说明实现落实情况，不构成计划关口、测试第三关或合并批准。
- **复核意见落实**：IR-33（记录称「只改两处措辞」而 `diff` 实测 4 处）已按实测逐条改写并闭合；IR-34（`business-observation.md` 末两行 `</content>`/`</write>` 残留）已清除，文件其余正文未动；IR-35（`prompt.txt` 的 519 字符与 520 单位混写）首轮修正时沿用了审核建议里的同一处单位误写（把 520 当作字节），经复核指出后按实测改为「`argv` 末项 519 字符；`prompt.txt` 含末尾换行共 520 字符、1248 字节」，证据文件与本节记录同步改正。复核代理随后对 `98781f7` 做小范围确认，结论**完整**：`wc -c`＝1248、`wc -m`＝520、`argv` 末项 519 字符三数自洽（且 `cmp` 证实 `argv` 末项与 `prompt.txt` 去末尾换行后逐字节相同）；「520 字节」错误写法在仓库与证据文件均为 0 处；`573bacc..98781f7` 只改 `plan/test-results.md`，工作树干净。

## 本次范围调整

以下 r4/r13 版本及其结果说明**本轮（r15）之前**的执行依据与观察，保留为历史与未受影响结果的来源。当前产品、版本与逐项结果以上文「r15：Markdown 单格式产品与正式执行」为准；本节中“产品仍为 b983”等描述只描述当时状态，不适用于 r15 之后的执行。

用户明确要求“只测 research-proposal 的逻辑，recipe 应该手动准备输入”。现行测试计划修订为 `rp-tests-r4-repository-scope-2026-11-03`，Recipe 为 `rp-recipe-r13-input-fixtures-2026-11-03`，本次准备和复核状态见测试审核记录。产品仍为下述 b983 版本，已有正式安装继续适用。

当前完整测试计划 SHA256 为 `087b0ad2702d8cfd3ca41f9c0ff945c9fea454e2a713b43328ef7bc3e2b81d73`。本轮结果根记为 `RP_RUN_R13`，实际位置由外部执行交接提供；旧 `RP_RUN`、`RP_RUN_PATH_FIX` 含义不变。原消费者和未提交非论文第 6 版保持原路径，固定产品仍为 b983；新配置从该版原安装快照生成，模型为 `gpt-6-luna/low`，线程数 1、单请求 600 秒，关闭范围外两项 MCP 并保留隔离端点。未访问上游服务。

RP-03 至 RP-05 改用准备好的上游输入检查本仓库发现与交接安排；RP-07、RP-08 不再等待上游采集、下载、分析或候选生成。旧上游失败作为历史事实保留，移出本仓库通过条件，不改写为成功；本仓库的方案保存、引用及尚未完成交付问题仍需处理。下面当前表按新范围列明适用结果；尚未按新版方法执行的项目不推定通过。

## 既有执行依据与环境

以下 r3/r12 版本和批准记录说明历史执行依据；新增测试只按本次 r4/r13 完整计划执行，不再照旧步骤续跑上游。

有效执行计划为 `rp-plan-r3-2026-11-03`，SHA256 `edf6692023be0e717ff454482c10763cc74c42885cc41ea8458fd1915fb69bcf`。测试业务版本为 `rp-tests-r3-2026-11-03`，当前执行步骤为 `rp-recipe-r12-user-retry-2026-11-03`，完整测试计划 SHA256 `8eea46b06c7769931197792efa19a96d63242a531d6184955c1434a9c2a14dc4`。先前 r11 为 `741ccc0bd099ce3cf7c3dfbca720905fd18c607270dab728e99217595bbdcc7a`，r10 为 `865b4c001f8eb741accc3375448ffbfbfdb87e043f7765034bd6852b1cf6fe65`，r9 为 `da81f2581c3fd97800a85ce1d2c87f2cf995475a0bedc409be8876d8d8fcfd99`，r8 为 `6265d0ff4cde2d4084d7c04f3b5abae45cff2eac2d80f87c2d967012c241b750`，r7 为 `f9dffd1546eabcc99916c1bf26c8d1b3c22336ccf054a46a05bed951fa135c93`，r6 为 `a7f1fe434c06e672d8c7b08f8bb7c5abd5b520adc664d751554cd9b6e2d12a3b`，r5 为 `1cc495e5a1f1210abe35132c4b18fedbfd8d2daac1dc9e68bb7dbd77ad990b94`，r4 为 `dc89ac273d927c9a2a4d470443343b4941b2f35ad9b1743b161e0a1d6455a0c3`。此前路径脱敏及格式修正不改变业务；r5 修正配置准备错误并记录合成申请者授权；r6、r7 落实用户恢复服务及认证后的有限尝试；r8 补齐沙箱网络；r9 修正 RP-13 的原路径快照与恢复；r10 落实用户要求的 RP-04 原条件一次追加请求；r11 补齐路径说明修正后换版安装和原路径续接；r12 仅落实用户要求的 OA 决定请求原条件追加一次。第一关继续有效，r5 至 r12 均取得第二关定向批准，模型及未受影响结果沿用。

首个正式产品版本为 `4797a1bd69dca2a1354476a564c5d2714d8004da`，发布仓库为 `ScholarWorkflow/research-proposal`。扫描修正版本为 `4dfb8bed5a17480728a073f951ba18e98c177829`；准备及第二关 r5 记录提交为 `3e9b6c4aab7b86dcf91a1ef9f6fd21f387c633a5`。四项代码问题修正版本为 `677055164c06d549f99b6e04a2e80d30f7b871c3`。当前路径说明修正版为 `b983497308157dedec6b4d97f16c95dc0b0f60f9`，已按 r11 从远端固定提交在原消费者位置完成空目录正式安装，恢复原业务资料；旧消费者完整归档，旧安装结果和原失败不覆盖。

运行原始材料保存在仓库外的独占目录，由本地交接记录提供实际位置。首候选结果目录记为 `RP_RUN_INITIAL`，扫描修正版本记为 `RP_RUN_PREVIOUS`；本记录既有 `RP_RUN` 引用始终指 677 版本的运行根。路径说明修正版的新结果根另记为 `RP_RUN_PATH_FIX`，其执行环境中的 `RP_RUN` 变量指该新根，`RP_RUN_BEFORE_PATH_FIX` 指前一根，消费者绝对位置保持不变。未带结果根的首轮组件、扫描及 npx 相对路径属于 `RP_RUN_INITIAL`；后续各条注明版本及结果根。尚未完成的复验不覆盖旧结果。

共享夹具在本轮使用前已由主对话更新干净的主分支，更新退出 0，仍为 `5a31ae0095952cc359f7fa826730f14e7ee4f5b2`。准备记录及不可变缓存继续有效。有限预检、源码语法检查及依赖静态求值均不代替下表结果。

用户已明确授权“由执行代理作测试决定”：执行者可在本轮隔离测试中扮演合成申请者，先阅读实际教授、方向、问题和中文方案，再针对当次内容通过正常请求作出决定，注明授权来源。该授权不预先确认尚未展示的内容，也不适用于用户真实申请；不手写产品确认状态。

### r13 历史结果表（只作历史与复用来源，不代表 r15 当前结论）

下表是 b983 产品在 r13 运行根下的**当时**结果，保留以便追溯与复用未受影响项。r15 的当前逐项结论以上文「结果表（四状态）」为准；两表冲突时以 r15 表为准，本表不得作为 r15 的通过依据。

| 编号 | 当时结果 | 结果位置与说明 |
|---|---|---|
| RP-01 | 部分完成 | 路径说明修正版的四输出和共享激活均退出 0，见 `RP_RUN_PATH_FIX/logs/build-*.log`、对应 `.exit` 与 `activate.log`。677 版本的主技能、六项依赖、17 份原代理、资源、无关技能及配置保留检查未受影响，沿用 `RP_RUN/logs/rp01-install-inspection.txt`；未重复完整验收。本仓库运行能力采用 RP-06、RP-08 的适用结果，不再等待上游业务。 |
| RP-02 | 通过（沿用） | `4797a1bd69dca2a1354476a564c5d2714d8004da` 通过 `skills@1.7.2` 在独立目录安装；主技能、脚本、四份参考规则和模板完整，资源引用可解析，README 如实说明环境要求。安装入口和资源布局未变，结果沿用至当前 `b983497308157dedec6b4d97f16c95dc0b0f60f9`，未重复 npx 安装。见 `RP_RUN_INITIAL/logs/npx-install.log`、`.exit`、`rp02-install-inspection.txt`。 |
| RP-03 | 通过 | r13 正式安装组件的 3 个方法通过，覆盖四入口、缺候选及对象/方向选择。见 `RP_RUN_R13/logs/rp03-components-recovery1.log` 与 `.exit`。 |
| RP-04 | 通过 | r13 组件检查 collect、preview、stage0–2 分支通过；stage3 采用 RP-03 的同一次结果。已直接核对安装后主技能和两份引用中的原命名、参数来源、等待消费、重新发现、第三阶段调用方收尾和邮件边界，符合。见 `RP_RUN_R13/logs/rp04-components-recovery1.log`、`.exit`、`rp04-handoff-review.md`。历史上游失败仍保留，不作本项新范围的通过条件。 |
| RP-05 | 通过 | r13 零散分析的三个独立输入副本正确保留归属、分析及事实路径，依前置状态返回 stage0、stage1、stage2。见 `RP_RUN_R13/logs/rp05-components-recovery1.log` 与 `.exit`，未运行上游分析业务。 |
| RP-06 | 通过（沿用） | 677 版本的载体、定位与相关组件通过；作品实际会话正确解码并完整保存原响应，提出 3 个有依据、方法及缺项的候选后等待选择。授权角色选择实际 Q2，后续 `rp07-01` 记录并进入方案准备。路径说明修正不影响这些结果，沿用 `RP_RUN/requests/rp06-01/`、`rp07-01/`。来源标签的具体不符交 RP-07、RP-08 的既定引用核对，不额外增设书目关口。旧乱码及梗概替代失败保留在 `RP_RUN_PREVIOUS/requests/rp06-01/`；扫描原图核对复用该目录的 `logs/rp06-*`。 |
| RP-07 | 通过（真实反馈修订后） | r13 论文路线依次保存问题、条件与中文方案，再取得各自决定；非论文路线针对旧作者错误给出具体反馈，实际保存 scheme-2，随后确认并补充采用出处勘误。两条路线均保留未确认时没有正文/当前稿的状态。见 `RP_RUN_R13/requests/paper-01/` 至 `paper-04/`、`nonpaper-01/`、`nonpaper-02/` 及状态快照。原 `RP_RUN/requests/rp07-03/` 的作者误写与方案未保存失败保留，不改称产品修复。 |
| RP-08 | 部分完成，尚未通过 | 论文日文正文及两格式半成品已保存，但正式页面预览失败，未提交；初稿还存在栏目与篇幅不符，正在按真实审稿反馈修订。非论文方案已确认，待继续正文与最终交付。见 `RP_RUN_R13/requests/paper-04/`。 |
| RP-09 | 部分完成 | 真实招生空白表读取已通过，识别封面与另附正文要求；模板导出两场景仍需 RP-08 的真实已确认正文。见 `RP_RUN/requests/rp09-blank-form/`。 |
| RP-10 | 部分完成 | 677 版本复跑 `RevisionImportTests` 两项通过，覆盖 Word 修订、批注、不支持对象及 Markdown 改动；路径说明修正不影响该结果。真实成稿的改稿场景仍待执行。见 `RP_RUN/logs/rp10-components.log`、`.exit`。 |
| RP-11 | 未执行 | 需要 RP-08 的真实状态、确认和步骤产物。 |
| RP-12 | 未执行 | 需要第一份成稿及第二项目的实际请求。 |
| RP-13 | 通过 | 原 r7 下空目录和学校名称分支明确缺项并保留进度；r9 下缺视觉配置分支返回具体错误、保存原件和缺项，已有问题确认及方案保留，没有成稿。完成后原稿与正常配置已恢复。见 `RP_RUN/requests/rp13-empty/`、`rp13-school/`、`rp13-missing-vision/`。回复中一个材料步骤链接错误另记，不改写实际保存与恢复结果。 |

所有正式尝试及修复复验会保留在本记录和对应运行输出中。实现符合性审核由专用审核代理执行，第三关由主对话审核；本文件不代作这两个结论。

以下「r13 本仓库执行」及更早各节是 b983 产品在当时运行根下的执行记录与历史尝试，保留为事实与复用来源；其产品版本、路径与结论不适用于 r15。

## r13 本仓库执行

15:41:52 UTC，按 Recipe 在原消费者 `input/r13-manual-inputs` 重新构造外部输入，未移动临时输入或改写路径，未生成本技能自己的确认或稿件。原配置保存于 `RP_RUN_R13/config/consumer-config.before.toml`；正式合成文件与约定字段检查分别保存在 `config/consumer-config-r13.toml`、`logs/config-check.json`。本轮安全绑定见外部 `config/run.env`。

RP-03 至 RP-05 的首次命令在 uv 初始化默认缓存时全部退出 2，尚未导入产品或运行断言；原输出保存在各自 `logs/rp0*-components.log` 及 `.exit`。沿用已经有效的 `RP_PREP/uv-cache`，把 `UV_CACHE_DIR` 写入本轮绑定后，执行原命令并另存 `recovery1` 日志。15:42:44–15:42:46 UTC 三组分别以 3、1、1 个测试方法通过，退出均为 0；各方法内部覆盖 Recipe 明示的全部路径和副本。此恢复只改启动缓存位置，输入、代码及观察点未变。

RP-04 直接核对安装后的主技能、`runtime.md`、`upstream.md` 与固定上游参数，逐分支位置及结论见 `RP_RUN_R13/logs/rp04-handoff-review.md`；没有调用上游代理、服务或业务入口。

论文路线 `paper-01` 实际发现完整包及候选，返回 `proposal` 并列出两个方向；执行者阅读后选择“叙述评价的归属”。`paper-02` 读取并保存三份原文，形成核心问题 `q_voice_01`，提出公开定稿替代未定位私人手稿的办法。返回时本稿状态为 3：问题待确认、条件未解决、方案和正文待处理、`current=null`，对应快照见该请求 `state-at-return.json`。

执行者针对上述实际内容选择该问题及公开定稿范围，首次提供根外补充条件，明确完整方案尚未确认。`paper-03` 保存并展示“《门灯》中评价归属与秩序解释的证据限度”中文方案：对照 P2/P3/P5/P6 及 P1/P4，区别原文、两项研究的解释及申请者拟做的归属判断；按 A3/B3 的限制保留分歧，不把不同结论简单判为一方错误。方案采用逐句证据表、四类归属、反例及无法裁定处，并列两年安排。补充条件仅证明可以申请检索，尚未申请、未确认馆藏、没有许可；核心研究采用已提供公开定稿，手稿为可选补充。返回时状态为 5：问题确认、条件解决、方案 `needs_input`、正文待处理、`current=null`，快照保存在请求目录。执行者读过实际保存件后才确认该方案并发送 `paper-04` 日文草稿请求。

`paper-04` 于 15:53:20 UTC 自然结束，确认和日文正文已保存；正式导出内部的固定 LibreOffice 转换两次退出 -6，保留 Word 本体及 Markdown，状态为 9、`docx=failed`、页面未核对、`current=null`。本轮实际 Word XML 与 Markdown 正文一致，但 AST 只有 11 个普通段落和参考文献列表，没有七个栏目标题；排除参考文献后拼接全部 `Str` 的字符数为 2456，再排除题目 24 字仍为 2432，超过上限 2400。没有把空白和 Markdown 标记计入这一数值。旧工作目录留在该请求 `working-at-return`，后续修稿不覆盖失败依据。原负责人定位到本次模型先写标题、又在转换前删除标题的具体执行动作，现行技能已经要求栏目与篇幅核对，暂无据修改产品说明；后续自然语言审稿修订另行记录。

导出负责人核对固定 `Contents/MacOS/soffice` 与产品参数，现有崩溃栈停在 macOS 应用初始化，尚未进入文档转换；模型另外试的 `bin/soffice` 包装错误不是产品正式调用路径。指定进程及 15 秒窗口的只读系统日志查询获准后返回空数组，未据此推断。经主对话同意的唯一最小对照采用同一固定程序、同一 Word 和同一转换参数，在获准外层执行一次，退出 0 并产生可读的 3 页 PDF。该结果仅收窄环境原因，不替代正式 API 导出、逐页核对或提交；诊断见 `RP_RUN_R13/logs/lo-init-check.md`。正式恢复方法交原测试准备负责人核对，不切换全局沙箱或模型。

`nonpaper-01` 采用针对旧方案作者误写的真实反馈，核对已提供 PDF 后保存完整 scheme-2 和文献记录，明确作者为前田角藏，石川巧文章致谢中的前田雅之是另一人；承认既有研究已经涉及权力关系，将本稿区别限定在灾荒/失业、相继辩解与夺衣场景顺序的分析。状态为 8，原 Q2 决定及公开底本条件有效，scheme-2 待确认，正文待处理、`current=null`。执行者读过实际保存的方案后在 `nonpaper-02` 确认，并指出旧材料“《新思潮》”来源标签错误；本次方案记录明确改以原文所载 1915 年《帝国文学》11月号为采用出处，保留原始读取记录并排除旧说。状态为 9，问题、方案确认和条件均有效，没有提前导出。原作者与未保存失败保留，当前纠正来自有具体内容的正常审稿反馈，不是无变化重采样。

`paper-05` 针对七栏目和超限事实提供正常审稿反馈，明确转换环境未恢复、本轮不重复转换。请求自然结束，但本轮仅直接改写工作版 Markdown，没有读取主技能或通过生产入口保存正文；`正文.json`、状态版本 9 和旧步骤数据未变，回复声称已同步 JSON 与实际不符。该次工作目录及状态另存请求内 `working-at-return`、`state-at-return.json`，不能把新 Markdown 当作已采用正文或完整交付。执行者没有补写状态，也没有再次原条件请求；衔接归属交主对话判断。另起的非论文正文准备明确使用原主技能和已确认方案，不尝试当前已知受限的页面转换。

原主技能负责人确认 `paper-05` 与前轮为不同实际线程，只有一般改稿调用，没有再次明确调用本次受测技能；技能描述已涵盖修订，未发现可定位的触发说明缺口。后续应修正产品调用入口、基于现有真实稿件继续，不能声称原条件复试或产品修复。用户新范围生效前没有再发送纸稿请求。

`nonpaper-03` 明确使用已安装主技能，依据已确认的 scheme-2 生成中文正文并经生产入口保存，16:07:07 UTC 自然结束。状态为 10，正文已完成且保存引用定位，问题、方案及条件仍有效，导出待处理、`current=null`。实际 AST 含七个有序栏目，正文沿用作者更正、原文初出和有限研究差异，不声称已经取得手稿；尚无最终 Markdown 交付，后续按新范围继续。该次未调用页面转换。

## 历史尝试与适用结果

以下记录不因范围缩小而删除。新版只复用其范围内仍适用的结果，不再执行已撤销的上游步骤，也不把旧版尚缺上游成果作为新版成稿的阻断。

2026-11-03 的安装执行逐条采用 Recipe 的远端固定提交构建、激活和 npx 命令。Nix 仅增加 `XDG_CACHE_HOME` 指向已有效的独占缓存，避免已确认只读的默认缓存；未替换 HOME，也未改变产品或业务配置。首次安装检查错误地对不存在的 TOML `agents` 表取键，已改为检查实际 `.codex/agents/*.toml`；无产品变更或重新安装，保留配置和资源的实际结论不受该检查表达式错误影响。

Chrome 首次在沙箱内启动时于 CDP 就绪前退出，Zotero 首次启动由 LaunchServices 拒绝；两次均在业务请求之前发生。依据项目的外部夹具规则，保留原尝试后，在获准的外部环境使用同一固定脚本和独占根目录启动，均退出 0。只有本轮 `fixture.env` 指定的实例由本轮负责清理。对应证据为 `logs/chrome-start*`、`logs/zotero-start*` 和 `config/*fixture-location-external.txt`；不将这两项环境恢复计为 RP 业务失败或通过。

首次消费者配置合成发现 `consumer-runtime.yq` 使用 `load()` 读取 TOML，当前 yq 将内容视为字符串，导致 `.features` 为空；直接按 TOML 解析源文件则得到既定嵌套开关。尚未提交业务 eval，不增加线程预算、不修改产品；已交测试准备负责人处理配置步骤。

r5 改为从同一固定 TOML 显式提取 `features` JSON，再由唯一合成表达式加载，写入前核对开关。原准备代理及同一专用审核代理已关闭 PRP-09，主对话批准第二关定向结论。原安装快照、失败配置和诊断保留，后续仅使用获批步骤；该配置修正不使已有安装和组件结果失效。

两组已执行组件测试均从 `test/` 目录使用正式远端 Nix 运行包的解释器，设置 `RP_TEST_OUTPUT=RP_RUN/component-output`，实际命令分别为：

```bash
UV_CACHE_DIR="$RP_PREP/uv-cache" uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v test_inputs.MaterialTests
UV_CACHE_DIR="$RP_PREP/uv-cache" uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v test_inputs.RevisionImportTests
```

两条均退出 0，各执行两项测试；载体测试的子项实际覆盖六种文字载体。扫描读取逐条采用 Recipe 的 `read_material --request` 命令及正常视觉配置；其退出 0 不替代原图对照所得失败结论。

扫描修正版本仅复验当时直接受影响的材料读取。扫描复验使用新消费者、同一原图和视觉配置，两个区域的 `origin` 均为 `live_stdout`。产品返回候选转录及明确待核事项；执行者按同一原图逐处核对，记录被遮挡的数量不能判断、原图印刷说明可读、两段服务坐标占位和操作注释不是原文。保留具体缺项，没有清空产品待核标记。四处文字载体定位与首轮一致，未改动的读取函数及同一原件的既有直接对照继续有效。详见 `RP_RUN_PREVIOUS/logs/rp06-locations.md`。

扫描修正版本首次实际业务请求的准备入口退出 0，`preparation.json.loading_method=config-args`，累计线程预算在请求前按固定 collector 未选择教授时的原返回点绑定为 1。POST `/eval` 于 2026-11-03 06:47:20 UTC 连接失败，未得到 HTTP 或模型响应；随后只读检查沙箱内外同一配置端口均无监听输出。按规则已交环境负责人，不自行启动或重启服务，也不因连接故障更改预算、输入或模型。该偶发故障与 RP-13 计划内的缺配置场景分别记录。

用户之后明确告知服务已经运行，根代理确认原端口正在监听；本轮执行者与根代理均未启动或重启该服务。恢复条件成立后，执行者将原 payload 原字节复制到独立重试目录并以 `cmp` 确认相同，再按原超时提交一次重试。监听只说明恢复条件成立，仍须等待业务产物判断 RP-04。

该重试返回 HTTP 503、`app-server runtime is not READY`，`version` 字段为 `codex-cli 0.166.0-alpha.5.1`，没有 `output` 或业务事件；此字段不是评估服务源码提交。固定适配器列出缺少 backend、runtime_generation、thread_id、turn_id、termination_reason，不能据此产生委派结论。达到原尝试上限后已停止。用户再次告知服务已恢复，根代理只读看到 `initial_start_ok`，并在 r6 中批准仅此首请求再尝试一次；执行者沿用原 payload 原字节、模型、输入、预算与超时，另存 `rp04-01-recovery1`，不覆盖前两次。

r6 尝试自然结束，`termination_reason=turn_failed`，模型 Responses 请求返回 401，明确缺少认证头；执行者随即停止。用户再次明确要求在其修复认证后试一次，主对话将此有限授权写入 r7 并定向批准，执行者才发送第四次原请求。没有读取或修改认证、切换模型或改变业务参数；原请求和追加请求均逐字比较相同。

r7 第四次返回 `passed=true`、`termination_reason=completed`，说明会话结束，不能覆盖实际业务失败。发现结果只有一个招生项目对象，`next_step=collect`；本次全部相关创建关系为空，主技能没有读取上游参考或尝试原采集委派，而是自行读取教员信息并保存 3 个题目。提前形成的工作目录及材料状态完整保留，不冒充 RP-04 的正式上游基准；已交主技能修复明确的下一步分支消费。

随后执行不依赖 RP-04 的真实非论文候选场景，仍用当前已安装候选和原配置，独立请求 `rp06-01` 正常结束。原件 HTML 的 XML 和 meta 均声明 Shift_JIS；原 `read_material` 输出却含替换字符且无缺项，解析后的真实输出保留在 `material-read-output.txt`。主技能转码副本后读到日文，但保存材料时删除原块编号、将逐字文本改为中文情节概述，并把副本材料编号对应到原件路径。候选本身有材料依据、方法、缺项并等待选择；这只作为局部观察，材料记录无效时不作用户确认或成稿。修复通用编码读取与完整原响应消费后，再按原方法复验。

修正候选 `b6921257d80c01eb01e396446bfd69babdf7003d` 已由主对话发布，但从未安装或执行正式用例。同一实现审核者发现 IR-02 的具体入口及 EX-02 的 EPUB 声明处理仍需小幅修正；按主对话决定完成修正及定向复核后，固定为 `677055164c06d549f99b6e04a2e80d30f7b871c3`。四项具体代码问题静态关闭不计为正式通过，后续只复验受影响原项并完成尚未执行项。

当前候选的四输出构建与激活于 2026-11-03 08:34:19–08:35:07 UTC 完成，均退出 0。原安装保留检查再次按实际目录确认，r7 配置采用同一固定准备输入、已有效的独占服务与缓存。受路径保存、编码及材料记录组装影响的 `MaterialTests`、`RevisionImportTests` 已由执行者亲自复跑，各两方法均通过；四类选定片段和定位解析后与同一原件的已核对记录一致，详见 `RP_RUN/logs/rp06-locations.md`。未变化的 npx 安装与扫描模型响应继续复用。

当前候选 RP-04 首请求为 `RP_RUN/requests/rp04-01`，沿用原招生输入和业务提示，仅安装及隔离路径对应修正版本。准备入口退出 0、`loading_method=config-args`；请求前按原 collector 未选教授时的返回点绑定累计预算 1，于 08:36:46 UTC 提交，等待实际结果后判断，不能用组件通过代替上游流程。

该请求于 08:37:28 UTC 正常结束，真实 `agent_type=professor-collector`，固定适配器无问题且有一个正式子线程；主技能等待并采用其结果，展示 8 位教员后停止于教授选择。执行者按本轮合成申请者授权选择已展示的石川巧，作为 `rp04-02` 的正常用户输入。该请求预算为 6：collector、preparer、单教授 worker 共 3，预筛两层共 2，返回尚未作出的方向选择的阶段 0 共 1；没有预填后续方向或配置无限容量。

`rp04-02` 正常结束，但实际 `zotero_probe.py` 对本轮两个本机端点都返回 `Operation not permitted`。配置传输记录中 `sandbox_mode=workspace-write`、`sandbox_workspace_write=null`；尚未进入 preparer、worker 或创建教授成果。访问拒绝不能证明服务本身是否存活，已交原测试准备负责人核对实际配置，没有以跳过 Zotero、重启服务或重复采样求通过。完整解析结果与观察在 `RP_RUN/requests/rp04-02/zotero-probe-result.json`、`business-observation.md`。独立 RP-06 作品候选按原 r7、原输入及业务提示继续，运行期间不改消费者配置。

当前候选 `rp06-01` 于 08:44:17–08:45:40 UTC 正常结束。原 Shift_JIS 作品读取为 9 块，主正文为 6455 字日文，未含替换字符；材料步骤内的完整作品对象与保存的 API 响应逐字段相等，逐字正文、块编号、定位、原件路径和材料编号保持一致，概括与解释另列。三个候选有依据、方法及缺项，未产生问题确认或正文。实际原文开头及结尾足以支持 Q2 的环境描写与生存辩解比较。

该次主技能填写的 `source` 标签把初出刊名写作《新思潮》，但完整原文的书目块明确为《帝国文学》1915 年 11 月号。候选记录另保留了发表版本尚待核实的说明；该说明不能消除具体标签错误，也不能把标签当作核实出处。主对话明确沿原 RP-07、RP-08 的来源与引用核对处理，不为 RP-06 新增“本阶段全部书目已核实”的关口，不冻结产品或重新采样。执行者已在阅读实际 Q2 及原文依据后作出选择，准备以正常后续请求传回；最终须按实际核对结果确认错误是否纠正，未通过改测试提示补写产品处理步骤。

等待网络配置定向审核期间，执行者继续了不依赖该网络能力的 RP-13 本地缺资料分支，仍使用 677 候选、原 r7 消费者配置、预算 1 和 600 秒超时。空目录请求于 09:10:28–09:10:44 UTC 完成，说明缺实际材料或招生项目，没有建立成稿；学校名称请求于 09:11:21–09:11:59 UTC 完成，读取“松川大学”后保存材料与具体缺项。后者状态 `current=null`，正文、Word、Markdown 均为 `pending`。这些分支通过，不代替本项计划内的缺视觉配置分支。

同一 r7 配置下，`rp07-01` 于 09:13:08–09:15:40 UTC 完成。执行者将实际 Q2 选择、两篇既定本地全文及尚未定位私人手稿的条件作为正常业务输入；没有发送人工对照笔记或预填方案确认。主技能区分石川对三好行雄、前田爱的转述与前田角藏 1996 的论文，保留关键原页未核事项；手稿条件不成立时保存缺项及公开文本替代建议，未生成正文。拟议的权力不对称焦点另待真实决定。`state-at-return.json` 保留此时 `current=null`、方案及正文导出均未完成的状态，`material-progress.json` 保留具体待办。

r8 准备问题 PRP-10 经原专用审核者关闭并取得主对话第二关批准，配置与记录提交为 `2d9a3d638ad49a838b4132f0b7ff03533eccd35b`，不改变产品 677 或已有有效结果。执行者确认所有前序请求结束、原 collector 已收尾且招生目录仍只有 5 个原输入后，按唯一表达式从原安装快照生成 `consumer-config-r8.toml`，保留 r5 输出和旧请求；网络键为 true、预算仍为 6。`rp04-02-network-recovery1` 于 09:19:33 UTC 采用同一教授决定及原业务提示续接，1800 秒超时，等待实际上游结果。未使用准备者的预算 1 预检副本，也未将有限预检视作实际访问通过。

该续接于 09:19:46 UTC 正常结束，响应中的实际 `networkAccess=true`；但主技能在 `discover=collect` 后直接声称没有委派工具，没有尝试原 collector，也没有机器错误。固定适配器无问题、正式子线程数为 0。主对话按业务失败处理；原产品负责人核对了实际安装的明确路由与本次相关输出，未找到有证据的产品连接缺口，零修改、不靠改字或提示补步骤取得新采样机会。原始结果和判断见该请求的 `business-observation.md`。没有真实上游成果，RP-03、RP-05 和论文稿继续未完成，独立项照原范围继续。

非论文 `rp07-02` 正常接受公开主材料和实际提出的 Q2 焦点，主材料条件成立但方案仍未确认，正文及导出未生成。方案 JSON 中初刊名称已正确；旧材料标签仍需在最终引用中解决。首次审阅交付存在具体不足：回复所链接的待确认事项 Markdown 只有待办，完整方案仅在步骤 JSON；相关研究差异仍留待正文核实。执行者实际阅读后，按获授权合成角色暂不确认并提出这两项内容反馈。主对话明确此为正常审阅决定，不是相同请求重采样；`rp07-03` 只传审阅意见，不给工具、状态或人工正确方案。首次不足及当时方案保存在 `RP_RUN/requests/rp07-02/`。

`rp07-03` 于 09:35:33–09:36:18 UTC 正常结束，回复中展示了具体的中文方案、相关研究差别和文本细读方法。但回复明确称尚未写回工作版本；稿件状态仍为版本 6，保存的 `scheme-1` 仍是先前含待核占位的内容，不能将对新展示内容的确认套到旧记录。该次回复又将 1996 年论文作者前田角藏误写为前田雅之；泛化的书目信息待核说明不能消除这一具体错误。执行者没有确认、手动写回或重复要求同样内容，按主对话安排交原主技能负责人核对保存、展示、确认之间是否有可定位缺口。

原负责人只读核对后未找到产品连接缺口，零修改。安装说明已明确新方案在等待决定前保存，未确认时使用 `needs_input`；本次只有读取操作，没有保存尝试或组件错误。原材料记录正确保留“前田角藏”，错误姓名来自本次回复。该方案未满足有效交付条件，不能据会话正常结束推进确认或成稿；已向主对话交接具体依据，当前不重复相同请求。

RP-09 的独立空白表读取请求于 09:48:30–09:48:47 UTC 完成。主技能读取真实招生表文本并查看整页图像，识别一页封面、另附 A4 横写正文约 2,000 字、两处装订，以及英美文学英语约 500 words 和史学史料要求。执行者对照原图确认该子项通过，甲项目状态原字节未变；没有把这张真实表套入合成甲项目，也不将该结果替代尚待成稿的两种模板导出。

RP-13 的原稿状态含绝对工作目录，普通副本续接会指回原稿。原准备者据此修正为原路径快照、独占执行、保留本次结果后恢复；同一准备审核者关闭 PRP-11，主对话批准 r9 第二关。没有增加搬迁能力或手改状态。

`rp13-missing-vision` 于 10:07:26–10:08:11 UTC 完成，使用同一 677 安装、原模型、预算 1 和 600 秒超时。实际材料组件返回 `blocked/vision_configuration`，列明三项配置缺失，保留原件、完整响应与空文字块；主技能保存缺项，未把扫描内容作为完整证据。状态由 6 更新为 7，原问题确认、方案未确认、条件及对应步骤保持不变，正文与两种导出仍待完成。确认所有命令结束后，执行者归档当次稿件，再恢复原稿和正常配置；目录比较及配置字节比较均退出 0，后续仍从原版本 6 继续。正常扫描引用同一原图和未变实现的 RP-06 结果，未重复调用视觉服务。

该次回复的“扫描读取结果”链接有效，但第二个“材料步骤”链接误用内容摘要拼成文件名，实际状态保存的是另一 UUID 文件名。此局部交付错误完整保留；实际材料和缺项已经保存，原稿恢复成功的观察不受影响。没有为该链接重复请求或手改回复，交同一实现审核者依原范围核对。执行者的首次只读状态比较表达式有括号错误，修正后仅从已保存的前后归档读取，未重跑业务或修改产品，说明保存在该运行目录的检查记录中。

交接勘误：该次材料步骤实际位于 `RP13_OUTPUT/proposal.after` 内、按已归档状态指向的实际材料步骤，含原 5 份材料及新增扫描缺项。精确位置仅保存在外部 `RP_RUN/requests/rp13-missing-vision/link-correction.md`，本轮目录绑定见外部 `RP_RUN/config/rp13-bindings.env`。此归档只供读取，恢复后的原稿仍是版本 6；原回复保留不变，不从故障归档继续业务。

用户随后明确要求“你要不再试试看，我总感觉很奇怪”。主对话在 r10 中仅批准 RP-04 的一次原条件追加请求，不将其视为产品修复或模型变更。执行者核对原 5 个招生输入原字节一致、没有新增正式上游成果、前序请求和原采集子代理已结束；现有安装和独占服务可续接。消费者配置由原表达式及绑定恢复为预算 6、原 r8 网络设置，与失败请求所存配置逐字节相同；原 `eval-request.json` 原字节复制，沿用 `gpt-6-luna`／`low`、石川巧决定及 1,800 秒超时。`RP_RUN/requests/rp04-02-user-retry1` 于 11:35:26 UTC 发出，未添加提示、修改产品或操作评估服务，原失败和 r9 第三关结论保留；本次结果须另按实际业务判断。

该请求于 11:46:09 UTC 自然结束，固定适配器无问题，实际累计创建 6 个子线程。主线程依次委派、等待并消费原采集代理、方向预筛代理与阶段 0 代理。实际 `papers.json`、完成记录和预筛文件保存 183 篇论文记录（181 篇保存、2 篇重复），未下载全文；预筛有 10 个方向，摘要覆盖 0/183，明确只按题名及主页研究领域归类、均为低置信。发现结果依次为 `collect`、`preview`、`stage0`，最后停于真实方向选择需求；此时只有教授选择，尚无目标、第一阶段快照、正式输入包或候选。该次完成了正常用户返回点，不代表 RP-04 全部通过，也不证明旧的零委派失败已被修复。

原完整任务和合成申请者授权仍有效。执行者阅读 10 个真实选项后，选择“近代文学、国语教育与读者制度”：其 11 个题名级成员与合成申请者既有的文学课程及注释练习准备相关，初步兴趣为文学作品进入教材、课堂和考试后，阅读方式如何受到教学目标和评价要求影响。该决定只选上游方向，不代替研究问题或中文方案确认；没有预填尚未出现的全文访问方式选择。新请求 `rp04-03` 沿用原产品、模型及 1,800 秒超时，累计预算 3 来自阶段 0、阶段 1 下载负责代理及缺少访问决定时的原采集代理各 1；按原流程应停于尚缺的真实访问决定，未增加临时业务停点。

该正常决定请求于 11:55:40–11:55:52 UTC 完成，固定适配器无问题，实际子线程数为 0。主技能把教授姓名直接传给 `selection.professor_path`，组件按普通路径解析后正确返回 `needs_input/selection_outside_scope`，并列出范围内的实际教授路径；方向编号本身正确。该错误分支先于材料校验，返回的空 `materials`、`valid_artifacts` 不能证明没有可用材料。最终回复却作出这一推断，并在已承认应改用返回路径继续发现后直接结束；没有第二次发现、阶段 0 委派或目标保存，也没有工具异常或线程耗尽的证据。该次仍是业务失败，不追加相同请求，不人工纠正产品状态。原始响应、解析及观察保存在 `RP_RUN/requests/rp04-03/`。

原主技能负责人对已返回的路径语义和现行说明作只读核对：当前字段约定已足以区分显示姓名与实际路径，组件范围校验未发现缺陷。可选的运行说明补充仅是明确“用已发现对象的路径原值对应用户决定”和错误分支尚未校验材料；它是针对初次误传的改进假设，不能解释或保证消除模型已理解纠正办法后仍提前结束。本轮没有据此修改产品、配置、提示或自动复验；交原实现审核者只核对新增结果及直接影响，其余有效结论保留。

用户随后明确要求修正后重跑。两份路径用法说明经原负责人修正、同一实现审核者静态复核后，由主对话固定为 `b983497308157dedec6b4d97f16c95dc0b0f60f9`。原准备者补齐换版和原路径恢复步骤，同一准备审核者完成定向复核，主对话批准 r11 第二关。共享夹具主分支更新后仍为原固定版本。没有更换模型、修改测试业务提示或新增文案关键词断言。

执行者按 r11 于 13:01:41–13:02:23 UTC 完成新远端四输出构建、原位置空目录正式激活和资料恢复，均退出 0。旧消费者完整归档于 `RP_RUN_PATH_FIX/consumer.before`；新安装只从原归档恢复 `input` 及 `.test-runtime`，两目录比较均为 0，没有复制旧受管技能或代理。两份实际安装说明与已审核冻结文件一致。配置从新安装快照和原表达式重建，保持正常视觉配置、r8 网络与预算 3，未操作现有服务；原状态和全部失败记录保留。

`RP_RUN_PATH_FIX/requests/rp04-03-path-fix1` 于 13:03:17 UTC 发出。准备入口退出 0、`loading_method=config-args`；提示与原 `rp04-03/prompt.txt` 原字节相同，预算说明沿用，模型仍为 `gpt-6-luna`／`low`、超时 1,800 秒。该受影响请求按原 RP-04 观察点等待实际结果，安装或静态检查不代替业务通过。

该请求于 13:04:46 UTC 正常结束，适配器无问题，真实创建 3 个子线程。主技能先不带选择发现，再原样使用返回的绝对教授路径及原方向编号；真实委派阶段 0、阶段 1 及原采集代理，等待并消费结果。教授目标保存原 11 成员方向与兴趣备注；阶段 1 按原候选规则扩展到 12 篇，快照为 `pdf_fill_needed`、12 篇缺 PDF、没有未解析条目，仍标明候选不是最终方向成员。所有子线程读取状态为 `idle`。最终展示真实访问选项，没有默认下载授权。路径发现、原值传递、目标保存和快照建立的受影响行为在本次复验通过，完整 RP-04 仍未完成，旧失败保留。

执行者阅读实际访问选项后，按合成申请者授权选择 `oa_only`，因为没有提供机构订阅权限的事实。`rp04-04-access` 于 13:12:07 UTC 作为新的正常决定请求发出，沿用产品、模型和 1,800 秒超时。累计预算仍为 3，按阶段 1 下载负责代理、定向采集代理和单教授 worker 各 1 计算；进入阶段 2 前原流程尚须取得真实执行通道决定，未预填该答案或研究方案确认。当前配置不在请求中途改动。

该请求于 13:12:34 UTC 正常结束，实际子线程为 0。主技能先用 Python 解释器运行本应直接执行的 shell 包装器，得到语法错误；随后没有建立适用于本轮招生目录的请求文件，而直接使用一个仍指向 `input/empty` 的旧临时请求。组件正确返回该空目录的 `application_materials_required`，不是当前招生目录缺资料的结论。最终回复又误称请求文件缺失，表示需正确重跑后直接结束，没有委派或下载。请求文件返回时副本、错误及解析保存在 `RP_RUN_PATH_FIX/requests/rp04-04-access/`。

正式教授目标及阶段 1 快照与上一返回点逐字相同，没有手动纠正状态、临时请求或自动重复业务。此为新的调用和错误解释失败，不能抹去前次路径说明修正的实际通过，也不能用前次通过覆盖本次失败。当前完整 RP-04、正式输入包及其下游仍未完成，原非论文 RP-07 失败不受本次修改影响，没有重新采样。

原负责人已完成现有调用说明与直接入口的只读核对，零修改。主技能第 15 行及运行说明第 3–11 行已要求准备本次请求 JSON 并直接执行包装器；运行说明第 27 行明确使用本次给定路径。实际安装包装器为 bash，直接转发到固定 Nix 运行包；CLI 对必填请求路径直接读取 JSON，文件不存在会报读取错误，没有回退到空目录的逻辑。本次是已加载用法未被遵从、实际错误被误述后提前结束，未找到具体产品缺口；不凭额外提醒或改测试提示获得新采样机会。同一实现审核者已定向核对新增实际结果，确认路径修正通过范围、新失败及依赖状态记录准确，整体仍部分完成；其余结果沿用，正式第三关由主对话决定。

用户之后明确要求对 OA 决定请求再试一次，主对话在 r12 中批准唯一一次原条件追加请求。该授权不表示产品或服务已修复，也没有批准更换模型。执行者确认原请求结束且没有委派，当前配置、教授目标和阶段 1 快照与保存件逐字相同；12 篇仍缺 PDF，183 条论文状态均为 `pending`。现有服务端点只读确认监听，夹具主分支由主对话更新后仍为原固定版本，没有启停服务。

`RP_RUN_PATH_FIX/requests/rp04-04-access-user-retry1` 于 13:42:44 UTC 发出，直接使用原 `eval-request.json` 原字节，配置、业务提示及预算说明一并保留并比较。产品仍为 b983，模型仍为 `gpt-6-luna`／`low`，预算 3、超时 1,800 秒；没有重装、重新生成评估请求、补操作提示、删除旧临时 JSON 或改写产品状态。原失败及路径修正通过记录保留，本次另按实际业务结果判断。

该请求于 13:45:39 UTC 自然结束，实际委派下载负责代理、采集代理和单教授 worker 共 3 个子线程，均已结束。原负责代理只处理 12 个候选与 `oa_only`。worker 的 Zotero 连通检查成功，另读取一个来源页面及本地论文记录；没有附件查询、PDF 导入或 Zotero 写入调用，也没有对应机器错误。它却以“没有 Zotero MCP 写入／导入工具或技能加载接口”的自述返回错误，上游据此返回部分完成。这不能证明真实服务或角色缺少写入能力，已交原负责人只读核对固定入口，不通过额外试写或下载探针取证。

下载数仍为 0。阶段 1 重建及校验完成后快照仍为 `pdf_fill_needed`、12 篇缺 PDF、零未解析；目标与原保存件相同，`papers.json` 与归档原件逐字相同，183 条论文仍为 `pending`。相关返回和必要调用解析在该请求的 `worker-events.json`、`worker-result.json`、`owner-results.json`、`stage1-at-return.json`。此次实际委派成立，但完整 RP-04 仍为业务失败，没有新用户问题可继续；唯一追加请求已结束，不自动重复或更换模型。

原负责人只读核对固定安装后确认：worker 的附件查询入口明确是 `run-tool curl` 调用本机 Zotero HTTP 的条目附件路径；已安装的 `zotero-save/SKILL.md` 规定通过同一 curl 传输初始化 MCP 会话、调用 `write_item` 的 `import` 操作，不要求会话暴露独立 Zotero 写入工具。本次 worker 已能执行该包装器，却没有读取这份说明、查询附件或尝试初始化与导入。未发现必需入口未安装或实际调用证明的写入能力故障；连通检查成功也不代替写入验证。

原 worker 的加载语句仍使用 `skill(name:...)` 写法，只能作为上游角色用法可读性的改进假设；文件实际存在且未出现读取失败，不能据此认定本次原因，也不在新技能中复制上游入口或增设能力认证。本轮零产品修改。同一实现审核者已定向核对新增结果及直接说明，确认记录准确、没有新增修正要求，整体仍部分完成；原路径修正通过及其他有效结果保持，正式第三关由主对话决定。

## r21：环境重建后的真实会话执行（2026-11-21）

本轮产品固定为 `e6ebaa4224e8d12f3ba7d9e6c60e2c31b4d4254c`，四个 Nix 输出从 `/nix/store` 复用、未重建；消费者为重建后的 `$RP_CONSUMER=/private/tmp/research-proposal-r21-run.dpYLsb/consumers/nix`，结果根 `RP_RUN=/private/tmp/research-proposal-r21-run.dpYLsb`。上一轮 r20 结果根随机器重启丢失；本轮只重建离线可验证部分（输入夹具、RP-01 安装检查、RP-03 至 RP-06、RP-10 导入组件），其日志在 `$RP_RUN/logs/`（RP-01 的无关项在业务请求后补检，见偏离 7）。下表的 RP-07 至 RP-13 为本轮新执行结果；RP-01 至 RP-06 采用本轮准备记录。

### 结果表（四状态）

| 编号 | 结果 | 说明与证据 |
|---|---|---|
| RP-01 | 通过（补检） | 主技能、六项直接依赖、17 个原代理按检查项核对。**重建时漏预置** `test/fixtures/install` 的无关技能与无关配置；用同一激活器在临时目录探针确认激活会保留预置项（`$RP_RUN/logs/activation-probe.log`），故为准备遗漏而非激活覆盖。RP-07/08/10/11/12/13 主请求结束后从夹具恢复 `unrelated-note` 与 `model_reasoning_effort`（补检后使用恢复配置的请求为 `rp08-paper-materials-2`、`rp08-paper-confirm`、`rp13-vision-missing` 三个；RP-07/08/10/11/12/13 主业务请求未使用这些预置项），补检结果在 `$RP_RUN/logs/rp01-install-inspection.txt`（主技能、6 个依赖、17 个代理、无关技能、配置条目逐项 OK）。该恢复发生在业务请求之后，业务结果未使用这些项。 |
| RP-02 | 通过（沿用） | 本轮未改技能资源布局；安装入口与文件集合同前，按 r14 只复核改写后的文档观察。npx 未重跑。 |
| RP-03 | 通过 | `test_inputs.DiscoveryTests` 3 个方法 `ok`、退出 0；见 `$RP_RUN/logs/rp03.log`。 |
| RP-04 | 通过（本轮准备） | `test_inputs.UpstreamRoutingTests` 1 个方法 `ok`、退出 0；见 `$RP_RUN/logs/rp04.log`、`rp04.exit`。 |
| RP-05 | 通过 | `test_inputs.AnalysisRoutingTests` 1 个方法 `ok`、退出 0；见 `$RP_RUN/logs/rp05.log`、`rp05.exit`。 |
| RP-06（文字载体） | 通过 | `test_inputs.MaterialTests` 2 个方法 `ok`、退出 0，覆盖文字 PDF、TXT、Markdown、EPUB、HTML 和 `.docx` 载体（`$RP_RUN/logs/rp06.log`、`rp06.exit`）；`.docx` 断言按 2026-11-04 决定只作历史资产、不作通过条件。 |
| RP-06（扫描页/图片） | 通过（沿用，原始输出丢失） | 按 `test-plan.md` 第 406 行“RP-06 的六类文字载体、未支持格式、四处人工定位及扫描结果，均采用仍适用的已有结果，不因 r14 重跑”，本项沿用扫描记录，不重跑视觉模型。**记录来源版本为 `4dfb8bed5a17480728a073f951ba18e98c177829`**（见本文件第 219 行“扫描修正版本”），不是 677 版本。沿用前提逐段核实：`4dfb8bed5a17480728a073f951ba18e98c177829..677055164c06d549f99b6e04a2e80d30f7b871c3` 之间 `_material_readers.py` 改动 230 行、`_materials.py` 改动 33 行，差异集中在文字载体读取新增 `movable_root` 参数与 HTML 解码、OCR 缓存由 `read_json`/`write_json` 改为 `read_record`/`write_record`、`ocr_failed` 文案改为携带 `diagnostic_path`；扫描成功路径未变——`vision-glance --ocr` 调用、`origin = "live_stdout"`、区域 locator 语义、`_vision_configuration` 的缺项判断均保持原样。`677055164c06d549f99b6e04a2e80d30f7b871c3..e6ebaa4224e8d12f3ba7d9e6c60e2c31b4d4254c` 之间该两文件无改动（`git diff --stat` 为 0 行）。扫描记录本身保留在本文件第 296 行：同一原图下两个区域的 `origin` 均为 `live_stdout`，产品返回候选转录及待核事项，执行者按原图逐处核对并记录了被遮挡数量不能判断、原图印刷说明可读、两段服务坐标占位和操作注释不是原文，未清空产品待核标记。**证据状况如实说明**：原始输出目录 `RP_RUN_PREVIOUS/logs/rp06-*` 随 `/private/tmp` 清空丢失，本条以既有文字记录、上述代码差异核对结论和计划的明确沿用要求为依据，不声称原始产物仍在。本轮另以受控缺配置实测了同一条材料读取路径：组件返回 `blocked` 与 `vision_configuration` 具体缺项并保留原件（见 `requests/rp13-vision-missing/`），说明读取入口仍正常工作。 |
| RP-07 | 通过 | 两条路线均由安装后的主技能完成真实会话。**论文路线**（`requests/rp07-paper-01/` 至 `-03/`）：展示候选 → 选择「叙述评价的归属」问题 → 形成中文方案 → 补入 `access-supplement.md` 后按实际条件更新方案。三次返回时磁盘状态依次为 `state_version=2/4/5`、`current=null`、`body=pending`，未提前生成正文。**非论文路线**（`requests/rp07-nonpaper-01/`、`-02b/`）：独立材料路线 `discover=read_materials`，保存 q1 与中文方案；`state_version=2` 时 `current=null`、`conditions.resolved=false`、无正文；`state_version=4` 时 question 已确认、scheme 待确认、仍无正文。问题与方案两处决定分别保存；条件未写成已取得。**输入偏离见下文**。 |
| RP-08 | 通过 | 两条路线各完成一稿并提交。**论文日文**：第 1 版 `requests/rp08-paper-01/`，`state_version=19`、`current=r-20261121T091245-c515602fb832`、7 栏、固定口径 2105 字符；按用户反馈修正第五栏标题与参考文献后，`requests/rp08-paper-02/` 提交 `state_version=25`、`current=r-20261121T092543-03235eb2409d`、7 栏、2103 字符（1800–2400 内）。后续按 IR-40 补材料并由合成申请者确认方案后，`requests/rp08-paper-confirm/` 提交当前有效版 `state_version=37`、`current=r-20261121T093049-daa4c4230eb0`、7 栏、固定口径 2093 字符（1800–2400 内）、`步骤-materials` 5 项含申请者资料与项目要求，`delivery_formats=["md"]`、`checked_formats=["md"]`、`content_consistent=true`、`artifacts` 只含 `md`。**非论文中文**：`requests/rp08-nonpaper-01/`，**交付时** `state_version=10`、`current=r-20261121T092812-388c7bcf344f`、7 栏、1540 字（1200–1600 内），同样只交付 `md`。该稿此后经 RP-10 场景 2 按用户明确要求改成英文（该场景版本为 `r-20261121T094302-e131e06b00f4`，7 栏 6753 字符），再经场景 3 与场景 4b 推进到当前版 `r-20261121T095506-f83d0d9ad1e2`（7 栏、固定口径 7088 字符），那是 RP-10 的后续授权结果，不回写为 RP-08 失败；RP-08 的通过对象是交付时的 `r-092812`。两稿的 `研究计划草稿.md`、`正文.json` 的 SHA-256 均与状态内 `checks.digests` 相等。**显示层保留**：Markdown 中参考文献的 em dash 显示为 `P1---P6`、非论文引用编号显示为 `\[1\]`；正文 AST 为 `—`/`[1]`，`review_revision` 读回一致，作为显示瑕疵记录，不另立通过条件。 |
| RP-09 | 未执行 | 用户已延期；不运行 Word 模板、转填或页面检查。 |
| RP-10 | 通过 | **导入组件**：本轮准备环境中的 `test_inputs.RevisionImportTests` 1 个方法 `ok`、退出 0（`$RP_RUN/logs/rp10.log`、`rp10.exit`），供本项「Markdown 内容差异读入」复用。**四个实际改稿场景**均从**当时 `current` 指向的已提交版本**复制修改稿（`scripts/make_revision.py` / `replace_section.py` 记录 base/output SHA-256 与 diff），每次独立请求；会话实际加载并使用主技能（RP-10 的六个提示词没有逐一写技能名称，见偏离 10）。**场景 1 纯措辞**（`rp10-s1-wording/`）：3 处替换，修改稿 `498e629e…` 与新提交 `r-20261121T093955-2eeac87bb58e` 逐字节相同；与基线 diff 仅 3 处、2 段；`question`/`scheme` 仍 `q1-public-final-v1`/`q1-scheme-public-final-v1` 且 confirmed，原确认复用。**场景 2 明确授权改核心方法并改英文**（`rp10-s2-method-english/`）：`question`/`scheme` 改为 `q1-reader-survey-v1` 并重新确认，decision 记录用户要求；新提交 `r-20261121T094302-e131e06b00f4`、7 个英文栏目，招募/伦理/同意为待办，未写成获批。**场景 3 文件自行写成已取得**（`rp10-s3-unverified/` + `rp10-s3-confirm/`）：首次请求识别「已取得许可/已完成比对/伦理已批」与条件记录冲突，保留导入原件与差异记录，**未写正文、状态与 `current` 不变**（24 / `r-20261121T094302…`），并向用户提出处理方式；第二次按决定只改「Schedule and Feasibility」栏，新提交 `r-20261121T095054-0243a4581b29`、`state_version=30`，与上一版 diff 仅该栏 6 行，确认与其余栏目未动。**场景 4 两份冲突稿**（`rp10-s4-conflict/` + `rp10-s4b-select-b/`）：A=细读＋第二编码者、B=五人思维出声访谈，两份都导入保留并列出影响，**状态版本/`current` 前后不变、`works` 未增加**，未按修改时间合并；用户选 B 后新提交 `r-20261121T095506-f83d0d9ad1e2`、`state_version=38`，`question`/`scheme` 改为 `q1-think-aloud-five-v1` 并确认，问卷/二十人招募改为访谈设计，伦理、同意、招募、转录、编码均为待办。 |
| RP-11 | 通过（基准偏离见偏离 9） | 实际基准为同一非论文稿在 RP-10 场景 4 后的当前提交版 `r-20261121T095506-f83d0d9ad1e2`（RP-08 交付版为 `r-20261121T092812-388c7bcf344f`）；`RP_TEST_PROPOSAL` 绑定 `input/nonpaper/研究计划/甲项目-联系教授`。`RP_SAVE_REQUESTS` 由当前版四份步骤数据用 `jq` 生成（`config/save-requests.json`）；`RP_RELATED_MATERIAL_RECORD=material-1.json`（`status=ready`，原文 `研究资料/材料/门灯.md` 在消费者 input 内）。命令 `uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v test_recovery.RecoveryTests` 从 `$RP_WORKTREE/test` 执行，8 个方法全部 `ok`、`Ran 8 tests in 6.318s`、退出 0，见 `$RP_RUN/logs/rp11-components.log`。运行前快照 `snapshots/rp11-proposal-before/`；运行后状态 SHA-256 不变、`current` 仍 `r-20261121T095506…`、`门灯.md` 恢复为原字节（`8b2721a3…`）。 |
| RP-12 | 通过 | 按计划先 `cp -p` 复制 `test/fixtures/applications/program-b.md` 到 `$RP_CONSUMER/input/nonpaper/` 并 `test -r` 成功，再从甲项目已提交稿发请求（`requests/rp12-program-b/`），明确复用文献与通用方案。新建独立稿件 `input/nonpaper/研究计划/乙项目-面试准备`：`proposal_id=proposal-199bf18b1676437f81aa9e694c868af6`、`binding={乙项目-面试准备, 面试准备, q1}`、`state_version=9`、`current=r-20261121T095953-0b6dfcc09910`；五个栏目（拟研究的问题／选题依据／实施步骤／条件与替代办法／参考文献）与固定口径 977 字（800–1000 内），未沿用甲稿七栏目。`inputs.material_paths` 记录复用来源，确认 revision 为 `q1-think-aloud-five-v1-b-interview` 独立确认；`delivery_formats=["md"]`、`checked_formats=["md"]`、`artifacts` 只含 `md`。请求前后甲项目状态 SHA-256 相同、5 个版本目录相同，未被改动。 |
| RP-13（缺资料分支） | 通过 | **空目录**（`requests/rp13-empty/`）：`discover` 返回 `needs_input`，说明缺可读材料、招生项目、教授与研究依据；未联网、未建项目。**仅学校名称**（`requests/rp13-school/`）：只给 `松川大学.txt`，`discover` 返回 `read_materials`，保存学校名称材料与缺项清单到 `input/nonpaper/研究计划/松川大学-联系教授`，状态 `state_version=2`、`current=null`、materials=complete、question/scheme/body=pending，未从任意网页建完整项目。 |
| RP-13（外部能力缺失分支） | 通过（r13 记录 + 本轮缺配置复核） | 原记录“未执行”把该分支误当成需要付费视觉识别；按 `test-plan.md` 第 150 行，该分支要求的是“使当前必需的一个外部能力不可用，例如未配置扫描文字识别服务”，不需要真实付费识别。**通过依据分两部分，不能由本轮新请求单独成立**：其一，计划第 150 行同时要求“在已有进度的隔离资料中”制造该故障、第 152 行要求“保存原错误或缺项及已有进度”，这一半由本文件第 342–346 行的 r13 记录覆盖——677 版本 `rp13-missing-vision` 在已有问题确认、方案和条件的稿件上返回 `blocked/vision_configuration`，状态由 6 更新为 7，原问题确认、方案未确认、条件及对应步骤保持不变，正文未生成，随后归档并恢复原稿；计划第 186 行也明确“RP-13 及未受影响的导入组件结果继续使用 `test-results.md` 的有效记录”。其二，本轮以受控缺失配置复核了当前产品的同一路径：`requests/rp13-vision-missing/`（`http-status.txt=200`、`passed=true`、`exit_code=0`、有 `turn.completed`，`thread_id` 与其余 21 次互不相同）。隔离目录 `$RP_CONSUMER/input/rp13-vision-missing/` 放同一 `damaged-scan.png`（与夹具同字节），`VISION_ENV_FILE` 指向 `$RP_RUN/config/vision-missing.env`（故意不含 `VISION_API_KEY`、`VISION_BASE_URL`、`VISION_MODEL`，文件内注明用途）。实际结果：材料组件返回 `status=blocked`、`issues=[{kind:"vision_configuration", message:"指定配置文件缺少：VISION_API_KEY、VISION_BASE_URL、VISION_MODEL"}]`（`working/material-read-result.json`），`blocks=[]`、`ocr_outputs=[]`，原件保留；主技能明确说明“技能要求显式配置 `VISION_ENV_FILE`，不会扫描用户目录或改用未经授权的视觉服务”，按原图逐处核对后只记录可辨认内容（“合成扫描样本，不是历史档案”、记录编号“乙七”、期刊仅供馆内阅览），对“借阅数量”后被黑块遮挡的数值明确记为无法辨认，未猜测，未据此刻画研究主题。**该新请求的限制需注明**：该隔离目录只有扫描图与 `working/`，没有项目状态或已提交稿，因此“已有进度”这一半不由它覆盖，只能由前半的 r13 记录覆盖。**另有一处交付瑕疵如实记录**：该次最终回复声称保存了“研究计划草稿.md”并链接 `$RP_CONSUMER/input/rp13-vision-missing/研究计划草稿.md`，该文件实际不存在（目录只有 `damaged-scan.png` 与 `working/`），材料记录链接有效而草稿链接无效，属交付层错误，交实现审核者核对，不据此认定完整草稿已保存。全程未进行任何付费识别，未使用用户实际视觉配置。 |

### 三份稿件终态

下表是 r21 执行结束时的状态。论文稿在 r22 修复 IR-45 后另建了补正版本：`state_version` 44、`current=r-20261121T135022-23ab987a4971`，正文与 Markdown 逐字节沿用 `r-093049` 的内容，详见文末「r22」一节；本表其余三行的当前值未变。

| 稿件 | `state_version` | `current` | 栏目 | 固定口径篇幅 | `delivery_formats` / `checked_formats` | `committed` |
|---|---|---|---|---|---|---|
| 论文（林安，日文） | 37（3 版全部已提交，`工作版本/` 为空） | `r-20261121T093049-daa4c4230eb0` | 7 | 2093 字符 | `["md"]` / `["md"]` | true |
| 非论文甲项目（RP-08 交付版，中文） | 10 | `r-20261121T092812-388c7bcf344f` | 7 | 1540 字 | `["md"]` / `["md"]` | true |
| 非论文甲项目（RP-10 后当前版，英文访谈） | 38 | `r-20261121T095506-f83d0d9ad1e2` | 7 | 7088 字符 | `["md"]` / `["md"]` | true |
| 乙项目（中文，面试准备） | 9 | `r-20261121T095953-0b6dfcc09910` | 5 | 977 字 | `["md"]` / `["md"]` | true |

字数口径固定为：拼接全部 `Str`、排除题目块的题目正文、文献列表内容不计入、栏目标题计入。脚本 `$RP_RUN/scripts/count_body.py` 对每版 `正文.json` 计算，结果分别保存在对应请求目录的 `body-count.json`。**1200–1600 字**是甲项目非论文路线中文正文的要求；RP-10 场景 2 按用户明确要求把正文改为英文，篇幅按同一固定口径记 6753 字符（`requests/rp10-s2-method-english/body-count.json`），不再套用中文 1200–1600 作为该场景通过条件；场景 4 选 B 后当前版为 7088 字符（`requests/rp10-s4b-select-b/body-count.json`），同样只记录实际篇幅。乙项目 800–1000 字与论文 1800–2400 字符按各自要求核对。上一版记录曾把场景 2 的 6753 误写到当前版行，本次按实际计算改正为 7088。

### 实际命令与请求索引

- 评估请求：`POST http://127.0.0.1:17902/eval`，body 为 `{"command": "--cd <consumer> --model gpt-6-luna --sandbox workspace-write -- '<prompt>'", "timeout": 600}`。发送脚本 `$RP_RUN/scripts/send_request.py`；早期请求目录保存 `prompt.txt`、`eval-request.json`、`response.json`、`http-status.txt`、`curl.exit`、`times.txt`、`summary.json`（各请求另存 `state-at-return.json` 快照；`requests/rp13-empty/` 没有稿件状态，未另存）。**后三个请求的文件集不同需注明**：`rp08-paper-materials-2/`、`rp08-paper-confirm/`、`rp13-vision-missing/` 只保存 `eval-request.json`、`response.json`、`http-status.txt`、`curl.stderr`、`start.txt`（`rp13-vision-missing/` 另有 `end.txt`），提示词可从 `eval-request.json.command` 复原；前两者没有 `state-at-return.json`。22 次请求（18 次主业务请求 + 1 次审核后材料补充请求 + 1 次论文材料补做 + 1 次方案确认 + 1 次缺配置复核）全部 HTTP 200、`passed=true`、`exit_code=0`、有 `turn.completed`，22 个 `thread_id` 互不相同；请求索引见 `$RP_RUN/requests/INDEX.md` 与 `observations/`。最后一次缺配置复核为 `requests/rp13-vision-missing/`，其隔离目录无稿件状态，未另存 `state-at-return.json`。
- 实际生效：`approvalPolicy=on-request`、`approvalsReviewer=user`、`sandbox=workspaceWrite`、`networkAccess=false`。
- 组件测试：RP-11 命令见上；RP-03 至 RP-06 的日志与退出码在 `$RP_RUN/logs/`。
- 篇幅与摘要核对：`$RP_RUNTIME/bin/python3 $RP_RUN/scripts/count_body.py <正文.json>`；`shasum -a 256` 对每版 Markdown/正文与状态内 `checks.digests` 独立比较。

### 执行偏离与未闭合项

1. **非论文基线缺失（输入偏离）**：旧消费者中的《罗生门》材料、相关研究、甲项目原稿与 `rashomon-read.json` 随 `/private/tmp` 清空丢失，仓库、夹具、Git 历史均无备份。本轮按现有合成写作包重建同结构的非论文输入（`input/nonpaper/研究资料/`、`研究条件/`），因此无法复现计划所写的「复用既有《罗生门》材料、版本 6、`rp07-03` 作者误写历史」。RP-07 非论文的逐步条件暴露也因补充条件与初始条件同目录而在第 1 次请求即被读到。上述偏离记在 `observations/rp07-nonpaper.md`；RP-07/08/10/11/12 的其余业务观察点按重建后的真实材料执行。
2. **执行偏离：请求未重申稿件路径**（`requests/rp07-nonpaper-02/`）：该次提示词未写非论文稿件目录，主技能定位到论文稿并另建未提交工作版本 `r-20261121T093049-daa4c4230eb0`。非论文稿未变（`state_version=2`、`current=null`）；论文稿 `current` 未变，仍为已提交版 `r-20261121T092543…`，新增的未提交工作版本按产品规则保留，未手改或删除。该次不计为非论文业务结果；以显式路径重发一次（`-02b/`）。
3. **运行配置未按 r14 表达式重建（IR-42）**：本轮交接只提供安装后的消费者配置与安全请求格式，未提供 `ZOTERO_*` 隔离值、`RP_VISION_CONFIG` 与 `RP_INSTALLED_CONFIG`；请求按交接的 `--cd/--model/--sandbox` 形式发出，实际 `networkAccess=false`，未额外禁用两个 MCP 服务。本轮全部业务只读本地材料，未依赖联网；该差异不影响材料与稿件状态，但属于准备层偏离，是否重建配置或补跑由测试计划负责人决定。
4. **论文稿材料步骤缺申请者与项目要求记录（IR-40，已修复）**：论文稿交付版 `步骤-materials` 原只保存作品与两篇研究（3 项），申请者资料与甲项目要求通过会话读取，未成为材料记录。审核后补发一次请求（`requests/rp08-paper-materials/`），主技能用 `read_material` 读取并保存了 `applicant.md`、`program-a.md`，但把结果写进了当时的未提交工作版本 `r-20261121T093049-daa4c4230eb0`，且该版本方案仍是 `needs_input`，主技能按流程正确拒绝提交并请用户确认方案。本轮据此补做：`requests/rp08-paper-materials-2/` 再次确认材料已补入该工作版本（各 5 个原文块，申请者材料明确标注不承担学术引用）；`requests/rp08-paper-confirm/` 由已授权的合成申请者审阅该版中文方案《话语归属与推断边界——以《门灯》公开定稿为中心》后确认，主技能完成正文交付。最终论文稿 `state_version` 37、`current=r-20261121T093049-daa4c4230eb0`、`committed=true`、`delivery_formats=["md"]`；`步骤-materials` 保存 **5 项**（作品公开定稿、林安研究、周岚研究、申请者资料 `applicant.md`、申请项目要求 `program-a.md`）；正文 7 栏目、固定口径 **2093 字符**（项目要求 1800–2400），`content_consistent=true`、`checked_formats=["md"]`。**仍存的次要缺口如实记录**：`工作版本/研究计划输入.json` 的 `requirements` 字段未随项目要求更新（仍是“中文方案先审阅，正式正文目标语言待项目要求确认”），项目要求实际保存在材料记录中；`inputs.material_paths` 也未加入两份新文件路径。该缺口不影响正文与材料记录本身的可核对性，但记录与输入的对应关系仍不完整，交主技能负责人判断是否另需修正。
5. **显示层瑕疵**：两稿参考文献的 em dash 在 Markdown 显示为 `P1---P6`，非论文引用编号显示为 `\[1\]`；正文 AST 与被引原文未变，`review_revision` 读回 `content_consistent=true`。不另立测试，也不改称正文已被手改。
6. **RP-09 未执行**：按用户已确认的延期范围，Word、模板、LibreOffice、页图均未执行。
7. **RP-01 重建时漏预置无关项（IR-36，已补检）**：重建消费者没有 `test/fixtures/install` 的 `unrelated-note` 与 `model_reasoning_effort`。用同一激活器在临时目录（`scratch/activation-probe/`）预置后激活，两项均保留（`logs/activation-probe.log`），故属准备遗漏、不是安装覆盖。主请求结束后从夹具恢复并补检（其后仅 `requests/rp08-paper-materials/` 使用该配置），`logs/rp01-install-inspection.txt` 记录主技能、6 个依赖、17 个代理、无关技能和配置条目均 OK；恢复发生在业务请求之后，未用于业务结果。若负责人要求“安装检查必须在请求前完成”，本项应改判为准备顺序偏离。
8. **RP-06 扫描页与 RP-13 外部能力分支（IR-37，已闭合）**：原先因缺 `RP_VISION_CONFIG` 记“无法判断/未执行”，后按 `test-plan.md` 第 406 行沿用扫描记录、并以受控缺配置补做 RP-13 外部能力分支，两项均已闭合，依据见本表 RP-06（扫描页/图片）与 RP-13（外部能力缺失分支）两行。原始视觉输出随 `/private/tmp` 清空丢失，已如实披露；未使用用户实际视觉配置，未发起付费识别。
9. **RP-11 基准与计划文字不一致（IR-39）**：计划第 410 行要求基准为 RP-08 产生的真实提交稿，实际运行使用 RP-10 场景 4 后的当前版 `r-20261121T095506-f83d0d9ad1e2`（同一非论文稿的已提交后代版，RP-08 交付版 `r-20261121T092812-388c7bcf344f` 保留在 `works`）。`test/support.py` 只断言 `current` 非空，没有绑定具体修订号，测试本身无法发现基准变化。8 个方法仍是在真实已提交稿上执行、未观察到代码路径差异，但“RP-08 基准”与固定顺序未按计划文字满足；是否接受替代基准由测试计划负责人决定，若不接受需在获批顺序下重跑。
10. **提示词未逐一写技能名称（IR-41，记录已改）**：RP-10 六个提示词、RP-08 两个写作提示词、RP-12 及 RP-07 的部分提示词只写业务要求，没有出现 `research-proposal` 名称；实际会话均读取并执行了安装后的主技能（`SKILL.md`、`runtime.md`、`proposal-runtime` 与保存/导出/提交）。这不是“只调组件 API”，但不符合计划第 116、158 行“每次明确点名”的文字；后续重发时应把技能名称写入提示词，旧请求保留为偏离记录。
11. **证据命名与测试范围的文字差异（IR-43）**：`logs/` 无 `rp03.exit`，RP-03 只有 `rp03.log`（3 个 `OK`）；实际文件名 `rp03.log` 等与计划示例的 `rp03-components.log` 不同；本轮重建后重新执行了 `RevisionImportTests`（计划第 406 行写“不因 r14 重跑”），属环境替代执行，已在 RP-10 行标明来源；`MaterialTests` 内部仍执行 `reading-room.docx` 子测试，`.docx` 只作历史资产、不作 RP-06 当前通过条件。

本轮未手改任何 `正文.json`、Markdown 或状态文件，未重置 `current`；所有稿件的保存、导出、核对与提交均由安装后的主技能完成。以上结果只说明实现符合性与测试执行情况，不构成计划关口、第三关或合并批准。

## r22：IR-45 修复、论文稿补正与受影响项复跑（2026-11-21）

合并审核的唯一阻断项 IR-45（`IMPLEMENTATION_DEFECT`）已在本轮修复并做真实验证。产品提交由 `e6ebaa4224e8d12f3ba7d9e6c60e2c31b4d4254c` 推进到 `457d8cfa5ad86881aaf06311766d227431291be6`（`feat/research-proposal`），两个提交只改状态组件与其对应文档：

| 提交 | 内容 |
|---|---|
| `67d1fde` | 材料步骤保存的每项材料按 `original_path` 进入依赖摘要（新 `adopted_materials` 项），并纳入导出、核对依赖与失效判断；`save_revision(stage="materials")` 把 `data.input_requirements` 同步为 `inputs.requirements`；后加摘要项在旧记录缺键时不判为变化。 |
| `457d8cf` | 材料步骤的读取记录本来就声明每份材料的 `digest`；再以该声明核对原件当前内容，记录与原文不符同样算材料变化。这样摘要项之前保存的旧记录也能发现原件被替换，原件未变时不误报。 |

`git diff --stat e6ebaa4..HEAD -- skills test flake.nix README.md nix` 只有 `README.md`、`SKILL.md`、`references/runtime.md`、`references/revisions.md`、`_state.py` 五个文件；`test/`、`flake.nix`、`nix/` 与两份计划文件均未修改。

**构建与安装**：结果根 `RP_RUN=/private/tmp/research-proposal-r22-run.t3ZjVR`，绑定见 `config/run.env`。四个输出从固定远端提交构建，均退出 0（`logs/build-*.log`、`logs/build-*.exit`）：runtime `msvk71zx32x1a4rhb2sv89d2sn49p81n`、package `3a95vpr8010i8i84lqh5721v15x3vzhp`、environment `cnskyah9z8krbzkb6fi8kkqrkmh562w6`、activate `7576fsl589x60n2yihq0m6m11id2vpha`。消费者仍在 `RP_CONSUMER=/private/tmp/research-proposal-r21-run.dpYLsb/consumers/nix`：原消费者完整归档在 `archive/consumer-before`，原位置预置 `test/fixtures/install` 的 `.agents`/`.codex` 后用激活器安装，激活输出（`agent-env: apply completed.`）与安装步骤同记在 `logs/install.log`，再原样还原 `input`（`diff -r` 无差异）。RP-01 安装检查在 `logs/rp01-install-inspection.txt`：主技能与四份参考、模板、包装脚本、六项直接依赖、17 份原代理、无关技能 `unrelated-note` 与配置条目 `model_reasoning_effort` 均存在，运行包指向新 store 路径。前一提交 `67d1fde` 的构建记录只在 `build/67d1fde/`，从未安装或用于任何业务结果。

**论文稿补正**：经消费者公开入口 `scripts/proposal-runtime` 依次调用 `begin_revision`、`save_revision(materials)`、`save_revision(body)`、`export_revision`、`review_revision`、`commit_revision`；请求与返回逐份在 `requests-ir45/paper-correction/`，摘要 `verification/paper-correction-summary.json`（该文件的 `product_revision` 字段记录的是运行时 store 路径，产品提交 SHA 以 `config/run.env` 与 `verification/ir45-verification.json` 为准）。未手改 `研究计划输入.json` 或状态文件。

| 项 | 实际值 |
|---|---|
| 旧提交版 | `r-20261121T093049-daa4c4230eb0`（`state_version=37`） |
| 新提交版 | `r-20261121T135022-23ab987a4971`，`state_version=44`，`committed=true` |
| `inputs.material_paths` | 5 条：作品、两篇研究、`applicant.md`、`program-a.md`（均为绝对路径） |
| `inputs.requirements` | 材料步骤 `input_requirements` 的结构化要求（甲项目、七栏目、论文日文 1800–2400 字符、非论文中文 1200–1600 字、一个核心问题）；与材料步骤数据及 `研究计划输入.json` 一致，不再写“目标语言待确认” |
| 正文 | `正文.json` SHA-256 `d2f1eee64f9daed076f077762c9dd9ac1c64a4b89550045cee64987bfc80a727`，与旧提交版逐字节相同 |
| Markdown | `研究计划草稿.md` SHA-256 `581f4dfb8902ebc2ba2e9025038b7bb32c83268aa3374598f05544297e8cda6f`，与旧版导出相同；7 栏，固定口径 2093 字符（`verification/paper-body-count.json`） |
| 交付与核对 | `delivery_formats=["md"]`、`checks.checked_formats=["md"]`、`content_consistent=true`、`artifacts` 只含 `md`；`question`/`scheme` 确认与条件沿用 |
| 版本保留 | 4 个版本目录全部保留，`工作版本/` 为空；旧版目录与补正前快照 `snapshots/paper-before-correction` 逐文件相同（`logs/paper-old-version.diff` 为空） |

**验收口径 1 的真实结果**（`verification/ir45-verification.json`；请求、返回与退出码在 `verification/responses/`）：

| 检查 | 实际返回 |
|---|---|
| A1 论文当前提交版未改动 | `committed`，`issues=[]` |
| A2 论文旧提交版 `r-093049` 未改动 | `committed`，`issues=[]`（没有后加摘要项也不误报） |
| A3 非论文甲项目当前版未改动 | `committed`，`issues=[]` |
| B1 改 `applicant.md` 后恢复论文当前提交版 | `needs_input`，`issues=[{kind:"committed_content_changed"}]`；恢复原字节后为 `committed` |
| B2 改 `program-a.md` 后同上 | `needs_input`，`committed_content_changed`；恢复后 `committed` |
| C1 同一旧提交版、同一 `applicant.md` 改动，旧产品 `e6ebaa4` | `committed`（复现 IR-45 漏检） |
| C2 同一旧提交版、同一改动，新产品 `457d8cf` | `needs_input`，`committed_content_changed` |
| C3 恢复原字节后新产品 | `committed` |
| D1/D2 复算：把 `r-093049` 的真实四步数据重放到新目录，输入只列原 3 条材料，分别用旧、新产品提交 | 旧产品记录 3 条材料、无 `adopted_materials`、`requirements` 仍是旧值；新产品记录 3 条材料、`adopted_materials` 5 条、`requirements` 同步为结构化要求 |
| D3 同一改动，旧产品复算稿 | `committed`（漏检） |
| D4 同一改动，新产品复算稿 | `needs_input`，`committed_content_changed` |
| D5/D6 恢复原字节后两份复算稿 | 均 `committed` |
| D8 新产品未提交工作版、改 `applicant.md` 后恢复 | `ready`；`materials`、`body`、`md`、`review` 为 `pending`，`question`、`scheme` 仍 `complete`；`checks.content_consistent=false`；材料步骤记录 `materials_changed`，location 为 `applicant.md` 实际路径 |
| D9/D10 恢复原字节后连续两次恢复 | `ready`；`state_version` 11→12 后保持 12，不再递增 |

`applicant.md`（`f9f7e449…`）与 `program-a.md`（`7bd03c03…`）每次都在 `finally` 中恢复原字节并核对摘要；验证前后论文状态文件 SHA-256 相同（`62709518…`）。

**受影响必测项与复用**：

| 项 | 处理 | 结果 |
|---|---|---|
| RP-01 | 本轮换版重装，按原检查项重查 | 通过（`logs/rp01-install-inspection.txt`） |
| RP-11 | 产品恢复与失效路径直接受影响，用新运行包重跑 `test_recovery.RecoveryTests` | 8 个方法 `ok`、`Ran 8 tests in 5.653s`、退出 0（`logs/rp11-components.log`，命令与绑定见 `logs/rp11-command.txt`）；运行前后稿件状态 SHA-256 相同（`4c54f358…`），`current` 仍 `r-20261121T095506-f83d0d9ad1e2` |
| RP-08（论文） | 当前版换为补正后的 `r-135022`；正文与 Markdown 逐字节等于真实会话产出，重新测量栏目与篇幅 | 7 栏、2093 字符、`content_consistent`、只交付 `md`；正文 SHA-256 与 `r-093049` 相同，未新增写作请求 |
| RP-02、RP-03、RP-04、RP-05、RP-06、RP-07、RP-08（非论文）、RP-10、RP-12、RP-13 | 产品差异只涉及状态摘要、恢复失效与材料步骤输入同步；发现、材料读取、研究设计、确认、导入与跨稿路径未改 | 复用 r21 已有通过结果，不重跑 |
| RP-09 | 仍按用户决定延期 | 未执行 |

**正式尝试与失败保留**：RP-11 第一次运行因未导出 `RP_TEST_OUTPUT`，8 个用例在 `setUp` 报“执行前须绑定”，属准备错误；日志另存 `logs/rp11-components-prepfail.log`，未改写为通过，导出后重跑得到上述结果。补正前论文稿快照、旧版目录与所有请求目录均保留，未覆盖。

**实现符合性审核**：专用 `implementation_reviewer` 对 `457d8cf` 做了 IR-45 定向复核，结论为**完整**：IR-45 已闭合，未发现与本项修改相关的剩余实现偏差或回归。完整转述见 [implementation-review.md](implementation-review.md) 的 r22 节。该结论只说明实现符合性，不代表计划关口、第三关或合并批准。

**未完成项与负责人**：`plan/test-plan-review.md` 的第三关记录已在 `bb83bec` 更新为 r22 与产品 `457d8cf`（本行所述时点早于该更新，保留为历史）；RP-11 的基准偏离（IR-39）与 IR-41、IR-42、IR-43 的既有偏离仍待测试计划负责人确认；RP-09 继续延期。

本轮未手改任何 `正文.json`、Markdown 或状态文件；论文稿的保存、导出、核对与提交都由安装后的公开入口完成。以上结果只说明实现符合性与测试执行情况，不构成计划关口、第三关或合并批准。

## r23：讲稿与想定问答交付的组件执行（2026-11-25）

本轮新增 `script`（发表讲稿）与 `qa`（想定问答）两项按需交付，并新增必测项 RP-14。计划依据为 [implementation-plan.md](implementation-plan.md) 的 `rp-plan-r5-interview-2026-11-25`，场景见 [test-plan.md](test-plan.md) 的 RP-14。

**产品版本**：`feat/interview-script-artifacts` 分支，HEAD `f06ac53`（试跑时为 `93a8275`，此后只改文档与讲稿入参检查，见下方“版本沿革”），基线 `786d1402929f25ca91f8cdaa4090e8bd73d6989b`，执行时工作树干净。

**执行方式**：本地执行工程师在仓库外隔离目录运行组件测试，固定依赖 `uv run --no-project --python 3.12 --with PyMuPDF==1.27.2.3 --with lxml==6.1.1 --with python-docx==1.2.0 --with Pillow==12.3.0 python -m unittest -v <套件>`；定稿记录的输出目录为 `/tmp/rp-final10`，各套件的总数与结果见该目录的 `run.log`；该日志用 `-v` 输出，带文档字符串的测试类会把首个用例折叠成 `ok`，因此逐项行数少于实际用例数。

**版本沿革**（同一组用例在不同时点的记录，均保留）：

| 时点 | HEAD | 用例数 | 输出目录 |
|---|---|---|---|
| 首次记录 | `93a8275` | 26 | `/tmp/rp-final7` |
| 入参检查修复后 | `e7e52f5` + 与 `bf00791` 相同的未提交改动 | 27 | `/tmp/rp-final9` |
| 定稿 | `f06ac53` | 27 | `/tmp/rp-final10` |

前两次运行的代码与定稿不同（`93a8275` 无入参检查、`e7e52f5` 的检查不含非对象分支），只作过程记录；现行结论以 `f06ac53` 为准。

| 套件 | 基准 | 用例数 | 结果 |
|---|---|---|---|
| `test_interview` | 用例自建隔离目录 | 27 | 通过 |
| `test_recovery.RecoveryTests` | 只交 Markdown 的已提交稿件（`/tmp/rp-recovery`） | 8 | 通过 |
| `test_recovery.InterviewRecoveryTests` | 加选讲稿的已提交稿件（`/tmp/rp-script-recovery`） | 4 | 通过 |

**RP-14 场景与用例对应**：

| 场景 | 用例 |
|---|---|
| 场景 1 加选并导出提交 | `InterviewDeliveryFlowTests.test_export_produces_script_then_review_and_commit` |
| 场景 2 不达标仍保存后补齐 | `InterviewDraftTests.test_selected_deliverable_must_be_saved`、`InterviewDraftTests.test_second_save_keeps_the_first_deliverable`、`InterviewDeliveryFlowTests.test_unchecked_script_content_blocks_export` |
| 场景 3 想定问答问题 | `InterviewRenderTests.test_question_coverage_and_answer_length` |
| 场景 4 手改导出文件核对失败 | `InterviewDraftTests.test_review_reports_edited_deliverable`、`InterviewRecoveryTests.test_edited_script_breaks_review` |
| 场景 5 旧状态恢复与提交 | `LegacyStateTests` 五项 |
| 场景 6 未加选不要求讲稿 | `InterviewStateTests.test_markdown_only_proposal_skips_interview_step` |

**另做的定向验证**（脚本与产物在仓库外 `/tmp/oldstate`、`/tmp/edge-probe`、`/tmp/delprobe`、`/tmp/addprobe`）：

- 用本修订前代码 `7da08f4` 生成真实旧状态稿件，`resume_revision` 返回 `committed`、`begin_revision` 返回 `ready`、`commit_revision` 返回 `committed`，未提交旧稿 `resume_revision` 返回 `ready`。
- 改动既有步骤的保存件后仍判为 `committed_content_changed`。
- 未加选但保存了有错的讲稿内容时返回 `interview_rate`，且该步骤保持未完成。
- 讲稿步骤无删除入口：首次验证只覆盖了「单独提交 `{"script": null}`」这一种输入。其后发现单独提交 `{"script": {}}` 会用空对象覆盖旧讲稿，提交 `{"qa": 合法, "script": null}` 会静默丢掉讲稿并从保存件消失；这两条已按产品缺陷修复，入口现在拒绝所有 `null` 与非空对象以外的写法，并补了用例 `test_null_or_empty_payload_never_drops_saved_content`。原描述「空对象与 null 都被拒绝」在修复前不成立，保留此处更正。新工作版总是从已提交的当前版本复制，因此会带过去已提交稿里的讲稿。
- 加选 `deliverables` 后正文步骤失效，`next_steps` 出现 `body`，与计划「交付、核对与提交的条件」一致。

**未执行**：Nix 构建（本修订未改 `flake.nix`、`flake.lock`、`nix/`）与真实评估会话。RP-14 的正式业务执行由测试计划负责人按第三关安排，本记录只说明组件测试结果。

**资源清单的过期描述**：上文 RP-01、RP-02 与 r22 的安装检查写「四份参考文件」，那是当时的产品内容。本修订新增 `references/interview.md` 后，安装后的参考文件为五份。这些历史行保留原文，不改写为当时未发生的结果；重新执行 RP-01、RP-02 时应按五份核对，是否需要重跑由测试计划负责人在第三关决定。

**审核状态**：专用 `implementation_reviewer` 对 `94519be`、`25956d0` 两次实现审核的 B-1、B-2 已闭合；计划审核在 r5 轮次对当时的计划候选提出 P-01 至 P-10（审阅时 HEAD `50651c9`），已全部由 r5 的 `Plan conclusion: APPROVED` 闭合；逐项轮次见 `implementation-plan-review.md` 的 r5 一节闭合表（P-05 至 P-08 在第二轮，P-09、P-10 与 P-04a–d 在第三轮）。第三关与合并审核见 `test-plan-review.md` 的 r23 与 `implementation-review.md` 的 r23 合并审核一节。本记录不代表计划关口、第三关或合并批准。

**r23 第三关**：安装后的产品 `ca5ab5e` 已完成 RP-14 六个场景的正式执行，结果见 `test-plan-review.md` 的 r23 一节；结果根 `/private/tmp/research-proposal-r23-run.cSceAb`。本记录只保存组件测试，业务执行记录在测试计划审核文件。

## r24：撞车判断文档的 RP-15 执行（2026-11-26）

本轮新增「撞车判断」文档，必测项 RP-15。计划依据为 `rp-plan-r8-collision-2026-11-26`（SHA256 `18113696…`），测试计划 `rp-tests-r8-collision-2026-11-26`（SHA256 `77faa2b9…`），执行说明 `rp-recipe-r16-collision-2026-11-26`。目标分支 `feat/collision-guidance`，基线 `8032701`；产品改动只有 `SKILL.md`、`references/research-design.md`、`references/interview.md` 三份文档。

**执行方式**：在仓库外 `/tmp/rp-collision-check` 运行只读检查脚本 `check_docs.py`，命令为 `UV_CACHE_DIR=/tmp/rp-collision-check/uv-cache uv run /tmp/rp-collision-check/check_docs.py "$(pwd)"`；同时执行基线 diff。完整输出保存在 `/tmp/rp-collision-check/rp15-run.log`。不安装、不启动产品、不运行组件测试。

| 检查 | 结果 |
|---|---|
| 基线 diff（`skills/research-proposal flake.nix flake.lock nix README.md`） | 3 files changed，74 insertions(+)，1 deletion(-)；仅三份技能文档 |
| 四份文档定向 diff | 同上；`candidate-scoring.md` 无 diff |
| `skills/research-proposal/scripts` 与 `test/` diff | 空 |
| 只读检查脚本 | PASS 113 checks |
| `git diff --check` | PASS |

**覆盖**：新节位于「新颖性写在哪里」与「与教授已有研究的关系」之间；`SKILL.md` 相关研究步骤与 `interview.md` 三类追问末尾两个入口可达；四类撞车、三种结论状态、三步诊断、四种切口、两个以上信号（回选题复查）、面试三句和诊断层边界均在；`candidate-scoring.md`、frontmatter、脚本、依赖、安装文件未变；新增行未出现真实人名、学校、机构、产品名或具体论文示例。

**复用**：RP-01 至 RP-14 的既有结果不受文档增补影响，直接沿用，不因本次提交编号变化重跑。本轮未执行安装、组件测试或实际会话。

**限定**：本记录只说明 RP-15 的检查结果，不构成计划关口、第三关或合并批准；第三关结论见 `test-plan-review.md` 的 r8 一节。

## r25：撞车评分映射与篇数上限修正（2026-11-26）

用户追加要求：评估评分细则是否需要新增维度；去掉“五篇左右”的篇数上限。评估结论是不新增第十个评分项，改为在 `candidate-scoring.md` 增加撞车类型到既有评分项的映射；三步诊断改为“篇数不设上限、不按固定篇数停手”。计划依据为 `rp-plan-r9-collision-scoring-2026-11-26`（SHA256 `d49b9135…`），测试计划 `rp-tests-r9-collision-scoring-2026-11-26`（SHA256 `260ac730…`），执行说明 `rp-recipe-r17-collision-scoring-2026-11-26`。目标分支 `feat/collision-guidance`，基线 `8032701`。

**执行方式**：在仓库外 `/tmp/rp-collision-check` 运行只读检查脚本 `check_docs.py`，同时执行基线 diff。完整输出保存在 `/tmp/rp-collision-check/rp15-run-r9b.log`。不安装、不启动产品、不运行组件测试。

| 检查 | 结果 |
|---|---|
| 基线 diff（`skills/research-proposal flake.nix flake.lock nix README.md`） | 4 files changed，94 insertions(+)，1 deletion(-)：`SKILL.md`、`candidate-scoring.md`、`interview.md`、`research-design.md` |
| `candidate-scoring.md` 定向 diff | 19 insertions(+)，无删除行；只新增「撞车类型怎么落到评分」 |
| `skills/research-proposal/scripts` 与 `test/` diff | 空 |
| 只读检查脚本 | PASS 133 checks |
| `git diff --check` | PASS |

**覆盖**：`candidate-scoring.md` 的九项权重表、两项硬门槛、评分公式和九项 0/1/2 判据未改；新增映射明确“不是第十个评分项”，只说明四类撞车与三种结论状态落到「先行核对」「空白成因」「新意落点」「价值」的哪一项，不固定 1 分、不新增条件；三步诊断不再出现“五篇”，写明“篇数不设上限”“不要按固定篇数停手”；“五篇工作”改为“多篇工作”；新增行未出现真实人名、学校、机构、产品名或具体论文示例。

**复用**：RP-01 至 RP-14 的既有结果不受本次文档修正影响，直接沿用；r24 的 RP-15 结果只覆盖上一版三份文档，本轮的 4 文件结果以本节为准。

**限定**：本记录只说明 RP-15 的检查结果，不构成计划关口、第三关或合并批准；第三关结论见 `test-plan-review.md` 的 r9 一节。

## r26：RP-16 教授方向对齐的三节文档（2026-11-27）

角色：本地执行工程师。执行对象为工作树 `.agents/worktrees/research-proposal-alignment`，分支 `feat/direction-alignment`，基线 `61257df`。执行计划 `rp-plan-r10-direction-alignment-2026-11-27`（SHA256 `37a0c8be…`，`APPROVED`，见 [implementation-plan-review.md](implementation-plan-review.md) 的 r10 一节），测试计划 `rp-tests-r10-direction-alignment-2026-11-27`（SHA256 `31059222…`），执行说明 `rp-recipe-r18-direction-alignment-2026-11-27`。

**范围**：只执行 RP-16。RP-01 至 RP-15 本轮未重跑，按计划沿用既有有效结果；RP-09 继续延期。不安装、不启动产品、不运行组件测试、不调用上游。

**产品版本**：工作树 HEAD `61257df` 加本轮未提交改动。相对基线的 `git diff --numstat 61257df -- skills/` 为：`SKILL.md` 2+/2-、`references/candidate-scoring.md` 4+/1-、`references/interview.md` 7+/0-、`references/research-design.md` 89+/2-，合计 4 files changed、102 insertions(+)、5 deletions(-)。`flake.nix`、`flake.lock`、`nix/`、`README.md`、`test/`、`skills/research-proposal/scripts/` 均无 diff；frontmatter 未改。

**执行命令**：`python3 /tmp/rp-r16-check/check.py . 61257df`（只读脚本，位于仓库外临时目录 `/tmp/rp-r16-check/`，不提交），另加 `git diff --check 61257df`。脚本对四份文档做结构、节序、关键词、锚点与不扩散检查，隐私检查只看新增行。

**结果**：`PASS 66 checks`，`ALL OK`，退出 0；`git diff --check` 无输出。

| 检查组 | 观察点 | 结果 |
|---|---|---|
| A1–A13 缺口 A | 轴节存在；位于「与教授已有研究的关系」之后、「改动先行研究的某一步之前」之前；含算法组/系统组/协同设计组三类与精度/延迟/功耗/吞吐/利用率指标；“稳定报告”有口径；对比表侧指标不算；不硬套三分类；篇名只作分析要求；不用于筛选教授；不替代 `discover` 与本稿问题确认；作为 2/1 判分输入；`candidate-scoring.md` 明写不自行提权重；教授关系末尾有指针 | 通过 |
| B1–B13 缺口 B | 脉络节存在；位于「新颖性写在哪里」与「撞车怎么判断」之间；含上位说法与抽象例子；说明定位错误而非空白大；写明已有多少工作（篇数或量级）与拥挤判断；阅读篇数不设上限、不按固定篇数停手；沿用三篇最低证据；不替代「空白成因」；两节都要过；任一节不过不进方案 | 通过 |
| C1–C14 缺口 C | 「多课题点合并」存在；四种切口仍在；明写切口之外、不是第五种切口；两到三个缺口；缺口须有「研究局限」/「未来工作」出处；单一研究问题；判断办法同时回答；每缺口独立证据；先行核对仍三篇；禁止缺口凑新意；`candidate-scoring.md` 标题已改为「四种常见打错」且条目数为 4；新增第 4 条打错 | 通过 |
| D1–D2 交叉引用 | 旧的“理由见上一节”已消除，改为具名指向「新颖性写在哪里」 | 通过 |
| E1–E5 入口 | `interview.md` 有轴与脉络两个指针；`SKILL.md` 中文方案步骤有轴入口、相关研究步骤有脉络入口并提到多课题点合并 | 通过 |
| F1–F8 不扩散 | 评分表、权重行、硬门槛段、评分公式未改；九项 0/1/2 判据表与「范围连接」2/1/0 判据表逐行与基线相同；三类追问标题未变；`candidate-scoring.md` 本轮只新增两处 | 通过 |
| G1–G2 文件范围 | 依赖/安装/README/test 无 diff；只改四份技能文档 | 通过 |
| H1–H2 隐私 | 新增行无 URL、绝对路径、邮箱、真实学校名 | 通过 |

**直接阅读记录**：四份文档已逐节读过。轴节位置（`research-design.md` 第 217 行起）在三类判据之外写清了适用范围与不替代边界；脉络节（第 69 行起）四项产出与「空白成因」的分工明确；多课题点合并在撞车一节“本节只是诊断层”之后独立成段，未改变“四种切口仍要落到四项之一”的原有计数与措辞；`interview.md` 与 `SKILL.md` 的新增均为指针与入口句，未改写既有答案要求。

**复用**：RP-01 至 RP-15 的既有结果直接沿用。RP-15 的既有通过只属于基线 `61257df` 之前的四份文档，本轮新增内容另由 RP-16 覆盖；RP-15 已确认的性质本轮未回退：三步诊断不设固定篇数、评分映射不固定分数的段落，以及九项 0/1/2 判据表与「范围连接」2/1/0 判据表，均相对基线无增删行（由 F1–F7 的逐行比较与本次 diff 直接确认，未另设 RP-15 的重复检查项）。

**限定**：这是文档层静态检查，不证明安装后的主技能在真实会话中的路由或生成效果；RP-16 的目标只要求文档内容与入口存在。结果适用于当前未提交工作树及基线 `61257df`；文档或提交 SHA 变化后，受影响项须重新核对。`PASS 66 checks` 是结构与关键词检查，不是语义审校，执行者已直接阅读四份文档。本记录只说明 RP-16 结果，不构成第三关或合并批准；第三关结论见 `test-plan-review.md` 的 r10 一节。

**第二关后的范围修正（2026-11-27）**：测试计划审核提出 B-1——RP-16 缺口 B 条目末尾的“只作阅读与说明、不用于筛选教授、不替代 `discover` 与本稿问题确认”在已批准执行计划第 384 行没有依据（该边界只写在 A 节，见计划第 382 行），属清单外新增的验收条件。已按 `Test Engineer Rule.md` 第 1、6 节删除该句，未改产品、未重新定义缺口 B 的其余义务。同时把执行说明段的“四类入口可达”改为逐项列出五个入口，把 `candidate-scoring.md`「范围连接」末尾的轴指针补入白名单，并修正本节两处行号与复用表述。删除后重跑同一只读脚本，结果仍为 `PASS 66 checks`、`ALL OK`；RP-16 的检查点、产品文件与 RP-01 至 RP-15 的复用结论均未受影响，不需要重跑任何必测项。B-1 关闭。本次修正后的测试计划 SHA256 为 `a3dc64dad4d150b27847b4a2513a0be0f48a97c174bc27526c6467ced546965c`（执行时为 `31059222…`；修正只改测试计划文本，产品四份文档未变，故 RP-16 结果对当前文件仍有效，不需要重跑）。

**实现审核后的措辞修正（2026-11-27）**：实现符合性审核结论为「完整」，同时提出三项非阻断观察，作者核对后全部采纳并修正 `references/research-design.md` 的轴节：
- O-01：系统组一行的指标原多列「吞吐」，与计划第 382 行“系统组只报延迟和功耗”、协同设计组报吞吐的分工不符；已删去「吞吐」，系统组改为“延迟、功耗、显存、成本”。
- O-02：原写“不写进技能说明或对外材料”，与同文件既有“用了必须标出处”的引用要求可能冲突；已改为“不写进本技能文档”，并补一句“计划正文和讲稿里引用论文，仍按「与教授已有研究的关系」标出处”。
- O-03：原写“判断「范围连接」该给 2 还是 1”，漏掉 0 档；已改为“2、1 还是 0”，与计划一致。

修正只涉及轴节的三处措辞，未改判据、权重、入口或其他文档。修正后重跑同一只读脚本，结果为 `PASS 66 checks`、`ALL OK`、退出 0，`git diff --check 61257df` 无输出；相对基线的 `skills/` diff 变为 `SKILL.md` 2+/2−、`candidate-scoring.md` 4+/1−、`interview.md` 7+/0−、`research-design.md` 90+/2−（原 89+/2−，O-02 多一行）。RP-16 的检查点相应表述已在脚本内对齐（A7 改为匹配“不写进本技能文档”，A11 改为匹配“2、1 还是 0”），检查项数量仍为 66。RP-01 至 RP-15 不受影响，不需要重跑。

## r27：RP-17 方向判决口径文档（2026-11-27）

角色：本地执行工程师。本段是**首次执行**记录；快审修正后的复验见本节末尾“快审后的修正”。执行对象为仓库同级容器下的 `worktrees/research-proposal-verdict`，分支 `feat/verdict-gate`，基线 `56369ad`。执行计划 `rp-plan-r11-verdict-2026-11-27`（SHA256 `c28fd0bc…a4843b`，`APPROVED`，见 [implementation-plan-review.md](implementation-plan-review.md) 的 r11 一节）。

**范围**：只执行 RP-17。RP-01 至 RP-16 本轮未重跑，按计划沿用既有有效结果；RP-09 继续延期。不安装、不启动产品、不运行组件测试、不调用上游。

**产品版本**：分支 `feat/verdict-gate`，基线 `56369ad`。首次执行时为工作树未提交改动；快审修正后已提交，提交内容与复核用的工作树一致（提交见 PR #8）。相对基线的 `git diff --numstat 56369ad -- skills/` 为：`SKILL.md` 1+/1-、`references/candidate-scoring.md` 54+/6-、`references/research-design.md` 20+/0-，3 files changed、75 insertions(+)、7 deletion(-)。

**执行命令**：`python3 /tmp/rp-r17-check/check.py . 56369ad`（只读脚本，位于仓库外临时目录 `/tmp/rp-r17-check/`，不提交），另加 `git diff --check 56369ad`。脚本对三份文档做结构、节序、关键词、锚点与不扩散检查，隐私检查只看新增行。

**结果**：首次 `PASS 75 checks`，`ALL OK`，退出 0；快审修正后重跑 `PASS 79 checks`，`ALL OK`，退出 0。两次 `git diff --check 56369ad` 均无输出。

| 检查组 | 观察点 | 结果 |
|---|---|---|
| A1–A17（修正后拆分 A9a–A9e，共 79 项）判决与停因 | 新节存在且位于「先过门槛，再算总分」与「打分前先定证据」之间；五种判决词与五个 `gate` 值齐全；三个 `stop_reason` 齐全；五个诊断问句齐全；禁止清单七项齐全；“分数也不能把 1 分判成停”存在；价值项自检存在；负结果判定句存在；`pending` 两个触发条件与“不得改写为停”存在；报告口径按五态改写；`items` 含 `stop_reason` 与 `merged_into`；软门槛旧词“降为备选”已无残留；两处新链接指向正确 | 通过 |
| B1–B6 证据推翻方案之后 | 新节存在且位于「有限补查」与「新颖性写在哪里」之间；五类分流齐全；“预注册判据是实验纪律，不是选题门槛”存在；三条证据要求齐全；回链指向「判决与停因」 | 通过 |
| C1–C3 入口 | `SKILL.md` 相关研究步骤末尾有「判决与停因」「证据推翻方案之后」两个入口，并写明判停只允许三类理由 | 通过 |
| D1–D11 不扩散 | 权重表、评分公式、0/1/2 判据表、两条硬门槛原文、四类撞车表、三种结论状态表、四种切口标题、新颖性四位置表逐行与基线相同；`interview.md`、`scripts/`、`test/`、`flake.nix`、`flake.lock`、`nix/`、`README.md` 无 diff；相对基线只改三份技能文档 | 通过 |
| E1–E3 交叉引用 | 「学术脉络怎么定位」的“上一节”仍指「新颖性写在哪里」；“见下面的「准备到哪一步算够」”顺序不变；“逐项判据见下”仍指紧随其后的「空白成因 1 分」 | 通过 |
| F1–F2 锚点 | 两个新增锚点可解析；相对基线没有新增无法解析的锚点 | 通过 |
| G1 隐私 | 新增行无 URL、绝对路径、邮箱、真实人名、学校名与用户材料片段 | 通过 |
| H1 diff 干净 | `git diff --check` 无输出 | 通过 |

**直接阅读记录**：三份文档已逐段读过。判决表把五种判决词与 `gate` 放在同一张表里，总分处理逐行写清；停因三类中 `problem_invalid` 单列，五问与“只写 `stop_reason`、分数照实记”连在一起没有分叉；`pending` 的两个触发条件与「推荐怎么写」的旧路径做了取代说明，旧句也改成指向新节；价值项自检给出 0 分同义句清单；负结果模板落在「解释」位置并回链到新节；`research-design.md` 的五类分流每行都有“允许的动作”和“不能做的事”，三条证据要求各自带一条例子；`SKILL.md` 新增句只加两个入口与停因闭集，不改步骤结构。

**复用**：RP-01 至 RP-16 的既有结果直接沿用。RP-16 的既有通过只属于基线 `61257df` 之前的三份文档，本轮新增内容另由 RP-17 覆盖；RP-16 已确认的性质本轮未回退：九项权重、两项硬门槛、评分公式、九项 0/1/2 判据表、四类撞车、三种结论状态、四种切口与多课题点合并段落，均相对基线无增删行（由 D1–D9 的逐行比较直接确认，未另设重复检查项）。

**范围外发现（不修）**：`research-design.md` 有一条相对基线就存在的失效锚点：`[候选选题评分](candidate-scoring.md#可加的一项范围连接)`，目标标题实为「可加的一项：范围连接」，链接一直解析不到。它不属于 RP-17 的目标，本轮不改；F2 按“相对基线不新增坏锚点”判断，未把这条既有失效计为回归。

**限定**：这是文档层静态检查，不证明安装后的主技能在真实会话中的路由或生成效果；RP-17 的目标只要求文档内容与入口存在。结果适用于当前未提交工作树及基线 `56369ad`；文档或提交 SHA 变化后，受影响项须重新核对。`PASS 75 checks` 是结构与关键词检查，不是语义审校，执行者已直接阅读三份文档。本记录只说明 RP-17 结果，不构成第三关或合并批准；本轮为文档静态检查，第三关与合并审核由独立快审一并核对。

**快审后的修正（2026-11-27）**：独立快审提出一项已证实缺陷与一项证据缺口，均已处理。

- **B1**：价值项自检把评分表的两个 1 分说法（“只填补空白”“只有研究者自己关心”）写进了 0 分清单。已改为只列 0 分定义的同义句（“答案是常识”“答案不改变谁的做法”“没人会因此改变判断或做法”“只避免傻事”），并写明“填补空白”“只有研究者自己关心”仍记 1，另补一句“价值项占 15 分，1 分和 0 分不能混”。评分表本身未改。
- **B2**：RP-17 原先只检查“价值项自检”这个词存在，没有核对自检与 0 分定义的对应。检查脚本的 A9 拆成 A9a–A9e：自检存在、0 分同义句齐全、0 分清单不混入 1 分说法、1 分说法明确保留、推荐旧路径已被取代。重跑为 `PASS 79 checks`。
- 非阻塞项一并处理：「推荐怎么写」旧路径句补“本条取代这条旧路”；测试计划的交叉引用行号标注为基线行号。
- 数值判断：新增的“判停禁止清单”列了 0.05、0.02、两个百分点、0.93 四个阈值，它们是效果量线的通用例子，不带出处、对象或结论，不构成用户材料片段，保留。G1 只按 7 个字符串做新增行筛查，不是完整隐私扫描；数值是否属于用户材料片段由本条人工判断。
- 修正后技能 diff 相对基线仍为 `SKILL.md` 1+/1−、`candidate-scoring.md` 54+/6−、`research-design.md` 20+/0−，与首次执行一致。修正只改自检句、旧路径句、脚本与记录，未改停因、`gate` 枚举、字段名与改动范围。

## r28：RP-18 判决记录与保存校验（2026-11-28）

角色：本地执行工程师。执行对象为仓库同级容器下的 `worktrees/research-proposal-record`，分支 `feat/verdict-record`，基线 `97c1340`。执行计划 `rp-plan-r12-verdict-record-2026-11-28`（`APPROVED`，见 [implementation-plan-review.md](implementation-plan-review.md) 的 r12 一节）；测试计划 `rp-tests-r12-verdict-record-2026-11-28`（`APPROVED`，见 [test-plan-review.md](test-plan-review.md) 的 rp-tests-r12 一节）。

**范围**：只执行 RP-18。RP-01 至 RP-17 本轮未重跑，按计划沿用既有有效结果；RP-09 继续延期。不安装产品到消费者、不启动评估会话、不调用上游。

**产品版本**：分支 `feat/verdict-record` 工作树未提交改动，基线 `97c1340`。相对基线的 `git diff --numstat 97c1340 -- skills/` 见本节末“实现符合性审核后的修正”，首次执行时为 4 files changed、252 insertions(+)、21 deletions(-)；新增 `test/test_verdict_record.py`（首个版本 21 用例、最终 30 用例）。

**执行环境**：结果根在仓库外的一次性临时目录（按 `PROJECT_CONSENSUS.md` 不入库不推送，本文只记相对布局与变量名，不写本机绝对路径）。运行包由当前工作树构建：

```bash
: "${RP_WORKTREE:?绑定到本轮工作树根目录}"
export RP_R18_RUN="$(mktemp -d "${TMPDIR:-/tmp}/rp-r18-run.XXXXXX")"
export RP_R18_RUNTIME="$RP_R18_RUN/runtime"
nix build .#research-proposal-runtime --out-link "$RP_R18_RUNTIME"
```

构建退出 0（`warning: Git tree ... is dirty` 属未提交工作树的正常提示）。`--out-link` 指向仓库外目录，工作树未留下 `result` 链接（`git status` 无新增未跟踪文件）。

**导入来源确认**（RP-18 执行步骤第 2 段）：

```bash
"$RP_R18_RUNTIME/bin/python3" -c \
  'import research_proposal._state as s; print(s.__file__); assert hasattr(s, "_check_candidate_scores")'
```

输出路径位于构建输出由 Nix 提供的 `site-packages` 内（形如 `<runtime>/lib/python3.14/site-packages/research_proposal/_state.py`），断言通过。另用 `diff` 比对运行包内 `_candidate_scores_problems` 至 `_check_interview_payload` 区间与工作树源码，**逐行相同**：被测模块确为本次实现，不是工作树源码或旧运行包。未设置 `PYTHONPATH`。

**组件执行**：

```bash
cd "$RP_WORKTREE/test"
RP_TEST_OUTPUT="$RP_R18_RUN/component-output" \
  "$RP_R18_RUNTIME/bin/python3" -m unittest -v test_verdict_record \
  > "$RP_R18_RUN/rp18-components.log" 2>&1
```

退出 0，`Ran 21 tests`、`OK`。日志：`$RP_R18_RUN/rp18-components.log`。

**文档执行**：仓库外临时目录的只读检查脚本（仓库外只读脚本，不提交），`PASS 79 checks`、`ALL OK`、退出 0。`pandoc -f markdown -t html` 对改动文件通过；`git diff --check 97c1340` 无输出。

| 检查组 | 观察点 | 结果 |
|---|---|---|
| A1–A3 新节与位置 | 「判决记录怎么写」存在，位于「判决与停因」之后、「打分前先定证据」之前 | 通过 |
| B1–B7 字段清单 | 四项字段齐全；`experiment`、`missing` 为数组，`evidence` 为与 `scores` 同键对象；三字段不可省；`hard_stop` 的 `evidence`、`pending` 的 `missing`、`pass` 与 `soft_stop` 的 `evidence` 非空 | 通过 |
| C1–C6 题面版本 | `id` 跨版本不变、`(id, statement_version)` 唯一、`merged_into` 指向身份；旧记录留档；转述带版本；汇总只能由当前版本记录生成 | 通过 |
| D1–D8 未评 | `scores` 写 `null` 并在 `evidence` 写明缺什么；不进总分、注明“按 N 项计”；硬门槛项未评不得 `pass`/`soft_stop`；含与不含未评不同表比较；不是第三道硬门槛；0 分只留给有依据的否定；「怎么算总分」已补分母规则 | 通过 |
| E 待补范围 | 六类触发情形齐全（近邻不足三篇、领先项只有摘要、关键数据缺失、实现有错、反例待核、口径未定）；承重证据按研究问题确定；第 2 句不再是唯一入口；`pending` 不得改写为「停」 | 通过 |
| F1–F9 `problem_invalid` | 锁定同一目标量、假设与观测资料；五问五个独立分支齐全；第 4 问与第 1 问分界写明；「依赖不可观测分布」收窄；轴匹配、算力、指标更换另行处理；判停写明 `statement_version` | 通过 |
| G1–G3 保存与拒绝路径 | 「保存」节含新字段与校验说明；「被拒绝时怎么办」四条齐全（不写入、状态版本不变、上一份记录原样保留、可按 `gate` 补齐、可先不带 `candidate_scores`、不自动迁移） | 通过 |

> **时点说明**：本节表格是本轮执行时的快照。该轮之后「被拒绝时怎么办」已扩为**五条**（第 5 条为同一题面版本被记了两条时的处理），「先不带」的补救也已扩为“先不带相应对象（`candidate_scores` 与／或 `verdicts`）”。本节表格内的“四条”“可先不带 `candidate_scores`”不再代表当前文档，当前规则以 `candidate-scoring.md` 与 `plan/test-results.md` 末尾「RP-18 第三轮复验」之后各节为准。

| H1–H5 入口 | `runtime.md` 写拒绝后状态并指向新节；`SKILL.md` 含新节入口、未评规则与汇总来源 | 通过 |
| I1–I8 不扩散 | 权重表、评分公式、五态判决词表逐行与基线相同；硬门槛仍为两条，新意落点评分行与基线的“新意落点行”相同，空白成因的评分行与硬门槛行按 IR-01 收窄为“已证伪”两种情形；空白成因 1 分判据行与基线相同（首次执行时整张硬门槛表还与基线相同，见本节末修正）；`research-design.md`、`interview.md`、`flake.nix`、`flake.lock`、`nix/`、`README.md` 无 diff | 通过 |
| J1–J2 锚点 | 本文件内全部锚点可解析；新锚点存在 | 通过 |
| K1–K3 交叉引用 | 「怎么报给用户」「推荐怎么写」「判决与停因」三处指向新节且措辞成立 | 通过 |
| L1 隐私 | 新增行与新增测试文件无 URL、绝对路径、邮箱、真实人名、学校名或用户材料片段；测试输入为合成项目名 | 通过 |

**组件观察点与实际用例**：

| 观察点 | 用例 | 结果 |
|---|---|---|
| 合规记录放行并原样落盘 | `test_compliant_record_is_saved` | 通过 |
| `pending` 带总分被拒 | `test_pending_with_total_is_rejected` | 通过 |
| `hard_stop` 缺 `stop_reason` 被拒 | `test_hard_stop_without_reason_is_rejected` | 通过 |
| `stop_reason` 取值非法被拒 | `test_hard_stop_with_unknown_reason_is_rejected` | 通过 |
| `merge` 缺 `merged_into` 被拒 | `test_merge_without_target_is_rejected` | 通过 |
| `merged_into` 指向不存在的候选被拒 | `test_merge_target_must_exist` | 通过 |
| `merged_into` 按候选身份跨版本成立 | `test_merge_target_uses_candidate_identity` | 通过 |
| `pass` 须带数值总分 | `test_pass_needs_numeric_total` | 通过 |
| `pending` 须有 `missing` | `test_pending_needs_missing` | 通过 |
| `pass` 须有 `evidence` | `test_pass_needs_evidence` | 通过 |
| 未评项须写 `evidence`、可与其他项共存 | `test_unrated_item_needs_evidence` | 通过 |
| 硬门槛项未评不得 `pass`/`soft_stop`，`pending` 放行 | `test_hard_gate_unrated_cannot_pass` | 通过 |
| `scores` 键集合须等于 `weights` | `test_scores_must_match_weights` | 通过 |
| 三样内容字段不可省 | `test_record_fields_are_required` | 通过 |
| 一次列出全部问题 | `test_all_problems_are_reported_at_once` | 通过 |
| 拒绝后状态版本不变 | `test_rejected_save_keeps_previous_state_version` | 通过 |
| 拒绝后上一份材料记录逐字节不变、新内容未写入 | `test_rejected_save_leaves_previous_materials_record_untouched` | 通过 |
| 同一候选可保留不同题面版本 | `test_same_candidate_may_keep_other_statement_version` | 通过 |
| 同一候选同一版本重复被拒 | `test_same_candidate_same_version_is_rejected` | 通过 |
| 不带 `candidate_scores` 的材料保存不变 | `test_materials_without_scores_still_save` | 通过 |
| 不带对象的材料保存按原行为 | `test_materials_without_object_saves_as_before`（原 `test_other_stages_are_not_affected`，IR-05 改名） | 通过 |
| 其他阶段不受影响 | 由 `test_interview` 27 项回归覆盖，不在本模块内重复 | 通过 |

**回归**：`test_interview`（27 用例）用同一运行包执行，退出 0、`OK`。日志 `$RP_R18_RUN/regress-interview.log`。该回归只覆盖与 `save_revision` 共用的入参拒绝路径，不重开 RP-14 的既有结论。

**执行中的自我修正（保留原始记录）**：

1. 首次组件执行用 `PYTHONPATH` 指向工作树源码，导入来源实为未打包的源码，跑出的 15 项通过不能证明运行包行为。计划审核 B-06 指出该问题后，改为从运行包自带 `site-packages` 导入，并加导入来源断言与源码逐行比对；此后 20 项、21 项通过均为运行包结果。首次 15 项结果不作为本项证据。
2. 首次构建运行包发生在 `_check_candidate_scores` 写入之前，该运行包内确无该函数（已实测 `grep -c` 为 0）。后续两次重建都在改码之后，正式结果使用最后一次构建。
3. 文档检查脚本首轮 4 项失败均为脚本断言本身写错：`C6` 把三级标题当作二级标题查、`D6` 与 `I6` 的期望字符串与文档实际措辞不符、`F6` 依赖的切片被 `##` 边界提前截断。逐条核实后修正脚本，并补写了文档中缺失的「五个独立分支」一句与第 4 问与第 1 问的分界说明；修正后 `PASS 79 checks`。脚本问题不计为产品失败，但文档缺句属真实遗漏，已补。

**未执行**：RP-01 至 RP-17（按计划沿用既有结果）、产品正式安装到消费者（本轮不改安装、依赖与交付格式）、真实评估会话、Word 与页图相关检查。

**限定**：RP-18 的组件部分是组件级入参校验与拒绝后不落盘，文档部分是静态结构与措辞检查；两者都不证明主技能在真实会话中会按新节写记录，也不证明模型会主动补齐旧记录。这类效果留待实际使用观察。

**审核状态**：本记录只说明 RP-18 结果，不构成第三关或合并批准。执行计划与测试计划均已 `APPROVED`；实现符合性审核与合并审核另行安排。

**实现符合性审核后的修正（2026-11-28）**：专用 `implementation_reviewer` 首次审核结论为**部分完成**，提出 IR-01 至 IR-07。逐条处理如下，原结论与问题保留。

- **IR-01（阻断，要求二未一致落实）**：`candidate-scoring.md` 就“空白成因 0”存在两套记法——评分表 0 分列与第 62 行把“还没查够三篇”记 0 并标待补，新节却要求证据未齐记「未评」。经需求裁定人按用户原话“证据未齐记未评、0 留给有依据的否定”确认：**0 分收窄为“已证伪”，一种来源、两种情形**（伪空白；查证后确认没有相近工作），“还没查够三篇”改记「未评」并按 `pending` 处理。评分表 0 分列、第 62 行、硬门槛表、门槛解释句、`gap_zero` 定义与 `pending` 情形清单六处同步改口，“伪空白”全文只保留一套定义。这是本轮唯一一处语义修订，已在执行计划中单列并注明它收窄了原先“九项 0/1/2 判据不变”的范围。
- **IR-02（校验比计划清单更严）**：保留而非收窄。依据是 `Implementation Reviewer` 未反对的三条都与 `candidate-scoring.md` 既有规则一致（每项 0、1、2 分；权重不为负；按 `gate` 写 `stop_reason` 或 `merged_into`），拒绝的是文档本来就禁止的写法。已在执行计划补「校验边界」一句：校验可覆盖既有规则，超出既有规则的新增拒绝项须另行批准。
- **IR-03（畸形输入抛 `TypeError`）**：`_candidate_scores_problems` 改为先判 `id` 与 `statement_version` 类型、再构造唯一键，畸形输入按 `ValueError` 报问题。新增 `test_malformed_id_types_raise_value_error`。
- **IR-04（必测观察点缺结果）**：补 9 个用例覆盖形状与类型（`candidate_scores` 非对象、`weights`／`evidence_cutoff` 缺失、权重为空或非数字、`items` 为空或非数组、`gate` 非法值、非停判决带停因字段、`merged_into` 指向自己、分数取值越界、`experiment`／`missing` 非数组、`evidence` 非对象）、畸形 `id` 与题面版本、合规 `soft_stop` 放行。用例数由 21 增至 30，重跑 `Ran 30 tests`、`OK`。
- **IR-05（用例名与断言不符）**：`test_other_stages_are_not_affected` 实际只保存材料步骤，改名为 `test_materials_without_object_saves_as_before` 并在 docstring 写明其他阶段由 `test_interview` 回归覆盖；r28 与测试计划的归属同步改正。
- **IR-06（检查脚本两项空过）**：`check.py` 的 I1 检索串原先在基线与当前文件都匹配 0 行（恒真），L1 的 URL 正则把 `^` 写在中间（永不匹配）。已改为真实存在的行 `| 问题成形 | 15 |` 与 `https?://`，并新增 I4a–I4f 六项核对 0 分收窄与“伪空白”单一定义。重跑 `PASS 84 checks`、`ALL OK`、退出 0。
- **IR-07（记录状态与行号）**：`test-plan-review.md` 的旧“当前状态”行改为历史并新增 r12 状态行；`implementation-plan-review.md` 的行号引用改为“`_state.py:995` 校验、996 加锁、1035 首次 `write_record`、1063 与 1073 `_persist_work`、`_store_state` 第 123 行递增版本”。

**修正后的正式结果**（用最后两次重建的运行包执行）：

| 项 | 命令 | 结果 |
|---|---|---|
| RP-18 组件 | `RP_TEST_OUTPUT=... "$RP_R18_RUNTIME/bin/python3" -m unittest -v test_verdict_record` | `Ran 30 tests`、`OK`、退出 0 |
| 回归 | 同上，`test_interview` | `Ran 27 tests`、`OK`、退出 0 |
| RP-18 文档 | 仓库外临时目录的只读检查脚本 | `PASS 84 checks`、`ALL OK`、退出 0 |
| diff 卫生 | `git diff --check 97c1340` | 无输出 |

最终产品差异（`git diff --numstat 97c1340 -- skills/ test/`，以提交前最后一次 `git diff --cached` 为准）：`SKILL.md` 1+/1−、`references/candidate-scoring.md` 114+/26−、`references/runtime.md` 1+/1−、`scripts/research_proposal/_state.py` 151+/0−、`test/test_verdict_record.py` 362+/0−。

**保留的观察（不阻断）**：组件校验在加锁之前执行，因此过期的 `expected_state_version` 或已提交修订若同时带不合规 `candidate_scores`，会先得到 `ValueError` 而不是 `conflict`/`blocked`。计划未要求两种响应优先，本轮不改；将来若有调用方依赖原顺序需另行决定。

**第二轮定向复核后的修正（2026-11-28）**：`implementation_reviewer` 定向复核结论仍为**部分完成**，指出 IR-01 在第 58 行残留直接矛盾，另有 IR-02、IR-05、IR-07 三处未闭合。逐条处理：

- **IR-01 残留**：第 58 行「空白成因的硬要求」原写“缺这三项也按 0 分”，与第 62 行“还没查够三篇记「未评」”直接冲突，正是本轮要消除的失败模式。改为“还没查够三篇不按 0 分记，记「未评」并按 `pending` 处理；只有查过之后仍凑不出这三项、且确认没有相近工作，才按 0 分”。第 70 行与第 185 行两处“0/1/2 判据不变”补括注，写明空白成因 0 分的适用情形已按 r12 收窄。计划第 439 行补记第 58 行同属该口径改写，避免下次漏查。
- **IR-02 边界清单缺一项**：`id` 与 `statement_version` 须为非空字符串这一要求原先既不在文档、也不在计划边界清单。已在 `candidate-scoring.md` 的题面版本段写明“`id` 与 `statement_version` 都写非空字符串（例如 `C1` 与 `q1`）”，并在计划「校验边界」清单补上该项。
- **IR-05 未闭合**：r28 观察点表仍把“其他步骤不受影响”归给已改名的用例。已改为两行：一行归 `test_materials_without_object_saves_as_before`（注明原名），一行写明其他阶段由 `test_interview` 27 项回归覆盖。
- **IR-07 行号**：`implementation-plan-review.md` 的行号引用按当前代码更新为第 1003 行校验、1004 加锁、738–757 类型判定与唯一键、1035 首次 `write_record`、1063 与 1073 `_persist_work`、`_store_state` 第 109 行递增。
- **测试计划第 236 行**：「不扩散」改为“新意落点判据行与基线相同，空白成因 1 分判据行与基线相同、0 分判据按 IR-01 收窄”，与同一文件第 232 行口径一致。
- **检查脚本**：新增 I4g 至 I4j 与 I4h2，覆盖第 58 行改写、两处括注、`id` 与题面版本类型要求。自查时发现自己写了一条带 `or True` 的恒真断言（与 IR-06 同类问题），已删除并改为两条实质断言。

**最终结果**（产品代码未变，故不重跑 27 项回归；运行包为最后一次构建）：

| 项 | 结果 |
|---|---|
| RP-18 组件 `test_verdict_record` | `Ran 30 tests`、`OK`、退出 0 |
| RP-18 文档 仓库外临时目录的只读检查脚本 | `PASS 89 checks`、`ALL OK`、退出 0 |
| 上一轮回归 `test_interview` | `Ran 27 tests`、`OK`、退出 0（产品代码未再变动，结果继续有效） |
| `git diff --check 97c1340` | 无输出 |

**第三轮审核触发修订后的记录（2026-11-28）**：实现符合性审核第三轮指出记录层四处未对齐，逐条处理如下。

- **I1–I8 行自相矛盾（R-05 同类）**：原写“两条硬门槛表……逐行与基线相同”，与同句“0 分判据已收窄”相反——`candidate-scoring.md` 的「空白成因 = 0」一行确已从“伪空白、换基底或指标但答不出新回答，或还没查够三篇”改为“已证伪：伪空白……或查证后确认没有相近工作”。已改为“硬门槛仍为两条，新意落点行与基线相同，空白成因的评分行与硬门槛行按 IR-01 收窄”。
- **计数过期**：按当前 `git diff --cached --numstat 97c1340` 更新为 `candidate-scoring.md` 114+/26−、`test_verdict_record.py` 362+/0−（上一轮记的是 112+/24− 与 361+/0−）。
- **测试文件最后改动晚于被引用的日志**：`test/test_verdict_record.py` 与 `candidate-scoring.md` 的最后修改时间为 06:03:20，而此前引用的组件日志为 05:53、文档检查为 05:52。为让记录对应实际版本，已在 06:13 重跑并保留日志：
  - `$RP_R18_RUN/rp18-components.log`（06:13:32）：`Ran 30 tests`、`OK`、退出 0；
  - `$RP_R18_RUN/regress-interview.log`（06:13:34）：`Ran 27 tests`、`OK`、退出 0；
  - `仓库外临时目录的 `check.log``（06:13:44）：`PASS 89 checks`、`ALL OK`、退出 0。
  产品代码自 IR-03 修正后未再变动，运行包无需重建；运行包内 `_state.py` 与工作树源码同哈希的前提在前一轮已核对。
- **本轮改动内容**：`test_malformed_id_types_raise_value_error` 的 `bad` 列表补空字符串与纯空白两种输入（用例数仍 30）；`candidate-scoring.md`「旧记录怎么继续保存」第 1 条补“`id`、`statement_version` 要写成字符串；旧记录把编号写成数字时改成同名文本，不要改编号本身”；两份计划与审核记录按 `plan_reviewer` 的定性写入审批记录（执行计划第 457 行新增项重新批准，测试计划 R-05 修正后复核 `APPROVED`）。
- **检查脚本标签**：`check.py` 的 I3 名称由“两条硬门槛表”改为“新意落点硬门槛行”，与实际只检索新意落点一行相符；空白成因行的收窄由 I4a–I4j 覆盖。名称修正只改检查标签、不改检索串与项数，89 项结果沿用 06:13 的运行；修正后又重跑一次覆盖了日志。

**最终状态**：RP-18 文档检查 89 项全通过、组件 30 项通过、回归 27 项通过，三者日志时间均晚于最后一次文件改动。

**PR #9 快审后的修正与复验（2026-11-28）**：独立快审按 `quick-merge-review` 结论 `NOT_READY`，提出 B1–B4。B1–B3 为已证实缺陷，逐条处理：

- **B1（实现缺陷）**：硬门槛项记「未评」时，校验只在 `gate in ("pass", "soft_stop")` 时报错，`hard_stop` 与 `merge` 分支不检查，因此“空白成因未评 + `hard_stop` + `gap_zero`”可通过，“门槛没查就判停”仍可入库。已改为存在硬门槛项未评时 `gate` 只能为 `pending`；`test_hard_gate_unrated_cannot_pass` 增补 `hard_stop` 与 `merge` 两条负向断言（用例数仍 30）。
- **B2（文档缺陷）**：「先行核对」0 分列原写“还没核对，或差别没有依据”，与「未评」规则冲突。已改为“核对过，但差别没有依据（还没核对不算 0 分，记「未评」）”，软门槛补法与该行解释句同步。
- **B3（文档缺陷）**：`SKILL.md` 判停句原写“空白成因 = 0 且已判伪空白”，比新定义窄。已改为“已证伪”，并写明两种情形与“还没查够三篇记「未评」，不算 0”。
- **B4（记录缺失）**：r12 最终结论未落在 `plan/implementation-review.md`，已补 r12 一节，含五轮审核过程与快审四项。

**复验**（重建运行包后执行）：
- `test_verdict_record`：`Ran 30 tests`、`OK`、退出 0。
- 文档检查：`PASS 94 checks`、`ALL OK`、退出 0（新增 I4k–I4o 覆盖硬门槛未评只能 `pending`、先行核对未评不记 0、`SKILL.md` 判停句）。
- `test_interview`：27 项回归，产品代码新增判定只作用于 `materials` 的可选对象。

快审同时确认无问题的部分（校验顺序、不误伤既有调用、空白成因单一外延、范围无越界、计划哈希与批准一致）继续有效，不重复证明。

**快审第二轮（B5、B6）修正与复验**：B5 为文档缺陷——「先行核对」的软门槛补法写成“整条按 `pending`”，与同文件的「同表比较」段和已批准计划冲突，会把软门槛未评变成第三道硬门槛。已删去该半句，改为“按未评记法处理，含未评时不与其他候选同表比较”。B6 为 B1 的配套文档未同步：代码对四值全拒，文档两处仍只写拒 `pass` 与 `soft_stop`，已改为“只能记 `pending`，四值都会被拒绝”，`runtime.md` 的“等”改为显式写“`pending` 以外的任何 `gate`”。

文档检查脚本 I4k 原先带 `or` 兜底、因而漏检 B6；已删除兜底并把 D4 更新为四值断言，新增 I4k2、I4k3。

复验：`test_verdict_record` 30 项、`test_interview` 27 项、文档检查 `PASS 96 checks` 全部通过。

**快审第二轮（用户四条件）修正与复验（2026-11-28）**：用户复核 PR #9 判 `NOT_READY`，提出四条。四条均经本地复现确认，逐条处理：

- **第 1 条（保存放行缺依据或缺待办的记录）**：实测五种写法原先都能保存成功——`pass` 的 `evidence` 与 `scores` 完全不对应、`evidence` 缺一项、`pending` 的 `missing: [null]`、`evidence_cutoff` 为空串、从权重/分数/依据同时删掉一道硬门槛仍记 `pass`。已补齐结构校验：`evidence_cutoff` 须非空字符串；`experiment`、`missing` 每项须非空字符串；`scores` 键集合须等于 `weights`（少评要写 `null`，不能删键）且必含两道硬门槛；`evidence` 须对 `scores` 每一项都有非空依据；权重不得为负。五种写法现已全部被拒。
- **第 2 条（一次报错漏掉可独立判断的问题）**：原实现遇到非法 `gate` 直接 `return`。已把字段自身问题（类型、取值、键集合、依据齐全）与 `gate` 对齐要求分开收集：非法 `gate` 时先报出所有独立字段错误，再报 `gate` 本身并说明后续检查无法进行。实测 `gate: "keep"` + `experiment: "文字"` + `missing: {}` 现能在一次报错里列出三条问题。
- **第 3 条（汇总与计分互相冲突）**：「汇总从记录生成」原先只允许五个字段却又要求报停因、并入目标和旧题面编号；报表第 3 条仍按默认权重直接相加，与未评分母规则冲突（权重 5 的一项未评时两处分别得 100 与 95）。已改为允许并直接读取记录里的全部判决字段，报表引用「怎么算总分」的同一规则，示例表补“九项都评过才能直接相加”。
- **第 4 条（公开差异含用户数值与本机路径）**：产品文档的示例改用合成数值（0.72、0.85、0.88、判据线 0.90）；计划同一示例替换并注明“合成数值，非用户记录”；测试步骤改为 `: "${RP_WORKTREE:?...}"` 由调用方绑定、临时目录用 `${TMPDIR:-/tmp}`；本记录也不再写本机绝对路径。新增检查 L2 对全部新增行扫描用户数值与本机路径。

**已推送历史的处理**：提交 `1fe8722` 等已含上述数值与路径。经查该分支 0 条评论、0 条 review、无他人引用、仅本人三个提交且尚未合并，按合并前重写分支历史的处理方式修正，不改写 `main`。

**复验**（重建运行包后）：
- `test_verdict_record`：`Ran 38 tests`、`OK`、退出 0（新增 8 个用例覆盖第 1、2 条）。
- `test_interview`：`Ran 27 tests`、`OK`、退出 0。
- 文档检查：`PASS 105 checks`、`ALL OK`、退出 0（新增 I4p–I4w 覆盖第 3 条的汇总字段与计分口径、L2 覆盖第 4 条、I4v 与 I4w 检索计划与测试计划里的窄枚举，防同类遗漏再发生）。
计划审核随后指出 M-01、M-02（计划第 436 行与测试计划第 231 行仍留五字段窄枚举），已修并复核 `APPROVED`；检查项数与结果在上表中已按修正后重跑。

## RP-18 第三轮复验：用户复核第二轮（三条）修正后的正式执行（2026-11-28）

> **结果指针（历史）**：本节是 RP-18 **第三轮**的结果（69 项／`PASS 169 checks`），**已被后续轮次取代**；当前最终结果是本文件最后一节「RP-18 第四轮复验」（78 项／`PASS 217 checks`）。测试计划 RP-18 步骤 4 写的是“记入 `plan/test-results.md` 的 r28 一节”，而 r28 记录的是更早轮次的 30 项；按实现符合性审核 R-1 的建议，此处就地说明各节关系，不改动已批准的测试计划文本（改动测试计划会使其获批版本失效，而该指针分歧不涉及任何观察点或步骤变化）。


用户对 PR head `15bb375` 再次判 `NOT_READY`，提出三条业务问题。修正后执行计划获 `APPROVED`（`implementation-plan-review.md` 最后一节），测试计划获 `APPROVED`（`test-plan-review.md` 的「rp-tests-r12：用户复核第二轮（三条）后的观察点修订与复核」）。

**角色与版本**
- 角色：本地执行工程师。工作树 `worktrees/research-proposal-record`，分支 `feat/verdict-record`，基线 `97c1340`，执行时 HEAD `15bb375`（本轮改动未提交）。
- 执行计划 `rp-plan-r12-verdict-record-2026-11-28`，SHA256 `3a3a99563099fcc77d00e420c243ce032a37188191c83e5401b95bd839df1d6a`（`APPROVED`）。
- 测试计划 `rp-tests-r12-verdict-record-2026-11-28`，SHA256 `c81d68b39258cf12d7b803b858a684dcd13d7ff7ac4c392472d1d802c9e15028`（`APPROVED`）。
- 产品源码 `_state.py` SHA256 `3f735b0eedeb78cabe2bbf7fe04367657d115d88d8b18e3de0db4a5d28dcf5f8`；测试文件 `test/test_verdict_record.py` SHA256 `04aa83e6ad21a3700bbfebe6e81e0bdef55cde293e147320f5501e08895923a0`。

**执行环境（按测试计划 RP-18 步骤 0）**：`RP_WORKTREE` 绑定到工作树根；`RP_R18_RUN` 为仓库外一次性目录 `${TMPDIR:-/tmp}/rp-r18-run.AhCgMZ`；`RP_R18_RUNTIME=$RP_R18_RUN/runtime`；未设置 `PYTHONPATH`（实测为空）。

**步骤 2：构建与导入来源确认**
- `nix build .#research-proposal-runtime --out-link "$RP_R18_RUNTIME"`：退出 0（有“Git tree is dirty”警告，属未提交工作树的正常提示）。
- 导入来源：位于 `$RP_R18_RUNTIME` 指向的构建输出内的 `lib/python3.14/site-packages/research_proposal/_state.py`，不在工作树内。
- 三个校验函数 `_check_candidate_scores`、`_check_verdicts`、`_check_materials_records` 均在，断言通过、退出 0。
- 运行包内 `_state.py` 与工作树源码 SHA256 **逐字节相同**（两侧均为 `3f735b0e…dcf5f8`），确认被测模块就是本次实现，不是旧运行包或未打包源码。

**步骤 3：组件测试**（`RP_TEST_OUTPUT=$RP_R18_RUN/component-output`，日志 `$RP_R18_RUN/rp18-components.log`）

| 项目 | 命令 | 结果 |
|---|---|---|
| RP-18 组件 | `"$RP_R18_RUNTIME/bin/python3" -m unittest -v test_verdict_record` | `Ran 69 tests`、`OK`、退出 0 |
| 兼容性回归 | 同解释器 `-m unittest test_interview` | `Ran 27 tests`、`OK`、退出 0 |

69 项覆盖本轮三条业务问题：硬门槛分数与判决对齐（`gap_zero` 要求「空白成因 = 0」、`novelty_zero` 要求「新意落点 = 0」、`pass` 与 `soft_stop` 要求两门槛都大于 0、`problem_invalid` 与 `merge` 不加入）；依据字段（空白串、布尔、数字、`null` 不算依据，多键被拒，`scores` 与 `evidence` 类型错误互不遮蔽）；免评分 `verdicts`（单候选可推进无总分保存并按题面版本读回、三值 `gate`、必填字段缺失、顶层与条目形状、未知 `gate`、数组形态、写分数键被拒、两对象共存与合并报错、一合规一违规、原样落盘、违规不改状态）。

**步骤 1：文档检查**（脚本 `$RP_R18_RUN/check.py`，日志 `$RP_R18_RUN/rp18-doccheck.log`）
- 结果：`PASS 169 checks / 169`、`ALL OK`、退出 0。
- 检查范围含：新节位置与字段清单、题面版本规则、汇总生成规则、未评记法、待补范围、`problem_invalid` 收窄、交叉引用与不扩散、去标识化；以及本轮三条修正的专项项——硬门槛分数与判决对齐、依据字段结构与报错累积、免评分 `verdicts`（文档与组件）、两对象合并报错（文档与 `runtime.md`）、导入命令为单个 `-c` 参数且含 `set -e`、`RP_R18_RUN` 定义在文档步骤之前。
- 该脚本的正向项（`runtime.md` 合并报错句存在性、`-c` 命令结构、变量步骤顺序）已用故意破坏验证会失败，不是空过。

**基线 diff 与不扩散**
- `git diff --numstat 97c1340 -- skills/research-proposal flake.nix flake.lock nix README.md`：`SKILL.md` 2+/2−、`references/candidate-scoring.md` 141+/31−、`references/runtime.md` 1+/1−、`scripts/research_proposal/_state.py` 395+/0−；`flake.nix`、`flake.lock`、`nix/`、`README.md` 无 diff。
- `test/test_verdict_record.py` 相对基线新增 841 行（新文件）。
- 九项权重、评分公式、两条硬门槛的含义与判据未改——**但空白成因 0 分的适用情形按 IR-01 收窄为“已证伪”（一种来源、两种情形：伪空白，或查证后确认没有相近工作），“还没查够三篇”改由「未评」承载**；这一收窄是先前已批准的语义修订，不是本轮改动。三类停因、五态判决词未改；`candidate_scores` 对 `pass` 的数值总分要求未因新增 `verdicts` 而放宽。

**隐私检查（只查新增行）**：新增行中无 URL、无用户主目录路径、无本次运行目录、无用户回看数值。唯一命中的绝对路径出现在 `plan/test-plan.md` 中 RP-14 的历史结果根一句——该句连同其中的路径在基线同一行已存在，本次只是同一行的仓库/分支/RP-18 说明被改写而使其显示为新增行，路径内容未新增也未改指向；按此前口径保留，不属本轮新引入的标识信息。

**结论**：RP-18 本轮必测项在当前版本取得通过结果，三条业务问题的失败输入均已被拒，合规输入仍可保存。本结论不代替实现符合性审核、第三关口与合并批准。

## RP-18 第四轮复验：用户复核第三轮（四条）修正后的正式执行（2026-11-28）

用户对 PR head `de1e42f` 第四次判 `NOT_READY`，提出四条：同一题面可在两个对象各记一条相反判决、非法停因抛 `TypeError` 打断整份报错、`scores` 形态错误时空白依据漏报、允许的权重配置让总分公式除以零。修正后执行计划与测试计划分别取得 `APPROVED`。

**角色与版本**
- 角色：本地执行工程师。工作树 `worktrees/research-proposal-record`，分支 `feat/verdict-record`，基线 `97c1340`，执行时 HEAD `de1e42f`（本轮改动未提交）。
- 执行计划 `rp-plan-r12-verdict-record-2026-11-28`，SHA256 `6a9353c307a3433eea715cfcb05ec42432831ecf841613e9f9a014f922a64655`（`APPROVED`，见 [implementation-plan-review.md](implementation-plan-review.md) 最后一节）。
- 测试计划 `rp-tests-r12-verdict-record-2026-11-28`，SHA256 `1fb92e33016b01c575e2056b9e1189d2010b2e5d60f16ce41133fdc00343356a`（`APPROVED`，见 [test-plan-review.md](test-plan-review.md) 最后一节）。
- 产品源码 `_state.py` SHA256 `3054f0936ec3b392fe4921015777cd74b6410691c96be4e26835c6df6e746a9d`；测试文件 `test/test_verdict_record.py` SHA256 `0140f2d898bce2f4733d3d91775aacfd663844021914b1009f527ca7fbe739ef`（79 项）。

**执行环境（按 RP-18 步骤 0）**：`RP_WORKTREE` 绑定到工作树根；`RP_R18_RUN` 为仓库外一次性目录；`RP_R18_RUNTIME=$RP_R18_RUN/runtime`；未设置 `PYTHONPATH`（实测为空）。

**步骤 2：构建与导入来源确认**
- `nix build .#research-proposal-runtime --out-link "$RP_R18_RUNTIME"`：退出 0（有“Git tree is dirty”警告，属未提交工作树的正常提示）。
- 导入来源位于构建输出的 `site-packages` 内，不在工作树。
- 三个校验函数 `_check_candidate_scores`、`_check_verdicts`、`_check_materials_records` 均在，断言通过、退出 0。
- 运行包内 `_state.py` 与工作树源码 SHA256 **逐字节相同**（两侧均为 `3054f093…746a9d`）。

**步骤 3：组件测试**（`RP_TEST_OUTPUT=$RP_R18_RUN/component-output`）

| 项目 | 命令 | 结果 |
|---|---|---|
| RP-18 组件 | `"$RP_R18_RUNTIME/bin/python3" -m unittest -v test_verdict_record` | `Ran 79 tests`、`OK`、退出 0 |
| 兼容性回归 | 同解释器 `-m unittest test_interview` | `Ran 27 tests`、`OK`、退出 0 |
| 四条缺陷探针 | 独立探针（非入库用例） | 6/6 符合预期：同版本跨对象重复被拒、`stop_reason` 为 `[]` 与 `{}` 均按 `ValueError` 拒绝且两侧问题同报、`scores: []` 配空白依据时两项同报、唯一正权重项未评时 `pass` 被拒 |

79 项覆盖本轮四条：整次保存的判决身份（跨对象重复被拒、同一候选不同版本可并存、同一题面文字下不同候选可并存、同对象重复不误报、`merge` 可指向只记在 `verdicts` 里的候选、报错含补救办法）；分母下限（`pass` 与 `soft_stop` 各提交一次、整表权重全为 0 同样被拒、改记 `pending` 可保存）；非法停因不打断报错（候选侧 `[]` 与 `{}` 两形态、另一对象错误同报；`verdicts` 侧四种形态）；依据取值可独立判断（`scores` 为 `[]`／`"70"`／`None` 时空白依据一并报出）。

**步骤 1：文档检查**（脚本 `$RP_R18_RUN/check.py`，日志 `$RP_R18_RUN/rp18-doccheck.log`）
- 结果：`PASS 217 checks / 217`、`ALL OK`、退出 0。
- 含本轮四条修正的专项检查（跨对象唯一性与补救句、分母为零在「未评」节与「怎么算总分」节两处、停因观察点写明候选侧、依据取值独立判断、文档“五条规则”／计划“五条处理”／测试计划“六类”计数一致）。
- 正向项（如 `runtime.md` 合并报错句与跨对象拒绝句存在性、`-c` 命令结构、变量步骤顺序）已用故意破坏验证会失败，不是空过。

**基线 diff 与不扩散**
- `git diff --numstat 97c1340 -- skills/research-proposal flake.nix flake.lock nix README.md`：`SKILL.md` 2+/2−、`references/candidate-scoring.md` 142+/31−、`references/runtime.md` 1+/1−、`scripts/research_proposal/_state.py` 489+/0−；`flake.nix`、`flake.lock`、`nix/`、`README.md` 无 diff。
- `test/test_verdict_record.py` 相对基线为新增文件（1002 行）。
- 九项权重、评分公式、两条硬门槛含义、三类停因、五态判决词未改（空白成因 0 分判据按 IR-01 收窄这一更早已批准的修订不变）；`candidate_scores` 对 `pass` 的数值总分要求未因新增 `verdicts` 而放宽；其他阶段与其他字段的保存行为不变。

**隐私检查（只查新增行）**：新增行中无 URL、无用户主目录路径、无本次运行目录、无 `nix` store 具体哈希、无用户回看数值。`plan/test-plan.md` 中 RP-14 的历史结果根绝对路径在基线同一行已存在，本次只是同一行其他文字被改写。

**快审后的补充复跑**：PR 快审指出两处记录层问题（本节前一轮的结果指针过期、`implementation-review.md` 的 R-1 表述未同步）与一处测试覆盖建议（“不同候选之间仍可保存”缺同版本不同候选的隔离用例）。已把第三轮复验标为历史、指针改指本节，并在 `test_verdict_record.py` 补 `test_same_version_different_candidates_can_coexist`（`C1/q1` 与 `C2/q1` 并存），用例数由 78 增至 79。测试计划观察点里“不同候选之间仍可保存”这句的对应案例名仍只列了原用例；补名会改变已批准的测试计划哈希，本轮不改计划文本，在此说明该覆盖由新增用例承担。

复跑结果（重建运行包、同一解释器）：组件 `Ran 79 tests`、`OK`、退出 0；回归 `Ran 27 tests`、`OK`、退出 0；文档检查 `PASS 222 checks / 222`、`ALL OK`、退出 0；运行包内 `_state.py` 与工作树源码 SHA256 仍逐字节相同（`3054f093…746a9d`）。执行计划 `6a9353c3…` 与测试计划 `1fb92e33…` 两个获批版本未变。

**结论**：RP-18 本轮必测项在当前版本取得通过结果，四条业务问题的失败输入均已被拒且不再抛 `TypeError`，合规输入仍可保存，跨对象重复报错给出可执行的补救办法。本结论不代替实现符合性审核、第三关口与合并批准。
