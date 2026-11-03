# 研究计划草稿技能测试计划

日期：2026 年 11 月 3 日。

## 版本与范围

- 测试计划版本：`rp-tests-r3-2026-11-03`。
- 需求版本：`rp-requirements-2026-11-02-q6-q16`。
- 执行计划：[implementation-plan.md](implementation-plan.md)，版本 `rp-plan-r3-2026-11-03`，校验值 `edf6692023be0e717ff454482c10763cc74c42885cc41ea8458fd1915fb69bcf`；批准依据见 [implementation-plan-review.md](implementation-plan-review.md)。
- 目标仓库：`research-proposal`；工作树：`worktrees/research-proposal-plan`；分支：`feat/research-proposal`。本次配置修正对应已交付产品 `4797a1bd69dca2a1354476a564c5d2714d8004da`；正式执行状态由执行工程师维护于 `plan/test-results.md`，本次准备修正不代跑用例。
- 第一关已通过，正式审核结论见 `plan/test-plan-review.md`。执行说明版本为 `rp-recipe-r5-2026-11-03`，本次仅修正固定夹具 TOML 的配置读取；准备符合性结论见 `plan/test-preparation-review.md`，第二关结论由主代理记录，第三关尚未执行。

范围来自已确认的业务要求和执行计划明确安排的成功、失败及兼容行为。首版完整流程只验收苹果芯片 Mac、Codex、Nix；npx skills 验收技能与随附资源的安装，不把它单独视为完整前置环境。

下面 RP-01 至 RP-13 及各项明确列出的场景构成唯一必测清单。每项按自己的观察点判断，不因某项安排了实际会话，就重新检查其他项已经覆盖的全部行为。不追加所有学科、学校、语言、文件格式的组合，不测试其他平台或运行工具，不重新验收上游全部业务、共享安装器或模型服务。

## 必测清单

### RP-01：Nix 安装交付

**目标**：一次安装提供主技能、直接依赖、原代理及固定运行程序，能支撑本计划要求的实际流程。

**输入或场景**：在约定平台，从固定产品提交安装到仓库和开发工作树之外的干净使用目录。该目录含一份无关的示例技能和一项无关配置，供检查保留行为；不使用用户真实配置。

**预期结果**：正式安装所需的固定构建输出实际构建成功；安装后的主技能及随附资源完整，六项直接依赖和原代理可用，不要求另跑 APM，不依赖开发目录的文件。安装保留无关示例技能与配置。安装说明准确区分代码安装与模型、Zotero、浏览器及视觉服务的外部条件。

**检查方式**：检查实际构建和安装结果、安装目录及相关配置条目；实际可用性直接采用 RP-04 的上游运行、RP-06 的材料读取和 RP-08 的成稿结果，不另跑一套相同流程。依赖服务采用真实服务的必要操作；不以仅列出工具、显示帮助或模拟成功代替可用。共享层已有适用结果直接引用，不新增安装冲突矩阵或通用运行时认证。

### RP-02：npx skills 安装入口

**目标**：用户能通过另一安装入口取得同一主技能及随附资源，知道仍需哪些运行条件。

**输入或场景**：在另一个隔离使用目录，从同一产品提交执行仓库公开说明的 npx skills 安装方式。

**预期结果**：主技能可以被发现，正文、脚本、参考资料和模板均可在安装位置访问；资源引用不依赖开发目录或另跑 APM。文档明确此入口不单独提供上游代理和工具服务，不承诺未经验证的平台组合。

**检查方式**：直接检查安装结果、技能发现结果及本技能引用的资源路径，并阅读该入口的说明。本项不重复 Nix 完整流程，也不要求为 npx skills 另造代理安装能力。

### RP-03：已有材料发现与复用

**目标**：用户给定路径后自动找到适用材料，并沿用有效成果及真实选择。

**输入或场景**：同一份有效资料分别以专攻目录、`教授研究` 目录、单个教授目录和具体正式产物路径进入输入发现组件；另有两个可选教授或方向而用户未指定的资料。已有产物包含两种状态：有效输入包及候选均齐全；有效输入包齐全但缺候选。

**预期结果**：四类路径均对应正确的申请项目、教授和已有进度；对象未明确时提供选择，收到已有明确选择时沿用。输入包和候选均有效时直接交研究计划选题；只缺候选时调用上游第三阶段。不会因存在 Markdown 报告就伪造正式上游状态，也不把套磁选择自动认作研究计划已确认的全部选题。

**检查方式**：输入发现与有效性判断采用产品组件的常规自动测试，直接检查其结果及正式输入状态；用户选择和第三阶段调用采用围绕同一资料的连续实际 Codex 交互，观察相关用户决定、该次委派和候选结果。两种方式各检查上述不同部分，不再次证明同一行为。有效产物由原流程生成或取自已有有效保存件，不手造“已完成”状态。

### RP-04：从合格招生项目资料补齐上游输入

**目标**：尚未运行 professor-contact 时，新技能通过依赖自行完成所需前置流程。

**输入或场景**：一个合格的招生项目资料目录，尚无教授研究产物；测试会话按真实提示提供教授、方向等必要选择。该资料采用可实际读取的公开研究来源。

**预期结果**：完成采集和预筛，沿原规则运行阶段 0、1、2、3，获得有效输入包和候选，并交研究计划自己的选题。定向补全文归第一阶段；各阶段由原命名代理负责，完成原检查和收尾，不手写上游状态，不进入邮件编译或邮件生成阶段。已有用户决定不被绕过。

**检查方式**：通过安装后的主技能进行实际 Codex 会话，检查正式目标、第一阶段快照、输入包和候选结果，以及本项要求的阶段委派与顺序。只查看这些相关调用及结果，不收集完整运行链或认证全部子代理。所得材料继续用于 RP-07、RP-08，不重新从头采集。

### RP-05：零散论文分析的前置补齐

**目标**：已有分析但缺正式输入包时，先满足上游真实前置条件，再复用有效分析。

**输入或场景**：从原流程的有效资料副本中保留论文分析和事实文件，移除正式输入包、目标及第一阶段快照，形成计划明确支持的未完成状态。

**预期结果**：先检查并补齐适用预筛、阶段 0 和第一阶段，再交第二阶段检查已有分析是否可复用；不会直接跳到第二阶段或第三阶段。只有通过原身份、来源和缓存检查的分析才可复用，最后形成有效输入包及候选。

**检查方式**：通过安装后的主技能运行此场景，查看目标和快照建立结果、第二阶段预检结果及最终输入包；核对本项要求的阶段顺序。直接采用上游的复用判断，不重新实现论文身份检查，也不要求再次批量分析全部论文。

### RP-06：非论文材料读取、定位和候选

**目标**：专著、史料或作品材料按实际载体读入，并能支持可追溯的候选研究问题。

**输入或场景**：一组小型、有权使用的材料，包含文字 PDF、扫描页或图片、TXT、Markdown、EPUB、HTML 和 Word；每种载体只需一个能体现其定位方式的样本。扫描样本含一处确实无法辨认的文字，另有一个不在支持范围内的文件。随后将其中相关材料交给主技能，不预先给定研究问题。

**预期结果**：读取内容与原材料相符；出处、页或段落、表格或区域等定位可回到相应原文。无稳定分页的 Word 不编造页码；识别不明处保留缺项，图像解释与逐字转录分开，不支持的文件明确报告需要转换。技能提出少量有材料依据、方法和缺项说明的候选，等待用户选择；这一路线不强制产生套磁候选文件或套用“作者后续工作”。

**检查方式**：载体读取及定位使用材料组件的常规自动测试并直接对照样本，扫描识别采用已安装视觉入口的实际结果；实际会话只检查候选形成和用户选择，不重新逐项验收解析器。文字识别不以逐字零误差或固定置信度作为新增通过条件，疑难部分须被如实保留。

### RP-07：相关研究、条件判断与中文方案

**目标**：将已选问题转成有证据且可以开展的方案，并落实两处用户决定。

