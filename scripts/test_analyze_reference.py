#!/usr/bin/env python3
"""Small standard-library tests for the reference analyzer's deterministic core."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import analyze_reference  # noqa: E402


def solid(value: int, size: int = 96 * 54 * 3) -> bytes:
    return bytes([value]) * size


class AnalyzerCoreTests(unittest.TestCase):
    def test_static_frames_have_no_candidates(self) -> None:
        frames = [solid(80), solid(80), solid(80), solid(80)]
        stats = analyze_reference.frame_statistics(frames, [0.0, 1 / 24, 2 / 24, 3 / 24])
        candidates, threshold, groups = analyze_reference.detect_candidates(stats, threshold=0.12, merge_frames=3)
        self.assertEqual(candidates, [])
        self.assertEqual(groups, [])
        self.assertEqual(threshold, 0.12)
        self.assertTrue(all(item["frame_delta"] == 0 for item in stats))

    def test_single_step_change_has_one_candidate(self) -> None:
        frames = [solid(0), solid(0), solid(255), solid(255), solid(255)]
        stats = analyze_reference.frame_statistics(frames, [index / 24 for index in range(len(frames))])
        candidates, _, groups = analyze_reference.detect_candidates(stats, threshold=0.12, merge_frames=3)
        self.assertEqual(candidates, [2])
        self.assertEqual(groups, [[2]])
        self.assertTrue(stats[2]["frame_delta"] > 0.9)

    def test_gradual_motion_does_not_explode_into_candidates(self) -> None:
        frames = [solid(value) for value in (0, 8, 16, 24, 32, 40, 48, 56)]
        stats = analyze_reference.frame_statistics(frames, [index / 24 for index in range(len(frames))])
        candidates, _, _ = analyze_reference.detect_candidates(stats, threshold=0.12, merge_frames=3)
        self.assertEqual(candidates, [])

    def test_candidate_groups_and_segments_have_no_gaps(self) -> None:
        groups = analyze_reference.group_candidate_frames([2, 3, 4, 10], merge_frames=3)
        self.assertEqual(groups, [[2, 3, 4], [10]])
        frames = [solid(40) for _ in range(12)]
        stats = analyze_reference.frame_statistics(frames, [index / 24 for index in range(len(frames))])
        segments = analyze_reference.build_segments(stats, [2, 10], 0.5)
        self.assertEqual([(item["start_frame"], item["end_frame"]) for item in segments], [(0, 2), (2, 10), (10, 12)])
        self.assertEqual(segments[0]["start_seconds"], 0.0)
        self.assertEqual(segments[-1]["end_seconds"], 0.5)
        self.assertEqual(json.loads(json.dumps(segments)), segments)


if __name__ == "__main__":
    unittest.main()
