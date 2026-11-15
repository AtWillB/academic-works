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

df_dict = {
    "CaseID": [],
    "Parameter Folder": [],
    "D (km)": [],
    "η_reff (Pa·s)": [],
    "Rayleigh Number": [],
    "Nusselt Top": [],
    "Nusselt Bottom": [],
    "Final Time (Myr)": []
}


for parameter_study_path in parameter_study_set:
    
    full_path = AUX_BASE / parameter_study_path

    if not any(full_path.glob("*.json")):
        print(f"No simulation .json files found in {full_path}")
        continue

    for sim_path in full_path.glob("*.json"):
        sim = GaiaSim.load_from_json(sim_path)

        df_dict["CaseID"].append(sim.caseID)
        df_dict["Parameter Folder"].append(parameter_study_path)
        df_dict["D (km)"].append(int(sim.D))
        df_dict["η_reff (Pa·s)"].append(sim.eta_ref)
        df_dict["Rayleigh Number"].append(sim.Ra)
        df_dict["Nusselt Top"].append(sim.avg_Nusselt_top)
        df_dict["Nusselt Bottom"].append(sim.avg_Nusselt_bottom)
        df_dict["Final Time (Myr)"].append(sim.final_time)


rayleigh_nusselt_df = pd.DataFrame(df_dict)
rayleigh_nusselt_df.to_csv(AUX_BASE / "rayleigh_nusselt_data_full_study.csv", index=False)