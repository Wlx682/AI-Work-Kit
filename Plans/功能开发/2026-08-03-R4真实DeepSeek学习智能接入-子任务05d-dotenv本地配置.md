---
tags: [功能开发, R4, DeepSeek, dotenv, 子任务]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-03
lifecycle_state: development
epic: Plans/Epic/2026-07-08-智能体开发.md
parent: Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入.md
含业务逻辑: 是
relations:
  depends_on:
    - Plans/需求分析/2026-08-03-R4真实DeepSeek学习智能接入.md
    - Plans/技术方案/2026-08-03-R4真实DeepSeek学习智能接入.md
    - Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务05c-产品目录与Agent分层重构.md
  dependents:
    - Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务06-在线闭环验收.md
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 子任务 05d：dotenv 本地配置

## 一、需求分析（开工门禁）

- 需求 plan：`Plans/需求分析/2026-08-03-R4真实DeepSeek学习智能接入.md`。
- 用户反馈 shell 环境未被后端继承，要求直接修改代码解决本地 Key 加载。
- API 与 DeepSeek 调用契约不变，只增加安全的本地配置适配层。

## 二、原子目标

后端启动时自动读取仓库根目录 `.env`，支持 `--env-file`，且进程环境变量优先；真实 `.env` 必须被 Git 忽略，只提交 `.env.example`。

## 三、验收

- [x] `config.py` 使用 `python-dotenv` 加载仓库根目录 `.env`。
- [x] 已存在的进程环境变量不会被 `.env` 覆盖。
- [x] CLI 支持 `--env-file` 并只输出配置是否加载，不输出 Secret。
- [x] `.env` / `.env.*` 被忽略，`.env.example` 可提交。
- [x] 配置加载与优先级测试通过；Backend 99 + Agent 45，共 144 tests。

## 四、续做

`/resume plan=Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务06-在线闭环验收.md 进度=dotenv自动加载完成；在根目录创建.env并重启后端后执行live smoke`

## 五、反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务05d-dotenv本地配置.md
  date: 2026-08-03
  contexts_used:
    - path: Plans/技术方案/2026-08-03-R4真实DeepSeek学习智能接入.md
      utility: high
      reason: "保持 DeepSeek adapter 与 CLI 入站适配器边界，只在 backend config 层增加本地 Secret 加载。"
    - path: Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务05c-产品目录与Agent分层重构.md
      utility: high
      reason: "沿用 knowledge_graph_learning 产品目录和 .runtime/本地边界，不把配置逻辑重新塞回 agent 底座。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
