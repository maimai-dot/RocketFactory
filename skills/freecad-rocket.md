---
name: freecad-rocket-design
description: FreeCAD 火箭结构参数化建模、质量特性提取、装配体管理与制造图纸导出
---

## 火箭结构建模策略

### 参数化设计原则
- 所有关键尺寸通过 Spreadsheet 工作台管理，单点修改全局生效
- 核心参数：箭体直径、壁厚、总长、级间比、鼻锥长径比
- 使用命名约束（Named Constraints）而非硬编码尺寸

### 坐标系约定
- 原点位于火箭顶点（鼻锥尖端）
- +Z 轴沿箭体向下（从鼻锥到喷管出口）
- +Y 轴为俯仰方向，+X 为偏航方向
- 所有子部件使用局部坐标系，通过装配体约束关联

## 箭体部件建模

### 鼻锥
- 型线：von Kármán 曲线（最优气动外形）
  - r(x) = R × sqrt(arcsin(x/L) / π - (1 - 2x/L) × sqrt(x/L - (x/L)²) / π)
  - 或使用 3:1 抛物线作为简化近似
- 使用 Part Design: Revolve 操作，从轮廓旋转 360°
- 鼻锥尖端圆角半径 ≥ 2mm（3D 打印可行）

### 箭体分段
- 每段箭体为薄壁圆筒，使用 Part Design: Pad 从圆环草图拉伸
- 段间连接：法兰盘或螺纹连接，在 FreeCAD 中使用布尔运算建模
- 舵面/栅格翼：使用独立 Body，通过装配体约束定位

### 着陆腿机构
- 4 腿对称布局，每条腿含：主支撑杆 + 铰链 + 展开弹簧 + 锁定机构
- 收起状态：腿贴合箭体外壁，使用 Assembly 工作台验证干涉
- 展开状态：腿与箭体轴线夹角 30-45°，足垫接触地面

## 质量特性提取

### Python API 自动化
```python
import FreeCAD as App
import Part, Mesh

doc = App.ActiveDocument
for obj in doc.Objects:
    if hasattr(obj, 'Shape'):
        print(f"{obj.Label}: Mass={obj.Shape.Mass:.3f} kg")
        print(f"  CG: {obj.Shape.CenterOfMass}")
        print(f"  MOI: {obj.Shape.MatrixOfInertia}")
```

### 质量预算表
- 结构质量：箭体、鼻锥、舵面、着陆腿、级间段
- 推进质量：发动机、推进剂、储箱、管路、阀门
- 设备质量：飞控、电池、传感器、通信、回收系统
- 余量：总质量的 15-20% 作为设计余量

## 导出规范

### 3D 打印 STL
- Mesh Workbench: 最大偏差 0.1mm，角度偏差 5°
- 检查法线方向一致（全部朝外）
- 修复非流形边和孔洞

### 工程图纸 TechDraw
- 三视图 + 等轴测视图
- 标注关键尺寸和公差
- 材料列表和表面处理要求

### 仿真用数据
- 质量、CG、MOI 导出为 JSON
- 外轮廓线导出为 CSV（供气动计算）
- 各部件截面参数汇总

## 迭代工作流

1. Director 下达总体参数 → 更新 Spreadsheet 中的驱动参数
2. 重建模型（Ctrl+R）并提取新版质量特性
3. 将质量数据传递给 Sim Chief 进行飞行仿真
4. 根据仿真反馈调整结构（减重 / 加强 / 改变布局）
5. 每轮迭代记录参数变更和仿真结果对比
