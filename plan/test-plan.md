# 研究计划草稿技能测试计划

日期：2026 年 11 月 3 日。

## 版本与范围

- 测试计划版本：`rp-tests-r4-repository-scope-2026-11-03`。
- 需求版本：`rp-requirements-2026-11-02-q6-q16`；测试范围采用用户 2026 年 11 月 3 日的新决定：“只测 research-proposal 的逻辑，recipe 应该手动准备输入”。产品功能要求不变。
- 执行计划：[implementation-plan.md](implementation-plan.md)，版本 `rp-plan-r3-2026-11-03`，校验值 `edf6692023be0e717ff454482c10763cc74c42885cc41ea8458fd1915fb69bcf`；批准依据见 [implementation-plan-review.md](implementation-plan-review.md)。
- 目标仓库：`research-proposal`；工作树：`worktrees/research-proposal-plan`；分支：`feat/research-proposal`。首个正式产品为 `4797a1bd69dca2a1354476a564c5d2714d8004da`；当前产品和执行状态由执行工程师维护于 `plan/test-results.md`。
- 执行说明版本：`rp-recipe-r13-input-fixtures-2026-11-03`。本次修订替代 r3 业务清单及 r12 的现行执行义务；历史尝试、发现的实际问题和不受影响的通过结果保留。独立设计复核、第一关及第二关结论见 `plan/test-plan-review.md`，准备符合性结论见 `plan/test-preparation-review.md`；准备完成不表示正式测试通过。

范围来自已确认的业务要求和执行计划明确安排的成功、失败及兼容行为。首版完整流程只验收苹果芯片 Mac、Codex、Nix；npx skills 验收技能与随附资源的安装，不把它单独视为完整前置环境。

下面 RP-01 至 RP-13 及各项明确列出的场景构成唯一必测清单。只验收本仓库的安装交付、输入发现与交接安排、材料整理、研究设计、成稿、修改和恢复。上游产物由 Recipe 手动准备为输入；不运行采集、Zotero 保存、全文下载、论文分析或套磁候选生成来证明这些输入的生成过程，也不验收上游子代理、服务、批次或委派链。已有上游检查随产品发现入口正常使用，不为本次测试重写或绕过它们。

每项按自己的观察点判断，不因某项安排了实际会话，就重新检查其他项已经覆盖的全部行为。不追加所有学科、学校、语言、文件格式的组合，不测试其他平台或运行工具，不重新验收共享安装器或模型服务。RP-04、RP-05 不再是 RP-07、RP-08 的前置运行；本次手工准备的是外部输入，不是 research-proposal 的成功输出或用户确认。

## 必测清单

### RP-01：Nix 安装交付

**目标**：一次安装提供主技能、声明的直接依赖、原代理及固定运行程序，正确交付本仓库功能所需的安装内容。

**输入或场景**：在约定平台，从固定产品提交安装到仓库和开发工作树之外的干净使用目录。该目录含一份无关的示例技能和一项无关配置，供检查保留行为；不使用用户真实配置。

**预期结果**：正式安装所需的固定构建输出实际构建成功；安装后的主技能及随附资源完整，六项直接依赖和原代理按声明安装并可定位，不要求另跑 APM，不依赖开发目录的文件。安装保留无关示例技能与配置。安装说明准确区分代码安装与模型、Zotero、浏览器及视觉服务的外部条件。

**检查方式**：检查实际构建和安装结果、安装目录及相关配置条目；本仓库运行入口的实际使用采用 RP-06 的材料读取和 RP-08 的成稿结果，不另跑一套相同流程。依赖交付检查到声明、安装位置和资源引用，不要求启动 Zotero、浏览器或上游代理证明其内部功能。共享层已有适用结果直接引用，不新增安装冲突矩阵或通用运行时认证。

### RP-02：npx skills 安装入口

**目标**：用户能通过另一安装入口取得同一主技能及随附资源，知道仍需哪些运行条件。

**输入或场景**：在另一个隔离使用目录，从同一产品提交执行仓库公开说明的 npx skills 安装方式。

**预期结果**：主技能可以被发现，正文、脚本、参考资料和模板均可在安装位置访问；资源引用不依赖开发目录或另跑 APM。文档明确此入口不单独提供上游代理和工具服务，不承诺未经验证的平台组合。

**检查方式**：直接检查安装结果、技能发现结果及本技能引用的资源路径，并阅读该入口的说明。本项不重复 Nix 完整流程，也不要求为 npx skills 另造代理安装能力。

### RP-03：已有材料发现与复用

**目标**：用户给定路径后自动找到适用材料，并沿用有效成果及真实选择。

**输入或场景**：Recipe 手动准备一份符合固定上游格式、内容及引用对应的资料，分别以专攻目录、`教授研究` 目录、单个教授目录和具体正式产物路径进入输入发现组件；另有两个可选教授或方向而用户未指定的资料。已有产物包含两种状态：有效输入包及候选均齐全；有效输入包齐全但缺候选。

