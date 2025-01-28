# YamBMS - Charging Logic

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

> [!NOTE]
> Please read the documentation regarding the [charging settings](YamBMS_functions.md#charging-settings).

## Charging Logic Diagram

The charging voltage and current correspond to the default values in the YAML script and can be modified.

![Image](../../images/YamBMS_Charging_Logic_Diagram.png "YamBMS Charging Logic")

## Cut-Off Charging Logic Equation

Source: [Charging Marine Lithium Battery Banks](https://nordkyndesign.com/charging-marine-lithium-battery-banks)

Special thanks to [@shvmm](https://github.com/shvmm) for creating the equations.

Note: The equations below are valid for other chemistries like Li-ion and LTO but with other CVmin and CVmax values.

![Image](../../images/YamBMS_Cut-Off_Charging_Logic_for_LFP_Equation.png "JK-BMS-CAN Cut-Off Charging Logic_for LFP Equation")

## Cut-Off Charging Logic Diagram (what's happening in the yellow diamond)

Note: The diagram below is valid for other chemistries like Li-ion and LTO but with other CVmin and CVmax values.

![Image](../../images/YamBMS_Cut-Off_Charging_Logic_Diagram.png "YamBMS Cut-Off Charging Logic Diagram")

## LFP Cut-Off Values

- Nominal : 3.20 V
- CV min : 3.37 V
- CV max : 3.65 V

![Image](../../images/YamBMS_LFP_Cut-Off_Values.png "LFP Cut-Off Values")

## Li-ion Cut-Off Values

- Nominal : 3.60 V
- CV min : 3.90 V
- CV max : 4.20 V

![Image](../../images/YamBMS_Li-ion_Cut-Off_Values.png "Li-ion Cut-Off Values")

## LTO Cut-Off Values

- Nominal : 2.40 V
- CV min : 2.55 V
- CV max : 2.85 V

![Image](../../images/YamBMS_LTO_Cut-Off_Values.png "LTO Cut-Off Value")
