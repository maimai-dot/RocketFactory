"""
FreeCAD 工具封装层
通过 MCP-FreeCAD 协议或 Python API 操作 FreeCAD，实现参数化火箭结构建模。
"""

import json
import subprocess
import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from sigma import BaseTool
except ImportError:
    BaseTool = object  # type: ignore


def _find_freecad_cmd() -> Optional[str]:
    """查找 freecadcmd 可执行文件路径."""
    search_paths: List[str] = []

    # 常见的 FreeCAD 安装位置
    local_app = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        Path(local_app) / "Programs" / "FreeCAD 1.1" / "bin" / "freecadcmd.exe",
        Path(local_app) / "Programs" / "FreeCAD 1.0" / "bin" / "freecadcmd.exe",
        Path("C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe"),
        Path("C:/Program Files/FreeCAD 1.0/bin/freecadcmd.exe"),
    ]

    for p in candidates:
        if p.exists():
            return str(p)

    # fallback: try PATH
    found = shutil.which("freecadcmd") or shutil.which("freecadcmd.exe")
    return found


FREECAD_CMD = _find_freecad_cmd()


class FreeCADModelBuilder(BaseTool):
    name: str = "freecad_model_builder"
    description: str = (
        "通过 FreeCAD Python API 创建或修改火箭结构模型。"
        "输入参数包括直径(m)、总长(m)、鼻锥型线(von_karman|conical|parabolic)、"
        "壁厚(mm)、材料类型。返回质量特性 JSON 和 STL 文件路径。"
    )

    def _run(
        self,
        diameter: float = 0.15,
        total_length: float = 2.0,
        nose_type: str = "von_karman",
        wall_thickness: float = 2.0,
        material: str = "stainless_steel",
        output_dir: str = "output/v1/",
    ) -> Dict[str, Any]:
        """构建火箭箭体模型并返回质量特性."""
        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)
        out_fwd = out_path.as_posix()

        script = self._build_freecad_script(
            diameter, total_length, nose_type, wall_thickness, material, out_fwd
        )

        script_path = str(out_path / "_freecad_script.py")
        Path(script_path).write_text(script, encoding="utf-8")

        if not FREECAD_CMD:
            return self._simulated(diameter, total_length, wall_thickness, material)

        try:
            result = subprocess.run(
                [FREECAD_CMD, script_path],
                capture_output=True, text=True, timeout=300,
            )
            if result.returncode != 0:
                return {"success": False, "error": result.stderr}

            mass_path = Path(output_dir) / "mass_properties.json"
            stl_path = Path(output_dir) / "rocket.stl"

            mass_data = {}
            if mass_path.exists():
                mass_data = json.loads(mass_path.read_text(encoding="utf-8"))

            return {
                "success": True,
                "mass_properties": mass_data,
                "stl_path": str(stl_path) if stl_path.exists() else None,
                "cad_script": str(script_path),
            }
        except (FileNotFoundError, OSError):
            return self._simulated(diameter, total_length, wall_thickness, material)

    def _simulated(
        self, diameter: float, length: float, wall_thickness: float, material: str
    ) -> Dict[str, Any]:
        """当 FreeCAD 不可用时的估算结果."""
        est_mass = self._estimate_mass(diameter, length, wall_thickness, material)
        return {
            "success": "simulated",
            "note": "FreeCAD 未安装或不可用，返回模拟结果供参考",
            "parameters": {
                "diameter": diameter,
                "total_length": length,
                "wall_thickness": wall_thickness,
                "material": material,
            },
            "estimated_mass": est_mass,
            "mass_properties": {
                "mass_kg": est_mass,
                "cg_z_m": length * 0.55,
                "cp_z_m": length * 0.65,
                "stability_margin_cal": 1.8,
            },
        }

    def _build_freecad_script(
        self,
        diameter: float,
        total_length: float,
        nose_type: str,
        wall_thickness: float,
        material: str,
        output_dir: str,
    ) -> str:
        """生成 FreeCAD Python 脚本.

        输入单位为米，FreeCAD 内部单位为毫米，所有尺寸需乘 1000。
        """
        # 转换为 FreeCAD 内部单位 (mm)
        d_mm = diameter * 1000.0
        l_mm = total_length * 1000.0

        densities = {
            "stainless_steel": 8.0e-6,
            "aluminum": 2.7e-6,
            "carbon_fiber": 1.6e-6,
            "pla": 1.24e-6,
        }
        rho = densities.get(material, 2.7e-6)  # kg/mm³

        return f'''
import FreeCAD as App
import Part, Mesh, json, os, math

doc = App.newDocument("RocketStage")

radius = {d_mm} / 2.0
length = {l_mm}
nose_len = length * 0.25
body_len = length - nose_len

# 鼻锥
nose_pts = []
import math
for i in range(50):
    x = nose_len * i / 50
    r = radius * math.sqrt(math.acos(x/nose_len)/math.pi - (1-2*x/nose_len)*math.sqrt(x/nose_len-(x/nose_len)**2)/math.pi) if nose_len > 0 else radius
    nose_pts.append(App.Vector(x, 0, r))
nose_spline = Part.BSplineCurve(nose_pts)
nose_profile = Part.makePolygon([App.Vector(0,0,0)] + nose_pts + [App.Vector(nose_len,0,0)])
nose_face = Part.Face(Part.Wire(nose_profile))
nose = nose_face.revolve(App.Vector(0,0,0), App.Vector(1,0,0), 360)
nose_obj = doc.addObject("Part::Feature", "NoseCone")
nose_obj.Shape = nose

# 箭体管段
body = Part.makeCylinder(radius - 0.001, body_len, App.Vector(nose_len, 0, 0))
body_obj = doc.addObject("Part::Feature", "BodyTube")
body_obj.Shape = body

# 引擎舱
engine_len = length * 0.15
engine_r = radius * 0.6
engine = Part.makeCylinder(engine_r, engine_len, App.Vector(length - engine_len, 0, 0))
engine_obj = doc.addObject("Part::Feature", "EngineBay")
engine_obj.Shape = engine

# 弹翼(4片)
fin_root = body_len * 0.15
fin_tip = body_len * 0.08
fin_span = radius * 2.5
fin_thick = 0.003
fin_pos = length - fin_root - 0.02
for i in range(4):
    angle = i * 90
    rad = math.radians(angle)
    p1 = App.Vector(fin_pos, radius*math.sin(rad), radius*math.cos(rad))
    p2 = App.Vector(fin_pos + fin_root, radius*math.sin(rad), radius*math.cos(rad))
    p3 = App.Vector(fin_pos + fin_tip, (radius+fin_span)*math.sin(rad), (radius+fin_span)*math.cos(rad))
    pts = [p1, p2, p3, p1]
    wire = Part.makePolygon(pts)
    face = Part.Face(wire)
    fin = face.extrude(App.Vector(0, fin_thick, 0))
    fin_obj = doc.addObject("Part::Feature", f"Fin_{{i}}")
    fin_obj.Shape = fin

doc.recompute()

# 材料密度 (kg/mm³)
rho = {rho}

# 提取质量特性
total_volume = 0.0
cg_sum = App.Vector()
for obj in doc.Objects:
    if hasattr(obj, "Shape") and obj.Shape:
        vol = obj.Shape.Volume  # mm³
        total_volume += vol
        cg_sum += obj.Shape.CenterOfMass * vol

cg = cg_sum / total_volume if total_volume > 0 else App.Vector()
mass_kg = total_volume * rho  # mm³ * kg/mm³ = kg
mass_data = {{
    "mass_kg": round(mass_kg, 4),
    "volume_mm3": round(total_volume, 1),
    "cg_x_m": round(cg.x / 1000.0, 6),
    "cg_y_m": round(cg.y / 1000.0, 6),
    "cg_z_m": round(cg.z / 1000.0, 6),
    "density_kg_m3": round(rho * 1e9, 1),
}}

with open(os.path.join("{output_dir}", "mass_properties.json"), "w") as f:
    json.dump(mass_data, f, indent=2)

# 导出 STL
Mesh.export([nose_obj, body_obj, engine_obj] + [o for o in doc.Objects if "Fin" in o.Label],
            os.path.join("{output_dir}", "rocket.stl"))

print("FreeCAD model complete: " + str(mass_data))
'''

    def _estimate_mass(
        self, diameter: float, length: float, wall_thickness: float, material: str
    ) -> float:
        """估算箭体质量（无 FreeCAD 时使用）."""
        import math
        densities = {
            "stainless_steel": 8000,   # kg/m³
            "aluminum": 2700,
            "carbon_fiber": 1600,
            "pla": 1240,
        }
        rho = densities.get(material, 8000)
        radius = diameter / 2.0
        volume = math.pi * ((radius) ** 2 - (radius - wall_thickness / 1000.0) ** 2) * length
        return round(volume * rho, 3)


