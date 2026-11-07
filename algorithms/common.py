"""Kiểu dữ liệu và hàm dùng chung cho các thuật toán lập lịch đĩa."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Sequence, cast

TRACK_MIN = 0
TRACK_MAX = 199
Direction = Literal["up", "down"]
Algorithm = Literal["LOOK", "C-LOOK"]


@dataclass(frozen=True)
class SimulationStep:
    """Một lần đầu đọc di chuyển để phục vụ một yêu cầu."""

    start: int
    track: int
    movement: int
    cumulative_movement: int
    direction: str
    action: str
    remaining: tuple[int, ...]


@dataclass(frozen=True)
class SimulationResult:
    """Kết quả và nhật ký đầy đủ của một lần mô phỏng."""

    algorithm: Algorithm
    order: tuple[int, ...]
    steps: tuple[SimulationStep, ...]
    total_movement: int


def parse_requests(value: str) -> list[int]:
    """Chuyển danh sách cylinder phân tách bằng dấu cách hoặc dấu phẩy."""
    if not value.strip():
        return []
    if re.fullmatch(r"\s*[+-]?\d+(?:\s*(?:,|\s+)\s*[+-]?\d+)*\s*", value) is None:
        raise ValueError(
            "Danh sách chỉ được chứa số nguyên, ngăn cách bằng dấu cách "
            "hoặc dấu phẩy, ví dụ: 98 37 122."
        )
    return [int(item) for item in re.findall(r"[+-]?\d+", value)]


def validate_input(
    requests: Sequence[int],
    head: int,
    direction: str,
    track_max: int = TRACK_MAX,
) -> Direction:
    """Kiểm tra cylinder, vị trí đầu đọc và hướng trước khi mô phỏng."""
    if isinstance(track_max, bool) or not isinstance(track_max, int):
        raise ValueError("Cylinder lớn nhất phải là số nguyên.")
    if track_max < TRACK_MIN:
        raise ValueError(
            f"Cylinder lớn nhất phải lớn hơn hoặc bằng {TRACK_MIN}."
        )
    if isinstance(head, bool) or not isinstance(head, int):
        raise ValueError("Vị trí đầu đọc phải là số nguyên.")
    if not TRACK_MIN <= head <= track_max:
        raise ValueError(
            f"Vị trí đầu đọc phải nằm trong khoảng {TRACK_MIN}..{track_max}."
        )
    if direction not in ("up", "down"):
        raise ValueError("Hướng di chuyển chỉ nhận 'up' hoặc 'down'.")
    seen: set[int] = set()
    for cylinder in requests:
        if isinstance(cylinder, bool) or not isinstance(cylinder, int):
            raise ValueError("Mỗi cylinder phải là một số nguyên.")
        if not TRACK_MIN <= cylinder <= track_max:
            raise ValueError(
                f"Cylinder {cylinder} không hợp lệ; giá trị phải từ "
                f"{TRACK_MIN} đến {track_max}."
            )
        if cylinder in seen:
            raise ValueError(
                f"Cylinder {cylinder} bị trùng trong danh sách yêu cầu."
            )
        seen.add(cylinder)
    return cast(Direction, direction)


def create_result(
    algorithm: Algorithm,
    requests: Sequence[int],
    head: int,
    direction: Direction,
    schedule: Sequence[tuple[int, str]],
) -> SimulationResult:
    """Tạo nhật ký chi tiết từ lịch cylinder đã được thuật toán sắp xếp."""
    pending = list(requests)
    position = head
    cumulative = 0
    steps: list[SimulationStep] = []

    for cylinder, action in schedule:
        pending.remove(cylinder)
        movement = abs(cylinder - position)
        cumulative += movement

        if "quay vòng" in action.lower():
            physical_direction = "Phải" if cylinder > position else "Trái"
            continuing_direction = "phải" if direction == "up" else "trái"
            step_direction = (
                f"{physical_direction} (quay vòng, tiếp tục {continuing_direction})"
            )
        else:
            step_direction = (
                "Phải"
                if cylinder > position
                else "Trái"
                if cylinder < position
                else ("Phải" if direction == "up" else "Trái")
            )

        steps.append(
            SimulationStep(
                start=position,
                track=cylinder,
                movement=movement,
                cumulative_movement=cumulative,
                direction=step_direction,
                action=action,
                remaining=tuple(pending),
            )
        )
        position = cylinder

    return SimulationResult(
        algorithm=algorithm,
        order=tuple(cylinder for cylinder, _ in schedule),
        steps=tuple(steps),
        total_movement=cumulative,
    )
