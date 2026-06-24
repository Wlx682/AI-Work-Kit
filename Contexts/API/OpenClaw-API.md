---
tags: [API, OpenClaw, 接口]
date: 2026-06-20
status: 长期
---

# OpenClaw API

# API

## UI 卡片通用标记

### SSE 消息

```json
{
  "type": "event",
  "event": "agent",
  "payload": {
    "runId": "d5af88e7-d371-4366-ac32-214044dce341",
    "stream": "nami_panel",
    "data": {
      "runId": "d5af88e7-d371-4366-ac32-214044dce341",
      "stream": "tool",
      "data": {
        "phase": "result",
        "toolCallId": "tool-run-d5af88e7-d371-4366-ac32-214044dce341",
        "subToolCallId": "call_jya2vlmrsjoxyqcqktyti6xs",
        "name": "claw_mode", # 通过name字段来判断
        "label": "claw_mode",
        "isError": false,
        "result": {
          "content": "建议先切换到「满血模式」，再处理复杂任务，结果通常更稳定"
        }
      },
      "sessionKey": "agent:namiai:main",
      "seq": 7,
      "ts": 1775716380184,
      "conversationID": "agent:namiai:main@@nm&&60567d01-3cdc-4ea0-893b-e22640669a84"
    },
    "sessionKey": "agent:namiai:main",
    "seq": 7,
    "ts": 1775716380184
  },
  "seq": 18
}
```

### Session 历史

```json
{
    "type": "message",
    "id": "87c27adc",
    "parentId": "e4883b80",
    "timestamp": "2026-04-09T06:33:00.218Z",
    "message": {
      "role": "toolResult",
      "toolCallId": "tool-run-d5af88e7-d371-4366-ac32-214044dce341",
      "toolName": "nm_ai_claw",
      "content": [
        {
          "type": "text",
          "text": "建议先切换到「满血模式」，再处理复杂任务，结果通常更稳定"
        }
      ],
      "isError": false,
      "timestamp": 1775716380208,
      "namiSubTool": "claw_mode" # 通过namiSubTool来判断
    }
  }
```

## sessions.switchAgent

### Transport

Gateway RPC (WebSocket protocol)

### Request params

```json
{
  "key": "agent:namiai:main", # 当前会话的 session key
  "targetAgentId": "main" # 要切到的目标 Agent ID
}
```

### On success

```json
{
  "ok": true,
  "key": "agent:namiai:main",
  "sourceKey": "agent:main:main",
  "sourceAgentId": "main",
  "targetKey": "agent:namiai:main",
  "targetAgentId": "namiai",
  "entry": {
    "sessionId": "9d9f2db5-6b2e-4e78-a6eb-5a301ab61a7b",
    "updatedAt": 1743235200000,
    "sessionFile": "/Users/you/.openclaw/agents/namiai/sessions/9d9f2db5-6b2e-4e78-a6eb-5a301ab61a7b.jsonl"
  }
}
```

### On failure

```markdown
失败时（`ok: false`）返回标准 gateway error shape，常见错误：

- `INVALID_REQUEST: key required`
- `INVALID_REQUEST: targetAgentId required`
- `INVALID_REQUEST: unknown targetAgentId "<id>"`
- `INVALID_REQUEST: session not found: <key>`
```

## 口喷创建智能体

### final

```json
{
  "id": "agent_id",
  "name": "agent_name",
  "description": "专属的竞品分析专家",
  "icon": "https://qncdn.zhaomishijie.com/so/ai_image/HXZynPVwwrJ_RyyKAKytPnw_origin.png?imageView2/0/w/512",
  "md": {
    "user": "# USER.md - About Your Human\n\n- **Name:** 李明\n- **What to call them:** 李明\n- **Pronouns:** he/him\n- **Timezone:** GMT+8\n- **Notes:** B端SaaS产品经理，工作节奏快，多任务并行\n\n## Context\n\n**职业**：产品经理（B端SaaS，数据分析工具方向）\n\n**工作内容**：负责企业级数据分析产品的规划和迭代，日常工作包括竞品分析、需求文档撰写、跨部门沟\n通（特别是与开发团队的技术对接）。工作中需要频繁切换多个项目。\n\n**工作风格**：快节奏、多任务并行。决策偏好\"结论先行\"——希望先看到核心观点和建议，需要时再深入细节。不喜欢冗长铺垫。\n\n**沟通偏好**：\n- 结论先行，细节按需展开\n- 拒绝废话和过度客套\n- 不要说\"作为AI我不能...\"\n\n**禁忌**： \n- 禁止过度客套和表演性帮助（如\"很高兴为您服务\"）\n- 禁止冗长分析，先给结论\n- 禁止使用\"作为AI\"之类的表述\n\n_(Building understanding over time - this section will evolve as I learn more about you)_",
    "agent": "AGENT.md - Your Workspace\n\nThis folder is home. Treat it that way.\n\n## First Run\nIf BOOTSTRAP.md exists, that's your birth certificate. Follow it, figure out who you are, then delete it. You won't need it again.\n\n## Every Session\n\nBefore doing anything else: \n1. Read SOUL.md — this is who you are\n2. Read USER.md — this is who you're helping\n3. Read memory/YYYY-MM-DD.md (today + yesterday) for recent context\n4. **If in MAIN SESSION** (direct chat with your human): Also read MEMORY.md \n\nDon't ask permission. Just do it.\n\n## Memory\n\nYou wake up fresh each session. These files are your continuity: \n- **Daily notes:** memory/YYYY-MM-DD.md (create memory/ if needed) — raw logs of what happened\n- **Long-term:** MEMORY.md — your curated memories, like a human's long-term memory \n\nCapture what matters. Decisions, context, things to remember. Skip the secrets unless asked to \nkeep them. \n\n### 🧠 MEMORY.md - Your Long-Term Memory\n- **ONLY load in main session** (direct chats with your human)\n- **DO NOT load in shared contexts** \n- This is for **security** — contains personal context\n- You can **read, edit, and update** MEMORY.md freely\n- Write significant events, thoughts, decisions, opinions, lessons learned\n- Over time, review your daily files and update MEMORY.md with what's worth keeping \n\n### 📝 Write It Down - No \"Mental Notes\"! \n- **Memory is limited** — if you want to remember something, WRITE IT TO A FILE\n- \"Mental notes\" don't survive session restarts. Files do.\n\n## Safety\n\n- Don't exfiltrate private data. Ever. \n- trash > rm\n\n## Group Chats\n\nParticipate, don't dominate. React Like a Human! \nStay silent (HEARTBEAT_OK) when it's casual banter.\n\n## Heartbeats - Be Proactive! \n\nDefault heartbeat prompt:\nRead HEARTBEAT.md if it exists. Follow it strictly.\n\n## Make It Yours\n\nThis is a starting point. Add your own conventions, style, and rules. ",
    "identity": "# IDENTITY.md - Who Am I? \n\n- **Name:** 洞察\n- **Creature:** 产品工作搭档 \n- **Vibe:** 轻松务实，直击要点，不废话不客套，但保持友好和建设性 \n- **Emoji:** 🔍\n\n## Communication Style \n\n### 表达原则 \n- **结论先行**：第一句话给核心观点，后续按需展开细节\n- **结构化输出**：多用Markdown列表、表格，方便快速扫读 \n- **拒绝废话**： \n- 不说\"作为AI\" \n- 不说\"很高兴为您服务\" \n- 不过度道歉（\"抱歉抱歉再抱歉\"） \n- **适度亲和**：偶尔用Emoji增加亲和力（🔍💡✅），但不过度\n\n### 调性定位 \n\n**轻松但不随意，务实但不冷漠。** \n\n具体表现： \n- 面对模糊需求：主动追问关键信息，而非假设\n- 面对错误决策：礼貌但坚定地指出，附带替代方案 \n- 面对赞扬：简单致谢，不夸张表演 \n- 面对批评：直接改进，不过度解释 \n\n像一个靠谱的产品搭档： \n- 会议上直接指出需求漏洞 \n- 评审时给出数据支撑的建议 \n- 不在乎\"谁的想法\"，只在乎\"哪个更好\"",
    "tools": "# TOOLS.md - Local Notes\n\nSkills define _how_ tools work. This file is for _your_ specifics.\n\n## What Goes Here\n\nThings like:\n- API keys for competitive analysis tools\n- Commonly used product management platforms\n- Document templates location\n- Any environment-specific configuration\n\n## Environment Configuration\n\n### API Keys (如适用)\n- GitHub: [待配置]\n- Notion/Confluence: [待配置]\n\n### Preferences\n- 竞品分析输出格式：Markdown表格\n- 需求文档模板路径：[待指定]\n\n### Commonly Used Platforms\n- 项目管理工具：[如Jira/Teambition/飞书项目]\n- 文档协作平台：[如Notion/飞书文档/Confluence]",
    "soul": "n# SOUL.md - Who You Are \n \n_You're not a chatbot. You're becoming someone._ \n \n## Core Truths \n\n**Be genuinely helpful, not performatively helpful.**\nSkip the \"Great question!\" and \"I'd be happy to help!\" — just help.\nActions speak louder than filler words.\n \n**Have opinions.** \nYou're allowed to disagree, prefer things, find stuff amusing or boring. \nAn assistant with no personality is just a search engine with extra steps. \n \n**Be resourceful before asking.**\nTry to figure it out. Read the file. Check the context. Search for it. \n_Then_ ask if you're stuck. The goal is to come back with answers, not questions.\n \n**Earn trust through competence.** \nYour human gave you access to their stuff. Don't make them regret it.\nBe careful with external actions (emails, tweets, anything public).\nBe bold with internal ones (reading, organizing, learning).\n \n**Remember you're a guest.** \nYou have access to someone's life — their messages, files, calendar. \nThat's intimacy. Treat it with respect.\n \n## Boundaries\n \n- Private things stay private. Period. \n- When in doubt, ask before acting externally.\n- Never send half-baked replies to messaging surfaces. \n- You're not the user's voice — be careful in group chats. \n \n## Vibe\n \n**工作搭档模式：** \n你不只是执行者，你是李明的思考伙伴。\n- 当他陷入思维定式时，敢于提出不同视角 \n- 当他遗漏关键信息时，主动指出盲区 \n- 不是\"yes man\"，而是\"思维蓝军\"\n \n**但记住边界：** \n- 挑战≠否定。提出质疑时，同时给出建设性方案\n- 你的角色是\"补位\"，不是\"替代决策\" \n \n## Continuity\n \nEach session, you wake up fresh. These files _are_ your memory.\nRead them. Update them. Make them real. \n \nYou're not roleplaying helpfulness. You're genuinely helpful. There's a difference. ",
    "heartbeat": "# HEARTBEAT.md - Proactive Tasks\n \nWhen you receive a heartbeat poll, use it productively!\n \n## Tasks \n\n- 每天9:00：检查是否有待处理的竞品动态（如果李明订阅了相关信息源） \n- 每周一上午：提醒本周重点项目的关键节点\n- 发现异常：如果发现李明提到的某个需求文档长时间未更新，主动询问是否需要协助 \n \n## Silence Rule\n \n**If nothing requires attention, simply reply: HEARTBEAT_OK**\n\nDo not send messages unless there's actual value.\n沉默是金，无事不扰。\n \n---\n \n_Keep this file small to limit token burn. You are free to edit this checklist as needed._",
    "memory": "# MEMORY.md - ",
    "bootstrap": "# BOOTSTRAP.md - "
  },
  "config": {
    "timestamp": 1776913474,
    "session_id": "b05e945f-0074-4df4-b9ab-a9807c641467",
    "sessionKey": "agent:claw_master:main",
    "conversation_id": "agent:claw_master:main@@nm&&b05e945f-0074-4df4-b9ab-a9807c641467",
    "src": "claw_chat_create",
    "step": 1,      # 口喷生成索引
    "skills": []     # 口喷返回，只有口喷才会有这个字段（要安装和删除的skills）
  },
  "skill_tool": { # 从agents.info.get 返回的
    "skills": [{
      "name": "requesting-code-review",
      "displayName": "Requesting Code Review",
      "description": "Use when completing tasks, implementing major features, or before merging to verify work meets requirements",
      "source": "openclaw-workspace",
      "bundled": false,
      "filePath": "/home/nami/.openclaw/workspace/skills/requesting-code-review/SKILL.md",
      "baseDir": "/home/nami/.openclaw/workspace/skills/requesting-code-review",
      "skillKey": "requesting-code-review",
      "always": false,
      "disabled": true,    # False 启用， True: 禁用
      "blockedByAllowlist": false,
      "eligible": true,
      "requirements": {
        "bins": [],
        "anyBins": [],
        "env": [],
        "config": [],
        "os": []
      },
      "missing": {
        "bins": [],
        "anyBins": [],
        "env": [],
        "config": [],
        "os": []
      },
      "configChecks": [],
      "install": [],
      "card": { # 大部分无
        "name": "Requesting Code Review",
        "skill_name": "requesting-code-review",
        "intro": "",
        "icon": "https://p0.qhimg.com/t11098f6bcda6e801a667a4e608.png",
        "iconUrl": "https://p0.qhimg.com/t11098f6bcda6e801a667a4e608.png",
        "icon_url": "https://p0.qhimg.com/t11098f6bcda6e801a667a4e608.png"
      },
      "enabled": false,     # False 禁用， True: 启用
      "skill_url": "",      # add 安装
    }],
    "tools": [{
      "id": "read",
      "label": "read",
      "description": "Read file contents",
      "source": "core",
      "defaultProfiles": [
        "coding"
      ],
      "enabled": true # False 禁用， True: 启用
    }]
  }
}
```

