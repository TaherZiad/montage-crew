#!/usr/bin/env python3
"""Dependency-light adaptive caption segmentation for word-timed Chinese speech."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field


PUNCTUATION = "，。！？；、,.!?;"
DEFAULT_CONNECTORS = (
    "也就是说", "总的来说", "但是", "所以", "因为", "而且", "然后", "包括",
    "以及", "如果", "就是", "至于", "其实", "反正", "不过", "首先", "加上", "并且",
)


@dataclass(frozen=True)
class CaptionConfig:
    target_min_chars: int = 8
    target_max_chars: int = 15
    soft_max_chars: int = 16
    hard_max_chars: int = 18
    max_duration_seconds: float = 3.2
    min_chars_preferred: int = 4
    min_duration_seconds_preferred: float = 0.55
    strong_pause_ms: int = 280
    weak_pause_ms: int = 160
    display_punctuation: bool = False
    protected_phrases: tuple[str, ...] = field(default_factory=tuple)
    connectors: tuple[str, ...] = DEFAULT_CONNECTORS

    @classmethod
    def from_manifest(cls, payload: dict | None) -> "CaptionConfig":
        data = payload or {}
        target = data.get("target_chars", [8, 15])
        return cls(
            target_min_chars=int(target[0]),
            target_max_chars=int(target[1]),
            soft_max_chars=int(data.get("soft_max_chars", 16)),
            hard_max_chars=int(data.get("hard_max_chars", 18)),
            max_duration_seconds=float(data.get("max_duration_seconds", 3.2)),
            min_chars_preferred=int(data.get("min_chars_preferred", 4)),
            min_duration_seconds_preferred=float(data.get("min_duration_seconds_preferred", 0.55)),
            strong_pause_ms=int(data.get("strong_pause_ms", 280)),
            weak_pause_ms=int(data.get("weak_pause_ms", 160)),
            display_punctuation=bool(data.get("display_punctuation", False)),
            protected_phrases=tuple(str(item) for item in data.get("protected_phrases", [])),
            connectors=tuple(str(item) for item in data.get("connectors", DEFAULT_CONNECTORS)),
        )


def clean_text(value: object) -> str:
    return re.sub(rf"[{re.escape(PUNCTUATION)}\s]", "", str(value))


def display_length(words: list[dict]) -> int:
    return len("".join(clean_text(word.get("text", "")) for word in words))


def protected_boundary_indices(words: list[dict], phrases: tuple[str, ...]) -> set[int]:
    """Return token boundaries that do not cut through an approved protected phrase."""
    token_texts = [clean_text(word.get("text", "")) for word in words]
    full_text = "".join(token_texts)
    cumulative = []
    cursor = 0
    for token in token_texts:
        cursor += len(token)
        cumulative.append(cursor)
    forbidden_character_boundaries: set[int] = set()
    for phrase in phrases:
        phrase = clean_text(phrase)
        if len(phrase) < 2:
            continue
        offset = 0
        while True:
            start = full_text.find(phrase, offset)
            if start < 0:
                break
            forbidden_character_boundaries.update(range(start + 1, start + len(phrase)))
            offset = start + 1
    return {
        index
        for index, character_offset in enumerate(cumulative, start=1)
        if character_offset not in forbidden_character_boundaries
    }


def adaptive_groups(words: list[dict], config: CaptionConfig) -> list[list[dict]]:
    """Choose a globally coherent caption partition using dynamic programming."""
    if not words:
        return []
    allowed_boundaries = protected_boundary_indices(words, config.protected_phrases)
    allowed_boundaries.add(len(words))
    count = len(words)
    costs = [math.inf] * (count + 1)
    previous: list[int | None] = [None] * (count + 1)
    costs[0] = 0.0

    for start in range(count):
        if math.isinf(costs[start]):
            continue
        for end in range(start + 1, count + 1):
            if end < count and end not in allowed_boundaries:
                continue
            group = words[start:end]
            chars = display_length(group)
            duration = float(group[-1]["end"]) - float(group[0]["start"])
            if end > start + 1 and (
                chars > config.hard_max_chars or duration > config.max_duration_seconds
            ):
                break

            score = 0.9
            if chars < config.min_chars_preferred:
                score += 7.0
            elif chars < config.target_min_chars:
                score += (config.target_min_chars - chars) * 0.55
            elif chars <= config.target_max_chars:
                pass
            elif chars <= config.soft_max_chars:
                score += 0.8
            else:
                score += (chars - config.soft_max_chars) * 3.0
            if duration < config.min_duration_seconds_preferred:
                score += (config.min_duration_seconds_preferred - duration) * 5.0
            elif duration > min(2.8, config.max_duration_seconds):
                score += (duration - min(2.8, config.max_duration_seconds)) * 4.0

            if end < count:
                current_text = "".join(str(word.get("text", "")) for word in group)
                next_text = "".join(
                    str(word.get("text", "")) for word in words[end:min(count, end + 6)]
                )
                mark = str(words[end - 1].get("_punctuation", ""))
                gap = max(0.0, float(words[end - 1].get("_source_gap_after", 0.0)))
                reward = 0.0
                if mark in "。！？；.!?;":
                    reward += 4.5
                elif mark in "，、,":
                    reward += 3.0
                if gap * 1000 >= config.strong_pause_ms:
                    reward += 4.0
                elif gap * 1000 >= config.weak_pause_ms:
                    reward += 2.5
                elif gap >= 0.10:
                    reward += 0.8
                if any(next_text.startswith(connector) for connector in config.connectors):
                    reward += 2.2
                if str(words[end - 1].get("text", "")) in "了吧吗呢啊呀嘛哦行对":
                    reward += 0.8
                if str(words[end].get("text", "")) in ("的", "得", "地"):
                    score += 9.0
                if str(words[end - 1].get("text", "")) in ("在", "把", "被", "和", "跟", "与", "及", "或"):
                    score += 8.0
                if str(words[end - 1].get("text", "")) == "的":
                    score += 4.0
                if any(current_text.endswith(connector) for connector in config.connectors):
                    score += 8.0
                if reward == 0.0:
                    score += 1.4
                score -= reward
                if 0 < display_length(words[end:]) < config.min_chars_preferred:
                    score += 7.0

            candidate = costs[start] + score
            if candidate < costs[end]:
                costs[end] = candidate
                previous[end] = start

    if previous[count] is None:
        raise ValueError("no valid adaptive subtitle partition; relax hard limits")
    groups = []
    cursor = count
    while cursor:
        start = previous[cursor]
        if start is None:
            raise ValueError("broken adaptive subtitle path")
        groups.append(words[start:cursor])
        cursor = start
    return list(reversed(groups))


def cue_text(words: list[dict], display_punctuation: bool = False) -> str:
    text = "".join(str(word.get("text", "")) for word in words).strip()
    return text if display_punctuation else clean_text(text)


def cue_metrics(cues: list[tuple[str, float, float]], config: CaptionConfig) -> dict:
    lengths = [len(clean_text(text)) for text, _, _ in cues]
    durations = [end - start for _, start, end in cues]
    return {
        "count": len(cues),
        "over_soft_max_chars": sum(value > config.soft_max_chars for value in lengths),
        "over_hard_max_chars": sum(value > config.hard_max_chars for value in lengths),
        "over_max_duration": sum(value > config.max_duration_seconds for value in durations),
        "under_min_chars_preferred": sum(value < config.min_chars_preferred for value in lengths),
        "under_min_duration_preferred": sum(
            value < config.min_duration_seconds_preferred for value in durations
        ),
        "starts_with_particle": sum(text.startswith(("的", "得", "地")) for text, _, _ in cues),
        "max_chars": max(lengths, default=0),
        "max_duration_seconds": round(max(durations, default=0.0), 3),
    }
