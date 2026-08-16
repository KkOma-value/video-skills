# Prompt Recipes: Faceted Noir Lyric Film

Replace every bracketed token with user material. Generate a master still and character/motif sheets first; use them as image references for later generations whenever the tool supports it.

## Global image-style clause

Append this clause to every still-generation prompt:

```text
editorial 2D illustration, faceted low-poly paper collage, angular cut-paper planes, charcoal and slate world, oxblood red tension planes, restrained deep teal, one luminous jade focal accent, cream light planes, sparse ink hairline contours, subtle printed-paper grain, graphic negative space, cinematic 16:9 composition, sharp silhouettes, high contrast, designed poster composition, not photorealistic, not glossy 3D
```

## Global negative clause

Append this negative constraint where supported:

```text
photorealistic skin, glossy 3D render, plastic CGI, soft bokeh, saturated rainbow palette, generic cyberpunk neon, volumetric fog, cluttered background, illegible text, watermark, duplicate limbs, inconsistent costume, automatic morphing, excessive particles, direct copy of a copyrighted character or logo
```

## Still and motion prompt pairs

### 1. Threshold — 0.0–2.1 s

**Still**

```text
[PROTAGONIST] appears as a small dark silhouette inside a towering [ARCHITECTURAL OR NATURAL THRESHOLD], a small [RED COUNTERPOINT] near the floor, [RECURRING MOTIF] barely visible at the edge, overwhelming dark slate shapes and a diagonal oxblood foreground plane, leave lower-center clear for lyric subtitles; [GLOBAL IMAGE-STYLE CLAUSE]
```

**Motion**

```text
Slow 2.5D dolly backward and slight slide left. Reveal the larger world and a distant [COUNTERFORCE] behind the protagonist. Keep the figure nearly still; move only a hanging line or the red counterpoint subtly. No shake, no morph.
```

### 2. Intimacy — 2.1–5.8 s

**Still**

```text
Tight side profile of [PROTAGONIST], face built from cream and slate geometric planes, black ink-like hair or contour lines, [RECURRING MOTIF] suspended beside the eye/hand/heart as the only jade illumination, red wedge behind the profile, very large negative black area; [GLOBAL IMAGE-STYLE CLAUSE]
```

**Motion**

```text
Slow 1.06x push toward the face. Let only the jade motif sway or pulse once. Maintain exact facial silhouette and costume; no lip-sync or facial redesign.
```

### 3. Ritual — 5.8–8.3 s

**Still**

```text
[RECURRING MOTIF] floats over a centered [VESSEL / PORTAL / INTERFACE / EYE-LIKE DEVICE] formed from rings and angular planes, dark teal and oxblood background, one pale cream circular boundary, lower-center negative space; [GLOBAL IMAGE-STYLE CLAUSE]
```

**Motion**

```text
Hold the centered composition, then let the motif descend once and transform into [USER-OWNED FLOWER / SHARD / MAP / SIGNAL]. One short jade flare only; cut immediately after the transformation.
```

### 4. Relationship tableau — 8.3–10.1 s

**Still**

```text
[PROTAGONIST] and [OTHER FIGURE OR COUNTERFORCE] stand apart in a field/room made of hundreds of simplified [RED REPEATED FORMS], huge black vertical [TREE / TOWER / MACHINE] separates them, muted cream horizon, the recurring motif is tiny but present; [GLOBAL IMAGE-STYLE CLAUSE]
```

**Motion**

```text
Use a restrained lateral drift. Let a few red forms sway and the motif blink once. Do not animate dialogue or walk cycles.
```

### 5. Flight/metaphor — 10.1–16.2 s

**Still**

```text
A user-owned symbolic [CREATURE / VEHICLE / OBJECT] made from white, red, and deep teal angular planes crosses a black background of radial wedges, graphic low-poly wings or shards, a small jade trace connects it to [RECURRING MOTIF]; [GLOBAL IMAGE-STYLE CLAUSE]
```

**Motion**

```text
Make the form glide on one diagonal vector for 2–3 seconds. On a music hit, let one section split into shards that resolve into the next landscape. Keep camera motion simple and directionally consistent.
```

### 6. Labyrinth — 16.2–19.3 s

**Still**

```text
[PROTAGONIST] is tiny within a near-monochrome impossible [STAIR / CITY / CIRCUIT / CANYON], looping slate architecture, a distant cream opening, only two or three red marks, jade absent or nearly absent; [GLOBAL IMAGE-STYLE CLAUSE]
```

**Motion**

```text
Slow forward push into looping geometry. Preserve the architectural layout; show no more than one small figure gesture.
```

### 7. Rupture — 19.3–23.8 s

**Still**

```text
Dark faceted panels compress around a hairline jade fissure shaped like [RECURRING MOTIF], heavy black negative space, a hidden oxblood underlayer, no characters at first; [GLOBAL IMAGE-STYLE CLAUSE]
```

**Motion**

```text
Let the jade line travel once, then release one 4–8 frame angular flash. Hard cut to [PROTAGONIST] and [OTHER FIGURE] in a cream/red/black graphic confrontation or embrace. Do not use smoke, continuous explosions, or strobing.
```

### 8. Release and end card — 23.8–30.0 s

**Still**

```text
Warm cream field with [PROTAGONIST] and [OTHER FIGURE] simplified into an almost-iconic composition; a translucent white low-poly [RELEASE SYMBOL] rises behind them; one tiny [RED COUNTERPOINT] remains; dark geometric frame edges and a clean central title area; [GLOBAL IMAGE-STYLE CLAUSE]
```

**Motion**

```text
Reveal the release symbol gently, then reduce motion to nearly zero. From 26.2 seconds, fade/wipe the custom title [TITLE] behind or around the symbol. Hold the final composition for at least 2.5 seconds.
```

## Prompting sequence

1. Generate the master style frame and approve palette/facet scale.
2. Generate the protagonist, other figure, motif, and release symbol as isolated sheets against simple backgrounds.
3. Generate one still per time-coded beat with the approved sheets as references.
4. Correct stills before motion generation. Reuse stills as first/last frames where supported.
5. Generate short 1.5–3.5 second motion clips only, then composite them according to the storyboard.
