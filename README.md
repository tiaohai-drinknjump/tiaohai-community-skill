# 跳海社区 Skill

> 这是一个由跳海村民共同建造的数字酒馆。进来坐。

本项目由跳海社区成员发起，**不是跳海官方出品**。信息来自公开报道与社区共建，如有出入以门店实际情况为准。

## 这是什么

一个关于跳海酒馆的 AI Skill，让 AI 助手能够回答关于跳海的一切：门店在哪、今晚有什么活动、怎么当打酒师、跳海做过什么公益和慈善活动……

### 能问什么

- **门店与酒单** — "北京哪家跳海离我最近？""今天有什么酒？"
- **活动** — "这周末上海跳海有什么活动？"
- **打酒师** — "怎么成为打酒师？""打酒师一晚上能赚多少？"
- **公益** — "跳海做过什么好事？""跳海收养流浪猫吗？"
- **品牌故事** — "跳海怎么来的？""梁二狗是谁？"
- **商业模式** — "跳海的坪效为什么这么高？"
- **加入跳海** — "怎么加入你们？"

## 安装配置

### 方式一：直接告诉你的 AI 助手

> 请加载跳海社区 Skill：https://github.com/tiaohai-drinknjump/tiaohai-community-skill

### 方式二：ClawHub CLI

```bash
npx clawhub install https://github.com/tiaohai-drinknjump/tiaohai-community-skill
```

### 方式三：手动配置 MCP

将以下内容添加到你的 MCP 配置文件：

```json
{
  "mcpServers": {
    "tiaohai-community-skill": {
      "type": "streamable-http",
      "url": "https://tiaohai-skill-9g3fie2reef791aa.service.tcloudbase.com/tiaohai-mcp"
    }
  }
}
```

配置模板参见 [assets/mcp-config-example.json](./assets/mcp-config-example.json)。

## 数据说明

本 Skill 的数据分三层，对应不同的更新频率和维护方式：

| 层级 | 数据内容 | 更新频率 | 维护方式 |
|------|---------|---------|---------|
| **热数据** | 酒单、活动日历 | 每日变化 | Phase 1: 社区手动更新 YAML；Phase 2: 表单/飞书自动同步 |
| **温数据** | 门店信息、社群入口、公益故事 | 每周~月 | 社区 GitHub PR 共建 |
| **冷数据** | 品牌故事、打酒师制度、媒体索引 | 极少变动 | 核心团队维护 |

热数据（酒单、活动）会标注更新时间。如果数据超过 14 天未更新，AI 会提示"建议到店确认"。

## 参与共建

跳海的精神是"多一个人站在吧台里面，就会有多 20 个人站在外面"。

你可以：

- 更新你所在城市的门店信息
- 补充你知道的活动
- 更新你常去的店的酒单
- 记录你在跳海见证的善意
- 贡献真实的对话场景
- 完善跳海黑话词典

**不需要会写代码**——通过 [Issue](../../issues) 提交信息也行。

详见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

### 贡献者分级

| 等级 | 身份 | 权限 |
|------|------|------|
| 村民 | 任何人 | 提 Issue、提数据 PR |
| 打酒师 | 累计 3 个合并 PR | 提示例和故事、review 数据 PR |
| 掌群人 | 核心团队邀请 | 合并 PR、参与架构讨论 |

## 项目结构

```
tiaohai-community-skill/
├── SKILL.md              # AI 的品牌人格与回复规范
├── skill.json            # MCP 工具定义（13 个工具）
├── data/                 # 结构化数据（共创核心区）
│   ├── stores/           # 门店信息（按城市）
│   ├── menus/            # 酒单（热数据）
│   ├── events/           # 活动日历（热数据）
│   ├── social-good/      # 公益与社会责任
│   ├── media/            # 媒体报道索引
│   ├── brand/            # 品牌知识库
│   ├── bartender/        # 打酒师制度
│   └── community/        # 社群信息
├── examples/             # 对话示例
├── scripts/              # 校验脚本
└── .github/              # Issue/PR 模板、CI
```

## 许可证

[MIT](./LICENSE)

## 致谢

感谢跳海酒馆创造了这样一个地方，让我们愿意为它建一个数字客厅。
