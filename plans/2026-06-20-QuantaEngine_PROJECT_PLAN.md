# QuantaEngine / GenesisEngine 可执行项目执行方案

版本：v1.0
目标文件：`PROJECT_PLAN.md`
定位：给 AI Coding Agent、人工开发者、项目负责人共同使用的端到端执行规划。
核心目标：从物理最基本原理、作用量、常数、初始条件出发，通过多尺度有效理论逐层生成一个自洽宇宙，并输出稳定原子、恒星、结构形成、复杂化学、生命窗口和文明潜力等指标。

---

## 0. 项目总目标

本项目不是直接从标准模型拉氏量暴力模拟到生命和文明，而是实现一个“物理规则编译器 + 多尺度宇宙模拟器”。

核心路径：

```text
基本公理
→ 作用量 / 拉氏量
→ 粒子谱与相互作用表
→ 宇宙热史
→ 粒子冻结 / 核合成
→ 原子与化学窗口
→ 恒星与结构形成
→ 复杂性 / 生命窗口 / 文明潜力
```

项目最终应支持：

```text
输入一组宇宙基本规则：
- 时空维度
- 引力模型
- 场内容
- 规范群
- 基本常数
- 初始条件
- 有效物理参数

输出一个宇宙报告：
- 基本物理是否自洽
- 是否有稳定粒子
- 是否有稳定原子
- 是否能形成原子核
- 是否能形成恒星
- 是否能产生重元素
- 是否存在复杂化学窗口
- 是否存在生命可行窗口
- 是否存在文明演化窗口
- 与标准宇宙相比的主要差异
```

---

## 1. 项目设计原则

### 1.1 分层有效理论原则

不要试图从夸克胶子直接模拟到人类文明。每一层只接收上一层的有效输出。

```text
高能粒子层输出：粒子质量、寿命、相互作用强度
↓
核物理层输入：质子/中子/轻核有效参数
↓
原子层输入：电子质量、精细结构常数、核电荷
↓
恒星层输入：核反应率、引力常数、辐射输运近似
↓
复杂性层输入：元素丰度、能量梯度、环境稳定时间
```

### 1.2 可替换物理模块原则

每一层允许不同精度模型：

```text
toy model      # 快速、可解释、用于扫描参数
analytic       # 半解析近似
numerical      # 数值求解
external       # 未来接入 CLASS、GADGET、MadGraph、PYTHIA、Geant4 等
```

第一版优先实现 toy + analytic，不追求高保真。

### 1.3 可验证原则

每个模块必须有：

```text
输入 schema
输出 schema
单位检查
边界检查
物理一致性检查
单元测试
端到端测试
```

### 1.4 AI 可执行原则

每个开发任务必须明确：

```text
任务目标
输入文件
需要创建/修改的文件
核心算法
测试命令
验收标准
失败时诊断方法
```

---

## 2. 推荐技术栈

### 2.1 第一版语言

```text
Python 3.11+
```

原因：

```text
- 科学计算生态成熟
- AI Coding Agent 容易生成和维护
- 适合快速原型
- 后续可把性能瓶颈迁移到 C++/Rust
```

### 2.2 核心依赖

```toml
[project]
dependencies = [
  "numpy",
  "scipy",
  "pydantic",
  "pyyaml",
  "matplotlib",
  "pandas",
  "rich",
  "typer",
  "pytest",
  "hypothesis"
]
```

### 2.3 可选依赖

```toml
[project.optional-dependencies]
dev = [
  "ruff",
  "mypy",
  "pytest-cov"
]

docs = [
  "mkdocs",
  "mkdocs-material"
]
```

---

## 3. 目标仓库结构

```text
quanta-engine/
├── README.md
├── PROJECT_PLAN.md
├── pyproject.toml
├── configs/
│   ├── standard_universe.yaml
│   ├── strong_alpha_universe.yaml
│   ├── weak_gravity_universe.yaml
│   ├── no_stable_atoms_universe.yaml
│   └── long_lived_stars_universe.yaml
├── src/
│   └── quanta_engine/
│       ├── __init__.py
│       ├── cli.py
│       ├── core/
│       │   ├── constants.py
│       │   ├── units.py
│       │   ├── dimensions.py
│       │   ├── schema.py
│       │   └── result.py
│       ├── axioms/
│       │   ├── axioms.py
│       │   ├── symmetries.py
│       │   └── consistency.py
│       ├── fields/
│       │   ├── particles.py
│       │   ├── interactions.py
│       │   ├── lagrangian.py
│       │   └── spectrum.py
│       ├── cosmology/
│       │   ├── friedmann.py
│       │   ├── thermal_history.py
│       │   ├── perturbations.py
│       │   └── epochs.py
│       ├── nuclear/
│       │   ├── bbn.py
│       │   ├── binding.py
│       │   └── stability.py
│       ├── atomic/
│       │   ├── hydrogen.py
│       │   ├── atoms.py
│       │   └── chemistry_window.py
│       ├── stars/
│       │   ├── stellar_scaling.py
│       │   ├── fusion.py
│       │   └── lifetime.py
│       ├── structure/
│       │   ├── halos.py
│       │   ├── galaxies.py
│       │   └── planets.py
│       ├── complexity/
│       │   ├── habitability.py
│       │   ├── life_window.py
│       │   └── civilization.py
│       ├── validation/
│       │   ├── conservation.py
│       │   ├── dimensional.py
│       │   ├── numerical.py
│       │   └── report.py
│       └── experiments/
│           ├── scan.py
│           ├── compare.py
│           └── sensitivity.py
├── examples/
│   ├── run_standard_universe.py
│   ├── scan_alpha.py
│   ├── scan_gravity.py
│   └── compare_universes.py
├── tests/
│   ├── test_units.py
│   ├── test_config_schema.py
│   ├── test_atomic.py
│   ├── test_cosmology.py
│   ├── test_stars.py
│   ├── test_validation.py
│   └── test_e2e_universe.py
└── docs/
    ├── architecture.md
    ├── physics_assumptions.md
    ├── api_reference.md
    └── examples.md
```

