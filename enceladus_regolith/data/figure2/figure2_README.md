# Figure 2 data

Figure 2 data are stored as whitespace-delimited temperature-profile text files
and comma-delimited CSV files.

## Temperature profiles

The two folders contain profiles used to generate the Figure 2 heat maps. Each
folder has 45 `.txt` files, for 90 profiles total. The filename encodes the
regolith depth, ice-shell depth, and regolith thermal conductivity. Across the
profiles, these parameters vary as follows:

| Parameter | Values |
| --- | --- |
| Regolith depth | 0, 100, 250, 400, and 700 m |
| Ice-shell depth | 5, 21, and 35 km |
| Regolith thermal conductivity | 0.1, 0.025, and 0.001 W/mK |

| Folder | Surface temperature indicated by folder name |
| --- | --- |
| `temperature_profiles_Ts_60/` | 60 K |
| `temperature_profiles_Ts_85/` | 85 K |

Each profile is a whitespace-delimited table with three columns:

| Column | Description |
| --- | --- |
| 1 | Radius, in meters |
| 2 | Depth, in meters |
| 3 | Temperature, in kelvin |

## Attenuation calculations

The attenuation CSVs contain heat-map values for the temperature-profile
combinations. Each folder contains six files: one for each of the three
ice-shell depths and two attenuation models (`low_loss` and `high_loss`).
Together, the three folders contain 18 files.

| Folder | Attenuation threshold |
| --- | --- |
| `attenuation_calculations/` | 100 dB |
| `attenuation_calculations_70_dB/` | 70 dB |
| `attenuation_calculations_130_dB/` | 130 dB |

The filenames identify the ice-shell depth and loss model. Each comma-delimited
CSV has a header row and contains:

| Column | Description |
| --- | --- |
| `Regolith Depth [m]` | Regolith depth, in meters |
| `0.1 W/mK` | Penetration depth as a percentage of the ice-shell depth for this conductivity |
| `0.025 W/mK` | Penetration depth as a percentage of the ice-shell depth for this conductivity |
| `0.001 W/mK` | Penetration depth as a percentage of the ice-shell depth for this conductivity |

The conductivity labels identify heat-map series; they do not represent the
regolith conductivity values in the temperature profiles. A penetration value
of `100.0` means the radar reaches the full ice shell before reaching the
specified attenuation threshold.

## Summary statistics

`figure2_stats.csv` contains summary statistics for the heat maps:

| Column | Description |
| --- | --- |
| `iceshell_depth` | Ice-shell depth, in kilometers |
| `attenuation_model` | Attenuation model |
| `min`, `max`, `mean` | Minimum, maximum, and mean penetration percentages across the heat-map cells |
| `num_to_ocean` | Number of heat-map cells where penetration reaches 100% of the ice-shell depth |

These statistics correspond to the 100 dB threshold in
`attenuation_calculations/`. The stats file does not include separate
statistics for the 70 dB and 130 dB folders.