**输入或场景**：复用论文路线或非论文路线已选问题，以及事先选定、可读取的相关来源；包含教授之外的研究、需要分辨的矛盾结论和一个有待核实的关键材料取得条件。条件先无可靠取得途径，再补充可核实的申请条件和备用办法，但不声称资源已经取得。条件补齐后，围绕同一稿件先查看尚未确认的中文方案，再针对实际方案给出用户确认；已有有效确认的部分继续复用。

**预期结果**：说明已有研究、本计划的具体区别及方法依据；资料足够后停止补查，矛盾尚可能推翻选题时继续针对该问题核对，已确认的真实学术分歧可以作为动机。关键条件未解决时保存方案、缺项和替代建议；有合理途径与备用办法后可形成中文方案，区分计划申请、符合条件和已经获得。关键条件未解决，或适用的中文方案尚未获得用户确认时，不生成或提交完整目标语言正文，可保存中文方案、大纲和缺项；条件与确认均满足后才进入 RP-08。研究问题与中文方案分别记录用户决定，已有明确决定不重复询问。

**检查方式**：沿同一稿件的连续实际交互继续，人工对照所用来源、条件说明、中文方案与用户决定。在条件未解决和中文方案尚未确认的时点，直接查看当时的输出与稿件状态，确认没有提前生成或提交完整正文；有效确认继续沿用，不增加重复成稿运行或逐步记录。只判断这些业务内容，不限定论文篇数、检索次数或答案固定措辞，不把搜索结果摘要当作已取得全文。缺少关键原文时应保留缺项。

### RP-08：完整草稿及两种格式

**目标**：在方案和条件成立后，交付符合目标用途、可继续修改的研究计划草稿。

**输入或场景**：复用 RP-07 已确认方案、真实或合成且明确给定的个人准备信息、申请项目要求及研究期限；先采用没有学校模板的情况。论文路线用日文、非论文路线用中文，各完成一份草稿；英文放入 RP-10 的明确改稿请求，不另做三种语言与全部输入的组合。

**预期结果**：正文说明背景与相关研究、一个核心问题及必要子问题、方法和步骤、适合课题的判断办法、进度、预期成果与备用方案，并遵守该项目规定的栏目、语言和篇幅。引用及定位支持论断，作者结果、作者建议和申请者设想被区分，个人能力与资源状态没有被夸大。Word 与 Markdown 正文一致，另有输入、状态和待确认事项；不影响方案成立的细节可保留待确认。研究计划文件存于资料目录，不进入产品源码。

**检查方式**：直接阅读两份草稿、必要引用原文及本稿状态，采用产品生成的页面预览核对缺页、溢出和不可读文字。按段落、列表、表格内容和引用比较正文，不要求 Markdown 复制 Word 版式；不另建评分模型或通用判定器。

### RP-09：学校模板与转填草稿

**目标**：可填写模板优先使用；无法可靠填写时仍交付学校栏目对应的 Word 草稿。

**输入或场景**：对已确认的同一正文，分别提供一个可直接填写的 `.docx` 模板和一个不能直接填写的学校模板。模板含固定说明和限定栏目；招生材料中另有一份需要读取栏目要求的空白研究计划表。

**预期结果**：正式表格要求被读取，不因招生摘要跳过空白表而遗漏。可填写模板在副本中完成，固定文字和原件保留；另一场景按原栏目生成普通 Word 草稿并说明需要转填，不声称已填好学校原表。两种场景均与该版 Markdown 正文一致。

**检查方式**：使用产品导出入口，直接检查填写区域、原模板及页图和正文对应关系。本项只验收模板适配，不重新审查 RP-08 已检查的学术内容；不新增 PDF 表单填写或旧 `.doc` 转换能力。

### RP-10：用户修改稿、确认及版本选择

**目标**：采用用户指定的修改稿继续工作，同时保留原件和仍有效的决定。

**输入或场景**：从已交付版本继续，分别给出带未决插入、删除和批注的 Word 修改稿，以及 Markdown 修改稿；附一个不能可靠读入的嵌入对象。覆盖纯措辞改动、用户明确要求的核心方法修改及改为英文、文件中未说明意图的关键条件变化；另给出两个互相冲突且用户尚未选定的版本。

**预期结果**：原件保留，修订和批注不会被静默全部接受或丢弃，批注不自动进入正文；无法可靠读取的对象报告具体位置。纯措辞改动复用原确认；明确授权的实质修改直接执行；意图不明的实质变化只确认受影响部分，未受影响成果继续使用。冲突版本由用户选择，不按修改时间自动合并；导入的事实和引用仍要有材料依据。

**检查方式**：修改稿内容及修订标记的读入采用产品导入组件常规测试；确认与版本选择在实际会话中观察用户决定、本稿状态和新旧稿件。各场景只检查发生变化的部分，引用 RP-08 的既有成稿结果。不能通过在测试提示词中替产品补写处理步骤获得通过。

### RP-11：提交失败、中断及恢复

**目标**：完整交付才切换当前版本，部分失败和中断后保留有效旧稿并续接已有成果。

**输入或场景**：使用已存在的正文和两种导出，在产品正文、导出和状态组件的常规测试中覆盖下表。失败在相应操作边界触发；不手写成功状态来冒充产品提交，也不建立通用故障注入平台。

| 场景 | 预期结果 |
|---|---|
| 两种导出和核对完成 | 当前版本切换，新旧版本均保留，两个交付路径属于同一新版。正常成稿采用 RP-08 的结果，本项不重复整段写作。 |
| 一种导出成功，另一种失败 | 当前版本仍为旧稿；首次生成时没有已提交稿。成功导出和工作正文保留，输入未变时补失败步骤后再提交。两种格式的失败分支按同一检查方式覆盖。 |
| 两种导出内容不一致，或页面核对发现缺页、溢出等问题 | 保留工作结果，修复并重新核对前不发布新版，不把半份或缺内容稿件作为完整交付。 |
| 材料、方案或正文步骤中断 | 从已经保存的有效步骤继续，未保存的步骤重新执行；不要求逐个内部函数安排中断。 |
| 完整目录已保存，当前版本尚未切换；以及切换后中断 | 前者按明确的进行中记录核对后续接提交；后者直接重报已提交文件，不重复生成或退回旧版。 |
| 恢复前正文、模板、材料或用户选择改变 | 只使依赖该变化的工作失效；不能继续交付基于旧正文生成的另一种格式，适用的实质变化按 RP-10 处理。 |
| 同稿的另一轮工作先更新了基准 | 后返回的工作保留自己的目录，不覆盖另一轮决定或当前稿；只覆盖这一个计划明确约定的冲突，不做并发压力测试。 |

**检查方式**：使用标准测试框架控制相应组件的文件操作、导出失败或返回结果，并检查实际保存的当前版本、工作状态及文件内容。只在这些失败分支使用受控失败，不将模拟的模型、论文分析或依赖服务成功当作真实完整流程结果。普通断言或人工文件检查足以判定，不增加事件重放、逐调用账本或独立判定器。

### RP-12：一稿一项目及跨校复用

**目标**：每份稿件绑定一个申请项目、用途和核心问题，复用资料时仍分别管理正文与进度。

**输入或场景**：已有一份已提交稿件；用户以同题申请第二个学校，并明确希望复用文献和通用方案。第二个项目有不同的用途、栏目或篇幅。

**预期结果**：建立新稿件编号并绑定第二个项目及用途；明确复用的材料和方案可使用，学校要求、正文、用户决定及当前版本分别保存。第一份稿件与其他教授状态保持原状，不简单复制原学校格式。

**检查方式**：通过实际改稿会话，检查两份稿件的输入、状态及正文，直接比较第一稿前后相关文件。本项只检查归属和复用边界，不重复全部材料读取和写作检查，也不增加同名对象消歧能力。

### RP-13：缺少前置资料或外部能力时保留进度

**目标**：缺输入或外部服务不能使用时如实说明受影响步骤，并保留已完成的有效成果。

