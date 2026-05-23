"""
任务控制台 (Mission Control)
炫酷的终端 UI —— 实时展示智能体团队工作过程。
使用 ANSI 色彩，兼容 Windows Terminal / Linux / macOS。
"""

import json
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── ANSI 色彩码 ───────────────────────────────────────────
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
BG_BLACK = "\033[40m"
BG_RED = "\033[101m"
BG_GREEN = "\033[102m"
BG_YELLOW = "\033[103m"
BG_BLUE = "\033[104m"
BG_MAGENTA = "\033[105m"
BG_CYAN = "\033[106m"

# Windows Terminal 色彩支持
if sys.platform == "win32":
    os.system("")  # 启用 ANSI 处理


def _ts() -> str:
    """简短时间戳."""
    return datetime.now().strftime("%H:%M:%S")


# ── 智能体角色定义 ────────────────────────────────────────
AGENTS = [
    ("Director",        "任务总监",     CYAN,    "◆"),
    ("Propulsion Chief","推进总工",     RED,     "▲"),
    ("Structures Chief","结构总工",     GREEN,   "■"),
    ("GNC Chief",       "飞控总工",     BLUE,    "●"),
    ("Sim Chief",       "仿真主任",     MAGENTA, "◈"),
    ("Supply Agent",    "采购与供应链", YELLOW,  "◎"),
    ("Safety Officer",  "法规与安全",   WHITE,   "◇"),
    ("Skill Crafter",   "技能工匠",     CYAN,    "⬡"),
]

TOOLS_LIST = [
    ("freecad_model_builder",   "FreeCAD 参数化建模"),
    ("freecad_mass_extractor",  "质量特性提取"),
    ("openrocket_sim_runner",   "OpenRocket 飞行仿真"),
    ("openrocket_param_sweep",  "批量参数扫描"),
    ("stability_analyzer",      "稳定性裕度分析"),
    ("skill_creator_tool",      "技能文件生成"),
    ("knowledge_gap_detector",  "知识缺口检测"),
    ("web_search_tool",         "四源网络搜索"),
    ("source_evaluator",        "信源可靠性评估"),
    ("complexity_monitor",      "复杂度监控"),
]


class Spinner:
    """旋转动画 —— 在后台线程运行."""

    def __init__(self, message: str = "工作中"):
        self._message = message
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.5)
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

    def _spin(self):
        i = 0
        while self._running:
            frame = self._frames[i % len(self._frames)]
            sys.stdout.write(
                f"\r  {CYAN}{frame}{RESET} {self._message}..."
            )
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1


