# Video Skills

一个面向 AI Agent 的视频创作 Skill 合集。每个子目录都是可独立安装、触发和复用的 Skill；它们保留各自的视觉语言与创作流程。

## 包含的 Skills

| Skill | 适用场景 | 核心效果 |
| --- | --- | --- |
| [field-archive-film](skills/field-archive-film/) | 品牌片、概念预告、产品发布 | 科学档案、实体实验、物件编舞、发现式叙事 |
| [faceted-noir-lyric-video](skills/faceted-noir-lyric-video/) | 歌词视频、音乐短片、叙事预告 | 黑红墨绿、纸雕低多边形、符号转化、2.5D 图形叙事 |

## 安装一个 Skill

克隆合集后，将需要的子目录放入所用 Agent 的 Skills 目录：

```bash
git clone https://github.com/KkOma-value/video-skills.git
cp -R video-skills/skills/faceted-noir-lyric-video ~/.codex/skills/
```

也可以安装 `field-archive-film`，或将对应 `SKILL.md` 与资源目录导入其他 Agent 平台。

## 使用

附上音乐、歌词/文案、人物或产品素材，并明确所选 Skill。例如：

```text
Use $faceted-noir-lyric-video to turn these materials into a 30-second narrative lyric video.
```

每个 Skill 都应使用用户拥有或已获授权的素材，并仅复用抽象的视觉与剪辑语法。