---

## 4. 第一版 MVP 范围

### 4.1 必须实现

MVP 不实现完整标准模型符号推导，而是实现一个可运行的有效宇宙生成管线：

```text
config.yaml
→ UniverseConfig
→ FundamentalParameters
→ ParticleEffectiveModel
→ CosmologyModel
→ NuclearModel
→ AtomicModel
→ StellarModel
→ StructureModel
→ ComplexityEvaluator
→ UniverseReport
```

### 4.2 暂不实现

```text
- 完整量子场论符号变分
- 自动从任意拉氏量生成 Feynman rules
- 完整 QCD confinement
- 完整 BBN 网络
- 完整 N-body 宇宙学模拟
- 完整化学反应网络
- 真实生物演化
- 文明个体级 agent simulation
```

### 4.3 MVP 的科学目标

MVP 应能回答：

```text
给定一组基础常数变化后：
1. 氢原子是否稳定？
2. 原子尺度如何变化？
3. 化学能标如何变化？
4. 恒星是否能燃烧？
5. 恒星寿命是否足够长？
6. 是否有重元素生成窗口？
7. 是否存在复杂化学和生命窗口？
```

---

## 5. 配置文件设计

### 5.1 标准宇宙配置

文件：`configs/standard_universe.yaml`

```yaml
universe:
  name: standard_universe
  description: Effective low-energy approximation of our universe.

spacetime:
  dimensions: 4
  metric_signature: "-+++"
  gravity_model: friedmann
  curvature_k: 0.0

constants:
  c: 299792458.0
  hbar: 1.054571817e-34
  G: 6.67430e-11
  k_B: 1.380649e-23

dimensionless:
  alpha: 0.0072973525693
  gravity_scale: 1.0
  strong_scale: 1.0
  weak_scale: 1.0
  cosmological_constant_scale: 1.0

particles:
  electron_mass_MeV: 0.51099895
  proton_mass_MeV: 938.27208816
  neutron_mass_MeV: 939.56542052
  pion_mass_MeV: 139.57039

cosmology:
  H0_km_s_Mpc: 67.4
  omega_b: 0.049
  omega_cdm: 0.265
  omega_lambda: 0.686
  primordial_amplitude: 2.1e-9
  scalar_spectral_index: 0.965

nuclear:
  deuteron_binding_MeV: 2.224566
  helium4_binding_MeV: 28.295674
  bbn_model: toy

atomic:
  model: hydrogenic
  require_stable_hydrogen: true

stellar:
  model: scaling
  min_lifetime_years_for_complexity: 1.0e9
  require_hydrogen_fusion: true

complexity:
  require_stable_atoms: true
  require_long_lived_stars: true
  require_heavy_elements: true
  require_energy_gradients: true
```

### 5.2 参数扫描配置

文件：`configs/strong_alpha_universe.yaml`

```yaml
universe:
  name: strong_alpha_universe
  description: Universe with stronger electromagnetic coupling.

inherit: standard_universe.yaml

dimensionless:
  alpha_scale: 1.2
```

### 5.3 AI 编码要求

AI 必须实现：

```text
- 支持 inherit 字段
- 支持 scale 参数覆盖标准值
- 支持 config validation
- 支持缺失字段的清晰错误
```

---

## 6. 阶段 0：项目骨架与基础工程

### 6.1 输入

```text
- 本 PROJECT_PLAN.md
- Python 3.11+
- 空 GitHub 仓库
```

### 6.2 策略

建立可测试、可安装、可运行的 Python package。

### 6.3 输出

```text
- pyproject.toml
- src/quanta_engine/
- tests/
- configs/
- README.md
- CLI 命令 quanta
```

### 6.4 具体开发任务

#### Task 0.1 创建 Python 项目骨架

AI Prompt：

```text
Create a Python 3.11 package named quanta_engine using src layout.
Add pyproject.toml with dependencies: numpy, scipy, pydantic, pyyaml, matplotlib, pandas, rich, typer, pytest, hypothesis.
Create src/quanta_engine/__init__.py and src/quanta_engine/cli.py.
Implement a Typer CLI with command:
  quanta --version
  quanta validate-config configs/standard_universe.yaml
  quanta run configs/standard_universe.yaml
Add pytest setup and one smoke test.
```

验收标准：

```text
pip install -e .
quanta --version
pytest
```

必须全部通过。

#### Task 0.2 创建 README

输入：

```text
项目目标说明
MVP 范围
命令示例
```

输出：

```text
README.md
```

验收标准：

```text
README 说明：
- 项目是什么
- 不是什么
- 如何安装
- 如何运行标准宇宙
- 如何运行参数扫描
```

---

## 7. 阶段 1：核心数据结构与配置系统

### 7.1 输入

```text
configs/*.yaml
```

### 7.2 策略

使用 Pydantic 定义强类型配置模型。

### 7.3 输出

```text
UniverseConfig
ConstantsConfig
ParticleConfig
CosmologyConfig
NuclearConfig
AtomicConfig
StellarConfig
ComplexityConfig
```