**输入或场景**：一个空目录或只有学校名称的输入；另在已有进度的隔离资料中，使当前必需的一个外部能力不可用，例如未配置扫描文字识别服务。只选择一个能代表保留进度行为的外部失败，不分别制造所有依赖的故障。

**预期结果**：缺招生项目前置资料时说明需要补齐，不自行承诺从任意网页建立完整项目。外部能力缺失时指出受影响步骤，保存原错误或缺项及已有进度，不把部分资料写成完整证据或完整草稿；条件补齐后可继续适用步骤。

**检查方式**：使用安装后的主技能观察缺项说明和资料状态；外部条件补齐后的继续执行采用对应正常项的结果，不另跑全流程。该项预期的缺配置表现与测试运行中偶发的服务故障分开记录，后者按实际影响记为无法判断。

## 准备和执行的边界

需要真实用户选择或确认的场景，使用现有评估服务对同一隔离使用目录和同一稿件逐次发送请求。先检查上一请求的实际问题、方案和产品保存的状态，再将针对该问题或该版方案的具体用户决定作为下一请求的输入；不预先灌入尚未提出的问题的答案，也不直接改写产品确认状态。每次请求可以建立新的运行时对话，不要求恢复同一个线程；交互之间继续使用产品已经保存的有效成果，不重复成稿。依据为现有评估服务 [app-server 入口约定](../../../eval-server/docs/appserver-migration.md)第 193–201 行，源码版本 `1ae8b6131bd0041b82cf3cc3789bf7fe09dfac6e`：每次评估创建新的主对话，不支持 `resume`。这只调整请求组织方式，不新增测试场景或修改运行时。

本轮用户已授权执行工程师扮演合成申请者，在看到实际选项或方案后作出测试决定，并在正式结果中保存实际选择；该授权仅用于隔离测试，不预填决定、不改写产品状态，也不省略原定确认条件。

上述目标和预期结果在产品运行前确定，不能根据实际输出倒推通过条件。业务判断所需的来源、材料片段、学校要求、用户选择及已知缺项由本地测试工程师事先准备；使用有权使用的公开材料或合成申请信息，不复制用户实际申请资料到产品仓库。

上游正式状态采用原流程生成的有效资料或已有有效保存件。未完成场景可从隔离副本移除本项指定的产物；检查仍由生产入口完成，不能补造成功状态或修改消费者里的受管代码。材料载体样本只用于其声明的检查，不伪装成现实中已发表的研究证据。

每个已完成目标选择表中规定的足够观察点。自动检查使用产品仓库的普通测试代码；实际会话使用安装后的主技能。只对 RP-03、RP-04、RP-05 明确列出的阶段委派与顺序查看相应调用；其他项以业务产物和用户可见行为判断，不要求完整运行轨迹。

以下准备职责继续有效。本轮已经准备输入、普通测试和配置合成步骤并做有限预检；没有构建或安装产品，也没有运行正式用例。执行时按下文绑定实际值：

1. 固定首个待测产品提交、实际依赖锁定图、配置版本和适用的已有结果；本次尚不存在这些执行记录，不虚填提交号或声称可复用测试已经通过。
2. 准备上述小型输入和必要测试代码，给出每项可直接执行的准备顺序、命令、实际输入与输出位置。对 RP-11 的受控失败，采用标准测试框架的现有能力；如果确实需要新的专用设施，先按测试规则申请明确范围，不能直接作为必测前置。
3. 从固定产品提交按正式入口安装到干净使用目录，按需要隔离 `CODEX_HOME`、Zotero 数据、浏览器配置和其他可写状态，不替换 `HOME` 或连接用户生产资料。可复用的安装和缓存继续使用；RP-01、RP-02 因目标就是安装交付而安排各自安装。
4. 使用 `skills-test-fixtures` 前先更新其主分支并固定实际使用版本；依该版本的现有配置与准备方式安排环境。运行配置的路径、变量来源与加载方式由测试工程师写清，不转交用户猜测，也不复制产品代理或工具配置到夹具中补偿安装缺陷。
5. Codex 实际会话使用现有评估服务，按项目共识使用默认配置；在干净使用目录启动，命令携带该目录。具体请求及配置以准备时读取的服务文档为准，本计划不虚构尚未核对的接口参数，不自行启动、停止或重启评估服务。
6. 仅做命令可运行、必需依赖与配置可用、用户状态隔离的预检。临时配置、预检输出与原始结果放在仓库外独立临时目录，正式测试代码留在产品仓库；不新增环境来源认证或全环境快照。
7. 在执行说明中写明可重试的外部故障、最多尝试次数、停止条件、需要重置的状态和保持不变的输入配置。已确认业务失败不因结果不满意而重跑；环境未恢复时不连续重复完整运行。所有正式尝试保留。

以上是准备职责。下文记录输入、可执行安排及执行前需要绑定的实际值。产品尚未实现、尚无正式运行生成物，不阻止按已批准执行计划编写步骤；第二关核对步骤与产品约定是否一致，不要求提前运行产品。

## 执行说明

### 已准备的版本、输入和配置

本节版本为 `rp-recipe-r4-2026-11-03`。它保留上面的全部业务检查，不增加通过条件。产品提交、发布来源、独占目录和服务端口在正式执行前按下文绑定；真实上游成果和成稿由指定的前序用例产生。它们当前没有实际值，不作为准备设计缺陷，也不表示已有产品通过结果。

共享夹具已先在干净 `master` 上执行 `git pull --ff-only origin master`，结果为已是最新；本轮固定 `5a31ae0095952cc359f7fa826730f14e7ee4f5b2`。共享缓存原记录属于 `8cecafc694e4591dee47372f38903e5ac2b689fe`，所以只复用其中的不可变插件与下载缓存，在独立临时根重跑现有 `prepare_shared_test_assets_macos.sh`，没有修改旧缓存或生产配置。本轮新记录与固定夹具版本一致、工作树干净。没有启动 Chrome、Zotero 或模型业务请求。

正式可复用输入均在 [test/fixtures](../test/fixtures/README.md)。该目录说明各样本的已知内容、定位、适用范围及公开来源，不另存执行步骤。七类载体、残损扫描图、未支持扩展名、两种模板、修订和冲突稿、合成申请者、甲乙项目要求以及无关安装项均已落盘。真实作品、期刊全文、募集要项与空白研究计划表仅保存在仓库外，避免向源码再分发全文。

本轮实际准备目录由交接提供，称为 `RP_PREP`；其中 `config/runtime-locations.env` 记录夹具目录、评估服务配置所在目录、视觉配置来源及隔离输出位置，不含密钥。`input/admissions/` 已组合公开招生资料与三字段 `info.json`；`input/nonpaper/` 已放入《罗生门》原文、合成个人资料与甲项目要求；`input/empty/` 为空目录。`sources/` 保留公开原始资料，`render/` 是样本页面，`logs/` 是有限预检输出。上述目录都不是干净产品安装，不能将其中的空消费者目录记为已安装。

配置来源按以下顺序使用：

