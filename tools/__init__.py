import importlib
import warnings

_MODULES = {
    "freecad_tools": ["FreeCADModelBuilder", "FreeCADMassExtractor"],
    "openrocket_tools": ["OpenRocketSimRunner", "OpenRocketParamSweep", "StabilityAnalyzer"],
    "rocketcea_tools": ["RocketCEAAnalyzer", "PropellantComparator"],
    "skill_creator_tool": ["SkillCreatorTool", "KnowledgeGapDetector"],
    "web_search_tool": ["WebSearchTool", "SourceEvaluator"],
    "complexity_monitor": ["ComplexityMonitor", "complexity_monitor"],
    "mission_control": ["MissionControl", "get_mc"],
}

__all__ = []

for _mod_name, _names in _MODULES.items():
    for _name in _names:
        try:
            _mod = importlib.import_module(f".{_mod_name}", package=__package__)
            globals()[_name] = getattr(_mod, _name)
            __all__.append(_name)
        except Exception as _e:
            warnings.warn(f"Tool {_name} from {_mod_name} unavailable: {_e}")