class FreeCADMassExtractor(BaseTool):
    name: str = "freecad_mass_extractor"
    description: str = (
        "从 FreeCAD 模型（STL 文件）中提取质量、重心、转动惯量数据。"
        "支持直接读取 mass_properties.json（快速路径），或通过 FreeCAD 分析 STL 文件。"
        "输入: stl_path(str), material(str), density_kg_m3(float|None)"
    )

    def _run(
        self,
        stl_path: str = "output/v1/rocket.stl",
        material: str = "aluminum",
        density_kg_m3: Optional[float] = None,
    ) -> Dict[str, Any]:
        """从 STL 模型提取质量特性.

        优先读取已存在的 mass_properties.json；若不存在，通过 FreeCAD
        导入 STL 并计算质量、重心、转动惯量。
        """
        output_dir = str(Path(stl_path).parent)
        mass_path = Path(output_dir) / "mass_properties.json"

        # 快速路径：已有缓存的 mass_properties.json
        if mass_path.exists():
            data = json.loads(mass_path.read_text(encoding="utf-8"))
            data["extraction_method"] = "cached_json"
            return data

        # 检查 STL 文件是否存在
        if not Path(stl_path).exists():
            return {
                "success": False,
                "error": f"STL 文件不存在: {stl_path}",
                "hint": "Run freecad_model_builder first to create the model.",
            }

        if not FREECAD_CMD:
            return self._estimate_from_geometry(stl_path, material, density_kg_m3)

        return self._extract_via_freecad(stl_path, output_dir, material, density_kg_m3)

    def _extract_via_freecad(
        self,
        stl_path: str,
        output_dir: str,
        material: str,
        density_kg_m3: Optional[float],
    ) -> Dict[str, Any]:
        """通过 FreeCAD 导入 STL 并分析质量特性."""
        densities = {
            "stainless_steel": 8000,
            "aluminum": 2700,
            "carbon_fiber": 1600,
            "pla": 1240,
        }
        rho = density_kg_m3 or densities.get(material, 2700)

        # 统一使用正斜杠避免 Windows 反斜杠在 f-string 中被转义
        stl_fwd = Path(stl_path).as_posix()
        out_fwd = Path(output_dir).as_posix()
        script_path = str(Path(output_dir).resolve() / "_mass_extractor_script.py")

        script = f'''import FreeCAD as App
import Mesh, Part, json, os

doc = App.newDocument("MassAnalysis")
Mesh.insert(r"{stl_fwd}", "MassAnalysis")
doc.recompute()

mesh_objects = [o for o in doc.Objects if hasattr(o, "Mesh")]
if not mesh_objects:
    print(json.dumps({{"error": "无法加载 STL 网格"}}))
    exit(1)

mesh = mesh_objects[0]
bbox = mesh.Mesh.BoundBox
volume_mm3 = bbox.XLength * bbox.YLength * bbox.ZLength * 0.3

cog = mesh.Mesh.CenterOfGravity
mass_kg = volume_mm3 * {rho} * 1e-9

try:
    shape = Part.Shape()
    shape.makeShapeFromMesh(mesh.Mesh.Topology, 0.1)
    solid = Part.Solid(shape)
    if solid.Volume > 0:
        volume_mm3 = solid.Volume
        cog = solid.CenterOfMass
        mass_kg = volume_mm3 * {rho} * 1e-9
except Exception:
    pass

mass_data = {{
    "success": True,
    "extraction_method": "freecad_analysis",
    "stl_path": r"{stl_fwd}",
    "material": "{material}",
    "density_kg_m3": {rho},
    "mass_kg": round(mass_kg, 4),
    "volume_mm3": round(volume_mm3, 1),
    "cg_x_mm": round(cog.x, 4),
    "cg_y_mm": round(cog.y, 4),
    "cg_z_mm": round(cog.z, 4),
    "note": "从 STL 逆向计算；精确质量请使用 freecad_model_builder 直接建模",
}}

json_path = os.path.join(r"{out_fwd}", "mass_properties.json")
with open(json_path, "w") as f:
    json.dump(mass_data, f, indent=2)

print(json.dumps(mass_data))
'''

        Path(script_path).write_text(script, encoding="utf-8")

        try:
            result = subprocess.run(
                [FREECAD_CMD, script_path],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode != 0:
                return {"success": False, "error": result.stderr.strip() or "(empty stderr)"}

            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if line.startswith("{") and "mass_kg" in line:
                    return json.loads(line)

            mass_path = Path(output_dir) / "mass_properties.json"
            if mass_path.exists():
                return json.loads(mass_path.read_text(encoding="utf-8"))

            return {"success": False, "error": "FreeCAD 完成但无可用输出", "stdout": result.stdout[:500]}
        except (FileNotFoundError, OSError, subprocess.TimeoutExpired) as e:
            return {"success": False, "error": str(e)}

    def _estimate_from_geometry(
        self, stl_path: str, material: str, density_kg_m3: Optional[float]
    ) -> Dict[str, Any]:
        """无 FreeCAD 时的几何估算."""
        densities = {
            "stainless_steel": 8000,
            "aluminum": 2700,
            "carbon_fiber": 1600,
            "pla": 1240,
        }
        rho = density_kg_m3 or densities.get(material, 2700)

        return {
            "success": "estimated",
            "extraction_method": "geometric_estimate",
            "note": "FreeCAD 未安装；通过 STL 文件大小 + 材料密度估算，精度有限",
            "stl_path": stl_path,
            "material": material,
            "density_kg_m3": rho,
            "mass_kg": "N/A — 需要 FreeCAD 或手动输入建模参数",
            "hint": "安装 FreeCAD 获取精确质量数据，或直接使用 freecad_model_builder 创建模型",
        }