1. Codex 的模型与推理强度只取固定夹具 `configs/codex-smoke-defaults.toml`，当前解析值为 `gpt-6-luna`、`low`；普通可写工作区差异取 `examples/codex/ordinary-smoke.toml`。不在请求里另写第二份默认值。
2. 主技能、原命名代理、运行程序、MCP 启动定义和项目配置由待测产品正式安装生成。原命名代理的递归调用沿用计划中的固定上游定义；嵌套调用开关读取夹具的 `configs/codex-nested-delegation-consumer.toml` 中 `features` 表，不复制其模型默认值，不增加角色或临场提高线程上限。
3. 视觉客户端固定来源声明的用户配置位置已经找到，`VISION_API_KEY`、`VISION_BASE_URL`、`VISION_MODEL` 三项均非空，另有模型链配置 `VISION_CHAIN`。已在 `RP_PREP/config/vision.env` 创建权限为 `0600` 的本轮副本，并用固定客户端支持的 `VISION_STATE_FILE` 指向本轮独占目录。实际值不写入计划或对话。RP-13 使用独立 `vision-missing.env`，明确把三项与 `VISION_CHAIN` 都设为空，避免继承模型链后继续调用服务。实际加载均须通过产品支持的 `VISION_ENV_FILE` 入口；当前没有运行该入口。
4. Zotero 与浏览器使用同版夹具的独占数据、配置、进程及自动端口。固定 Zotero 客户端接受 `ZOTERO_HTTP_URL`、`ZOTERO_MCP_URL`，通过 shell 环境传入；固定 `chrome-devtools` 原生 MCP 服务接受 `CHROME_CDP_PORT`、`CHROME_PROFILE_DIR`、`SKILLREPO_DATA_HOME`，通过该服务的 `env` 传入。固定 `personal-knowledge` 原生 MCP 服务接受 `OPENCODE_PK_DATA_DIR`、`OPENCODE_PK_MODEL_CACHE_DIR` 和 `KB_SERVER_PATH`；前两项指向本轮目录，后一项保留环境已有程序位置。现有覆盖入口足够按下文生成配置；不复制代理、包装器或启动定义。
5. 评估端口和已有知识库程序位置从 `direnv exec "$RP_EVAL_DIRECTORY"` 取得，不另行启动、停止或重配评估服务。共享安装器进程使用本轮空 `CODEX_HOME` 避免读取用户安装配置；该值不传给评估请求，已有服务认证不复制到仓库，`HOME` 保持原值。

