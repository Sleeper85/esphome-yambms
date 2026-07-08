# YamBMS - Charging a battery with CVL and CCL

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

## Charging a battery: pressure (CVL) and flow (CCL)

Think of charge voltage as water pressure and charge current as flow. The inverter is the pump pushing at the requested pressure (CVL); the battery pushes back with its own counter-pressure, which rises as it fills. Flow depends on the *difference* between the two. There are three ways to end a charge:

### 1. CCL based — full pressure, closing valve (native Pylontech)
The source pressure stays at maximum (53.2 V) from start to finish. Charge termination is handled entirely by a valve (CCL) that is progressively closed as SOC approaches 100%, until it shuts completely (CCL = 0). This gives direct, precise control over how fast energy enters the battery — but the safety of the whole system rests on the valve's obedience. The pipe remains fully pressurized behind a closed valve: if the inverter ignores or reacts slowly to the CCL command (as with Victron's DC feed-in behavior), the full pressure is still there, ready to push. The result is the hydraulic equivalent of water hammer — overcharge spikes, high-voltage alarms, Victron error #29, and cells held permanently at elevated voltage, which accelerates calendar aging.

### 2. CVL based (Classic Float) — pressure lowered to a fixed value
After full charge, the source pressure drops to a preset float level. Inherently safer: with reduced pressure, over-filling becomes physically impossible regardless of how the downstream equipment behaves. But the fixed value is a compromise — too high and a residual trickle keeps stressing the cells; too low and the battery must discharge into the loads to reach the setpoint, causing micro-cycling and the SOC sawtooth.

### 3. CVL based (Float Follow/Immediate) — pressure tracking the battery's natural relaxation (YamBMS)
Instead of picking an arbitrary float value, the source pressure follows the battery's counter-pressure as it settles after charging, the way LFP cells naturally relax toward their resting voltage once charge current is removed. The differential stays near zero, so no meaningful flow in either direction: the battery rests at its true equilibrium voltage as if disconnected, while remaining online and ready to resume charging. It combines the built-in safety of pressure control with none of the compromises of a fixed float value.

### The key takeaway

Controlling charge through the valve alone (CCL) offers authority over flow, but keeping the pipe at full pressure behind a closed valve means safety depends entirely on the valve holding. Lowering the pressure itself (CVL) makes overcharge impossible by construction — and letting that pressure follow the battery's own relaxation is the gentlest way to do it.

## YamBMS safe-charging functions

YamBMS controls charging through both levers available on the CAN/RS485 bus — voltage (the pressure the inverter pushes at, CVL) and current (the flow admitted into the battery, CCL/DCL) — and layers several automatic protections on top of the staged charging logic.

### Charging logic (Bulk / Balancing / Cut-Off / EOC or Float)

The foundation is a staged charge profile driven by cell-level measurements, with chemistry-aware thresholds set at startup (for LFP: 3.37 V = fully charged at rest, 3.65 V = max cell voltage).

The **Cut-Off phase** is where YamBMS decides the battery is genuinely full, and it does so with an IR-compensated criterion rather than a naive voltage or tail-current test. The core computes a pseudo internal resistance, `cutoff_resistance = (cv_max − cv_min) / battery_capacity / 0.05`, then evaluates the highest cell's *compensated* voltage while charging: `cutoff_voltage = max_cell_v − cutoff_resistance × current`. This estimates what the runner cell would read *at rest*, stripped of the voltage inflation caused by charge current flowing through its internal resistance. When that compensated value reaches the "fully charged at rest" threshold (3.37 V for LFP), the cell is truly full — regardless of how much current is still flowing. The criterion must hold continuously for 10 s before entering Cut-Off (and symmetrically 10 s to fall back to Bulk), filtering out spurious BMS readings; a grey zone between the two conditions resets both timers so the state can't oscillate. Once in Cut-Off, two timers manage the exit: if the BMS reports active equalization, YamBMS holds the phase so balancing can finish; otherwise a short cut-off timer (60 s default) confirms end of charge. An overarching EOC timer (30 min default) caps the whole phase so a poorly balanced multi-battery bank can't keep the system pinned at high voltage for hours — though it can be deliberately disabled to let YamBMS rebalance a badly drifted pack over many hours. At EOC, the state moves to Float if enabled, otherwise to EOC, and only then is SOC 100% reported to the inverter.

