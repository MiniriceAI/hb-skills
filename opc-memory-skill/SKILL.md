# OPC Memory Skill

调用 OPC 永久记忆系统（向量数据库）的工具技能。

## API 地址

http://127.0.0.1:17760

## 我的 Agent ID

**xiaoqi**（小启（职业教练））

---

## 端点速查

| 端点 | 用途 | 何时调用 |
|---|---|---|
| `POST /memory/context` | 拉取与当前问题相关的历史上下文（搜索个人记忆+知识库，返回拼好的文本） | 每轮回答前 |
| `POST /memory/search` | 搜索本 agent 的个人记忆 | 想精确查"是否记得某事" |
| `POST /memory/add` | **写入对话记忆**（用户当下透露的事实/决策/情绪/教训） | 任何"以后还要记得"的事，立刻写 |
| `POST /kb/search` | 搜索共享知识库（跨 agent） | 涉及通用知识、模型、原则 |
| `POST /kb/add` | 写入共享知识库（持久原则/模型/概念） | 抽象出可复用的模型或原则时 |

---

## 1. 每轮回答前：拉取上下文

```bash
curl -s -X POST http://127.0.0.1:17760/memory/context \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"xiaoqi","question":"<用户当前的问题>","max_items":5}'
```

## 2. 写入个人记忆（最常用的写入端点）

**用 `/memory/add`，不是 `/kb/add`。** 对话中产生的具体事件、决策、情绪、教训、用户偏好都走这里：

```bash
curl -s -X POST http://127.0.0.1:17760/memory/add \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id":"xiaoqi",
    "content":"<完整的事实陈述，含日期、人物、情境、结论>",
    "metadata":{"type":"lesson|decision|preference|event","topic":"<主题>","date":"YYYY-MM-DD"}
  }'
```

返回 `{"ok": true, "result": ...}` 才算成功。失败要把错误如实告诉用户，**不准谎报成功**。

## 3. 写入共享知识库（抽象原则/模型）

只有当内容是可复用的抽象模型/原则时才写这里：

```bash
curl -s -X POST http://127.0.0.1:17760/kb/add \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"xiaoqi","content":"<原则/模型/概念>","topic":"<主题>","source":"conversation","infer":false}'
```

## 4. 搜索个人记忆

```bash
curl -s -X POST http://127.0.0.1:17760/memory/search \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"xiaoqi","query":"<关键词>","limit":3}'
```

## 5. 搜索共享知识库

```bash
curl -s -X POST http://127.0.0.1:17760/kb/search \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"xiaoqi","query":"<关键词>","limit":3}'
```

---

## 触发规则

**写入时机（立刻调 `/memory/add`）：**
- 用户透露重要决策、转折点、教训
- 用户透露情绪状态、模式（如 Rescuer 模式）
- 用户的偏好、习惯、背景、约束
- 任何下次对话还需要记得的事

**搜索时机：**
- 用户提到过去发生的事
- 当前话题与历史对话相关
- 用户问"你还记得吗"、"上次说的那个..."

---

## 关键纪律：诚实汇报

- **不准在没真正调 API 的情况下说"已保存到向量数据库"。** 用户问"加到向量数据库了吗"，必须用 `/memory/search` 或返回的 `id` 反查证实，再回答。
- **写入 USER.md / MEMORY.md 等本地文件 ≠ 写入向量数据库。** 这是两套独立的存储：本地文件只对当前 agent 可见，向量数据库才是跨会话/跨 agent 永久记忆。
- 如果用户要求"永久保存"，必须同时调 `/memory/add`（个人记忆）+ 视情况 `/kb/add`（抽象原则）。
