"""
火箭工厂 —— Σ (Sigma) PDCA 多智能体协同框架
Founder 直接传入愿景级指令，启动 AI 智能体团队的 PDCA 协作。
质量第一 · 效率第二 · 成本第三
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ═══ Sigma 框架 ═══
from sigma import SigmaOrchestrator
from sigma.llm import OpenAIBackend
from sigma_config import (
    build_sigma_config,
    build_tool_specs,
    build_agents,
    build_skills,
    _project_root,
)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def run(
    instruction: str,
    output_dir: Optional[str] = None,
    verbose: bool = True,
    max_rounds: int = 4,
    replay: Optional[str] = None,
    interactive: bool = True,
) -> dict:
    """
    启动 Σ (Sigma) PDCA 多智能体协同框架。

    Args:
        instruction: Founder 的愿景级指令
        output_dir: 产出目录（默认自动递增版本号）
        verbose: 是否输出详细执行日志
        max_rounds: 最大 PDCA 轮次
        replay: 回放文件路径（用于测试，不烧 token）
        interactive: 是否允许 Founder 在每轮后介入

    Returns:
        dict: 包含结构化结果和文件路径
    """
    from pathlib import Path as _Path
    _ROOT = _Path(__file__).parent.resolve()

    if output_dir is None:
        output_dir = _next_version()

    output_path = _Path(output_dir)
    if not output_path.is_absolute():
        output_path = _ROOT / "output" / output_dir

    # 回放模式
    if replay:
        return _run_replay(instruction, output_path, replay, verbose)

    # ── 构建 Sigma 注入 ──
    config = build_sigma_config()
    tools_dir = _ROOT / "tools"
    raw_tools = {}
    # 尝试从 tools 目录发现工具实例
    from sigma.discovery import discover_tools_from_dir
    raw_tools = discover_tools_from_dir(tools_dir)
    tools = build_tool_specs(raw_tools)
    agents = build_agents()
    skills = build_skills()
    llm = OpenAIBackend()

    # 正常模式
    orchestrator = SigmaOrchestrator(
        config=config,
        agents=agents,
        tools=tools,
        skills=skills,
        llm_backend=llm,
        max_rounds=max_rounds,
        verbose=verbose,
        interactive=interactive,
    )

    task_record = {
        "instruction": instruction,
        "timestamp": datetime.now().isoformat(),
        "output_dir": str(output_path),
        "framework": "Sigma PDCA",
    }

    try:
        result = orchestrator.run(instruction, str(output_path))
        result.update({
            "instruction": instruction,
            "timestamp": task_record["timestamp"],
            "output_dir": str(output_path),
        })
        return result

    except Exception as e:
        error_path = output_path / "error.json"
        error_data = {
            "instruction": instruction,
            "timestamp": task_record["timestamp"],
            "error": str(e),
        }
        error_path.write_text(
            json.dumps(error_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n[Σ Error] {e}", file=sys.stderr)
        raise


def _run_replay(
    instruction: str, output_path: Path, replay_file: str, verbose: bool,
) -> dict:
    """回放模式 — 不烧 token 验证框架逻辑."""
    from sigma.replay import ReplayPlayer

    config = build_sigma_config()
    agents = build_agents()
    tools = build_tool_specs({})
    skills = build_skills()
    llm = OpenAIBackend()

    player = ReplayPlayer(replay_file)
    if not player.load():
        return {"error": f"无法加载回放文件: {replay_file}"}

    print(f"  Σ Replay Mode — {player.remaining()} 条预录响应")
    orchestrator = SigmaOrchestrator(
        config=config, agents=agents, tools=tools,
        skills=skills, llm_backend=llm,
        verbose=verbose, interactive=False,
    )
    return orchestrator.run(instruction, str(output_path))


def _next_version() -> str:
    """自动确定下一个版本编号."""
    base = Path("output")
    base.mkdir(exist_ok=True)
    existing = []
    for entry in base.iterdir():
        if entry.is_dir() and entry.name.startswith("v"):
            try:
                existing.append(int(entry.name[1:]))
            except ValueError:
                pass
    return f"v{max(existing, default=0) + 1}"


# ── 向后兼容函数 ──────────────────────────────────────────────


def list_outputs() -> list[dict]:
    """列出所有历史输出目录及任务摘要."""
    base = Path("output")
    if not base.exists():
        return []

    outputs = []
    for entry in sorted(base.iterdir()):
        if entry.is_dir() and entry.name.startswith("v"):
            result_file = entry / "result.json"
            if result_file.exists():
                try:
                    data = json.loads(result_file.read_text(encoding="utf-8"))
                    outputs.append({
                        "version": entry.name,
                        "instruction": data.get("instruction", ""),
                        "timestamp": data.get("timestamp", ""),
                        "framework": data.get("framework", "Sigma PDCA"),
                        "total_rounds": data.get("total_rounds", "N/A"),
                        "final_verdict": data.get("final_verdict", ""),
                    })
                except Exception:
                    outputs.append({
                        "version": entry.name,
                        "instruction": "(解析失败)",
                        "timestamp": "",
                        "framework": "",
                        "total_rounds": "",
                        "final_verdict": "",
                    })
            elif (entry / "REPORT.md").exists():
                outputs.append({
                    "version": entry.name,
                    "instruction": "(无结构化记录)",
                    "timestamp": "",
                    "framework": "",
                    "total_rounds": "",
                    "final_verdict": "",
                })

    return outputs


def view_report(version: str):
    """查看指定版本的完整报告."""
    report_path = Path(f"output/{version}/REPORT.md")
    result_path = Path(f"output/{version}/result.json")

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if report_path.exists():
        print(report_path.read_text(encoding="utf-8"))
    elif result_path.exists():
        data = json.loads(result_path.read_text(encoding="utf-8"))
        print(f"# {version} — 结构化结果\n")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"版本 {version} 无产出记录")


# ── CLI Entry ─────────────────────────────────────────────────


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == "--list":
            outputs = list_outputs()
            if not outputs:
                print("暂无历史产出")
            else:
                print()
                print("火箭工厂 — 历史任务产出")
                print("=" * 60)
                for o in outputs:
                    fw = o.get("framework", "")
                    rounds = o.get("total_rounds", "")
                    extra = f" | {fw}" if fw else ""
                    extra += f" | {rounds}轮" if rounds else ""
                    print(f"  output/{o['version']}/  {o['instruction'][:60]}{extra}")
                    if o.get("timestamp"):
                        print(f"    {o['timestamp']}")
                    if o.get("final_verdict"):
                        print(f"    结论: {o['final_verdict']}")
                    print()
            sys.exit(0)

        elif arg == "--view":
            if len(sys.argv) > 2:
                view_report(sys.argv[2])
            else:
                print("用法: python main.py --view v4")
            sys.exit(0)

        elif arg == "--index":
            from tools.mission_control import get_mc
            mc = get_mc()
            path = mc.generate_index()
            print(f"产出索引已生成: {path}")
            sys.exit(0)

        elif arg == "--replay":
            if len(sys.argv) < 3:
                print("用法: python main.py --replay <responses.json> \"指令\"")
                sys.exit(1)
            replay_file = sys.argv[2]
            instruction = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "test"
            result = run(instruction, replay=replay_file, interactive=False)
            sys.exit(0)

        elif arg == "--yes" or arg == "-y":
            instruction = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
            if not instruction:
                print("用法: python main.py -y \"指令\"")
                sys.exit(1)
            result = run(instruction, interactive=False)

        else:
            instruction = " ".join(sys.argv[1:])
            result = run(instruction)

    else:
        instruction = "设计一枚1公里级可回收验证箭的数字样机，包括推进系统选型、箭体结构设计、气动仿真和GNC方案"
        try:
            result = run(instruction)
        except Exception as e:
            print(f"\n[需要解决的技术问题] {e}", file=sys.stderr)
            sys.exit(1)
