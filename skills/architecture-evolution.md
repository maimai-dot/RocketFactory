---
name: architecture-evolution
description: CrewAI到LangGraph架构迁移策略、复杂度监控指标、状态图设计与检查点机制
---

## 架构演进路线图

### 阶段 0：CrewAI 快速原型（当前）
- 目标：验证多智能体协作可行性，产出第一版数字样机
- 特点：层级管理、线性任务流、隐式状态
- 适用：概念设计、初步仿真、方案选型

### 阶段 1：混合架构过渡
- 触发：复杂度监控首次报警（并行任务 > 20 或出现设计迭代循环）
- 策略：核心设计循环用 LangGraph 管理，外围任务仍用 CrewAI
- 保持所有 Agent 定义和 Skill 文件不变

### 阶段 2：全量 LangGraph 迁移
- 触发：阶段 1 稳定运行 2 周，且实物试验阶段开始
- 策略：完整迁移到 LangGraph StateGraph，启用检查点和人工干预
- 包含：审计跟踪、人类确认节点、多轮设计优化闭环

## 复杂度监控指标

### 监控维度
| 指标 | 当前阈值 | 警告阈值 | 严重阈值 | 采集方式 |
|------|----------|----------|----------|----------|
| 并行子任务数 | < 10 | 10-20 | > 20 | Director 任务分配计数 |
| 设计迭代循环数 | 0 | 1-3 | > 3 | 同一子任务执行历史 |
| 工作流深度 | < 5 | 5-10 | > 10 | DAG 最长路径分析 |
| 状态变量数 | < 20 | 20-50 | > 50 | 全局状态字典键计数 |
| 人工介入频率 | 低 | 中 | 高 | Founder 干预日志 |

### 监控数据输出格式
```json
{
  "timestamp": "2026-05-17T10:00:00",
  "metrics": {
    "parallel_tasks": 8,
    "iteration_loops": 1,
    "workflow_depth": 4,
    "state_variables": 15,
    "human_interventions": 2
  },
  "alerts": [],
  "recommendation": "no_action"
}
```

## LangGraph StateGraph 设计模式

### 核心状态结构
```python
from typing import TypedDict, List, Dict, Any

class RocketDesignState(TypedDict):
    # 任务管理
    task_queue: List[Dict]
    completed_tasks: List[Dict]
    current_phase: str

    # 设计数据
    design_parameters: Dict[str, float]
    cad_files: List[str]
    simulation_results: Dict[str, Any]

    # 通信
    messages: List[Dict]
    director_decisions: List[Dict]

    # 审计
    checkpoint_id: str
    execution_trace: List[Dict]
```

### 关键节点定义
```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(RocketDesignState)

# 核心节点
workflow.add_node("director_plan", director_plan_node)
workflow.add_node("propulsion_design", propulsion_node)
workflow.add_node("structures_design", structures_node)
workflow.add_node("gnc_design", gnc_node)
workflow.add_node("simulation_run", simulation_node)
workflow.add_node("safety_review", safety_review_node)
workflow.add_node("skill_crafting", skill_crafting_node)
workflow.add_node("founder_review", founder_review_node)
```

### 条件边（设计优化闭环）
```python
def should_iterate(state: RocketDesignState) -> str:
    sim_results = state["simulation_results"]
    if sim_results.get("stability_margin", 0) < 1.5:
        return "structures_design"  # 重新设计
    if sim_results.get("apogee_error", 0) > 0.1:
        return "propulsion_design"
    if sim_results.get("landing_error", 0) > 10:
        return "gnc_design"
    return "founder_review"

workflow.add_conditional_edges(
    "simulation_run",
    should_iterate,
    {
        "structures_design": "structures_design",
        "propulsion_design": "propulsion_design",
        "gnc_design": "gnc_design",
        "founder_review": "founder_review",
    }
)
```

### 检查点机制
```python
from langgraph.checkpoint.sqlite import SqliteSaver

# SQLite 持久化检查点，支持暂停/恢复和审计
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
app = workflow.compile(checkpointer=checkpointer)
```

## 迁移检查清单

### 迁移前
- [ ] 所有 9 个 Agent 定义文件完整且通过单元测试
- [ ] 所有 Skill 文件版本已锁定
- [ ] CrewAI 最后一版运行日志已保存
- [ ] 现有设计数据已备份

### 迁移中
- [ ] Agent system_message 保持不变
- [ ] Skill 文件路径映射不变
- [ ] 工具函数封装层不变
- [ ] 任务分配格式保持一致

### 迁移后
- [ ] 回归测试：所有智能体响应质量不下降
- [ ] 新增检查点恢复测试
- [ ] 新增设计优化闭环测试（仿真→修改→再仿真）
- [ ] Founder 审批节点功能验证