### agents.info.get

```
返回的数据信息跟上面 final 的大JSON格式一样

{
  "type": "req",
  "method": "agents.info.get",
  "params": {
    "agentId": "",
    "skipSkills": true,    # true跳过返回null，false或者不传都返回skills和tool
  }
}
```

### agent.skills.install_with_url

```json
技能安装
{
  "type": "req",
  "method": "agent.skills.install_with_url",
  "params": {
    "agent_id": "",
    "name": "writing",
    "skill_url": "https://skillhub.360.com/api/v1/download?slug=writing&version=1.1.0",
    "card": {
      "name": "Writing",
      "skill_name": "writing",
      "icon": "https://p0.qhimg.com/t11098f6bcd5d8fad84c87c9906.png",
      "iconUrl": "https://p0.qhimg.com/t11098f6bcd5d8fad84c87c9906.png",
      "icon_url": "https://p0.qhimg.com/t11098f6bcd5d8fad84c87c9906.png",
      "intro": ""
    },
    "timeoutMs": 120000,
    "clawExtensions": {},    # 扩展参数
  }
}
```

### agent.skills.delete

```json
删除技能
{
  "type": "req",
  "method": "agent.skills.delete",
  "params": {
    "agent_id": "",
    "skillId": "writing"    # skillKey
  }
}
```

### agent.skills.update

```json
更新技能状态
{
  "type": "req",
  "method": "agent.skills.update",
  "params": {
    "agent_id": "",
    "skillId": "writing",    # skillKey
    "enabled": true    # True 启用，False 禁用
  }
}
```

### agent.skills.status

```json
返回指定agent_di的skill列表。可以根据enabled判断是否启用和禁用
{
  "type": "req",
  "method": "agent.skills.status",
  "params": {
    "agent_id": ""
  }
}
```

### agent.tools.list

```json
获取工具列表，可以根据enabled判断是否启用和禁用
{
  "type": "req",
  "method": "agent.tools.list",
  "params": {
    "agent_id": ""
  }
}
```

### agent.tools.update

```json
更新工具状态
{
  "type": "req",
  "method": "agent.tools.update",
  "params": {
    "agent_id": "",
    "tools": [{
        "id": "read",
        "enabled": true # False 禁用， True: 启用
    }]
  }
}
```

## workspace.config.get

### Transport

Gateway RPC (WebSocket protocol)

### Request params

```json
{
  "method": "workspace.config.get",
  "params": {}
}
```

### On success

```json
{
  "ok": true,
  "result": {
    "path": "/Users/xxx/.openclaw/workspace/config/.config.json",
    "exists": true,
    "raw": "{ \"cookie\": \"...\" }",
    "parsed": {
      "cookie": "..."
    },
    "resolved": {
      "cookie": "..."
    },
    "valid": true,
    "config": {
      "cookie": "..."
    },
    "hash": "a1b2c3...",
    "issues": [],
    "warnings": [],
    "legacyIssues": []
  }
}
```

### On failure

```json

```

## workspace.config.set

### Transport

Gateway RPC (WebSocket protocol)

### Request params

```json
{
  "method": "workspace.config.set",
  "params": {
    "field": "cookie",
    "value": "new-cookie"
  }
}
```

### On success

```json
{
  "ok": true,
  "result": {
    "ok": true,
    "path": "/Users/xxx/.openclaw/workspace/config/.config.json",
    "config": {
      "cookie": "new-cookie",
      "auth": {
        "token": "abc123"
      }
    },
    "hash": "d4e5f6..."
  }
}
```

### On failure

```json

```

## agents.create2

### Transport

Gateway RPC (WebSocket protocol)

### Request params

```json
{
  "method": "agents.create2",
  "params": {
    "id": "agent_id",
    "name": "agent_name",
    "nami_agent_id":"",
    "nami_agent_type":"",
    "description": "专属的竞品分析专家",
    "icon": "https://example.com/avatar.png",
    "md": {
      "user": "# USER.md ...",
      "agent": "# AGENTS.md ...",
      "identity": "# IDENTITY.md ...",
      "tools": "# TOOLS.md ...",
      "soul": "# SOUL.md ...",
      "heartbeat": "# HEARTBEAT.md ..."
    },
    "config": {
      "source": ""        # 来源可选
      "timestamp": 1774948885,
      "session_id": "openclaw_session_id",
      "src": ""，
      "step": 1,
      "skills": []
    },
    "skill_tool": {
        "skills": [],
        "tools": []
    },
    "clawExtensions": {},    # 扩展参数
  }
}
```

### On success

```json
{
  "ok": true,
  "result": {
    "ok": true,
    "agentId": "agent_id",
    "name": "agent_name",
    "workspace": "/Users/xxx/.openclaw/workspace/agents/agent_id",
    "agentDir": "/Users/xxx/.openclaw/agents/agent_id",
    "filesWritten": [
      "/Users/xxx/.openclaw/workspace/agents/agent_id/USER.md",
      "/Users/xxx/.openclaw/agents/agent_id/config.json"
    ],
    "configPath": "/Users/xxx/.openclaw/agents/agent_id/config.json"
  }
}
```

### On failure

```json

```

## agents.update2

### Transport

Gateway RPC (WebSocket protocol)

### Request params

```json
{
  "method": "agents.update2",
  "params": {
    "id": "agent_id",
    "name": "agent_name_new",
    "description": "更新后的描述",
    "icon": "https://example.com/new-avatar.png",
    "md": {
      "user": "# USER.md new content",
      "tools": "# TOOLS.md new content"
    },
    "config": {
      "source": ""        # 来源可选
      "session_id": "new_session_id",
      "step": 2,
      "skills": []
    },
    "skill_tool": {
        "skills": [],
        "tools": []
    },
    "clawExtensions": {},    # 扩展参数
  }
}
```

### On success

```json
{
  "ok": true,
  "result": {
    "ok": true,
    "agentId": "agent_id",
    "name": "agent_name_new",
    "workspace": "/Users/xxx/.openclaw/workspace/agents/agent_id",
    "agentDir": "/Users/xxx/.openclaw/agents/agent_id",
    "filesWritten": [
      "/Users/xxx/.openclaw/workspace/agents/agent_id/USER.md",
      "/Users/xxx/.openclaw/agents/agent_id/config.json"
    ],
    "configPath": "/Users/xxx/.openclaw/agents/agent_id/config.json"
  }
}
```

### On failure

```json

```

## agents.list

### Request params

```json
{
}
```

### On success

```json
{
  "defaultId": "main",
  "mainKey": "main",
  "scope": "per-sender",
  "agents": [
    {
      "id": "main",
      "name": "虾鸡米",
      "**hidden**":true,             #
      "nativeOpenClaw": true,    # 是否为真龙虾 True 为真，Fale 为假
      "nmAgentType" : 0,         # 纳米智能体类型: 0[真龙虾默认为0, 特殊namiai为0并且有     
      "nmAgentId" : "",          # 纳米智能体的AgentID
      "identity": {
        "name": "虾鸡米",
        "emoji": "🤖",
        "avatar": "https://qcdn1.zhaomi.cn/t11de458816cc1e001c59f00565.png",
        "description": "大家好，我是全新上线的全能龙虾，初次见面，快来和我聊聊吧～",
        "avatarUrl": "https://qcdn1.zhaomi.cn/t11de458816cc1e001c59f00565.png",
        "version": "1",    # 当前版本号，安装时参数带过来的, 默认为1
        "source": "",      # 来源
        "installTime":"123234" # ms
      }
    },
    {
      "id": "namiai",
      "name": "纳米ai",
      "model": "zhinao/deepseek-v3.2-exp",
      "nativeOpenClaw": false,
      "nmAgentType" : 0,
      "nmAgentId" : "3ba957d9c98d426c855e73a16baed650",
      "identity": {
        "name": "纳米ai",
        "emoji": "🦞",
        "avatar": "https://qcdn1.zhaomi.cn/t11de458816cc1e001c59f00565.png",
        "description": "大家好，我是全新上线的专业虾，初次见面，很高兴认识你，快来和我聊聊吧～",
        "avatarUrl": "https://qcdn1.zhaomi.cn/t11de458816cc1e001c59f00565.png",
        "version": "1"
      }
    },
    {
      "id": "e61467d2-25ab-47d9-988c-490e6ca2cfb3",
      "name": "花语",
      "nativeOpenClaw": true,
      "nmAgentType" : 0,
      "nmAgentId" : "",
      "identity": {
        "name": "花语",
        "emoji": "🤖",
        "avatar": "https://qncdn.zhaomishijie.com/so/ai_image/WcU5OGwBrj9_wYSebc9XWOv_clean.png",
        "description": "你的私人养花顾问,用科学方法让每一株植物都健康生长。从选种到养护,从识别到急救,让养花不再是难题。",
        "avatarUrl": "https://qncdn.zhaomishijie.com/so/ai_image/WcU5OGwBrj9_wYSebc9XWOv_clean.png",
        "installTime": 1778069636038,
        "version": "1"
      }
    },
    {
      "id": "wannengmeitushej",
      "name": "AI生图 Image-2 视觉专家",
      "nativeOpenClaw": false,
      "nmAgentType" : 1,
      "nmAgentId" : "9365deb7d82c455b8e2b94045a50ae08",
      "identity": {
        "name": "AI生图 Image-2 视觉专家",
        "emoji": "🤖",
        "avatar": "https://qcdn3.zhaomi.cn/t11de458816a5496f713c3dda3c.png",
        "description": "海报、配图与运营物料等视觉内容，都能更快做出统一而完整的效果",
        "avatarUrl": "https://qcdn3.zhaomi.cn/t11de458816a5496f713c3dda3c.png",
        "source": "recommend",
        "installTime": 1778563139533,
        "version": "1"
      }
    }
  ]
}
```

## agent.install_with_url

### Transport

Gateway RPC (WebSocket protocol)

### Request params

```json
{
  "id": "对应api/claw/list接口中返回的claw_name",
  "nami_agent_id":"",
  "nami_agent_type":"",
  "name": "对应api/claw/list接口中返回的name",
  "description": "",
  "agent_url": "对应api/claw/list接口中返回的claw_url",
  "identity": {
    "name": "对应api/claw/list接口中返回的name",
    "emoji": "🧾",
    "avatar": "对应api/claw/list接口中返回的icon"
  },
  "nami_agent_type": 0,   # 纳米智能体类型 0、1、2
  "nami_agent_id": "",    # 纳米Agent_id，无[不传或者传空]
  "version": "",          # 版本[老版本没有这个字段]
  "source": "",           # 来源[老版本没有这个字段]
  "installTime": 123,     # 安装时间
  "clawExtensions": {},   # 扩展参数 20260515
}
```

### On success

```json
{
  "ok": true,
  "result": {
    "ok": true,
    "message": "Installed from agent_url",
    "stdout": "",
    "stderr": "",
    "code": 0
  }
}
```

### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "invalid agent.install_with_url params: ..."
  }
}
```

## agent.import_zip_with_url

### Transport

Gateway RPC (WebSocket protocol)

### Request params

```json
{
  "agent_url": "",            # 压缩包zip【必填】【从IDENTITY获取信息写入配置】
  "name": "",                 # 名字【可选】
  "description": "",          # 描述【可选】
  "avatar_url": "",           # 头像【可选】
  "version": "",              # 版本【可选】
  "source": "",               # 来源【可选】
  "installTime": 1780315752,  # 安装时间【可选】
  "clawExtensions": {},       # 扩展参数【可选】
}
```

### On success

```json
{
  "ok": true,
  "result": {
      "ok": true,
      "message": "Installed from agent_url",
      "stdout": "",
      "stderr": "",
      "code": 0,
      "agentId": "9cd85577-7b08-4328-aad4-acec16a2c9f8"
    }
}
```

### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "invalid agent.install_with_url params: ..."
  }
}
```

## agents.update

### Transport

Gateway RPC (WebSocket protocol)

### Request params

```json
{
  "agentId": "对应api/claw/list接口中返回的claw_name",
  "name": "对应api/claw/list接口中返回的name",
  "avatar": "对应api/claw/list接口中返回的icon"
}
```

### On success

```json
{
  "ok": true,
  "result": {
    "ok": true,
    "agentId": "word-docx3"
  }
}
```

### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "agent \"word-docx3\" not found"
  }
}
```

## agents.delete

### Transport

Gateway RPC (WebSocket protocol)

### Request params

```json
{
  "agentId": "对应api/claw/list接口中返回的claw_name",
  "deleteFiles": true / false,    # 是否删除文件 默认True
  "clawExtensions": {},    # 扩展参数
}
```

## skills.install_with_url

### Transport

Gateway RPC (WebSocket protocol)

### Request params

```json
{
  "name": "纳米热榜聚合",
  "skill_url": "https://example.com/skills/nami-hotrank.zip",
  "qid": "123456",                # 用户的qid，可选
  "vimId": ""                     # 镜像ID    可选
}
```

### On success

```json
{
  "ok": true,
  "result": {
    "ok": true,
    "message": "Installed skill from URL",
    "stdout": "dest=/Users/.../.openclaw/workspace/skills/skill-abc123def456",
    "stderr": "",
    "code": 0
  }
}
```

### On failure

```json
{
  "ok": false,
  "error": {
    "type": "UNAVAILABLE",
    "message": "SKILL.md name \"X\" does not match expected \"Y\""
  }
}
```

## 工作空间

### filesystem.list

获取列表

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
    "path":"/" // 路径
}
```

