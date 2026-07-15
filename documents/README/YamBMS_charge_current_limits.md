## Charge-current limits in YamBMS

YamBMS does not have a single “max charge current.” It has a pipeline of limits, applied in stages, each with a distinct role.

I’ll use four names:

1. Hard cap  
2. User cap  
3. System cap  
4. Charge cap

---

### 1) Hard cap (configuration ceiling)

**What it is**  
A compile-time ceiling that limits the maximum possible value of the user-adjustable max-charge-current slider.

**Source**  
substitution: yambms_max_requested_charge_current

**Role**
- Bounds the UI
- Encodes absolute system constraints (inverter max, wiring, fusing)
- Does not participate directly in charge-control logic

**Important**  
The hard cap never directly limits charging. It only constrains what the user is allowed to request.

**Practical note**  
Setting this to the inverter maximum (for example 220 A) is often cleaner than setting it to the theoretical sum of BMS limits, because it represents a true physical constraint.

---

### 2) User cap (manual derating)

**What it is**  
A runtime-adjustable value set by the user in Home Assistant.

**Entity**  
number.yambms_*_max_requested_charge_current

**Role**
- Intentional manual derating
- Defines the target operating ceiling
- Can be used to give higher-level logic (Auto CCL) a stable reference

This value expresses user intent, not battery capability.

---

### 3) System cap (effective maximum before Auto CCL)

**What it is**  
The single, authoritative maximum charge current that feeds all automatic derating logic.

**How it is computed (inside `combine`)**  

system_cap = min(  
&nbsp;&nbsp;user_cap,  
&nbsp;&nbsp;combined_bms_max_charge_current × 0.9  
)

**Key clarifications**
- The “combined BMS × 0.9” value exists only transiently inside the `combine` lambda
- It is not stored and not exposed as a sensor
- The only published result is the post-min value

**Entity**  
sensor.yambms_*_max_charge_current

This sensor already is the system cap. It is neither a raw BMS value nor a raw user value.

**Why the 0.9 exists**  
The 10% margin provides headroom for:
- reporting latency
- aggregation effects
- rounding and transient behavior  

and ensures YamBMS stays conservatively below BMS-declared limits.

---

### 4) Charge cap (final requested current)

**What it is**  
The current actually requested from the inverter.

**Computation (in `yambms_core`)**  

charge_cap =  
&nbsp;&nbsp;system_cap +  
&nbsp;&nbsp;min(auto_ccl, auto_eoc, auto_temperature_ccl)

This value can only be lower than the system cap and is shaped dynamically by voltage, temperature, and end-of-charge logic.

---

## Why the max charge current “moves”

If:

user_cap > combined_bms_cap × 0.9

then the BMS is the active limiter, and the system cap will move as the BMS reduces its allowed charge current (commonly near high SOC, high voltage, temperature limits, or balancing).

This behavior is correct and intentional.

Note: Not all BMS reduce the maximum charge current. Seplos does but I think JK does not.
