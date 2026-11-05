# Why YamBMS, if my BMS already talks to my inverter?

Most YamBMS installations run on BMS models that can be wired straight to an inverter — JK
accounts for about 72% of them, and RS485 for about 65% of the links. These users could skip
YamBMS entirely. They don't.

The reason is that a working link is not the same as a good one. Your BMS firmware is closed and
its logic is fixed. Your inverter's firmware is closed and has its own quirks. YamBMS sits
between the two and is the only layer in that chain you can actually configure, observe and fix.

## Does any of this sound familiar?

**"My SoC drifts further off every week, ever since I stopped charging to 100%."**
A BMS estimates SoC by counting coulombs through its own internal shunt, and recalibrates when
the pack reaches full charge. If you deliberately stop short of full — which is exactly what you
should do to limit calendar ageing — that recalibration never happens and the error accumulates.
This is not a firmware bug that a future update will fix; it is the limit of the method.

It matters more than a wrong gauge reading, because many inverters make their decisions from
SoC. A drifting SoC produces an inverter that cuts discharge too early, force-charges for no
reason, or switches to grid at the wrong moment. You end up troubleshooting the inverter when
the real problem is upstream.

YamBMS lets you combine an external shunt and use **its** SoC as the reference sent to the
inverter — measured on the real system current, independent of what each BMS believes about its
own pack. This is the problem the project was originally built to solve.

**"My inverter charges at a higher voltage than the BMS asked for."**
Some inverters hold their output slightly above the requested CVL — around 0.1 to 0.3 V. A BMS
wired directly has no way to react: it sends its setpoint and lives with the result. `Auto CVL`
is a PI controller that measures the actual result and trims the request until the pack sits
where it should.

**"My inverter discharges the battery when it switches from Bulk to Float."**
A sudden drop in requested voltage can make an inverter pull the pack back down to the new
target instead of simply stopping. `Auto Float` ramps the voltage down gradually instead of
stepping it, so the transition stays smooth.

**"My battery sits at 100% all day and I worry about its lifespan."**
`Auto SoC Limit` lets you charge to a target SoC instead of to full, switching to `Float`,
limiting the charge current, or both once the limit is reached.

**"One cell hits OVP at the end of charge while the others are still well below."**
Cells with different internal resistance diverge under current — the weakest one runs ahead and
trips the alarm. `Auto CCL Current Taper` reduces the charge current along a knee-to-bulk curve
so the pack reaches bulk cleanly, then holds a low balance current so there is a real balancing
window instead of a race to zero.

**"I added a third BLE pack and the connections keep dropping."**
An ESP32 saturates after a small number of simultaneous BLE links. YamBMS's server/client
architecture turns each BLE, UART or RS485 BMS into a Modbus RS485 node, so the number of packs
is no longer limited by the BLE stack. Every server node still publishes its full telemetry to
Home Assistant on its own; only the values needed for aggregation travel on the bus.

## Where it also helps

- **Inverters that follow a protocol loosely.** SRNE units and their rebranded variants are a
  recurring case with PYLON RS485. YamBMS speaks several inverter protocols and is fixed on the
  YamBMS side when an inverter misbehaves — you don't have to wait for a firmware release.
- **Mixed batteries.** Different BMS brands or models that cannot talk to each other are
  combined into a single view and a single link to the inverter.
- **Non-communicating BMS.** YamBMS supplies the communication layer that isn't there.
- **Active balancers.** Supervised in the same device rather than left as a silent box in the
  corner.
- **Visibility.** Everything lands in Home Assistant — per-pack entities, a ready-made dashboard,
  and an optional LVGL display.

## When you don't need it

If your BMS drives your inverter correctly, your SoC is accurate, and the default behaviour
suits you, you don't need YamBMS. It earns its place when the fixed logic on either side stops
matching what you want from your system.

*Around 256 installations are running today.*
