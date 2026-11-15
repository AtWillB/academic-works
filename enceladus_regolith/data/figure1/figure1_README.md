# Figure 1 data

Figure 1 uses two data formats: whitespace-delimited text files and
comma-delimited CSV files.

## Temperature profiles

The 11 `.txt` files in `temperature_profiles/` describe one-dimensional
geophysical simulations of Enceladus's interior. Each file contains a
whitespace-delimited table. Calculations run from the ice–ocean interface
toward the surface.

| Column | Description |
| --- | --- |
| 1 | Radius, in meters |
| 2 | Depth, in meters |
| 3 | Temperature, in kelvin |

The profiles are grouped by the parameter varied in each simulation:

| Subfolder | Profiles | Parameters held constant | Parameter varied |
| --- | --- | --- | --- |
| `ice_shell_depth/` | 3 | Regolith thermal conductivity: 0.025 W/mK; regolith thickness: 250 m | Ice-shell depth |
| `regolith_conductivity/` | 3 | Ice-shell depth: 21 km; regolith thickness: 250 m | Regolith thermal conductivity |
| `regolith_depth/` | 4 | Ice-shell depth: 21 km; regolith thermal conductivity: 0.025 W/mK | Regolith depth |

## Attenuation calculations

The 6 `.csv` files in `attenuation_calculations/` contain attenuation
calculations for the one-dimensional temperature profiles. Each file is a
comma-delimited table. Calculations are reported for each simulation layer.

| Column | Description |
| --- | --- |
| `layerNum` | Layer number, starting from the surface |
| `depth_[m]` | Depth of the current simulation layer, in meters |
| `thickness_[km]` | Thickness of the current simulation layer, in kilometers |
| `temp_[k]` | Temperature of the current simulation layer, in kelvin |
| `attenuation_model` | Attenuation model: `high_loss` or `low_loss` |
| `twoway_loss_[db]` | Two-way attenuation of the current layer, in decibels |
| `sim_name` | Name of the one-dimensional temperature profile used for the calculation |

Each subfolder contains two sets of calculations—one using the low-loss
attenuation profile and one using the high-loss profile—for the temperature
profiles in the corresponding parameter group.

| Subfolder | Temperature-profile variations |
| --- | --- |
| `regolith_conductivity/` | Regolith thermal conductivity |
| `regolith_thickness/` | Regolith thickness |
| `ice_shell_depth/` | Ice-shell depth |

## Summary statistics

`figure1_stats.csv` contains one summary row for each temperature-profile and
attenuation-model combination. Its columns are:

| Column | Description |
| --- | --- |
| `sim_name` | Name of the temperature-profile simulation |
| `attenuation_model` | Attenuation model (`low_loss` or `high_loss`) |
| `twoway_loss` | Two-way attenuation at the reported penetration depth, in decibels |
| `pen_depth` | Penetration depth, in meters |
| `max_depth` | Maximum depth of the simulation, in meters |
| `pen_percent` | Penetration depth as a percentage of maximum simulation depth |