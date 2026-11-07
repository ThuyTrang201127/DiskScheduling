"""Biểu đồ đường đi đầu đọc từ trên xuống và so sánh tổng quãng đường."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Mapping

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from algorithms.common import TRACK_MAX, SimulationResult

COLORS = {"LOOK": "#2563eb", "C-LOOK": "#0f9d8a"}
WRAP_COLOR = "#e58a16"


class DiskCharts:
    """Vẽ đường đi theo bước và cột so sánh trực tiếp trên giao diện Tkinter."""

    def __init__(self, parent: tk.Misc) -> None:
        self.figure = Figure(figsize=(10, 4.8), dpi=100, facecolor="#ffffff")
        self.path_axis, self.comparison_axis = self.figure.subplots(1, 2)
        self.figure.subplots_adjust(left=0.08, right=0.97, top=0.88, bottom=0.15, wspace=0.28)
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.widget = self.canvas.get_tk_widget()
        self.widget.configure(highlightthickness=0, background="#ffffff")
        self.results: dict[str, SimulationResult] = {}
        self.head = 0
        self.marker = None
        self.animation_route = "LOOK"
        self._draw_empty()

    def _style_axis(self, axis) -> None:
        axis.set_facecolor("#ffffff")
        axis.tick_params(colors="#53657d", labelsize=8)
        for spine in axis.spines.values():
            spine.set_color("#dce4ef")
        axis.grid(True, color="#e7edf5", linewidth=0.8, alpha=0.9)
        axis.set_axisbelow(True)

    def _draw_empty(self) -> None:
        self.path_axis.clear()
        self.comparison_axis.clear()
        self._style_axis(self.path_axis)
        self._style_axis(self.comparison_axis)
        self.path_axis.set_title("Đường đi đầu đọc", color="#172b4d", fontweight="bold")
        self.path_axis.set_xlabel("Cylinder")
        self.path_axis.set_ylabel("Thứ tự bước")
        self.path_axis.set_xlim(-5, TRACK_MAX + 5)
        self.path_axis.set_ylim(0.5, -0.5)
        self.comparison_axis.set_title(
            "So sánh tổng quãng đường", color="#172b4d", fontweight="bold"
        )
        self.comparison_axis.set_ylabel("Di chuyển (cylinder)")
        self.comparison_axis.text(
            0.5,
            0.5,
            "Chạy mô phỏng để xem kết quả",
            ha="center",
            va="center",
            color="#65758b",
            transform=self.comparison_axis.transAxes,
            fontsize=9,
        )
        self.canvas.draw_idle()

    def update(
        self,
        results: Mapping[str, SimulationResult],
        head: int,
        animation_route: str,
    ) -> None:
        self.results = dict(results)
        self.head = head
        self.animation_route = animation_route
        self.path_axis.clear()
        self.comparison_axis.clear()
        self.marker = None
        self._style_axis(self.path_axis)
        self._style_axis(self.comparison_axis)
        self.path_axis.set_title("Đường đi đầu đọc", color="#172b4d", fontweight="bold")
        self.path_axis.set_xlabel("Cylinder")
        self.path_axis.set_ylabel("Thứ tự bước (từ trên xuống)")
        self.path_axis.set_xlim(-5, TRACK_MAX + 5)
        self.path_axis.set_xticks(range(0, TRACK_MAX + 1, 20))

        largest_step = max(
            (len(result.steps) for result in self.results.values()), default=0
        )
        self.path_axis.set_ylim(largest_step + 0.5, -0.5)
        self.path_axis.set_yticks(range(largest_step + 1))

        for name, result in self.results.items():
            color = COLORS[name]
            x_values = [head, *result.order]
            y_values = list(range(len(result.order) + 1))
            self.path_axis.plot(
                x_values,
                y_values,
                color=color,
                marker="o",
                markersize=4,
                linestyle="None",
                label=f"{name} ({result.total_movement})",
                zorder=3,
            )
            for index, step in enumerate(result.steps, start=1):
                wrapped = "quay vòng" in step.action.lower()
                segment_color = WRAP_COLOR if wrapped else color
                self.path_axis.annotate(
                    "",
                    xy=(step.track, index),
                    xytext=(step.start, index - 1),
                    arrowprops={
                        "arrowstyle": "->",
                        "color": segment_color,
                        "linewidth": 2 if wrapped else 1.2,
                        "linestyle": "--" if wrapped else "-",
                    },
                    zorder=4,
                )
                self.path_axis.annotate(
                    str(step.track),
                    (step.track, index),
                    textcoords="offset points",
                    xytext=(3, 5),
                    fontsize=7,
                    color="#34445a",
                )
            self.path_axis.scatter(
                [0], [head], color="#172b4d", marker="D", s=35, zorder=5
            )

        if self.results:
            self.path_axis.legend(loc="best", fontsize=8, frameon=False)
        else:
            self.path_axis.text(
                0.5,
                0.5,
                "Không có yêu cầu cần phục vụ",
                ha="center",
                va="center",
                color="#65758b",
                transform=self.path_axis.transAxes,
            )

        names = list(self.results)
        values = [self.results[name].total_movement for name in names]
        bars = self.comparison_axis.bar(
            names,
            values,
            color=[COLORS[name] for name in names],
            width=0.55,
            edgecolor="white",
        )
        self.comparison_axis.set_title(
            "So sánh tổng quãng đường"
            if len(names) > 1
            else f"Tổng quãng đường — {names[0]}",
            color="#172b4d",
            fontweight="bold",
        )
        self.comparison_axis.set_ylabel("Di chuyển (cylinder)")
        self.comparison_axis.set_ylim(0, max(values, default=0) * 1.2 + 5)
        for bar, value in zip(bars, values):
            self.comparison_axis.annotate(
                str(value),
                (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                color="#172b4d",
                fontweight="bold",
                fontsize=9,
            )

        active = self.results.get(animation_route)
        if active is not None and active.steps:
            (self.marker,) = self.path_axis.plot(
                [head],
                [0],
                marker="o",
                markersize=10,
                markerfacecolor=WRAP_COLOR,
                markeredgecolor="white",
                linestyle="None",
                zorder=6,
            )
        self.canvas.draw_idle()

    def set_progress(self, route: str, step_index: int, fraction: float) -> None:
        result = self.results.get(route)
        if result is None or self.marker is None:
            return
        if step_index >= len(result.steps):
            self.marker.set_data([result.order[-1]], [len(result.steps)])
        else:
            step = result.steps[step_index]
            x = step.start + (step.track - step.start) * fraction
            y = step_index + fraction
            self.marker.set_data([x], [y])
        self.canvas.draw_idle()

    def clear(self) -> None:
        self.results.clear()
        self.marker = None
        self._draw_empty()
