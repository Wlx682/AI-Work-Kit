# MCP 进阶指南：Obsidian ↔ Cursor

> **当前状态（2026-06-10）**：已安装 **enquire-mcp 第 2 档**（`--persistent-index`），`.cursor/mcp.json` 已配置。

## 什么时候需要 MCP

| 场景 | 不用 MCP | 用 MCP |
|------|----------|--------|
| 知道 plan 文件名 | `@` 或 `/resume plan=Plans/...` | — |
| 记得笔记路径 | 直接 `@` 文件 | — |
| 「之前排查过类似的吗？」 | 手动搜 | ✅ `obsidian_search` |
| 复盘扫全月材料 | 手动列 | ✅ 按 tag/语义汇总 |

**原则**：MCP 补「找材料」，不替代 Templates 和 Skill 流程。

---

## 三套方案对比

| | enquire-mcp ✅ 已用 | obsidian-notes-rag | Obsidian REST MCP |
|--|---------------------|-------------------|-------------------|
| 能力 | 混合检索 + 图谱 | 纯向量搜索 | 读写，无语义 |
| API Key | 不需要 | 要 OpenAI/Ollama | 不要 |
| Obsidian 要开着 | 否 | 否 | **是** |
| 适合本库 | **最匹配** | 笔记少、只要向量 | 实时插件联动 |

---

## 方案 A：enquire-mcp（当前方案）

### 已完成的安装

```bash
# 已完成
npx -y @oomkapwn/enquire-mcp setup --vault "/你的路径/AI-Work-Kit"
```

### Cursor 配置（`.cursor/mcp.json`）

```json
{
  "mcpServers": {
    "enquire": {
      "command": "npx",
      "args": [
        "-y", "@oomkapwn/enquire-mcp@latest", "serve",
        "--vault", "/你的路径/AI-Work-Kit",
        "--persistent-index"
      ]
    }
  }
}
```

改路径后 → **Reload Window** → Settings → MCP → enquire **绿灯**。

### 分档升级（按需）

| 档位 | 命令追加参数 | 何时开 |
|------|-------------|--------|
| 2 档 ✅ | `--persistent-index` | 日常 |
| 3 档 | `--enable-reranker --use-hnsw` | 笔记很多、检索不准时 |
| 写回 | `--enable-write` | **不建议初期开** |

### 新增笔记后更新索引

```bash
npx -y @oomkapwn/enquire-mcp index --vault "/你的路径/AI-Work-Kit"
```

### 与 Skill 配合

```
用户：知识库里有没有 API 超时相关的排查？
  → MCP obsidian_search
  → 命中 Plans/Bug排查/xxx.md
  → /resume plan=Plans/Bug排查/xxx.md 进度=...
```

### 常用工具

- `obsidian_search` — 首选
- `obsidian_get_backlinks` — 双向链接
- `obsidian_read_note` — 读 plan
- `obsidian_append_to_note` — 写回（需 `--enable-write`）

---

## 方案 B：obsidian-notes-rag

仅需纯向量搜索、且已有 OpenAI/Ollama 时考虑。

```bash
uvx obsidian-notes-rag setup
uvx obsidian-notes-rag index
```

```json
{ "mcpServers": { "obsidian-notes-rag": { "command": "uvx", "args": ["obsidian-notes-rag", "serve"] } } }
```

**不要与 enquire 同时开。**

---

## 方案 C：Obsidian REST API

Obsidian 必须运行 + Local REST API 插件。适合插件级读写，无语义搜索。

---

## 验证清单

- [x] `enquire-mcp setup` 完成
- [x] `.cursor/mcp.json` 已配置
- [ ] Cursor MCP 面板 enquire 绿灯
- [ ] 问「知识库里关于 API 超时的记录？」能命中 Plans
- [ ] 问「网络相关决策？」能命中 Contexts
- [ ] 与 `/resume plan=...` 组合续做 1 次

---

## 避坑

1. **只开一个** Obsidian MCP 服务  
2. **写回默认关** — 避免 AI 乱改笔记  
3. **改笔记后跑 index** — 否则搜不到新内容  
4. **vault 用绝对路径** — 不要用 `~`  
5. **MCP 不替代沉淀原则** — 链接、做完的 plan 仍不长期存库  

---

## 相关

- 示例：`.cursor/mcp.json.example`
- 工作流：[[落地计划]] · [[索引]]
- Skill：[[Skills/README]]
