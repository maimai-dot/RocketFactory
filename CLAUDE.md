# CLAUDE.md — 火箭工厂 (RocketFactory)

> AI 智能体团队设计可回收火箭。所有技术决策以"最终建成实物"为唯一目标。  
> "不行"是非法词汇，只能转换为"需要解决的技术问题清单"。

## 项目定位

建造人类第一枚完全由 AI 智能体团队设计的可回收火箭 —— 1 公里级验证箭，6 个月内用民用材料实现。

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 智能体框架 | **Σ (Sigma)** AERC 多智能体协同框架 (`sigma-aerc`) | A→E→R→C 循环 + 交叉审查 + 收敛判断 |
| LLM | DeepSeek V4 Pro（OpenAI 兼容 API） | 所有智能体的大脑 |
| 3D 建模 | FreeCAD 1.0+ | Python API / `freecadcmd` 命令行 |
| 飞行仿真 | OpenRocket 23.09+ | `java -jar` CLI 调用 |
| 推进剂分析 | NASA CEA → Python `rocketcea` | 燃烧性能计算 |
| 数据处理 | numpy, pandas, matplotlib, scipy | 仿真后处理与可视化 |

> Σ 框架已独立发布为 `sigma-aerc` PyPI 包（v0.1.0, 985 tests, AGPLv3）。  
> `pip install sigma-aerc` → `import sigma`。已彻底解耦 CrewAI。

## 目录结构

```
RocketFactory/
├── CLAUDE.md                   # 本文件
├── PROJECT_RULES.md            # 项目宪法（一切的根本）
├── main.py                     # 入口：python main.py "指令"
├── framework/                  # Σ AERC 多智能体协同框架
│   ├── __init__.py             # 公共 API 导出
│   ├── protocol.py             # AERC 协议引擎（核心）
│   ├── orchestrator.py         # 循环调度 + Founder 交互 + 报告生成
│   ├── state.py                # 三层共享状态 + ConsensusEstimate
│   ├── convergence.py          # 收敛判断 + 振荡检测 + 物理不可能检查
│   ├── triggers.py             # 事件驱动触发器（知识缺口/工具异常/数据偏差）
│   ├── cost_tracker.py         # Token 成本追踪
│   ├── replay.py               # 回放测试模式
│   └── _crewai_compat.py       # CrewAI 兼容层（让 agents/ 和 tools/ 无需真实 CrewAI）
├── agents/                     # 8 个火箭工程师智能体定义
│   ├── director.py             # 任务总监
│   ├── propulsion_chief.py     # 推进总工
│   ├── structures_chief.py     # 结构总工（FreeCAD 工具）
│   ├── gnc_chief.py            # 飞控总工
│   ├── sim_chief.py            # 仿真主任（OpenRocket 工具）
│   ├── supply_agent.py         # 采购与供应链
│   ├── safety_officer.py       # 法规与安全
│   └── skill_crafter.py        # 技能工匠（网络搜索 + 技能生成）
├── tools/                      # 工具模块
│   ├── rocketcea_tools.py      # NASA CEA 推进剂分析
│   ├── freecad_tools.py        # FreeCAD 建模 + 质量提取
│   ├── openrocket_tools.py     # OpenRocket 仿真 + 参数扫描 + 稳定性
│   ├── skill_creator_tool.py   # 技能文件生成 + 知识缺口检测
│   ├── web_search_tool.py      # 四源搜索 + 信源评估
│   ├── mission_control.py      # 任务控制台（终端 UI）
│   └── complexity_monitor.py   # 架构演进监控
├── skills/                     # 专业技能 .md 文件 + generated/
├── output/                     # 所有任务产出
│   ├── INDEX.md                # 自动生成的产出索引
│   └── v{N}/                   # 版本化产出
│       ├── REPORT.md           # 完整可读报告
│       ├── result.json         # 结构化元数据
│       └── round_{N}/          # 每轮详细记录
└── tests/                      # 测试（目标 ≥80% 覆盖）
```

