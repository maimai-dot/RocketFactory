"""
技能文件生成工具
Skill Crafter 的核心工具，用于动态创建新的技能 .md 文件并注入对应智能体。
"""

import re
from pathlib import Path
from datetime import datetime
from typing import ClassVar, Dict, Any, List, Optional

from sigma import BaseTool


SKILLS_DIR = Path(__file__).parent.parent / "skills"


class SkillCreatorTool(BaseTool):
    name: str = "skill_creator"
    description: str = (
        "动态生成新的技能 .md 文件。输入技能名称(kebab-case)、描述和专业知识内容，"
        "自动添加 YAML 头部并保存到 skills/ 目录。"
        "输入: skill_name(str), description(str), content(str), target_agent(str)"
    )

    def _run(
        self,
        skill_name: str,
        description: str,
        content: str,
        target_agent: str = "",
    ) -> Dict[str, Any]:
        """创建新的技能文件."""
        filename = f"{skill_name}.md"
        filepath = SKILLS_DIR / filename

        if filepath.exists():
            version = 2
            while (SKILLS_DIR / f"{skill_name}_v{version}.md").exists():
                version += 1
            filepath = SKILLS_DIR / f"{skill_name}_v{version}.md"

        yaml_header = f"""---
name: {skill_name}
description: {description}
created: {datetime.now().strftime("%Y-%m-%d")}
target_agent: {target_agent}
version: 1
---

"""
        full_content = yaml_header + content

        filepath.write_text(full_content, encoding="utf-8")

        return {
            "success": True,
            "skill_name": skill_name,
            "file_path": str(filepath),
            "target_agent": target_agent,
            "size_bytes": len(full_content),
            "action_required": (
                f"更新 agents/{target_agent}.py 的 skill_path 列表，"
                f"添加: skills/{filename}"
            ) if target_agent else "手动指定目标智能体以完成注入",
        }


class KnowledgeGapDetector(BaseTool):
    name: str = "knowledge_gap_detector"
    description: str = (
        "分析智能体输出或对话，检测知识缺口。返回缺口主题、关键词、紧急程度。"
        "输入: agent_name(str), context(str), output_quality(str)"
    )

    GAP_SIGNALS: ClassVar[List[str]] = [
        "不确定如何", "需要更多信息", "超出知识范围",
        "不确定", "需要帮助", "无法确定",
        "不知道", "缺乏数据", "缺少参考",
        "unable to", "cannot determine", "insufficient information",
    ]

    def _run(
        self,
        agent_name: str,
        context: str,
        output_quality: str = "normal",
    ) -> Dict[str, Any]:
        """检测知识缺口."""
        gaps = []

        for signal in self.GAP_SIGNALS:
            if signal.lower() in context.lower():
                idx = context.lower().index(signal.lower())
                snippet = context[max(0, idx - 30): idx + len(signal) + 80]
                topic_match = re.search(
                    r'(?:关于|about|regarding|related to|in|on)\s+([^。.!！\n]{3,50})',
                    snippet, re.IGNORECASE,
                )
                topic = topic_match.group(1).strip() if topic_match else "unknown"
                gaps.append({
                    "topic": topic,
                    "signal": signal,
                    "context_snippet": snippet.strip(),
                })

        urgency = (
            "CRITICAL" if output_quality == "low"
            else "HIGH" if len(gaps) > 2
            else "MEDIUM" if gaps
            else "LOW"
        )

        return {
            "agent_name": agent_name,
            "gaps_found": len(gaps),
            "gaps": gaps,
            "urgency": urgency,
            "recommendation": (
                "触发 Skill Crafter 生成新技能文件" if gaps
                else "当前知识覆盖充分，无需新技能"
            ),
            "search_keywords": [g["topic"] for g in gaps],
        }
