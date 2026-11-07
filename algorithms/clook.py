"""Cài đặt thuật toán C-LOOK."""

from __future__ import annotations

from typing import Sequence

from .common import (
    Direction,
    SimulationResult,
    TRACK_MAX,
    create_result,
    validate_input,
)


def simulate_clook(
    requests: Sequence[int],
    head: int,
    direction: Direction = "up",
    track_max: int = TRACK_MAX,
) -> SimulationResult:
    """Phục vụ một chiều; quay vòng đến đầu kia rồi tiếp tục cùng chiều."""
    direction = validate_input(requests, head, direction, track_max)
    left = sorted(track for track in requests if track < head)
    right = sorted(track for track in requests if track > head)
    at_head = [track for track in requests if track == head]

    schedule: list[tuple[int, str]] = [(track, "Phục vụ") for track in at_head]
    if direction == "up":
        schedule.extend((track, "Phục vụ") for track in right)
        if left:
            schedule.append((left[0], "Quay vòng, tiếp tục phải"))
            schedule.extend((track, "Phục vụ") for track in left[1:])
    else:
        schedule.extend((track, "Phục vụ") for track in reversed(left))
        if right:
            schedule.append((right[-1], "Quay vòng, tiếp tục trái"))
            schedule.extend((track, "Phục vụ") for track in reversed(right[:-1]))

    return create_result("C-LOOK", requests, head, direction, schedule)


__all__ = ["simulate_clook"]
