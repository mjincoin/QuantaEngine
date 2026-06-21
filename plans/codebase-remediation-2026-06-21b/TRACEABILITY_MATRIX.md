# 追踪矩阵（codebase-remediation-2026-06-21b）

finding → 改动代码 → 回归测试 → 验收要点。Phase A/B/C 已完成，D 待实现。

| Finding | Phase | 拟改代码 | 拟加回归测试 | 验收要点 |
|---|---|---|---|---|
| `QE-2026-101` | A | `arena/cards.py`、`core/protocol.py`、`schemes/*/engine.py`、`arena/duel.py`、`arena/ledger.py` | `test_remediation_b.py::test_suggestion_adopted_only_if_self_verified_improvement` | 自证改进才采纳；否则拒绝并记录；无合并 |
| `QE-2026-102` | A | `arena/scoring.py` | `test_remediation_b.py::test_scoring_objectives_are_measured_not_declared` | efficiency 实测可区分；simplicity 非二值；Pareto 收敛可解释 |
| `QE-2026-103` | B (fixed) | `docs/design/PHYSICS_CALIBRATION.md`、`core/protocol.py`、`schemes/*/engine.py` | `test_remediation_b.py::test_standard_universe_within_calibrated_ranges` | 阈值有来源/区间；标准宇宙在区间内；敏感性有报告 |
| `QE-2026-104` | C (fixed) | `arena/bridge.py` | `test_remediation_b.py::test_assess_memoized_and_deterministic` | assess 调用数下降；结果与未缓存一致 |
| `QE-2026-105` | C (fixed) | `arena/evolution.py`、`arena/scoring.py` | `test_remediation_b.py::test_novelty_archive_bounded_no_collapse` | archive 有界；长跑 novelty 不塌缩 |
| `QE-2026-106` | C (fixed) | `schemes/__init__.py`、`arena/patchgate.py` | `test_remediation_b.py::test_new_scheme_discovered_without_central_edit` | 放入新 scheme 子包即参与对抗；冲突策略可替换 |
| `QE-2026-107` | D | `docs/design/DEPRECATION.md` | `test_remediation_b.py::test_deprecation_schedule_documented` | lattice 定位与 1.0 移除时间表存在 |
| `QE-2026-108` | C (fixed) | `arena/evolution.py` | `test_remediation_b.py::test_evolution_early_stops_on_stable_ecosystem` | 生态稳定时早停；默认行为不变 |
| `QE-2026-109` | D | `plans/2026-06-21-GENESIS_ARENA_V2_PARALLEL_ADVERSARIAL.md` | （文档检查，无单测） | 顶部有 superseded 横幅指向 REPO_STRUCTURE |
| `QE-2026-110` | B (fixed) | `tests/test_physics_invariants.py` | `tests/test_physics_invariants.py`（自身即测试） | 守恒/量纲/单调/锚点不变量通过 |

## 验收门禁（全部 finding 实现后）

```bash
python -m pytest
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src
python plans/codebase-remediation-2026-06-21/execution/check_coverage.py
```
