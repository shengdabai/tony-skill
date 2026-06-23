# tony-skill

蒸馏一个人的认知操作系统的 Agent Skill — 对外汉语教学法 × AI「第零阶级」方法论 × 跨时空连接思维。Distill a person's cognitive OS. Inspired by nuwa-skill.

## Business Context

- **Category:** AI workflow infrastructure
- **Audience:** AI builders, creators, independent developers, and small teams that want repeatable local AI workflows.
- **Repository status:** Public repository. Keep examples, docs, and issues free of credentials, private data, and machine-specific paths.
- **Topics:** agent-skills, ai-methodology, chinese-teaching, claude-code, claude-skill, cognitive-framework, mental-models, nuwa-skill

## What This Project Is For

- 蒸馏一个人的认知操作系统的 Agent Skill — 对外汉语教学法 × AI「第零阶级」方法论 × 跨时空连接思维。Distill a person's cognitive OS. Inspired by nuwa-skill.
- Package repeatable AI workflows into reusable local assets.
- Reduce one-off prompt work with versioned skills, guardrails, and handoff files.

## Where It Fits

This repository is part of a broader AI local-workbench operating model: reusable skills, local automation, auditable configuration, and repeatable delivery workflows.

## Technical Overview

- **Primary language:** Not classified by GitHub
- **Default branch:** `master`
- **Visibility:** `PUBLIC`
- **License:** Other

## Repository Map

- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `LICENSE`
- `README.md`
- `SECURITY.md`
- `SKILL.md`
- `examples`
- `references`

## Quick Start

No universal setup command is declared yet. Start by inspecting the repository map above and the project-specific scripts or docs committed with the code.

## Operating Notes

- Keep real credentials out of the repository. Use local environment files, GitHub repository secrets, or the deployment platform secret manager.
- If a `.env.example` file exists, treat it as documentation only; never commit filled-in `.env` files.
- Before publishing screenshots, demos, or client examples, remove private names, internal paths, account IDs, and API endpoints.
- The `Repository Hygiene` workflow is a lightweight guardrail, not a replacement for product-specific tests.

## Delivery Checklist

- [ ] README describes the user, business outcome, and operating boundary.
- [ ] Setup or preview commands are current and do not rely on private machine state.
- [ ] No real secrets, private user data, or machine-local state are tracked.
- [ ] Screenshots, demos, or sample outputs are safe to share publicly when the repository is public.
- [ ] Product-specific tests or smoke checks are documented before production use.

## Roadmap

- Tighten the fastest path from clone to useful demo.
- Add project-specific screenshots, sample outputs, or a short walkthrough where useful.
- Promote repeated manual steps into scripts, tests, or documented workflows.
- Keep security, privacy, and licensing boundaries explicit as the project evolves.

## Maintainer Notes

