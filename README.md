# Field Archive Film Skill

这个 skill 已经把用户提供的参考视频总结成一套可复用的档案实验片风格，直接用于生成原创分镜、AI 视频提示词与声音设计。

## 使用

日常创作不需要再次提供原视频，直接使用：

```text
使用 $field-archive-film，为我的主题设计一支原创概念片。
```

只有在需要复核或替换参考视频时，才运行：

```bash
python3 scripts/analyze_reference.py /path/to/reference.mp4 \
  --out /tmp/field-archive-analysis
```

随后让 Codex 读取分析目录并更新 profile。原始视频只作为输入，不放入 skill 包；核心风格总结位于 `references/source-analysis.md` 和 `references/style-profile.*`，详细创作规则位于 `SKILL.md`。
