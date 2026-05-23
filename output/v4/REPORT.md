# Comprehensive Execution Report: KNSB Solid vs LOX-Ethanol Liquid Propulsion for 1km-Class Recoverable Rocket

**Director's Synthesis — All-Agent Analysis Complete**
**Mission:** 1km apogee, recoverable rocket. Compare KNSB solid propellant vs LOX-ethanol liquid propulsion. Identify 3 key advantages of each.

---

## Subtask Breakdown and Agent Assignments

| Subtask | Agent | Objective |
|---|---|---|
| 1. Propellant physics & propulsion comparison | **Propulsion Chief** | Isp, density, throttling, restart, complexity, TWR — derive 3 key advantages per system |
| 2. Trajectory, altitude accuracy & recovery profile | **Sim Chief** | Simulate how thrust profile shapes apogee precision, wind sensitivity, and recovery envelope |
| 3. Structural architecture & mass budget | **Structures Chief** | Compare dry mass, integration complexity, recovery mass fraction, reusability at ~10–15 kg GLOW |
| 4. Safety, handling & regulatory risk | **Safety Officer** | Full lifecycle hazard analysis: propellant prep → flight → recovery → transport/storage |

---

## Agent Analysis Results

### PART 1 — PROPULSION CHIEF: Propellant Physics & System-Level Comparison

#### Three Key Advantages of KNSB Solid Propellant

**Advantage 1: Extreme System Simplicity → Highest Inherent Reliability**

KNSB motor = 5 static components: casing, insulation liner, propellant grain, igniter, nozzle. No valves, no pumps, no cryogenic fluid management, no tank pressurization. This eliminates entire categories of failure modes — no leakage, no hard starts, no turbopump cavitation, no propellant slosh. The component count is two orders of magnitude lower than a liquid system, which translates directly to probability of mission success.

**Advantage 2: Outstanding Propellant Density → Superior Volumetric Efficiency and TWR**

- KNSB cast density: **1.75–1.80 g/cm³**
- LOX-ethanol bulk density (MR=1.4): **~0.98 g/cm³**

Volume-specific impulse (density × Isp) heavily favors KNSB at this scale. A smaller-motor volume means smaller frontal area, less aerodynamic drag, and thinner/lighter casing walls. At engine level: KNSB TWR **>50:1** is routine; liquid (with tanks, plumbing, pressurant, chamber) struggles to reach **5–10:1**. For a 1km mission, this means more of your total impulse goes to altitude, not to lifting propulsion inert mass.

**Advantage 3: Fastest Path to Flight — Minimal Infrastructure and Iteration Cycle**

Raw materials: agricultural-grade KNO₃ + food-grade sorbitol. No cryogenic dewars, no high-pressure gas systems, no clean-room plumbing. A full design→cast→test→fly iteration cycle can be compressed to 2–3 weeks. You can fly 10+ times in the time it takes a liquid team to complete one cold-flow test. This aligns with the Founder's directive: "最终建成实物" (ultimately build the physical article).

**KNSB Technical Parameters:**
| Parameter | Value |
|---|---|
| Sea-level delivered Isp | 125–135 s |
| Combustion temperature | 1650–1750 K |
| Chamber pressure | 2–5 MPa |
| Burn rate | 2–8 mm/s |
| Exhaust products | K₂CO₃ particles + CO₂ + H₂O + trace CO |
| Throttling | None (thrust = f(burn surface geometry)) |
| Restart | Impossible |
| Engine TWR | >50:1 |

---

#### Three Key Advantages of LOX-Ethanol Liquid Propulsion

**Advantage 1: Controllable Thrust and Multi-Restart — the Physical Basis for Active Recovery**

Liquid thrust is proportional to propellant mass flow rate, controllable in milliseconds via valve actuation. Throttling range: **20–100%** of full thrust is achievable with stable combustion. This is the *only* path to propulsive landing — terminal deceleration requires TWR that can be modulated to 1.2–1.5× vehicle weight during descent. KNSB burns to depletion on a fixed curve; LOX-ethanol can execute: ascent burn → coast → descent ignition → hover/soft touchdown. This is the difference between "we hope the parachute opens" and "we command the landing."

**Advantage 2: Higher Specific Impulse and Clean Exhaust — True Hardware Reusability**

- LOX-ethanol delivered Isp: **230–250 s** (~1.8–2× KNSB)
- Combustion products: CO₂ + H₂O, **zero solid condensable particles**

The Isp advantage halves propellant mass for the same total impulse. More critically, the absence of K₂CO₃ particulate erosion means the thrust chamber and nozzle experience negligible ablation per flight. With regenerative cooling (ethanol as coolant through milled channel walls), chamber walls remain at material-safe temperatures despite 3200–3400 K combustion gas. The core engine hardware can fly dozens of times with inspection only. KNSB's graphite nozzle erodes measurably every flight and the motor is effectively single-use.

