"""
网络搜索工具
Skill Crafter 用于从外部获取专业知识，支持多源搜索与结果聚合。
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from sigma import BaseTool


class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = (
        "搜索网络获取技术资料。Skill Crafter 使用此工具获取新领域的专业知识，"
        "搜索结果经过可靠性评估后整合入技能文件。"
        "输入: query(str), source_types(list[str]): github|docs|academic|forum|general"
    )

    def _run(
        self,
        query: str,
        source_types: Optional[List[str]] = None,
        max_results: int = 10,
    ) -> Dict[str, Any]:
        """执行网络搜索并聚合结果."""
        if source_types is None:
            source_types = ["general", "github", "docs"]

        results = []

        for src in source_types:
            if src == "github":
                results.extend(self._search_github(query, max_results))
            elif src == "docs":
                results.extend(self._search_docs(query, max_results))
            elif src == "academic":
                results.extend(self._search_academic(query, max_results))
            else:
                results.extend(self._search_general(query, max_results))

        results.sort(key=lambda r: r.get("reliability_score", 0), reverse=True)

        return {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "total_results": len(results),
            "results": results[:max_results],
            "_note": (
                "实际部署时替换为真实的 gh search / Context7 / WebSearch API 调用。"
                "当前返回搜索结果框架供 Skill Crafter 参考。"
            ),
        }

    def _search_github(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """GitHub 代码搜索."""
        return [{
            "source": "github",
            "query": query,
            "reliability_score": 0.85,
            "suggested_command": f"gh search repos --limit {limit} '{query}'",
            "target_repos": [
                "psas/stm32f4-discovery-board",
                "openrocket/openrocket",
                "FreeCAD/FreeCAD",
                "PX4/PX4-Autopilot",
                "ArduPilot/ardupilot",
            ],
        }]

    def _search_docs(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """技术文档搜索."""
        return [{
            "source": "docs",
            "query": query,
            "reliability_score": 0.90,
            "suggested_sources": [
                "https://wiki.freecad.org",
                "https://openrocket.info/documentation",
                "https://docs.px4.io",
                "https://ardupilot.org/dev",
                "https://ntrs.nasa.gov",
            ],
        }]

    def _search_academic(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """学术搜索."""
        return [{
            "source": "academic",
            "query": query,
            "reliability_score": 0.95,
            "suggested_sources": [
                "https://arxiv.org (search: rocketry + guidance)",
                "https://ntrs.nasa.gov (NASA Technical Reports Server)",
                "https://apps.dtic.mil (DTIC technical reports)",
            ],
        }]

    def _search_general(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """通用搜索."""
        return [{
            "source": "general",
            "query": query,
            "reliability_score": 0.60,
            "suggested_sites": [
                "space.stackexchange.com",
                "engineering.stackexchange.com",
                "en.wikipedia.org/wiki/SpaceX_reusable_launch_system",
                "nakka-rocketry.net (amateur experimental rocketry)",
            ],
        }]


class SourceEvaluator(BaseTool):
    name: str = "source_evaluator"
    description: str = "评估搜索来源的可靠性。基于来源类型、权威性和时效性进行打分。"

    def _run(self, url: str, source_type: str = "web") -> Dict[str, Any]:
        """评估来源可靠性."""
        trusted_domains = {
            "nasa.gov": 0.98,
            "esa.int": 0.97,
            "wikipedia.org": 0.75,
            "github.com": 0.80,
            "stackexchange.com": 0.70,
            "arxiv.org": 0.90,
            "dtic.mil": 0.92,
            "youtube.com": 0.40,
            "bilibili.com": 0.35,
            "zhihu.com": 0.30,
            "csdn.net": 0.25,
        }

        score = 0.50
        for domain, weight in trusted_domains.items():
            if domain in url:
                score = weight
                break

        return {
            "url": url,
            "source_type": source_type,
            "reliability_score": score,
            "warning": "需交叉验证" if score < 0.70 else "较可靠",
            "verification_required": score < 0.60,
        }
