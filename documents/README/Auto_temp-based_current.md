# Auto Temp-Based Current

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

The YamBMS `Auto Temp-Based Current` function is a software control designed to protect battery cells from damage due to charging or discharging at extreme temperatures.

It dynamically calculates a "Delta" (reduction value) that adjusts the configured maximum charge and discharge limits based on the thermal environment of the battery.

Lithium Iron Phosphate (LiFePO4) batteries have specific "C-rate" limits that change with temperature. For example, charging at 0°C may be prohibited or restricted to a very low current, while charging at 25°C allows for the full rated current.

This function automates that logic by:
- Monitoring the minimum and maximum cell temperatures.
- Filtering out sensor noise.
- Interpolating a safe C-rate from user-defined tables.
- Calculating the required current reduction (Delta).

### Sequence of Operation
1. Check Switch: Is the feature enabled?
2. Validate Data: Are sensors online and reporting valid numbers?
3. Filter: Apply EMA smoothing to the raw temperature values.
4. Lookup: Find the C-rate for the current temperature.
5. Calculate: Determine the current reduction needed.
6. Apply: Round the result and update the relevant globals.


## Core Logic
### EMA Filter
Battery cells have significant thermal mass; their temperature does not change instantly. However, digital sensors often jitter between values (e.g., bouncing between 6.8°C and 6.9°C).  
To prevent the charge current unnecessary fluctuations, an Exponential Moving Average (EMA) is used:

$$S_t = (\alpha \times Y_t) + ((1 - \alpha) \times S_{t-1})$$

**Alpha** ($\alpha$) - Set to `0.05`. This provides a stable, slow-moving average that ignores minor sensor noise but tracks real thermal trends.

**Adaptive Filtering** - If the sensor jumps by more than 5°C (for example, during boot-up or BMS connection), the filter ignores the EMA logic and updates immediately to the new value to ensure safety.

### Linear Interpolation
Auto Temp uses a pair of mapping tables (`yambms_charging_rate_table`  & `yambms_charging_rate_table`) to define the relationship between temperature and C-Rate for both charging and discharging.

The interpolation function calculates values between defined points in these tables:

For example:
- **Point A**: $0^\circ\text{C}$ = $0.0\text{C}$ (No charging)
- **Point B**: $10^\circ\text{C}$ = $0.1\text{C}$ (Slow charging)

If the actual battery temperature is $5^\circ\text{C}$, the code determines that 5 is exactly halfway between 0 and 10, so it outputs $0.05\text{C}$.

#### Logic Walkthrough
The function is written as a C++ lambda (a small, self-contained function) that takes two inputs: the mapping table (`m`) and the current temperature (`x`).

1. **Boundarys and checks**

```c++
if (m.empty()) return 0.0f;
if (x <= m.begin()->first) return m.begin()->second;
if (x >= m.rbegin()->first) return m.rbegin()->second;
```
- Empty table: If the table isn't loaded, it returns 0.
- Lower bound: If the temperature is colder than the first mapping entry (e.g., $-10^\circ\text{C}$ when the table starts at $0^\circ\text{C}$), it simply returns the rate for $0^\circ\text{C}$.
- Upper Bound: If the temperature is hotter than the last mapping entry, it returns the rate for the highest temperature defined.

2. **Bracketing the input temperature value** 

```c++
auto it_upper = m.upper_bound(x);
auto it_lower = std::prev(it_upper);
```
The function looks through the mapping table to find the two points that encompass the current temperature.  
For a temperature of $7^\circ\text{C}$, it finds the entries for $0^\circ\text{C}$ (lower) and $10^\circ\text{C}$ (upper).

3. **The Slope Calculation**

```c++
float x0 = it_lower->first, y0 = it_lower->second;
float x1 = it_upper->first, y1 = it_upper->second;
return y0 + (x - x0) * ((y1 - y0) / (x1 - x0));
```
This uses the standard slope-intercept formula ($y = mx + b$).  
It calculates the slope (Rate of change): $\frac{\text{Change in C-Rate}}{\text{Change in Temp}}$, then multiplies that slope by the distance the current temperature is from the lower bracket.  
Finally, it adds that result to the lower bracket C-rate.

#### Why Use Interpolation Instead of Simple Steps?
Without interpolation, current limits would jump abruptly when the cell temperature passes a threshold.  
Stepped current limits:
- $4.9^\circ\text{C}$ = $14.0\text{A}$
- $5.0^\circ\text{C}$ = $33.6\text{A}$

This creates sudden changes in requested current that can stress equipment.

Interpolated current limits:
- $4.9^\circ\text{C}$ = $33.2\text{A}$
- $5.0^\circ\text{C}$ = $33.6\text{A}$

The current limit adjusts smoothly between C-rate thresholds as the battery temperature changes. This reduces current hunting and minimises equipment stress.

## The Delta Calculation
Unlike some systems that overwrite the maximum current, this function calculates a negative delta to be applied to a configured current limit.

$$\text{Target Current} = \text{Allowed Rate} \times \text{Battery Capacity (Ah)}$$
$$\text{Delta} = \text{Target Current} - \text{Max Configured Current}$$

Example:
- Battery Capacity: 280Ah
- Configured Max Charge Limit: 140A
- Interpolated Rate at 4.9°C: 0.12C
- Calculation: $(0.12 \times 280) - 140 = -106.4\text{A}$
- **Result:** The system requests a reduction of 106.4A, effectively setting the limit to 33.6A.

## Safety & Edge Cases

- The code contains a clamp that ensures the logic can only lower the current limit, never increase it beyond configured limits settings.
- If the `Temperature-based Current Limitation` switch is turned OFF, the Delta is immediately reset to 0 to prevent temperature based current restrictions.
- If any critical sensor (temperature or capacity) returns NaN (Not a Number), the system defaults the Delta to 0 to prevent unpredictable behavior.

## Configuration
The behavior is dictated by the following tables defined in the main YAML. These values represent the multiplier of the total Ah capacity (C-rate).

```YAML
  # +-------------------------------------------------------------------------
  # | Temperature-based current limitation
  # | Can be disabled via the switch "Temperature-based current limitation"
  # | This factor is applied to the battery capacity (Ah), not the current 
  # | maximum charge/discharge current. For example : 280Ah x 0.5 = 140A
  # +-------------------------------------------------------------------------
  # Temperature °C -> Charge Rate (0.0C to 1.0C)
  yambms_charging_rate_table: |
    {
      {  0.0, 0.05 },
      {  5.0, 0.12 },
      { 10.0, 0.30 },
      { 20.0, 0.50 },
      { 25.0, 0.50 },
      { 45.0, 0.50 },
      { 50.0, 0.50 },
      { 55.0, 0.50 },
      { 60.0, 0.00 }
    }
 # Temperature °C -> Discharge Rate (0.0C to 1.0C)
  yambms_discharging_rate_table: |
    {
      {-30.0, 0.00 },
      {-20.0, 0.50 },
      {-10.0, 0.50 },
      { -5.0, 0.50 },
      {  0.0, 0.50 },
      {  5.0, 0.50 },
      { 45.0, 0.50 },
      { 50.0, 0.50 },
      { 55.0, 0.50 },
      { 60.0, 0.00 }
    }
```
These values can be adjusted as needed, including adding or removing rows - the function will handle these changes automatically.