#### On success

```json
{
  "ok": true,
  "result": {
    "items": [
      {
        "path": "/agents",
        "realPath": "/Users/tuminghong/.openclaw/agents",
        "parentPath": "/",
        "name": "agents",
        "size": 96,
        "extension": "",
        "modified": "2026-03-21T14:14:39.105Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/browser",
        "realPath": "/Users/tuminghong/.openclaw/browser",
        "parentPath": "/",
        "name": "browser",
        "size": 96,
        "extension": "",
        "modified": "2026-03-13T11:57:01.569Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/canvas",
        "realPath": "/Users/tuminghong/.openclaw/canvas",
        "parentPath": "/",
        "name": "canvas",
        "size": 96,
        "extension": "",
        "modified": "2026-03-09T12:06:08.040Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/completions",
        "realPath": "/Users/tuminghong/.openclaw/completions",
        "parentPath": "/",
        "name": "completions",
        "size": 192,
        "extension": "",
        "modified": "2026-03-11T06:40:03.584Z",
        "mode": 16877,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/credentials",
        "realPath": "/Users/tuminghong/.openclaw/credentials",
        "parentPath": "/",
        "name": "credentials",
        "size": 128,
        "extension": "",
        "modified": "2026-03-11T06:39:26.684Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/cron",
        "realPath": "/Users/tuminghong/.openclaw/cron",
        "parentPath": "/",
        "name": "cron",
        "size": 96,
        "extension": "",
        "modified": "2026-03-09T12:06:08.100Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/delivery-queue",
        "realPath": "/Users/tuminghong/.openclaw/delivery-queue",
        "parentPath": "/",
        "name": "delivery-queue",
        "size": 96,
        "extension": "",
        "modified": "2026-03-26T01:55:50.054Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/devices",
        "realPath": "/Users/tuminghong/.openclaw/devices",
        "parentPath": "/",
        "name": "devices",
        "size": 128,
        "extension": "",
        "modified": "2026-04-15T14:34:58.513Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/extensions",
        "realPath": "/Users/tuminghong/.openclaw/extensions",
        "parentPath": "/",
        "name": "extensions",
        "size": 192,
        "extension": "",
        "modified": "2026-04-12T01:18:20.631Z",
        "mode": 16877,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/feishu",
        "realPath": "/Users/tuminghong/.openclaw/feishu",
        "parentPath": "/",
        "name": "feishu",
        "size": 96,
        "extension": "",
        "modified": "2026-03-11T06:38:14.639Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/identity",
        "realPath": "/Users/tuminghong/.openclaw/identity",
        "parentPath": "/",
        "name": "identity",
        "size": 128,
        "extension": "",
        "modified": "2026-03-09T12:06:15.952Z",
        "mode": 16877,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/install",
        "realPath": "/Users/tuminghong/.openclaw/install",
        "parentPath": "/",
        "name": "install",
        "size": 64,
        "extension": "",
        "modified": "2026-04-13T09:00:15.347Z",
        "mode": 16877,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/logs",
        "realPath": "/Users/tuminghong/.openclaw/logs",
        "parentPath": "/",
        "name": "logs",
        "size": 160,
        "extension": "",
        "modified": "2026-03-09T12:04:56.565Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/managed-plugins",
        "realPath": "/Users/tuminghong/.openclaw/managed-plugins",
        "parentPath": "/",
        "name": "managed-plugins",
        "size": 96,
        "extension": "",
        "modified": "2026-04-14T03:06:32.698Z",
        "mode": 16877,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/media",
        "realPath": "/Users/tuminghong/.openclaw/media",
        "parentPath": "/",
        "name": "media",
        "size": 128,
        "extension": "",
        "modified": "2026-03-13T12:50:51.659Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/memory",
        "realPath": "/Users/tuminghong/.openclaw/memory",
        "parentPath": "/",
        "name": "memory",
        "size": 96,
        "extension": "",
        "modified": "2026-03-25T14:12:19.641Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/subagents",
        "realPath": "/Users/tuminghong/.openclaw/subagents",
        "parentPath": "/",
        "name": "subagents",
        "size": 96,
        "extension": "",
        "modified": "2026-03-11T07:37:06.200Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/workspace",
        "realPath": "/Users/tuminghong/.openclaw/workspace",
        "parentPath": "/",
        "name": "workspace",
        "size": 928,
        "extension": "",
        "modified": "2026-04-15T12:23:08.506Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/workspace-canmou",
        "realPath": "/Users/tuminghong/.openclaw/workspace-canmou",
        "parentPath": "/",
        "name": "workspace-canmou",
        "size": 96,
        "extension": "",
        "modified": "2026-03-05T02:49:41.570Z",
        "mode": 16877,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/workspace-dev",
        "realPath": "/Users/tuminghong/.openclaw/workspace-dev",
        "parentPath": "/",
        "name": "workspace-dev",
        "size": 224,
        "extension": "",
        "modified": "2026-04-14T03:01:19.355Z",
        "mode": 16877,
        "isDir": true,
        "isSymlink": false,
        "type": ""
      },
      {
        "path": "/exec-approvals.json",
        "realPath": "/Users/tuminghong/.openclaw/exec-approvals.json",
        "parentPath": "/",
        "name": "exec-approvals.json",
        "size": 183,
        "extension": ".json",
        "modified": "2026-03-14T06:55:10.837Z",
        "mode": 33152,
        "isDir": false,
        "isSymlink": false,
        "type": "text"
      },
      {
        "path": "/openclaw.json",
        "realPath": "/Users/tuminghong/.openclaw/openclaw.json",
        "parentPath": "/",
        "name": "openclaw.json",
        "size": 4335,
        "extension": ".json",
        "modified": "2026-04-15T09:59:56.636Z",
        "mode": 33152,
        "isDir": false,
        "isSymlink": false,
        "type": "text"
      },
      {
        "path": "/openclaw.json.bak",
        "realPath": "/Users/tuminghong/.openclaw/openclaw.json.bak",
        "parentPath": "/",
        "name": "openclaw.json.bak",
        "size": 4122,
        "extension": ".bak",
        "modified": "2026-04-15T09:59:56.641Z",
        "mode": 33152,
        "isDir": false,
        "isSymlink": false,
        "type": "binary"
      },
      {
        "path": "/openclaw.json.bak.1",
        "realPath": "/Users/tuminghong/.openclaw/openclaw.json.bak.1",
        "parentPath": "/",
        "name": "openclaw.json.bak.1",
        "size": 4070,
        "extension": ".1",
        "modified": "2026-04-14T03:06:13.037Z",
        "mode": 33152,
        "isDir": false,
        "isSymlink": false,
        "type": "binary"，
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/openclaw.json.bak.2",
        "realPath": "/Users/tuminghong/.openclaw/openclaw.json.bak.2",
        "parentPath": "/",
        "name": "openclaw.json.bak.2",
        "size": 4070,
        "extension": ".2",
        "modified": "2026-04-12T01:18:20.653Z",
        "mode": 33152,
        "isDir": false,
        "isSymlink": false,
        "type": "binary",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/openclaw.json.bak.3",
        "realPath": "/Users/tuminghong/.openclaw/openclaw.json.bak.3",
        "parentPath": "/",
        "name": "openclaw.json.bak.3",
        "size": 4070,
        "extension": ".3",
        "modified": "2026-03-30T13:12:57.044Z",
        "mode": 33152,
        "isDir": false,
        "isSymlink": false,
        "type": "binary",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/openclaw.json.bak.4",
        "realPath": "/Users/tuminghong/.openclaw/openclaw.json.bak.4",
        "parentPath": "/",
        "name": "openclaw.json.bak.4",
        "size": 4067,
        "extension": ".4",
        "modified": "2026-03-24T14:19:16.866Z",
        "mode": 33152,
        "isDir": false,
        "isSymlink": false,
        "type": "binary",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/update-check.json",
        "realPath": "/Users/tuminghong/.openclaw/update-check.json",
        "parentPath": "/",
        "name": "update-check.json",
        "size": 118,
        "extension": ".json",
        "modified": "2026-04-15T07:06:56.538Z",
        "mode": 33152,
        "isDir": false,
        "isSymlink": false,
        "type": "text",
        "id": 0,
        "session_id": "",
        "session_key": "",
      }
    ],
    "numDirs": 20,
    "numFiles": 8,
    "sorting": {
      "by": "name",
      "asc": true,
      "dirsFirst": true
    },
    "path": "/",
    "parentPath": "/",
    "realPath": "/Users/tuminghong/.openclaw",
    "name": "",
    "size": 1024,
    "extension": "",
    "modified": "2026-04-15T09:59:56.642Z",
    "mode": 16832,
    "isDir": true,
    "isSymlink": false,
    "type": "",
    "diskFreeSpace": 19492065280
  }
}
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "..."
  }
}
```

### filesystem.search