**预期结果**：四类路径均对应正确的申请项目、教授和已有进度；对象未明确时提供选择，收到已有明确选择时沿用。输入包和候选均有效时返回 `proposal`；只缺候选时返回 `stage3`。不会因存在 Markdown 报告就伪造正式上游状态，也不把套磁选择自动认作研究计划已确认的全部选题。

**检查方式**：采用产品输入发现组件的常规自动测试，检查四种入口、返回对象、已有选择、未选择时的需求及 `next_step`。有效性由发现入口调用既有上游检查；不另行认证检查器。第三阶段的交接说明统一在 RP-04 静态核对，不实际生成候选。研究计划自身的选题确认由 RP-07 检查。

### RP-04：识别缺少的上游步骤并安排交接

**目标**：资料未齐时，research-proposal 识别应交给哪个上游步骤，并提供与其职责一致的交接说明。

**输入或场景**：Recipe 准备合格招生项目、缺预筛、缺目标、缺第一阶段快照、缺输入包和缺候选的对应小型输入副本。每份输入在调用前就固定已有内容及预期下一步，不在用例中调用上游采集、下载、分析或候选生成。

**预期结果**：发现结果分别指向适用的 `collect`、`preview`、`stage0`、`stage1`、`stage2`、`stage3`，不把缺少材料误当成 `proposal`。主技能及引用文件使用原命名代理和既定业务参数，要求等待、消费返回结果后重新发现；定向补全文交第一阶段，第三阶段的调用方收尾按原约定安排，不进入邮件阶段。这里检查的是本仓库的分支与交接安排，不要求原代理完成业务。

**检查方式**：普通自动测试调用产品 `discover`，检查对应副本的 `next_step`；缺候选的 `stage3` 分支直接采用 RP-03 的同一次检查，不重复执行。准确代理名称、参数来源、等待与消费、第三阶段调用方收尾由直接阅读本仓库技能及引用文件核对。两种检查分别覆盖可执行组件和提示文本，不新建模拟代理或委派观察设施，不发送会运行上游代理的评估请求。完整输入另由 Recipe 准备，供 RP-07、RP-08 使用。

### RP-05：零散论文分析的前置顺序

**目标**：已有分析但缺正式输入包时，research-proposal 不跳过目标和第一阶段快照直接交第二阶段。

**输入或场景**：Recipe 手动准备相互对应的论文分析及事实文件。三个输入副本分别缺目标和第一阶段快照、只有有效目标、目标与快照齐全但缺输入包；适用预筛按场景备齐。

**预期结果**：三个副本依次交阶段 0、阶段 1、阶段 2；未满足前置时不直接返回阶段 2、阶段 3 或 `proposal`。本仓库保留分析和事实文件供原负责代理采用，不自行声明其已通过上游身份、来源或缓存检查。

**检查方式**：普通自动测试对准备好的三个副本调用 `discover`，检查实际分析归属、材料发现及下一步。每个副本是独立的测试输入，不冒充前一用例生成的产物；不运行上游代理、论文分析或缓存复用业务。

### RP-06：非论文材料读取、定位和候选

**目标**：专著、史料或作品材料按实际载体读入，并能支持可追溯的候选研究问题。

**输入或场景**：一组小型、有权使用的材料，包含文字 PDF、扫描页或图片、TXT、Markdown、EPUB、HTML 和 Word；每种载体只需一个能体现其定位方式的样本。扫描样本含一处确实无法辨认的文字，另有一个不在支持范围内的文件。随后将其中相关材料交给主技能，不预先给定研究问题。

**预期结果**：读取内容与原材料相符；出处、页或段落、表格或区域等定位可回到相应原文。无稳定分页的 Word 不编造页码；识别不明处保留缺项，图像解释与逐字转录分开，不支持的文件明确报告需要转换。技能提出少量有材料依据、方法和缺项说明的候选，等待用户选择；这一路线不强制产生套磁候选文件或套用“作者后续工作”。

**检查方式**：载体读取及定位使用材料组件的常规自动测试并直接对照样本，扫描识别采用已安装视觉入口的实际结果；实际会话只检查候选形成和用户选择，不重新逐项验收解析器。文字识别不以逐字零误差或固定置信度作为新增通过条件，疑难部分须被如实保留。

### RP-07：相关研究、条件判断与中文方案

**目标**：将已选问题转成有证据且可以开展的方案，并落实两处用户决定。

**输入或场景**：论文路线直接使用 Recipe 准备的有效上游输入包、候选及可核对原文；非论文路线复用 RP-06 的材料与候选。由主技能展示研究问题后取得合成申请者的实际选择，再使用事先选定、可读取的相关来源；包含教授之外的研究、需要分辨的矛盾结论和一个有待核实的关键材料取得条件。条件先无可靠取得途径，再补充可核实的申请条件和备用办法，但不声称资源已经取得。条件补齐后，围绕同一稿件先查看尚未确认的中文方案，再针对实际方案给出用户确认；已有有效确认的部分继续复用。不以 RP-04、RP-05 或上游实际运行成功作为开始条件。

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