class MissionControl:
    """任务控制台 —— 所有显示逻辑集中于此."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self._phase = 0

    # ── 横幅 ─────────────────────────────────────────────

    def print_banner(self):
        """打印火箭工厂横幅."""
        if not self.verbose:
            return
        print()
        print(f"{RED}{BOLD}")
        print("  ╔══════════════════════════════════════════════════════╗")
        print("  ║         火  箭  工  厂  —  AI 智能体团队            ║")
        print("  ║         ROCKET FACTORY MISSION CONTROL                ║")
        print("  ╚══════════════════════════════════════════════════════╝")
        print(f"{RESET}")

    def print_divider(self, char: str = "─", color: str = DIM):
        """打印分隔线."""
        if not self.verbose:
            return
        print(f"{color}{char * 60}{RESET}")

    # ── 任务简报 ─────────────────────────────────────────

    def print_briefing(self, instruction: str, output_dir: str):
        """打印任务启动简报."""
        if not self.verbose:
            return
        self.print_divider("═", CYAN)
        print(f"  {BOLD}{WHITE}📋 任务指令{RESET}")
        print(f"  {YELLOW}Founder:{RESET} {instruction}")
        print()
        print(f"  {DIM}产出目录:{RESET} {output_dir}")
        print(f"  {DIM}启动时间:{RESET} {_ts()}")
        self.print_divider("═", CYAN)
        print()

    # ── 智能体阵容 ───────────────────────────────────────

    def print_agent_roster(self):
        """打印智能体团队阵容."""
        if not self.verbose:
            return
        print(f"  {BOLD}{WHITE}🛰️  智能体团队就绪{RESET}")
        print()
        for name, role, color, icon in AGENTS:
            status = f"{GREEN}●{RESET}" if name != "Director" else f"{CYAN}◆{RESET}"
            print(f"  {status} {color}{BOLD}{icon} {name:<20}{RESET}{DIM}{role}{RESET}")
        print()
        print(f"  {DIM}工具链: {len(TOOLS_LIST)} 个工具 | 框架: Sigma (PDCA) | LLM: DeepSeek V4{RESET}")
        print()

    # ── 任务阶段 ─────────────────────────────────────────

    def phase(self, title: str):
        """开始一个新阶段."""
        self._phase += 1
        if not self.verbose:
            return
        print()
        print(f"  {BOLD}{YELLOW}[阶段 {self._phase}] {title}{RESET}")
        self.print_divider("·", DIM)

    def agent_activated(self, agent_name: str, task: str):
        """显示智能体被激活."""
        if not self.verbose:
            return
        for name, role, color, icon in AGENTS:
            if name == agent_name:
                print(f"  {color}{icon} {BOLD}{name}{RESET} {DIM}▸{RESET} {task}")
                return
        print(f"  {DIM}  ▸ {agent_name}: {task}{RESET}")

    def agent_completed(self, agent_name: str):
        """显示智能体完成工作."""
        if not self.verbose:
            return
        for name, _, color, _ in AGENTS:
            if name == agent_name:
                print(f"  {color}  ✓{RESET} {DIM}{name} 完成{RESET}")
                return

    def tool_call(self, tool_name: str, params: dict = None):
        """显示工具调用."""
        if not self.verbose:
            return
        for t_name, t_desc in TOOLS_LIST:
            if t_name == tool_name:
                print(f"  {MAGENTA}  ⚙ {t_desc}{RESET}")
                if params:
                    for k, v in params.items():
                        print(f"  {DIM}    {k}: {v}{RESET}")
                return
        print(f"  {MAGENTA}  ⚙ {tool_name}{RESET}")

    def tool_result(self, success: bool, summary: str = ""):
        """显示工具执行结果."""
        if not self.verbose:
            return
        icon = f"{GREEN}✓{RESET}" if success else f"{RED}✗{RESET}"
        print(f"  {icon} {DIM}{summary}{RESET}")

    def director_thinking(self, message: str):
        """显示 Director 的决策/思考."""
        if not self.verbose:
            return
        print(f"  {CYAN}  🧠 Director:{RESET} {DIM}{message}{RESET}")

    # ── 完成 ─────────────────────────────────────────────

    def print_mission_complete(self, output_dir: str):
        """任务完成摘要."""
        if not self.verbose:
            return
        print()
        self.print_divider("═", GREEN)
        print(f"  {GREEN}{BOLD}✅ 任务执行完成{RESET}")
        print(f"  {DIM}产出目录: {output_dir}{RESET}")
        print(f"  {DIM}完成时间: {_ts()}{RESET}")
        self.print_divider("═", GREEN)
        print()

    def print_mission_error(self, error: str):
        """任务失败显示."""
        if not self.verbose:
            return
        print()
        self.print_divider("═", RED)
        print(f"  {RED}{BOLD}⚠ 任务遇到障碍{RESET}")
        print(f"  {RED}{error}{RESET}")
        print(f"  {YELLOW}→ 正在转换为'需要解决的技术问题清单'...{RESET}")
        self.print_divider("═", RED)
        print()

    # ── 结果显示 ─────────────────────────────────────────

    def print_result_preview(self, text: str, max_lines: int = 30):
        """打印结果的格式化预览."""
        if not self.verbose:
            return

        lines = text.split("\n")
        print(f"  {BOLD}{WHITE}📄 执行报告预览{RESET}")
        self.print_divider("─", DIM)

        for line in lines[:max_lines]:
            line = line.rstrip()
            if line.startswith("# "):
                print(f"  {BOLD}{YELLOW}{line}{RESET}")
            elif line.startswith("## "):
                print(f"  {BOLD}{WHITE}{line}{RESET}")
            elif line.startswith("### "):
                print(f"  {BOLD}{CYAN}{line}{RESET}")
            elif line.startswith("**") and line.endswith("**"):
                print(f"  {BOLD}{line}{RESET}")
            elif line.startswith("- ") or line.startswith("* "):
                print(f"  {DIM}  {line}{RESET}")
            elif line.startswith("|"):
                print(f"  {DIM}{line}{RESET}")
            else:
                print(f"  {line}")

        if len(lines) > max_lines:
            print(f"  {DIM}... (共 {len(lines)} 行，完整报告见产出目录){RESET}")

        self.print_divider("─", DIM)

    # ── 索引管理 ─────────────────────────────────────────

    def generate_index(self):
        """生成 output/INDEX.md 索引文件."""
        base = Path("output")
        if not base.exists():
            return

        entries = []
        for entry in sorted(base.iterdir()):
            if entry.is_dir() and entry.name.startswith("v"):
                result_file = entry / "result.json"
                report_file = entry / "REPORT.md"
                error_file = entry / "error.json"

                status = "⬜ 空"
                instruction = ""
                timestamp = ""

                if result_file.exists():
                    try:
                        data = json.loads(result_file.read_text(encoding="utf-8"))
                        instruction = data.get("instruction", "")
                        timestamp = data.get("timestamp", "")
                        has_content = data.get("result") or data.get("summary") or data.get("sections")
                        status = "✅ 成功" if has_content else "⬜ 空"
                    except Exception:
                        status = "⚠ 异常"
                elif error_file.exists():
                    try:
                        data = json.loads(error_file.read_text(encoding="utf-8"))
                        instruction = data.get("instruction", "")
                        timestamp = data.get("timestamp", "")
                        status = "❌ 失败"
                    except Exception:
                        status = "❌ 失败"

                has_report = "📄" if report_file.exists() else ""
                entries.append({
                    "version": entry.name,
                    "status": status,
                    "instruction": instruction[:80] if instruction else "(无记录)",
                    "timestamp": timestamp[:19] if timestamp else "",
                    "has_report": has_report,
                })

        lines = [
            "# 火箭工厂 —— 任务产出索引",
            "",
            f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "| 版本 | 状态 | 指令 | 时间 | 报告 |",
            "|------|:----:|------|------|:----:|",
        ]

        for e in entries:
            lines.append(
                f"| [{e['version']}]({e['version']}/) "
                f"| {e['status']} "
                f"| {e['instruction']} "
                f"| {e['timestamp']} "
                f"| {e['has_report']} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 使用方式",
            "",
            "```bash",
            "python main.py \"你的任务指令\"    # 执行新任务",
            "python main.py --list             # 列出历史产出",
            "python main.py --view v4           # 查看指定版本报告",
            "```",
        ])

        index_path = base / "INDEX.md"
        index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(index_path)


# 全局单例
_mission_control: Optional[MissionControl] = None


def get_mc(verbose: bool = True) -> MissionControl:
    global _mission_control
    if _mission_control is None:
        _mission_control = MissionControl(verbose=verbose)
    return _mission_control
