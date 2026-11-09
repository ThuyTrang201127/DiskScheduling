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


def clook_algorithm(
    requests: Sequence[int],
    head: int,
    direction: Direction = "up",
    track_max: int = TRACK_MAX,
) -> SimulationResult:
    """Phục vụ một chiều; quay vòng đến đầu kia rồi tiếp tục cùng chiều."""
    direction = validate_input(requests, head, direction, track_max)
    sorted_requests = sorted(requests)
    left_requests = [track for track in sorted_requests if track < head]
    right_requests = [track for track in sorted_requests if track > head]
    requests_at_head = [track for track in sorted_requests if track == head]

    if direction == "up":
        sequence = requests_at_head + right_requests + left_requests
        wrap_at = len(requests_at_head) + len(right_requests)
        wrap_action = "Quay vòng, tiếp tục phải"
    else:
        sequence = requests_at_head + left_requests[::-1] + right_requests[::-1]
        wrap_at = len(requests_at_head) + len(left_requests)
        wrap_action = "Quay vòng, tiếp tục trái"

    schedule: list[tuple[int, str]] = []
    has_wraparound = bool(left_requests and right_requests)
    for index, track in enumerate(sequence):
        action = (
            wrap_action
            if has_wraparound and index == wrap_at
            else "Phục vụ"
        )
        schedule.append((track, action))

    return create_result("C-LOOK", requests, head, direction, schedule)


simulate_clook = clook_algorithm

__all__ = ["clook_algorithm", "simulate_clook"]
