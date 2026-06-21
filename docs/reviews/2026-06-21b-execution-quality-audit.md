# Remediation 执行质量审计报告（round B）

## 1. 元数据

| 字段 | 值 |
|---|---|
| 审计对象 | 方案包 [`codebase-remediation-2026-06-21b`](../../plans/codebase-remediation-2026-06-21b/EXECUTION_REPORT.md) 的 Phase A/B/C/D 实现 |
| 审计基线 | `7c179ed`（审计前 HEAD） |
| 审计方式 | 独立重跑全部质量门禁 + 9 道验收执行器；逐 finding 比对**设计意图**与**实现**；核对不变量；核对证据记录一致性 |
| 结论 | **通过（高质量）**。实现与 `EXECUTION_REPORT.md` 设计一致，证据完全可复现，不变量保持；发现 1 处可强化点已修复，另记 3 条非阻断性观察 |

## 2. 独立验证结果

| 检查 | 结果 |
|---|---|
| `python -m pytest` | `120 passed`（审计新增 1 项强化测试，原 119） |
| 覆盖率合约 | 总 `95.29%`（≥90%）；`patchgate.py` `100%`；`cosmogenesis.cli` `94.32%` |
| `ruff check` / `ruff format --check` | 通过（115 文件） |
| `mypy src` | 通过（93 文件） |
| 验收执行器 `run_remediation.py` 9 门禁 | **全部独立重跑通过**：round-b-regressions / coverage-contracts / full-tests / lint / format / types / dependencies / build / wheel-smoke |
| 证据一致性 | `records/remediation-evidence.json`（status=passed，巴黎时区时间戳）与复审报告数字一致 |

## 3. 逐 finding 执行质量审计

| Finding | 设计意图 | 实现核验 | 质量评级 |
|---|---|---|---|
| `QE-2026-101` | 接收方在自身 objective 下独立复核建议，自证改进才采纳，绝不合并 | `BaseEngine.consider` 用自身 objective + warm-start 复核；`duel.py` 接入仅更新自身谱系；`ConsiderationCard`+ledger 留 before/after/delta/reason；`allow_merge` 恒 False | 高 |
| `QE-2026-102` | 评分目标引擎派生、非自报 | efficiency←`compute_cost`（variational 为**实测**迭代数）、simplicity←真实 `free_parameters`；篡改 YAML 自报值不改分（回归证实） | 高 |
| `QE-2026-103` | 阈值校准 + 不确定性接口 + 锚点 | variational 12 / minimal 8 阈值覆盖全部窗口、analytic 1（委托 quanta_engine）；`threshold_sensitivity` 逐项区间重算；`PHYSICS_CALIBRATION.md` 56 行 | 高（见 §4 强化） |
| `QE-2026-104` | assess 记忆化、确定性不变 | `bridge.assess` 线程安全 LRU（键=id+version+rounded-vector），深拷贝防污染，版本提升强制 miss；回归实测 1 build/重复键 | 高 |
| `QE-2026-105` | novelty archive 有界/衰减/去重 | `NoveltyArchive` 容量+按 generation 衰减（无 wall-clock）+圆整去重；30 代回归容量有界、末段 novelty>0 | 高 |
| `QE-2026-106` | 插件式注册 + 冲突策略对象 | `pkgutil` 自动发现 + `quanta_engine.schemes` entry point + 校验；`PatchGate` 可注入 `ConflictStrategy`；回归在 tmp 落地一个 drop-in 方案被发现 | 高 |
| `QE-2026-107` | lattice/namespace 退役时间表 | `DEPRECATION.md` 76 行：lattice 冻结、`quantaengine` 1.0（不早于 2027-06-21）移除 + 迁移 | 高 |
| `QE-2026-108` | 收敛指标 + 可选早停 | 每代 `ConvergenceMetrics`；`early_stopping` 默认 False（默认行为不变）；稳定场景早停回归 | 高 |
| `QE-2026-109` | v2 计划加 superseded 横幅 | 历史 v2 计划顶部双语横幅指向 `REPO_STRUCTURE.md` | 高 |
| `QE-2026-110` | 物理不变量属性测试 | `test_physics_invariants.py`（8 个 `@given`）：单位往返、平直密度守恒、引力↑→寿命↓、α↑→结合更强半径更小、标准宇宙锚点 | 高 |

## 4. 审计期应用的强化（修复优化）

**校准敏感性框架的非空洞性证据**（强化 `QE-2026-103`）：
原实现中 variational/minimal 在**标准锚点**即有非零阈值敏感（0.036 / 0.030），但 analytic 唯一可覆写阈值（恒星寿命）在标准点敏感度为 `0`。审计确认这是**物理正确**——标准宇宙恒星寿命 ~1e10 yr 远高于阈值区间 `[5e8, 2e9]`，稳健可行故不敏感。为避免"框架对 analytic 是否有效"的误读，审计实测并新增回归
`test_calibration_sensitivity_is_nonvacuous`：在强引力（gravity_scale=3，短寿命恒星近边界宇宙）下，analytic 的恒星寿命阈值敏感度达 **0.322**，证明校准/不确定性框架对**三方案均非空洞**、能在窗口边界正确检测阈值效应。

## 5. 非阻断性观察（建议，不影响 verified 结论）

1. `display_score` 权重仍为手设启发式；已与物理事实分层、且**选择用 Pareto 而非 display**，故不影响选择可信度。建议未来在文档中记录权重依据或附敏感性。
2. analytic 仅 1 个可覆写阈值（因委托 `quanta_engine` 流水线，其内部阈值不易外覆）。如需更细校准，应在 `quanta_engine` 暴露阈值钩子，属独立工作。
3. `bridge.consider` 不走 assess 缓存（需 engine 实例做 optimize）；对决中为轻量重算，非缺陷。

## 6. 结论

方案包 round B 的 Phase A/B/C/D **执行质量高**：实现忠实于 `EXECUTION_REPORT.md` 设计，10 项 finding 的回归真实非套话，9 道验收门禁独立重跑全部通过，核心不变量（永不合并 / 接收方自身独立判定 / 确定性 / 无 wall-clock / 覆盖率门槛）均保持。审计补强了校准敏感性证据。**维持 `QE-REVIEW-2026-06-21B` 为 `verified`**。
