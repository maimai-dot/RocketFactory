"""
NASA CEA 推进剂分析工具封装
通过 rocketcea Python 库计算燃烧性能、比冲、推力系数等。
支持液体双组元推进剂 + KNSB 固体推进剂。
"""

from typing import Dict, Any, Optional, List

try:
    from rocketcea.cea_obj import CEA_Obj
    HAS_ROCKETCEA = True
except ImportError:
    HAS_ROCKETCEA = False

try:
    from sigma import BaseTool
except ImportError:
    BaseTool = object  # type: ignore

# ============================================================================
# KNSB 固体推进剂卡片注册
# 65% KNO3 (硝酸钾) + 35% Sorbitol (山梨醇 C6H14O6)
# ============================================================================
KNSB_CARD = {
    "name": "KNSB",
    "composition": "KNO3 65% + Sorbitol 35%",
    "density_g_cc": 1.80,
    "formula": "K 0.6429 N 0.6429 O 3.0816 C 1.1528 H 2.6898",
    "h_cal": -138104.0,
}

# KNSB CEA 验证数据 (Pc=30-70 bar, eps=4-8)
KNSB_CEA_BENCHMARKS = {
    "Pc50_eps6": {
        "Isp_vac_s": 157.8,
        "Isp_real_est_s": "135-142 (工程实际, 理论值的 85-90%)",
        "T_comb_K": 2713,
        "C_star_ms": 2958.3,
        "Molar_mass_gmol": 34.93,
        "Gamma": 1.1137,
    },
    "Pc50_eps4": {"Isp_vac_s": 150.3, "T_comb_K": 2713},
    "Pc50_eps8": {"Isp_vac_s": 162.6, "T_comb_K": 2713},
    "Pc30_eps6": {"Isp_vac_s": 157.4, "T_comb_K": 2667},
    "Pc70_eps6": {"Isp_vac_s": 158.0, "T_comb_K": 2742},
}


def _register_knsb():
    """将 KNSB 推进剂卡片注册到 rocketcea 的 propCards 中."""
    if not HAS_ROCKETCEA:
        return False
    try:
        from rocketcea import input_cards
        if "KNSB" not in input_cards.propCards:
            input_cards.propCards["KNSB"] = [
                f' name KNSB {KNSB_CARD["formula"]} wt%=100.00 ',
                f' h,cal={KNSB_CARD["h_cal"]} t(k)=298.15 rho.g/cc={KNSB_CARD["density_g_cc"]} ',
            ]
        return True
    except Exception:
        return False


KNSB_REGISTERED = _register_knsb()


