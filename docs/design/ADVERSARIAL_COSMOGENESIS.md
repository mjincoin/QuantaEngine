> **历史文档（已被取代）**：本文描述的是早期「两方案 + 共识宇宙」的 `cosmogenesis.Arena`，
> 已被「多方案并行、不合并」的新结构取代。当前权威文档见
> [REPO_STRUCTURE.md](REPO_STRUCTURE.md) 与
> [../../plans/2026-06-21-GENESIS_ARENA_V2_PARALLEL_ADVERSARIAL.md](../../plans/2026-06-21-GENESIS_ARENA_V2_PARALLEL_ADVERSARIAL.md)。保留本文仅作设计沿革记录。

# 对抗式宇宙生成（Adversarial Cosmogenesis）设计方案

## 0. 目标

从基本物理原理出发，生成一个**自洽的宇宙**，并用**两套完全不同范式**的方案各自独立优化、同时进行**对抗式协同训练**：互相指出对方方案的问题、给出可供对方评价采纳的优化建议，并在自己的方案中保留**同一入口**，最终实现**端到端的宇宙生成 + 不断迭代的对抗优化**。

本文档定义新增的 `cosmogenesis` 元层（src/cosmogenesis/），它**不修改** `quanta_engine` 与 `quantaengine` 旧代码，只在其上构建对抗框架。

## 1. 现有代码（方案 A 的本体）做了什么

`quanta_engine` 是一个**解析式有效物理编译器**：

```
YAML 配置（基本常数 ħ,c,G,k_B + 无量纲量 α,gravity/strong/weak/Λ 标度 + 粒子质量 + 宇宙学 Ω） 
   → validation → 粒子谱 → 原子(玻尔模型) → 核(玩具结合能) → 宇宙学(Friedmann 数值积分)
   → 恒星(标度律) → 结构(暗物质晕/星系/行星) → 复杂度(化学/生命/文明启发式打分) → UniverseReport
```

特征：**单向前馈、闭式公式、确定性、白盒可解释**。每层信任上一层结果，**不回检层间自洽性**。
- 入口：`run_universe_pipeline(config) -> UniverseReport`，目标量 = `civilization_potential_score ∈ [0,1]`。
- 优化路线：`scan_parameter`（单参数网格扫描）+ `normalized_sensitivity`（有限差分灵敏度）。没有真正的优化器。

`quantaengine`（旧）是标量场格点模拟（高斯随机场 + Friedmann 膨胀 + PDE 步进 → 密度场/功率谱），数值涌现、黑盒。

## 2. 两套方案的范式对立

| | 方案 A：前馈解析编译器（沿用 quanta_engine） | 方案 B：变分自洽场松弛（全新实现） |
|---|---|---|
| 生成宇宙的方式 | 常数 → 闭式公式逐层前馈一次 | 把宇宙当作**耦合约束的不动点**，迭代松弛到自洽 |
| 自洽性 | 默认假设（不回检） | **核心**：显式计算层间自洽残差 R，可判定"每层都过但整体不自洽" |
| 判据 | 硬阈值布尔窗口 | 平滑 logistic 软窗口边际 ∈[0,1] + 残差惩罚 |
| 数学 | 解析灵敏度（白盒梯度） | 不动点迭代 + 自由能极值（virial 极小） |
| 优化器 | `SensitivityClimber`：坐标灵敏度爬山（确定性、可解释） | `EvolutionaryRelaxer`：(μ+λ)-ES/CMA-lite 群体随机搜索（探索耦合方向） |
| 哲学 | 透明、可解释、单参数敏感 | 鲁棒、自洽、耦合全局 |

二者消费**同一** `UniverseConfig`/YAML、同一参数路径，因此配置可互换——这就是"保留同样的入口"。

## 3. 统一接口（同一入口）

```python
class UniverseScheme(Protocol):
    name: str
    def assess(self, config: UniverseConfig) -> UniverseAssessment: ...
    def optimize(self, start: ParameterVector, objective) -> ParameterVector: ...
    def critique(self, rival_champion: ParameterVector, rival: "UniverseScheme") -> Critique: ...
    def consider(self, critique: Critique) -> bool: ...   # 评价并决定是否采纳对方建议

@dataclass
class UniverseAssessment:
    scheme: str; score: float; feasible: bool
    margins: dict[str,float]      # 各窗口软边际/分数
    residual: float               # 自洽残差（A 报 0，B 真算）
    diagnostics: dict; warnings: list[str]
```

两个方案都提供与现有签名兼容的 `run_universe_pipeline(config) -> UniverseAssessment` 适配器。

`ParameterVector` 是被优化的"基本常数"向量（与 scan 用的参数路径一致）：
`alpha_scale, gravity_scale(log), strong_scale, cosmological_constant_scale, log10_primordial_amplitude`，各带物理边界，可双向映射到 `UniverseConfig`。

