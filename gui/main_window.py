"""Cửa sổ Tkinter cho ứng dụng mô phỏng lập lịch đĩa."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from algorithms import (
    TRACK_MAX,
    TRACK_MIN,
    Algorithm,
    Direction,
    SimulationResult,
    parse_requests,
    simulate_clook,
    simulate_look,
    validate_input,
)
from visualization import DiskCharts

BACKGROUND = "#f3f6fb"
NAVY = "#172b4d"
BLUE = "#2563eb"
MUTED = "#65758b"


class DiskSchedulingWindow:
    """Nhận dữ liệu, chạy thuật toán, hiển thị nhật ký và biểu đồ."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("DISK SCHEDULING SIMULATOR | LOOK & C-LOOK")
        self.root.geometry("1240x900")
        self.root.minsize(1000, 720)
        self.root.configure(bg=BACKGROUND)

        self.algorithm_var = tk.StringVar(value="So sánh cả hai")
        self.requests_var = tk.StringVar(value="98, 183, 37, 122, 14, 124, 65, 67")
        self.head_var = tk.StringVar(value="53")
        self.direction_var = tk.StringVar(value="Tăng")
        self.speed_var = tk.StringVar(value="Vừa")
        self.status_var = tk.StringVar(value="Nhập dữ liệu rồi chọn Chạy mô phỏng.")
        self.order_var = tk.StringVar(value="—")
        self.distance_var = tk.StringVar(value="—")
        self.served_var = tk.StringVar(value="—")
        self.results: dict[str, SimulationResult] = {}
        self.initial_head = 0
        self.active_route: str | None = None
        self.animation_step = 0
        self.animation_frame = 0
        self.animation_frames = 16
        self.animation_after_id: str | None = None
        self.animation_token = 0
        self.paused = False

        self._configure_style()
        self._build_layout()
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background=BACKGROUND)
        style.configure(
            "TLabel", background="#ffffff", foreground=NAVY, font=("Segoe UI", 10)
        )
        style.configure(
            "Header.TLabel",
            background=BACKGROUND,
            foreground=NAVY,
            font=("Segoe UI", 22, "bold"),
        )
        style.configure(
            "Subheader.TLabel",
            background=BACKGROUND,
            foreground=MUTED,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Metric.TLabel", foreground=BLUE, font=("Segoe UI", 15, "bold")
        )
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 8))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=27, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("TLabelframe", background="#ffffff")
        style.configure(
            "TLabelframe.Label",
            background="#ffffff",
            foreground=NAVY,
            font=("Segoe UI", 10, "bold"),
        )
        style.configure("TNotebook", background=BACKGROUND, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 8), font=("Segoe UI", 10))

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        header = ttk.Frame(self.root, padding=(22, 16, 22, 8))
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(
            header,
            text="DISK SCHEDULING SIMULATOR",
            style="Header.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="Mô phỏng từng bước LOOK và C-LOOK · Track từ "
            f"{TRACK_MIN} đến {TRACK_MAX}",
            style="Subheader.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        inputs = ttk.LabelFrame(
            self.root, text="  Dữ liệu mô phỏng  ", padding=(14, 10)
        )
        inputs.grid(row=1, column=0, padx=22, pady=(4, 10), sticky="ew")
        inputs.columnconfigure(1, weight=1)
        inputs.columnconfigure(3, weight=1)

        ttk.Label(inputs, text="Hàng đợi cylinder").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(inputs, textvariable=self.requests_var).grid(
            row=0, column=1, columnspan=5, sticky="ew", padx=5, pady=5
        )
        ttk.Label(
            inputs,
            text="Số nguyên phân tách bằng dấu phẩy; để trống để mô phỏng hàng đợi rỗng.",
            style="Subheader.TLabel",
        ).grid(row=1, column=1, columnspan=5, sticky="w", padx=5)

        ttk.Label(inputs, text="Vị trí đầu đọc").grid(
            row=2, column=0, sticky="w", padx=5, pady=(9, 4)
        )
        ttk.Entry(inputs, textvariable=self.head_var, width=12).grid(
            row=2, column=1, sticky="w", padx=5, pady=(9, 4)
        )
        ttk.Label(inputs, text="Hướng ban đầu").grid(
            row=2, column=2, sticky="e", padx=5, pady=(9, 4)
        )
        ttk.Combobox(
            inputs,
            textvariable=self.direction_var,
            values=("Tăng", "Giảm"),
            state="readonly",
            width=12,
        ).grid(row=2, column=3, sticky="w", padx=5, pady=(9, 4))
        ttk.Label(inputs, text="Thuật toán").grid(
            row=2, column=4, sticky="e", padx=5, pady=(9, 4)
        )
        ttk.Combobox(
            inputs,
            textvariable=self.algorithm_var,
            values=("LOOK", "C-LOOK", "So sánh cả hai"),
            state="readonly",
            width=20,
        ).grid(row=2, column=5, sticky="w", padx=5, pady=(9, 4))

        buttons = ttk.Frame(inputs)
        buttons.grid(row=3, column=0, columnspan=6, sticky="ew", pady=(10, 0))
        ttk.Button(buttons, text="Nạp dữ liệu mẫu", command=self._load_example).pack(
            side="left"
        )
        ttk.Button(
            buttons,
            text="Chạy mô phỏng",
            style="Primary.TButton",
            command=self._run_simulation,
        ).pack(side="left", padx=(8, 0))
        ttk.Button(buttons, text="Hiển thị biểu đồ", command=self._show_chart).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(buttons, text="Xóa dữ liệu", command=self._clear).pack(
            side="right"
        )
        ttk.Label(buttons, text="Tốc độ:").pack(side="right", padx=(10, 4))
        ttk.Combobox(
            buttons,
            textvariable=self.speed_var,
            values=("Chậm", "Vừa", "Nhanh"),
            state="readonly",
            width=9,
        ).pack(side="right")
        self.pause_button = ttk.Button(
            buttons, text="Tạm dừng", command=self._toggle_pause, state="disabled"
        )
        self.pause_button.pack(side="right", padx=(0, 8))

        summary = ttk.Frame(self.root, padding=(22, 0, 22, 9))
        summary.grid(row=2, column=0, sticky="nsew")
        summary.columnconfigure(0, weight=1)
        summary.rowconfigure(1, weight=1)
        metrics = ttk.Frame(summary)
        metrics.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        for column in range(3):
            metrics.columnconfigure(column, weight=1)
        self._metric(metrics, 0, "THỨ TỰ PHỤC VỤ", self.order_var)
        self._metric(metrics, 1, "TỔNG QUÃNG ĐƯỜNG", self.distance_var)
        self._metric(metrics, 2, "TIẾN ĐỘ PHỤC VỤ", self.served_var)

        self.notebook = ttk.Notebook(summary)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        self.chart_tab = ttk.Frame(self.notebook, padding=8)
        self.log_tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.chart_tab, text="Biểu đồ & so sánh")
        self.notebook.add(self.log_tab, text="Nhật ký từng bước")
        self.chart_tab.columnconfigure(0, weight=1)
        self.chart_tab.rowconfigure(0, weight=1)
        self.charts = DiskCharts(self.chart_tab)
        self.charts.widget.grid(row=0, column=0, sticky="nsew")
        self._build_log_table()

        footer = ttk.Frame(self.root, padding=(22, 0, 22, 12))
        footer.grid(row=3, column=0, sticky="ew")
        ttk.Label(
            footer,
            textvariable=self.status_var,
            background=BACKGROUND,
            foreground=MUTED,
        ).pack(anchor="w")

    @staticmethod
    def _metric(
        parent: ttk.Frame, column: int, title: str, value: tk.StringVar
    ) -> None:
        card = ttk.LabelFrame(parent, text=f"  {title}  ", padding=(10, 6))
        card.grid(row=0, column=column, sticky="ew", padx=(0, 8))
        ttk.Label(
            card, textvariable=value, style="Metric.TLabel", wraplength=350
        ).pack(anchor="w")

    def _build_log_table(self) -> None:
        self.log_tab.columnconfigure(0, weight=1)
        self.log_tab.rowconfigure(0, weight=1)
        columns = (
            "algorithm",
            "step",
            "from",
            "to",
            "distance",
            "total",
            "direction",
            "action",
            "remaining",
        )
        self.log_table = ttk.Treeview(
            self.log_tab, columns=columns, show="headings", height=12
        )
        headings = {
            "algorithm": ("Thuật toán", 90),
            "step": ("Bước", 48),
            "from": ("Từ", 54),
            "to": ("Đến", 54),
            "distance": ("Khoảng cách", 82),
            "total": ("Tích lũy", 72),
            "direction": ("Hướng", 170),
            "action": ("Sự kiện", 175),
            "remaining": ("Hàng đợi còn lại", 300),
        }
        for column, (heading, width) in headings.items():
            self.log_table.heading(column, text=heading)
            self.log_table.column(column, width=width, minwidth=45, anchor="w")
        scrollbar = ttk.Scrollbar(
            self.log_tab, orient="vertical", command=self.log_table.yview
        )
        self.log_table.configure(yscrollcommand=scrollbar.set)
        self.log_table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _load_example(self) -> None:
        self.requests_var.set("98, 183, 37, 122, 14, 124, 65, 67")
        self.head_var.set("53")
        self.direction_var.set("Tăng")
        self.algorithm_var.set("So sánh cả hai")
        self.status_var.set("Đã nạp TC01. Nhấn Chạy mô phỏng để xem kết quả.")

    def _read_input(self) -> tuple[list[int], int, Direction]:
        requests = parse_requests(self.requests_var.get())
        head_text = self.head_var.get().strip()
        try:
            head = int(head_text)
        except ValueError as error:
            raise ValueError("Vị trí đầu đọc phải là số nguyên.") from error
        direction: Direction = "up" if self.direction_var.get() == "Tăng" else "down"
        validate_input(requests, head, direction)
        return requests, head, direction

    def _run_simulation(self) -> None:
        try:
            requests, head, direction = self._read_input()
            look_result = simulate_look(requests, head, direction)
            clook_result = simulate_clook(requests, head, direction)
        except ValueError as error:
            self.status_var.set(f"Lỗi dữ liệu: {error}")
            messagebox.showerror("Dữ liệu không hợp lệ", str(error), parent=self.root)
            return

        choice = self.algorithm_var.get()
        if choice == "LOOK":
            self.results = {"LOOK": look_result}
            self.active_route: Algorithm = "LOOK"
        elif choice == "C-LOOK":
            self.results = {"C-LOOK": clook_result}
            self.active_route = "C-LOOK"
        else:
            self.results = {"LOOK": look_result, "C-LOOK": clook_result}
            self.active_route = "LOOK"

        self._stop_animation()
        self.initial_head = head
        self.animation_step = 0
        self.animation_frame = 0
        self.paused = False
        self.pause_button.configure(
            state="normal" if any(result.steps for result in self.results.values()) else "disabled",
            text="Tạm dừng",
        )
        self._show_summary(requests, head)
        self._fill_log()
        self.charts.update(self.results, head, self.active_route)
        self._print_terminal_log(requests, head)
        self.notebook.select(self.chart_tab)

        active = self.results[self.active_route]
        if active.steps:
            self.status_var.set(f"Đang mô phỏng {self.active_route}…")
            self._schedule_animation(self.animation_token)
        else:
            self.status_var.set("Hàng đợi rỗng — không có yêu cầu cần phục vụ.")

    def _show_summary(self, requests: list[int], head: int) -> None:
        if len(self.results) == 2:
            self.order_var.set("Xem từng thứ tự trong nhật ký")
            self.distance_var.set(
                f"LOOK: {self.results['LOOK'].total_movement}  |  "
                f"C-LOOK: {self.results['C-LOOK'].total_movement}"
            )
        else:
            result = next(iter(self.results.values()))
            self.order_var.set(" → ".join(map(str, (head, *result.order))))
            self.distance_var.set(f"{result.total_movement} cylinder")
        self.served_var.set(f"0 / {len(requests)}")

    def _fill_log(self) -> None:
        self.log_table.delete(*self.log_table.get_children())
        for name, result in self.results.items():
            if not result.steps:
                self.log_table.insert(
                    "",
                    "end",
                    values=(name, "—", self.initial_head, "—", 0, 0, "—", "Hàng đợi rỗng", "—"),
                )
                continue
            for index, step in enumerate(result.steps, start=1):
                self.log_table.insert(
                    "",
                    "end",
                    values=(
                        name,
                        index,
                        step.start,
                        step.track,
                        step.movement,
                        step.cumulative_movement,
                        step.direction,
                        step.action,
                        ", ".join(map(str, step.remaining)) or "—",
                    ),
                )

    def _print_terminal_log(self, requests: list[int], head: int) -> None:
        print("\n" + "=" * 78)
        print(f"Hàng đợi: {requests} | Đầu đọc ban đầu: {head}")
        for name, result in self.results.items():
            print(f"\n{name} | thứ tự phục vụ: {list(result.order)}")
            if not result.steps:
                print("  Hàng đợi rỗng; tổng di chuyển: 0 cylinder.")
            for index, step in enumerate(result.steps, start=1):
                print(
                    f"  Bước {index}: {step.start} -> {step.track}; "
                    f"khoảng cách {step.movement}; tích lũy "
                    f"{step.cumulative_movement}; hướng {step.direction}; "
                    f"{step.action}; còn lại {list(step.remaining)}"
                )
            print(f"Tổng quãng đường: {result.total_movement} cylinder")
        print("=" * 78, flush=True)

    def _show_chart(self) -> None:
        self.notebook.select(self.chart_tab)
        self.charts.canvas.draw_idle()
        self.status_var.set("Đang hiển thị biểu đồ đường đi và so sánh hiệu năng.")

    def _schedule_animation(self, token: int) -> None:
        if token != self.animation_token or self.active_route is None:
            return
        if self.paused:
            self.animation_after_id = self.root.after(
                100, lambda: self._schedule_animation(token)
            )
            return
        active = self.results[self.active_route]
        if self.animation_step >= len(active.steps):
            self.charts.set_progress(
                self.active_route, len(active.steps), 1.0
            )
            self.served_var.set(f"{len(active.steps)} / {len(active.steps)}")
            self.animation_after_id = None
            self.pause_button.configure(state="disabled", text="Tạm dừng")
            self.status_var.set(
                f"Hoàn tất {self.active_route}: "
                f"{active.total_movement} cylinder."
            )
            return

        speed_ms = {"Chậm": 800, "Vừa": 420, "Nhanh": 180}.get(
            self.speed_var.get(), 420
        )
        self.animation_frame += 1
        fraction = self.animation_frame / self.animation_frames
        self.charts.set_progress(self.active_route, self.animation_step, fraction)
        if self.animation_frame >= self.animation_frames:
            step = active.steps[self.animation_step]
            self.animation_step += 1
            self.animation_frame = 0
            self.served_var.set(
                f"{self.animation_step} / {len(active.steps)}"
            )
            self.status_var.set(
                f"{self.active_route} — bước {self.animation_step}/"
                f"{len(active.steps)}: đầu đọc đến cylinder {step.track}."
            )
        self.animation_after_id = self.root.after(
            max(12, speed_ms // self.animation_frames),
            lambda: self._schedule_animation(token),
        )

    def _toggle_pause(self) -> None:
        if not any(result.steps for result in self.results.values()):
            return
        self.paused = not self.paused
        self.pause_button.configure(text="Tiếp tục" if self.paused else "Tạm dừng")
        self.status_var.set("Đã tạm dừng hoạt ảnh." if self.paused else "Tiếp tục mô phỏng.")

    def _stop_animation(self) -> None:
        self.animation_token += 1
        if self.animation_after_id is not None:
            self.root.after_cancel(self.animation_after_id)
            self.animation_after_id = None

    def _clear(self) -> None:
        self._stop_animation()
        self.results.clear()
        self.active_route = None
        self.animation_step = 0
        self.animation_frame = 0
        self.paused = False
        self.requests_var.set("")
        self.head_var.set("")
        self.order_var.set("—")
        self.distance_var.set("—")
        self.served_var.set("—")
        self.status_var.set("Đã xóa dữ liệu và kết quả.")
        self.log_table.delete(*self.log_table.get_children())
        self.charts.clear()
        self.pause_button.configure(state="disabled", text="Tạm dừng")

    def _close(self) -> None:
        self._stop_animation()
        self.root.destroy()


def run_app() -> None:
    root = tk.Tk()
    DiskSchedulingWindow(root)
    root.mainloop()