用户已经明确授权 Recipe 手动准备上游输入。准备者可以按固定格式制作合成上游产物，也可采用已有保存件；提供对应原文、定位与预期场景，必要时使用原仓库既有的纯本地格式构造助手。合成材料及外部输入须明确标识，不宣称本轮已经完成采集、下载、分析或上游校验代理。未完成场景从这些输入副本移除指定产物。正式测试仍通过本仓库生产入口，正常采用已有格式检查；不改检查结果、不修改消费者受管代码，不预写 research-proposal 自己的问题确认、方案确认、正文或提交成功。材料载体样本只用于其声明的检查，不伪装成现实中已发表的研究证据。

每个目标选择表中规定的足够观察点。自动检查使用产品仓库的普通测试代码；实际会话使用安装后的主技能并从资料已齐全的位置开始。RP-03、RP-04、RP-05 检查发现结果和本仓库交接说明，不检查上游实际调用链；其他项以业务产物和用户可见行为判断。完整上游输入若不能被产品接受，先区分测试输入准备错误与本仓库发现逻辑错误，不因此转回从招生资料跑上游。

以下准备职责适用于本次范围修订；历史上已完成的安装、运行和结果保留，本次只重做受影响的输入与步骤：

1. 固定当前待测产品提交、依赖锁定图、配置版本和适用的已有结果。只改测试计划及输入不使原产品安装失效；复用现有有效安装与缓存，不因为上游测试被移出范围就重装产品。
2. 准备上述小型输入和必要测试代码，给出每项可直接执行的准备顺序、命令、实际输入与输出位置。对 RP-11 的受控失败，采用标准测试框架的现有能力；如果确实需要新的专用设施，先按测试规则申请明确范围，不能直接作为必测前置。
3. 产品安装来自固定提交的正式入口，使用仓库外的干净目录，隔离本次资料、稿件及必需服务的可写状态，不替换 `HOME` 或连接用户生产资料。RP-01、RP-02 已有仍适用安装结果直接复用。新范围不需要启动或探测 Zotero、浏览器，也不以它们可用作为准备条件；不因范围修订擅自清理原有进程。
4. 使用 `skills-test-fixtures` 前先更新其主分支并固定实际使用版本；依该版本的现有配置与准备方式安排环境。运行配置的路径、变量来源与加载方式由测试工程师写清，不转交用户猜测，也不复制产品代理或工具配置到夹具中补偿安装缺陷。
5. Codex 实际会话使用现有评估服务，按项目共识使用默认配置；在干净使用目录启动，命令携带该目录。具体请求及配置以准备时读取的服务文档为准，本计划不虚构尚未核对的接口参数，不自行启动、停止或重启评估服务。
6. 仅做命令可运行、必需依赖与配置可用、用户状态隔离的预检。临时配置、预检输出与原始结果放在仓库外独立临时目录，正式测试代码留在产品仓库；不新增环境来源认证或全环境快照。
7. 在执行说明中写明可重试的外部故障、最多尝试次数、停止条件、需要重置的状态和保持不变的输入配置。已确认业务失败不因结果不满意而重跑；环境未恢复时不连续重复完整运行。所有正式尝试保留。

以上是准备职责。下文为唯一现行执行说明；旧步骤只保留在 Git 历史和历史结果中，不再要求执行者拼接旧续跑方案。第二关核对步骤与本仓库公开接口及本次范围是否一致，不要求准备角色提前运行产品或正式用例。

## 执行说明

### 当前版本与复用范围

本节版本为 `rp-recipe-r13-input-fixtures-2026-11-03`，落实上面的 r4 业务范围，整段替代旧依赖链步骤。待测产品仍为 `b983497308157dedec6b4d97f16c95dc0b0f60f9`；其正式 Nix 安装位于既有消费者目录，继续复用，不因修改测试输入重装。固定共享夹具为 `5a31ae0095952cc359f7fa826730f14e7ee4f5b2`；主对话本轮已在干净主分支更新，退出 0、已是最新。

RP-01、RP-02 的适用安装结果、RP-06、RP-13 及未受影响的组件结果直接采用 `test-results.md` 当前记录。RP-01 的实际运行能力继续采用 RP-06、RP-08；RP-09 的空白招生表读取已经完成，不重复请求。旧上游运行、旧配置故障及本仓库实际业务失败保留原样。RP-03 至 RP-05 按本节新方法正式执行后才能更新结果；手工材料准备及配置检查均不表示业务通过。

本次仍使用固定夹具的 `gpt-6-luna`、`low` 默认值。此前放在临时目录的其他模型候选没有获批，不能加载。不会启动、停止或探测 Zotero、浏览器或评估服务，也不要求任何上游采集、下载、分析、校验或候选生成业务完成。

### 运行目录与安装入口

