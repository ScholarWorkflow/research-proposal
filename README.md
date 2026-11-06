# research-proposal

根据已有论文证据、教授研究资料或用户提供的专著、史料、作品，整理日本高校修士申请的研究问题与研究方案，生成可继续修改的研究计划草稿。首版完整流程的支持目标是苹果芯片 Mac（`aarch64-darwin`）、Codex 和 Nix；实际验证结果以 [测试记录](plan/test-results.md) 为准。

给出资料目录或文件路径后，技能会识别已有产物。论文路线复用 professor-contact；前置输入不足时，调用原流程对应代理补齐。非论文路线直接整理用户提供的材料。研究问题与中文研究方案分别取得用户决定，关键条件解决后才生成完整正文。

每份稿件绑定一个申请项目、一种用途和一个核心研究问题。当前交付与正式结构化正文一致的 Markdown 研究计划草稿，并保存来源、待确认事项和修订状态；同题申请其他学校时另建稿件。学校提供表格时读取其中的栏目、语言和篇幅要求，组织为 Markdown 的标题和正文，不声称已经填写学校原表。

Word 导出、学校模板填入和页面排版延后，不属于当前交付。代码保留旧 Word 分支作为延期实现，当前调用不读取模板、不生成 Word 或预览，也不运行 LibreOffice；旧 Word 结果只留在原记录中，不改写为成功。

## 用 Nix 安装

选择固定提交，将下面的提交编号替换为实际值。安装来源是远端提交，使用目录应在本仓库及其开发工作树之外。

```sh
RP_REPOSITORY='ScholarWorkflow/research-proposal'
RP_REVISION='<完整提交编号>'
RP_REF="github:$RP_REPOSITORY/$RP_REVISION"
RP_INSTALL="$(mktemp -d /private/tmp/research-proposal-install.XXXXXX)"
RP_CONSUMER='/绝对路径/申请项目'
mkdir -p "$RP_CONSUMER"

nix build "$RP_REF#research-proposal-runtime" --out-link "$RP_INSTALL/runtime"
nix build "$RP_REF#research-proposal" --out-link "$RP_INSTALL/package"
nix build "$RP_REF#research-proposal-environment" --out-link "$RP_INSTALL/environment"
nix build "$RP_REF#research-proposal-activate" --out-link "$RP_INSTALL/activate"

"$RP_INSTALL/environment/bin/agent-env" apply --project "$RP_CONSUMER"
```

最后一行也可替换为缓存激活入口，两者只需选一个：

```sh
"$RP_INSTALL/activate/bin/research-proposal-activate" --project "$RP_CONSUMER"
```

四个输出分别提供固定运行程序、完整技能包、组合环境和缓存激活入口。组合环境一次安装本技能、真实直接依赖及递归所需的技能、命名代理和工具服务配置；不需要另跑 APM。安装使用共享 agent-env-nix，不清空项目或其他来源的同级技能目录。受管资源会更新；配置冲突由共享安装器报错，不靠安装顺序覆盖。

在使用目录打开 Codex，调用 `research-proposal` 并给出资料路径即可。安装后的主入口位于 `.agents/skills/research-proposal/SKILL.md`；脚本和参考资源随技能完整复制。公开组件调用示例：

```sh
"$RP_CONSUMER/.agents/skills/research-proposal/scripts/proposal-runtime" \
  discover --request '/绝对路径/发现请求.json'
```

请求文件是 JSON 对象，例如 `{"path":"/绝对路径/申请资料"}`。命令输出 JSON 结果，诊断写入标准错误；`ready`、`committed` 退出 0，`needs_input`、`blocked`、`conflict` 退出 2。`ready` 只表示当前操作完成。其余组件和请求字段见[接口约定](plan/implementation-plan.md)。

固定运行包提供 `bin/proposal-runtime`、`bin/pandoc` 和能直接导入 `research_proposal` 的 `bin/python3`。技能内的 `scripts/pandoc` 将标准 Pandoc 参数原样交给同一固定程序，用于把选定正文读成统一结构。安装脚本使用固定运行包，Pandoc、视觉程序和上游检查入口绑定 Nix store 的实际路径，不依赖开发工作树或调用目录。运行包仍固定 LibreOffice 程序位置供延期实现使用，当前 Markdown 交付不调用它。