## 关键命令

```bash
python main.py "你的任务指令"    # 执行任务（Σ AERC 循环）
python main.py -y "指令"         # 非交互模式（跳过每轮确认）
python main.py --list            # 列出历史产出（秒出）
python main.py --view v11        # 查看报告全文
python main.py --index           # 重建产出索引
```

## Σ 框架协作架构

```
Founder (你)
  │
  ▼
┌─────────── AERC 循环 ──────────┐
│  A (Analyze)  — 多角色并行独立分析 + 交叉审查    │
│  E (Execute)  — 并行工具调用（function calling + 文本标记 fallback）│
│  R (Review)   — 数据驱动的跨角色审查 + 魔鬼代言人  │
│  C (Converge) — 收敛判断 + 共识估算 + 知识沉淀    │
└────────────────────────────────┘
  │
  ▼
  REPORT.md + result.json
```

**Σ 核心机制：**
- **交叉审查**：多个角色先独立分析（互不可见），然后互相审查——v11 实测证明了多角色能独立发现数据异常
- **魔鬼代言人**：安全官每轮从最坏情况审视方案，拥有一票否决权
- **共识估算**：当工具数据不可靠时，多角色独立估算 → 互相审视 → 收敛为共识范围（带置信度）
- **收敛判断**：数值变化 <5% + 无新定性冲突 → 收敛；连续振荡 → 停车；大规模 LLM 失败 → 中止（verdict="error"）；4 轮硬上限
- **Skill Crafter**：检测到知识缺口 → 搜索 → 生成技能文件，下一轮注入相关角色
- **复杂度自适应**：纯规则引擎评估任务复杂度（0-10分），自动选择 LITE/STANDARD/RIGOROUS 三层：
  - LITE (≤2.5分)：Director + 2-3个最相关领域角色，1轮，无交叉审查/魔鬼代言人/共识估算
  - STANDARD (≤6.0分)：6核角色，≤3轮，有交叉审查，无魔鬼代言人
  - RIGOROUS (>6.0分)：全部8角色，≤4轮，完整交叉审查+魔鬼代言人+共识估算+Skill Crafter
- **OpenAI Function Calling**：工具调用优先使用原生 function calling（LLM 动态选择参数），fallback 文本标记 `[需要工具: xxx]`
- **大规模 LLM 失败检测**：P 阶段后自动检测，≥50% 智能体返回错误 → 立即中止，防止假收敛

**9 个智能体角色：**

| 角色 | 职责 | 核心工具 |
|------|------|---------|
| Director | 任务拆解、系统工程视角 | — |
| Propulsion Chief | 推进剂、发动机、推力曲线 | rocketcea_analyzer, propellant_comparator |
| Structures Chief | 箭体结构、质量、强度 | freecad_model_builder, freecad_mass_extractor |
| GNC Chief | 飞控、传感器、航电 | — |
| Sim Chief | 气动、弹道、飞行仿真 | openrocket_sim_runner, openrocket_param_sweep, stability_analyzer |
| Supply Agent | 采购、BOM、供应链 | — |
| Safety Officer | 法规、安全评审、魔鬼代言人 | — |
| Skill Crafter | 知识缺口 → 搜索 → 技能文件 | skill_creator, knowledge_gap_detector, web_search, source_evaluator |

每个角色有独立的 `role`、`goal`、`backstory`、`skill_files`、`tools`。

## 代码规范

- Python: PEP 8, 类型注解, 函数 < 50 行, 文件 < 800 行
- 不可变模式优先（`dataclass(frozen=True)`, `NamedTuple`）
- 所有错误显式处理，禁止静默吞异常
- 提交格式: `feat: / fix: / refactor: / test: / chore:`
- 测试覆盖率 ≥ 80%

## 外部工具（已安装 ✅）

