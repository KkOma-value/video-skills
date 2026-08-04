# Frame Audit

## 目录

- [目的](#目的)
- [证据等级](#证据等级)
- [分析产物](#分析产物)
- [镜头归并规则](#镜头归并规则)
- [报告模板](#报告模板)

## 目的

将参考视频拆成可复核的证据层，再把证据转译成原创视觉规则。分析结果不等于剪辑决定：算法只提供逐帧变化和候选边界，语义镜头需要结合 contact sheet、代表帧、画面内容和声音判断。

这是可选的复核/更新流程。当前 skill 已经包含一份由用户参考视频提炼出的 `source-analysis` 和 `style-profile`；日常创作无需运行分析器。

运行：

```bash
python3 scripts/analyze_reference.py INPUT.mp4 \
  --out OUTPUT_DIR \
  --overview-fps 2 \
  --merge-frames 3
```

分析器只读取源文件，输出到指定目录，不保存绝对源路径，也不复制源视频。

## 证据等级

| 等级 | 含义 | 允许的表述 |
|---|---|---|
| `measured` | 来自 ffprobe、逐帧计算或音频工具的结果 | “24 fps”“第 314 帧差异峰值” |
| `observed` | 从代表帧或 contact sheet 直接看到的画面事实 | “手部从画面下缘进入”“背景呈冷灰绿色” |
| `inferred` | 根据多个观察归纳的可复用创作规则 | “用圆形作为图形桥接” |
| `uncertain` | 低分辨率、微小文字或遮挡导致无法确认 | “标签文字无法可靠识别” |

不要把 `inferred` 写成源片的测量事实，也不要把 `uncertain` 补写成猜测。

## 分析产物

### `metadata.json`

包含媒体规格、分析参数、帧差异摘要、候选边界数量和派生图像文件名。`video.duration_seconds` 使用容器时长；`video.stream_duration_seconds` 保留视频流时长；需要剪辑对齐时同时查看二者。

### `frames.ndjson`

每行记录一个解码帧：

```json
{
  "frame_index": 314,
  "time_seconds": 13.083333,
  "mean_rgb": [0.72, 0.76, 0.71],
  "mean_luma": 0.75,
  "frame_delta": 0.636717,
  "transition_candidate": true
}
```

`frame_delta` 是低分辨率 RGB 代理与上一帧的平均归一化差异。它能发现突变和强运动，不能单独证明硬切。

### `shots.json`

`boundary_frames` 是候选边界；`candidate_groups` 是合并前的局部峰值组；`segments` 使用半开区间 `[start_frame, end_frame)`，字段如下：

```json
{
  "start_frame": 314,
  "end_frame": 331,
  "start_seconds": 13.083333,
  "end_seconds": 13.791667,
  "duration_seconds": 0.708334,
  "representative_frame": 318,
  "evidence": "candidate"
}
```

`evidence: candidate` 表示段落起点来自算法候选边界；`evidence: sequence` 表示从视频开始或上一候选边界延续而来。最终报告应为这些段落补充语义标签。

### `contact-sheet.jpg` 与 `waveform.jpg`

contact sheet 用于快速判断阶段密度、构图重复和形状连续性；waveform 用于判断持续底噪、瞬态、静音和声音密度。contact sheet 的单元格时间顺序写入 `metadata.json`，不依赖 drawtext 字体插件。

## 镜头归并规则

1. 先保留原始帧率记录，不以 0.5 秒采样替代逐帧证据。
2. 使用默认自适应 `p95` 阈值并设 `0.12` 下限；需要复核时记录显式阈值。
3. 将相邻 `merge_frames` 帧内的局部峰值归为一组，默认 `3` 帧。
4. 选取组内差异最大的帧作为候选代表边界；不要自动命名为“硬切”。
5. 查看代表帧前后至少一个短窗口，区分硬切、物体运动、快速材质变化、淡入淡出和图形生成。
6. 将连续的同一视觉命题归并成语义镜头；将镜头内部的物件状态变化记录为 micro-beat。
7. 在最终分镜中同时保留镜头级时间码与关键帧范围，便于复核和再创作。

## 报告模板

### 参考视频审计

- **输入规格（`measured`）**：
- **分析参数（`measured`）**：
- **候选变化数量（`measured`）**：
- **主要视觉阶段（`observed`）**：
- **声音阶段（`observed`）**：
- **视觉 DNA（`inferred`）**：
- **源片专属元素（`observed`/`uncertain`）**：
- **原创风险边界**：

### 镜头卡

| 字段 | 内容 |
|---|---|
| 帧范围/时间码 |  |
| 阶段 |  |
| 景别、机位、镜头运动 |  |
| 单一视觉命题 |  |
| 材质与道具功能 |  |
| 动作和物件状态 |  |
| 图形/动作连接 |  |
| 光线、色彩、对比 |  |
| 声音触发点 |  |
| 证据等级与置信度 |  |
| 可复用规则 |  |
| 不得复制的源片细节 |  |