### 7.4 文件

```text
src/quanta_engine/core/schema.py
src/quanta_engine/core/constants.py
src/quanta_engine/core/result.py
src/quanta_engine/core/units.py
tests/test_config_schema.py
tests/test_units.py
```

### 7.5 具体开发任务

#### Task 1.1 配置 schema

AI Prompt：

```text
Implement Pydantic models for the universe YAML config.
The top-level model should be UniverseConfig with sections:
- universe
- spacetime
- constants
- dimensionless
- particles
- cosmology
- nuclear
- atomic
- stellar
- complexity

Support optional "inherit" field. Implement load_config(path) that:
1. loads YAML
2. if inherit exists, loads parent config from same directory
3. deep merges parent and child
4. validates with UniverseConfig
5. returns UniverseConfig

Add tests:
- standard_universe.yaml loads successfully
- child config overrides alpha_scale
- missing required fields raise helpful errors
```

输入：

```text
configs/standard_universe.yaml
configs/strong_alpha_universe.yaml
```

输出：

```text
load_config(path) -> UniverseConfig
```

验收：

```text
pytest tests/test_config_schema.py
```

#### Task 1.2 单位和常数模块

AI Prompt：

```text
Implement constants and simple unit conversion helpers.
Required:
- MeV_to_kg
- kg_to_MeV
- eV_to_J
- J_to_eV
- year_to_second
- Mpc_to_meter
- dimensionless scale helper

Add tests for known conversions within relative tolerance.
```

输出：

```text
src/quanta_engine/core/units.py
```

验收：

```text
pytest tests/test_units.py
```

---

## 8. 阶段 2：物理一致性验证层

### 8.1 输入

```text
UniverseConfig
```

### 8.2 策略

先实现轻量级一致性检查，不做完整规范理论证明。

### 8.3 输出

```text
ValidationReport
- passed: bool
- errors: list[str]
- warnings: list[str]
- scores: dict[str, float]
```

### 8.4 文件

```text
src/quanta_engine/validation/report.py
src/quanta_engine/validation/dimensional.py
src/quanta_engine/validation/numerical.py
src/quanta_engine/validation/conservation.py
tests/test_validation.py
```

### 8.5 检查项

```text
- 常数为正
- 质量为正
- alpha 在合理区间
- G 为正
- omega 总和近似合理
- deuteron binding 为正
- helium binding 为正
- min stellar lifetime 为正
```

### 8.6 具体开发任务

#### Task 2.1 ValidationReport

AI Prompt：

```text
Create ValidationReport dataclass or Pydantic model.
Implement methods:
- add_error(message)
- add_warning(message)
- add_score(name, value)
- passed property
- to_markdown()

Add unit tests.
```

#### Task 2.2 Universe config validation

AI Prompt：

```text
Implement validate_universe_config(config: UniverseConfig) -> ValidationReport.
Check numerical ranges and return warnings/errors.
Do not crash on bad physics; return a structured report.
Add tests for:
- valid standard universe
- negative mass
- alpha too large
- omega sum warning
```

---

## 9. 阶段 3：粒子有效模型

### 9.1 输入

```text
UniverseConfig.particles
UniverseConfig.dimensionless
```

### 9.2 策略

先不从完整标准模型拉氏量自动推导粒子谱，而是建立 EffectiveParticleModel。

### 9.3 输出

```text
ParticleSpectrum
- electron
- proton
- neutron
- photon
- neutrino_effective
- helium4
- deuteron
```

每个粒子包括：

```text
name
mass_MeV
charge_e
stable_bool
lifetime_s or None
category
```

### 9.4 文件

```text
src/quanta_engine/fields/particles.py
src/quanta_engine/fields/spectrum.py
tests/test_particles.py
```

### 9.5 具体开发任务

#### Task 3.1 Particle 数据结构

AI Prompt：

```text
Implement Particle and ParticleSpectrum models.
Particle fields:
- name: str
- mass_MeV: float
- charge_e: float
- stable: bool
- lifetime_s: float | None
- category: str

ParticleSpectrum should support:
- get(name)
- list_stable()
- total_known_particles()
- to_dataframe()
- to_markdown_table()

Add build_effective_particle_spectrum(config) that creates photon, electron, proton, neutron, deuteron, helium4.
```

验收：

```text
pytest tests/test_particles.py
```

---

## 10. 阶段 4：原子稳定性模块

### 10.1 输入

```text
alpha
electron_mass
proton_mass
hbar
c
```

### 10.2 策略

使用氢原子 Bohr 模型 + 简单相对论稳定性判据。

### 10.3 输出

```text
AtomicReport
- bohr_radius_m
- binding_energy_eV
- rydberg_energy_eV
- electron_velocity_over_c
- stable_hydrogen: bool
- chemistry_energy_scale_eV
- warnings
```

### 10.4 物理公式

约化质量：

\[
\mu = \frac{m_e m_p}{m_e + m_p}
\]

Bohr 半径：

\[
a_0 = \frac{\hbar}{\mu c \alpha}
\]

氢原子结合能：

\[
E_1 = -\frac{1}{2}\mu c^2 \alpha^2
\]

电子典型速度：

\[
v/c \sim \alpha
\]

简单稳定判据：

```text
alpha < 1
binding_energy_eV > 0
bohr_radius_m > 0
electron_mass > 0
proton_mass > electron_mass
```

### 10.5 文件

