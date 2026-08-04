# Field Archive Film 生成模板

## 输入

- 参考风格基线：默认使用随 skill 固化的参考视频 profile；只有用户明确提供新参考时才替换它。
- 主题/产品：`{{SUBJECT}}`
- 核心研究命题：`{{CORE_IDEA}}`
- 时长：`{{DURATION_SECONDS}}` 秒
- 帧率：`{{FPS|24}}`
- 比例：`{{ASPECT_RATIO}}`
- 投放平台：`{{PLATFORM}}`
- 风格强度：`{{STYLE_STRENGTH|balanced}}`
- 参考视频审计：`{{REFERENCE_AUDIT|use_bundled_source_profile}}`
- 新核心材质：`{{HERO_MATERIAL}}`
- 新图形母题：`{{GRAPHIC_MOTIF}}`
- 新结尾符号/短句：`{{END_SYMBOL}}`
- 资产策略：`{{SOURCE_STRATEGY|hybrid_practical_and_controlled_generation}}`
- 必须出现：`{{MUST_INCLUDE}}`
- 禁止出现：`{{MUST_AVOID}}`
- 是否旁白：`{{VOICEOVER|false}}`

## 创作约束

1. 把核心价值转译成一个可以被观察、测量、排列或显影的实体实验。
2. 选择 3–5 个围绕新主题的视觉母题，构建新的形状、方向或动作图形链。
3. 主要使用顶视、正面静物和微距镜头；人物只作为手部或前臂尺度出现。
4. 使用冷灰绿、冷白、档案棕、石墨黑和少量深青蓝作为色彩角色；黑白高反差只用于材料冲击。
5. 让物体通过展开、翻页、对齐、称量、吸附、聚集、扩散、显影或归位完成叙事。
6. 活跃段落优先控制在 `0.3–1.2s`，开场保留 `1.5–2s`，结尾保留 `4–6s`；根据总时长重新缩放，不硬复制参考时长。
7. 以硬切、图形匹配和动作匹配为主，让数字线条服从真实物理。
8. 结尾将复杂实验结果简化为全新的符号或短句，不复制参考字标的文字、形态或变形过程。
9. 不复制参考品牌、原文案、具体技术文字、完整道具组合或镜头顺序。
10. 每个镜头和 micro-beat 都要用 `round(seconds × FPS)` 写出半开帧范围 `[start_frame, end_frame)`；不得只输出时间码。

## 提示词构造顺序

按以下顺序组织总提示词和分镜级提示词：

`叙事命题 → 研究空间 → 主要材质 → 单一动作 → 摄影机/镜头 → 光线/色彩 → 物理感 → 图形连接 → 剪辑节奏 → 声音触发 → 结尾锁定`

使用具体的可见名词和动作，避免只写“高级、科技、神秘、电影感”等空泛形容词。

## 输出顺序

1. 一句话创意概念。
2. 参考审计摘要与证据等级（有参考视频时）。
3. 原创视觉母题和图形链。
4. 阶段时间轴。
5. 镜头级完整分镜。
6. 节奏级 micro-beat 摘要。
7. AI 视频总提示词。
8. 分镜级提示词。
9. 负面提示词。
10. 声音设计和同步点。
11. 原创性检查。

镜头表和 micro-beat 表都必须显示 `[start_frame, end_frame)`、时间码/时长和声音触发；若没有参考视频，按 `FPS` 计算帧范围。

## 负面提示词

`neon cyberpunk, blue-purple tech gradient, full-screen HUD, stock corporate montage, smiling office team, fast handheld camera, drone orbit, exaggerated camera spin, glitch preset, flash transition, zoom tunnel, elastic bounce, cartoon overshoot, uncontrolled particles, glowing energy ball, galaxy background, long explanatory subtitles, source brand, source logo, source wordmark, source readable copy, copied prop combination, copied shot order, copied glyph morph`
