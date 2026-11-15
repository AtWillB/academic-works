import numpy as np
import pandas as pd
from glob import glob
from pathlib import Path

from europa_eutectic.gaia_sim import GaiaSim




AUX_BASE = Path("/plp_user/byrn_wi/europa_eutectic/data/auxillary")


shell_visc ="shell_visc"
shell_thermal_constK_varA = "shell_thermal_cond_expan/constK_varA"
shell_thermal_varK_constA = "shell_thermal_cond_expan/varK_constA"
shell_thermal_varK_varA = "shell_thermal_cond_expan/varK_varA"
shell_complex_rheo = "shell_complex_rheo"
shell_tidal = "shell_tidal"

parameter_study_set = [shell_visc,
                       shell_thermal_constK_varA,
                       shell_thermal_varK_constA,
                       shell_thermal_varK_varA,
                       shell_complex_rheo,
                       shell_tidal]

df_list = []

for parameter_study_path in parameter_study_set:
    
    parameter_study_folder = AUX_BASE / parameter_study_path

    if not any(parameter_study_folder.glob("*.json")):
        print(f"No simulation .json files found in {parameter_study_folder}")
        continue

    for sim_path in parameter_study_folder.glob("*.json"):
        df_dict = {
            "Time (Myr)": [],
            "RMS Velocity (cm/year)": [],
            "Average RMS Velocity (cm/year)": [],
            "D (km)": [],
            "log(η_reff) (Pa·s)":[],
            "Parameter Folder": []
        }

        sim = GaiaSim.load_from_json(sim_path)

        df_dict["Time (Myr)"] = np.array(sim.times)

        rms_velocity_temporal = sim.rms_velocity_temporal
        if sim.times.shape != sim.rms_velocity_temporal.shape:
            rms_velocity_temporal = sim.rms_velocity_temporal[:-1]

        df_dict["RMS Velocity (cm/year)"] = np.array(rms_velocity_temporal)
        df_dict["Average RMS Velocity (cm/year)"] = np.array([sim.avg_rms_velocity for time in sim.times])
        df_dict["D (km)"] = np.array([int(sim.D) for time in sim.times])
        df_dict["log(η_reff) (Pa·s)"] = np.array([sim.eta_ref for time in sim.times])
        df_dict["Parameter Folder"] = np.array([sim.parent_dir.name for time in sim.times])


        stats_df = pd.DataFrame(df_dict)
        df_list.append(stats_df)
    
    
big_df = pd.concat(df_list)
big_df.to_csv(AUX_BASE / "rms_vel_data_full_study.csv", index=False)