```text
src/quanta_engine/atomic/hydrogen.py
src/quanta_engine/atomic/chemistry_window.py
tests/test_atomic.py
```

### 10.6 具体开发任务

#### Task 4.1 Hydrogen atom model

AI Prompt：

```text
Implement compute_hydrogen_properties(config) -> AtomicReport.

Use:
- alpha from config.dimensionless.alpha times alpha_scale if present
- electron/proton masses from config.particles
- hbar and c from config.constants
- unit conversions from core.units

Return:
- bohr_radius_m
- binding_energy_eV
- electron_velocity_over_c
- stable_hydrogen bool
- chemistry_energy_scale_eV

Add tests:
- standard universe binding energy is approximately 13.6 eV
- Bohr radius is approximately 5.29e-11 m
- alpha > 1 gives unstable warning
```

验收：

```text
pytest tests/test_atomic.py
```

---

## 11. 阶段 5：核物理与轻元素窗口

### 11.1 输入

```text
proton_mass
neutron_mass
deuteron_binding
helium4_binding
strong_scale
weak_scale
```

### 11.2 策略

第一版不做完整 BBN 网络，只判断轻核稳定窗口。

### 11.3 输出

```text
NuclearReport
- neutron_proton_mass_difference_MeV
- deuteron_stable
- helium4_stable
- hydrogen_available
- helium_available
- heavy_element_seed_possible
- warnings
```

### 11.4 简单判据

```text
deuteron_binding_MeV > 0 → deuteron_stable
helium4_binding_MeV > 0 → helium4_stable
neutron_mass > proton_mass → free neutron beta decay allowed in our-like universe
if deuteron unstable → normal stellar nucleosynthesis severely suppressed
```

### 11.5 文件

```text
src/quanta_engine/nuclear/stability.py
src/quanta_engine/nuclear/bbn.py
tests/test_nuclear.py
```

### 11.6 具体开发任务

#### Task 5.1 Nuclear stability model

AI Prompt：

```text
Implement compute_nuclear_stability(config) -> NuclearReport.
Use a toy model:
- deuteron_stable = deuteron_binding_MeV * strong_scale > 0
- helium4_stable = helium4_binding_MeV * strong_scale > 0
- neutron_proton_mass_difference_MeV = neutron_mass - proton_mass
- hydrogen_available = proton_mass + electron_mass < neutron_mass or allow parameterized baryon chemistry
- heavy_element_seed_possible = deuteron_stable and helium4_stable

Add warnings if:
- deuteron unstable
- neutron lighter than proton
- helium4 unstable
```

验收：

```text
pytest tests/test_nuclear.py
```

---

## 12. 阶段 6：宇宙学热史模块

### 12.1 输入

```text
H0
omega_b
omega_cdm
omega_lambda
curvature_k
radiation density approximation
```

### 12.2 策略

实现 FLRW 背景宇宙求解，不做完整扰动和 CMB。

### 12.3 输出

```text
CosmologyReport
- age_of_universe_s
- age_of_universe_Gyr
- expansion_history_sample
- matter_radiation_equality_estimate
- accelerated_expansion_bool
- structure_growth_window_bool
```

### 12.4 方程

\[
H(a) = H_0 \sqrt{
\Omega_r a^{-4}
+
\Omega_m a^{-3}
+
\Omega_k a^{-2}
+
\Omega_\Lambda
}
\]

宇宙年龄：

\[
t_0 = \int_0^1 \frac{da}{aH(a)}
\]

### 12.5 文件

```text
src/quanta_engine/cosmology/friedmann.py
src/quanta_engine/cosmology/thermal_history.py
tests/test_cosmology.py
```

### 12.6 具体开发任务

#### Task 6.1 Friedmann solver

AI Prompt：

```text
Implement compute_friedmann_background(config) -> CosmologyReport.
Use scipy.integrate.quad to compute age:
t0 = integral from a_min=1e-8 to 1 of da/(a*H(a)).
Use H0 conversion from km/s/Mpc to 1/s.
Assume omega_r = 9e-5 unless provided.
omega_m = omega_b + omega_cdm.
omega_k = 1 - omega_r - omega_m - omega_lambda if curvature not explicitly set.

Return sampled expansion history for a = logspace(-4, 0, 200).
Add tests:
- standard universe age around 13.8 Gyr within broad tolerance
- increasing omega_lambda changes accelerated_expansion_bool
- bad negative density gives validation error or warning
```

验收：

```text
pytest tests/test_cosmology.py
```

---

## 13. 阶段 7：恒星可行性模块

### 13.1 输入

```text
G
alpha
electron_mass
proton_mass
nuclear_report
atomic_report
cosmology_report
```

### 13.2 策略

使用简化尺度关系判断恒星能否形成、燃烧和长期稳定。

### 13.3 输出

```text
StellarReport
- hydrogen_fusion_possible
- long_lived_stars_possible
- characteristic_stellar_lifetime_years
- stellar_energy_window_score
- heavy_element_production_possible
- warnings
```

### 13.4 简化判据

第一版使用启发式：

```text
hydrogen_fusion_possible =
    stable_hydrogen
    and deuteron_stable
    and helium4_stable
    and gravity_scale within broad range
    and alpha < 0.2

long_lived_stars_possible =
    characteristic_lifetime_years > min_lifetime_years_for_complexity

heavy_element_production_possible =
    hydrogen_fusion_possible
    and helium4_stable
    and stellar lifetime not too short
```

### 13.5 文件

