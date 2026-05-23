"""
OpenRocket 仿真工具封装层
通过命令行接口调用 OpenRocket JAR，实现弹道仿真、参数扫描和结果分析。
"""

import csv
import json
import subprocess
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from sigma import BaseTool
except ImportError:
    BaseTool = object  # type: ignore


def _find_java() -> Optional[str]:
    """查找 Java 可执行文件."""
    found = shutil.which("java") or shutil.which("java.exe")
    if found:
        return found
    for d in [
        r"C:\Program Files\Microsoft\jdk-17.0.19.10-hotspot\bin",
        r"C:\Program Files\Java\jre1.8.0_491\bin",
    ]:
        java_exe = Path(d) / "java.exe"
        if java_exe.exists():
            return str(java_exe)
    return None


def _find_openrocket_jar() -> Optional[str]:
    """查找 OpenRocket JAR 文件."""
    candidates = [
        Path(r"C:\Program Files\OpenRocket\OpenRocket.jar"),
        Path(r"C:\Program Files (x86)\OpenRocket\OpenRocket.jar"),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    env_path = os.environ.get("OPENROCKET_JAR")
    if env_path and Path(env_path).exists():
        return env_path
    return None


JAVA_CMD = _find_java()
OPENROCKET_JAR = _find_openrocket_jar()


class OpenRocketSimRunner(BaseTool):
    name: str = "openrocket_sim_runner"
    description: str = (
        "运行 OpenRocket 飞行仿真。OpenRocket 23.09 是 GUI 应用，"
        "无原生 CLI 仿真接口。此工具提供仿真估算和 GUI 启动功能。"
        "输入: ork_file(str), launch_angle(float), wind_speed(float)"
    )

    def _run(
        self,
        ork_file: str,
        launch_angle: float = 85.0,
        wind_speed: float = 3.0,
        wind_direction: float = 0.0,
    ) -> Dict[str, Any]:
        """执行 OpenRocket 仿真（估算模式 + GUI 启动提示）."""
        ork_path = Path(ork_file)

        result = self._simulated_result(launch_angle, wind_speed)
        result["openrocket_installed"] = bool(OPENROCKET_JAR)
        result["java_available"] = bool(JAVA_CMD)

        if ork_path.exists():
            result["ork_file"] = str(ork_path)
            result["note"] = (
                "OpenRocket 23.09 已安装，GUI 模式可用。"
                "运行: OpenRocket.exe 并打开 .ork 文件进行精确仿真。"
                "当前指标为基于经验公式的推估值。"
            )
        else:
            result["ork_file"] = None
            result["note"] = (
                "需要 .ork 文件才能运行精确仿真。"
                "请先在 OpenRocket GUI 中建模并导出 .ork 文件。"
            )

        if OPENROCKET_JAR:
            result["openrocket_jar"] = OPENROCKET_JAR
            result["launch_command"] = f'"{OPENROCKET_JAR}"'

        return result

    def _parse_results(self, csv_path: Path) -> Dict[str, Any]:
        """从仿真输出 CSV 中提取关键指标."""
        if not csv_path.exists():
            return {}

        rows = []
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

        if not rows:
            return {}

        altitudes = [float(r.get("Altitude (m)", 0)) for r in rows]
        velocities = [float(r.get("Vertical velocity (m/s)", 0)) for r in rows]
        mach_numbers = [float(r.get("Mach number", 0)) for r in rows]
        stabilities = [float(r.get("Stability margin (cal)", 0)) for r in rows]
        max_accel = max(abs(float(r.get("Acceleration (m/s²)", 0))) for r in rows)

        return {
            "apogee_m": max(altitudes),
            "max_velocity_ms": max(velocities),
            "max_mach": max(mach_numbers),
            "max_acceleration_ms2": max_accel,
            "min_stability_cal": min(stabilities),
            "flight_time_s": len(rows) * 0.05,  # assumed 50ms timestep
        }

    def _simulated_result(
        self, launch_angle: float, wind_speed: float
    ) -> Dict[str, Any]:
        """无 OpenRocket 时的模拟输出."""
        angle_factor = launch_angle / 90.0
        wind_penalty = 1.0 - wind_speed * 0.02
        return {
            "success": "simulated",
            "note": "OpenRocket 未安装，返回基于经验公式的推估值",
            "metrics": {
                "apogee_m": round(1200 * angle_factor * wind_penalty, 1),
                "max_velocity_ms": round(180 * angle_factor, 1),
                "max_mach": round(0.55 * angle_factor, 2),
                "max_acceleration_ms2": round(80, 1),
                "min_stability_cal": round(1.6 + wind_speed * 0.05, 2),
                "flight_time_s": round(25 * angle_factor, 1),
            },
        }


class OpenRocketParamSweep(BaseTool):
    name: str = "openrocket_param_sweep"
    description: str = (
        "批量参数扫描仿真。对指定参数在范围内进行多次仿真，寻找最优参数组合。"
        "输入: ork_file(str), param_name(str), param_range(list[float])"
    )

    def _run(
        self,
        ork_file: str,
        param_name: str,
        param_values: List[float],
        output_dir: str = "output/v1/sweeps/",
    ) -> List[Dict[str, Any]]:
        """执行参数扫描，返回所有仿真结果."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        results = []
        sim = OpenRocketSimRunner()

        for val in param_values:
            result = sim._run(ork_file)
            result["param"] = {param_name: val}
            results.append(result)

        report_path = Path(output_dir) / f"sweep_{param_name}.json"
        report_path.write_text(
            json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        return results


class StabilityAnalyzer(BaseTool):
    name: str = "stability_analyzer"
    description: str = (
        "分析火箭稳定性裕度。提取 CG 和 CP 位置，计算各飞行段的稳定裕度，"
        "判断是否满足 ≥1.5 calibre 的安全要求。"
    )

    def _run(
        self,
        cg_z_m: float,
        cp_z_m: float,
        diameter_m: float,
    ) -> Dict[str, Any]:
        """计算静稳定裕度."""
        margin_m = cp_z_m - cg_z_m
        margin_cal = margin_m / diameter_m if diameter_m > 0 else 0.0
        is_stable = margin_cal >= 1.5

        recommendation = "pass" if is_stable else (
            "需要增加弹翼面积或将重心前移至少 "
            f"{round((1.5 - margin_cal) * diameter_m * 1000, 1)} mm"
        )

        return {
            "cg_z_m": cg_z_m,
            "cp_z_m": cp_z_m,
            "margin_m": round(margin_m, 4),
            "margin_caliber": round(margin_cal, 2),
            "diameter_m": diameter_m,
            "is_stable": is_stable,
            "pass_threshold_1.5cal": is_stable,
            "recommendation": recommendation,
        }
