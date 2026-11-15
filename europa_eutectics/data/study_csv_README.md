# Study-wide CSV data

The `*_full_study.csv` files summarize or analyze simulation results. Each is a comma-delimited table with a header row. The descriptions below use the column names exactly as stored in the files.

## Eutectic data

`eutectic_data_full_study.csv` has 90 rows, one per simulation and eutectic.
It is used by Figure 5 for eutectic detectability.

| Column | Description |
| --- | --- |
| `Eutectic Type` | Eutectic identifier, such as `Zolotov` or `NaCl` |
| `Eutectic Temperature (K)` | Eutectic temperature, in kelvin |
| `log(η_ref) (Pa·s)` | Base-10 logarithm of reference viscosity in Pa s |
| `D (km)` | Reference shell thickness, in kilometers |
| `Eutectic Depth (km)` | Mean depth of the eutectic interface, in kilometers |
| `Stagnant Lid Thickness (km)` | Mean stagnant-lid thickness, in kilometers |
| `Detectability Low Loss (%)` | Percentage of lateral positions counted as detectable using the low-loss attenuation model |
| `Detectability High Loss (%)` | Percentage of lateral positions counted as detectable using the high-loss attenuation model |
| `Eutectic Amplitude (%)` | Range of eutectic depths divided by shell thickness, expressed as a percentage |
| `Sim Folder` | Name of the simulation's parent study folder |

## Attenuation data

`attenuation_data_full_study.csv` has 90 rows, one per simulation and
attenuation model. The saved simulations specify a 100 dB threshold. No direct
use of this CSV was found in the included figure notebooks.

| Column | Description |
| --- | --- |
| `D (km)` | Reference shell thickness, in kilometers |
| `log(η_ref) (Pa·s)` | Base-10 logarithm of reference viscosity in Pa s |
| `Sim Folder` | Name of the simulation's parent study folder |
| `Attenuation Model` | Attenuation model: `Low Loss` or `High Loss` |
| `Minimum Interface Depth (km)` | Minimum finite attenuation-threshold depth, in kilometers |
| `Mean Interface Depth (km)` | Mean finite attenuation-threshold depth, in kilometers |
| `Maximum Interface Depth (km)` | Maximum finite attenuation-threshold depth, in kilometers |
| `Smallest Distance to Ice Ocean Interface (km)` | Difference between maximum simulation depth and maximum threshold depth, or zero if any threshold depth is missing |
| `Ice Ocean Interface Detected` | Whether any lateral position has no attenuation-threshold crossing |
| `Ice Ocean Interface Detectability (%)` | Percentage of lateral positions with no attenuation-threshold crossing |

## Rayleigh and Nusselt data

`rayleigh_nusselt_data_full_study.csv` has 45 rows, one per simulation. No
direct use of this CSV was found in the included figure notebooks.

| Column | Description |
| --- | --- |
| `CaseID` | Simulation case identifier |
| `Parameter Folder` | Study folder path relative to the data root |
| `D (km)` | Reference shell thickness, in kilometers |
| `η_reff (Pa·s)` | Base-10 logarithm of reference viscosity in Pa s, despite the column label |
| `Rayleigh Number` | Reference Rayleigh number |
| `Nusselt Top` | Time-averaged top Nusselt number |
| `Nusselt Bottom` | Time-averaged bottom Nusselt number |
| `Final Time (Myr)` | Final output time, in millions of years |

## RMS velocity data

`rms_vel_data_full_study.csv` contains 40,836 rows of time-series data across
the simulations. No direct use of this CSV was found in the included figure
notebooks.

| Column | Description |
| --- | --- |
| `Time (Myr)` | Output time, in millions of years |
| `RMS Velocity (cm/year)` | RMS velocity at that output time, in centimeters per year |
| `Average RMS Velocity (cm/year)` | Simulation's average RMS velocity over the final 10% of saved outputs, in centimeters per year; repeated for each time |
| `D (km)` | Reference shell thickness, in kilometers |
| `log(η_reff) (Pa·s)` | Base-10 logarithm of reference viscosity in Pa s |
| `Parameter Folder` | Name of the simulation's parent study folder |
