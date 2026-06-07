# Contributing · 用本框架蒸馏你自己（或另一个人）

> `tony-skill` 本身就是一次"迁移"——把 [nuwa-skill](https://github.com/alchaincyf/nuwa-skill) 蒸馏公众人物的框架，迁移到"一个具体的人的私有记忆与知识食谱"。
> 最自然的二次创作，就是**用同一套方法蒸馏你自己**，做出 `your-name-skill`。本文给出可复制的迁移流程。
>
> Contributions to `tony-skill` itself (typo fixes, clearer examples, better triggers) are welcome via PR. But the highest-value fork is to **distill yourself** with the same method. This guide shows how.

## 一、迁移流程（四阶段，源自 nuwa-skill + skill-creator）

1. **并行研究（多源采集）**
   收集关于"蒸馏对象"的素材。tony-skill 用的是私有源（跨会话 AI 记忆、知识库笔记、教学档案）；你也可以用公开源（文章、播客、社交）。**用多个 agent 并行**分析不同维度（认知框架 / 领域方法论 / 知识谱系 / voice）。

2. **三重验证**
   每个心智模型必须通过：**跨领域复现**（不止一个领域有证据）、**生成力**（能产出新判断）、**独特性**（不是人人都有的通识）。过不了的不要写进去。

3. **技能构建**（对齐 skill-creator）
   产出 `SKILL.md`（frontmatter 仅 `name` + `description`，body < 500 行，progressive disclosure）+ `references/`（分领域，一级深）+ `examples/`。结构参考本仓库。

4. **质量测试**
   找一个独立 reviewer（最好换个模型，如用 Codex 交叉审）逐项审：合规 / 框架完整度 / 内部一致 / PII / 诚实边界 / 实用性。**作者与审查分两遍跑，不在同一上下文自我批准。**

## 二、PII 脱敏清单（迁移到真人时必做）

公开发布前，逐项确认产出里**没有**：

- [ ] 真名、邮箱、电话、住址、身份证 / 证件号
- [ ] GitHub / 社交账号 handle（除非本人愿意公开）
- [ ] IP、真实主机名、私有路径里的用户名、密钥 / token
- [ ] 第三方个人姓名（学员、客户、家人）
- [ ] 私有链接（NotebookLM / 网盘 / 内部文档 URL）

用一条 grep 兜底扫一遍，再推送。机密文件（`.env`、`*.key` 等）一律 `.gitignore`。

## 三、诚实边界要求（不可省）

继承 nuwa 的核心纪律，每个蒸馏 skill 都必须包含：

- 每个心智模型**标注盲区/局限**，不只写它的威力。
- voice 部分明确标注是**推断**（从"读什么/说什么"反推），不是本人逐字背书。
- 一份 **agentic 研究协议**：涉及当下事实先查证再断言，**绝不编造**。
- 一节**能力边界 / 不适合谁**，不做万能宣称。

> 判据：你的 skill 让使用者**能力增益**了，还是只是"听起来像某人"？前者才值得发布。

## 四、给 tony-skill 本身提 PR

- 小修（错别字、更清晰的示例、更准的触发词）直接开 PR。
- 改动 `SKILL.md` 触发描述前，先想清楚会不会误伤现有触发。
- 任何改动不得引入 PII。

---

License: [MIT](./LICENSE)。Fork 自由，记得在你的衍生作里同样致谢 nuwa-skill。
