# QuantaEngine 代码库评估报告

## 1. 评估元数据

| 字段 | 值 |
|---|---|
| Review ID | `QE-REVIEW-2026-06-21` |
| 评估日期 | 2026-06-21 |
| 基线提交 | `6050e48e095fc87770c7b1e02fc1883f675fe5b3` |
| 分支 | `main` |
| 评估范围 | `quanta_engine`、`quantaengine_lattice`、`cosmogenesis`、tests、CI、持久化和双远端状态 |
| 评估方式 | 静态审查、单元/集成测试、覆盖率、类型检查、格式检查、独立进程复现、并发复现 |
| 代码修改 | 无；本报告仅记录评估结果 |
| 总体结论 | 分层架构和测试基础良好，但 arena 的并发、novelty、复现性和评分闭环尚不足以支撑可信长期演化 |

## 2. 摘要

仓库已经形成三个边界清楚的子系统：有效物理主管线、独立格点原型和多方案对抗平台。Pydantic schema、统一参数向量、方案协议、理论谱系、81 项测试和结构化文档构成了不错的工程基础。

当前主要风险集中在 `cosmogenesis.arena`：并行 duel 会竞争写入同一个 registry；novelty 算法把自身保留在最近邻集合；随机种子依赖 Python 进程哈希；对抗裁决没有真正进入选择分数。这些问题会让长期历史和演化结果无法可靠解释或重放。

## 3. 验证基线

| 检查 | 结果 | 说明 |
|---|---|---|
| `python -m pytest` | 通过 | `81 passed` |
| 覆盖率 | 通过但有缺口 | 总体 85%；`PatchGate` 62%；`cosmogenesis.cli` 0% |
| `ruff check` | 通过 | lint 无错误 |
| `ruff format --check` | 失败 | 7 个文件需要格式化 |
| `mypy src` | 失败 | 4 个错误，位于 agents、duel、evolution |
| `python -m cosmogenesis theory-list` | 通过 | 三个理论可列出 |
| `python -m cosmogenesis score` | 通过 | CLI 可运行，但未展示 novelty |
| 工作区 | 干净 | `main...origin/main` |
| origin/main | `6050e48` | 当前代码基线 |
| quantaengine/main | `ac26132` | 评估时落后三个提交 |

### 3.1 Mypy 错误

- `arena/agents.py:67`：`max(..., key=profile.get)` 类型不兼容。
- `arena/duel.py:78-79`：线程池 lambda 类型无法推断。
- `arena/evolution.py:88`：利用 `set.add()` 返回 `None` 去重，类型检查失败。

### 3.2 格式检查缺口

需要格式化的文件包括 `agents.py`、`evolution.py`、`patchgate.py`、`verifier.py`、`cosmogenesis/cli.py`、variational engine 和 `test_arena.py`。

## 4. Findings 总表

| ID | 严重度 | 状态 | 问题 | 主要影响 |
|---|---|---|---|---|
| `QE-2026-001` | P1 | open | 并行 tournament 竞争写 registry | fork/patch 丢失、ID 冲突、历史不可信 |
| `QE-2026-002` | P1 | open | novelty 始终为零 | novelty archive 和多样性选择失效 |
| `QE-2026-003` | P1 | open | RNG 使用 salted `hash()` | 跨进程结果不可复现 |
| `QE-2026-004` | P1 | open | 裁决结果未进入评分 | 对抗层与演化选择没有闭环 |
| `QE-2026-005` | P1 | open | 旧 Python API 兼容性被破坏 | 现有用户升级后 import 失败 |
| `QE-2026-006` | P2 | open | theory/config 依赖 cwd | 安装后无法从任意目录运行 |
| `QE-2026-007` | P2 | open | `Axis.log` 未实现 | 重力搜索几何严重偏斜 |
| `QE-2026-008` | P2 | planned | CI、版本和双远端不一致 | 缺陷未被门禁阻止，发布状态分叉 |

## 5. 详细问题

### QE-2026-001：并行 tournament 会丢失 registry 更新

**严重度：P1　状态：open　类别：concurrency**

相关代码：