## 4. 方案 B 的物理（从原理独立推导）

输入：ħ,c,G_eff=G·gravity_scale, α_eff=α·alpha_scale, strong_scale, Λ_scale, m_e,m_p,m_n, Ω's, A_s。

1. **原子尺度（能量极值）** E(r)=ħ²/(2μr²)−α ħc/r，dE/dr=0 ⇒ r₀=ħ/(μcα)，E_b=½μc²α²。软窗口：0<α<α_crit 且 E_b 落在支持化学的能带 [E_lo,E_hi]。
2. **核结合窗口** 强吸引（strong_scale）对抗库仑（α）排斥 ⇒ 氘/氦-4 软稳定边际。
3. **恒星自洽** virial 给核心温度 T_core∝G_eff μ m_p/(k_B R)，点火需 T_core≥T_gamow(α,strong)；寿命∝燃料/光度。
4. **宇宙学耦合（关键）** 在 Λ,H0 决定的年龄内，必须同时容纳：结构线性增长（∝A_s×增长因子）与至少一代恒星寿命。残差：
   - R_time = relu(恒星复杂度所需寿命 − 宇宙年龄)
   - R_struct = relu(所需增长 − 实际增长)
   - R_flat = |ΣΩ − 1|（平直/闭合约束，A 仅软处理）
   - R_chem = 原子结合能与恒星/CMB 能标的相容性
5. **不动点松弛** 对涌现态 x=[金属丰度, 结构幅度, 平均恒星寿命] 迭代 x←F(x;常数) 至收敛；**收敛残差 / 是否收敛**进入评估——不收敛/振荡的宇宙即"内在不自洽"，A 无法察觉。
6. **可行性分数** score_B = softmin(各软边际) × exp(−λ·R_total)。即使所有单窗口通过，全局残差高仍被惩罚 ⇒ 与 A 排序不同 ⇒ 对抗信号来源。

## 5. 对抗式协同训练（Arena）

每轮 r：
1. **各自优化**：A 从 champion_A 用 SensitivityClimber 最大化 objective_A；B 从 champion_B 用 EvolutionaryRelaxer 最大化 objective_B。
2. **交叉评估**：A.assess(champion_B)、B.assess(champion_A)；在共享探针集上算**分歧度 D**（双方对同一宇宙打分之差）。
3. **互评（指出对方问题）**：
   - A 评 B：**脆弱性分析**——对 champion_B 每个参数 ±ε 扰动，看 A-score 跌落最快的轴 = 脆弱轴；并列出 B 软边际放过、A 硬窗口却判失败的项。给出**建议**：沿脆弱轴把 champion_B 推向 A 的鲁棒区。
   - B 评 A：用 B 模型算 champion_A 的**自洽残差**及主导残差项（A 从不优化它），给出**建议**：数值寻找最能降低该残差项的参数方向。
4. **评价并考虑对方建议（让对方评价考虑）**：每个方案在**自己模型**下评估对方建议——采纳后自身目标是否改善/不破坏？是则接受并把对方关切**作为正则项并入自己的目标**：
   - B 接受 A 的关切 ⇒ objective_B += A 硬窗口软惩罚 + 鲁棒性惩罚（脆弱性）。
   - A 接受 B 的关切 ⇒ objective_A += λ·R（把 B 的自洽残差当惩罚）——**等于把 B 的自洽原理引入 A 作正则**。
   接受/拒绝都记录。
5. **收敛判据**：跟踪 D 随轮次下降。双方都并入对方惩罚后，champions 收敛、互评分趋同 ⇒ D↓。**共识宇宙** = 最大化 min(score_A,score_B) 的宇宙（对两种范式都鲁棒）。当 D<tol 且双分数高 ⇒ 宣布"在两种独立范式下都自洽的宇宙"。

这是一个定义明确的极小极大 / 互蒸馏对抗博弈，带明确收敛指标。

## 6. 端到端产物

`python -m cosmogenesis run-adversarial --base configs/standard_universe.yaml --rounds N --out reports/adversarial/`
输出：两 champion 配置 YAML、交叉评分、逐轮分歧曲线 PNG、互评与采纳/拒绝记录、最终共识宇宙报告（md+json）。

## 7. 文件结构

```
src/cosmogenesis/
  parameters.py   ParameterVector / 边界 / config<->vector
  assessment.py   UniverseAssessment
  scheme.py       UniverseScheme Protocol + 共享入口
  scheme_a.py     quanta_engine 适配器 + SensitivityClimber + 评 B
  scheme_b.py     变分自洽场引擎 + EvolutionaryRelaxer + 评 A
  critique.py     Critique + 脆弱性/残差工具
  arena.py        对抗协同编排器
  cli.py / __main__.py
tests/test_cosmogenesis.py
```