class RocketCEAAnalyzer(BaseTool):
    name: str = "rocketcea_analyzer"
    description: str = (
        "NASA CEA 燃烧性能分析。计算推进剂组合的比冲(Isp)、燃烧温度、"
        "特征速度(C*)、推力系数(Cf)等核心参数。"
        "支持液体双组元: ox_name + fuel_name (如 ox='LOX', fuel='LH2')"
        "支持单组元/固体推进剂: prop_name='KNSB'"
        "KNSB 采用 CEA 真实计算 (65% KNO3 + 35% Sorbitol, 理论 Isp≈158s @50bar/eps6)"
    )

    def _run(
        self,
        ox_name: str = "",
        fuel_name: str = "",
        prop_name: str = "",
        Pc: float = 50.0,
        MR: float = 1.0,
        eps: float = 6.0,
    ) -> Dict[str, Any]:
        """执行 NASA CEA 燃烧分析.

        Args:
            ox_name: 氧化剂名称 (液体双组元模式)
            fuel_name: 燃料名称 (液体双组元模式)
            prop_name: 单组元/固体推进剂名称，如 'KNSB'
            Pc: 燃烧室压力 (bar)
            MR: 混合比 (仅液体双组元)
            eps: 喷管膨胀比
        """
        if not HAS_ROCKETCEA:
            return self._fallback(ox_name or prop_name, fuel_name, Pc, MR, eps)

        # 确认 KNSB 已注册
        if prop_name == "KNSB" and not KNSB_REGISTERED:
            return self._knsb_empirical(Pc, eps)

        try:
            if prop_name:
                C = CEA_Obj(propName=prop_name)
            elif ox_name and fuel_name:
                C = CEA_Obj(oxName=ox_name, fuelName=fuel_name)
            else:
                return {"success": False, "error": "需要指定 (ox_name+fuel_name) 或 prop_name"}

            isp_vac = C.get_Isp(Pc=Pc, MR=MR, eps=eps)
            t_comb = C.get_Tcomb(Pc=Pc, MR=MR)
            c_star = C.get_Cstar(Pc=Pc, MR=MR)
            cf_result = C.get_PambCf(Pc=Pc, MR=MR, eps=eps)
            cf_eq = cf_result[0] if isinstance(cf_result, tuple) else cf_result
            mw, gamma = C.get_Chamber_MolWt_gamma(Pc=Pc, MR=MR, eps=eps)

            result: Dict[str, Any] = {
                "success": True,
                "method": "NASA CEA (rocketcea)",
                "propellant": prop_name or f"{ox_name}/{fuel_name}",
                "conditions": {"Pc_bar": Pc, "MR": MR, "eps": eps},
                "performance": {
                    "Isp_vac_s": round(isp_vac, 1),
                    "T_comb_K": round(t_comb, 0),
                    "C_star_ms": round(c_star, 1),
                    "Cf_eq": round(cf_eq, 3),
                    "Molar_mass_gmol": round(mw, 2),
                    "Gamma": round(gamma, 4),
                },
            }

            # KNSB: 附加工程实际估算
            if prop_name == "KNSB" or (ox_name == "" and fuel_name == "" and prop_name == "KNSB"):
                result["performance"]["Isp_engineering_est_s"] = f"{round(isp_vac * 0.85)}-{round(isp_vac * 0.90)}"
                result["knsb_notes"] = (
                    "KNSB is a solid propellant; real-world Isp is 85-90% of theoretical "
                    "due to heat losses, two-phase flow, and incomplete combustion. "
                    "Typical amateur motors achieve 110-140s depending on optimization."
                )

            return result
        except Exception as e:
            if prop_name == "KNSB":
                return self._knsb_empirical(Pc, eps)
            return {"success": False, "error": str(e)}

    def _fallback(
        self, prop: str, fuel: str, Pc: float, MR: float, eps: float
    ) -> Dict[str, Any]:
        """rocketcea 不可用时的 fallback."""
        if "KNSB" in prop.upper():
            return self._knsb_empirical(Pc, eps)
        return {
            "success": "simulated",
            "note": "rocketcea 未安装，返回经验估算值",
            "propellant": prop or f"unknown/{fuel}",
            "conditions": {"Pc_bar": Pc, "MR": MR, "eps": eps},
            "performance": {
                "Isp_vac_s": "N/A",
                "T_comb_K": "N/A",
                "C_star_ms": "N/A",
            },
        }

    def _knsb_empirical(self, Pc: float, eps: float) -> Dict[str, Any]:
        """KNSB 经验数据（CEA 不可用时的备用）.

        基于 NASA CEA 实测计算值的内插/外推。
        """
        # 从 CEA 基准数据估计
        base_isp = 157.8  # Pc=50, eps=6
        pc_factor = 1.0 + (Pc - 50) * 0.00015  # 弱压力依赖
        eps_factor = 1.0 + (eps - 6) * 0.012  # eps 每增加1，Isp 增加约 1.2%
        isp_est = base_isp * pc_factor * eps_factor

        return {
            "success": True,
            "method": "empirical (CEA benchmarks interpolation)",
            "propellant": "KNSB (65% KNO3 + 35% Sorbitol)",
            "conditions": {"Pc_bar": Pc, "eps": eps},
            "performance": {
                "Isp_vac_s": round(isp_est, 1),
                "Isp_engineering_est_s": f"{round(isp_est*0.85)}-{round(isp_est*0.90)}",
                "T_comb_K": 2713,
                "C_star_ms": 2958,
                "Molar_mass_gmol": 34.93,
                "Gamma": 1.114,
            },
            "knsb_notes": "经验估算值，建议安装 rocketcea 获取精确 CEA 计算结果",
        }


class PropellantComparator(BaseTool):
    name: str = "propellant_comparator"
    description: str = (
        "对比多种推进剂组合的性能。支持液体双组元、固体推进剂(KNSB)。"
        "输入 propellants(list[dict])，返回对比表。"
        "液体: {'ox': 'LOX', 'fuel': 'LH2', 'MR': 6.0}"
        "固体: {'prop': 'KNSB'}"
    )

    def _run(
        self,
        propellants: list = None,
        Pc: float = 50.0,
        eps: float = 6.0,
    ) -> Dict[str, Any]:
        """对比多种推进剂组合."""
        if propellants is None:
            propellants = [
                {"prop": "KNSB"},
                {"ox": "LOX", "fuel": "Ethanol", "MR": 1.5},
                {"ox": "N2O", "fuel": "Ethanol", "MR": 3.0},
                {"ox": "LOX", "fuel": "LH2", "MR": 6.0},
            ]

        analyzer = RocketCEAAnalyzer()
        results: List[Dict[str, Any]] = []
        for p in propellants:
            if "prop" in p:
                r = analyzer._run(prop_name=p["prop"], Pc=Pc, eps=eps)
            else:
                r = analyzer._run(
                    ox_name=p.get("ox", "LOX"),
                    fuel_name=p.get("fuel", "LH2"),
                    Pc=Pc,
                    MR=p.get("MR", 1.0),
                    eps=eps,
                )
            results.append(r)

        return {
            "success": True,
            "comparison": results,
            "common_conditions": {"Pc_bar": Pc, "eps": eps},
        }


