# Figure 4 data

Figure 4 data are stored in comma-delimited CSV files. The folder includes
ice-shell and regolith input maps, eutectic-depth maps, calculated attenuation
maps, and summary statistics.

## Ice-shell depth maps

`ice_shell_depth_maps/` contains two maps from Hemingway & Mittal (2019), for
map tiles `a` and `b`. Each file contains a 181-by-361 numeric matrix with
comment lines identifying the tile and units. Rows correspond to latitude,
columns to longitude, and cell values are ice-shell depth in meters.

## Regolith distribution maps

`regolith_distribution_maps/` contains three 181-by-361 maps:
`bc_regolith_dist.csv` (best-case), `exp_regolith_dist.csv` (exponential), and
`no_regolith_dist.csv` (no regolith). Comment lines identify the distribution,
units, and matrix dimensions. Rows correspond to latitude, columns to
longitude, and cell values are regolith depth in meters.

## Attenuation and eutectic-depth maps

The two attenuation-map folders each contain 18 CSV files: 12 attenuation maps
and 6 eutectic-depth maps.

| Folder | Ice-shell map tile |
| --- | --- |
| `attenuation_calculations_map_a/` | Hemingway map A |
| `attenuation_calculations_map_b/` | Hemingway map B |

The 12 attenuation maps in each folder cover ammonia (`NH3`) and ammonium
chloride (`NH4Cl`) eutectics, three regolith distributions (best-case,
exponential, and no regolith), and two attenuation models (low-loss and
high-loss). The remaining six files in each folder are eutectic-depth maps:
one for each combination of eutectic and regolith distribution. Filenames and
comment lines identify the eutectic, map tile, regolith distribution, and
attenuation model where applicable.

Each map is a comma-delimited 181-by-361 numeric matrix preceded by comment
lines. For attenuation outputs, the cell values are attenuation in decibels
at the corresponding eutectic depth. For eutectic-depth maps, the cells
represent the depth of the specified eutectic. Rows correspond to latitude
and columns to longitude.

## Summary statistics

`figure4_stats.csv` summarizes the attenuation results. Its columns identify
one combination of ice-shell map, regolith distribution, and attenuation
model per row. The columns are:

| Column | Description |
| --- | --- |
| `icesehll_map` | Ice-shell map tile used (column name as stored in the CSV) |
| `regolith_distribution` | Regolith distribution used |
| `attenuation_model` | Eutectic and attenuation-model combination |
| `global_min`, `global_max`, `global_mean` | Minimum, maximum, and mean attenuation at the eutectic depth across the map, in decibels |
| `mean_at_north_pole`, `mean_at_equator`, `mean_at_south_pole` | Mean attenuation at the eutectic depth in the corresponding latitude region, in decibels |
