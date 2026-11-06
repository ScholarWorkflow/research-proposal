# 研究计划草稿技能计划审核记录

## 当前状态：r4 Markdown 交付修订已通过

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
