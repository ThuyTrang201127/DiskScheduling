"""Cài đặt thuật toán LOOK."""

from __future__ import annotations

from typing import Sequence

from .common import (
    Direction,
    SimulationResult,
    TRACK_MAX,
    create_result,
    validate_input,
)


def look_algorithm(
    requests: Sequence[int],
    head: int,
    direction: Direction = "up",
    track_max: int = TRACK_MAX,
) -> SimulationResult:
    """Phục vụ theo hướng đã chọn, rồi đổi chiều tại yêu cầu cuối của phía đó."""
    direction = validate_input(requests, head, direction, track_max)
    sorted_requests = sorted(requests)
    left_requests = [track for track in sorted_requests if track < head]
    right_requests = [track for track in sorted_requests if track > head]
    requests_at_head = [track for track in sorted_requests if track == head]

    if direction == "up":
        sequence = requests_at_head + right_requests + left_requests[::-1]
        turnaround_at = len(requests_at_head) + len(right_requests)
    else:
        sequence = requests_at_head + left_requests[::-1] + right_requests
        turnaround_at = len(requests_at_head) + len(left_requests)

    schedule: list[tuple[int, str]] = []
    has_turnaround = bool(left_requests and right_requests)
    for index, track in enumerate(sequence):
        action = (
            "Đổi hướng, phục vụ"
            if has_turnaround and index == turnaround_at
            else "Phục vụ"
        )
        schedule.append((track, action))

    return create_result("LOOK", requests, head, direction, schedule)


simulate_look = look_algorithm

__all__ = ["look_algorithm", "simulate_look"]
