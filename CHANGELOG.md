# Changelog

本项目记录 tony-skill 的版本演进。遵循 [Keep a Changelog](https://keepachangelog.com/) 精神。

## [1.2.0] - 2026-06-08

跨模型独立评审（Codex / GPT-5.5）后的学术准确性与诚实边界修复。

### Changed（学术准确性）
- **教学法-实例二（前/后 vs 艾马拉时间观）**：去掉"中文与艾马拉同构/一样"的过强表述，改为"中文主要是早晚顺序隐喻、艾马拉是身体取向+手势证据，机制不同"，补 Núñez & Sweetser (2006) 出处，明确"对照而非同构"。
- **教学法-实例三（砍价 vs 阎云翔《礼物的流动》）**：改"砍价本质=人情账本"为"类比而非证明"，区分熟人/重复交易与陌生议价，删除"亏本卖是关系话术""熟人价"等会被读成刻板印象的断言。
- **教学法-实例一（二/两字源）**：从"三千年前概念的化石"软化为"记忆线索，非完整规则来源"，补反例（二十/两百/二两/第二个）。
- `research-protocol.md`：删除对三例"已验证/站得住"的盖章，改为"用前归类为事实/类比/教学简化并按来源核验"——消除诚实文件的自相矛盾。

### Changed（诚实边界 / OPSEC）
- 软化 README "不含任何个人身份信息"的绝对表述为"已移除密钥/私链/第三方姓名等直接敏感信息"，并明示作者有意公开职业身份/食谱规模是自觉的隐私权衡（中英同步）。
- 移除个人消费数字（API/周期金额）；"第零阶级"统一删除自相矛盾的精确比例（千分之一 vs 千分之 1.5）改为"极少数"；token/cache 的"80%/90%"加"取决于提供商是否支持 prompt caching"的环境限定。
- 软化可画像数字：学员数统一为"数千名（作者自述）"，"9 年/5000h"改为"多年/大量"。
- `examples/teaching-example.md`：把"中文是关系本位语言"的本质论断言降级为"教学类比"。

### Fixed
- README 仓库结构树补回 README/LICENSE/CONTRIBUTING/CHANGELOG 根文件。
- voice 规则计数在 SKILL.md 与 genealogy 间统一为"7 条（第 7 条可选）"。

## [1.1.0] - 2026-06-08

独立质量评审后的全面优化升级（评级从 A- 提升）。

### Added
- `references/mental-models.md`：新增「二·补 停止判据」——给七个模型共同的"缺何时该停"盲区开出 5 条可操作刹车（把最诚实的弱点转成差异化资产）。
- `references/genealogy-and-voice.md`：新增「三·补 认知演化关键转折」时间线（教学法 → 学习元研究 → AI 能力增益伦理 → 自进化系统 → 收获导向），补上 nuwa 框架缺失的时间维度。
- `examples/learner-self-study-example.md`：新增中文学习者视角自助示例（用四层对照攻克「把」字句），兑现对"中文学习者"用户的承诺。
- `CONTRIBUTING.md`：新增"如何用本框架蒸馏你自己"的迁移流程 + PII 脱敏清单 + 诚实边界要求。
- `CHANGELOG.md`（本文件）。
- SKILL.md `description` 补充英文触发词，覆盖非中文母语的中文学习者。
- README 顶部新增「60 秒试一下」即时上手块。

### Changed
- `examples/ai-leverage-example.md`：从"一次成功的理想流程"重写为**含真实翻车（自报 44 条实则磁盘 0）→ 诊断 → 修正 → 落盘**的多轮范例，让示例本身演示 skill 的核心纪律。
- README：删除无依据的"50+ runtimes"宣称、软化"6000+ 学员/官方标准"等未核实表述（与"以现实为准"内核对齐）；clone URL 换成真实仓库地址。
- 统一 voice 规则计数为 7 条；统一三大模块命名；mental-models 三重验证名实对齐。

### Fixed
- voice 规则数三方不一致（标题 6 / 实列 7）。
- ai-method 原则 4 与第 4 节的锚点缺失。

## [1.0.0] - 2026-06-08

首个公开版本。

### Added
- `SKILL.md`：路由 + 7 心智模型 + 12 决策启发式 + 7 voice 规则 + 价值观 + agentic 研究协议。
- `references/`：teaching-method / ai-method / mental-models / genealogy-and-voice / research-protocol。
- `examples/`：教学备课 / 自进化系统设计 / Tony 式思考。
- 中英双语 README、MIT LICENSE（标注 nuwa-skill 灵感与引用）。
- 灵感与方法论框架来自 [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill)，遵循 Claude skill-creator 结构规范。