```text
src/quanta_engine/stars/fusion.py
src/quanta_engine/stars/stellar_scaling.py
src/quanta_engine/stars/lifetime.py
tests/test_stars.py
```

### 13.6 具体开发任务

#### Task 7.1 Stellar window model

AI Prompt：

```text
Implement compute_stellar_window(config, atomic_report, nuclear_report, cosmology_report) -> StellarReport.

Use a transparent toy model:
- baseline_lifetime = 1e10 years
- lifetime scales inversely with gravity_scale^2
- lifetime also decreases if alpha_scale is too high
- fusion possible only if nuclear_report.heavy_element_seed_possible and atomic_report.stable_hydrogen
- long_lived_stars_possible if lifetime > config.stellar.min_lifetime_years_for_complexity
- heavy_element_production_possible if fusion possible and lifetime > 1e6 years

Document clearly that this is a first-order habitability heuristic, not a stellar evolution code.

Add tests:
- standard universe has fusion and long-lived stars
- no stable deuteron suppresses fusion
- very strong gravity makes lifetime too short
```

验收：

```text
pytest tests/test_stars.py
```

---

## 14. 阶段 8：结构形成与行星窗口

### 14.1 输入

```text
cosmology_report
stellar_report
omega_m
primordial_amplitude
stellar lifetime
heavy element flag
```

### 14.2 策略

第一版使用指标模型，不做 N-body。

### 14.3 输出

```text
StructureReport
- structure_growth_possible
- galaxy_formation_possible
- planet_formation_possible
- metallicity_window_score
- stable_orbits_possible
- warnings
```

### 14.4 简化判据

```text
structure_growth_possible =
    primordial_amplitude > lower_bound
    and omega_m > lower_bound
    and universe_age > minimum_growth_time

galaxy_formation_possible =
    structure_growth_possible
    and not dark_energy_dominates_too_early

planet_formation_possible =
    galaxy_formation_possible
    and heavy_element_production_possible
```

### 14.5 文件

```text
src/quanta_engine/structure/halos.py
src/quanta_engine/structure/galaxies.py
src/quanta_engine/structure/planets.py
tests/test_structure.py
```

### 14.6 具体开发任务

#### Task 8.1 Structure window model

AI Prompt：

```text
Implement compute_structure_window(config, cosmology_report, stellar_report) -> StructureReport.

Use heuristic criteria:
- primordial_amplitude between 1e-7 and 1e-3 is favorable
- omega_m > 0.05
- age_of_universe_Gyr > 0.5
- planet formation requires heavy_element_production_possible

Add tests:
- standard universe passes
- zero primordial amplitude fails structure growth
- no heavy elements fails planet formation
```

---

## 15. 阶段 9：复杂性、生命窗口与文明潜力

### 15.1 输入

```text
AtomicReport
NuclearReport
CosmologyReport
StellarReport
StructureReport
```

### 15.2 策略

定义评分，不声称直接模拟生命。

### 15.3 输出

```text
ComplexityReport
- chemistry_score
- energy_gradient_score
- stability_score
- element_diversity_score
- life_window_score
- civilization_potential_score
- qualitative_summary
```

### 15.4 评分建议

```text
chemistry_score:
  stable_hydrogen
  reasonable binding energy
  alpha not too large
  atoms not too small or too large

energy_gradient_score:
  long_lived_stars
  fusion possible

stability_score:
  universe age
  stellar lifetime
  stable atoms
  stable nuclei

element_diversity_score:
  heavy element production
  planet formation

life_window_score:
  weighted combination

civilization_potential_score:
  life_window_score
  long-term stability
  energy gradients
  planet formation
```

### 15.5 文件

```text
src/quanta_engine/complexity/habitability.py
src/quanta_engine/complexity/life_window.py
src/quanta_engine/complexity/civilization.py
tests/test_complexity.py
```

### 15.6 具体开发任务

#### Task 9.1 Complexity evaluator

AI Prompt：

```text
Implement compute_complexity_report(config, atomic_report, nuclear_report, cosmology_report, stellar_report, structure_report) -> ComplexityReport.

Scores should be floats in [0, 1].
Use simple, documented weighted averages.
Return qualitative_summary:
- "sterile"
- "simple atoms only"
- "stellar but chemically poor"
- "complex chemistry possible"
- "life window plausible"
- "civilization window plausible"

Add tests:
- standard universe should score high
- unstable atoms score near zero
- no stars lowers energy_gradient_score
```

---

## 16. 阶段 10：UniversePipeline 总管线

### 16.1 输入

```text
config path
```

### 16.2 策略

串联所有模块，生成统一报告。

### 16.3 输出

```text
UniverseReport
- config_summary
- validation_report
- particle_spectrum
- atomic_report
- nuclear_report
- cosmology_report
- stellar_report
- structure_report
- complexity_report
- final_verdict
- markdown_report
- json_report
```

### 16.4 文件

```text
src/quanta_engine/core/result.py
src/quanta_engine/pipeline.py
src/quanta_engine/cli.py
tests/test_e2e_universe.py
```

### 16.5 具体开发任务

#### Task 10.1 Pipeline implementation

AI Prompt：

```text
Implement run_universe_pipeline(config_path: str | Path) -> UniverseReport.

Pipeline steps:
1. load_config
2. validate_universe_config
3. build_effective_particle_spectrum
4. compute_hydrogen_properties
5. compute_nuclear_stability
6. compute_friedmann_background
7. compute_stellar_window
8. compute_structure_window
9. compute_complexity_report
10. assemble UniverseReport

If validation has errors, still return a report but mark final_verdict as invalid.
Implement UniverseReport.to_markdown() and UniverseReport.to_json_dict().
```