资料根与结果根分开：`RP_CONSUMER` 是现有正式安装及真实稿件所在目录；`RP_RUN` 只保存本次日志、配置、请求和组件输出。未提交状态可能含绝对路径，因此保持消费者和原稿位置，不复制状态后手改路径。

第二关通过后由执行者设置以下绑定。既有 `run.env` 仅含路径和版本；视觉秘密仍只通过配置文件路径引用，不输出内容。

```bash
set -e
: "${RP_CONTINUATION_ENV:?采用本轮本地交接的 continuation.env 绝对路径}"
source "$RP_CONTINUATION_ENV"
source "$RP_PREP/config/runtime-locations.env"
export RP_WORKTREE RP_PREP RP_FIXTURES RP_EVAL_DIRECTORY RP_RUNTIME RP_CONSUMER
export RP_INSTALLED_CONFIG
RP_RUN="$(mktemp -d /private/tmp/research-proposal-r13-run.XXXXXX)"
export RP_RUN
mkdir -p "$RP_RUN/config" "$RP_RUN/logs" "$RP_RUN/requests" "$RP_RUN/component-output"
export RP_TEST_OUTPUT="$RP_RUN/component-output"
```

`continuation.env` 已在本轮独占准备目录写明既有产品运行包、消费者、准备根、工作树及原安装快照的准确路径，并加载同目录 `zotero-isolation.env` 导出从旧消费者正常配置保留的两个隔离端点；位置随本地交接提供，不把机器部署路径写入公共仓库。正式测试从该 Nix 运行包导入模块，不从开发源码补依赖。旧结果根不被本次输出覆盖。

RP-01 的正式入口仍是 README 中四个输出：`research-proposal-runtime`、`research-proposal`、`research-proposal-environment`、`research-proposal-activate`。已有有效结果直接引用；若产品变更确实影响安装，另由执行负责人绑定新提交并在空消费者执行下面原入口，不能把当前含稿件目录当成空安装：

```bash
# 仅用于经实际影响确定需要的新安装；当前 b983 安装不执行本段。
RP_REF="github:ScholarWorkflow/research-proposal/$RP_REVISION"
nix build "$RP_REF#research-proposal-runtime" --out-link "$RP_INSTALL/runtime"
nix build "$RP_REF#research-proposal" --out-link "$RP_INSTALL/package"
nix build "$RP_REF#research-proposal-environment" --out-link "$RP_INSTALL/environment"
nix build "$RP_REF#research-proposal-activate" --out-link "$RP_INSTALL/activate"
"$RP_INSTALL/activate/bin/research-proposal-activate" --project "$RP_CONSUMER"
```

缓存激活与 `"$RP_INSTALL/environment/bin/agent-env" apply --project "$RP_CONSUMER"` 二选一，不能要求重复激活。首次安装前预置 `test/fixtures/install/.agents/skills/unrelated-note` 及 `test/fixtures/install/.codex/config.toml` 无关配置，安装后按 RP-01 检查保留、声明的六项依赖、原代理及本技能资源；不启动依赖业务。RP-02 在另一干净目录使用 `npx --yes skills@1.7.2 add "https://github.com/ScholarWorkflow/research-proposal/tree/$RP_REVISION/skills/research-proposal" --skill research-proposal --agent codex --copy --yes`，检查主技能及引用资源。当前这两项的适用既有结果不重跑。

### 手动准备上游输入

正式输入源位于 `test/fixtures/upstream/`：合成作品《门灯》、林安和周岚两篇合成研究、招生信息、初始材料条件及补充条件。每份都标明合成身份；作品 P1—P6、研究 A1—A4/B1—B4 可以直接核对。个人准备和甲乙项目沿用 `test/fixtures/applications/`。合成论文不是现实出版物，也不声称上游已执行成功。

[test/prepare_inputs.py](../test/prepare_inputs.py) 是输入构造脚本，不导入或调用待测 API。它使用当前安装的固定上游 `contact_targets`、`contact_stage1` 的纯本地字典构造函数，保持目标和快照格式；其余给定输入按同版格式整理。候选中 `validator.results` 明确标为合成终态，不记录或证明真实校验代理历史。脚本不调用上游业务 CLI、不联网，不写 research-proposal 自己的确认、正文或提交状态。

第二关后在消费者内新建专用输入目录；不覆盖旧采集资料或非论文原稿。不能把生成后的目录搬到另一位置，因为输入引用使用绝对路径；需换位置时用同一脚本重新构造外部输入。

```bash
RP_INPUT_ROOT="$RP_CONSUMER/input/r13-manual-inputs"
test ! -e "$RP_INPUT_ROOT"
UV_CACHE_DIR="$RP_PREP/uv-cache" uv run --no-project python \
  "$RP_WORKTREE/test/prepare_inputs.py" \
  --output "$RP_INPUT_ROOT" \
  --contact-scripts "$RP_CONSUMER/.agents/skills/professor-contact/scripts" \
  > "$RP_RUN/logs/prepare-inputs.log" 2>&1
export RP_INPUT_CASES="$RP_INPUT_ROOT/cases.json"
jq '{complete, without_candidates, multiple, writing}' "$RP_INPUT_CASES"
```