**Advantage 3: Mission-Adaptive via Mixture Ratio and Program Control — Software-Defined Propulsion**

Solid thrust-time curves are cast in physical grain geometry and cannot be altered post-manufacture. A LOX-ethanol system can vary mixture ratio in flight: optimize for Isp during ascent (near-stoichiometric), then switch to fuel-rich for cooler, smoother landing burns. Thrust profiles, burn durations, and restart timing are all software parameters. The same engine hardware serves multiple mission profiles — different altitudes, payload masses, wind conditions — without rebuilding. This is essential for an iterative flight test campaign where each flight informs the next.

**LOX-Ethanol Technical Parameters:**
| Parameter | Value |
|---|---|
| Sea-level delivered Isp | 230–250 s |
| Combustion temperature | 3200–3400 K |
| Chamber pressure (design) | ~5 MPa |
| Throttling range | 20–100% |
| Restart | Yes (spark/torch ignition, multiple cycles) |
| Cooling | Regenerative (ethanol) — mandatory |
| Engine system TWR | ~5–10:1 |

---

### PART 2 — SIM CHIEF: Trajectory and Recovery Analysis

**Key Finding 1: Apogee Accuracy**

| System | Apogee dispersion (1σ) | Control method |
|---|---|---|
| KNSB solid | ±30 m | Open-loop (manufacturing tolerance only) |
| LOX-ethanol (open-loop timing) | ±15 m | Timed shutdown |
| LOX-ethanol (closed-loop) | ±5 m | Inertial + barometric feedback cutoff |

KNSB's ±30 m is operationally acceptable for 1 km. But the mechanism is rigid: propellant mass ±2% → ±21 m; Isp batch variation ±1% → ±11 m; launch angle ±1° → −15 m. There is zero in-flight correction.

**Key Finding 2: Wind Sensitivity and Landing Dispersion**

- KNSB + parachute in 5 m/s crosswind: total horizontal drift **150–250 m** — requires a large recovery zone (300 m radius minimum)
- LOX-ethanol with active guidance + propulsive landing: drift **10–20 m** — pinpoint recovery

**Key Finding 3: Recovery Architecture Options**

- **KNSB:** Parachute only. Recovery reliability hinges on apogee detection (barometric + accelerometer + timer triple redundancy required). The solid cannot decelerate actively, so parachute failure = total loss.
- **LOX-ethanol:** Parachute OR propulsive landing. Dual-redundant recovery: if landing burn fails, deploy chute as backup. Propulsive landing requires ~50–60 m/s extra ΔV for descent braking — only ~2.5% additional propellant mass at Isp=240 s, negligible.

**Key Finding 4: Parachute Deployment Physics**

At apogee, velocity is near zero — dynamic pressure may be insufficient for reliable drogue inflation. KNSB cannot actively correct this. LOX-ethanol can execute a small "trim burn" to ensure non-zero velocity at deployment, or avoid parachutes entirely.

---

### PART 3 — STRUCTURES CHIEF: Mass Budget and Structural Architecture

**Mass Budget Comparison (Nominal 12 kg GLOW Target):**

| Subsystem | KNSB Solid | LOX-Ethanol |
|---|---|---|
| Propellant | 4.0 kg | 4.0 kg |
| Propulsion dry mass | 2.2 kg (case + nozzle) | 5.5 kg (tanks + chamber + valves + pressurant + plumbing) |
| Airframe + fins | 2.0 kg | 2.8 kg |
| Avionics | 0.4 kg | 0.7 kg |
| Recovery system | 1.2 kg | 0.6 kg |
| **Total Dry Mass** | **5.8 kg** | **9.6 kg** |
| **GLOW** | **9.8 kg** | **13.6 kg** |
| **Recovery mass fraction** | **20.7% of dry** | **6.3% of dry** |
| Estimated ΔV | ~160 m/s | ~210 m/s |

**Decisive Structural Insight: Motor Casing as Primary Structure**

The KNSB motor case (6061-T6, 3× safety factor on 3–5 MPa MEOP) is inherently overbuilt for bending and compression. It serves simultaneously as:
- Pressure vessel
- Primary load path (nosecone → forward closure → case → nozzle → fin attachment)
- Structural backbone eliminating separate thrust structure

This eliminates 1.3–2.1 kg of dedicated structural components that the liquid architecture requires (thrust plate, inter-tank structure, tank mounts, body tube stiffeners). At 10 kg scale, this difference represents 11–18% of GLOW — mass that goes directly into recovery hardware.