验收：

```text
pytest tests/test_e2e_universe.py
quanta run configs/standard_universe.yaml
```

#### Task 10.2 CLI 输出

AI Prompt：

```text
Update cli.py with:
quanta run CONFIG --output reports/standard.md --json reports/standard.json
quanta validate-config CONFIG
quanta compare CONFIG_A CONFIG_B
quanta scan CONFIG --param dimensionless.alpha_scale --values 0.5,1.0,1.5

Use rich for terminal output.
```

验收：

```text
quanta run configs/standard_universe.yaml --output reports/standard.md --json reports/standard.json
```

---

## 17. 阶段 11：参数扫描与宇宙实验

### 17.1 输入

```text
base config
parameter name
parameter values
```

### 17.2 策略

运行多个宇宙，比较分数。

### 17.3 输出

```text
ScanReport
- table.csv
- plot.png
- markdown summary
```

### 17.4 文件

```text
src/quanta_engine/experiments/scan.py
src/quanta_engine/experiments/compare.py
src/quanta_engine/experiments/sensitivity.py
examples/scan_alpha.py
examples/scan_gravity.py
tests/test_scan.py
```

### 17.5 具体开发任务

#### Task 11.1 Parameter scan

AI Prompt：

```text
Implement scan_parameter(base_config_path, parameter_path, values) -> pandas.DataFrame.

parameter_path example:
- dimensionless.alpha_scale
- dimensionless.gravity_scale
- cosmology.primordial_amplitude

For each value:
- deep copy config
- set parameter
- run pipeline
- collect key outputs:
  stable_hydrogen
  hydrogen_binding_energy_eV
  stellar_lifetime_years
  structure_growth_possible
  life_window_score
  civilization_potential_score
  final_verdict

Add CLI support:
quanta scan configs/standard_universe.yaml --param dimensionless.alpha_scale --values 0.5,0.8,1.0,1.2,1.5 --output reports/scan_alpha.csv
```

验收：

```text
quanta scan configs/standard_universe.yaml --param dimensionless.alpha_scale --values 0.5,1.0,1.5
```

---

## 18. 端到端测试方案

### 18.1 E2E-1 标准宇宙

输入：

```text
configs/standard_universe.yaml
```

运行：

```bash
quanta run configs/standard_universe.yaml --output reports/standard.md --json reports/standard.json
```

预期输出：

```text
validation passed
stable hydrogen = true
hydrogen binding energy ≈ 13.6 eV
Bohr radius ≈ 5.29e-11 m
deuteron stable = true
helium4 stable = true
universe age ≈ 10–20 Gyr
hydrogen fusion possible = true
long lived stars possible = true
structure growth possible = true
life window score high
civilization potential nonzero/high
```

验收标准：

```text
- 命令 exit code = 0
- 生成 markdown report
- 生成 json report
- JSON 可被 Python json.load 读取
- final_verdict 不为 invalid
```

### 18.2 E2E-2 强电磁耦合宇宙

输入：

```text
configs/strong_alpha_universe.yaml
```

预期：

```text
alpha 增大
Bohr radius 变小
binding energy 变大
如果 alpha_scale 很大，稳定性警告增加
化学窗口可能变窄
```

验收：

```text
- 与 standard universe 的 atomic_report 数值不同
- compare 命令能显示差异
```

### 18.3 E2E-3 无稳定原子宇宙

配置：

```yaml
inherit: standard_universe.yaml
dimensionless:
  alpha_scale: 200.0
```

预期：

```text
alpha > 1
stable_hydrogen = false
chemistry_score 接近 0
life_window_score 接近 0
civilization_potential_score 接近 0
```

验收：

```text
- pipeline 不崩溃
- 报告明确说明失败原因
```

### 18.4 E2E-4 强引力短寿命恒星宇宙

配置：

```yaml
inherit: standard_universe.yaml
dimensionless:
  gravity_scale: 100.0
```

预期：

```text
恒星寿命显著缩短
long_lived_stars_possible = false 或 score 降低
life_window_score 降低
```

### 18.5 E2E-5 无初始扰动宇宙

配置：

```yaml
inherit: standard_universe.yaml
cosmology:
  primordial_amplitude: 0.0
```

预期：

```text
structure_growth_possible = false
galaxy_formation_possible = false
planet_formation_possible = false
life_window_score 显著降低
```

---

## 19. 测试矩阵

| 测试类型 | 命令 | 必须覆盖 |
|---|---|---|
| 单元测试 | `pytest tests/test_units.py` | 单位换算 |
| 配置测试 | `pytest tests/test_config_schema.py` | YAML 解析、继承、覆盖 |
| 原子测试 | `pytest tests/test_atomic.py` | 氢原子结合能、Bohr 半径 |
| 核物理测试 | `pytest tests/test_nuclear.py` | 氘核、氦核稳定性 |
| 宇宙学测试 | `pytest tests/test_cosmology.py` | Friedmann 年龄 |
| 恒星测试 | `pytest tests/test_stars.py` | 恒星窗口 |
| 结构测试 | `pytest tests/test_structure.py` | 星系/行星窗口 |
| 复杂性测试 | `pytest tests/test_complexity.py` | 生命/文明评分 |
| 端到端测试 | `pytest tests/test_e2e_universe.py` | 完整管线 |
| CLI 测试 | `quanta run ...` | 用户命令可用 |
| 扫描测试 | `quanta scan ...` | 多宇宙批量运行 |

