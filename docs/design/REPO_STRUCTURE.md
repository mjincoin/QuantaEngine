# 代码库结构规范（长期多方案并行的目录约定）

本仓库分三层，目录名即内容，互不混淆：

```
src/
  quanta_engine/         物理基座：有效物理前馈 pipeline（常数→各物理层→UniverseReport）
  quantaengine_lattice/  历史原型：标量场格点模拟（高斯随机场+Friedmann+PDE 步进），与上面完全独立
  cosmogenesis/          多方案对抗式创世平台（核心）
```

## cosmogenesis 的内部规范

```
cosmogenesis/
  core/        所有方案共享的「对抗式输入输出契约」
    parameters.py   ParameterVector：被优化的基本常数向量（统一参数空间，方案间可互换）
    assessment.py   UniverseAssessment：统一评估输出（score/feasible/margins/residual/diagnostics）
    protocol.py     UniverseScheme 协议 + BaseEngine 基类 + 共享分析工具（fragility_profile）

  schemes/     每个「方案」一个自洽子包，互不依赖、可独立增删
    <scheme_name>/
      __init__.py   方案名 SCHEME_NAME、元数据、导出 Engine 类
      engine.py     物理：assess(ParameterVector) -> UniverseAssessment（对抗式 I/O）
      optimizer.py  迭代优化路径：optimize(start, budget) -> ParameterVector
    __init__.py   SCHEME_REGISTRY：方案名 -> Engine 类；build_scheme(name) / list_schemes()

  arena/       并行对抗平台（裁决、对决、演化），消费 schemes，不含物理
    cards.py        结构化 Challenge/Defense/Judge/Patch（pydantic, schema 校验）
    theory.py       TheorySpec：方案的「命名谱系实例」（engine 键 + 配置 + claims + 哲学 + 版本 + parent）
    registry.py     TheoryRegistry：谱系注册/版本/血统，永不合并
    bridge.py       TheorySpec.engine 键 -> schemes 注册表实例
    scoring.py      多目标评分 + Pareto + family niche + novelty
    verifier.py     确定性验证（复现+benchmark）
    agents.py       规则型攻击/防守
    judge.py        裁决
    patchgate.py    patch/fork/不改/失效（永不 merge，写 history）
    duel.py / tournament.py / evolution.py   并行编排
  cli.py / __main__.py   genesis-arena CLI
```

## 「方案 / scheme」与「理论 / theory」的区别（避免混淆）

- **方案 (scheme)** = 一种**物理范式 + 优化路径**的代码实现，住在 `cosmogenesis/schemes/<name>/`。
  当前三个：`analytic_compiler`（前馈闭式）、`variational_relaxer`（自洽不动点）、`minimal_axiom`（量纲人择不等式）。
- **理论 (theory)** = 一个**命名的谱系实例**：选定一个 scheme + 一份配置 + claims/哲学 + 版本号 + 血统，
  住在仓库根的 `theories/T-NNNN_<family>/`，并各自维护 `history.jsonl`（迭代/对抗历史）。

> 一句话：scheme 是「方法库」，theory 是「用该方法跑出的、带身份与历史的长期谱系」。
> 多个 theory 可共用同一 scheme（不同配置/血统），多个 scheme 永远并行存在、永不合并。

## 长期存储：对抗结果与迭代计划存在哪里

| 内容 | 位置 | 是否入 git | 写入者 |
|---|---|---|---|
| 每条谱系的逐代对抗历史 | `theories/T-NNNN_<family>/history.jsonl`（append-only，每行一代：时间戳[巴黎时区]、版本、冠军参数、各目标分、patch/fork 事件） | 是（长期累积、可 diff） | `arena/ledger.py` |
| 自动生成的下一轮迭代优化计划 | `plans/iterations/<时间戳>_genN.md`（每代弱项 + 推荐动作 + Pareto 快照） | 是 | `arena/ledger.py` |
| 最近一次运行的可读快照 | `reports/arena/evolution_report.{md,json}`（每次覆盖，演示用） | 是 | `arena/evolution.py` |
| 临时/草稿输出 | `runs/`、`outputs/` | 否（gitignore） | — |

- 复用既有目录（`theories/`、`plans/`、`reports/`），**不新增空目录**。
- `evolve()` 默认 `lineage_root=None`/`plan_dir=None`（库与测试调用不碰仓库）；CLI `cosmogenesis evolve` 默认开启（`--no-record` 关闭，`--persist-forks` 连同新 fork 的 theory.yaml 一并落盘成为正式谱系）。

## 增加一个新方案的标准步骤

1. 新建 `cosmogenesis/schemes/<new_name>/`，实现 `engine.py`(assess) 与 `optimizer.py`(optimize)，在子包 `__init__.py` 设 `SCHEME_NAME`。
2. 在 `cosmogenesis/schemes/__init__.py` 的 `SCHEME_REGISTRY` 注册。
3. 新建 `theories/T-NNNN_<family>/theory.yaml`，`engine: <new_name>`。
4. 跑 `genesis-arena evolve`，它自动并入对抗与 Pareto 生态。

无需改动 arena 任何代码——这是「长期多方案并行不混乱」的关键。