### Auto CVL — the pressure regulator
When a runner cell starts exceeding the bulk target, YamBMS automatically lowers the requested charge voltage so that cell is held at or near its target (e.g. 3.45 V) while the balancer brings up the lagging cells. It serves a double purpose: keeping the runner at bulk voltage for effective balancing, *and* preventing it from ever climbing to the OVP threshold. In the water analogy, this is regulating the pump pressure itself: as soon as one cell's back-pressure rises too fast, the source pressure is dialed down, so overpressure — an OVP trip — becomes impossible by construction. It uses the BMS's balance trigger voltage as its reference and also tames a deliberately raised Boost Charge voltage back down at the end of charge. This is the control mode Victron and others recommend, but its effectiveness depends on how faithfully the inverter follows CVL commands.

### Auto CCL & DCL — the safety valve
Complementary current-based protection against OVP and UVP alarms. Auto CCL progressively closes the valve — throttling the admitted flow — when a cell approaches the BMS's overvoltage cutoff, keeping it just below the limit even if the pressure upstream stays high. Auto DCL mirrors this on discharge as a cell nears UVP + 0.2 V. Where Auto CVL acts on the pressure and needs a well-behaved inverter, Auto CCL acts on the flow and works with virtually any CAN/RS485-controlled inverter. Together they cover each other's weaknesses.

### Auto Float Voltage — controlled pressure release
Some inverters (e.g. Deye) interpret the Bulk-to-Float CVL drop as battery overvoltage and dump current into the grid at maximum discharge rate. Auto Float releases the pressure gradually in configurable steps (default 0.1 V every 3 minutes) instead of all at once. In *Follow* mode it waits for the battery's own voltage to relax below the current CVL before stepping down further — the source pressure tracks the battery's natural post-charge settling, keeping the differential near zero so no meaningful flow occurs in either direction. *Immediately* mode steps down on a timer regardless of battery voltage.

### Max Requested Current — layered current limiting

The requested charge/discharge current starts from the lowest of three static ceilings: a user-defined hard maximum that can never be exceeded, the aggregate BMS capability (sum of OCP values × 0.9), and the nominal current of the battery bank (total capacity × a configurable C-Rate, 0.5C by default as recommended by most LFP cell datasheets, e.g. EVE MB31). On top of that baseline, the active functions can each further reduce the current in real time: Auto Temp-Based Current, Auto CCL, Auto SoC Limit and Auto EOC act on the charge current (CCL), while Auto Temp-Based Current and Auto DCL act on the discharge current (DCL). The final CCL/DCL sent to the inverter is always the lowest value among them. The three ceilings define how far the valve may ever open in the first place — with the C-Rate ceiling anchoring it to what the cells are actually rated for, rather than to a protection threshold — then each active function closes it further as conditions require: a cold pack, a runner cell nearing OVP, a weak cell sagging toward UVP, a SoC target, or a scheduled end-of-charge time. The CCL/DCL derating reason is exposed as a diagnostic sensor so you can always see which function is currently holding the valve.

### Auto SoC Limit and Auto EOC — supervisory limits
Auto SoC Limit stops charging at a target SoC by switching to Float, clamping the CCL to a configurable small value (avoiding the 0 A requests some inverters mishandle), or both, with hysteresis to prevent oscillation around the threshold. Auto EOC slows the charge so the battery reaches full at a chosen time instead of sitting fully charged all day — a calendar-aging benefit, since it minimizes time spent at high pressure.

### ReBulk and Request Force Charge
Recharge is re-triggered by SoC, voltage, or days since last full charge (useful for periodic SOC recalibration and top balancing), and a grid force-charge can be requested between configurable start/stop SoC values on PYLON, LuxPower and Victron protocols. Force Bulk automatically disengages once the pack enters Cut-Off.

### Supporting safeguards
A 16-bit alarm bitmask consolidates protections across all connected BMS units (OVP, UVP, temperature, overcurrent, short circuit, imbalance…), distinguishing a single unit in alarm ("Warning") from a bank-wide condition. An Inverter Offset compensates for cable voltage drop or inverters that under-deliver the requested voltage, and Inverter Heartbeat Monitoring helps detect a failing CAN/RS485 link — the silent failure mode where an inverter charges blind.

### In short
Auto CVL regulates the pump pressure so no cell can ever be over-pressurized, Auto CCL is the valve that closes when a cell rises too fast despite the pressure, Auto Float releases the pressure at the battery's own relaxation rate, the three-way current minimum decides how far the valve may open at all — and the Cut-Off logic knows the tank is full by reading what the pressure would be with the flow removed, rather than trusting the inflated reading while water is still rushing in.
