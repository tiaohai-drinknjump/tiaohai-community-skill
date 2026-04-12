# 部署指南 — 腾讯 CloudBase

## 前提条件

- 腾讯云账号（已实名认证）
- Node.js 16+
- 安装 CloudBase CLI：`npm i -g @cloudbase/cli`

## 步骤

### 1. 开通 CloudBase

```bash
# 登录腾讯云控制台 → 云开发 CloudBase → 创建环境
# 选择"按量计费"（有免费额度）
# 记下环境 ID（如 tiaohai-xxx）
```

### 2. 配置环境 ID

编辑项目根目录的 `cloudbaserc.json`，把 `{{YOUR_ENV_ID}}` 替换为你的环境 ID：

```json
{
  "envId": "tiaohai-xxx"
}
```

### 3. 配置飞书凭证（可选）

如果已经从跳海运营获得了飞书多维表格的凭证，编辑 `cloudbaserc.json` 中的 `envVariables`：

```json
{
  "FEISHU_APP_ID": "cli_xxxx",
  "FEISHU_APP_SECRET": "xxxx",
  "FEISHU_BOTTLE_APP_TOKEN": "xxxx",
  "FEISHU_BOTTLE_TABLE_ID": "xxxx",
  "FEISHU_MENU_APP_TOKEN": "xxxx",
  "FEISHU_MENU_TABLE_ID": "xxxx",
  "FEISHU_EVENT_APP_TOKEN": "xxxx",
  "FEISHU_EVENT_TABLE_ID": "xxxx"
}
```

如果还没有飞书凭证，可以全部留空或删除——服务会自动降级到静态 YAML 数据。漂流瓶会使用内存存储（重启丢失，仅用于测试）。

### 4. 安装依赖

```bash
cd server
npm install
```

### 5. 本地测试

```bash
cd server
node index.js
# 服务启动在 http://localhost:3000
```

测试工具调用：

```bash
# 查询门店
curl -X POST http://localhost:3000 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_store_info","arguments":{"city":"北京"}}}'

# 查询品牌故事
curl -X POST http://localhost:3000 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_brand_story","arguments":{}}}'

# 投递漂流瓶
curl -X POST http://localhost:3000 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"post_bottle","arguments":{"city":"北京","store":"后海店","message":"今晚十点，穿格子衬衫坐吧台最左边","identity":"anonymous"}}}'
```

### 6. 登录 CloudBase CLI

```bash
tcb login
```

### 7. 部署

```bash
# 在项目根目录执行
tcb fn deploy tiaohai-mcp --force
```

### 8. 创建 HTTP 触发路径

```bash
tcb service create -f tiaohai-mcp -p /tiaohai-mcp
```

部署完成后，你的 MCP 服务地址为：

```
https://{YOUR_ENV_ID}.service.tcloudbase.com/tiaohai-mcp
```

### 9. 更新 MCP 配置模板

编辑 `assets/mcp-config-example.json`：

```json
{
  "mcpServers": {
    "tiaohai-community-skill": {
      "type": "streamable-http",
      "url": "https://{YOUR_ENV_ID}.service.tcloudbase.com/tiaohai-mcp"
    }
  }
}
```

## 验证

```bash
# 列出工具
curl -X POST https://{YOUR_ENV_ID}.service.tcloudbase.com/tiaohai-mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

应返回 15 个工具的列表。

## 更新数据后重新部署

修改 `data/` 目录下的 YAML 文件后：

```bash
tcb fn deploy tiaohai-mcp --force
```

数据文件会随云函数一起上传。

## 环境变量说明

| 变量 | 必填 | 说明 |
|------|------|------|
| FEISHU_APP_ID | 否 | 飞书应用 ID |
| FEISHU_APP_SECRET | 否 | 飞书应用密钥 |
| FEISHU_BOTTLE_APP_TOKEN | 否 | 漂流瓶多维表格的 app_token |
| FEISHU_BOTTLE_TABLE_ID | 否 | 漂流瓶多维表格的 table_id |
| FEISHU_MENU_APP_TOKEN | 否 | 酒单多维表格的 app_token |
| FEISHU_MENU_TABLE_ID | 否 | 酒单多维表格的 table_id |
| FEISHU_EVENT_APP_TOKEN | 否 | 活动多维表格的 app_token |
| FEISHU_EVENT_TABLE_ID | 否 | 活动多维表格的 table_id |

所有飞书变量都是可选的。不配置时，查询类工具使用静态 YAML 数据，漂流瓶使用内存存储。