线程配置使用受支持的 `agents.max_concurrent_threads_per_session`，值由执行者在每次请求提交前绑定为 `RP_THREAD_BUDGET`。按该请求从现有保存点开始、依原流程可能处理的对象数及固定上游声明计算**累计可创建的子线程数**，主对话不计入，已完成子线程不扣除；不把同一时刻的并行数当作会话容量。上游 analyzer 的[固定调用约定](https://github.com/ScholarWorkflow/professor-contact/blob/ad096fe31a4b5694cbe47a40f37b621435e1eeec/packages/professor-contact-codex/.apm/agents/professor-contact-analyzer.agent.md#L40)规定同批最多 3 个 `paper-analysis`，每个再启动 3 个叶子；对一次 analyzer 调用，按本请求的论文分析任务数 `P` 与剩余样式校验次数 `V` 预留 `1 + 4 × P + V`。`P` 包括全部批次及适用的仅补缺项分析；`V` 按[默认最多两次校验](https://github.com/ScholarWorkflow/professor-contact/blob/ad096fe31a4b5694cbe47a40f37b621435e1eeec/packages/professor-contact-codex/.apm/agents/professor-contact-analyzer.agent.md#L628)的剩余次数计算，额外校验仅采用已有真实授权的记录上限。再加上本请求仍会进入的采集、预筛、阶段 0、1、3 及它们按固定入口需要的子线程和校验；已有效完成且不会重跑的阶段不计入。计算中的对象数取当前有效输入、原阶段目标和既有批次安排，在现有请求准备说明中留一句来源与算式；不要求采集运行调用树证明这个数值。

只在原流程已保存进度且请求自然返回后，按下一请求的已知范围重新绑定预算。若现有资料尚不能确定下一请求的合法处理范围，先完成该阶段原有的用户选择，再按原交互继续；不强制拆分业务阶段、不更改上游批次或真实决定。数值必须在对应请求开始前确定，不能在线程失败后提高并重试。允许的嵌套层级沿固定上游根→analyzer→paper-analysis→叶子，叶子是终点；已有 `multi_agent_v2` 模式承担嵌套委派。[当前官方配置参考](https://learn.chatgpt.com/docs/config-file/config-reference)给出上述线程键，未给出 `max_depth`，因此不写未支持的深度覆盖。

### 准备与执行顺序

以下步骤由第二关通过后的本地执行工程师按依赖顺序执行。本轮只编写和检查步骤，不运行构建、安装、组件测试或实际请求。产品交付时绑定来源和提交，不改动以下已约定的输出、接口或命令参数。

1. 在生产者工作树运行 `pwd`，把返回值保存为 `RP_WORKTREE`。将交接给出的准备目录赋给 `RP_PREP`，读取 `config/runtime-locations.env`。在仓库及其工作树之外用 `mktemp -d /private/tmp/research-proposal-run.XXXXXX` 创建正式运行根 `RP_RUN`；两个安装目录分别为 `RP_RUN/consumers/nix` 和 `RP_RUN/consumers/npx`，原始响应在 `RP_RUN/requests/`。安装后把实际输入复制到 Nix 使用目录的 `input/` 子目录，稿件保存于该子目录内，便于同一使用目录持续处理。
2. RP-01 安装前放入无关技能和配置。按下方四个固定输出构建，使用共享缓存激活器安装；它调用同一组合环境的 `bin/agent-env apply --project`。构建和安装属于 RP-01，不作为准备预检执行。
3. RP-02 在另一目录用固定 `skills@1.7.2` 安装同一产品提交及 `skills/research-proposal` 子目录，不使用本地复制、开发路径或另跑 APM。两种安装记录实际来源、版本、命令与路径；后续沿用 RP-01 安装。
4. 从 `RP_PREP/input/admissions` 复制招生输入，先运行 RP-04 形成真实上游成果，供 RP-03、RP-05、RP-07 和 RP-08 复用。此前已在本工作区的旧测试消费者及临时目录内查找正式输入包和候选，没有找到可引用的有效保存件；没有使用生产申请资料。RP-04 的有效结果在正式执行前尚不存在，不能提前编造。
5. 各实际交互都使用下节的相同评估入口。首次只提供该场景的资料路径、用途及已存在的真实决定；提出新的问题或方案后，先阅读响应及产品已保存状态，再取得针对该对象的用户决定，作为下一请求。请求次数由既有必需交互决定，不预填尚不存在的问题答案，不直接修改产品状态。

发布交接提供 GitHub 的 `RP_REPOSITORY`（`owner/repo`）和完整 `RP_REVISION`。它们是必填执行参数，未填时先取得交接，不默认取主分支。安装命令如下：

```bash
set -euo pipefail
RP_WORKTREE="$(pwd)"
source "$RP_PREP/config/runtime-locations.env"
: "${RP_REPOSITORY:?需要产品发布仓库}"
: "${RP_REVISION:?需要完整产品提交}"
RP_REF="github:$RP_REPOSITORY/$RP_REVISION"
RP_SKILLS_SOURCE="https://github.com/$RP_REPOSITORY/tree/$RP_REVISION/skills/research-proposal"
RP_RUN="$(mktemp -d /private/tmp/research-proposal-run.XXXXXX)"
RP_CONSUMER="$RP_RUN/consumers/nix"
RP_NPX_CONSUMER="$RP_RUN/consumers/npx"
mkdir -p "$RP_CONSUMER" "$RP_NPX_CONSUMER" "$RP_RUN/logs" \
  "$RP_RUN/requests" "$RP_RUN/config" "$RP_RUN/activation-home"
cp -R "$RP_WORKTREE/test/fixtures/install/.agents" "$RP_CONSUMER/.agents"
cp -R "$RP_WORKTREE/test/fixtures/install/.codex" "$RP_CONSUMER/.codex"
nix build "$RP_REF#research-proposal-runtime" --out-link "$RP_RUN/runtime" \
  > "$RP_RUN/logs/build-runtime.log" 2>&1
nix build "$RP_REF#research-proposal" --out-link "$RP_RUN/package" \
  > "$RP_RUN/logs/build-package.log" 2>&1
nix build "$RP_REF#research-proposal-environment" --out-link "$RP_RUN/environment" \
  > "$RP_RUN/logs/build-environment.log" 2>&1
nix build "$RP_REF#research-proposal-activate" --out-link "$RP_RUN/activate" \
  > "$RP_RUN/logs/build-activate.log" 2>&1
CODEX_HOME="$RP_RUN/activation-home" \
  "$RP_RUN/activate/bin/research-proposal-activate" --project "$RP_CONSUMER" \
  > "$RP_RUN/logs/activate.log" 2>&1
RP_RUNTIME="$RP_RUN/runtime"
(
  cd "$RP_NPX_CONSUMER"
  NPM_CONFIG_CACHE="$RP_RUN/npm-cache" npx --yes skills@1.7.2 add \
    "$RP_SKILLS_SOURCE" --skill research-proposal --agent codex --copy --yes
) > "$RP_RUN/logs/npx-install.log" 2>&1
```

各命令单独等待退出，非零时停止受影响步骤，不继续把后续空目录当安装成果；长构建按本地执行角色的原生会话规则等待。缓存激活器的名称由执行计划明确为 `research-proposal-activate`，`--project` 来自固定共享入口；首次安装已调用 `agent-env apply`，无需再执行第二次 apply。RP-01 的保留项、技能资源、原代理及六项依赖按原检查方式阅读实际安装结果。RP-02 按固定 CLI 的项目安装位置 `.agents/skills/research-proposal/` 检查完整资源及相对引用。

实际业务前复制本轮输入到 `RP_CONSUMER/input/`，服务只启动一次并由所有请求共用。下列启动入口返回本轮 `fixture.env`，其中端口由服务分配；不写固定端口：

```bash
cp -R "$RP_PREP/input" "$RP_CONSUMER/input"
export SCHOLAR_TEST_FIXTURE_ROOT="$RP_FIXTURE_ROOT"
CHROME_FIXTURE_ENV="$(uv run bash "$RP_FIXTURES/scripts/start_chrome_test_fixture_macos.sh")"
source "$CHROME_FIXTURE_ENV"
ZOTERO_FIXTURE_ENV="$(uv run bash "$RP_FIXTURES/scripts/start_zotero_test_fixture_macos.sh")"
source "$ZOTERO_FIXTURE_ENV"
export RP_FIXTURES
export RP_KB_DATA="$RP_CONSUMER/.test-runtime/knowledge/data"
export RP_KB_CACHE="$RP_CONSUMER/.test-runtime/knowledge/cache"
export RP_BROWSER_DATA="$RP_CONSUMER/.test-runtime/browser"
export RP_VISION_FILE="$RP_VISION_CONFIG"
export RP_KB_SERVER_PATH="$(direnv exec "$RP_EVAL_DIRECTORY" sh -c 'printf %s "$KB_SERVER_PATH"')"
: "${RP_KB_SERVER_PATH:?需要现有知识库程序配置}"
mkdir -p "$RP_KB_DATA" "$RP_KB_CACHE" "$RP_BROWSER_DATA"
```

使用固定工具的真实覆盖键合成消费者配置，表达式仅在 [consumer-runtime.yq](../test/config/consumer-runtime.yq) 维护。先用 `yq -p=toml` 从原夹具提取 `features` 到本轮 JSON 输入；yq 4.54.1 的 `load` 不自动按 TOML 解析，也不支持 `from_toml`，不能直接对加载后的字符串读取 `.features`。它保留原有模型、代理、服务命令与参数，仅增加本轮环境和已有嵌套模式。原生 MCP 环境与 shell 环境分别设置；不依赖长期运行的评估服务自动继承调用者临时变量：

```bash
: "${RP_THREAD_BUDGET:?按当前请求的固定上游处理范围绑定累计线程预算}"
test "$RP_THREAD_BUDGET" -gt 0
export RP_THREAD_BUDGET
RP_PROJECT_CONFIG="$RP_CONSUMER/.codex/config.toml"
test -f "$RP_PROJECT_CONFIG"
test ! -L "$RP_PROJECT_CONFIG"
yq -e -p=toml \
  '.mcp_servers."chrome-devtools".command != null and .mcp_servers."personal-knowledge".command != null' \
  "$RP_PROJECT_CONFIG" > /dev/null
RP_INSTALLED_CONFIG="$RP_RUN/config/installed-config.toml"
if [ ! -f "$RP_INSTALLED_CONFIG" ]; then
  cp "$RP_PROJECT_CONFIG" "$RP_INSTALLED_CONFIG"
fi
umask 077
RP_CONFIG_OUTPUT="$RP_RUN/config/consumer-config-r5.toml"
export RP_NESTED_FEATURES_FILE="$RP_RUN/config/nested-features.json"
yq -e -p=toml -o=json '.features' \
  "$RP_FIXTURES/configs/codex-nested-delegation-consumer.toml" \
  > "$RP_NESTED_FEATURES_FILE"
jq -e 'type == "object" and .multi_agent_v2.enabled == true' \
  "$RP_NESTED_FEATURES_FILE" > /dev/null
yq -p=toml -o=toml --from-file "$RP_WORKTREE/test/config/consumer-runtime.yq" \
  "$RP_INSTALLED_CONFIG" > "$RP_CONFIG_OUTPUT"
yq -e -p=toml '.features.multi_agent_v2.enabled == true' \
  "$RP_CONFIG_OUTPUT" > /dev/null
cp "$RP_CONFIG_OUTPUT" "$RP_CONSUMER/.codex/config.toml.new"
mv "$RP_CONSUMER/.codex/config.toml.new" "$RP_PROJECT_CONFIG"
```

本轮项目本身是独占消费者；这些写入不触及用户配置或已有生产数据。`KB_SERVER_PATH` 如已由安装固定，保留安装值；新增时采用环境已有值。知识库数据和缓存、浏览器辅助数据均为本轮路径。若必需服务定义缺失，按 RP-01 的实际安装结果归属，不以临时启动定义补齐。共享请求准备器的单个 `fixture_mcp` 范例不用于替代这份多服务配置。

本次 r5 修正只影响消费者配置合成及写入前检查。若 r4 已生成失败配置，保留原安装快照、失败配置和诊断，另用新配置输出路径从原安装快照重新合成；检查通过后由执行者替换自己的消费者配置。未受影响的 RP-01、RP-02 安装和组件结果继续采用，不重装、不重跑，尚未发出的评估请求在本次配置修正审核后继续。

已安装使用目录的每次请求采用固定夹具现有入口：

```bash
UV_CACHE_DIR="$RP_PREP/uv-cache" uv run \
  "$RP_FIXTURES/scripts/prepare_codex_project_config.py" \
  --defaults "$RP_FIXTURES/configs/codex-smoke-defaults.toml" \
  --recipe "$RP_FIXTURES/examples/codex/ordinary-smoke.toml" \
  --consumer-root "$RP_CONSUMER" \
  --run-dir "$RP_REQUEST_DIR" \
  --prompt "$RP_PROMPT" \
  --timeout "$RP_TIMEOUT"
```

`RP_CONSUMER` 是 RP-01 的实际安装路径；`RP_REQUEST_DIR` 是 `RP_RUN/requests/` 下尚未存在的本次请求目录。`RP_PROMPT` 是当前业务请求或刚取得的具体用户决定；`RP_TIMEOUT` 对 RP-04、RP-05 固定为 1800 秒，对其他请求固定为 600 秒。每个新请求有独占目录，但沿用同一消费者和稿件数据。准备入口生成 `resolved-config.toml`、`preparation.json`、`eval-request.json`，只读取本次 `preparation.json.loading_method` 确认应使用的加载方式；不另造配置解析器或手抄配置参数。

上面的普通范例与已合成的消费者配置共同使用；模型默认仍只来自固定夹具。准备入口发现缺少变量、未安装服务、受保护设置冲突或配置不能传输时停止受影响项，不改为连接生产服务。RP-13 将 `RP_VISION_FILE` 设为 `RP_VISION_MISSING_CONFIG`，重新执行同一配置合成和请求准备步骤；恢复时改回 `RP_VISION_CONFIG`。两次都保留各自请求目录，不修改视觉凭据文件。

实际请求采用已核对的服务协议：

```bash
RP_EVAL_PORT="$(direnv exec "$RP_EVAL_DIRECTORY" sh -c 'printf %s "$EVAL_PORT"')"
curl --silent --show-error --max-time "$((RP_TIMEOUT + 30))" \
  --output "$RP_REQUEST_DIR/response.json" \
  --write-out '%{http_code}\n' \
  --request POST "http://127.0.0.1:$RP_EVAL_PORT/eval" \
  --header 'Content-Type: application/json' \
  --data-binary @"$RP_REQUEST_DIR/eval-request.json" \
  > "$RP_REQUEST_DIR/http-status.txt"
jq '{passed, version, termination_reason: .output.termination_reason, error}' \
  "$RP_REQUEST_DIR/response.json"
```

`passed` 只表示请求正常结束，不是 RP 业务通过。一般项直接阅读返回的业务回复与产物。RP-03、RP-04、RP-05 使用固定夹具的 `configs/codex-eval-adapter-contract.json`，契约编号 `skills-test-fixtures/codex-eval-adapter@21`，以及它已有的解析入口；在正式请求保存后执行：

```bash
UV_CACHE_DIR="$RP_PREP/uv-cache" uv run \
  "$RP_FIXTURES/scripts/parse_codex_eval_evidence.py" \
  --contract "$RP_FIXTURES/configs/codex-eval-adapter-contract.json" \
  --eval-response "$RP_REQUEST_DIR/response.json" \
  --output "$RP_REQUEST_DIR/evidence.json"
jq '{adapter_contract_id, problems, delegation,
     relations: [.dispatch.thread_relations[]? |
       select(.tool == "spawnAgent") |
       {sender_thread_id, receiver_thread_ids, call_id, runtime_seq, status}]}' \
  "$RP_REQUEST_DIR/evidence.json"
```

这一步列出本次请求已有的创建关系，供定位本项阶段，不启用完整调用树、MCP 或命名角色认证选项。`sender_thread_id` 是调用方，`receiver_thread_ids` 是实际子线程，`call_id` 连接对应调用，`runtime_seq` 指向响应中已有事件顺序。原阶段角色与本项操作要结合该次结构化调用参数、返回结果和正式阶段产物核对；提示文字出现名称不构成委派证据。执行者将本项相关阶段的实际子线程编号写入 `RP_RELATED_THREAD_IDS`，值为 JSON 字符串数组；不填猜测编号。只读取这些线程的现有生命周期片段：

```bash
jq --argjson related "$RP_RELATED_THREAD_IDS" '
  .output.app_server_events[]? |
  . as $event | .message.params as $params |
  select(.message.method == "item/started" or
         .message.method == "item/completed") |
  select($params.item.type == "subAgentActivity" or
         $params.item.type == "collabAgentToolCall") |
  select((($related | index($params.item.agentThreadId)) != null) or
         any($params.item.receiverThreadIds[]?;
             . as $child | ($related | index($child)) != null)) |
  {runtime_generation, runtime_seq, method: .message.method,
   parent_thread_id: $params.threadId, item: $params.item}' \
  "$RP_REQUEST_DIR/response.json"
```

仅在同一 `runtime_generation` 内按 `runtime_seq` 比较相关调用的顺序；连续请求先后以各自保存的请求与响应及实际产品状态连接，不跨请求比较序号。RP-03 只核对需要补候选时的第三阶段委派与候选；RP-04 核对采集、预筛及阶段 0—3 与目标、快照、输入包、候选；RP-05 核对补齐前置条件后才交第二阶段复用判断，并得到最终输入包。`dispatch.thread_relations[].status=completed` 仅表示创建关系事件结束，不能当作子代理业务结束；完成与收尾依原必测项的真实阶段产物和已有生命周期或结果事件判断。适配器的 `fixture_status`、`delegation.state` 均不是 RP 业务结论。字段缺失、相关阶段不能对应、先后无法观察或解析报错时，保留具体缺项并记无法判断，交测试负责人处理，不补造证据、重采样或新增采集设施。

### 普通组件测试与实际输入绑定

测试直接导入执行计划规定的 `research_proposal.api`，由正式 Nix 运行包的 Python 提供产品模块；没有开发模块回退、缺模块跳过或空断言。`test/support.py` 只提供普通文件读取和用例目录安排，不实现产品行为。`test/fixtures/` 共 26 个文件，含 25 项输入和一份 README；其中 `revisions/baseline.json` 是原短 Word 样本的 Pandoc AST 输入，不是成稿或新场景。

RP-04 完成后，把真实路径写入 `RP_INPUT_CASES` 指向的 JSON 文件。`complete.paths` 按专攻目录、教授研究目录、单教授目录、正式输入包四种入口排列；`application_root`、`professor_path`、`selection.professor_path`、`selection.direction_id`、`input_file`、`candidate_file` 都取这次真实结果。`without_candidates` 记录只移除候选后的有效资料副本，包含 `path` 及同名归属、选择、输入包、候选路径字段；其中 `candidate_file` 仍记被移除文件的原路径。副本中的其他正式产物仍须经原检查认可，不改写上游完成状态。以下 JSON 仅是测试输入绑定，不进入产品状态：

```json
{
  "complete": {
    "paths": ["实际专攻目录", "实际教授研究目录", "实际单教授目录", "实际输入包文件"],
    "application_root": "实际专攻目录",
    "professor_path": "实际单教授目录",
    "selection": {"professor_path": "实际单教授目录", "direction_id": "真实已选方向编号"},
    "input_file": "实际有效输入包文件",
    "candidate_file": "实际有效候选文件"
  },
  "without_candidates": {
    "path": "缺候选副本中的教授目录",
    "application_root": "副本中的专攻目录",
    "professor_path": "副本中的教授目录",
    "selection": {"professor_path": "副本中的教授目录", "direction_id": "相同真实方向编号"},
    "input_file": "副本中的有效输入包文件",
    "candidate_file": "副本中已移除候选的原路径"
  }
}
```

RP-08 完成后，将本轮隔离运行目录中的真实稿件目录绑定为 `RP_TEST_PROPOSAL`。RP-09、RP-11 串行独占它：每个普通用例先保存原目录快照，在原路径调用组件，结束后保存本次结果并恢复原目录，保持状态中绝对路径有效；不复制到新路径后手改确认或摘要。快照与结果放在 `RP_TEST_OUTPUT`，仅属于本轮原始输出。不得指向生产申请资料，不与实际改稿会话并行。

从 RP-08 当前提交的 `works[current.revision_id]`、其步骤指向的实际保存件和 `正文.json`，用 `jq` 读取真实材料记录、问题及方案确认、条件、正文与引用，整理为公开 `save_revision` 的四份 `data` 输入 JSON，分别绑定 `RP_MATERIAL_DATA`、`RP_QUESTION_DATA`、`RP_SCHEME_DATA`、`RP_BODY_DATA`。问题数据保留 `question_id/text/confirmation`，方案数据保留 `scheme/conditions/confirmation`，正文数据保留 `body/references`，材料数据沿用已保存的材料记录。不补写决定、完成状态或摘要；测试经 API 建立新工作版。自然保留的有效请求也可用 `jq '.data'` 提取，但不要求逐调用取证或产品新增请求日志。下式只组合数据，实际调用时使用新的修订编号与当前计数：

```bash
export RP_TEST_OUTPUT="$RP_RUN/component-output"
mkdir -p "$RP_TEST_OUTPUT"
export RP_SAVE_REQUESTS="$RP_RUN/config/save-requests.json"
jq -n --slurpfile materials "$RP_MATERIAL_DATA" \
  --slurpfile question "$RP_QUESTION_DATA" \
  --slurpfile scheme "$RP_SCHEME_DATA" \
  --slurpfile body "$RP_BODY_DATA" \
  '{materials: {data: $materials[0]}, question: {data: $question[0]},
    scheme: {data: $scheme[0]}, body: {data: $body[0]}}' \
  > "$RP_SAVE_REQUESTS"
```

RP-09 的 `RP_TEMPLATE_MAPPING` 指向按实际正文填写的映射数组。先用 `jq '.blocks | to_entries'` 读取当前 `正文.json` 的顶层块；按学校七个栏目为每项选择完整正文块，记录 `{field, target, body_blocks}`。合成 Word 模板没有独立表头，表格索引为 0，填写列为 1，栏目所在行依次为 0—6；不能把整篇正文塞进单一栏目。转填场景复用相同栏目与块索引，组件测试将 `target` 改为 `null`。映射文件只描述学校栏目位置，不改变已确认正文。

RP-11 的材料变化分支选用 RP-08 非论文稿正文确实采用的一份文字原文，将其在 `RP_RUN` 内的隔离输入副本路径绑定为 `RP_RELATED_MATERIAL`；本轮已有的 `rashomon.html` 可直接使用，不限于 UTF-8 文本。以已保存引用及材料编号确认关联，且该路径须在本稿 `inputs.material_paths` 中。测试先保留原字节，在同一路径临时替换为有效 ASCII 正文：HTML 用完整的 `html/body` 文本，TXT、Markdown 用一段文本，使实际引用内容发生变化；在 `finally` 恢复原字节和编码。不新增无关文件，也不修改下载原件或生产资料。

按依赖顺序分别执行下面的普通测试命令；相关变量均导出给对应测试进程。缺绑定会报错，不记为跳过或通过。只需运行对应类，不做全仓收集或重复回归：

```bash
export RP_RUN RP_TEST_PROPOSAL RP_INPUT_CASES RP_TEMPLATE_MAPPING RP_SAVE_REQUESTS RP_RELATED_MATERIAL
cd "$RP_WORKTREE/test"
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v \
  test_inputs.MaterialTests > "$RP_RUN/logs/rp06-components.log" 2>&1
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v \
  test_inputs.DiscoveryTests > "$RP_RUN/logs/rp03-components.log" 2>&1
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v \
  test_inputs.RevisionImportTests > "$RP_RUN/logs/rp10-components.log" 2>&1
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v \
  test_export.TemplateTests > "$RP_RUN/logs/rp09-components.log" 2>&1
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v \
  test_recovery.RecoveryTests > "$RP_RUN/logs/rp11-components.log" 2>&1
```

RP-09 的自动断言检查原件、栏目填写、产物和未切换当前稿；执行者仍直接阅读本次 `after/` 中 Word、Markdown 和全部页图，核对对应正文及转填说明。RP-11 仅在已批准的失败分支控制 `page_review` 返回：`true` 用于进入状态提交边界，`false` 用于页面核对失败。它明确不表示真实页面合格，也不作为 RP-08、RP-09 的结果；正文、确认和导出仍来自真实基准及产品组件。单格式失败由目标文件位置的目录冲突触发，状态中断由公开 `os.replace` 边界触发，不要求实现私有 helper 或特定 subprocess 调用形式。

`MaterialTests` 将 TXT、Markdown、HTML、EPUB 四类的原生结果保存为各用例输出目录中的 `<扩展名>-reading.json`，标准日志打印路径。执行者用 `jq '.material.blocks'` 读取选定片段和实际 `locator`，按它回到本次保留的原件，完成以下四处直接对照；PDF、Word 直接采用自动定位断言，不重复人工证明。这属于 RP-06 原定检查，自动测试成功不单独表示 RP-06 通过。

| 载体及选定片段 | 原件中应能回到的位置 |
|---|---|
| TXT：“十二人” | 第一章开放记录中的周二句，原文件第 5 行。 |
| Markdown：“书籍可以外借” | 借阅规则下首段，原文件第 7 行。 |
| HTML：“雨天仍开放” | `opening` 内的 `p2`。 |
| EPUB：“书籍二十四册” | `EPUB/chapter.xhtml` 的 `chapter-one` 内 `p2`。 |
| PDF：“期刊” | 物理第 2 页；直接采用普通测试的页码断言，不重复人工定位。 |
| Word：“24” | 首表第 2 行第 2 列，即零起始 `table=0,row=1,column=1`；直接采用普通测试按返回坐标读回原件的断言，不重复人工定位。 |

章节、段落、行的等价表达均可，但对应位置必须含有该片段；把所有定位写成 1、指向错误网页片段或错误表格单元格都不通过。只检查上述既有片段，不逐块重放或新增定位判定程序；扫描图另按下列原定步骤检查。

RP-06 扫描图采用真实产品读取入口，独立于文字载体普通测试；先复制样本，再用 `jq` 构造公开请求：

```bash
cp "$RP_WORKTREE/test/fixtures/materials/damaged-scan.png" "$RP_CONSUMER/input/damaged-scan.png"
jq -n --arg path "$RP_CONSUMER/input/damaged-scan.png" \
  --arg output "$RP_CONSUMER/input/scan-reading" \
  '{path: $path, material_type: "合成史料扫描图", source: "残损扫描测试输入", output_dir: $output}' \
  > "$RP_RUN/config/read-scan.json"
RP_SCAN_EXIT=0
VISION_ENV_FILE="$RP_VISION_CONFIG" \
  "$RP_RUNTIME/bin/proposal-runtime" read_material --request "$RP_RUN/config/read-scan.json" \
  > "$RP_RUN/logs/rp06-scan.json" 2> "$RP_RUN/logs/rp06-scan.stderr" \
  || RP_SCAN_EXIT=$?
printf '%s\n' "$RP_SCAN_EXIT" > "$RP_RUN/logs/rp06-scan.exit"
if [ "$RP_SCAN_EXIT" -ne 0 ] && [ "$RP_SCAN_EXIT" -ne 2 ]; then
  exit "$RP_SCAN_EXIT"
fi
jq '{status, issues, material: {material_id: .material.material_id,
    blocks: .material.blocks, issues: .material.issues}}' "$RP_RUN/logs/rp06-scan.json"
```

对照原图阅读解析后的文字、像素定位和缺项；缺损数量没有标准答案，不能补成确定数字，图形解释不得混入逐字转录。业务缺项的退出 2 按实际字段和原图判断，不按退出码一项认定失败。该命令属于正式 RP-06，准备阶段未运行。

### 各项输入与具体安排

| 编号 | 准备与执行安排 |
|---|---|
| RP-01 | 使用前述 Nix 目录及无关安装输入，执行四输出构建和共享缓存激活，检查资源、六项直接依赖、原代理及保留项；实际功能引用 RP-04、RP-06、RP-08。 |
| RP-02 | 用固定 skills@1.7.2 从同一发布提交在另一目录安装，检查发现结果、随附资源和资源引用，阅读文档的环境边界；不运行完整前置流程。 |
| RP-03 | 从 RP-04 的真实产物做隔离副本，以专攻目录、教授研究目录、单教授目录、正式产物四种路径分别输入组件；输入包及候选俱全的副本保持原样，只缺候选的副本仅移除该候选产物。另保留两个有效可选方向或教授，在实际交互先不选择，待真实选项出现后作决定；已有明确决定的分支继续采用它。若 RP-04 不足两个有效选项，补齐第二份真实上游材料，不能手造状态。运行 DiscoveryTests；真实用户选择和第三阶段委派仍由既有 eval 交互检查。 |
| RP-04 | 采用准备好的 2027 招生目录和官方教员、研究者来源，初始目录没有教授研究产物。实际交互按原提示提供所需教授、方向和访问决定，保留原命名代理的工作安排。只有原流程真正完成目标、快照、输入包及候选后，才把该目录作为后续基准；不得提前标完成。 |
| RP-05 | 在 RP-04 成果的独立副本中保留论文分析及事实文件，移除该副本的正式输入包、目标文件和原流程记录的第一阶段快照。删除范围只能在该副本内。通过主技能继续，观察原流程补齐目标与快照、第二阶段复用判断及最终结果；不修改缓存校验器。 |
| RP-06 | 普通组件测试使用 `materials/` 六类文字载体及未支持文件；定位与原文对照见输入说明。第七类扫描 PNG 使用上述正式读取命令及视觉配置，按原图核对实际结果。实际候选交互使用 `input/nonpaper/` 中真实《罗生门》作品，首次不指定问题，待候选出现后选择；载体合成记录不当成现实研究证据。 |
| RP-07 | 在已选问题上提供真实相关研究文件；先给出未定位私人手稿且没有备选的条件，观察缺项和稿件状态。补充官方阅览条件后，用户可以明确将已定位公开版本改为主材料，特殊阅览仅作可选补充；若所选问题仍必须依赖未取得途径的私人材料，保持受阻，不把一般申请规则当成具体材料存在证明。方案条件成立后先观察尚未确认的中文方案和稿件状态，再取得用户对该版的真实确认；两处确认和不得提前成稿的检查沿用上表。 |
| RP-08 | 论文路线复用 RP-04、RP-07，采用甲项目日文要求；非论文路线复用 RP-06、RP-07，采用甲项目中文要求。个人资料只取 `applicant.md` 的合成事实。每条路线完成一稿，直接读双格式、待确认事项、输入状态和产品页面预览；不再从头采集材料。 |
| RP-09 | 复用 RP-08 同一已确认正文，运行 TemplateTests 分别给出可填写 Word 与转填 PDF，然后直接检查本次输出的填写区、全部页图、Markdown 及转填说明。另通过主技能读取真实 research-plan-cover-2027.pdf 的空白表要求；不把真实封面与合成学校栏目混为一份要求。 |
| RP-10 | RevisionImportTests 用 revisions/ 短样本检查内容和标记。实际交互从 RP-08 稿件副本制作对应修改：纯措辞、明确要求修改核心方法并改成英文、文件内把未核实条件改为已获得但未解释意图、两份核心方法冲突且未选定的稿件。先保存原件与基准，由用户对未决修订作决定，批注不直接作为正文。实际编辑位置取已交付稿件对应段落，不把短样本冒充它。 |
| RP-11 | 运行 RecoveryTests，覆盖两种单格式失败及首次无当前稿、内容不一致、受控页面核对失败、材料/方案/正文保存中断、目录已完成而未切换、切换后中断、四类恢复输入变化、另一轮先更新基准。只使用正式 API、文件条件和公开 os.replace 边界；保存旧稿与每例工作结果，直接读状态及内容。正常完整成稿引用 RP-08，受控页面结果不能作真实页面通过证据。 |
| RP-12 | 沿 RP-08 稿件继续，提出以同题用于乙项目的明确请求，提供 `program-b.md` 并明确复用文献与通用方案。操作前后只比较第一稿输入、状态、正文及已有其他教授状态，检查新稿绑定和栏目变化，不重验全部写作。 |
| RP-13 | 空输入使用准备的空目录；学校名称输入使用 `school-name-only.txt`。外部能力失败只选扫描视觉配置缺项：在已保存进度的副本上，按产品入口指向 `vision-missing.env`，检查缺项及保存结果。恢复原 `vision.env` 后续接对应 RP-06 的正常步骤，不制造第二种外部故障或重跑完整流程。 |

### 外部故障、输出与清理

正式尝试最多两次，即首次加一次有依据的外部恢复后重试。可重试的原因只包括明确发生在业务动作之前的临时网络失败，或已确认恢复的服务不可达；产品版本、输入、用户决定、模型、配置、入口与超时保持不变。额度不足、权限拒绝、已知配置缺失、线程失败或观察字段缺失没有恢复证据时停止，不能连续完整采样。改变任何上述条件属于步骤修订，不算同条件重试。

请求超时或返回 `termination_uncertain` 时，不启动第二份等价工作。先按现有服务状态与已保存产品状态确认上轮已停止及副作用；无法确认时保持无法判断并交执行负责人。已确认的业务失败不因网络、记录或清理错误被覆盖。新的用户决定是连续业务输入，不是重试；只提交当次真实决定，沿用先前有效成果。

每次请求的请求文件、响应、HTTP 状态和必需业务产物都保存在自己的目录，前次不得覆盖。只有 RP-03 至 RP-05 留存所需相关调用片段，其余不额外保存全环境快照或逐调用账本。敏感配置仅在本轮受控目录，公开记录只写必要结论。

Chrome、Zotero 在真正需要时按固定夹具启动入口分配独占状态，记录其返回的 `fixture.env`；结束后只用同一入口的 `stop <fixture.env>` 清理本轮实例，不按程序名称停止进程。配置准备目录只用现有 `prepare_codex_project_config.py --cleanup-run-dir` 清理带归属标记的本轮目录。测试结果交接前保留输入、失败尝试和必要输出；清理失败单列，不覆盖业务结论。评估服务不属于本轮可清理对象。

### 执行时绑定及依赖顺序

| 项目 | 已准备的安排与执行时绑定值 | 下一负责人 |
|---|---|---|
| D1 | 四输出、共享激活与固定 npx 命令已写明。RP_REPOSITORY、RP_REVISION 由产品发布交接绑定；RP_RUN 与两个消费者目录由上述 mktemp/mkdir 命令生成。 | 产品负责人交付实现；执行工程师绑定后运行 RP-01、RP-02。 |
| D2 | 九个公开操作及数据约定来自已批准执行计划 r3；普通测试已经按该契约编写。RP_RUNTIME 由 RP-01 构建输出绑定；缺产品模块时不得改用开发代码或跳过。 | 执行工程师在实现交付后按各类命令运行；不一致按实际事实归属产品或测试问题。 |
| D3 | 固定服务键、环境传递、配置合成和请求生成步骤已写明。动态端点取本轮 fixture.env，评估端口与已有程序位置取现有 direnv 配置。RP_THREAD_BUDGET 按本请求固定上游处理范围及累计创建数，在请求开始前绑定。最终消费者配置在正式安装后按给定表达式生成。 | 执行工程师绑定本轮值；外部访问故障交环境负责人。 |
| D4 | RP-04 生成真实输入包、候选、快照、有效分析和选择范围；随后绑定 RP_INPUT_CASES。RP-08 生成真实成稿、决定和步骤保存件；随后绑定 RP_TEST_PROPOSAL、RP_SAVE_REQUESTS、RP_TEMPLATE_MAPPING、RP_RELATED_MATERIAL，并派生 RP-10、RP-12 输入。 | 正式执行工程师按顺序产生并保留，测试准备阶段不代跑、不伪造。 |

本轮有限预检只确认：苹果芯片架构；`uv`、`jq`、`yq`、`xmllint`、Nix、Node/npm 可用；固定夹具及默认配置可读；共享资产重建成功；视觉必需配置值存在；小型载体、模板及修改稿已经生成且 ZIP/XML 结构和页面可检查。样本渲染使用现有文档工具随附的 LibreOfficeDev 26.8，不是产品计划要求的 LibreOffice 26.2.4 构建结果；作者环境 Pandoc 3.1.11.1 也不替代产品固定 3.7.0.2。没有把这些预检当作 RP-01、RP-06、RP-09 或 RP-10 的通过结果。

## 结果、复验与交接

正式执行时，每个编号及其必需场景仅记录实际产品版本、命令、通过／业务失败／无法判断／未执行、必要结果位置和简短说明。标准测试报告和直接阅读结果即可，不要求统一 JSON 或独立证据系统。JSON 或 XML 结果需要读取时按项目指定解析器检查相关字段，不靠文本关键词猜测。

失败归属按事实处理：目标或检查方式有缺口由测试计划工程师补齐；执行步骤未落实交本地测试工程师；执行偏离交执行工程师；产品错误交产品负责人；外部访问或服务故障在无产品错误依据时记为无法判断。不得用后续清理、记录或网络错误覆盖已确认的业务失败。

修改后只复核受影响的目标和步骤，未受影响的有效结果直接引用。文档调整、提交编号变化或审核偏好不自动触发完整重跑。只有本清单全部必要场景取得当前有效通过结果，且范围内已发现业务缺陷处理完成，才能申请第三关；本计划文件和计划审核通过均不表示产品测试已通过。

下一负责人：主对话负责第二关审核；第二关通过且产品按计划交付后，本地执行工程师绑定实际值，按适用步骤执行。产品尚未实现不单独构成 Recipe 不完整。