- [`arena/tournament.py`](../../src/cosmogenesis/arena/tournament.py#L34-L42) 并发运行所有理论对。
- [`arena/registry.py`](../../src/cosmogenesis/arena/registry.py#L14-L15) 无锁覆盖 theory。
- [`arena/registry.py`](../../src/cosmogenesis/arena/registry.py#L29-L31) 通过扫描当前字典分配下一个 ID。
- [`arena/patchgate.py`](../../src/cosmogenesis/arena/patchgate.py#L87-L101) 在 duel 线程内分配并写入 child。

同一 theory 会同时出现在多个 pair 中，各 duel 从旧快照开始并写入共享 registry。最后完成的线程会覆盖较早 patch；两个 fork 也可能取得同一 ID。

复现实验结果：

```text
并发 fork child IDs: ['T-0004', 'T-0004']
registry 最终只剩一个 T-0004 child
```

建议修复：duel 只生成不可变事件，不直接改 registry；tournament 完成计算后，由单线程 deterministic reducer 统一排序、分配 ID、合并同一 theory 的 patch 决策并提交。

验收标准：

- 100 个并发 fork 不产生重复 ID。
- `parallel=True/False` 在相同 seed 下产生相同 registry、事件和报告。
- 同一 theory 的多个 patch 不丢失，冲突有明确规则。

### QE-2026-002：novelty 目标始终为零

**严重度：P1　状态：open　类别：scoring**

相关代码：[`arena/tournament.py`](../../src/cosmogenesis/arena/tournament.py#L50-L57)、[`arena/scoring.py`](../../src/cosmogenesis/arena/scoring.py#L148-L157)。

`feats` 每次都是新 list，再使用 `f is not feats` 排除自身。因为对象身份永远不同，自身向量仍在 archive，最近距离为零，最终 novelty 为零。

复现实验结果：

```text
T-0001 novelty=0.0
T-0002 novelty=0.0
T-0003 novelty=0.0
reports/arena/evolution_report.json archive_ids=[]
```

建议修复：按 theory ID 或索引排除自身；使用 `bridge.novelty_features()` 的行为特征而不是只比较参数；明确 novelty archive 是跨代还是当代 archive。

验收标准：

- 两个不同特征的 theory novelty 大于零。
- 自身不会出现在自己的邻居集合。
- 至少一个满足阈值的有效理论进入 archive。
- 当前历史、报告和重跑结果中的 novelty 一致。

### QE-2026-003：跨进程随机结果不可复现

**严重度：P1　状态：open　类别：reproducibility**

相关代码：[`arena/scoring.py`](../../src/cosmogenesis/arena/scoring.py#L64-L76)、[`arena/agents.py`](../../src/cosmogenesis/arena/agents.py#L97-L104)、[`arena/patchgate.py`](../../src/cosmogenesis/arena/patchgate.py#L110-L128)。

代码使用 `abs(hash(text))` 作为 NumPy seed。Python 默认对字符串 hash 加进程级随机盐，因此相同输入在不同进程中产生不同随机序列。并行 challenge ID 还依赖全局计数器和调度顺序。

复现实验中，同一 `T-0001 v0.1.0` 在不同 `PYTHONHASHSEED` 下得到显著不同的 robust reseed 参数。

建议修复：使用 SHA-256/Blake2 从 `run_seed + theory_id + version + operation` 派生 32 位 seed；challenge/event ID 从稳定输入摘要产生；历史记录 run seed、代码提交和输入文件哈希。

验收标准：

- 不同 `PYTHONHASHSEED`、不同进程和串并行模式输出相同。
- 保存的历史可通过记录的 seed、commit 和 config hash 精确重放。

### QE-2026-004：对抗裁决没有进入演化评分

**严重度：P1　状态：open　类别：adversarial-loop**

[`arena/scoring.py`](../../src/cosmogenesis/arena/scoring.py#L40-L53) 定义了 `unresolved_challenge_penalty`，但 [`arena/tournament.py`](../../src/cosmogenesis/arena/tournament.py#L46-L48) 对所有 theory 都用默认零值调用 `score_theory()`。JudgeResult、未解决挑战和 defense 表现没有汇总到 selection。

结果是对抗只可能触发 patch/fork；`CHALLENGE_UPHELD_NO_PATCH`、`NEEDS_MORE_TESTS` 等裁决不会降低分数，也不会改变 Pareto front。

建议修复：按 target 聚合 judge severity、reproduced 状态、defense 质量和未解决期限，形成结构化 penalty；在评分、history 和报告中同时保存原始值与聚合值。

验收标准：同一 theory 在新增可复现且未解决的 major challenge 后 display score 下降，并能改变 Pareto/selection 结果。

### QE-2026-005：旧 Python API 兼容性破坏且版本不一致

**严重度：P1　状态：open　类别：compatibility**

README 声称旧 API 保持兼容，但源码包已从 `quantaengine` 改名为 `quantaengine_lattice`。在干净 `PYTHONPATH=src` 环境中执行 `import quantaengine` 会得到 `ModuleNotFoundError`。

同时 [`pyproject.toml`](../../pyproject.toml#L7) 的发行版是 `0.2.0`，而 [`cosmogenesis/__init__.py`](../../src/cosmogenesis/__init__.py#L55) 声明 `0.3.0`。

建议修复：短期增加 `quantaengine` deprecation shim；中期统一单一版本来源并发布 `0.3.0`，在 changelog 中明确迁移周期和移除版本。

验收标准：旧 import 和控制台入口均通过兼容测试；所有包、wheel metadata 和 CLI 显示相同版本。

### QE-2026-006：理论配置无法脱离仓库 cwd

**严重度：P2　状态：open　类别：portability**

[`arena/theory.py`](../../src/cosmogenesis/arena/theory.py#L55-L59) 保存裸相对 `base_config`，[`arena/bridge.py`](../../src/cosmogenesis/arena/bridge.py#L18-L26) 从当前进程目录解析，CLI 也硬编码 `theories`。

从临时目录加载绝对 theory 文件后评估，实际失败于：

```text
FileNotFoundError: .../Temp/.../configs/standard_universe.yaml
```

建议修复：加载 theory 时把配置解析为相对 theory 文件、显式 workspace root 或资源 URI；将默认 configs/theories 作为 package data，CLI 增加 `--workspace`。

验收标准：安装 wheel 后可从任意目录运行 theory-list、score、duel 和 evolve。

### QE-2026-007：对数搜索轴未按对数空间归一化

**严重度：P2　状态：open　类别：optimization**

[`core/parameters.py`](../../src/cosmogenesis/core/parameters.py#L16-L28) 声明 `Axis.log`，但 [`to_normalized/from_normalized`](../../src/cosmogenesis/core/parameters.py#L79-L93) 始终采用线性映射。重力范围 `0.01..100` 中，标准值 1 位于归一化坐标约 0.01，局部步长会直接跳到数量级十几。

建议修复：对 log axis 使用 `log10(value)` 归一化；统一 primordial amplitude 的内部/配置表示，避免某些轴储存 raw、某些轴储存 log。

验收标准：每个数量级在归一化空间占相同距离；round-trip、边界和 optimizer 收敛测试通过。

### QE-2026-008：工程门禁、版本和双远端发布不一致

**严重度：P2　状态：planned　类别：engineering-release**

CI 只运行 pytest 和 MVP 验收，不执行全量 Ruff、format 和 Mypy。[`tests.yml`](../../.github/workflows/tests.yml#L21-L27)。README 的 Mypy 命令也只检查 `src/quanta_engine`，遗漏新 `cosmogenesis`。

评估时 origin 为 `6050e48`，组织远端仍为 `ac26132`，GenesisArena 三个提交尚未镜像。发布本报告时应同步两个远端并验证哈希。

建议修复：增加独立 `quality` job；检查 `ruff check`、`ruff format --check`、`mypy src`、wheel build、CLI smoke；发布脚本同时验证两个远端。

验收标准：所有门禁在 Python 3.11 至 3.13 通过；本地、origin 和 quantaengine 的 `main` 哈希一致。

## 6. 优化路线

### Phase 0：结果可信性

目标 finding：`QE-2026-001` 至 `QE-2026-004`。

1. 引入 immutable duel events 和单线程 registry reducer。
2. 使用稳定摘要种子和可重放 run manifest。
3. 修复 novelty，自身排除并转向行为特征。
4. 将 judge/defense/unresolved challenge 接入评分和选择。
5. 增加串并行一致性、跨进程复现和事件冲突测试。

完成标准：同一 run manifest 在不同进程、机器和并行模式下生成同一理论版本、分数、archive 和历史。

### Phase 1：兼容和可移植发布

目标 finding：`QE-2026-005`、`QE-2026-006`。

1. 增加旧包 shim 和迁移告警。
2. 统一版本来源并升级发行版本。
3. 规范 workspace/resource 路径和 package data。
4. 增加 wheel 安装后、非仓库 cwd 的 CLI E2E。

### Phase 2：优化器与科学可解释性

目标 finding：`QE-2026-007`。

1. 正确实现 log 参数几何。
2. 对 assessment 增加缓存和批处理，减少 tournament 重复求值。
3. 给 scoring 权重、窗口阈值和残差加入敏感性/不确定性报告。
4. 将 novelty 拆分为参数 novelty、行为 novelty 和谱系 novelty。

### Phase 3：工程质量与发布

目标 finding：`QE-2026-008`。

1. CI 增加 lint、format、全量 typing、build 和 CLI smoke。
2. 将 `PatchGate` 覆盖率提升到至少 85%，覆盖冲突、并发和持久化失败。
3. 为 `cosmogenesis.cli` 增加 Typer CliRunner 测试。
4. 发布时同步两个远端并记录 CI URL。

## 7. 正向评价

- `core / schemes / arena` 的目录边界清楚，新增 scheme 的扩展点明确。
- Pydantic cards 和 theory schema 为后续外部 agent/LLM 接入提供了良好边界。
- 三种 scheme 在计算路径上确实不同，不是简单换权重。
- 81 项测试和 85% 总体覆盖率提供了可用的回归基础。
- 方案、执行记录、理论历史和自动迭代计划已经形成初步可追踪链路。

## 8. 评估限制

- 本次没有对物理模型做外部论文级数值校准。
- 没有运行长时间、多进程或故障注入压力测试。
- 没有审查 GitHub 权限、分支保护和发布签名配置。
- 复现实验针对核心代码路径，未修改仓库文件。

## 9. 后续复审模板

每个 finding 修复后记录：

```text
Finding ID:
修复提交:
状态: fixed / verified / accepted-risk
实现摘要:
原复现命令结果:
新增回归测试:
跨进程/并行证据:
CI URL:
剩余风险:
```

复审应创建新报告并链接本文件，保留 `6050e48` 基线事实不变。