输入清单按以下场景固定，缺项由脚本预先安排，不由用例中的上游运行补齐：

| 清单键 | 已有输入与下一步 |
|---|---|
| `complete` | 同一完整输入包、候选、原文；`paths` 为专攻、教授研究、单教授、正式输入包四种入口，预期 `proposal`。 |
| `without_candidates` | 有效输入包，缺候选，预期 `stage3`；同时作为 RP-04 的同一分支结果。 |
| `multiple` | 两位可选教授；林安有两个方向。先无选择，再仅选择教授，再给完整选择，检查需求及已有选择沿用。 |
| `collect`、`preview`、`stage0`、`stage1`、`stage2` | 分别只有合格招生项目、有论文但缺预筛、有预筛但缺目标、有目标但缺快照、目标及快照齐全但缺输入包。 |
| `analysis_stage0`、`analysis_stage1`、`analysis_stage2` | 每份含对应分析、事实和索引；分别缺目标及快照、只有目标、目标及快照齐全；以实际分析文件为入口。 |
| `writing` | 独立的完整包、候选、作品和两篇研究全文，加个人准备、甲项目和初始条件，直接供论文路线 RP-07、RP-08。补充条件留在该根以外的 `operator-inputs`，路径只记入执行者用清单的 `writing.access_supplement`。 |

`cases.json` 只绑定路径和预期对象，不是产品状态。原检查仍随产品 `discover` 正常运行；输入若不能接受，先由准备者修正具体格式错误或由产品负责人修发现逻辑，不改检查器返回，也不转回运行上游链。

### 唯一运行配置与实际请求

