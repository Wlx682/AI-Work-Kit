# backlog-prioritization-assistant · Backlog 需求排序

用于 `client-dev` 的 `prioritization` 阶段。读取已采纳需求 Plan，按业务价值、紧迫度、风险验证价值和依赖生成团队确认的有序 Backlog。

产物为 `Plans/需求排序/YYYY-MM-DD-标题.md` 和同名 `.backlog.json`。每项需求必须包含 `id/title/business_value/urgency/dependencies/priority/reason/confirmed`。本阶段不填写故事点、工时、架构或开发任务。

门禁：`python3 scripts/validate-client-dev.py backlog --plan Plans/需求排序/xxx.md`。阶段反馈必须包含 `workflow_stage: prioritization`。