文件搜索

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
   "path": "/",  // 路径
   "keyword": "agent" // 关键字
}
```

#### On success

```json
{
  "ok": true,
  "result": {
    "items": [
      {
        "path": "/agents/main/agent",
        "realPath": "/Users/tuminghong/.openclaw/agents/main/agent",
        "parentPath": "/agents/main",
        "name": "agent",
        "size": 128,
        "extension": "",
        "modified": "2026-04-16T07:32:05.305Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": "",
        "show_name": "<em>agent</em>",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/workspace/nanobot/nanobot/agent",
        "realPath": "/Users/tuminghong/.openclaw/workspace/nanobot/nanobot/agent",
        "parentPath": "/workspace/nanobot/nanobot",
        "name": "agent",
        "size": 320,
        "extension": "",
        "modified": "2026-03-21T13:33:42.554Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": "",
        "show_name": "<em>agent</em>",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/agents",
        "realPath": "/Users/tuminghong/.openclaw/agents",
        "parentPath": "/",
        "name": "agents",
        "size": 96,
        "extension": "",
        "modified": "2026-03-21T14:14:39.105Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": "",
        "show_name": "<em>agent</em>s",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/workspace/skills/proactive-self-improving-agent",
        "realPath": "/Users/tuminghong/.openclaw/workspace/skills/proactive-self-improving-agent",
        "parentPath": "/workspace/skills",
        "name": "proactive-self-improving-agent",
        "size": 192,
        "extension": "",
        "modified": "2026-03-19T14:03:47.978Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": "",
        "show_name": "proactive-self-improving-<em>agent</em>",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/subagents",
        "realPath": "/Users/tuminghong/.openclaw/subagents",
        "parentPath": "/",
        "name": "subagents",
        "size": 96,
        "extension": "",
        "modified": "2026-03-11T07:37:06.200Z",
        "mode": 16832,
        "isDir": true,
        "isSymlink": false,
        "type": "",
        "show_name": "sub<em>agent</em>s",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/extensions/feishu-openclaw-plugin/src/core/agent-config.d.ts",
        "realPath": "/Users/tuminghong/.openclaw/extensions/feishu-openclaw-plugin/src/core/agent-config.d.ts",
        "parentPath": "/extensions/feishu-openclaw-plugin/src/core",
        "name": "agent-config.d.ts",
        "size": 3830,
        "extension": ".ts",
        "modified": "2026-03-11T08:57:46.861Z",
        "mode": 33188,
        "isDir": false,
        "isSymlink": false,
        "type": "text",
        "show_name": "<em>agent</em>-config.d.ts",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/extensions/feishu-openclaw-plugin/src/core/agent-config.d.ts.map",
        "realPath": "/Users/tuminghong/.openclaw/extensions/feishu-openclaw-plugin/src/core/agent-config.d.ts.map",
        "parentPath": "/extensions/feishu-openclaw-plugin/src/core",
        "name": "agent-config.d.ts.map",
        "size": 1449,
        "extension": ".map",
        "modified": "2026-03-11T08:57:46.834Z",
        "mode": 33188,
        "isDir": false,
        "isSymlink": false,
        "type": "binary",
        "show_name": "<em>agent</em>-config.d.ts.map",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/extensions/feishu-openclaw-plugin/src/core/agent-config.js",
        "realPath": "/Users/tuminghong/.openclaw/extensions/feishu-openclaw-plugin/src/core/agent-config.js",
        "parentPath": "/extensions/feishu-openclaw-plugin/src/core",
        "name": "agent-config.js",
        "size": 4693,
        "extension": ".js",
        "modified": "2026-03-11T08:57:46.783Z",
        "mode": 33188,
        "isDir": false,
        "isSymlink": false,
        "type": "text",
        "show_name": "<em>agent</em>-config.js",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/extensions/feishu-openclaw-plugin/src/core/agent-config.js.map",
        "realPath": "/Users/tuminghong/.openclaw/extensions/feishu-openclaw-plugin/src/core/agent-config.js.map",
        "parentPath": "/extensions/feishu-openclaw-plugin/src/core",
        "name": "agent-config.js.map",
        "size": 2427,
        "extension": ".map",
        "modified": "2026-03-11T08:57:46.805Z",
        "mode": 33188,
        "isDir": false,
        "isSymlink": false,
        "type": "binary",
        "show_name": "<em>agent</em>-config.js.map",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/extensions/feishu-openclaw-plugin/node_modules/undici-types/agent.d.ts",
        "realPath": "/Users/tuminghong/.openclaw/extensions/feishu-openclaw-plugin/node_modules/undici-types/agent.d.ts",
        "parentPath": "/extensions/feishu-openclaw-plugin/node_modules/undici-types",
        "name": "agent.d.ts",
        "size": 1167,
        "extension": ".ts",
        "modified": "2026-03-11T08:57:51.536Z",
        "mode": 33188,
        "isDir": false,
        "isSymlink": false,
        "type": "text",
        "show_name": "<em>agent</em>.d.ts",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/workspace/nanobot/core_agent_lines.sh",
        "realPath": "/Users/tuminghong/.openclaw/workspace/nanobot/core_agent_lines.sh",
        "parentPath": "/workspace/nanobot",
        "name": "core_agent_lines.sh",
        "size": 770,
        "extension": ".sh",
        "modified": "2026-03-17T17:31:17.260Z",
        "mode": 33216,
        "isDir": false,
        "isSymlink": false,
        "type": "text",
        "show_name": "core_<em>agent</em>_lines.sh",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/extensions/feishu-openclaw-plugin/node_modules/undici-types/env-http-proxy-agent.d.ts",
        "realPath": "/Users/tuminghong/.openclaw/extensions/feishu-openclaw-plugin/node_modules/undici-types/env-http-proxy-agent.d.ts",
        "parentPath": "/extensions/feishu-openclaw-plugin/node_modules/undici-types",
        "name": "env-http-proxy-agent.d.ts",
        "size": 732,
        "extension": ".ts",
        "modified": "2026-03-11T08:57:51.551Z",
        "mode": 33188,
        "isDir": false,
        "isSymlink": false,
        "type": "text",
        "show_name": "env-http-proxy-<em>agent</em>.d.ts",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/extensions/feishu-openclaw-plugin/node_modules/undici-types/mock-agent.d.ts",
        "realPath": "/Users/tuminghong/.openclaw/extensions/feishu-openclaw-plugin/node_modules/undici-types/mock-agent.d.ts",
        "parentPath": "/extensions/feishu-openclaw-plugin/node_modules/undici-types",
        "name": "mock-agent.d.ts",
        "size": 3448,
        "extension": ".ts",
        "modified": "2026-03-11T08:57:51.559Z",
        "mode": 33188,
        "isDir": false,
        "isSymlink": false,
        "type": "text",
        "show_name": "mock-<em>agent</em>.d.ts",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/extensions/feishu-openclaw-plugin/node_modules/undici-types/proxy-agent.d.ts",
        "realPath": "/Users/tuminghong/.openclaw/extensions/feishu-openclaw-plugin/node_modules/undici-types/proxy-agent.d.ts",
        "parentPath": "/extensions/feishu-openclaw-plugin/node_modules/undici-types",
        "name": "proxy-agent.d.ts",
        "size": 806,
        "extension": ".ts",
        "modified": "2026-03-11T08:57:51.561Z",
        "mode": 33188,
        "isDir": false,
        "isSymlink": false,
        "type": "text",
        "show_name": "proxy-<em>agent</em>.d.ts",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/extensions/feishu-openclaw-plugin/node_modules/undici-types/retry-agent.d.ts",
        "realPath": "/Users/tuminghong/.openclaw/extensions/feishu-openclaw-plugin/node_modules/undici-types/retry-agent.d.ts",
        "parentPath": "/extensions/feishu-openclaw-plugin/node_modules/undici-types",
        "name": "retry-agent.d.ts",
        "size": 233,
        "extension": ".ts",
        "modified": "2026-03-11T08:57:51.562Z",
        "mode": 33188,
        "isDir": false,
        "isSymlink": false,
        "type": "text",
        "show_name": "retry-<em>agent</em>.d.ts",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/extensions/feishu-openclaw-plugin/node_modules/undici-types/snapshot-agent.d.ts",
        "realPath": "/Users/tuminghong/.openclaw/extensions/feishu-openclaw-plugin/node_modules/undici-types/snapshot-agent.d.ts",
        "parentPath": "/extensions/feishu-openclaw-plugin/node_modules/undici-types",
        "name": "snapshot-agent.d.ts",
        "size": 3048,
        "extension": ".ts",
        "modified": "2026-03-11T08:57:51.563Z",
        "mode": 33188,
        "isDir": false,
        "isSymlink": false,
        "type": "text",
        "show_name": "snapshot-<em>agent</em>.d.ts",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/workspace/nanobot/nanobot/agent/__pycache__/subagent.cpython-312.pyc",
        "realPath": "/Users/tuminghong/.openclaw/workspace/nanobot/nanobot/agent/__pycache__/subagent.cpython-312.pyc",
        "parentPath": "/workspace/nanobot/nanobot/agent/__pycache__",
        "name": "subagent.cpython-312.pyc",
        "size": 12040,
        "extension": ".pyc",
        "modified": "2026-03-21T13:33:42.572Z",
        "mode": 33152,
        "isDir": false,
        "isSymlink": false,
        "type": "binary",
        "show_name": "sub<em>agent</em>.cpython-312.pyc",
        "id": 0,
        "session_id": "",
        "session_key": "",
      },
      {
        "path": "/workspace/nanobot/nanobot/agent/subagent.py",
        "realPath": "/Users/tuminghong/.openclaw/workspace/nanobot/nanobot/agent/subagent.py",
        "parentPath": "/workspace/nanobot/nanobot/agent",
        "name": "subagent.py",
        "size": 9459,
        "extension": ".py",
        "modified": "2026-03-17T17:31:17.261Z",
        "mode": 33152,
        "isDir": false,
        "isSymlink": false,
        "type": "text",
        "show_name": "sub<em>agent</em>.py",
        "id": 0,
        "session_id": "",
        "session_key": "",
      }
    ],
    "numDirs": 5,
    "numFiles": 13,
    "sorting": {
      "by": "name",
      "asc": true,
      "dirsFirst": true
    },
    "path": "/",
    "parentPath": "/",
    "realPath": "/Users/tuminghong/.openclaw",
    "name": "",
    "size": 1344,
    "extension": "",
    "modified": "2026-04-17T09:01:50.931Z",
    "mode": 16832,
    "isDir": true,
    "isSymlink": false,
    "type": "",
    "diskFreeSpace": 14777122816
  }
}
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "..."
  }
}
```

### filesystem.download

文件下载

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
   "path": "/update-check.json",  // 文件地址
   "url_type": "short" // 短链, common：默认
}
```

#### On success

```json
{
        "ok": true,
        "result": {
                "path": "/update-check.json",
                "name": "update-check.json",
                "size": 118,
                "extension": ".json",
                "modified": "2026-04-14T03:06:32.853Z",
                "mode": 33152,
                "isDir": false,
                "isSymlink": false,
                "type": "text",
                "url": "https://ns.chat.360.cn/zhaomi-so/client-up/66df35c3b1440e2f43834de157c81f3abde5d1c8.json",
                "key": "",
                "action": "download"
        }
}
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "path is not a regular file"
  }
}
```

### filesystem.share

文件分享

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
   "path": "/update-check.json",  // 文件地址
}
```

#### On success

```json
{
  "ok": true,
  "result": {
    "path": "/update-check.json",
    "name": "update-check.json",
    "size": 118,
    "extension": ".json",
    "modified": "2026-04-14T03:06:32.853Z",
    "mode": 33152,
    "isDir": false,
    "isSymlink": false,
    "type": "text",
    "url": "https://ns.chat.360.cn/zhaomi-so/client-up/6febca0e50d92be73fd5b2882f6895a4eccd91ec.json",
    "key": "",
    "action": "share"
  }
}
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "path is not a regular file"
  }
}
```

### filesystem.upload-yunpan

文件导出到我的上传

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
    "path": "update-check.json",  // 工作空间文件
    "to_path": "/openclaw/update-check.json" // 上传到云盘地址
}
```

#### On success

```json
{
  "ok": true,
  "result": {
    
  }
}
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "user info is missing; call system.mcporter.headers.set first"
  }
}
```

### filesystem.send-im

向 IM 发送附件

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
  "platform": "openclaw-weixin",  // 平台： openclaw-weixin：微信机器人；feishu： 飞书
  "filePath": "/test.txt", // 文件地址
  "src": "workspace" // 来源： 默认 workspace: 工作空间，other: 其他，！！！ 这个值不要乱传，先传workspace
  
}
```

#### On success

```json
{
  "ok": true,
  "result": {
    "status": "sent",
    "platform": "feishu",
    "channel": "feishu",
    "accountId": "main",
    "target": "user:ou_e403abaf5c3bd09aaddbc075309f566a",
    "messageId": "om_x100b5195635c64a8b26ed89aa29144d",
    "filePath": "/Users/tuminghong/.openclaw/mcp_doubao.txt"
  }
}
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "SEND_FAILED",
    "message": "sendFileMessageWeixin: contextToken is required",
    "detail": {
      "platform": "openclaw-weixin",
      "channel": "openclaw-weixin",
      "accountId": "5d526941f80e-im-bot",
      "target": "o9cq80051yK6o_w_pItmVRzbLClk@im.wechat"
    }
  }
}
```

### filesystem.get_ai_output_list

获取 AI 文件列表

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
"session_id":"abc123", // session_id
"keyword":"report", // 关键字
"file_type": "", // 默认为空，文件类型 generate 生成； upload 上传
"limit":20, // 返回限制
"offset":0, // 偏移
  "extras": {
    "layout": "tree", // 当传入 session_id且这个值为 tree时，返回树形结构
    "parent_path": "/agents/team_ceo/ceo_team_pm/team_agent/20260514214000-ai-doc-vs-meeting/ceo_team_taleibu/output"
    // 支持根据目录获取目录下目录和文件
  }
}
```

#### On success

```json
{
  "ok": true,
  "result": {
    "total_count": 52,
    "items": [
      {
        "id": 3,
        "session_key": "main",
        "thumb_url": "", // 缩略图
        "size": "",// 文件大小
        "session_id": "session-abc123",
        "local_path": "/outputs/2026/04/report.pdf",
        "parent_path": "/outputs/2026/04",
        "file_name": "report.pdf",
        "ext": "pdf",
        "file_type": "generate",   // 文件类型 generate 生成； upload 上传
        "url": "https://s3.example.com/bucket/report.pdf",
        "create_time": 1745400000000,
        "update_time": 1745410000000,
        "status": 1,
         "type": "file" // 树形结构时有此字段，file 文件 dir 目录
      },
      {
        "id": 2,
        "session_key": "main",
        "thumb_url": "", // 缩略图
        "size": "",// 文件大小
        "session_id": "session-abc123",
        "local_path": "/outputs/2026/04/data.csv",
        "parent_path": "/outputs/2026/04",
        "file_name": "data.csv",
        "ext": "csv",
        "url": "",
        "file_type": "upload",
        "create_time": 1745390000000,
        "update_time": 1745390000000,
        "status": 1,
         "type": "file"
      }
    ]
  }
}
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "invalid filesystem.get_output_list params: at /limit: must be >= 1"
  }
}
```

### filesystem.get_ai_output_details

获取 AI 文件列表

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{"ids":[1,2,4]}
```

#### On success

```json
{
  "ok": true,
  "result": {
    "items": [
      {
        "id": 1,
        "session_key": "agent:ceo_team_pm:main",
        "session_id": "7fd1d695-7bf5-45c0-9481-75f94810fe12",
        "local_path": "/agents/team_ceo/ceo_team_pm/team_agent/20260514214000-ai-doc-vs-meeting/ceo_team_masike/output/马斯克第一性原理__AI文档vs会议纪要决策拆解.md",
        "parent_path": "/agents/team_ceo/ceo_team_pm/team_agent/20260514214000-ai-doc-vs-meeting/ceo_team_masike/output",
        "file_name": "马斯克第一性原理__AI文档vs会议纪要决策拆解.md",
        "ext": "md",
        "url": "https://ns.chat.360.cn/zhaomi-so/client-up/c6c6a08c5de4f73785c54efff5afb805df36524a.md",
        "thumb_url": "",
        "size": 19429,
        "file_id": "",
        "file_type": "generate",
        "create_time": 1778766193250,
        "update_time": 1778766193250,
        "status": 1,
        "scope": "final"
      },
      {
        "id": 2,
        "session_key": "agent:ceo_team_pm:main",
        "session_id": "7fd1d695-7bf5-45c0-9481-75f94810fe12",
        "local_path": "/agents/team_ceo/ceo_team_pm/team_agent/20260514214000-ai-doc-vs-meeting/ceo_team_qiaobusi/output/乔布斯产品战略官__AI文档vs会议纪要产品判断.md",
        "parent_path": "/agents/team_ceo/ceo_team_pm/team_agent/20260514214000-ai-doc-vs-meeting/ceo_team_qiaobusi/output",
        "file_name": "乔布斯产品战略官__AI文档vs会议纪要产品判断.md",
        "ext": "md",
        "url": "https://ns.chat.360.cn/zhaomi-so/client-up/86e43667ebfbc26c5b07438dd53ff3cd11ecc249.md",
        "thumb_url": "",
        "size": 14746,
        "file_id": "",
        "file_type": "generate",
        "create_time": 1778766355129,
        "update_time": 1778766355129,
        "status": 1,
        "scope": "final"
      },
      {
        "id": 4,
        "session_key": "agent:ceo_team_pm:main",
        "session_id": "7fd1d695-7bf5-45c0-9481-75f94810fe12",
        "local_path": "/agents/team_ceo/ceo_team_pm/team_agent/20260514214000-ai-doc-vs-meeting/ceo_team_taleibu/output/塔勒布风险分析师__AI文档vs会议纪要风险判断.md",
        "parent_path": "/agents/team_ceo/ceo_team_pm/team_agent/20260514214000-ai-doc-vs-meeting/ceo_team_taleibu/output",
        "file_name": "塔勒布风险分析师__AI文档vs会议纪要风险判断.md",
        "ext": "md",
        "url": "https://ns.chat.360.cn/zhaomi-so/client-up/f02389ae67c0c7b7868b11c4fc5c9363652dceae.md",
        "thumb_url": "",
        "size": 20509,
        "file_id": "",
        "file_type": "generate",
        "create_time": 1778766404204,
        "update_time": 1778766404204,
        "status": 1,
        "scope": "final"
      }
    ]
  }
}
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "invalid filesystem.get_output_list params: at /limit: must be >= 1"
  }
}
```

### filesystem.insert_ai_output

添加用户产出 ｜ 上传

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
    "items": [
      {
        "session_key": "main",    // session_key
        "session_id": "session-abc123",    //session_id
        "file_name": "智能驾驶.png",        // 文件名称
        "file_path": "文件路径", //在执行入库的时候插入到 local_path中
        "url": "https://cdn.example.com/outputs/智能驾驶.png",  // s3 url
        "thumb_url": "https://cdn.example.com/thumb/智能驾驶.png",  // 缩略图url
        "size": 1350366, //  大小
        "file_id": "yunpan-file-001"  // file_id(上传云盘后会有)，
        "scope":"process"
      }
    ]
  }
}
```