class KNSBAnalyzer(BaseTool):
    name: str = "knsb_analyzer"
    description: str = (
        "KNSB 固体推进剂专用分析。KNSB = 65% 硝酸钾 + 35% 山梨醇。"
        "基于 NASA CEA (rocketcea) 真实计算，含工程实际修正。"
        "输入: Pc(float bar), eps(float), include_real_estimate(bool)"
    )

    # 已知工程数据 — 基于 CEA 验证 + 业余火箭社群经验
    REFERENCE_DATA: Dict[str, Any] = {
        "composition": {
            "oxidizer": "KNO3 (Potassium Nitrate), 65%",
            "fuel": "Sorbitol (C6H14O6), 35%",
            "density_g_cc": 1.80,
            "burn_rate_at_50bar_mm_s": 8.0,
            "pressure_exponent_n": 0.5,
        },
        "cea_theoretical": {
            "Pc_50_bar_eps_6": {
                "Isp_vac_s": 157.8,
                "T_comb_K": 2713,
                "C_star_ms": 2958,
                "Molar_mass_gmol": 34.93,
                "Gamma": 1.114,
            }
        },
        "engineering_notes": (
            "KNSB 是业余火箭最常用的推进剂之一："
            "1) 安全：常压可熔融浇注，无需真空；"
            "2) 成本：KNO3 ≈¥30/kg, 山梨醇 ≈¥40/kg, 总推进剂成本 ¥32/kg；"
            "3) 性能：理论 Isp 158s，工程实际 110-140s (取决于喷管优化和燃烧效率)；"
            "4) 回收友好：燃烧产物主要为 K2CO3 (水溶性)，用水即可清洗；"
            "5) 燃烧速度 6-10 mm/s @50bar，n≈0.5，适合内孔燃烧药柱"
        ),
    }

    def _run(
        self,
        Pc: float = 50.0,
        eps: float = 6.0,
        include_real_estimate: bool = True,
    ) -> Dict[str, Any]:
        """KNSB 推进剂综合性能分析."""
        result: Dict[str, Any] = {
            "success": True,
            "propellant": "KNSB (65% KNO3 + 35% Sorbitol)",
            "reference_data": self.REFERENCE_DATA,
            "conditions": {"Pc_bar": Pc, "eps": eps},
        }

        if HAS_ROCKETCEA and KNSB_REGISTERED:
            try:
                C = CEA_Obj(propName="KNSB")
                isp_vac = C.get_Isp(Pc=Pc, MR=1.0, eps=eps)
                t_comb = C.get_Tcomb(Pc=Pc, MR=1.0)
                c_star = C.get_Cstar(Pc=Pc, MR=1.0)
                cf_result = C.get_PambCf(Pc=Pc, MR=1.0, eps=eps)
                cf_eq = cf_result[0] if isinstance(cf_result, tuple) else cf_result
                mw, gamma = C.get_Chamber_MolWt_gamma(Pc=Pc, MR=1.0, eps=eps)

                result["cea_results"] = {
                    "Isp_vac_s": round(isp_vac, 1),
                    "T_comb_K": round(t_comb, 0),
                    "C_star_ms": round(c_star, 1),
                    "Cf_eq": round(cf_eq, 3),
                    "Molar_mass_gmol": round(mw, 2),
                    "Gamma": round(gamma, 4),
                }
            except Exception as e:
                result["cea_error"] = str(e)

        if include_real_estimate:
            result["engineering_estimate"] = self._real_world_estimate(Pc, eps)

        return result

    def _real_world_estimate(self, Pc: float, eps: float) -> Dict[str, Any]:
        """基于 CEA 理论值的工程实际估算."""
        from math import exp
        # CEA 基准: Pc=50, eps=6 → Isp=157.8s
        isp_theoretical = 157.8
        isp_theoretical *= (1.0 + (Pc - 50) * 0.00015)
        isp_theoretical *= (1.0 + (eps - 6) * 0.012)

        # 工程效率因子
        efficiency = 0.87  # 典型 KNSB 电机效率
        isp_realistic = isp_theoretical * efficiency
        isp_optimistic = isp_theoretical * 0.90
        isp_pessimistic = isp_theoretical * 0.80
        isp_typical_amateur = 125.0  # 典型业余水平

        return {
            "Isp_theoretical_s": round(isp_theoretical, 1),
            "Isp_realistic_s": round(isp_realistic, 1),
            "Isp_range_s": f"{round(isp_pessimistic)}-{round(isp_optimistic)}",
            "typical_amateur_isp_s": isp_typical_amateur,
            "efficiency_factor": efficiency,
            "notes": (
                f"工程实际 Isp 约为理论值的 {efficiency*100:.0f}%。"
                "业余级电机典型 110-130s；优化级 130-142s；专业级 142-150s。"
                "影响因素：喷管膨胀比、燃烧效率、热损失、两相流损失。"
            ),
        }
