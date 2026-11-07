"""Cài đặt thuật toán LOOK."""

from __future__ import annotations

from typing import Sequence

from .common import (
    Direction,
    SimulationResult,
    create_result,
    validate_input,
)


def simulate_look(
    requests: Sequence[int], head: int, direction: Direction = "up"
) -> SimulationResult:
    """Phục vụ theo hướng đã chọn, rồi đổi chiều tại yêu cầu cuối của phía đó."""
    direction = validate_input(requests, head, direction)
    left = sorted((track for track in requests if track < head), reverse=True)
    right = sorted(track for track in requests if track > head)
    at_head = [track for track in requests if track == head]

    schedule: list[tuple[int, str]] = [(track, "Phục vụ") for track in at_head]
    if direction == "up":
        schedule.extend((track, "Phục vụ") for track in right)
        if left:
            schedule.append((left[0], "Đổi hướng, phục vụ"))
            schedule.extend((track, "Phục vụ") for track in left[1:])
    else:
        schedule.extend((track, "Phục vụ") for track in left)
        if right:
            schedule.append((right[-1], "Đổi hướng, phục vụ"))
            schedule.extend((track, "Phục vụ") for track in reversed(right[:-1]))

    return create_result("LOOK", requests, head, direction, schedule)


__all__ = ["simulate_look"]