---

## 20. 报告格式

### 20.1 Markdown 报告结构

`UniverseReport.to_markdown()` 输出：

```markdown
# Universe Report: standard_universe

## Final Verdict
civilization window plausible

## Validation
- Passed: true
- Errors: none
- Warnings: ...

## Fundamental Parameters
...

## Atomic Layer
- Stable hydrogen: true
- Bohr radius: ...
- Binding energy: ...

## Nuclear Layer
...

## Cosmology Layer
...

## Stellar Layer
...

## Structure Layer
...

## Complexity Layer
...

## Key Bottlenecks
...

## Comparison to Standard Universe
...
```

### 20.2 JSON 报告结构

```json
{
  "universe_name": "standard_universe",
  "final_verdict": "civilization window plausible",
  "validation": {
    "passed": true,
    "errors": [],
    "warnings": []
  },
  "atomic": {
    "stable_hydrogen": true,
    "binding_energy_eV": 13.6
  },
  "complexity": {
    "life_window_score": 0.87,
    "civilization_potential_score": 0.81
  }
}
```

---

## 21. AI Coding Agent 工作流

### 21.1 每个任务必须遵守的流程

```text
1. 阅读本 PROJECT_PLAN.md 中对应阶段
2. 只修改任务指定文件
3. 先写测试
4. 再写实现
5. 运行相关 pytest
6. 运行全量 pytest
7. 更新 README 或 docs 中必要说明
8. 给出变更摘要
```

### 21.2 AI 输出格式

每次 AI 完成任务后，必须输出：

```text
Changed files:
- ...

Implemented:
- ...

Tests:
- command: ...
- result: ...

Known limitations:
- ...

Next recommended task:
- ...
```

### 21.3 禁止事项

```text
- 不要引入未要求的大型外部依赖
- 不要把 toy model 写成真实高精度物理
- 不要删除已有测试
- 不要跳过配置验证
- 不要让 pipeline 在非致命物理失败时崩溃
- 不要把 warnings 当 errors
- 不要把生命/文明评分解释为确定预言
```

---

## 22. 分阶段里程碑

### Milestone 0：可安装项目

完成条件：

```text
pip install -e .
quanta --version
pytest
```

### Milestone 1：配置与验证

完成条件：

```text
quanta validate-config configs/standard_universe.yaml
```

### Milestone 2：原子与核物理窗口

完成条件：

```text
pytest tests/test_atomic.py tests/test_nuclear.py
```

并且标准宇宙输出：

```text
binding energy ≈ 13.6 eV
Bohr radius ≈ 5.29e-11 m
```

### Milestone 3：宇宙学与恒星窗口

完成条件：

```text
pytest tests/test_cosmology.py tests/test_stars.py
```

标准宇宙年龄在合理范围：

```text
10 Gyr < age < 20 Gyr
```

### Milestone 4：完整宇宙报告

完成条件：

```text
quanta run configs/standard_universe.yaml --output reports/standard.md --json reports/standard.json
```

### Milestone 5：参数扫描

完成条件：

```text
quanta scan configs/standard_universe.yaml --param dimensionless.alpha_scale --values 0.5,1.0,1.5 --output reports/scan_alpha.csv
```

### Milestone 6：GitHub 可展示 Demo

完成条件：

```text
README 有完整演示
examples 可运行
reports 有示例输出
CI 通过 pytest
```

---

## 23. 后续高级版本路线

### V2：拉氏量 DSL

增加：

```text
- GaugeGroup
- FieldRepresentation
- LagrangianTerm
- SymmetryBreakingPattern
- EffectiveOperator
```

目标：

```text
从简化拉氏量配置生成粒子谱和相互作用图。
```

### V3：接入外部高能物理工具

可选接入：

```text
- FeynRules / SARAH：模型文件与 Feynman rules
- MadGraph：散射截面
- PYTHIA：事件生成
- Geant4：粒子穿过物质
```

### V4：接入宇宙学工具

可选接入：

```text
- CLASS / CAMB：线性扰动、CMB、功率谱
- GADGET / AREPO 类模拟：结构形成
```

### V5：复杂化学与生命前体

增加：

```text
- 化学网络
- 行星大气模型
- 溶剂窗口
- 自由能梯度
- 信息存储分子可能性
```

### V6：文明抽象模型

增加：

```text
- 能源获取
- 信息积累
- 技术复杂度
- 灾变风险
- 星系尺度扩展窗口
```

---

## 24. 关键物理假设文档要求

必须创建：

```text
docs/physics_assumptions.md
```

内容包括：

```text
- 哪些是标准物理
- 哪些是 toy model
- 哪些是经验启发式
- 哪些参数只是占位
- 哪些结论不能过度解释
```

尤其要明确：

```text
生命窗口评分不是生命必然出现的概率。
文明潜力评分不是文明必然出现的概率。
它们只是物理可行性指标。
```

---

## 25. 最终交付物清单

第一阶段最终应该交付：

```text
1. 可安装 Python 包
2. CLI 工具 quanta
3. 标准宇宙配置
4. 多个变体宇宙配置
5. 完整 pipeline
6. Markdown 报告输出
7. JSON 报告输出
8. 参数扫描功能
9. 单元测试
10. 端到端测试
11. README
12. docs/physics_assumptions.md
13. examples/
14. GitHub Actions CI
```

---

## 26. GitHub Actions CI

文件：

```text
.github/workflows/tests.yml
```

内容目标：

