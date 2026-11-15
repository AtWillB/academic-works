# Figure 3 data

Figure 3a and Figure 3b use comma-delimited CSV files containing map data and
summary statistics.

## Ice-shell depth maps

`ice_shell_depth_maps/` contains two maps from Hemingway & Mittal (2019), one
for each map tile (`a` and `b`). The files contain numeric matrices with
comment lines describing the map. Each matrix has 181 rows and 361 columns;
rows correspond to latitude and columns to longitude. Each cell gives the
ice-shell depth in meters.

## Regolith distribution maps

`regolith_distribution_maps/` contains three maps: `bc_regolith_dist.csv`,
`exp_regolith_dist.csv`, and `no_regolith_dist.csv`. They represent the
best-case, exponential, and no-regolith distributions, respectively. Each file
contains a 181-by-361 numeric matrix with comment lines describing the map;
rows correspond to latitude, columns to longitude, and cell values are
regolith depth in meters.

## Attenuation calculation maps

`attenuation_calculations_maps/` contains 14 maps, divided between two
subfolders:

| Subfolder | Loss model | Number of maps |
| --- | --- | --- |
| `low_loss/` | Low-loss attenuation profile | 7 |
| `high_loss/` | High-loss attenuation profile | 7 |

The maps give relative depth penetration as a percentage of ice-shell depth.
Each comma-delimited file contains a 181-by-361 numeric matrix, preceded by
comment lines identifying the ice-shell map tile, regolith distribution, loss
model, and units. Rows correspond to latitude and columns to longitude. The
files cover map tiles A and B with the best-case, exponential, and no-regolith
distributions, plus tile D with the no-regolith distribution.

## Summary statistics

`figure3a_stats.csv` and `figure3b_stats.csv` contain summary statistics for
the corresponding figure panels. Each row describes one combination of
ice-shell map, regolith distribution, and attenuation model. The columns are:

| Column | Description |
| --- | --- |
| `icesehll_map` | Ice-shell map tile used (column name as stored in the CSV) |
| `regolith_distribution` | Regolith distribution used |
| `attenuation_model` | Attenuation model (`low_loss` or `high_loss`) |
| `global_min`, `global_max`, `global_mean` | Minimum, maximum, and mean relative depth penetration across the map, in percent |
| `mean_at_north_pole`, `mean_at_equator`, `mean_at_south_pole` | Mean relative depth penetration in the corresponding latitude region, in percent |
| `percent_at_ocean` | Percentage of map cells where penetration reaches 100% of the ice-shell depth |