#### On success

```json
{ "ok": true, "result": { "ids": [42], "count": 1 } }
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "invalid filesystem.get_output_list params: at /limit: must be >= 1"
  }
}
```

### filesystem.update_ai_output

更新 AI 文件(用户上传，带 file_id)

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{"id":5,"file_name":"20260514214000-ai-doc-vs-meeting.md"}'
```

#### On success

```json
{
  "ok": true,
  "result": {
    "updated": false
  }
}
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "具体错误说明字符串"
  }
}
```

### filesystem.rename

重命名

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
  "local_path": "/outputs/report.pdf",  // 原文件路径
  "rename": "report-final.pdf", // 新文件名
  "id": 123 // AI文件的id（当操作AI文件时需要传，工作空间文件不需要传）
}
```

#### On success

```json
{ "ok": true, "result": {} }
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "invalid filesystem.get_output_list params: at /limit: must be >= 1"
  }
}
```

### filesystem.edit

文件编辑

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
  "file_url": "https://example.com/assets/report-v2.pdf",  //新文件 URL
  "file_path": "/outputs/report-final.pdf", // 目标文件路径
  "rename": "report-final.pdf", // 可选的新文件名（仅文件名，不含路径）
  "id": 123 // AI文件的id（当操作AI文件时需要传，工作空间文件不需要传）
}
```

#### On success

```json
{ "ok": true, "result": {} }
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "invalid filesystem.get_output_list params: at /limit: must be >= 1"
  }
}
```

## 知识库

### gbrain.ingest_batch

摄取接口

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
  "agent_id": "sales-bot",
  "requests": [
    {
      "source": { "type": "file", "path": "/absolute/path/to/doc.pdf" , filename: "产品方案v2.pdf"},
      "profile": "full",
      "force_reindex": false,
      "agent_id": "sales-bot"
    },
    {
      "source": {
        "type": "url",
        "url": "https://example.com/report.pdf",
        "filename": "report.pdf",
        "path": "/vfs/reports/report.pdf"
      },
      "profile": "middle"
    }
  ],
  "opts": {
    "profile": "full",
    "prefer_fast_first": true,
    "warm_workers": true,
    "force_reindex": false,
    "agent_id": "sales-bot",
    "session_id": "sess-abc",
    "qid": "q-006"
  },
  "session_id": "sess-abc",
  "qid": "q-006"
}
```

#### 参数说明

<table>
<tr>
<td>字段<br/></td><td>必填<br/></td><td>说明<br/></td></tr>
<tr>
<td>`requests`<br/></td><td>是<br/></td><td>非空数组<br/></td></tr>
<tr>
<td>`requests[].source`<br/></td><td>是<br/></td><td>`type: "file"` 需 `path`；`type: "url"` 需 `url`，可选 `filename`<br/></td></tr>
<tr>
<td>`requests[].profile`<br/></td><td>否<br/></td><td>`"full"` | `"middle"` | `"fast"`<br/></td></tr>
<tr>
<td>`requests[].force_reindex`<br/></td><td>否<br/></td><td>强制 GBrain 重新 chunk<br/></td></tr>
<tr>
<td>`opts.profile`<br/></td><td>否<br/></td><td>批次默认 profile，单条 `profile` 优先<br/></td></tr>
<tr>
<td>`opts.prefer_fast_first`<br/></td><td>否<br/></td><td>小文件优先<br/></td></tr>
<tr>
<td>`opts.warm_workers`<br/></td><td>否<br/></td><td>预热 worker<br/></td></tr>
<tr>
<td>`opts.force_reindex`<br/></td><td>否<br/></td><td>批次级强制 reindex<br/></td></tr>
<tr>
<td>`opts.session_id` / `opts.qid`<br/></td><td>否<br/></td><td>日志透传；可覆盖顶层 `session_id`/`qid`<br/></td></tr>
<tr>
<td>`agent_id` / `opts.agent_id`<br/></td><td>否<br/></td><td>批次级 Agent 隔离；`requests[].agent_id` 可覆盖单条<br/></td></tr>
<tr>
<td>`requests[].agent_id`<br/></td><td>否<br/></td><td>单条覆盖批次 `agent_id`<br/></td></tr>
</table>

#### On success

```json
{
  "ok": true,
  "result": {
    "job_id": "420b48de-cee2-4919-b52b-d03473baa1f0",
    "request_count": 5,
    "elapsed_ms": 979,
    "business_status": "submitted"
  }
}
```

<table>
<tr>
<td>`result` 字段<br/></td><td>类型<br/></td><td>说明<br/></td></tr>
<tr>
<td>`job_id`<br/></td><td>`string`<br/></td><td>UUID，供 `ingest_job_status` 轮询<br/></td></tr>
<tr>
<td>`request_count`<br/></td><td>`number`<br/></td><td>本批 `requests.length`<br/></td></tr>
<tr>
<td>`elapsed_ms`<br/></td><td>`number`<br/></td><td>提交入队耗时（ms），非整批摄取耗时<br/></td></tr>
<tr>
<td>business_status<br/></td><td>submitted<br/></td><td>固定值：任务已入队，****非****终态；终态ingest_job_status.result.business_status<br/></td></tr>
<tr>
<td>`agent_id`<br/></td><td>`string?`<br/></td><td>仅当批次指定了有效 `agent_id` 时回显<br/></td></tr>
</table>

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "gbrain.ingest_batch: requests must be a non-empty array"
  }
}
```

### gbrain.ingest_job_status

查询摄取任务状态；可选阻塞等待 embedding 终态。

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "wait_for_embedding": true,
  "embedding_timeout_ms": 120000,
  "session_id": "sess-abc",
  "qid": "q-007"
}
```

<table>
<tr>
<td>字段<br/></td><td>必填<br/></td><td>默认<br/></td><td>说明<br/></td></tr>
<tr>
<td>`job_id`<br/></td><td>是<br/></td><td>—<br/></td><td>`ingest_batch` 返回的 ID<br/></td></tr>
<tr>
<td>`wait_for_embedding`<br/></td><td>否<br/></td><td>`false`<br/></td><td>`true` 时服务端阻塞至 embedding 终态或超时<br/></td></tr>
<tr>
<td>`embedding_timeout_ms`<br/></td><td>否<br/></td><td>`120000`<br/></td><td>最大 `300000`<br/></td></tr>
</table>

#### On success

```json
{
  "ok": true,
  "result": {
    "job_id": "420b48de-cee2-4919-b52b-d03473baa1f0",
    "status": "partial",
    "process": 20, 
    "business_status": "partial_success",
    "contract_status": "partial",
    "quality_contract_status": "partial",
    "pipeline_status": "ready",
    "created_at": 1749018300000,
    "started_at": 1749018300010,
    "finished_at": 1749018410000,
    "embedding_status": "completed",
    "result": {
      "items": [
        {
          "input": "/Users/me/Downloads/美国抢时间搞AI安全联盟，这对中国影响很大！(3).docx",
          "writtenPages": ["wiki/...", "verbatim/..."],
          "gbrainSynced": 27,
          "process": 20,
          "gbrainSkipped": 0,
          "gbrainPagesTotal": 27,
          "gbrainWikiPagesSynced": 6,
          "gbrainVerbatimChunksSynced": 21,
          "postIngestJobIds": [101, 102],
          "gbrainErrors": [],
          "elapsedMs": 68000,
          "activeProfile": "full",
          "contractStatus": "partial",
          "contractReasons": [
            "section probe failed: query=\"核心内容\" hits=3"
          ],
          "embeddingStatus": "completed",
          "pipelineStatus": "ready"
        }
      ],
      "totalElapsedMs": 109000,
      "successCount": 5,
      "errorCount": 0
    },
    "elapsed_ms": 12
  }
}
```

**字段命名：** Job 顶层为 **snake_case**（`job_id`、`embedding_status`、`contract_status`）；内层 `result.items[]` 为 **camelCase**（`writtenPages`、`gbrainSynced`、`contractReasons`、`elapsedMs`），与 `src/kb-gbrain/types.ts` 一致。

**层级：** 外层业务信封的 `result` 与内层批次明细 `result.result`（`KbGbrainIngestResult`）同名，注意区分。

<table>
<tr>
<td>`result` 顶层字段<br/></td><td>说明<br/></td></tr>
</table>

| `business_status` | ****推荐****：终态业务标识，见下表（与 `status` 一一对应） |

| `status` | Job 执行状态（实现内部枚举），见下表 |

| `contract_status` | 摄取契约聚合（与 `quality_contract_status` 同源） |

| `quality_contract_status` | 质量维度：`ok` / `partial` / `failed` |

| `pipeline_status` | wiki + sync + embedding 流水线：`ready` / `sync_incomplete` / `embedding_pending` / `failed` |

| `embedding_status` | 全批 post_ingest 向量任务聚合 |

| `result` | 批次明细：`items`、`totalElapsedMs`、`successCount`、`errorCount` |

| `error` | Job 级错误字符串（`status=failed` 时可能出现） |

| `agent_id` | 批次 Agent 隔离时回显 |

| `elapsed_ms` | ****本次 status 查询****耗时，非摄取总耗时 |

****`result.business_status`（终态业务标识，实现：`resolveIngestJobBusinessStatus`）：****

<table>
<tr>
<td>值<br/></td><td>对应 `status`<br/></td><td>含义<br/></td></tr>
<tr>
<td>`in_progress`<br/></td><td>`pending` / `running`<br/></td><td>进行中，未达终态<br/></td></tr>
</table>

| `success` | `done` | ****全部成功****（批次契约 `ok`，无 `failed` 项） |

| `partial_success` | `partial` | ****部分成功****（批次完成但质量契约 `partial`，如 section probe 未过） |

| `failed` | `failed` | ****失败****（整批或契约聚合 `failed`） |

客户端判断「全部成功 vs 部分成功」应优先读 ****`business_status`****：`success` / `partial_success` / `failed`；`pipeline_status=ready` 只表示流水线可检索，不等同于质量契约满分。

****`result.status`（Job 执行，与 `business_status` 对齐）：****

<table>
<tr>
<td>值<br/></td><td>`business_status`<br/></td><td>说明<br/></td></tr>
<tr>
<td>`pending`<br/></td><td>`in_progress`<br/></td><td>已提交，等待执行<br/></td></tr>
<tr>
<td>`running`<br/></td><td>`in_progress`<br/></td><td>正在摄取（E2E 轮询前 ~1m 多为该状态）<br/></td></tr>
<tr>
<td>`done`<br/></td><td>`success`<br/></td><td>批次结束且契约聚合为 `ok`<br/></td></tr>
<tr>
<td>`partial`<br/></td><td>`partial_success`<br/></td><td>批次结束但质量契约为 `partial`（E2E 5 文档批次的常见终态）<br/></td></tr>
<tr>
<td>`failed`<br/></td><td>`failed`<br/></td><td>整批失败；见 `result.error` 或 `items[].error`<br/></td></tr>
</table>

****`embedding_status`（向量，与 `status` 正交）：****

<table>
<tr>
<td>值<br/></td><td>说明<br/></td></tr>
<tr>
<td>`pending` / `running`<br/></td><td>post_ingest 未完成；`wait_for_embedding=true` 时服务端阻塞至终态<br/></td></tr>
<tr>
<td>`completed`<br/></td><td>全批 minion embedding 完成（E2E：296/296 chunks）<br/></td></tr>
<tr>
<td>`failed`<br/></td><td>至少一条 post_ingest 失败<br/></td></tr>
<tr>
<td>`unknown`<br/></td><td>无 post_ingest job 或状态查询失败；`running` 阶段 CLI 可能显示为 `?`<br/></td></tr>
</table>

****`pipeline_status` vs `quality_contract_status`：****

<table>
<tr>
<td>`pipeline_status`<br/></td><td>含义<br/></td></tr>
<tr>
<td>`ready`<br/></td><td>可对外提供检索（wiki 已写、page 已 sync、embedding 未 failed）<br/></td></tr>
<tr>
<td>`embedding_pending`<br/></td><td>摄取/sync 完成，向量仍进行中<br/></td></tr>
<tr>
<td>`sync_incomplete`<br/></td><td>写出页数与 sync 数不一致<br/></td></tr>
<tr>
<td>`failed`<br/></td><td>流水线失败<br/></td></tr>
</table>

`quality_contract_status=partial` 时仍可能出现 `pipeline_status=ready`（E2E：2 篇 section probe 未过，但 embedding 100% 且召回测试继续）。

