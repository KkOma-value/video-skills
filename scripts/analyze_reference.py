#!/usr/bin/env python3
"""Read-only frame and audio analysis for Field Archive Film references.

The script intentionally produces evidence, not a final editorial decision. It
decodes a small RGB proxy for every source frame, records adjacent-frame
differences, groups local maxima into candidate boundaries, and creates a
contact sheet and waveform with ffmpeg. No source video is copied or modified.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


SCHEMA_VERSION = "1.0"
PROXY_WIDTH = 96
PROXY_HEIGHT = 54
DEFAULT_OVERVIEW_FPS = 2.0
DEFAULT_MERGE_FRAMES = 3
MIN_ADAPTIVE_THRESHOLD = 0.12


def run_command(command: Sequence[str], *, text: bool = False) -> subprocess.CompletedProcess[str | bytes]:
    """Run a required local command and return its completed result."""

    try:
        return subprocess.run(
            list(command),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=text,
        )
    except FileNotFoundError as exc:
        executable = command[0] if command else "required command"
        raise RuntimeError(f"Required command is unavailable: {executable}") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else exc.stderr
        detail = stderr.strip() or "no stderr output"
        raise RuntimeError(f"Command failed ({exc.returncode}): {' '.join(command)}\n{detail}") from exc


def parse_fraction(value: str | None) -> float | None:
    if not value or value in {"0/0", "N/A"}:
        return None
    try:
        parsed = Fraction(value)
    except (ValueError, ZeroDivisionError):
        return None
    return float(parsed)


def as_float(value: Any, default: float | None = None) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int | None = None) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def probe_media(input_path: Path) -> dict[str, Any]:
    result = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(input_path),
        ],
        text=True,
    )
    payload = json.loads(result.stdout)
    streams = payload.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    if not video:
        raise RuntimeError("Input does not contain a video stream")
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)

    fps = parse_fraction(video.get("avg_frame_rate")) or parse_fraction(video.get("r_frame_rate"))
    frame_count = as_int(video.get("nb_frames"))
    stream_duration = as_float(video.get("duration"))
    container_duration = as_float(payload.get("format", {}).get("duration"))
    duration = container_duration or stream_duration
    if not fps or fps <= 0:
        raise RuntimeError("Unable to determine the video frame rate")
    if not duration or duration <= 0:
        raise RuntimeError("Unable to determine the video duration")

    return {
        "format_name": payload.get("format", {}).get("format_name"),
        "video": {
            "codec": video.get("codec_name"),
            "width": as_int(video.get("width")),
            "height": as_int(video.get("height")),
            "fps": fps,
            "frame_count_probe": frame_count,
            "duration_seconds": duration,
            "stream_duration_seconds": stream_duration,
            "container_duration_seconds": container_duration,
            "pixel_format": video.get("pix_fmt"),
        },
        "audio": (
            {
                "codec": audio.get("codec_name"),
                "sample_rate": as_int(audio.get("sample_rate")),
                "channels": as_int(audio.get("channels")),
                "channel_layout": audio.get("channel_layout"),
                "duration_seconds": as_float(audio.get("duration")),
            }
            if audio
            else None
        ),
    }


def probe_frame_times(input_path: Path, fps: float, expected_count: int | None) -> list[float]:
    """Read best-effort frame PTS values, with a CFR fallback."""

    result = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_frames",
            "-show_entries",
            "frame=best_effort_timestamp_time",
            "-of",
            "csv=p=0",
            str(input_path),
        ],
        text=True,
    )
    times: list[float] = []
    for line in result.stdout.splitlines():
        value = line.strip().split(",", 1)[0]
        parsed = as_float(value)
        if parsed is not None:
            times.append(parsed)
    if expected_count and len(times) != expected_count:
        times = []
    if not times:
        count = expected_count or max(1, math.ceil(fps * 1.0))
        times = [index / fps for index in range(count)]
    return times


def iter_proxy_frames(input_path: Path, width: int = PROXY_WIDTH, height: int = PROXY_HEIGHT) -> Iterable[bytes]:
    """Yield RGB proxy frames decoded by ffmpeg."""

    frame_bytes = width * height * 3
    process = subprocess.Popen(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(input_path),
            "-vf",
            f"scale={width}:{height}:flags=area,format=rgb24",
            "-an",
            "-fps_mode",
            "passthrough",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdout is not None
    try:
        while True:
            buffer = process.stdout.read(frame_bytes)
            if len(buffer) < frame_bytes:
                break
            yield buffer
    finally:
        process.stdout.close()
        stderr = process.stderr.read().decode(errors="replace") if process.stderr else ""
        return_code = process.wait()
        if return_code != 0:
            raise RuntimeError(f"ffmpeg proxy decode failed ({return_code}): {stderr.strip()}")


def frame_mean_rgb(buffer: bytes) -> tuple[float, float, float]:
    red = green = blue = 0
    pixel_count = len(buffer) // 3
    for index in range(0, len(buffer), 3):
        red += buffer[index]
        green += buffer[index + 1]
        blue += buffer[index + 2]
    return tuple(round(channel / pixel_count / 255.0, 6) for channel in (red, green, blue))


def frame_luma(mean_rgb: Sequence[float]) -> float:
    return round(0.2126 * mean_rgb[0] + 0.7152 * mean_rgb[1] + 0.0722 * mean_rgb[2], 6)


def frame_delta(previous: bytes | None, current: bytes) -> float:
    if previous is None:
        return 0.0
    difference = sum(abs(left - right) for left, right in zip(previous, current))
    return round(difference / len(current) / 255.0, 6)


def frame_statistics(frames: Sequence[bytes], times: Sequence[float]) -> list[dict[str, Any]]:
    stats: list[dict[str, Any]] = []
    previous: bytes | None = None
    for index, current in enumerate(frames):
        mean_rgb = frame_mean_rgb(current)
        timestamp = times[index] if index < len(times) else (times[-1] if times else float(index))
        stats.append(
            {
                "frame_index": index,
                "time_seconds": round(timestamp, 6),
                "mean_rgb": list(mean_rgb),
                "mean_luma": frame_luma(mean_rgb),
                "frame_delta": frame_delta(previous, current),
            }
        )
        previous = current
    return stats


def percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def summarize_deltas(stats: Sequence[dict[str, Any]]) -> dict[str, float]:
    values = [float(item["frame_delta"]) for item in stats[1:]]
    return {
        "median": round(percentile(values, 0.50), 6),
        "p90": round(percentile(values, 0.90), 6),
        "p95": round(percentile(values, 0.95), 6),
        "p99": round(percentile(values, 0.99), 6),
    }


def group_candidate_frames(candidates: Sequence[int], merge_frames: int) -> list[list[int]]:
    groups: list[list[int]] = []
    for candidate in sorted(set(candidates)):
        if not groups or candidate - groups[-1][-1] > merge_frames:
            groups.append([candidate])
        else:
            groups[-1].append(candidate)
    return groups


def detect_candidates(
    stats: Sequence[dict[str, Any]],
    *,
    threshold: float | None = None,
    merge_frames: int = DEFAULT_MERGE_FRAMES,
) -> tuple[list[int], float, list[list[int]]]:
    if len(stats) < 3:
        return [], threshold or MIN_ADAPTIVE_THRESHOLD, []
    summary = summarize_deltas(stats)
    actual_threshold = max(MIN_ADAPTIVE_THRESHOLD, summary["p95"]) if threshold is None else threshold
    raw_candidates: list[int] = []
    for index in range(1, len(stats) - 1):
        current = float(stats[index]["frame_delta"])
        previous = float(stats[index - 1]["frame_delta"])
        following = float(stats[index + 1]["frame_delta"])
        if current >= actual_threshold and current >= previous and current >= following:
            raw_candidates.append(index)
    groups = group_candidate_frames(raw_candidates, max(0, merge_frames))
    peaks = [max(group, key=lambda item: float(stats[item]["frame_delta"])) for group in groups]
    return peaks, round(actual_threshold, 6), groups


def representative_frame(start: int, end: int, stats: Sequence[dict[str, Any]]) -> int:
    if end <= start:
        return start
    middle = range(start, min(end, len(stats)))
    return min(middle, key=lambda index: float(stats[index]["frame_delta"]))


def build_segments(
    stats: Sequence[dict[str, Any]],
    boundary_frames: Sequence[int],
    duration_seconds: float,
) -> list[dict[str, Any]]:
    if not stats:
        return []
    frame_count = len(stats)
    boundaries = [0] + sorted({frame for frame in boundary_frames if 0 < frame < frame_count}) + [frame_count]
    segments: list[dict[str, Any]] = []
    for start, end in zip(boundaries, boundaries[1:]):
        start_seconds = float(stats[start]["time_seconds"])
        end_seconds = float(stats[end]["time_seconds"]) if end < frame_count else duration_seconds
        segments.append(
            {
                "start_frame": start,
                "end_frame": end,
                "start_seconds": round(start_seconds, 6),
                "end_seconds": round(end_seconds, 6),
                "duration_seconds": round(max(0.0, end_seconds - start_seconds), 6),
                "representative_frame": representative_frame(start, end, stats),
                "evidence": "candidate" if start in boundary_frames else "sequence",
            }
        )
    return segments


def run_ffmpeg_artifact(command: Sequence[str], output_path: Path) -> bool:
    try:
        run_command(list(command), text=False)
    except RuntimeError:
        return False
    return output_path.exists() and output_path.stat().st_size > 0


def create_contact_sheet(input_path: Path, output_path: Path, duration: float, overview_fps: float) -> dict[str, Any]:
    columns = 6
    sample_count = max(1, math.ceil(duration * overview_fps))
    rows = max(1, math.ceil(sample_count / columns))
    filter_graph = (
        f"fps={overview_fps:g},scale=480:-2:flags=lanczos,"
        f"tile={columns}x{rows}:padding=4:margin=8"
    )
    created = run_ffmpeg_artifact(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(input_path),
            "-vf",
            filter_graph,
            "-frames:v",
            "1",
            str(output_path),
        ],
        output_path,
    )
    return {
        "path": output_path.name if created else None,
        "columns": columns,
        "rows": rows,
        "sample_fps": overview_fps,
        "sample_times_seconds": [round(index / overview_fps, 6) for index in range(sample_count)],
    }


def create_waveform(input_path: Path, output_path: Path, has_audio: bool) -> dict[str, Any]:
    if not has_audio:
        return {"path": None, "available": False, "reason": "no audio stream"}
    created = run_ffmpeg_artifact(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(input_path),
            "-filter_complex",
            "[0:a]showwavespic=s=1600x260:colors=0x6b766f:split_channels=0",
            "-frames:v",
            "1",
            str(output_path),
        ],
        output_path,
    )
    return {
        "path": output_path.name if created else None,
        "available": created,
        "reason": None if created else "ffmpeg could not render waveform",
    }


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_ndjson(path: Path, records: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def analyze_reference(
    input_path: Path,
    output_dir: Path,
    *,
    overview_fps: float = DEFAULT_OVERVIEW_FPS,
    merge_frames: int = DEFAULT_MERGE_FRAMES,
    cut_threshold: float | None = None,
) -> dict[str, Any]:
    if not input_path.is_file():
        raise RuntimeError(f"Input file does not exist: {input_path}")
    if overview_fps <= 0:
        raise RuntimeError("--overview-fps must be greater than zero")
    if merge_frames < 0:
        raise RuntimeError("--merge-frames must be zero or greater")
    if cut_threshold is not None and not 0 < cut_threshold <= 1:
        raise RuntimeError("--cut-threshold must be between 0 and 1")
    if not shutil.which("ffprobe") or not shutil.which("ffmpeg"):
        missing = [name for name in ("ffprobe", "ffmpeg") if not shutil.which(name)]
        raise RuntimeError(f"Missing required command(s): {', '.join(missing)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    probe = probe_media(input_path)
    video = probe["video"]
    duration = float(video["duration_seconds"])
    fps = float(video["fps"])
    times = probe_frame_times(input_path, fps, video.get("frame_count_probe"))
    frames = list(iter_proxy_frames(input_path))
    if not frames:
        raise RuntimeError("No video frames could be decoded")
    if len(times) != len(frames):
        times = [index / fps for index in range(len(frames))]
    stats = frame_statistics(frames, times)
    candidates, threshold, groups = detect_candidates(
        stats,
        threshold=cut_threshold,
        merge_frames=merge_frames,
    )
    segments = build_segments(stats, candidates, duration)
    delta_summary = summarize_deltas(stats)

    contact_sheet = create_contact_sheet(
        input_path,
        output_dir / "contact-sheet.jpg",
        duration,
        overview_fps,
    )
    waveform = create_waveform(
        input_path,
        output_dir / "waveform.jpg",
        probe["audio"] is not None,
    )

    for item in stats:
        item["transition_candidate"] = item["frame_index"] in candidates
    write_ndjson(output_dir / "frames.ndjson", stats)
    write_json(
        output_dir / "shots.json",
        {
            "schema_version": SCHEMA_VERSION,
            "boundary_frames": candidates,
            "candidate_groups": groups,
            "segments": segments,
            "semantics": "Candidate segments require visual review; frame deltas do not distinguish hard cuts from intentional in-shot motion.",
        },
    )
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "source": {"name": input_path.name},
        "format_name": probe.get("format_name"),
        "video": {
            **video,
            "frame_count": len(frames),
            "duration_seconds": duration,
        },
        "audio": probe["audio"],
        "analysis": {
            "proxy_size": [PROXY_WIDTH, PROXY_HEIGHT],
            "frames_read": len(frames),
            "native_frame_rate": fps,
            "overview_fps": overview_fps,
            "merge_frames": merge_frames,
            "cut_threshold": threshold,
            "threshold_mode": "explicit" if cut_threshold is not None else "adaptive_p95_with_minimum",
            "delta_summary": delta_summary,
            "candidate_boundary_count": len(candidates),
            "candidate_segment_count": len(segments),
        },
        "artifacts": {"contact_sheet": contact_sheet, "waveform": waveform},
        "privacy": {"absolute_source_path_stored": False, "source_video_copied": False},
    }
    write_json(output_dir / "metadata.json", metadata)
    return metadata


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create evidence artifacts for a local reference video without modifying the source."
    )
    parser.add_argument("input", type=Path, help="Local reference video")
    parser.add_argument("--out", required=True, type=Path, help="Output directory for analysis artifacts")
    parser.add_argument(
        "--overview-fps",
        type=float,
        default=DEFAULT_OVERVIEW_FPS,
        help=f"Contact-sheet sampling rate (default: {DEFAULT_OVERVIEW_FPS:g})",
    )
    parser.add_argument(
        "--merge-frames",
        type=int,
        default=DEFAULT_MERGE_FRAMES,
        help=f"Merge candidate peaks within this many frames (default: {DEFAULT_MERGE_FRAMES})",
    )
    parser.add_argument(
        "--cut-threshold",
        type=float,
        default=None,
        help="Optional explicit normalized frame-delta threshold; default uses adaptive p95 with a 0.12 floor",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        metadata = analyze_reference(
            args.input,
            args.out,
            overview_fps=args.overview_fps,
            merge_frames=args.merge_frames,
            cut_threshold=args.cut_threshold,
        )
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"analyze_reference: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
