# 修复方案包：codebase-remediation-2026-06-21b

针对独立评估 [`QE-REVIEW-2026-06-21B`](../../docs/reviews/2026-06-21b-codebase-assessment.md)
（基线 `2ab9917`）的 10 项 finding 的可执行修复规划。

| 字段 | 值 |
|---|---|
| 状态 | `in-progress`（Phase A/B/C 已实现；D 待办） |
| 基线提交 | `2ab9917708b2ba1574301d48196743c4771a2282` |
| 评估报告 | [2026-06-21b-codebase-assessment.md](../../docs/reviews/2026-06-21b-codebase-assessment.md) |
| Findings | P1×3、P2×4、P3×3 |
| **接手入口** | **[HANDOVER.md](HANDOVER.md)** — 下一个 AI 完成 B/C/D 的输入文档 |

## 文件

- [`PLAN_MANIFEST.yaml`](PLAN_MANIFEST.yaml) — 机读：每个 finding 的拟改文件与拟加回归测试、phase、验收门禁、不变量。
- [`EXECUTION_REPORT.md`](EXECUTION_REPORT.md) — 设计说明，重点是 `QE-2026-101`「独立考虑建议」回路。
- [`TRACEABILITY_MATRIX.md`](TRACEABILITY_MATRIX.md) — finding → 拟改代码 → 拟加测试 → 验收。
- [`ITERATION_GUIDE.md`](ITERATION_GUIDE.md) — 实现/复审流程。

## 核心设计原则（用户确认的意图）

> 每个方案保持**独立**；对抗产出是给对方的**建议**；接收方不是盲目听众，要用自己的标准
> **谨慎独立复核**，**只有自己独立确认正确才采纳进优化**，否则拒绝并记录。**绝不合并。**

## Phase 顺序

1. **A 可信对抗回路**：`QE-2026-101`（独立考虑建议）、`QE-2026-102`（评分目标去自报化）。
2. **B 科学可信度**：`QE-2026-103`（物理校准）、`QE-2026-110`（物理不变量测试）。
3. **C 性能与扩展**：`QE-2026-104/105/106/108`。
4. **D 维护与文档**：`QE-2026-107/109`。

## 已完成阶段

- Phase A：`QE-2026-101/102`，commit `7b798a7`。
- Phase B：`QE-2026-103/110`。三方案标准锚点分别为 `0.9997 / 0.8614 /
  0.9233`；逐阈值单因素敏感性可通过 `threshold_sensitivity()` 复算；Hypothesis
  覆盖单位往返、平直密度预算、引力/恒星寿命单调性、电磁/氢原子单调性。阶段门禁：
  `112 passed`、总覆盖率 `95.61%`、PatchGate `100%`、CLI `94.32%`。
- Phase C：`QE-2026-104/105/106/108`。assess 缓存按 theory/version/rounded-vector
  隔离；novelty 归档有容量、按代衰减并去重；scheme 子包/entry point 自动发现；
  PatchGate 使用可注入冲突策略；evolve 报告收敛指标并支持显式早停，默认行为不变。

## 实现后流程

按 [ITERATION_GUIDE.md](ITERATION_GUIDE.md)：实现 → 跑验收门禁 → 写复审报告
`docs/reviews/2026-06-21b-codebase-remediation.md` → 在 `index.yaml` 把对应 finding 置 `verified`。
