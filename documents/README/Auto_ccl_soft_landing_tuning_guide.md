Auto CCL Soft Landing Tuning Doc

# Auto CCL Soft Landing – Tuning Notes

## Knee Voltage Behavior

**Lower knee**
- Larger taper window  
- More time to ramp down smoothly  
- More likely to reduce charge current prematurely on high-power days  

**Higher knee**
- Shorter taper window  
- More abrupt deceleration near bulk  
- Less risk of premature current reduction  

Knee defines when tapering becomes eligible. Below knee, Soft Landing does nothing.

---

# Deye Interaction (Critical)

CVL = bulk_voltage + inverter_offset  

Bulk is the real target.  
Offset exists only to shape inverter behavior.

The inverter’s behavior changes depending on **Minimum SoC (Time-of-Use setting).**

---

## Case 1 – Minimum SoC in Tine of Use = 100%

Behavior:

- The inverter obeys CVL directly.
- Charging continues until voltage reaches CVL.
- No early termination behavior occurs.

Implications:

- Inverter offset can be 0V (or only compensate wiring drop).
- Bulk voltage is the real ceiling.
- Soft Landing’s role is voltage inertia control, not enforcement.

Appropriate tuning:

- Moderate `knee_c_rate`
- Moderate `bulk_c_rate`
- Curve does not need to approach zero
- `taper_to_zero` usually unnecessary

In this mode, Soft Landing smooths the approach.  
The inverter handles voltage enforcement.
YamBMS will not signal EOC until current falls below a computed threshold. 

---

## Case 2 – Minimum SoC < 100%

Behavior:

- The inverter will stop charging at:

CVL − 0.5V  

If CVL equals bulk voltage, charging will terminate before reaching bulk.

To prevent premature termination:

- Set `inverter_offset` ≥ 0.5V  
  (so the inverter stop point aligns at or above bulk)

This means:

- CVL is intentionally above real bulk.
- The inverter will push voltage higher than true bulk unless controlled.

Soft Landing now becomes the primary voltage control mechanism.

It must taper current aggressively enough that:

- Pack voltage does not overshoot bulk
- Voltage inertia is controlled
- Charging completion logic can still function

Note float voltage will also be inflated by the inverter offset, so float voltage will need to be set lower than your target by the amount of inverter offset. This seems like a bug but it's intentional since the purpose of inverter offset is to compensate for voltage drop, which applies to all voltages the inverter sees.

Appropriate tuning:

- Lower the C-rate at bulk to prevent overshoot
- Curve should approach near-zero current at bulk
- taper_to_zero = true may be appropriate unless the c-rate at bulk is very low (1 or 2 amps only)
- Curve shape becomes more important

In this configuration, Soft Landing is not smoothing — it is enforcing.

Note: YamBMS will 'prematurely' transtion to bulk since the low current wil trigger a transion to bulk. This isn't necessarily a problem but you should be aware of this consequence.

---

## System Philosophy

| Configuration       | Who Enforces Voltage? | Role of Soft Landing      |
|---------------------|-----------------------|---------------------------|
| Min SoC = 100%      | Inverter              | Smooth approach           |
| Min SoC < 100%      | Soft Landing          | Active voltage control    |