| 工具 | 版本 | 路径 | 状态 |
|------|------|------|:--:|
| Java OpenJDK | 17.0.19 LTS | `C:\Program Files\Microsoft\jdk-17.0.19.10-hotspot` | ✅ |
| FreeCAD | 1.1.1 | `%LOCALAPPDATA%\Programs\FreeCAD 1.1\bin\freecadcmd.exe` | ✅ |
| OpenRocket | 23.09 | `C:\Program Files\OpenRocket\OpenRocket.jar` | ✅ (GUI) |
| rocketcea | 1.2.3 | pip (Python 3.14) | ✅ |
| matplotlib, scipy | latest | pip | ✅ |

**注意**: OpenRocket 23.09 为 GUI 应用，无原生 CLI 仿真接口。工具调用返回 simulated 标记，由共识估算补充。

## 进度

| 版本 | 框架 | 状态 | 产出 |
|------|------|:----:|------|
| v1 | CrewAI | ❌ | API 超时 |
| v4 | CrewAI | ✅ | KNSB vs LOX-乙醇 推进方案对比 |
| v10 | CrewAI | ✅ | KNSB 比冲 + 铝管质量（Isp≈183s 理论 [N2O/EtOH 近似，v20 修正为 158s]，工程 140-155s） |
| v11 | Σ (Sigma) | ✅ | 首次 Σ 端到端测试：3 轮收敛，8 角色识别数据异常，安全官否决 |
| v12 | Σ (Sigma) | ⬜ | 共识估算验证（Round 1 完成：mass_kg=5.15kg [MEDIUM]） |
| v15 | Σ (Sigma) | ✅ | 复杂度自适应系统：LITE(2角色/1轮/¥0.03) 端到端验证通过 |
| v16 | Σ (Sigma) | ✅ | PyPI 发布 `sigma-aerc` v0.1.0（包名 sigma→sigma-aerc 因重名） |
| v20 | Σ (Sigma) | ✅ | FreeCAD + KNSB 工具修复：真实 FreeCAD 建模正常，KNSB CEA 理论 Isp≈158s（原估算 183s 有误） |

**当前焦点**：
- ✅ 复杂度自适应系统已完成（2026-05-19）— 三层分层 + orchestrator 全集成
- ✅ Σ 框架从 RocketFactory 解耦为独立 pip 包（985 tests, `__version__`, `py.typed`, MANIFEST.in）
- ✅ OpenAI Function Calling 集成（2026-05-21）— `ToolSpec.to_openai_schema()` + `do()` function calling 优先
- ✅ 真实场景验证（2026-05-21）— 软件工程+医疗双场景，非花架子
- ✅ 3 个鲁棒性 bug 修复 — 大规模 LLM 失败检测 / `agent_analyses` 返回 / `reasoning_content` 收集
- ✅ 专利决策最终确定 — 不申请，走 arXiv + AGPLv3 + AERC 协议标准路线
- ✅ PyPI 发布（2026-05-22）— `sigma-aerc` v0.1.0 上线 https://pypi.org/project/sigma-aerc/
- ✅ 修复 freecad_mass_extractor（2026-05-23）— FreeCAD 1.1.1 实际可用，builder + extractor 均通过真实建模验证
- ✅ 补充 rocketcea 真实 KNSB 推进剂数据（2026-05-23）— CEA 计算理论 Isp=157.8s @50bar/eps6（非之前 183s 估算），工程实际 126-142s
- ✅ GitHub 开源（2026-05-23）— https://github.com/maimai-dot/RocketFactory, AGPLv3
- arXiv 防御性公开

## 信仰声明

> 我们正在建造人类第一枚完全由 AI 智能体团队设计的可回收火箭。  
> 没有预算，没有经验，但这与能否成功无关。  
> 所有障碍都将被第一性原理拆解，并转化为可在 6 个月内用民用材料实现的步骤。
