# Sigma AERC Paper

arXiv 防御性公开论文。Sigma AERC 多智能体协同框架的设计、验证与火箭工程应用。

## 编译

```bash
# 本地编译（需要 TeX Live 或 MiKTeX）
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex

# 或使用 tectonic（轻量，无需完整 TeX Live）
tectonic paper.tex

# 在线编译
# 上传到 https://www.overleaf.com 直接编译
```

## arXiv 提交

1. 注册/登录 https://arxiv.org
2. 选择 cs.MA (Multiagent Systems) 作为主分类
3. 选择 cs.AI, cs.CE (Computational Engineering) 作为交叉分类
4. 上传 paper.tex（不需要 .bib 文件，参考文献已内嵌）
5. 填写元数据：标题、摘要、作者
6. 选择 CC BY 4.0 或 CC BY-NC 4.0 许可证
7. 提交，等待审核（通常 1-2 天）

## 核心贡献

1. **AERC 协议**: 结构化的 Analyze→Execute→Review→Converge 多轮协同
2. **交叉审查**: 盲分析 + 跨领域配对审查，消除群体思维
3. **共识估算**: 工具数据不可靠时的多角色独立估算→收敛
4. **魔鬼代言人**: 安全官一票否决权 + 最坏情况分析
5. **复杂度自适应**: 纯规则引擎 0-10 评分，自动选择 LITE/STANDARD/RIGOROUS
6. **工程验证**: KNSB 推进剂性能被交叉审查修正 16%（183s→158s）
