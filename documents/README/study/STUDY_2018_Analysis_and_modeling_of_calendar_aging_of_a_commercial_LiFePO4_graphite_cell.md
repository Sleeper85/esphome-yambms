# Summary — Analysis and Modeling of Calendar Aging of a Commercial LiFePO4/Graphite Cell

> **Full reference:** Maik Naumann, Michael Schimpe, Peter Keil, Holger C. Hesse, Andreas Jossen (2018).
> *Analysis and modeling of calendar aging of a commercial LiFePO4/graphite cell.*
> Journal of Energy Storage, **17**, 153–169.
> DOI: [10.1016/j.est.2018.01.019](https://doi.org/10.1016/j.est.2018.01.019)
>
> Institute for Electrical Energy Storage Technology (EES), Technical University of Munich (TUM)

---

## 1. Context and Motivation

In stationary battery energy storage systems (BESS), **calendar aging is the dominant lifetime-limiting factor**, not cycle aging. As the authors note:

> *"As current mass-produced LiFePO4/graphite battery cells show cycle stability up to 10,000 full equivalent cycles (FECs) [...] the cycle lifetime is commonly not a limiting factor in stationary applications."* (§1.1)

Within 20 years of home energy storage operation, only ~6,000 FECs are expected. Therefore, the **calendar lifetime becomes the decisive parameter** for economic assessment of stationary BESS. (§1.1)

This study is described as the **first comprehensive calendar aging study** for the widely deployed Sony/Murata US26650FTC1 LFP/graphite cell — a 3 Ah 26650 format cell used commercially under the brand name *fortelion* in many home storage systems, as well as in a 192 kWh containerized BESS (the *Energy Neighbor* project). (§1.1, §2.1)

---

## 2. Investigated Cell — Sony US26650FTC1

Key datasheet parameters (Table 2 of the paper):

| Parameter | Value |
|---|---|
| Nominal capacity | 3.0 Ah (measured mean over 1,100 cells) |
| Nominal voltage | 3.2 V |
| Max. charge voltage | 3.6 V (applied in study) |
| Min. discharge voltage | 2.0 V |
| Max. continuous charge current | 3.0 A (1C) |
| Max. continuous discharge current | 20 A |
| Charge temperature range | 0 °C to 45 °C |
| Discharge temperature range | −20 °C to 60 °C |
| Mass | 84.5 g |

Prior to the aging study, all 1,100 cells were characterized by Rumpf et al., showing a mean discharge capacity of **3.019 Ah** and a very low cell-to-cell variation (σ = 0.007 Ah). (§2.1, §2.7)

---

## 3. Experimental Protocol

### 3.1 Static Aging Study (primary dataset)

- **17 test points (TPs)**, each with **3 cells** stored at constant temperature and SOC
- Duration: **885 days of storage** (970 days total including check-ups)
- **35 periodic check-up (CU) measurements** performed throughout
- Test matrix covers temperatures: **0, 10, 25, 40, 60 °C** and SOC: **0% to 100%** (Table 4)
- Reference condition: 25 °C, SOC = 50% (expected average in BESS operation)
- Accelerated aging at 60 °C (maximum datasheet temperature) to project long-term behavior via Arrhenius extrapolation (§2.5)

### 3.2 Dynamic Aging Study (model validation)

- **15 test points**, 1 cell each, with **alternating temperature and/or SOC conditions** every ~4 weeks
- Duration: ~**270 days** (9 months)
- Designed to validate path-independence of storage conditions and model accuracy under realistic variable conditions (§2.6, Table 5)

### 3.3 Check-Up Measurement Procedure

Each check-up includes (§2.3):
1. Two consecutive full charge/discharge cycles at 1C (CC+CV) to determine discharge capacity *C*disch
2. Pulse resistance test at 1/3C, 2/3C and 1C to determine *R*DC,10s
3. Electrochemical Impedance Spectroscopy (EIS) at SOC = 50%, 25 °C
4. Extended check-ups (×4 over the study): additional 0.02C slow charge/discharge for Differential Voltage Analysis (DVA)

---

## 4. Aging Mechanisms

### 4.1 Dominant mechanism: SEI growth → Loss of Lithium Inventory (LLI)

> *"The SEI growth leads to an irreversible loss of lithium inventory (LLI) [...] and is accelerated with increased temperatures and higher SOCs."* (§1.2, citing Barré et al. [11])

The DVA analysis (§3.1.2, Fig. 3 & 4) confirms that capacity fade is predominantly driven by the **shift of the LiC₁₂ graphite peak** (Q2 parameter), consistent with LLI from SEI growth. At 25 °C, Q1 (anode capacity) is virtually unchanged, confirming **no Loss of Active Material (LAM)** at moderate temperatures.

### 4.2 Secondary mechanism: LAM at high temperatures

At 60 °C, a **slight decrease of Q1** is observed in the DVA, indicating some LAM of the negative electrode — attributed to iron dissolution from the LFP cathode depositing on the graphite surface. However:

> *"LLI remains the dominating factor for capacity fade."* (§3.1.2)

### 4.3 Anode overhang effect

The investigated cell has an anode overhang area of **6.2% of total coated anode area** (Table 3). This can produce a reversible capacity shift of up to ~2.2% depending on storage SOC, but this effect is considered secondary and is not integrated into the aging model. (§2.1, §3.2.1)

---

## 5. Aging Results

### 5.1 Capacity loss (Q_loss)

- Capacity decreases for **all temperatures over time**, with the **rate slowing down** — consistent with a **square root (√t) time dependence** (Fig. 2a, 2c)
- Higher storage SOC → stronger capacity fade, but **between SOC = 37.5% and 62.5%, the difference is minimal** (§3.1.1)
- Higher temperature → strongly accelerated capacity fade

> *"With higher storage SOCs the rates of Q_loss are increasing, but in the middle SOC-range, the rate stays almost constant."* (§4 — Conclusions)

### 5.2 Resistance increase (R_inc)

- Resistance increases **linearly over time** (not √t) for most test points (Fig. 2b, 2d)
- A slight transient **resistance decrease** is observed at the very beginning of storage for most TPs — possibly linked to anode overhang redistribution or measurement uncertainty (§3.1.1)
- Most notable finding: **highest resistance increase occurs in the middle SOC range (~50%)**, not at high SOC — a behavior the authors consider specific to this cell chemistry (§3.1.1, §3.1.3)

> *"The resistance increase shows a non-monotonic dependance over the storage SOC with the highest increase in the middle SOC-range."* (§3.1.1)

---

## 6. Semi-Empirical Aging Model

### 6.1 Model equations

The model expresses capacity loss and resistance increase as a **product of three independent factors** (Eqs. 3 & 4):

**Capacity loss:**

    Q_loss(T, SOC, t) [%] = k_temp,Q(T) * k_SOC,Q(SOC) * sqrt(t)

**Resistance increase:**

    R_inc(T, SOC, t) [%] = k_temp,R(T) * k_SOC,R(SOC) * t

### 6.2 Temperature factor — Arrhenius law (Eq. 5)

    k_temp(T) = k_ref * exp( Ea/R * (1/T_ref - 1/T) )

With reference conditions: *T*ref = 25 °C = 298.15 K, SOCref = 100%.

### 6.3 SOC factor

- **Q_loss**: modeled with a **cubic function** of (SOC − 0.5) → captures the step-like increase above ~75% SOC (Eq. 12)
- **R_inc**: modeled with a **quadratic function** of (SOC − 0.5) → captures the peak at ~50% SOC (Eq. 14)

Parameters fitted on 40 °C test points with 9 SOC values (0% to 100%).

### 6.4 Model parameters (Table 7)

| Parameter | Q_loss | R_inc |
|---|---|---|
| *k*ref | 0.001257 % s⁻⁰·⁵ | 3.419 × 10⁻⁸ % s⁻¹ |
| *E*a | **17.126 kJ mol⁻¹** | **71.827 kJ mol⁻¹** |
| *c* | 2.8575 | 3.3903 |
| *d* | 0.60225 | 1.5604 |
| *T*ref | 298.15 K | 298.15 K |
| SOCref | 100% | 100% |

### 6.5 Dynamic application — virtual time t*

When storage conditions change over time, the model is applied in **differential form** (Eqs. 15 & 16). A **virtual time t*** is introduced to correctly account for the SEI growth history when transitioning between conditions:

    t*_cal(T, SOC, Q_loss) = ( Q_loss / (k_temp,Q(T) * k_SOC,Q(SOC)) )^2

This ensures the model correctly represents the **path-independence of storage conditions** confirmed experimentally. (§3.3)

### 6.6 Validation accuracy (Table 8)

| Parameter | Maximum absolute model error |
|---|---|
| Q_loss | **< 2.2%** across all 15 dynamic TPs |
| R_inc | **< 6.9%** across all 15 dynamic TPs |

---

## 7. Long-Term Lifetime Projection

From the Arrhenius extrapolation (§4 — Conclusions):

> Storage at **25 °C / SOC = 50%** yields a projected calendar lifetime of **more than 22 years** before reaching EOL (Q_loss = 20%).

For a standard 20-year BESS operation at 25 °C / 50% SOC:
- Capacity loss from calendar aging alone: **~19.0%**
- Resistance increase from calendar aging alone: **~33.7%**

When combined with cycle aging (covered in the companion paper by Naumann, Spingler & Jossen, 2020), the EOL criterion of Q_loss = 20% would typically be reached **before 20 years** under realistic operating conditions.

---

## 8. Best Practices for Maximizing LFP Cell Lifetime

The following recommendations are directly derived from the experimental results and conclusions of this study.

### 🌡️ 1 — Control storage temperature

Keep cells between **15 °C and 25 °C** whenever possible. The Arrhenius law governs temperature sensitivity: the **activation energy for capacity loss is E_a = 17.126 kJ mol⁻¹**, implying that each ~8–10 °C rise in temperature roughly doubles the aging rate. Storage above 40 °C is significantly detrimental; at 60 °C, the cell approaches EOL conditions within months. (§3.2.4, Table 7)

> In outdoor or non-climate-controlled BESS installations, **summer thermal management is the single most impactful lever** for extending lifetime.

### ⚡ 2 — Avoid prolonged storage at high SOC

The cubic SOC factor (Eq. 12) shows that capacity fade accelerates substantially above **~75–80% SOC**. The optimal long-term storage range is **SOC = 30–60%**, where Q_loss is near its minimum and nearly independent of SOC. (§3.1.1, §3.2.5, Fig. 2c & Fig. 7a)

### 📉 3 — Reduce maximum charge setpoint

Lowering the charge ceiling from 100% to 80–85% SOC significantly reduces calendar aging at the cost of a small reduction in usable capacity. In a BMS-controlled system with accurate Coulomb counting, transitioning to float mode at a defined SOC target is a direct implementation of this recommendation. (§3.2.5)

### 🔁 4 — Prefer regular cycling over prolonged static storage at high SOC

Short idle periods at high SOC (a few hours daily, as in a typical solar self-consumption cycle) are far less damaging than multi-day storage at 100% SOC. The key cumulative variable is **time spent at high SOC × high temperature**. (§1.1, §3.1.1)

### 🔬 5 — Note on resistance: the 50% SOC anomaly

Unlike capacity loss, **internal resistance increases fastest at mid-SOC (~50%)**, not at high SOC. This counter-intuitive behavior appears to be specific to this cell type and may be related to homogeneous vs. inhomogeneous SEI growth patterns across the anode. This does not change the SOC recommendation for capacity preservation, but is relevant for power performance monitoring over time. (§3.1.1, §3.1.3, Table 6)

### 🔋 6 — Initial cell storage matters

Cells were delivered and stored at **50% SOC at ~8 °C** to minimize pre-study aging — a direct confirmation that low temperature + mid-SOC is the optimal long-term storage condition even before commissioning. (§2.4)

---

## 9. Applicability to BMS-Controlled Systems

This model is designed for integration into BESS lifetime simulations with **dynamic SOC and temperature profiles**. The differential form of the model (Eqs. 15–17) allows real-time or periodic aging estimation based on continuously logged temperature and SOC data.

A BMS that can:
1. Track SOC accurately via Coulomb counting (shunt-based)
2. Communicate charge voltage setpoints dynamically to the MPPT charge controller
3. Log cell temperature continuously

...has all the inputs needed to implement an **active aging minimization strategy** grounded directly in this model. The virtual time *t** mechanism (Eq. 17) even allows implementing a running Q_loss estimate that correctly accounts for past operating history.

---

## 10. Selected References from the Paper

| # | Authors | Title | Journal | Year |
|---|---|---|---|---|
| [1] | Naumann et al. | LFP battery cost analysis in PV-household applications | Energy Procedia | 2015 |
| [6] | Schmalstieg et al. | Holistic aging model for NMC 18650 cells | J. Power Sources | 2014 |
| [11] | Barré et al. | Review of Li-ion aging mechanisms for automotive applications | J. Power Sources | 2013 |
| [12] | Li et al. | Degradation mechanisms of graphite electrode in C6/LFP | J. Electrochem. Soc. | 2016 |
| [13] | Li et al. | Calendar aging degradation mechanisms of C6/LFP | Electrochim. Acta | 2016 |
| [14] | Keil et al. | Calendar aging of lithium-ion batteries | J. Electrochem. Soc. | 2016 |
| [25] | Sarasketa-Zabala et al. | Calendar aging of LFP with dynamic model validation | J. Power Sources | 2014 |
| [45] | Rumpf et al. | Cell-to-cell variation study on 1,100 commercial Li-ion cells | J. Energy Storage | 2017 |

---

*This summary was prepared from the full text of: Naumann et al. (2018), Journal of Energy Storage, Vol. 17, pp. 153–169.
All section (§), equation, figure and table references correspond directly to the original publication.*
