"""
复杂度监控工具
持续检测任务复杂度，在满足触发条件时发出架构升级信号（Sigma → LangGraph）。
仅 Director 智能体挂载此工具。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import ClassVar, Dict, Any, List, Optional

from sigma import BaseTool


class ComplexityMonitor(BaseTool):
    name: str = "complexity_monitor"
    description: str = (
        "监控当前任务复杂度，检测架构升级触发条件。"
        "每次 Director 分配任务后调用此工具记录并评估复杂度指标。"
        "输入: action(record|report|check), metrics(dict)"
    )

    # 触发阈值（来自 PROJECT_RULES.md 第 5 节）
    THRESHOLDS: ClassVar[Dict[str, Dict[str, int]]] = {
        "parallel_tasks": {"warn": 10, "critical": 20},
        "iteration_loops": {"warn": 1, "critical": 3},
        "workflow_depth": {"warn": 5, "critical": 10},
        "state_variables": {"warn": 20, "critical": 50},
    }

    _history: ClassVar[List[Dict[str, Any]]] = []
    _log_path: ClassVar[Path] = Path("output/complexity_log.json")

    def _run(
        self,
        action: str = "record",
        metrics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """记录或检查复杂度指标."""
        if action == "record" and metrics:
            return self._record(metrics)
        elif action == "report":
            return self._generate_report()
        elif action == "check":
            return self._check_triggers(metrics or {})
        else:
            return self._check_triggers(self._latest_metrics())

    def _record(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """记录一次复杂度快照."""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
        }
        self._history.append(snapshot)
        self._persist()
        return self._check_triggers(metrics)

    def _check_triggers(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """检查是否触发架构升级条件."""
        alerts = []
        should_upgrade = False

        for metric, thresholds in self.THRESHOLDS.items():
            value = metrics.get(metric, 0)
            if isinstance(value, (int, float)):
                if value >= thresholds["critical"]:
                    alerts.append({
                        "metric": metric,
                        "value": value,
                        "threshold": thresholds["critical"],
                        "severity": "CRITICAL",
                        "message": f"{metric} 超过严重阈值 {thresholds['critical']} (当前: {value})",
                    })
                    should_upgrade = True
                elif value >= thresholds["warn"]:
                    alerts.append({
                        "metric": metric,
                        "value": value,
                        "threshold": thresholds["warn"],
                        "severity": "WARNING",
                        "message": f"{metric} 超过警告阈值 {thresholds['warn']} (当前: {value})",
                    })

        result = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "alerts": alerts,
            "should_upgrade": should_upgrade,
            "recommendation": self._upgrade_recommendation(should_upgrade, alerts),
            "upgrade_conditions_met": [
                {
                    "condition": "并行子任务数 > 20",
                    "met": metrics.get("parallel_tasks", 0) >= 20,
                },
                {
                    "condition": "设计迭代循环 > 3",
                    "met": metrics.get("iteration_loops", 0) >= 3,
                },
                {
                    "condition": "工作流深度 > 10",
                    "met": metrics.get("workflow_depth", 0) >= 10,
                },
                {
                    "condition": "状态变量数 > 50",
                    "met": metrics.get("state_variables", 0) >= 50,
                },
                {
                    "condition": "实物试验阶段开始",
                    "met": metrics.get("hardware_phase", False),
                },
            ],
        }
        return result

    def _generate_report(self) -> Dict[str, Any]:
        """生成历史复杂度报告."""
        if not self._history:
            return {"message": "尚无复杂度监控数据"}

        latest = self._history[-1]
        return {
            "total_snapshots": len(self._history),
            "latest": latest,
            "trend": self._compute_trend(),
            "history": self._history[-10:],
        }

    def _compute_trend(self) -> str:
        """计算复杂度趋势."""
        if len(self._history) < 2:
            return "stable"
        recent = self._history[-5:] if len(self._history) >= 5 else self._history
        tasks = [s["metrics"].get("parallel_tasks", 0) for s in recent]
        if len(tasks) >= 2:
            if tasks[-1] > tasks[0] * 1.5:
                return "increasing"
            elif tasks[-1] < tasks[0] * 0.7:
                return "decreasing"
        return "stable"

    def _upgrade_recommendation(
        self, should_upgrade: bool, alerts: List[Dict]
    ) -> str:
        """生成升级建议."""
        if not should_upgrade:
            return "no_action — 当前架构满足需求"
        criticals = [a for a in alerts if a["severity"] == "CRITICAL"]
        if criticals:
            return (
                f"RECOMMEND_UPGRADE — {len(criticals)} 个 CRITICAL 指标触发: "
                + "; ".join(a["metric"] for a in criticals)
                + "。建议向 Founder 提交 LangGraph 迁移提案。"
            )
        return (
            "MONITOR — WARNING 级别指标出现，继续观察。"
            "如趋势持续恶化，应准备 LangGraph 迁移方案。"
        )

    def _latest_metrics(self) -> Dict[str, Any]:
        """获取最近一次指标."""
        if self._history:
            return self._history[-1]["metrics"]
        return {}

    def _persist(self) -> None:
        """持久化到日志文件."""
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        self._log_path.write_text(
            json.dumps(self._history, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )


# 模块级实例（单例模式，跨调用保持 history）
complexity_monitor = ComplexityMonitor()
