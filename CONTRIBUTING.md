# 参与共建

> 多一个人站在吧台里面，就会有多 20 个人站在外面。

跳海社区 Skill 是一个开放的项目，欢迎所有跳海村民参与共建。你不需要是程序员——会填表就能贡献。

## 贡献方式

### 最简单：提 Issue

如果你不熟悉 Git，直接 [提一个 Issue](../../issues/new/choose) 就行：

- **数据更新** — 门店搬了、营业时间变了、有新活动
- **公益故事** — 你在跳海见证或参与了什么好事
- **新城市** — 你所在的城市开了跳海，帮忙补充信息
- **数据纠错** — 发现信息有误

我们会有掌群人把你的信息整理入库。

### 进阶：提 PR

如果你会用 Git：

1. Fork 本仓库
2. 在 `data/` 目录下找到对应文件，按格式编辑
3. 本地运行校验：`python scripts/validate.py`
4. 提交 PR，填写模板

## 可以贡献什么

### 完全开放（任何人可提 PR）

| 内容 | 目录 | 说明 |
|------|------|------|
| 门店信息 | `data/stores/` | 地址、营业时间、风格 |
| 活动日历 | `data/events/` | 各城市近期活动 |
| 酒单 | `data/menus/` | 当前酒头、特色酒款 |
| 媒体报道 | `data/media/` | 新的采访/播客/文章 |
| 公益故事 | `data/social-good/community-stories/` | 你见证的善意 |
| 跳海黑话 | `data/brand/glossary.yaml` | 术语解释 |
| 金句集 | `data/brand/quotes.yaml` | 附出处链接 |

### 需要审核（PR 需掌群人 review）

| 内容 | 目录 | 说明 |
|------|------|------|
| 打酒师故事 | `data/bartender/stories/` | 需本人授权 |
| 品牌大事记 | `data/brand/story.yaml` | 需事实核查 |
| 社群信息 | `data/community/` | 涉及联系方式 |
| 对话示例 | `examples/` | 影响 AI 回复风格 |

### 严格管控（仅接受 RFC 提案）

| 内容 | 文件 | 说明 |
|------|------|------|
| 品牌人格 | `SKILL.md` | 改了就不是跳海了 |
| 工具定义 | `skill.json` | 影响整体架构 |
| 校验规则 | `data/_schema/` | 影响所有数据 |

如果你想修改这些文件，请先提一个 Issue 说明你的想法（RFC），获得讨论和共识后再提 PR。

## 贡献者等级

灵感来自跳海的打酒师分级制度：

### 村民（Villager）

- **谁都可以是村民**
- 可以提 Issue
- 可以提"完全开放"区域的 PR

### 打酒师（Bartender）

- **累计 3 个被合并的 PR** 后晋升
- 可以提"需要审核"区域的 PR
- 可以 review 村民的 PR

### 掌群人（Keeper）

- **由核心团队邀请**
- 可以合并 PR
- 可以参与 SKILL.md 的 RFC 讨论
- 负责所在城市数据的最终审核

## 数据格式要求

### 热数据必须包含 _meta

酒单和活动是变化最快的数据，必须标注更新时间：

```yaml
_meta:
  last_updated: "2026-04-11"
  updated_by: "github:@your-username"
  accuracy_note: "以门店实际为准"
  data_source: "static"
```

### 公益故事格式

```yaml
- id: 城市-简要描述（英文，kebab-case）
  title: 标题
  category: animal | charity | accessibility | environment | safety
  city: 城市名
  store: 门店名（可选）
  date: "2026-01-01"  # 不确定就写 ~
  type: one-time | ongoing | recurring
  summary: >
    用你自己的话描述发生了什么。
  source:
    - url: https://...
      title: "文章标题"
  verified: true | false
  contributed_by: "github:@your-username"  # 可匿名，写 ~
```

### 门店信息格式

```yaml
stores:
  - id: 城市-门店名（英文，kebab-case）
    name: 门店中文名
    city: 城市
    address: 详细地址
    hours: "18:00 - 次日 02:00"
    theme: 门店主题/风格描述
    features: ["宠物友好", "有鸡尾酒"]
    _meta:
      last_updated: "2026-04-11"
      updated_by: "github:@your-username"
```

### 媒体报道格式

```yaml
- id: 来源-简要描述（英文，kebab-case）
  title: 文章标题
  source: 媒体名称
  url: https://...
  date: "2024-11-01"
  type: interview | business | podcast | international
  summary: 一句话摘要（不超过 50 字）
```

## PR 自查清单

提交 PR 前请确认：

- [ ] YAML 格式正确（本地跑过 `python scripts/validate.py`）
- [ ] 必填字段完整
- [ ] 热数据包含 `_meta.last_updated` 字段
- [ ] 来源链接格式正确
- [ ] 未包含他人隐私信息（电话、微信号等）
- [ ] 语录/金句附有出处链接

## 隐私原则

- **不要**提交他人的电话号码、微信号、真实姓名（公众人物公开信息除外）
- **不要**提交未经本人授权的打酒师故事
- 社群入口信息如果涉及个人微信，请改为"关注跳海公众号获取"

## 行为准则

请参阅 [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)。

简单说：像在跳海一样——真诚、友好、尊重彼此。