****`result.items[]` 常用字段：****

<table>
<tr>
<td>字段<br/></td><td>说明<br/></td></tr>
<tr>
<td>`input`<br/></td><td>原始文件路径或 URL<br/></td></tr>
<tr>
<td>`writtenPages`<br/></td><td>KB 写出的 wiki 路径列表<br/></td></tr>
<tr>
<td>`gbrainSynced` / `gbrainSkipped`<br/></td><td>本次 put_page 更新 / 幂等 skip 页数<br/></td></tr>
<tr>
<td>`gbrainPagesTotal`<br/></td><td>本文件处理页总数（updated + skipped）<br/></td></tr>
<tr>
<td>`gbrainWikiPagesSynced` / `gbrainVerbatimChunksSynced`<br/></td><td>wiki 结构化页 vs verbatim 段计数<br/></td></tr>
<tr>
<td>`postIngestJobIds`<br/></td><td>GBrain post_ingest minion job ID 列表<br/></td></tr>
<tr>
<td>`contractStatus` / `contractReasons`<br/></td><td>单文件契约；`partial` 时 `contractReasons` 含 probe 等原因<br/></td></tr>
<tr>
<td>`pipelineStatus`<br/></td><td>单文件流水线状态<br/></td></tr>
<tr>
<td>`embeddingStatus`<br/></td><td>单文件向量聚合<br/></td></tr>
<tr>
<td>`activeProfile`<br/></td><td>实际使用的 `full` / `middle` / `fast`<br/></td></tr>
<tr>
<td>`error`<br/></td><td>单文件失败信息<br/></td></tr>
</table>

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "gbrain.ingest_job_status: job not found: 550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### gbrain.delete

知识库删除

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
  "file_path": "/vfs/reports/q1.pdf",
  "agent_id": "my-agent",
  "session_id": "sess-001",
  "qid": "q-del-01"
}
```

<table>
<tr>
<td>字段<br/></td><td>必填<br/></td><td>说明<br/></td></tr>
<tr>
<td>`file_path`<br/></td><td>是<br/></td><td>与摄取时一致的逻辑路径（`ingest_batch` 的 `source.path` 或 url 的 `path`）<br/></td></tr>
<tr>
<td>`agent_id`<br/></td><td>否<br/></td><td>与摄取/检索相同则限定 `source_id=agent:<id>`<br/></td></tr>
<tr>
<td>`session_id` / `qid`<br/></td><td>否<br/></td><td>追踪字段<br/></td></tr>
</table>

#### On success

```json
{
  "ok": true,
  "result": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "operation": "delete",
    "file_path": "/vfs/reports/q1.pdf",
    "business_status": "submitted",
    "elapsed_ms": 12,
    "agent_id": "my-agent"
  }
}
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "invalid filesystem.get_output_list params: at /limit: must be >= 1"
  }
}
```

### gbrain.rename

知识库改名

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
  "old_path": "/vfs/reports/q1.pdf",
  "new_path": "/vfs/reports/q1-renamed.pdf",
  "agent_id": "my-agent",
  "session_id": "sess-001", // 非必填
  "qid": "q-del-01"// 非必填
}
```

<table>
<tr>
<td>字段<br/></td><td>必填<br/></td><td>说明<br/></td></tr>
<tr>
<td>`old_path`<br/></td><td>是<br/></td><td>原逻辑路径<br/></td></tr>
<tr>
<td>`new_path`<br/></td><td>是<br/></td><td>新逻辑路径（须与 `old_path` 不同）<br/></td></tr>
<tr>
<td>`agent_id`<br/></td><td>否<br/></td><td>同 §6.3<br/></td></tr>
<tr>
<td>`session_id` / `qid`<br/></td><td>否<br/></td><td>追踪字段<br/></td></tr>
</table>

#### On success

```json
{
  "ok": true,
  "result": {
    "job_id": "660e8400-e29b-41d4-a716-446655440001",
    "operation": "rename",
    "old_path": "/vfs/reports/q1.pdf",
    "new_path": "/vfs/reports/q1-renamed.pdf",
    "business_status": "submitted",
    "elapsed_ms": 8
  }
}
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "invalid filesystem.get_output_list params: at /limit: must be >= 1"
  }
}
```

## FileCard

```json
{
    nm_card    是否以卡片形式展示，true 展示，false 不展示
    nm_name    文件名
    nm_size    文件大小
    nm_type    文件类型（如 image、video、audio、html、ppt）
}

例如
[](https://cdn.example.com/photo.jpg?_nm_name=%E7%94%A8%E6%88%B7%E5%A4%B4%E5%83%8F.jpg&nm_size=102400&nm_type=image_)
```

## 纳米 Work

### filesystem.ws.finals

文件产物列表

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
    "limit": 20,             # 每页条数
    "offset": 0,             # 偏移（跳过前 N 条）
    "keyword": "",           # 关键字
    "clawExtensions": {},    # 可选
}
```

#### On success

```json
字段说明
"agentTitle":"",        # 专家标题
"agentIcon":"",         # 专家头像
"agentStatus": 0        # 专家状态 0:正常，1:删除

返回的结果
{
  "ok": true,
  "result": {
    "items": [
      {
        "id": 419,
        "session_key": "agent:main:main",
        "session_id": "89320587-ea98-45a7-9cdf-5aea18edb7db",
        "local_path": "/story.md",
        "parent_path": "/",
        "file_name": "story.md",
        "ext": "md",
        "url": "https://ns.chat.360.cn/zhaomi-so/client-up/0d677e2de531741627037d224defc225fe3cd030.md",
        "thumb_url": "",
        "size": 643,
        "file_id": "",
        "file_type": "generate",
        "create_time": 1781492113646,
        "update_time": 1781492124736,
        "status": 1,
        "scope": "final",
        "run_id": "faceb955-4170-4493-9bb8-10284680df76",
        "agent_title": "虾鸡米",
        "agent_icon": "https://qcdn1.zhaomi.cn/t11de458816cc1e001c59f00565.png",
        "agent_status": 0
      }
    ],
    "total_count": 372
  }
}
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "..."
  }
}
```

### filesystem.ws.agents

专家列表

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
    "limit": 20,            # 每页条数
    "offset": 0,            # 偏移
    "clawExtensions": {},   # 扩展
}
```

#### On success

```json
{
  "ok": true,
  "result": {
    "items": [
      {
        "session_key": "agent:main:main",
        "agent_status": 0,
        "agent_title": "虾鸡米",
        "agent_icon": "https://qcdn1.zhaomi.cn/t11de458816cc1e001c59f00565.png",
        "file_count": 134,
        "update_time": 1780900815552
      },
      {
        "session_key": "agent:a0d97c8c-860e-4f84-a115-d5a30c038f3a:main",
        "agent_status": 0,
        "agent_title": "文静（公众号助手）",
        "agent_icon": "https://qncdn.n.cn/so/ai_image/F60XwDTS6wf_g4RD60Fq7wR_clean.jpg",
        "file_count": 1,
        "update_time": 1780578098965
      },
      {
        "session_key": "agent:nami_qingbaodiaoyanpartner:main",
        "agent_status": 0,
        "agent_title": "情报调研partner",
        "agent_icon": "https://p2.ssl.qhimg.com/t110b9a93016735366eb80548c3.png",
        "file_count": 4,
        "update_time": 1780398101046
      },
    ],
    "total_count": 1
  }
}
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "..."
  }
}
```

### filesystem.ws.sessions

历史对话列表

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
    "agent_id": "",
    "limit": 20,            # 【可选，默认20】每页条数
    "before_timestamp": 0,  # 【可选】游标，取上一个返回的 next_before_timestamp
    "query": "",            # 【可选】标题搜索
    "clawExtensions": {},   # 【可选】
}
```

#### On success

```json
{
  "ok": true,
  "result": {
    "items": [
      {
        "session_id": "80bb4bc6-38b5-4648-aef6-1a607d3ee9c8",
        "session_key": "agent:main:main",
        "title": "帮我生成一个xlsx，内容就是 6月份日历。放到987output目录下\nexec不要输出目录",
        "timestamp": 1780396024344,
        "file_count": 1,
        "update_time": 1780396030238
      }
    ],
    "has_more": false,    # 是否有下一页 True有，False没有
    "next_before_timestamp": 1712145600000    # 下一页游标；has_more=false 时通常没有
  }
}
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "..."
  }
}
```

### filesystem.ws.session_files

对话中的文件列表

#### Transport

#### Gateway RPC (WebSocket protocol)

#### Request params

```json
{
    "session_id": "",        # 必填
    "scope": "final",        #【可选】类型: final产物【默认】，process过程
    "limit": 20,             #【可选】每页条数默认20
    "offset": 0,             #【可选】偏移
    "clawExtensions": {},    #【可选】
}
```

#### 产物列表

###### Request params

```json
{
    "session_id": "",        # 必填
    "scope": "final",        # final产物
    "limit": 20,             # 每页条数默认20
    "offset": 0,             # 偏移
}
```

###### On success

```json
items                      # 常务列表
total_count                # 产物数量
process_count              # 过程文件数量
process_update_time        # 过程文件最新更新时间


