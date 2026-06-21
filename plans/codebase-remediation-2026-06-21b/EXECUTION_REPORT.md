# 执行设计说明（codebase-remediation-2026-06-21b）

本文件给出各 finding 的修复设计；状态 `planned`，**不含源码实现**。

## QE-2026-101：对抗「独立考虑建议」回路（Phase A，最高优先）

### 目标

把对抗从"只影响选择分数"升级为"**给对方可独立复核的建议**"，且接收方**只有自己独立确认能改进自身目标才采纳**——绝不盲从、绝不合并。

### 设计

1. **建议载体**：`ChallengeCard` 已有 `probe_vector`；规范一个语义明确的 `suggestion: list[float]`（一个具体 `ParameterVector`），表示攻击方"我认为你在这个点会更好"。攻击方依据自身对目标弱点的判断（如脆弱轴、低自洽残差方向）构造该建议。

2. **接收方独立复核**：在 `cosmogenesis/core/protocol.py` 的 `BaseEngine` 增加：

   ```text
   consider(current, suggestion) -> ConsiderDecision
     own_now  = self.objective(current)
     own_sugg = self.objective(suggestion)            # 用“自己的”目标评估对方建议
     # 可选：以 suggestion 为 warm-start 在自身模型内再优化少量预算
     own_warm = self.objective(self.optimize(suggestion, budget=small))
     adopt = max(own_sugg, own_warm) > own_now + eps   # 仅当自证改进
     return ConsiderDecision(adopt, evaluated_by=self.name, delta=..., reason=...)
   ```

   关键：复核用**接收方自身的 `objective`**，不是攻击方的分数；这保证独立性。

3. **复用已退役模式**：git 历史中 `cosmogenesis/scheme_a.py::consider()` / `scheme_b.py::consider()` 已实现过"再优化后只在自身目标不退化时接受"的逻辑。复用其判定骨架，但**去掉**原共识/合并语义——这里只更新接收方自己的 champion，绝不把两方案合并。

4. **接入对决**：`arena/duel.py` 在挑战-防守之后，若挑战带 `suggestion`，目标方调用 `consider`；采纳则更新其 `seed_vector`（仅其自身谱系），拒绝则不变。

5. **可回溯**：`arena/ledger.py` 的 history 记录新增字段 `suggestion_source / suggestion_vector / considered / adopted / delta / reason`，形成"建议→独立复核→采纳/拒绝"的可追踪链路。

### 验收

- 当建议在接收方自身模型下确能改进时被采纳并改变其后续优化；不能改进时被拒并记录理由。
- 采纳前后两方案冠军均由各自模型独立判定，`allow_merge` 恒 False。
- 跨进程/串并行确定性不变（沿用稳定 seed）。
- 回归：`tests/test_remediation_b.py::test_suggestion_adopted_only_if_self_verified_improvement`。

## QE-2026-102：评分目标去"自报化"（Phase A）

- `computational_efficiency`：改为**实测**（对 `assess`/`optimize` 计时或计调用次数并归一化），不再读 `philosophy.computational_efficiency`（后者降级为展示/先验，不进硬 Pareto）。
- `simplicity`：改为真实**假设/参数计数**（每个 scheme 暴露其有效自由度，而非仅 minimal_axiom 设 `free_parameters`）。
- `display_score` 权重：给出依据或随报告附敏感性；评估"弱/可声明目标退出硬 `pareto_dominates` 维度"。
- 验收：efficiency 不同 scheme 可区分且来自实测；simplicity 非二值；移除可自报目标后 Pareto front 收敛可解释。

## QE-2026-103：物理校准与不确定性（Phase B）

- 新增 `docs/design/PHYSICS_CALIBRATION.md`：为每个 logistic 窗口阈值给出来源/文献区间，标注"物理事实 vs 启发式权重"。
- 在 engine 暴露阈值敏感性接口；标准宇宙数值锚点纳入区间断言。
- 验收：`test_standard_universe_within_calibrated_ranges`；阈值扰动的分数敏感性有报告。

## QE-2026-104：assess 记忆化（Phase C）

- `arena/bridge.py` 对 `assess` 按 `(theory_id, version, vector-rounded)` 缓存；保证确定性不变、调用次数显著下降。

