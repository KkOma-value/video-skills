# Field Archive Film Skill

这是从用户提供的参考视频中提炼出的可复用视频风格 Skill。

## 文件

- `SKILL.md`：完整执行规则，可放入 Claude Code、Codex 或其他 Agent 的 Skills 目录。
- `references/style-profile.yaml`：机器可读风格参数。
- `references/source-analysis.md`：参考视频的具体拆解和数据。
- `templates/generation-prompt.md`：创建新视频时的输入模板。
- `templates/storyboard.md`：标准分镜格式。
- `examples/ai-workspace-example.md`：原创应用示例。
- `references/contact-sheet.jpg`：参考视频采样图，仅用于理解风格。

## 最简用法

将整个文件夹复制到你的 Skills 目录，然后输入：

> 使用 field-archive-film skill，为我的产品制作一支 30 秒发布片。核心概念是……，风格强度 balanced。

## 推荐原则

默认使用 `balanced`。重点复用视觉语法，不复刻原视频的品牌、镜头或道具组合。