```yaml
name: tests

on:
  push:
  pull_request:

jobs:
  pytest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python -m pip install -U pip
      - run: pip install -e ".[dev]"
      - run: pytest
      - run: quanta run configs/standard_universe.yaml --output reports/standard.md --json reports/standard.json
```

验收：

```text
每次 push 自动运行测试和标准宇宙端到端生成。
```

---

## 27. 第一轮 AI 实际开发任务列表

建议按以下顺序交给 AI Coding Agent：

```text
Task A:
Create Python package skeleton, pyproject.toml, CLI smoke test.

Task B:
Implement config schema, YAML loader, inheritance, validation tests.

Task C:
Implement units and constants conversion helpers.

Task D:
Implement ValidationReport and validate_universe_config.

Task E:
Implement Particle and ParticleSpectrum.

Task F:
Implement hydrogen atom and chemistry window.

Task G:
Implement nuclear stability toy model.

Task H:
Implement Friedmann background solver.

Task I:
Implement stellar window toy model.

Task J:
Implement structure window toy model.

Task K:
Implement complexity evaluator.

Task L:
Implement UniversePipeline and UniverseReport.

Task M:
Implement CLI run/validate/compare/scan.

Task N:
Add example configs, example scripts, reports.

Task O:
Add GitHub Actions CI and docs.
```

---

## 28. 第一条 AI Coding Agent 总控 Prompt

可以直接复制给 AI Coding Agent：

```text
You are building a scientific Python project named quanta-engine.

Read PROJECT_PLAN.md and implement the project incrementally.
Start with Milestone 0 and Task A only.

Hard requirements:
- Use Python 3.11+
- Use src layout
- Add pyproject.toml
- Add Typer CLI
- Add pytest tests
- Keep code modular
- Do not implement advanced physics yet
- Do not skip tests
- Do not overclaim toy models as real precision physics

For Task A:
1. Create package skeleton.
2. Implement quanta --version.
3. Add pytest smoke test.
4. Add README with install and run instructions.
5. Run pytest and report results.

Return:
- changed files
- test commands
- result summary
- next recommended task
```

---

## 29. 第二条 AI Coding Agent Prompt：配置系统

```text
Continue quanta-engine.

Implement Task B from PROJECT_PLAN.md:
- UniverseConfig Pydantic schema
- YAML load_config(path)
- inherit support
- deep merge
- validation tests
- configs/standard_universe.yaml
- configs/strong_alpha_universe.yaml

Do not implement physics modules yet.
Focus only on robust configuration loading.

Acceptance:
- pytest tests/test_config_schema.py passes
- quanta validate-config configs/standard_universe.yaml works
```

---

## 30. 第三条 AI Coding Agent Prompt：第一条完整物理链

```text
Continue quanta-engine.

Implement the first complete physics chain:
- units.py
- ValidationReport
- particle spectrum
- hydrogen atom report
- nuclear stability report
- UniversePipeline with only validation + particles + atomic + nuclear
- CLI quanta run producing markdown report

Acceptance:
- standard universe gives hydrogen binding energy around 13.6 eV
- Bohr radius around 5.29e-11 m
- deuteron and helium4 stable
- pytest passes
- quanta run configs/standard_universe.yaml --output reports/standard.md works
```

---

## 31. 第四条 AI Coding Agent Prompt：端到端宇宙窗口

```text
Continue quanta-engine.

Extend UniversePipeline with:
- Friedmann cosmology solver
- stellar window model
- structure window model
- complexity evaluator
- UniverseReport JSON and Markdown outputs
- end-to-end tests

Acceptance:
- standard universe age is between 10 and 20 Gyr
- standard universe has stable hydrogen, fusion possible, structure possible
- standard universe life_window_score > 0.5
- unstable atom universe life_window_score < 0.1
- pytest passes
```

---

## 32. 第五条 AI Coding Agent Prompt：扫描与比较

```text
Continue quanta-engine.

Implement:
- quanta compare CONFIG_A CONFIG_B
- quanta scan CONFIG --param PATH --values CSV --output CSV
- scan_alpha example
- scan_gravity example
- tests for scan and compare

Acceptance:
- alpha scan runs for 0.5,1.0,1.5
- CSV contains binding_energy_eV, stable_hydrogen, life_window_score
- compare standard vs strong_alpha prints key differences
- pytest passes
```

---

## 33. 项目成功标准

本项目第一阶段成功的判断不是“是否真实模拟整个宇宙”，而是：

```text
1. 输入清晰
2. 模块分层清楚
3. 每层有物理含义
4. 每层有输出
5. 每层可测试
6. 端到端可运行
7. 改变基础参数会产生可解释的宇宙差异
8. 报告明确区分真实物理、近似模型和启发式评分
9. AI Coding Agent 能按任务列表逐步实现
10. 项目结构能自然扩展到更高级物理模块
```

---

## 34. 最小演示脚本

文件：

```text
examples/demo.py
```

目标行为：

```python
from quanta_engine.pipeline import run_universe_pipeline

report = run_universe_pipeline("configs/standard_universe.yaml")
print(report.to_markdown())
```

运行：

```bash
python examples/demo.py
```

预期：

```text
输出一个标准宇宙报告。
```

---

## 35. 一句话项目定位

```text
QuantaEngine 是一个从基本物理参数和有效理论出发，逐层生成并评估自洽宇宙的开源物理创世引擎。
```

更工程化地说：

```text
它不是一个单一模拟器，而是一个多尺度物理编译器：
把底层物理规则编译成粒子、原子、恒星、星系、复杂性和生命窗口。
```
