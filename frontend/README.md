<!--
  前端项目说明文档
  记录启动方式、代理配置和部署时的环境变量
-->

# Shopkeeper Agent Frontend

匹配后端 `shopkeeper-agent` 的问数聊天前端，技术栈为 React + Vite + Tailwind CSS + pnpm。

## 启动

```bash
cd frontend
pnpm install
pnpm dev
```

默认开发代理会把 `/api` 转发到 `http://127.0.0.1:8000`，对应后端的 `POST /api/query` SSE 接口。后端用 `uv run shopkeeper-agent` 启动。

如需修改后端地址：

```bash
cp .env.example .env
```

然后调整：

```bash
VITE_DEV_PROXY_TARGET=http://127.0.0.1:8000
```

如果前端与后端不在同一域部署，可设置：

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## 其他命令

```bash
pnpm lint    # tsc --noEmit 类型检查
pnpm build   # 类型检查 + 生产构建，产物在 frontend/dist
```

## 与后端的约定

- 请求：`POST /api/query`，JSON 请求体 `{"query": "..."}`。
- 响应：`text/event-stream`，每帧为 `data: <JSON>\n\n`。
- 事件类型（`src/types/agent.ts`）：
  - `{"type":"progress","step":"...","status":"running|success|error"}`
  - `{"type":"result","data":[...]}`
  - `{"type":"error","message":"..."}`

`src/components/StepRail.tsx` 中 `nodes` 的 `step` 必须与 `app/agent/nodes/*.py` 里写入 `stream_writer` 的 `step` 字符串逐字一致，否则对应节点会一直显示为 pending。