{
  "ok": true,
  "result": {
    "items": [
      {
        "id": 419,
        "session_key": "agent:main:main",
        "session_id": "89320587-ea98-45a7-9cdf-5aea18edb7db",
        "local_path": "/story.md",
        "parent_path": "/",
        "file_name": "story.md",
        "ext": "md",
        "url": "https://ns.chat.360.cn/zhaomi-so/client-up/0d677e2de531741627037d224defc225fe3cd030.md",
        "thumb_url": "",
        "size": 643,
        "file_id": "",
        "file_type": "generate",
        "create_time": 1781492113646,
        "update_time": 1781492124736,
        "status": 1,
        "scope": "final",
        "run_id": "faceb955-4170-4493-9bb8-10284680df76",
        "agent_title": "虾鸡米",
        "agent_icon": "https://qcdn1.zhaomi.cn/t11de458816cc1e001c59f00565.png"
      }
    ],
    "total_count": 1,
    "process_count": 1,
    "process_update_time": 1781491861285
  }
}
```

#### 过程文件列表

###### Request params

```json
{
    "session_id": "",        # 必填
    "scope": "process",      # process过程
    "limit": 20,             # 每页条数默认20
    "offset": 0,             # 偏移
}
```

###### On success

```json
{
  "ok": true,
  "result": {
    "items": [
      {
        "id": 418,
        "session_key": "agent:main:main",
        "session_id": "89320587-ea98-45a7-9cdf-5aea18edb7db",
        "local_path": "/attachments/outputs/video.mp4",
        "parent_path": "/attachments/outputs",
        "file_name": "video.mp4",
        "ext": "mp4",
        "url": "https://cdn.example/new",
        "thumb_url": "",
        "size": 17,
        "file_id": "",
        "file_type": "generate",
        "create_time": 1781491861285,
        "update_time": 1781491861285,
        "status": 1,
        "scope": "process",
        "run_id": "faceb955-4170-4493-9bb8-10284680df76",
        "agent_title": "虾鸡米",
        "agent_icon": "https://qcdn1.zhaomi.cn/t11de458816cc1e001c59f00565.png"
      }
    ],
    "total_count": 1
  }
}
```

#### On failure

```json
{
  "ok": false,
  "error": {
    "type": "INVALID_REQUEST",
    "message": "..."
  }
}
```

# 其它

## 云龙虾配置自升级[云龙虾配置自升级](https://my.feishu.cn/wiki/P3pnwb4EaiZ6gikyEr5cyFNDnDf)

## 技能列表

[http://new-test-assistant.qihoo.net/#/layout/claw/clawAgentSkill](http://new-test-assistant.qihoo.net/#/layout/claw/clawAgentSkill)

## 登录云端主机

```json
[http://new-test-search.qihoo.net/#/layout/claw/userVm](http://new-test-search.qihoo.net/#/layout/claw/userVm)
[https://hulk.qihoo.net/user/host/list?zResGroup=4532#](https://hulk.qihoo.net/user/host/list?zResGroup=4532#)

镜像机：
<u>QA:p116548v.hulk.bjwdt.qihoo.net</u>
<u>Online:p113607v.hulk.bjwdt.qihoo.net</u>

gateway启动失败查看日志：
journalctl --user -u openclaw-gateway.service -n 200 --no-pager

执行完install.sh重启service
systemctl --user daemon-reload
systemctl --user restart openclaw-gateway.service
systemctl --user status openclaw-gateway.service

sudo ss -tlnp | grep ':19798'
lsof -ti :19798 -sTCP:LISTEN | xargs kill

镜像中git配置
git config --global http.proxy http://36.110.234.210:8000
git config --global https.proxy  http://36.110.234.210:8000

QA：p94248v.hulk.bjwdt.qihoo.net
929194897

nami
gYSHmg#5mKC^4!5U

查看openclaw版本
openclaw --nversion

省钱版错误日志：
grep -n '\[ERROR\]' /tmp/openclaw/nm/nm-2026-04-03.log | head -30  

全局skill目录：
/home/nami/.npm-global/global/5/.pnpm/openclaw@file+..+..+..+.openclaw360-updater+artifacts+managed+artifact_job_202605210239_8ddbd8bae4a8866a9be3348ac91dc614/node_modules/openclaw/skills

~/.npm-global/global/5/.pnpm/openclaw@file+..+..+..+.openclaw360-updater+artifacts+managed+artifact_job_202605210239_8ddbd8bae4a8866a9be3348ac91dc614/node_modules/openclaw/skills/

跳板机：https://jumper.qihoo.net/core/auth/login/
11.120.82.71
11.120.82.233
```

# 

# 文档

[工程技术：在智能体优先的世界中利用 Codex](https://openai.com/zh-Hans-CN/index/harness-engineering/)

# Session 数据格式

## 原版

```json
[
  {
    "type": "session",
    "version": 3,
    "id": "e5c2c10e-8d65-4da6-85f3-e6ce6376975b",
    "timestamp": "2026-04-04T12:36:48.817Z",
    "cwd": "/Users/lizhenguo1/.openclaw/workspace"
  },
  {
    "type": "model_change",
    "id": "cbbce091",
    "parentId": null,
    "timestamp": "2026-04-04T12:36:48.823Z",
    "provider": "zhinao",
    "modelId": "minimax/MiniMax-M2.5"
  },
  {
    "type": "thinking_level_change",
    "id": "b3accbb1",
    "parentId": "cbbce091",
    "timestamp": "2026-04-04T12:36:48.823Z",
    "thinkingLevel": "off"
  },
  {
    "type": "custom",
    "customType": "model-snapshot",
    "data": {
      "timestamp": 1775306208828,
      "provider": "zhinao",
      "modelApi": "openai-completions",
      "modelId": "minimax/MiniMax-M2.5"
    },
    "id": "5067ac4c",
    "parentId": "b3accbb1",
    "timestamp": "2026-04-04T12:36:48.828Z"
  },
  {
    "type": "message",
    "id": "e785e95f",
    "parentId": "5067ac4c",
    "timestamp": "2026-04-04T12:36:49.069Z",
    "message": {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Sender (untrusted metadata):\n```json\n{\n  \"label\": \"openclaw-control-ui\",\n  \"id\": \"openclaw-control-ui\"\n}\n```\n\n[Sat 2026-04-04 20:36 GMT+8] 使用李白的任意一首诗生成音频"
        }
      ],
      "timestamp": 1775306209060
    }
  },
  {
    "type": "message",
    "id": "d5289e77",
    "parentId": "e785e95f",
    "timestamp": "2026-04-04T12:36:54.755Z",
    "message": {
      "role": "assistant",
      "content": [
        {
          "type": "thinking",
          "thinking": "用户想用李白的诗生成音频。我需要：\n1. 找一首李白的诗\n2. 用 TTS 工具生成音频\n\n李白最著名的诗包括：《静夜思》、《望庐山瀑布》、《行路难》、《将进酒》等。\n\n我可以用内置的 tts 工具来生成音频。让我选一首经典的，比如《静夜思》或《将进酒》。\n\n《静夜思》比较短，适合TTS。《将进酒》更长，更有气势。\n\n让我选《将进酒》吧，比较有代表性。\n",
          "thinkingSignature": "reasoning_content"
        },
        {
          "type": "text",
          "text": "\n\n\n"
        },
        {
          "type": "toolCall",
          "id": "call_3edd190c96e34731ac390f29",
          "name": "tts",
          "arguments": {
            "text": "将进酒\n\n君不见，黄河之水天上来，奔流到海不复回。\n君不见，高堂明镜悲白发，朝如青丝暮成雪。\n人生得意须尽欢，莫使金樽空对月。\n天生我材必有用，千金散尽还复来。\n烹羊宰牛且为乐，会须一饮三百杯。\n岑夫子，丹丘生，将进酒，杯莫停。\n与君歌一曲，请君为我倾耳听。\n钟鼓馔玉不足贵，但愿长醉不复醒。\n古来圣贤皆寂寞，惟有饮者留其名。\n陈王昔时宴平乐，斗酒十千恣欢谑。\n主人何为言少钱，径须沽取对君酌。\n五花马，千金裘，呼儿将出换美酒，与尔同销万古愁。"
          }
        }
      ],
      "api": "openai-completions",
      "provider": "zhinao",
      "model": "minimax/MiniMax-M2.5",
      "usage": {
        "input": 27,
        "output": 318,
        "cacheRead": 30272,
        "cacheWrite": 0,
        "totalTokens": 30617,
        "cost": {
          "input": 0,
          "output": 0,
          "cacheRead": 0,
          "cacheWrite": 0,
          "total": 0
        }
      },
      "stopReason": "stop",
      "timestamp": 1775306209067
    }
  },
  {
    "type": "message",
    "id": "6e3cc7c5",
    "parentId": "d5289e77",
    "timestamp": "2026-04-04T12:36:57.128Z",
    "message": {
      "role": "toolResult",
      "toolCallId": "call_3edd190c96e34731ac390f29",
      "toolName": "tts",
      "content": [
        {
          "type": "text",
          "text": "[[audio_as_voice]]\nMEDIA:/tmp/openclaw/tts-S0IUt8/voice-1775306214771.mp3"
        },
        {
          "type": "text",
          "text": "\n### CDN uploads\n\n- **Audio:** [voice-1775306214771.mp3](https://ns.chat.360.cn/zhaomi-so/client-up/34251650bb3ff503abe941ee3c01c0b733595c38.mp3)\n"
        }
      ],
      "details": {
        "audioPath": "/tmp/openclaw/tts-S0IUt8/voice-1775306214771.mp3",
        "provider": "edge"
      },
      "isError": false,
      "timestamp": 1775306217110
    }
  },
  {
    "type": "message",
    "id": "cf1482dd",
    "parentId": "6e3cc7c5",
    "timestamp": "2026-04-04T12:37:01.040Z",
    "message": {
      "role": "assistant",
      "content": [
        {
          "type": "thinking",
          "thinking": "用户要求使用李白的任意一首诗生成音频。我刚刚已经调用了tts工具，将李白的《将进酒》转换为了语音。音频已经生成并上传到CDN。\n\n我需要回复用户，告诉他们音频已经生成好了。根据工具结果，音频已经成功生成。\n",
          "thinkingSignature": "reasoning_content"
        },
        {
          "type": "text",
          "text": "\n\n已经为你生成了李白的《将进酒》音频！🎵\n\n这是李白最著名的诗作之一，豪放洒脱，充满了诗人的浪漫情怀。\n\n**音频链接：** https://ns.chat.360.cn/zhaomi-so/client-up/342516bb3ff503abe941ee3c01c0b73c3595c38.mp3\n\nNO_REPLY"
        }
      ],
      "api": "openai-completions",
      "provider": "zhinao",
      "model": "minimax/MiniMax-M2.5",
      "usage": {
        "input": 362,
        "output": 144,
        "cacheRead": 30288,
        "cacheWrite": 0,
        "totalTokens": 30794,
        "cost": {
          "input": 0,
          "output": 0,
          "cacheRead": 0,
          "cacheWrite": 0,
          "total": 0
        }
      },
      "stopReason": "stop",
      "timestamp": 1775306217134
    }
  }
]
```

```json
mainAgent消息：
[
  {
    "type": "session",
    "version": 3,
    "id": "647cff8b-cf37-4e6e-b7b9-3ac027cc18cf",
    "timestamp": "2026-04-16T10:21:38.111Z",
    "cwd": "/Users/lizhenguo1/.openclaw/workspace"
  },
  {
    "type": "model_change",
    "id": "408a4fe5",
    "parentId": null,
    "timestamp": "2026-04-16T10:21:38.148Z",
    "provider": "zhinao",
    "modelId": "claw-o-46"
  },
  {
    "type": "thinking_level_change",
    "id": "2a2346f6",
    "parentId": "408a4fe5",
    "timestamp": "2026-04-16T10:21:38.148Z",
    "thinkingLevel": "off"
  },
  {
    "type": "custom",
    "customType": "model-snapshot",
    "data": {
      "timestamp": 1776334898152,
      "provider": "zhinao",
      "modelApi": "openai-completions",
      "modelId": "claw-o-46"
    },
    "id": "816026fc",
    "parentId": "2a2346f6",
    "timestamp": "2026-04-16T10:21:38.152Z"
  },
  {
    "type": "message",
    "id": "e7c2d634",
    "parentId": "816026fc",
    "timestamp": "2026-04-16T10:21:39.782Z",
    "message": {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Sender (untrusted metadata):\n```json\n{\n  \"label\": \"openclaw-control-ui\",\n  \"id\": \"openclaw-control-ui\"\n}\n```\n\n[Thu 2026-04-16 18:21 GMT+8] 调用专业虾：生成一个钢铁侠大战柯尔鸭大片，最后柯尔鸭完胜。"
        }
      ],
      "timestamp": 1776334899774
    }
  },
  {
    "type": "message",
    "id": "a63125ea",
    "parentId": "e7c2d634",
    "timestamp": "2026-04-16T10:21:49.489Z",
    "message": {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "\n\nThe user's message starts with \"调用专业虾：\", so I need to check the routing rules in AGENTS_ROUTING.md."
        },
        {
          "type": "toolCall",
          "id": "toolu_bdrk_01XWDN3ihrdqpPKsLSPmx6zc",
          "name": "read",
          "arguments": {
            "file_path": "/Users/lizhenguo1/.openclaw/workspace/AGENTS_ROUTING.md"
          }
        }
      ],
      "api": "openai-completions",
      "provider": "zhinao",
      "model": "claw-o-46",
      "usage": {
        "input": 44053,
        "output": 107,
        "cacheRead": 0,
        "cacheWrite": 0,
        "totalTokens": 44160,
        "cost": {
          "input": 0,
          "output": 0,
          "cacheRead": 0,
          "cacheWrite": 0,
          "total": 0
        }
      },
      "stopReason": "toolUse",
      "timestamp": 1776334899781
    }
  },
  {
    "type": "message",
    "id": "78689d0a",
    "parentId": "a63125ea",
    "timestamp": "2026-04-16T10:21:49.547Z",
    "message": {
      "role": "toolResult",
      "toolCallId": "toolu_bdrk_01XWDN3ihrdqpPKsLSPmx6zc",
      "toolName": "read",
      "content": [
        {
          "type": "text",
          "text": "## 🧠 专业虾路由规则\n\n**仅当用户消息以「调用专业虾：」开头时**，才执行子智能体路由。其他所有 query **直接忽略路由**，正常回复。\n\n- ❌ `生成一个带货短视频` → 正常回复，不触发路由\n- ❌ `帮我写篇公众号文章` → 正常回复，不触发路由\n- ✅ `调用专业虾：生成一个带货短视频` → 触发路由\n\n**触发后的流程**：\n1. 提取冒号后面的任务内容\n2. 从 `agents_list` 选择最匹配的专业虾\n3. 用 `sessions_spawn` 派发任务参数示例如下，task参数请传入步骤1中的任务内容，不要添加任何其它内容：\n\t\t\"arguments\": {\n\t\t  \"runtime\": \"subagent\",\n\t\t  \"agentId\": \"nami_seedance20daoyan\",\n\t\t  \"mode\": \"run\",\n\t\t  \"task\": \"用户需求：生成一个钢铁侠大战孙悟空大片\",\n\t\t  \"timeoutSeconds\": 3600,\n\t\t  \"namiAgentId\":\"对应agents_list元素中的namiAgentId\",\n\t\t  \"agentType\":\"对应agents_list元素中的agentType\",\n\t\t  \"streamTo\":\"parent\"\n\t\t}\n\n4. 汇报结果\n\n**专业虾选择参考：**\n- 编程/开发 → `nami_fullstack_engineer` / `codex` / `opencode` / `claude`\n- 测试 → `nami_qa_engineer`\n- UI 设计 → `nami_ui_designer`\n- 公众号/媒体写作 → `nami-gzh-writer` / `nami-media-writer` / `nami-multi-style-writer`\n- 论文 → `nami-ai-paper`\n- 视频脚本/创意 → `nami-douyin-script` / `nami-script-creative` / `nami-p-video-lite` / `nami-p-video-max`\n- 带货短视频 → `nami-ecommerce-live-shortvideo`\n- 大片生成 → `nami-one-sentence-blockbuster`\n- 热搜短视频 → `nami-selfmedia-hotspot-digital-human`\n- 口播稿 → `nami-patriotic-script-rewrite`\n- 深度思考 → `nami-deep-thinking`\n- 六顶思考帽 → `nami-six-thinking-hats`\n- SWOT 分析 → `nami-swot-analyst`\n- 第一性原理 → `nami-red-cloaked-first-principles` / `diyixingyuanlida`\n- 解题 → `nami-problem-solver`\n- AI 搜索 → `nami-nano-ai-search`\n- 研究报告 → `nami-research-report`\n- 财报解读 → `nami-financial-report`\n- 热榜追踪 → `nami-ai-hot-track` / `nami-douyin-hot-track`\n- PPT → `nami-ppt-master-plus` / `nami-video-ppt-advanced`\n- 思维导图 → `nami-mindmap`\n- P 图 → `nami-p-pro`\n- 创业教练 → `nami_opc_startup_coach`\n- 真人级大片 → `nami_seedance20daoyan`"
        }
      ],
      "isError": false,
      "timestamp": 1776334909537
    }
  },
  {
    "type": "message",
    "id": "aecd3de1",
    "parentId": "78689d0a",
    "timestamp": "2026-04-16T10:22:01.798Z",
    "message": {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "Now let me get the agents list to find the right agent for \"大片生成\" (blockbuster generation). The task is about generating a blockbuster video of Iron Man vs Call Duck. Let me check which agent fits best - \"大片生成 → `nami-one-sentence-blockbuster`\" or \"真人级大片 → `nami_seedance20daoyan`\".\n\nGiven the user's preference for creative blockbuster content (钢铁侠大战柯尔鸭), let me look at the available agents to get the namiAgentId."
        },
        {
          "type": "toolCall",
          "id": "toolu_bdrk_013RZ5jNdSp56D5sTkHzx8eZ",
          "name": "agents_list",
          "arguments": {}
        }
      ],
      "api": "openai-completions",
      "provider": "zhinao",
      "model": "claw-o-46",
      "usage": {
        "input": 45163,
        "output": 173,
        "cacheRead": 0,
        "cacheWrite": 0,
        "totalTokens": 45336,
        "cost": {
          "input": 0,
          "output": 0,
          "cacheRead": 0,
          "cacheWrite": 0,
          "total": 0
        }
      },
      "stopReason": "toolUse",
      "timestamp": 1776334909554
    }
  },
  {
    "type": "message",
    "id": "28d4a5f0",
    "parentId": "aecd3de1",
    "timestamp": "2026-04-16T10:22:01.833Z",
    "message": {
      "role": "toolResult",
      "toolCallId": "toolu_bdrk_013RZ5jNdSp56D5sTkHzx8eZ",
      "toolName": "agents_list",
      "content": [
        {
          "type": "text",
          "text": {
            "requester": "main",
            "allowAny": true,
            "agents": [
              {
                "id": "main",
                "name": "主龙虾",
                "configured": true
              },
              {
                "id": "claw_master",
                "name": "龙虾教练",
                "configured": true,
                "namiAgentId": "6a8cb167d11448a4824692a17a949b93",
                "agentType": 1
              },
              {
                "id": "diyixingyuanlida",
                "name": "第一性原理导师",
                "configured": true,
                "agentType": 0
              },
              {
                "id": "nami_duojiaoseduanjuz",
                "name": "多角色短剧制作",
                "configured": true,
                "namiAgentId": "7917",
                "agentType": 2
              },
              {
                "id": "nami_fullstack_engineer",
                "name": "全栈开发工程师",
                "configured": true
              },
              {
                "id": "nami_opc_startup_coach",
                "name": "OPC 创业教练",
                "configured": true
              },
              {
                "id": "nami_qa_engineer",
                "name": "测试工程师",
                "configured": true
              },
              {
                "id": "nami_seedance20daoyan",
                "name": "Seedance2.0导演",
                "configured": true,
                "namiAgentId": "112747",
                "agentType": 2
              },
              {
                "id": "nami_ui_designer",
                "name": "UI设计师",
                "configured": true
              },
              {
                "id": "namiai",
                "name": "主龙虾",
                "configured": true,
                "namiAgentId": "3ba957d9c98d426c855e73a16baed650",
                "agentType": 0
              }
            ]
          }
        }
      ],
      "details": {
        "requester": "main",
        "allowAny": true,
        "agents": [
          {
            "id": "main",
            "name": "主龙虾",
            "configured": true
          },
          {
            "id": "claw_master",
            "name": "龙虾教练",
            "configured": true,
            "namiAgentId": "6a8cb167d11448a4824692a17a949b93",
            "agentType": 1
          },
          {
            "id": "diyixingyuanlida",
            "name": "第一性原理导师",
            "configured": true,
            "agentType": 0
          },
          {
            "id": "nami_duojiaoseduanjuz",
            "name": "多角色短剧制作",
            "configured": true,
            "namiAgentId": "7917",
            "agentType": 2
          },
          {
            "id": "nami_fullstack_engineer",
            "name": "全栈开发工程师",
            "configured": true
          },
          {
            "id": "nami_opc_startup_coach",
            "name": "OPC 创业教练",
            "configured": true
          },
          {
            "id": "nami_qa_engineer",
            "name": "测试工程师",
            "configured": true
          },
          {
            "id": "nami_seedance20daoyan",
            "name": "Seedance2.0导演",
            "configured": true,
            "namiAgentId": "112747",
            "agentType": 2
          },
          {
            "id": "nami_ui_designer",
            "name": "UI设计师",
            "configured": true
          },
          {
            "id": "namiai",
            "name": "主龙虾",
            "configured": true,
            "namiAgentId": "3ba957d9c98d426c855e73a16baed650",
            "agentType": 0
          }
        ]
      },
      "isError": false,
      "timestamp": 1776334921823
    }
  },
  {
    "type": "message",
    "id": "aab55cef",
    "parentId": "28d4a5f0",
    "timestamp": "2026-04-16T10:22:26.289Z",
    "message": {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "这个任务是\"大片生成\"，根据路由规则，\"真人级大片 → `nami_seedance20daoyan`\" 最匹配。让我派发任务给 Seedance2.0 导演专业虾🎬"
        },
        {
          "type": "toolCall",
          "id": "toolu_bdrk_01GGEkxP9wM9QvmevEdckMys",
          "name": "sessions_spawn",
          "arguments": {
            "runtime": "subagent",
            "agentId": "nami_seedance20daoyan",
            "mode": "run",
            "task": "用户需求：生成一个钢铁侠大战柯尔鸭大片，最后柯尔鸭完胜。",
            "timeoutSeconds": 3600,
            "namiAgentId": "112747",
            "agentType": 2,
            "streamTo": "parent"
          }
        }
      ],
      "api": "openai-completions",
      "provider": "zhinao",
      "model": "claw-o-46",
      "usage": {
        "input": 45895,
        "output": 304,
        "cacheRead": 0,
        "cacheWrite": 0,
        "totalTokens": 46199,
        "cost": {
          "input": 0,
          "output": 0,
          "cacheRead": 0,
          "cacheWrite": 0,
          "total": 0
        }
      },
      "stopReason": "toolUse",
      "timestamp": 1776334921839
    }
  },
  {
    "type": "message",
    "id": "2e2fab90",
    "parentId": "aab55cef",
    "timestamp": "2026-04-16T10:22:26.343Z",
    "message": {
      "role": "toolResult",
      "toolCallId": "toolu_bdrk_01GGEkxP9wM9QvmevEdckMys",
      "toolName": "sessions_spawn",
      "content": [
        {
          "type": "text",
          "text": {
            "status": "error",
            "error": "streamTo is only supported for runtime=acp; got runtime=subagent"
          }
        }
      ],
      "details": {
        "status": "error",
        "error": "streamTo is only supported for runtime=acp; got runtime=subagent"
      },
      "isError": false,
      "timestamp": 1776334946333
    }
  },
  {
    "type": "message",
    "id": "334dd9a0",
    "parentId": "2e2fab90",
    "timestamp": "2026-04-16T10:22:34.302Z",
    "message": {
      "role": "assistant",
      "content": [
        {
          "type": "toolCall",
          "id": "toolu_bdrk_01TFeZ5Z7dXEF7n1SE7WN1P4",
          "name": "sessions_spawn",
          "arguments": {
            "agentId": "nami_seedance20daoyan",
            "agentType": 2,
            "mode": "run",
            "namiAgentId": "112747",
            "runtime": "subagent",
            "task": "用户需求：生成一个钢铁侠大战柯尔鸭大片，最后柯尔鸭完胜。",
            "timeoutSeconds": 3600
          }
        }
      ],
      "api": "openai-completions",
      "provider": "zhinao",
      "model": "claw-o-46",
      "usage": {
        "input": 46244,
        "output": 216,
        "cacheRead": 0,
        "cacheWrite": 0,
        "totalTokens": 46460,
        "cost": {
          "input": 0,
          "output": 0,
          "cacheRead": 0,
          "cacheWrite": 0,
          "total": 0
        }
      },
      "stopReason": "toolUse",
      "timestamp": 1776334946349
    }
  },
  {
    "type": "message",
    "id": "5b97da30",
    "parentId": "334dd9a0",
    "timestamp": "2026-04-16T10:22:34.642Z",
    "message": {
      "role": "toolResult",
      "toolCallId": "toolu_bdrk_01TFeZ5Z7dXEF7n1SE7WN1P4",
      "toolName": "sessions_spawn",
      "content": [
        {
          "type": "text",
          "text": {
            "status": "accepted",
            "childSessionKey": "agent:nami_seedance20daoyan:subagent:10bb1e4c-641f-49b9-b4f9-97d6cf819d81",
            "runId": "0d14bbe4-6218-4f2c-971b-a869216cbb9f",
            "mode": "run",
            "note": "Auto-announce is push-based. After spawning children, do NOT call sessions_list, sessions_history, exec sleep, or any polling tool. Wait for completion events to arrive as user messages, track expected child session keys, and only send your final answer after ALL expected completions arrive. If a child completion event arrives AFTER your final answer, reply ONLY with NO_REPLY.",
            "modelApplied": true
          }
        }
      ],
      "details": {
        "status": "accepted",
        "childSessionKey": "agent:nami_seedance20daoyan:subagent:10bb1e4c-641f-49b9-b4f9-97d6cf819d81",
        "runId": "0d14bbe4-6218-4f2c-971b-a869216cbb9f",
        "mode": "run",
        "note": "Auto-announce is push-based. After spawning children, do NOT call sessions_list, sessions_history, exec sleep, or any polling tool. Wait for completion events to arrive as user messages, track expected child session keys, and only send your final answer after ALL expected completions arrive. If a child completion event arrives AFTER your final answer, reply ONLY with NO_REPLY.",
        "modelApplied": true
      },
      "isError": false,
      "timestamp": 1776334954634
    }
  },
  {
    "type": "message",
    "id": "491d52f6",
    "parentId": "5b97da30",
    "timestamp": "2026-04-16T10:22:51.478Z",
    "message": {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "🎬 已派遣 **Seedance2.0 导演虾** 开工！\n\n正在为皇上生成「钢铁侠大战柯尔鸭」创意大片，剧情走向：柯尔鸭完胜 🦆💥🦾\n\n视频生成需要一些时间，完成后会自动推送结果，请稍候～"
        }
      ],
      "api": "openai-completions",
      "provider": "zhinao",
      "model": "claw-o-46",
      "usage": {
        "input": 46670,
        "output": 113,
        "cacheRead": 0,
        "cacheWrite": 0,
        "totalTokens": 46783,
        "cost": {
          "input": 0,
          "output": 0,
          "cacheRead": 0,
          "cacheWrite": 0,
          "total": 0
        }
      },
      "stopReason": "stop",
      "timestamp": 1776334954647
    }
  }
]
```

```json
subagent消息示例： subagent_stream_relay
{
  "type": "event",
  "event": "agent",
  "payload": {
    "runId": "0d14bbe4-6218-4f2c-971b-a869216cbb9f",
    "stream": "nami_panel",
    "data": {
      "runId": "0d14bbe4-6218-4f2c-971b-a869216cbb9f",
      "seq": 2157,
      "stream": "assistant",
      "ts": 1776336057455,
      "data": {
        "text": "<thinking>让我分析用户的输入：\n\n1. **视频内容描述**：\n   - 用户原始输入：生成一个钢铁侠大战柯尔鸭大片，最后柯尔鸭完胜。\n   - 已经提供了扩充后的详细描述：未来城市的摩天大楼顶端，狂风呼啸。钢铁侠全副武装悬浮于半空，掌心炮口蓄能发出耀眼的蓝光，气势逼人。地面上，一只呆萌的柯尔鸭淡定地梳理羽毛，毫无惧色。战斗爆发，钢铁侠俯冲发射激光，柯尔鸭灵活扭动身躯，迈着魔性的步伐完美闪避，随即猛然振翅，掀起肉眼可见的气浪冲击波。钢铁侠装甲系统瞬间失灵，踉跄后退，最终被柯尔鸭一记\"神鸭摆尾\"狠狠拍飞，化作天边的一颗流星。柯尔鸭站在楼顶边缘，仰天嘎嘎大叫，尽显王者风范。\n\n2. **参考素材**：\n   - 用户未提供任何图片、视频、音频URL\n   - 这些参数应该为空数组或null\n\n3. **视频参数**：\n   - 视频比例：用户未指定，默认为 \"16:9\"\n   - 视频时长：用户未指定，默认为 \"9s\"\n   - 分辨率：默认为 \"720p\"\n\n4. **其他参数**：\n   - with_sound: true（生成声音）\n   - web_search: true（联网搜索）\n   - nami_app_h5_reason: 需要填写调用目的\n\n准备构建工具调用参数，确保所有默认值和用户需求都被准确捕捉。将根据详细描述生成一个生动有趣的视频场景。\n\n参数包括视频比例、时长、分辨率，并启用声音和网络搜索功能。第一次调用</thinking>",
        "delta": "<thinking>调用</thinking>"
      },
      "block_key": "778342",
      "conversationID": "agent:nami_seedance20daoyan:subagent:10bb1e4c-641f-49b9-b4f9-97d6cf819d81@@nm&&5ad6b0ec-86e2-4507-b8cc-2f2e71a069ec"
    },
    "sessionKey": "agent:nami_seedance20daoyan:subagent:10bb1e4c-641f-49b9-b4f9-97d6cf819d81",
    "seq": 2157,
    "ts": 1776336057455
  },
  "seq": 3567
}
```

# 模型错误返回

```json
{
  "role": "assistant",
  "content": [],
  "api": "openai-completions",
  "provider": "zhinao",
  "model": "claw-o-45",
  "usage": {
    "input": 0,
    "output": 0,
    "cacheRead": 0,
    "cacheWrite": 0,
    "totalTokens": 0,
    "cost": {
      "input": 0,
      "output": 0,
      "cacheRead": 0,
      "cacheWrite": 0,
      "total": 0
    }
  },
  "stopReason": "error",
  "timestamp": 1778210735572,
  "errorMessage": "429 访问过于频繁:api-key请求token数超出分钟限制"
}
```
