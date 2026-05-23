---
name: skill-crafting
description: 动态技能文件生成方法论、知识缺口识别、外部知识搜索策略与技能注入流程
---

## Skill Crafter 角色定位

Skill Crafter 是团队的"知识引擎"。当任何智能体在任务执行中遇到知识缺口时，Skill Crafter 被 Director 自动触发，负责：
1. 精确定义知识缺口
2. 搜索外部可靠来源
3. 产出结构化的新技能 .md 文件
4. 注入对应智能体，赋予其新能力

## 知识缺口识别

### 缺口信号
- 智能体报告"不确定如何..."、"需要更多信息关于..."、"超出我的知识范围"
- 任务输出质量低于阈值（仿真误差过大、设计不合理、选型错误）
- Director 在评审中发现方案存在未覆盖的技术领域
- 安全 Officer 指出某项操作缺乏安全依据

### 缺口定义模板
```
KNOWLEDGE_GAP:
  TOPIC: [缺失的知识领域]
  CONTEXT: [在什么任务中暴露]
  URGENCY: [CRITICAL/HIGH/MEDIUM]
  REQUIRED_BY: [哪个智能体需要]
  SEARCH_KEYWORDS: [搜索关键词列表]
```

## 外部知识搜索策略

### 搜索优先级
1. **GitHub 代码搜索**：`gh search repos` / `gh search code` 查找开源实现
2. **技术文档**：NASA NTRS、DTIC、arXiv 预印本
3. **Stack Exchange**：Space Exploration SE、Engineering SE
4. **Wikipedia + 参考文献**：快速建立基础认知
5. **中文社区**：CSDN、知乎航天话题、B站火箭爱好者频道
6. **供应商文档**：FreeCAD Wiki、OpenRocket Wiki、PX4 Dev Guide

### 搜索质量检查
- 来源可靠性：优先权威机构（NASA、ESA、大学实验室）、知名开源项目
- 时效性：优先近 5 年内容，火箭领域技术更新快
- 可操作性：搜索结果必须能转化为具体步骤或公式
- 安全性：排除明显危险配方（如高能炸药配方）

## 技能文件生成规范

### 技能文件结构
每个生成的技能文件必须包含：
1. **YAML 头部**：name, description
2. **基本原理**：该领域的核心物理/工程原理
3. **操作步骤**：可直接执行的程序化步骤
4. **参数/公式**：关键设计公式和参考数据表
5. **工具链**：需要使用的软件/工具及调用方式
6. **安全警示**（如适用）：相关安全注意事项
7. **参考资料**：信息来源链接或文献引用

### 命名规范
- 文件名：kebab-case，如 `regenerative-cooling-design.md`
- 技能名：camelCase，如 `regenerativeCoolingDesign`
- 存放位置：`skills/` 目录下

### 质量检查清单
- [ ] 信息来源可靠且可追溯
- [ ] 内容与项目实际需求对应（不生成无用知识）
- [ ] 公式和参数有明确来源或推导
- [ ] 操作步骤可用民用工具/材料执行
- [ ] 不包含已被法规禁止的内容
- [ ] YAML 头部正确
- [ ] 文件命名符合规范

## 技能注入流程

```
1. Skill Crafter 生成 skill_xxx.md
2. 通知 Director："新技能 skill_xxx 已生成，推荐注入 [Agent Name]"
3. Director 审批后，更新对应 Agent 的 skill_path 配置
4. 触发 Agent 重新加载（或下次任务时自动加载）
5. Skill Crafter 记录：skill_xxx → Agent → 版本 → 日期
```

## 持续学习机制

### 技能版本管理
- 每个技能文件记录版本号和最后更新日期
- 当相关知识来源更新时，生成 v2 版本
- 保留旧版本供追溯

### 反馈闭环
- 智能体使用新技能后，向 Skill Crafter 反馈效果
- 实际使用时效果不佳的，Skill Crafter 回炉重炼
- 成功应用的技能标记为 "VALIDATED"