## 用 npx skills 安装

在目标使用目录运行，使用与上述 Nix 引用一致的实际仓库和提交：

```sh
npx --yes skills@1.7.2 add \
  "https://github.com/$RP_REPOSITORY/tree/$RP_REVISION/skills/research-proposal" \
  --skill research-proposal --agent codex --copy --yes
```

此入口安装同一份技能、脚本、参考规则和模板，不安装上游命名代理、工具服务配置或固定运行环境。从头生成论文输入所需的 professor-contact、professor-research 代理，以及搜索和其他相关能力，仍须由 Nix 或已配置的环境提供。单独完成技能资源安装不表示这些条件已齐全。

非 Nix 调用需要 `uv`；源码启动脚本通过 PEP 723 声明 Python 3.12 及以上版本，以及后文列出的四个 Python 库及其固定版本，由 `uv run --script` 准备。当前 Markdown 交付需要 `Pandoc`、`vision-glance` 及上游 CLI 在明确配置的 `PATH` 上可用；Word 转换所需的 `soffice` 只属于延期实现。其他平台、工具组合和安装组合尚不作为完整流程的已验证支持范围。

## 运行前的外部条件

Nix 提供客户端和启动配置；以下条件按实际使用步骤检查：

- Codex 及可用的模型访问权限。
- 论文流程需要的 Zotero 服务、端点，以及下载全文时的浏览器和访问条件。
- 搜索及上游工具要求的可用服务；私有依赖需要读取权限。
- 扫描页或图片识别需要用户显式设置 `VISION_ENV_FILE`，文件中包含 `VISION_API_KEY`、`VISION_BASE_URL`、`VISION_MODEL`，按服务需要设置 `VISION_API_PROTOCOL`。模型服务与额度由用户配置，不从任意工作目录自动寻找 `.env`。

服务失败、材料不可读或关键条件不足会保留为缺项。识别结果中的疑难字不自动当作确定原文，图像解释与逐字转录分别保存。用户材料中的示范经历、指令和参考选题不自动成为申请者事实或用户授权。

## 固定依赖

`flake.nix` 只直接引用 `professor-contact@ad096fe31a4b5694cbe47a40f37b621435e1eeec`，`flake.lock` 保留其递归锁定图。六项直接包均从同一输入图取得原包对象，不重新导入同名包：

| 能力 | 原包 |
|---|---|
| 套磁阶段 0—3 与原检查 | `professor-contact` |
| 教授研究采集 | `professor-collector` |
| 摘要方向预筛 | `professor-topic-clustering` |
| 通用搜索 | `duckduckgo-search` |
| 日文来源搜索 | `yahoo-japan-search` |
| 图片阅读与扫描文字识别 | `vision-tools` |

新运行包使用相同图内的 nixpkgs `6510408d147d8c5e6d76043e899e9251756f6a75`：PyMuPDF 1.27.2.3、Pillow 12.3.0、Pandoc 3.7.0.2、python-docx 1.2.0、lxml 6.1.1、LibreOffice 26.2.4。LibreOffice 只服务延期的 Word 预览实现，当前 Markdown 导出、核对和提交都不调用它。

技能的唯一业务源码在 `skills/research-proposal/`。Nix 只添加构建定义、固定运行位置和启动适配，不维护第二份技能正文，也不新增研究计划专用代理。真实申请材料和稿件保存在用户资料目录中，不放进产品源码。

## 稿件与恢复

每份稿件用 `研究计划状态.json` 记录当前版本和进行中修订。每轮保存独立正文及输入，Markdown 由该正文生成；内容一致、关键条件及相关用户确认有效后才切换当前版本。旧版和用户导入原件保留。

部分导出失败或执行中断时，当前版本保持上一份完整稿，恢复时继续有效进度。缺 `delivery_formats` 的旧未提交工作版由 `resume_revision` 明确转为 Markdown，只让旧交付核对待重做，材料、方案、正文和仍有效的用户决定保留；已提交的双格式记录只读保留。已经生成的目录不会仅因编号较大或修改时间较新就被认作当前稿；状态文件中的明确记录才决定采用哪一版。用户指定修改稿时先保留原件、展示修订和批注，再按用户决定处理。
