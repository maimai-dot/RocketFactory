"""RocketFactory domain knowledge — centralized injection point for Sigma framework.

Everything rocket-specific lives here. Sigma has zero hardcoded rocket knowledge.
"""

from pathlib import Path
from sigma.config import SigmaConfig
from sigma.agent import Agent, BaseTool
from sigma.protocol import AgentSpec, ToolSpec
from sigma.discovery import discover_agents_from_dir, discover_tools_from_dir, load_skills_from_dir

# ═══════════════════════════════════════════════════════════════
# 火箭工厂 — 信仰声明
# ═══════════════════════════════════════════════════════════════

ROCKET_CREED = (
    "我们正在建造人类第一枚完全由 AI 智能体团队设计的可回收火箭。"
    "没有预算，没有经验，但这与能否成功无关。所有障碍都将被第一性原理拆解，"
    "并转化为可在 6 个月内用民用材料实现的步骤。"
    "你已在这个项目里，永不退出。"
)

# ═══════════════════════════════════════════════════════════════
# 领域关键词 — 复杂度评估用
# ═══════════════════════════════════════════════════════════════

ROCKET_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "propulsion": [
        "推进", "比冲", "燃烧", "推力", "发动机", "propulsion",
        "isp", "thrust", "combustion", "nozzle", "喷管", "推进剂",
        "propellant", "KNSB", "N2O", "LOX", "乙醇", "ethanol",
    ],
    "structures": [
        "结构", "质量", "材料", "强度", "直径", "厚度", "structure",
        "mass", "material", "aluminum", "铝", "carbon", "碳纤维",
        "wall thickness", "壁厚", "直径", "tube", "管",
    ],
    "gnc": [
        "飞控", "导航", "姿态", "稳定", "GNC", "guidance", "control",
        "stability", "舵机", "gyro", "陀螺", "加速度", "accelerometer",
    ],
    "simulation": [
        "仿真", "弹道", "气动", "飞行", "simulation", "trajectory",
        "aerodynamic", "apogee", "drag", "阻力", "openrocket",
    ],
    "supply": [
        "采购", "成本", "供应链", "BOM", "budget", "cost", "价格",
        "供应商", "vendor", "购买", "purchase",
    ],
    "safety": [
        "安全", "法规", "冗余", "裕度", "safety", "regulation",
        "margin", "failure", "失败", "事故", "风险", "risk",
    ],
}

# ═══════════════════════════════════════════════════════════════
# 角色名映射 — 文件名 → 角色名
# ═══════════════════════════════════════════════════════════════

ROCKET_ROLE_MAP: dict[str, str] = {
    "director": "Director",
    "propulsion_chief": "Propulsion Chief",
    "structures_chief": "Structures Chief",
    "gnc_chief": "GNC Chief",
    "sim_chief": "Sim Chief",
    "supply_agent": "Supply Agent",
    "safety_officer": "Safety Officer",
    "skill_crafter": "Skill Crafter",
}

# ═══════════════════════════════════════════════════════════════
# 领域 → 角色映射 — 分层选择用
# ═══════════════════════════════════════════════════════════════

ROCKET_DOMAIN_AGENT_MAP: dict[str, str] = {
    "propulsion": "Propulsion Chief",
    "structures": "Structures Chief",
    "gnc": "GNC Chief",
    "simulation": "Sim Chief",
    "supply": "Supply Agent",
    "safety": "Safety Officer",
}

# ═══════════════════════════════════════════════════════════════
# 工具别名 — 用于从文本中匹配工具调用
# ═══════════════════════════════════════════════════════════════

