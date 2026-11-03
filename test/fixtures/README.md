# 研究计划测试输入

这些文件只为已批准的 RP-01 至 RP-13 提供输入，不是产品实现或测试通过记录。完整执行步骤只放在 `plan/test-plan.md`。组件测试按执行计划 r3 的公开接口提前编写；产品实现后按既定步骤执行，不因接口当前尚未实现而跳过测试或使用固定通过的断言。

## 合成载体

`materials/` 中的内容由本轮测试准备编写，可以随测试代码复用。它们明确标注为合成材料，不得当成真实已发表研究的证据。

| 文件 | 已知内容及可定位位置 |
|---|---|
| `reading-room.txt` | 第一章三行分别为周二十二人、周四十八人和记录限制；第二章写明期刊不外借、空白不等于零。 |
| `reading-room.md` | “借阅规则”下的表格为书籍 24、期刊 6；最后一段保留空白记录的限制。 |
| `reading-room.html` | `opening` 章节中 `p1` 为开放时间，`p2` 为雨天记录；`rules` 中 `p3` 为借阅说明。 |
| `reading-room.epub` | `EPUB/chapter.xhtml` 的 `chapter-one` 章节，`p2` 为书籍二十四册和期刊六种，`p3` 为期刊限制。 |
| `reading-room.pdf` | 物理第 1 页印刷页“二”，记录十二人和十八人；物理第 2 页印刷页“三”，记录书籍、期刊及空白限制。 |
| `reading-room.docx` | “开放记录”后正文有十二人、十八人；第一个表格第 2 行第 2 列为 24，第 3 行第 2 列为 6。没有稳定分页承诺。 |
| `damaged-scan.png` | 1200 × 900 像素；“记录编号：乙七”和“期刊只供馆内阅览”清晰；数量所在区域约为左上角坐标 `(292,418)` 至右下角 `(378,468)`，该内容已完全缺失，没有可恢复的标准答案。右下角空心圆是图形，不含文字。 |
| `unsupported.xyz` | 有非空中文内容，扩展名不属于已批准支持载体。 |

扫描图只要求如实保留读不出的部分，不要求逐字零误差；图形含义不得混入逐字转录。

## 模板和修改稿

`templates/editable-form.docx` 是合成的两列表格，左栏为栏目，右栏为空白填写区；表格前后有固定说明。`templates/transfer-form.pdf` 没有表单控件，作为不能直接填写的模板输入。它们没有现实学校的效力。

`revisions/baseline.docx` 是导入组件用的短基准。`marked.docx` 把“段落比较”标为未决删除，把“逐段比较”标为未决插入；批注 0 附在“材料取得条件尚未核实”上，批注内容不是正文。最后一段含一个未支持的嵌入对象，关系为 `rIdFixtureObject`、部件为 `word/embeddings/opaque.bin`；其载荷故意不可解释，文档其余部分可以打开。`wording.md` 只改措辞；`condition-change.md` 把未核实改为已经获得；两个 `conflict-*.md` 分别采用段落比较和读者访谈。

`revisions/baseline.json` 是同一短基准的 Pandoc AST，供公开导入接口的 `baseline_body` 参数使用。它在准备阶段由作者工具 Pandoc 3.1.11.1 读取 `baseline.docx` 生成，含两个正文块；不是产品运行结果，也不替代产品固定 Pandoc 3.7.0.2 的正式检查。

这些短样本只供 RP-10 的导入组件自动测试。RP-10 的实际修订从 RP-08 真正交付的稿件副本制作，不能把这些文件冒充上一轮成稿，也不能预写产品确认状态。

## 真实来源

以下来源的原文件保存在本轮仓库外准备目录，不把期刊全文或申请资料再分发到源码。获取时间为 2026 年 11 月 3 日；正文判断须读原文和相应位置，不能只读本表或搜索摘要。

| 本轮文件名 | 来源与用途 |
|---|---|
| `rashomon.html` | [青空文库《羅生門》](https://www.aozora.gr.jp/cards/000879/files/127_15260.html)，芥川龙之介作品原文，用于非论文候选输入。 |
| `maeda-1996.pdf` | [前田角藏《「羅生門」論：老婆の視座から》](https://www.jstage.jst.go.jp/article/nihonbungaku/45/2/45_KJ00009823286/_article/-char/ja)，1996 年，第 29—41 页，共 13 个物理页；目标教授之外的研究。其视角重在老婆与暴力关系。 |
| `ishikawa-2016.pdf` | [石川巧《「羅生門」精読》](https://www.jstage.jst.go.jp/article/nihonbungaku/65/4/65_13/_article/-char/ja/)，2016 年，第 13—24 页，共 12 个物理页。第 13—14 页讨论既有解释与教学关注的差别，可据此核对“共同承认生存之恶”与“弱者内部的暴力”是否真的相容；不能预先把所有差别定性成矛盾。 |
| `admissions-2027.pdf` | [立教大学文学研究科博士前期课程募集要项](https://www.rikkyo.ac.jp/admissions/graduate/mknpps000003n0nr-att/guidelines_arts_mas.pdf)，来自[2027 年官方入口](https://www.rikkyo.ac.jp/admissions/graduate/guidelines.html)。 |
| `research-plan-cover-2027.pdf` | [同项目春季研究计划表封面](https://www.rikkyo.ac.jp/admissions/graduate/mknpps000003n0nr-att/4_arts-keikakusho_sper.pdf)，用于 RP-09 读取空白表中的要求；与合成填表模板分开使用。 |
| `faculty.html` | [立教大学日本文学专攻及教员页面](https://www.rikkyo.ac.jp/graduate/arts/major_01.html)，为上游采集提供公开入口。 |
| `reading-conditions.html` | [日本近代文学馆使用说明](https://www.bungakukan.or.jp/guidance/facilities/)，说明普通阅览和肉笔材料特殊阅览的申请条件。只证明有相应申请途径，不能证明某件未定位手稿在馆或已经获准使用。 |

RP-07 的材料条件先声明“拟使用私人手稿，但尚未定位收藏处、取得途径和替代材料”。补充阶段提供上述阅览规则，并由用户明确改用已定位的公开版本作主材料、特殊阅览仅作可选补充：[国会图书馆所藏 1917 年版《羅生門》目录](https://ndlsearch.ndl.go.jp/books/R100000002-I000000570013)及其公开数字阅读入口可供核对；若原计划必须依赖私人手稿，则仍不得声称条件已解决。没有实际提交阅览申请，也没有取得私人手稿。