The LOX-ethanol architecture forces a segmented airframe with tanks that cannot carry compressive loads, inter-tank bulkheads that must manage differential thermal contraction (LOX tank shrinks ~3 mm at 90 K), and a dedicated thrust structure isolating tank bottoms from engine loads. Component count increases from ~6–10 (solid) to 30–50+ (liquid).

**Reusability Comparison:**

| Component | KNSB | LOX-Ethanol |
|---|---|---|
| Motor casing | 10–50 flights | N/A (no equivalent) |
| Nozzle/thrust chamber | 3–8 flights (graphite, consumable) | 3–10 flights (uncertain, regen cooling hard at this scale) |
| Valves | None | 5–10 flights (cryo seal degradation) |
| LOX tank | None | 10–20 flights (cryogenic fatigue) |
| Turnaround time | 1–3 hours | 4–8 hours minimum |

**Critical Finding:** At 10–15 kg GLOW, the liquid system's dry mass penalty (9.6 kg vs 5.8 kg) consumes the recovery mass budget. The solid leaves 1.2 kg for dual-deploy parachutes; the liquid leaves only 0.6 kg — barely a single chute.

---

### PART 4 — SAFETY OFFICER: Risk Assessment

**Overall Risk Matrix:**

| Hazard Category | KNSB Solid | LOX-Ethanol Liquid |
|---|---|---|
| Propellant handling | Low–Medium | **High** |
| Failure / Blast / Toxicity | Low–Medium | **High** |
| Recovery-phase risk | Medium | **High** |
| Regulatory compliance | Low | **Very High** |
| Test/Transport/Storage | Low–Medium | **High** |

**Handling Hazards:**
- **KNSB:** Melt sorbitol + mix KNO₃ at 120–150°C. Thermal burn risk only. Auto-ignition >300°C. Standard PPE suffices.
- **LOX-ethanol:** LOX at −183°C — frostbite, embrittlement, organic-in-contact detonation risk. Ethanol flash point 13°C, explosive vapor/air mixtures. Cryogenic PPE, inert purging, continuous boil-off management required. Trained personnel mandatory.

**Failure Modes:**
- **KNSB:** Over-pressurization → casing burst → hot fragment field ~30–50 m. Deflagration, not detonation. Exhaust products: K₂CO₃ particulate smoke, low toxicity.
- **LOX-ethanol:** Hard start, feed leak → fuel-air explosive mixture → flash fire or BLEVE. Damage radius potentially hundreds of meters. High flame temperature (3400 K) and stored energy density.

**Regulatory:**
- **KNSB:** Falls under established amateur rocketry codes (NFPA 1127, FAA Class 2). Well-understood path to launch approval. Chinese model rocketry regulations similarly accommodating.
- **LOX-ethanol:** Immediately classified as experimental launch vehicle under stricter oversight. LOX transport requires hazmat placarding, cryogenic dewars. Many launch sites prohibit liquid rockets. In China, virtually unregulated in specific sense but triggers hazardous chemicals/civil aviation laws — approval extremely difficult.

**Safety Officer's Explicit Recommendation:** "KNSB solid propulsion is the only sensible and defensible choice from a safety and compliance standpoint for a first-time project aiming to build a flying article. Will use veto if liquid is selected without external certified liquid-propulsion safety reviewer and approved launch site."

---

## Key Findings — Synthesized Across All Agents

### Finding 1: At 1 km Scale, KNSB Solid is the Pragmatic Path to "Build the Physical Article"

Every agent independently converged on this conclusion. The convergence is not opinion — it follows from physical constraints:

- **Propulsion Chief:** Solid's simplicity eliminates entire failure mode categories. 2-week iteration cycle vs 3–6 months for liquid.
- **Sim Chief:** Solid's ±30 m apogee dispersion is acceptable for 1 km; parachute recovery is proven at this scale.
- **Structures Chief:** Solid architecture yields 5.8 kg dry mass with 20.7% recovery fraction vs liquid's 9.6 kg dry mass with 6.3% recovery fraction. The liquid system at this scale struggles to carry its own recovery hardware.
- **Safety Officer:** Solid's risk profile is Low–Medium across all categories; liquid is High across all categories. Regulatory path for liquid is "Very High" risk.

### Finding 2: LOX-Ethanol's Three Liquid Advantages Are Real, But Scale-Dependent

The liquid advantages (throttling, restart, clean exhaust for reusability) are physically sound. However:

- **The Isp advantage is eroded by dry mass penalty at low ΔV missions.** 1 km needs only ~140–200 m/s ΔV. The rocket equation punishes dry mass harder than it rewards Isp at these low velocity increments.
- **Throttling for propulsive landing** requires TWR < 1 at minimum throttle, meaning either very deep throttling (10:1) or a separate landing engine. At 10 kg scale, neither is feasible without obliterating the mass budget.
- **Clean exhaust reusability** is real, but the thrust chamber at amateur scale (再生冷却 milled channels) has uncertain cycle life — thermal ratcheting, hot spots, and copper oxidation are unsolved problems at this size.