`test/config/consumer-runtime.yq` 是本轮唯一项目配置合成表达式，从 b983 的原安装快照出发。保留安装定义，设置本仓库实际会话所需的正常视觉文件、原有工作区联网、单主线程，以及关闭本范围不使用的两个 MCP 服务；保留旧消费者的 `ZOTERO_HTTP_URL`、`ZOTERO_MCP_URL` 隔离覆盖，防止意外误路由退回本机默认库。不读取 Zotero 进程状态，不启动或探测端点，不把连通性作为准备条件，也不重新引入 Zotero 业务测试；浏览器、知识库目录及嵌套代理配置不再作为绑定前提。`mcp_servers.<id>.enabled=false` 使用 [Codex 官方配置字段](https://learn.chatgpt.com/docs/config-file/config-reference)，只在本次隔离消费者中禁用该服务，安装定义及旧进程都保留。线程数 1 对应本节不启动上游子代理的实际请求，不作上游容量计算。模型、审批及 `sandbox_mode=workspace-write` 仍取固定默认与普通范例，不写 CLI 重复覆盖。

确认没有正在运行的请求或写入后，执行者保存原配置，再按单一表达式生成新文件；准备者的有限检查只在自己的临时目录进行，不修改消费者。

```bash
export RP_VISION_FILE="$RP_VISION_CONFIG"
RP_CONFIG_OUTPUT="$RP_RUN/config/consumer-config-r13.toml"
cp -p "$RP_CONSUMER/.codex/config.toml" "$RP_RUN/config/consumer-config.before.toml"
yq -p=toml -o=toml --from-file "$RP_WORKTREE/test/config/consumer-runtime.yq" \
  "$RP_INSTALLED_CONFIG" > "$RP_CONFIG_OUTPUT"
yq -p=toml -o=json '.' "$RP_CONFIG_OUTPUT" | jq -e '
  .agents.max_concurrent_threads_per_session == 1 and
  .sandbox_workspace_write.network_access == true and
  .mcp_servers["chrome-devtools"].enabled == false and
  .mcp_servers["personal-knowledge"].enabled == false and
  (.shell_environment_policy.set.ZOTERO_HTTP_URL | length > 0) and
  (.shell_environment_policy.set.ZOTERO_MCP_URL | length > 0) and
  .shell_environment_policy.set.ZOTERO_HTTP_URL == env.ZOTERO_HTTP_URL and
  .shell_environment_policy.set.ZOTERO_MCP_URL == env.ZOTERO_MCP_URL and
  (.shell_environment_policy.set.VISION_ENV_FILE | length > 0)'
cp "$RP_CONFIG_OUTPUT" "$RP_CONSUMER/.codex/config.toml.new"
mv "$RP_CONSUMER/.codex/config.toml.new" "$RP_CONSUMER/.codex/config.toml"
```

每个实际请求采用固定夹具的原入口。`RP_REQUEST_DIR` 是 `$RP_RUN/requests/` 下尚未存在的新目录，`RP_PROMPT` 是本次自然语言业务输入或阅读实际输出后作出的具体决定，`RP_TIMEOUT=600`。它们由执行者逐次绑定，不能在提示词里补产品工具名称、参数或保存步骤。下列命令只适用于需要实际会话的 RP-07 至 RP-10、RP-12；RP-03 至 RP-05 不发送评估请求。

```bash
RP_TIMEOUT=600
UV_CACHE_DIR="$RP_PREP/uv-cache" uv run \
  "$RP_FIXTURES/scripts/prepare_codex_project_config.py" \
  --defaults "$RP_FIXTURES/configs/codex-smoke-defaults.toml" \
  --recipe "$RP_FIXTURES/examples/codex/ordinary-smoke.toml" \
  --consumer-root "$RP_CONSUMER" --run-dir "$RP_REQUEST_DIR" \
  --prompt "$RP_PROMPT" --timeout "$RP_TIMEOUT"
jq '{loading_method, run_dir}' "$RP_REQUEST_DIR/preparation.json"
RP_EVAL_PORT="$(direnv exec "$RP_EVAL_DIRECTORY" sh -c 'printf %s "$EVAL_PORT"')"
curl --silent --show-error --max-time "$((RP_TIMEOUT + 30))" \
  --output "$RP_REQUEST_DIR/response.json" --write-out '%{http_code}\n' \
  --request POST "http://127.0.0.1:$RP_EVAL_PORT/eval" \
  --header 'Content-Type: application/json' \
  --data-binary @"$RP_REQUEST_DIR/eval-request.json" \
  > "$RP_REQUEST_DIR/http-status.txt"
jq '{passed, version, termination_reason: .output.termination_reason, error}' \
  "$RP_REQUEST_DIR/response.json"
```

准备器只把固定默认与普通范例的缺省项传给服务；原生项目文件保留上面合成的视觉、联网与禁用字段。`resolved-config.toml` 不是完整项目快照，不能因它不重复这些字段就判定未加载。每次请求另存配置、请求和响应，沿用同一消费者及稿件。`passed` 只表示请求结束，业务仍按本文观察点判断。无需收集或解析上游委派树。若使用执行者既有临时封装，它也必须采用这两个固定默认来源、当前 `RP_RUN` 与原 `RP_CONSUMER`；不得读取旧的其他模型候选或把旧结果根覆盖。

### RP-03 至 RP-05 的自动检查与交接核对

测试直接导入正式运行包的 `research_proposal.api`。缺模块或绑定会报错，不跳过、不回退到工作树源码。以下是正式命令，不在准备阶段执行：

```bash
cd "$RP_WORKTREE/test"
export RP_CONSUMER RP_INPUT_CASES RP_TEST_OUTPUT
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v \
  test_inputs.DiscoveryTests > "$RP_RUN/logs/rp03-components.log" 2>&1
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v \
  test_inputs.UpstreamRoutingTests > "$RP_RUN/logs/rp04-components.log" 2>&1
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v \
  test_inputs.AnalysisRoutingTests > "$RP_RUN/logs/rp05-components.log" 2>&1
```

RP-04 的文字交接部分直接阅读安装后的 `research-proposal/SKILL.md`、`references/runtime.md`、`references/upstream.md`，对照原安装代理的既有职责和参数，记录位置及符合/不符合；不调用这些代理。核对下表足以覆盖本项，不新增调用证明：

| 分支 | 本仓库应说明的目标与参数来源 |
|---|---|
| collect | `professor-collector`，发现结果的 `application_root` 作为 `folder_path`，`skip_pdf:true`；仅传已有教授范围。 |
| preview | `professor-topic-clustering`，同一 `folder_path`、已有范围、`preview:true`。 |
| stage0 | `professor-contact`，同一根；教授姓名先对应发现中的真实绝对教授目录，已有选择按正式教授/预筛路径与方向编号传入，不自造目标。 |
| stage1 | `professor-contact-downloader`，同一根及阶段 0 的实际 `target_state`，按 `target_files` 格式；定向补全文仍归此阶段。 |
| stage2 | `professor-contact-analyzer`，同一根与目标文件，先核对阶段 1；已有分析供原负责人采用，本仓库不宣称缓存已经可复用。 |
| stage3 | `professor-contact-idea-generator`，有效输入包及精确方向；调用方按既有 prepare/save/record 校验收尾及终态重建总览约定处理。只核对文字安排，不生成候选或伪造代理调用。 |

共同核对：准确名称、业务参数、等待并消费返回、完成后重新发现、保留真实用户决定、第三阶段调用方职责，以及 `proposal` 不进入邮件阶段。自动测试中的缺候选结果直接供 stage3 使用，不重复执行。

### 论文与非论文路线的真实交互

论文路线输入目录取 `jq -r '.writing.application_root' "$RP_INPUT_CASES"`，教授及包取同一 `writing` 记录；自然语言给出这些实际资料路径、林安、拟研究叙述问题、甲项目日文用途及合成材料身份。最初只提供该根及其中的 `access-initial.md`，不提供整个构造输出根或执行者用的 `cases.json`。补充条件在该根以外，待实际暴露关键条件缺项后，用 `jq -r '.writing.access_supplement' "$RP_INPUT_CASES"` 取得其路径，再提供给下一请求并针对实际建议决定。不得用“跳过上游”等指令替代有效输入；如果完整输入仍返回上游分支，保留结果并交准备/产品负责人，不启动上游业务。

1. 阅读产品展示的问题，合成申请者针对当次内容选择；上游候选文件不构成研究计划问题确认。实际输出和磁盘保存状态一起检查，不能只看回复中的完成声明。
2. 对照 `story.md` P1—P6、`professor-study.md` A1—A4、`outside-study.md` B1—B4，判断两种解释是证据冲突、推断差异还是合理分歧。不得把合成研究描述为现实论文，也不把申请者设想写成已有结果。资料足够后不为测试追加检索。
3. 私人手稿尚无收藏处和取得条件时，查看中文方案、缺项及替代建议，并查看本稿状态没有完整正文或当前提交稿。随后提供 `access-supplement.md`；合成申请者可针对实际建议选择以已提供公开版本为主、手稿仅作可选补充，不能声称许可已取得。
4. 阅读实际修订的中文方案后再决定确认，保留问题与方案两处决定。条件与确认满足后才提出生成甲项目日文稿的请求，完成 RP-08。

非论文路线复用现有《罗生门》材料、相关研究及甲项目原稿，原位置为 `$RP_CONSUMER/input/nonpaper/研究计划/甲项目-联系教授`。其版本 6 尚未提交，历史 `rp07-03` 展示方案未保存且误写 1996 年论文作者的失败保留。先阅读该次实际方案，合成申请者通过正常反馈明确拒绝错误作者归属，要求按已提供的前田角藏 1996 年原文与石川巧 2016 年原文更正并继续当前方案；不提供组件调用或保存步骤，不原样重采样。检查真实修订及保存后再确认；已有问题决定、条件及未受影响内容沿用。相关原文位于本消费者既有非论文输入和原准备目录 `sources/`，需要补入时只复制对应现成文件，不重新下载或调用上游。

两条路线各完成一稿：论文日文、非论文中文；要求使用同批 `program-a.md`、`applicant.md`。直接阅读 Word、Markdown、引用原文、状态与所有产品页图；比较正文、列表、表格和引用，检查栏目、篇幅、可行性及不确定事项。产品真实保存的正文与确认供后续测试使用，不能由输入脚本代写。

### 其余组件与改稿安排

RP-06 的六类文字载体、未支持格式、四处人工定位及扫描结果，RP-10 的导入组件，均采用仍适用的已有结果，不因 r13 重跑。对应正式组件命令保留为 `uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v test_inputs.MaterialTests` 和 `... test_inputs.RevisionImportTests`；仅当以后出现直接影响时再按该影响执行。TXT“十二人”回到第 5 行、Markdown“书籍可以外借”回到第 7 行、HTML“雨天仍开放”回到 `opening/p2`、EPUB“书籍二十四册”回到 `EPUB/chapter.xhtml` 的 `chapter-one/p2`，PDF 页码及 Word 单元格采用已有自动断言，不重复人工定位。正常扫描和 RP-13 恢复共用既有同图结果，不再次调用视觉模型。

RP-08 真实提交后，绑定 `RP_TEST_PROPOSAL` 为非论文已成稿目录。RP-09、RP-11 串行独占原路径；`SavedDraftCase` 要求该稿和相关可改材料位于 `$RP_CONSUMER/input`，输出位于 `$RP_TEST_OUTPUT`，不再错误要求稿件位于新的日志根。每例先保存完整原路径快照，运行结束保存结果，再恢复原目录；状态中绝对路径保持不变。不得与实际改稿会话并行。

RP-09：用 `jq '.blocks | to_entries'` 读取真实 `正文.json`，按七个栏目整理 `RP_TEMPLATE_MAPPING` 指向的数组，项为 `{field,target,body_blocks}`。合成 Word 首表索引 0、填写列 1、行 0—6；选择各栏目实际正文块，不把整稿放一格。转填测试复用同一内容映射而把 target 设为 null。执行后直接读本例 after 中 Word、Markdown 和所有页图，核对固定文字、填写内容与转填说明，不重审学术内容。

RP-11：从真实当前版 `works[current.revision_id]` 的步骤保存件和正文，用 `jq` 整理四份公开 save_revision 的 data 输入，绑定 `RP_MATERIAL_DATA`、`RP_QUESTION_DATA`、`RP_SCHEME_DATA`、`RP_BODY_DATA`。保留真实材料、问题 `question_id/text/confirmation`、方案 `scheme/conditions/confirmation`、正文 `body/references`；不补写确认或完成标记，不要求产品另存原始调用日志。

材料变化分支的 `RP_RELATED_MATERIAL_RECORD` 绑定本稿正文实际引用原文对应的既有读取记录。先用 `jq -r '.works[.current.revision_id].inputs.material_paths[]' "$RP_TEST_PROPOSAL/研究计划状态.json"` 读取实际材料输入，再对照本稿引用选定该读取记录，用 `jq '.material | {material_id, original_path}' "$RP_RELATED_MATERIAL_RECORD"` 查看原文绑定。当前已有记录可能是 `rashomon-read.json`；原文由其中的 `.material.original_path` 定位，不能假定 `inputs.material_paths` 直接列出 `rashomon.html`，也不为测试改写该列表。按下式组合数据并执行：

```bash
export RP_SAVE_REQUESTS="$RP_RUN/config/save-requests.json"
jq -n --slurpfile materials "$RP_MATERIAL_DATA" \
  --slurpfile question "$RP_QUESTION_DATA" --slurpfile scheme "$RP_SCHEME_DATA" \
  --slurpfile body "$RP_BODY_DATA" \
  '{materials:{data:$materials[0]}, question:{data:$question[0]},
    scheme:{data:$scheme[0]}, body:{data:$body[0]}}' > "$RP_SAVE_REQUESTS"
export RP_TEST_PROPOSAL RP_TEMPLATE_MAPPING RP_SAVE_REQUESTS RP_RELATED_MATERIAL_RECORD
cd "$RP_WORKTREE/test"
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v \
  test_export.TemplateTests > "$RP_RUN/logs/rp09-components.log" 2>&1
uv run --no-project --python "$RP_RUNTIME/bin/python3" python -m unittest -v \
  test_recovery.RecoveryTests > "$RP_RUN/logs/rp11-components.log" 2>&1
```

测试从 `RP_RELATED_MATERIAL_RECORD` 的 `.material.original_path` 读取实际原文；若为相对路径，按该读取记录所在目录解释，不按测试进程目录解释。要求原文位于本轮消费者 input 内；保留原字节，把同路径内容临时替换为有效 ASCII 正文，再在 finally 恢复原字节和编码。它不改原下载件或无关文件，不要求原文直接列入 `inputs.material_paths`。产品能否正确处理材料记录指向原文的变化，仍由正式恢复结果判断。RP-11 的单格式失败用目标位置冲突，状态中断用公开 `os.replace` 边界，受控 `page_review` 仅用于失败/提交状态分支，不声称真实页图合格，也不作为 RP-08、RP-09 结果。

RP-10 实际会话从 RP-08 的真实交付副本制作修改稿：纯措辞 Markdown；明确要求核心方法修改且改英文；文件自行把未核实条件写为已取得但没有解释意图；两份核心方法冲突且未选择的版本。依次检查实际改变的确认与版本选择，用户决定针对当次内容，原件保留；已有 Word 修订/批注/未支持对象的组件结果沿用。不得把短样本冒充真实交付稿，不因测试提示而补产品处理步骤。

RP-12 从已提交稿提出乙项目请求，提供 `program-b.md` 并明确复用文献和通用方案。开始前保存第一稿及同资料范围其他教授的相关状态/正文副本，结束后直接比较这些文件，检查新稿的项目、用途、栏目与独立状态；不重验全部写作。

RP-13 已完成且原路径与正常配置已恢复，直接采用现有结果。本项的缺配置输入与偶发环境故障分开。若以后产品修正直接影响本项，仍采用已批准的原路径办法：确认前序请求与写入结束，完整快照已有稿件和正常项目配置；在消费者内新目录放同一残损扫描图，唯一合成表达式改用 `RP_VISION_MISSING_CONFIG`；通过主技能提供该材料；自然结束后保存响应与稿件 after，确认无未完请求或写入，再将原目录移至本次结果目录并把快照原样恢复原位置、恢复正常配置。副作用不明时不恢复覆盖而交负责人判断；正常扫描引用 RP-06，不额外采样。不得手改状态绝对路径或确认。

### 结束、失败与交接

每项读取实际结果后记录通过、失败或无法判断，直接注明正式日志和产物位置；准备与静态检查不计作业务结果。旧失败不覆盖，新范围撤回的上游验收不再阻塞本仓库测试。已保存进度按真实状态续接，不重新采集、分析或生成上游候选。

格式/路径等测试准备错误交本地测试工程师；本仓库行为错误交本地执行工程师修复；目标或判断方法缺项交测试计划负责人。已有业务失败不能为取得满意输出原条件重采样。偶发外部故障只在确认请求、子进程及写入已经结束、环境确已恢复且副作用可判定后，保持业务输入、模型和配置不变，最多补一次（总计两次）；否则保留原始结果并停止受影响项。超时或响应丢失时先查已有请求状态，不并行重发，不自行启停服务。

本次准备只运行本地输入构造、文件解析、语法和配置传输有限检查，不运行 unittest、产品入口或评估请求。准备审核与第二关完成后，正式执行由本地执行工程师按上述剩余项负责；全部历史及有效结果继续由 `test-results.md` 管理，不新增重复证据账本。