Maintained by [Tony Sheng](https://github.com/shengdabai). This README is written as a business-facing handoff: it should help a future collaborator, client, or reviewer understand why the repository exists, how to inspect it, and what must be true before it is reused or shipped.

| 模块 | 帮谁 | 核心 |
|---|---|---|
| 🀄 **思维桥梁教学法** | 中文老师 & 中文学习者 | **教思维不教翻译**：四层逐字对照（Chinese / Pinyin / Word-by-Word / English）+ 把语言点拉进历史与跨学科纵深的"文化对照配方" |
| 🤖 **「第零阶级」AI 方法论** | 想真正用好 AI 的人 | **能力增益而非卸载**（"用 AI 让你变轻松=用错了"）+ 自进化系统 8 大设计原则 + 多模型编排 + token 经济学 |
| 🧩 **跨时空连接思维** | 任何做思考 / 写作 / 决策的人 | 7 个心智模型 + 12 条决策启发式 + 7 条 voice 规则，把当下任何事拉进历史长河与别的学科 |

外加一套贯穿全局的 **Agentic 研究协议**：涉及当下事实必须先查证再断言，**绝不编造**——这是从 nuwa-skill 继承的诚实纪律。

### 七个心智模型（思维内核）

1. **跨时空连接** — 没有孤立知识点，只有节点和连边
2. **工程化破界** — 一切皆可拆解、优化、重构的系统
3. **自进化系统优先** — 最高产出是"造一个能造系统的系统"，进化本质即递归
4. **能力增益而非卸载** — "变轻松"是用错的信号
5. **迭代胜过规格** — 先跑 v1 看真实结果，卡在规划比做错更糟
6. **验证以现实为准** — 只信磁盘 / 真实渲染 / smoke test，不信自报数字
7. **杠杆经济学** — 在"放大产出"与"守住约束"间显式权衡

> 谱系：Tony = 李笑来「重新定义 + 践行」× 万维钢「科学破常识」× 金观涛 / 史学「大历史纵深」× 李小龙 / 禅「集成不立派」× Karpathy / Sutton「工程审美与 scaling 信仰」，再用余华式「人味与反讽」上色。

### 安装与使用

`tony-skill` 遵循开放的 **Agent Skills 协议**，`SKILL.md` + `references/` 即可被任意兼容运行时加载。

**Claude Code**

```bash
# 克隆到你的 skills 目录
git clone https://github.com/shengdabai/tony-skill ~/.claude/skills/tony-skill
```

随后在对话里自然触发即可，例如：
- "用思维桥梁教学法教我『把』字句" → 自动加载教学模块
- "帮我设计一个能自进化的资讯简报系统" → 自动加载 AI 方法论
- "用 Tony 的方式想想：我该不该用 AI 写日记" → 自动加载心智模型 + voice

**Cursor / Codex / 其他**：把本仓库作为 skill 目录引入，或把 `SKILL.md` 内容作为 system prompt 注入；`references/` 按需加载。

### 仓库结构

```
tony-skill/
├── SKILL.md                        # 核心：路由 + 心智模型摘要 + voice + 边界 + 研究协议
├── README.md / LICENSE             # 仓库文档与许可
├── CONTRIBUTING.md / CHANGELOG.md  # 迁移指南与版本记录
├── references/
│   ├── teaching-method.md          # 思维桥梁教学法全文（四层对照 + 文化纵深五步配方）
│   ├── ai-method.md                # 「第零阶级」playbook（8 原则 + 多模型编排 + token 经济学）
│   ├── mental-models.md            # 7 心智模型 + 12 启发式 + 反模式 + 价值观（全证据版）
│   ├── genealogy-and-voice.md      # 思想谱系（225 本知识食谱聚类）+ 7 条 voice 规则
│   └── research-protocol.md        # Agentic 研究协议 + 诚实边界
└── examples/
    ├── teaching-example.md             # 老师视角备课：「给我打电话」教成思维跃迁
    ├── learner-self-study-example.md   # 学习者视角自助：用四层对照攻克「把」字句
    ├── ai-leverage-example.md          # 自进化系统设计（含一次真实翻车→诊断→修正→落盘）
    └── thinking-example.md             # Tony voice 思考：该不该用 AI 写日记
```

### 它怎么被造出来的

遵循 Claude **skill-creator** 的结构规范，借鉴 **nuwa-skill** 的"并行研究 → 三重验证 → 技能构建 → 质量测试"四阶段框架。素材由**多个 AI agent 并行**分析以下私有源蒸馏而成（已移除密钥、私有链接、第三方姓名等直接敏感信息；但作者**有意公开**了自己的职业身份、知识食谱规模等可画像信息，这是一个自觉的隐私权衡，并非"零信息暴露"）：

- 跨会话的 AI 协作记忆与决策记录
- 225 本 NotebookLM 知识库构成的"知识食谱"（用于反推思想谱系与表达 DNA）
- 真实教学实例与方法论档案

每个心智模型都经过"跨领域复现 / 生成力 / 独特性"三重验证，并**诚实标注局限**——这套思维擅长生成洞察、驱动产出，但普遍缺"何时该停"的内建判据，文档对此如实交代。

### 诚实边界

- **教学法的文化对照**必须基于真实史料；编一个玄乎的"文化解释"比不讲更糟。
- **voice 部分是合理推断**（从"读什么"+ 真实教学实例反推），模仿时继承 Tony"多空对冲、自己当裁判"的姿态，不替他对争议选边。
- 涉及当下事实，**先查证再说**，绝不用"Tony 大概会这么想"掩盖一个本该核实的事实。

---

<a name="english"></a>

## English

### What it is

`tony-skill` distills the **cognitive operating system** of **Tony** — a career teacher of Chinese as a foreign language (CELTA + TESOL certified, thousands of students taught, per the author) who is also a heavy AI power-user — into one executable Agent Skill.

It captures not *what he said*, but *how he thinks, teaches, and uses AI*: transferable mental models, a reusable teaching method, and a copy-able methodology. Install it and your AI will dissect problems, design Chinese-learning, build self-evolving systems, and write in Tony's voice.

> **This is not role-play.** Don't imitate a persona — install a way of thinking. The test is always: does the answer make the other person **see deeper, do more, grow** — not "does it sound like Tony."

### Three capability modules

| Module | For whom | Core |
|---|---|---|
| 🀄 **The "Thinking Bridge" teaching method** | Chinese teachers & learners | **Teach thinking, not translation**: a four-line gloss (Chinese / Pinyin / Word-by-Word / English) + a recipe for pulling any language point into historical & cross-disciplinary depth |
| 🤖 **"Class Zero" AI methodology** | Anyone who wants to truly master AI | **Augmentation over offloading** ("if AI makes you *easier*, you're using it wrong") + 8 design principles for self-evolving systems + multi-model orchestration + prompt-cache economics |
| 🧩 **Cross-temporal connective thinking** | Anyone who thinks / writes / decides | 7 mental models + 12 decision heuristics + 7 voice rules that pull any topic into deep history and other fields |

Plus a global **agentic research protocol**: any present-day fact must be *verified before asserted* — **never fabricated**. This honesty discipline is inherited from nuwa-skill.

### The seven mental models

1. **Cross-temporal bridging** — no isolated facts, only nodes and edges
2. **Engineering-lens universalism** — everything is a system to be re-architected
3. **Recursive self-improving systems** — the highest output is "a system that builds systems"; evolution *is* recursion
4. **Augmentation over offloading** — "feeling easier" is the signal you're doing it wrong
5. **Iteration over specification** — ship a real v1, getting stuck in planning is worse than being wrong
6. **Reality-grounded verification** — trust disk / rendered output / smoke tests, never self-reported numbers
7. **Constraint-aware leverage** — every decision weighs "amplify output" against "respect the constraint"

### Install & use

`tony-skill` follows the open **Agent Skills** protocol — `SKILL.md` + `references/` load into any compatible runtime.

**Claude Code**

```bash
git clone https://github.com/shengdabai/tony-skill ~/.claude/skills/tony-skill
```

Then trigger naturally in chat, e.g.:
- "Teach me the 把 construction with the thinking-bridge method" → loads the teaching module
- "Design a self-evolving news-brief system for me" → loads the AI methodology
- "Think about this the way Tony would: should I use AI to write my journal?" → loads the mental models + voice

**Cursor / Codex / others**: add this repo as a skill directory, or inject `SKILL.md` as a system prompt and load `references/` on demand.

### How it was built

Built following Anthropic's **skill-creator** structure conventions, using **nuwa-skill**'s four-phase framework (parallel research → triple validation → skill construction → quality testing). The source material was distilled by **multiple AI agents working in parallel** over private sources, with **secrets, private links, and third-party names removed**. (Note: the author *intentionally* discloses his own professional identity and the scale of his knowledge diet — a deliberate privacy trade-off, not a claim of zero information exposure.):

- cross-session AI-collaboration memory and decision logs
- a "knowledge diet" of 225 NotebookLM notebooks (used to reconstruct intellectual genealogy & expression DNA)
- real teaching cases and methodology archives

Every mental model passes a triple test (cross-domain reproduction / generative power / uniqueness) and **honestly states its limits** — these frameworks excel at generating insight and driving output, but generally lack a built-in sense of *when to stop*, which the docs disclose plainly.

### Honest boundaries

- The teaching method's **cultural depth must rest on real sources**; inventing a mystical "cultural explanation" is worse than not giving one.
- The **voice profile is reasoned inference** (reverse-engineered from "what he reads" + real teaching cases); imitate his *hedge-both-sides, be-your-own-judge* stance, don't take sides for him.
- For present-day facts, **research first** — never let "Tony would probably think…" paper over something that should be checked.

### Known limitations (for fork users)

- **No built-in stop criteria**: the frameworks here excel at generating insight and driving output, but don't tell you *when enough is enough*. Add your own exit conditions when adapting them to loops or automated pipelines.
- **Token-cache economics are provider-dependent**: the prompt-cache figures in `references/ai-method.md` apply only when your provider supports prompt caching (e.g. Claude, some OpenAI models). Don't assume the numbers hold on every runtime.
- **No automated CI**: there are no tests validating that routing table entries in `SKILL.md` match actual files in `references/`. If you fork and rename files, update `SKILL.md` manually.

---

## 🛠️ 二次创作 · Fork & Distill Yourself

最自然的 fork 方式是**用同一套方法蒸馏你自己**，做出 `your-name-skill`。
迁移流程、PII 脱敏清单与诚实边界要求见 **[CONTRIBUTING.md](./CONTRIBUTING.md)**；版本演进见 **[CHANGELOG.md](./CHANGELOG.md)**。

The most natural fork is to **distill yourself** with the same method.
See **[CONTRIBUTING.md](./CONTRIBUTING.md)** for the migration workflow, PII checklist, and honesty-boundary requirements.

---

## 🙏 致谢 · Credits

本项目的灵感、方法论框架与"蒸馏认知而非角色扮演"的核心理念，全部来自
**[alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill)** —— 花叔（Huashu）的开源杰作。
nuwa-skill 提出了"何必只蒸馏同事"的精彩命题，并设计了并行研究 + 三重验证的造技能流程。
`tony-skill` 把这套框架从"公众人物的公开资料"迁移到"一个具体的人的私有记忆与知识食谱"，并补上了严格的 PII 脱敏与诚实边界。

This project's inspiration, methodological framework, and the central idea of
*distilling cognition rather than performing a persona* all come from
**[alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill)** by Huashu (花叔).
`tony-skill` adapts that framework from "a public figure's public record" to
"one specific person's private memory and knowledge diet," adding strict PII
de-identification and explicit honesty boundaries.

Also built on Anthropic's **[skill-creator](https://github.com/anthropics/skills)** conformance standard.

## 📄 License

[MIT](./LICENSE) © 2026 Tony · tony-skill