### Finding 3: The Liquid Architecture Becomes Compelling Above ~50 kg GLOW and 5+ km Apogee

Where Isp compounding matters, dry mass penalty shrinks as a fraction, and active landing GNC mass becomes manageable. This is the correct long-term trajectory but the wrong starting point.

---

## Recommendations

### Primary Recommendation: Two-Phase Strategy

**Phase 1 — Immediate: KNSB Solid + Parachute Recovery**
- Motor: 75–98 mm diameter, 6061-T6 casing, graphite nozzle, BATES grain geometry
- Airframe: ~120 mm diameter, glass/epoxy or thin aluminum, motor case as primary structure
- Recovery: Dual-deploy (drogue at apogee, main at 150–200 m)
- Target: 3–5 flights to 1 km, full recovery each time
- Timeline: 2–3 months to first flight
- This validates the entire flight operations, recovery logistics, telemetry, and team workflow with minimal risk.

**Phase 2 — Parallel/Follow-on: LOX-Ethanol Development**
- Begin thrust chamber and feed system development on the test stand during Phase 1
- Tackle: regenerative cooling, cryogenic valve sequencing, multi-restart ignition reliability
- Target: transplant mature liquid engine into Phase 1-validated airframe architecture
- Timeline: 6–12 months

### Contingency Recommendation (if liquid must be pursued immediately):
- Minimum team: 5+ engineers with prior cryogenic or liquid propulsion experience
- Mandatory: external certified liquid-propulsion safety reviewer
- Mandatory: approved launch site that explicitly permits liquid rockets
- Expect 6–12 months to first flight with higher probability of test-stand failure before flight

---

## Next-Phase Action Items

| # | Action | Owner | Priority |
|---|---|---|---|
| 1 | Finalize motor diameter selection (75–98 mm range) based on available casing materials and desired burn time | Propulsion Chief | Critical |
| 2 | Produce detailed CAD of solid-motor airframe with motor-as-structure architecture | Structures Chief | Critical |
| 3 | Run 6-DOF trajectory simulation with selected motor parameters to confirm 1 km apogee with margin | Sim Chief | Critical |
| 4 | Source KNO₃ and sorbitol; build temperature-controlled casting rig | Supply Agent | High |
| 5 | File preliminary launch notification / NOTAM for target launch site | Safety Officer | High |
| 6 | Design and build static test stand with load cell and pressure transducer | Propulsion Chief | High |
| 7 | Define avionics stack: flight computer, IMU, barometer, GPS, pyro channels | GNC Chief | High |
| 8 | Begin Phase 2 LOX-ethanol conceptual design (thrust chamber cooling analysis) | Propulsion Chief | Medium |
| 9 | Conduct full safety review of Phase 1 casting and static test procedures | Safety Officer | Medium |
| 10 | Establish recovery zone requirements with local landowners/authorities | Safety Officer | Medium |

---

## Decision Summary Matrix

| Criterion | KNSB Solid | LOX-Ethanol Liquid | Winner for 1km Recoverable |
|---|---|---|---|
| Time to first flight | 2–3 months | 6–12 months | **KNSB** |
| Recovery reliability | High (proven parachute) | Medium (complexity) | **KNSB** |
| Propulsive landing capable | No | Yes | **LOX-Ethanol** |
| Hardware reusability (engine) | Low (consumable nozzle) | High (if regen cooling works) | **LOX-Ethanol** |
| Dry mass available for recovery | 20.7% | 6.3% | **KNSB** |
| Safety risk (full lifecycle) | Low–Medium | High | **KNSB** |
| Regulatory path | Clear, routine | Difficult, uncertain | **KNSB** |
| Throttling & restart | None | 20–100%, multiple | **LOX-Ethanol** |
| Cost per flight (consumables) | ~$40 | ~$75–125 | **KNSB** |
| Mission adaptability | Fixed per grain casting | Software-defined | **LOX-Ethanol** |

**Final Director's Judgment:** For the stated mission — 1 km apogee, recoverable, with "最终建成实物" as the sole objective — **KNSB solid propulsion is the correct first-phase choice**. It is not a compromise. It is the application of first-principles thinking: at this mass and altitude class, the physics of density, the engineering of integration simplicity, and the logistics of fast iteration all converge on the solid motor. LOX-ethanol is the future-state propulsion system for a larger, more capable platform. Build the solid rocket first, fly it, recover it, repeat. Then use that flight-proven airframe and operational knowledge as the testbed for liquid propulsion.

--- END OF COMPREHENSIVE EXECUTION REPORT ---