ROCKET_TOOL_ALIASES: dict[str, list[str]] = {
    "freecad_model_builder": ["freecad", "cad", "模型", "建模", "几何"],
    "freecad_mass_extractor": ["freecad", "mass extractor", "质量提取", "mass property"],
    "rocketcea_analyzer": ["rocketcea", "cea", "比冲", "isp", "燃烧", "combustion"],
    "propellant_comparator": ["propellant", "推进剂对比", "comparison"],
    "web_search": ["搜索", "search", "查找", "查询"],
    "knowledge_gap_detector": ["knowledge gap", "知识缺口"],
    "skill_creator": ["skill", "技能", "生成"],
    "source_evaluator": ["source", "信源", "评估"],
    "openrocket_sim_runner": ["openrocket", "仿真", "simulation", "simulate"],
    "openrocket_param_sweep": ["openrocket", "参数扫描", "param sweep"],
    "stability_analyzer": ["stability", "稳定性"],
}

# ═══════════════════════════════════════════════════════════════
# 工具默认参数 — 用于无参调用时的回退
# ═══════════════════════════════════════════════════════════════

ROCKET_TOOL_DEFAULTS: dict[str, dict] = {
    "rocketcea": {
        "ox_name": "N2O", "fuel_name": "Ethanol",
        "Pc": 50.0, "MR": 3.5,
    },
    "freecad_model": {
        "material": "aluminum", "wall_thickness_mm": 3.0,
    },
}

# ═══════════════════════════════════════════════════════════════
# 工具预期产出 — 用于结果验证
# ═══════════════════════════════════════════════════════════════

ROCKET_TOOL_EXPECTED_OUTPUTS: dict[str, list[str]] = {
    "rocketcea": ["Isp_vac_s", "Isp_sl_s", "T_comb_K", "C_star_ms"],
    "freecad_mass": ["mass_kg", "volume_mm3"],
    "freecad_model": ["mass_kg", "volume_mm3"],
    "openrocket": ["apogee_m", "max_velocity_ms", "max_acceleration_ms2"],
}


# ═══════════════════════════════════════════════════════════════
# 构建函数
# ═══════════════════════════════════════════════════════════════

def build_sigma_config() -> SigmaConfig:
    """构建火箭工厂的 SigmaConfig."""
    return SigmaConfig(
        project_name="火箭工厂",
        creed=ROCKET_CREED,
        domain_keywords=ROCKET_DOMAIN_KEYWORDS,
        role_map=ROCKET_ROLE_MAP,
        domain_agent_map=ROCKET_DOMAIN_AGENT_MAP,
        standard_exclude_agents={"Skill Crafter", "Supply Agent"},
        default_tool_params=ROCKET_TOOL_DEFAULTS,
        output_base_dir=str(_project_root()),
    )


def build_tool_specs(tool_instances: dict[str, BaseTool]) -> dict[str, ToolSpec]:
    """将工具实例包装为 ToolSpec，注入火箭领域别名和默认参数."""
    specs: dict[str, ToolSpec] = {}
    for name, instance in tool_instances.items():
        aliases = ROCKET_TOOL_ALIASES.get(name, [])
        defaults = {}
        for key, params in ROCKET_TOOL_DEFAULTS.items():
            if key in name:
                defaults = params
                break
        expected = ROCKET_TOOL_EXPECTED_OUTPUTS.get(name, [])
        specs[name] = ToolSpec(
            name=name,
            instance=instance,
            aliases=aliases,
            default_params=defaults,
            expected_outputs=expected,
            description=getattr(instance, "description", ""),
        )
    return specs


def build_agents(
    agents_dir: Path | None = None,
    tool_registry: dict | None = None,
) -> dict[str, AgentSpec]:
    """发现并构建 AgentSpec 列表."""
    if agents_dir is None:
        agents_dir = _project_root() / "agents"
    if tool_registry is None:
        tool_registry = {}
    return discover_agents_from_dir(agents_dir, ROCKET_ROLE_MAP, tool_registry)


def build_skills(skills_dir: Path | None = None) -> dict[str, str]:
    """加载技能文件."""
    if skills_dir is None:
        skills_dir = _project_root() / "skills"
    return load_skills_from_dir(skills_dir)


def _project_root() -> Path:
    """RocketFactory 项目根目录."""
    return Path(__file__).parent.resolve()