## QE-2026-105：novelty archive 有界（Phase C）

- `arena/evolution.py`/`scoring.py`：archive 加容量上限或时间衰减 + 特征去重；区分当代/跨代 novelty。

## QE-2026-106：插件式方案注册 + reducer 冲突策略（Phase C）

- `schemes/__init__.py`：子包自动发现或 entry-point 注册（放入新 scheme 子包即生效）。
- `arena/patchgate.py`：抽出冲突策略对象，支持未来更多 patch 类型。

## QE-2026-107：历史原型/旧 namespace 退役（Phase D）

- 新增 `docs/design/DEPRECATION.md`：lattice 定位（冻结/归档）、`quantaengine` namespace 1.0 移除时间表与迁移说明。

## QE-2026-108：演化收敛/早停（Phase C）

- `arena/evolution.py`：收敛指标（Pareto 稳定、分数增量阈值、family 稳定）+ 可选早停参数。

## QE-2026-109：文档漂移（Phase D）

- 给 `plans/2026-06-21-GENESIS_ARENA_V2_PARALLEL_ADVERSARIAL.md` 加"已被 REPO_STRUCTURE 取代"横幅。

## QE-2026-110：物理不变量属性测试（Phase B）

- 新增 `tests/test_physics_invariants.py`：property-based（hypothesis）守恒/量纲/单调/标准宇宙锚点。

## 全局不变量（实现期必须保持）

- `allow_merge` 恒 False；采纳建议必由接收方自身模型独立判定。
- 不降低既有覆盖率门槛（总 90% / patchgate 85% / cli 85%），不破坏跨进程确定性。

## Phase B 实施记录

- `QE-2026-103`：所有方案通过 `CalibrationThreshold` 暴露阈值名义值、模型不确定性
  区间、单位、分类与文档依据；`threshold_sensitivity()` 对每个阈值执行单因素上下界
  重算。标准分数为 analytic `0.9997237`、variational `0.8614355`、minimal
  `0.9232608`。当前最大单阈值分数变化分别为 `0`、`0.03635`（nuclear low）、
  `0.03035`（seed high）。analytic 的标准锚点远离其恒星寿命阈值，因此该区间内为零敏感。
- `QE-2026-110`：新增 Hypothesis 属性测试，覆盖能量/质量单位往返、平直 FLRW 密度
  预算守恒、引力增强使恒星寿命严格缩短、电磁增强使氢结合更强且半径更小，以及标准
  宇宙的氢、Bohr 半径、年龄与三方案分数锚点。
- Phase B 完整门禁：`112 passed`；Ruff lint/format、Mypy 全绿；总覆盖率 `95.61%`，
  `patchgate.py` `100%`，`cosmogenesis/cli.py` `94.32%`。

## Phase C 实施记录

- `QE-2026-104`：`bridge.assess` 使用线程安全、LRU 有界缓存，键为
  `(theory_id, version, rounded-vector)`，缓存值深拷贝防止调用方污染。一次完整
  `score_theory` 实测 `17 misses / 4 hits`；重复评分全部复用已有键，版本提升强制 miss。
- `QE-2026-105`：`NoveltyArchive` 默认容量 `128`，按确定性 generation 过期（默认 8 代）
  并按圆整特征去重；禁止 wall-clock 进入结果。30 代回归中容量始终不超 8，3 代窗口
  最终仅保留 4 项，末 10 代 novelty 均大于 0。
- `QE-2026-106`：内置 scheme 由 `pkgutil` 自动发现；外部插件使用
  `quanta_engine.schemes` entry point。`PatchGate` 的决策映射抽为可注入
  `ConflictStrategy`，默认策略保持 patch/fork/invalidate/unchanged 既有语义与 no-merge
  不变量。
- `QE-2026-108`：每代记录 Pareto、family 与最大 display-score 增量稳定性；显式
  `early_stopping=True` 后按 patience 早停。稳定场景从请求 10 代缩短至 2 代；
  `early_stopping=False` 的默认路径仍完成全部请求代数。
- Phase C 完整门禁：`118 passed`；Ruff lint/format、Mypy 全绿；总覆盖率 `95.29%`，
  `patchgate.py` `100%`，`cosmogenesis/cli.py` `94.32%`。
