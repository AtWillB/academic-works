import numpy as np
import pandas as pd
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
    "D (km)": [],
    "log(η_ref) (Pa·s)":[],
    "Sim Folder": [],
    "Attenuation Model": [],
    "Minimum Interface Depth (km)": [],
    "Mean Interface Depth (km)": [],
    "Maximum Interface Depth (km)": [],
    "Smallest Distance to Ice Ocean Interface (km)": [],
    "Ice Ocean Interface Detected": [],
    "Ice Ocean Interface Detectability (%)": []
}

for parameter_study_path in parameter_study_set:
    
    full_path = AUX_BASE / parameter_study_path


    if not any(full_path.glob("*.json")):
        print(f"No simulation .json files found in {full_path}")
        continue


    for sim_path in full_path.glob("*.json"):

        sim = GaiaSim.load_from_json(sim_path)

        for interface in sim.attenuation_interfaces:
            
            df_dict["D (km)"].append(sim.D)
            df_dict["log(η_ref) (Pa·s)"].append(sim.eta_ref)
            df_dict["Sim Folder"].append(sim.parent_dir.name)
            df_dict["Attenuation Model"].append(interface.attenuation_model)

            interface_depth = interface.depth_to_attenuation_limit
            cleaned_interface_depth = interface_depth[~np.isnan(interface_depth)]
            max_depth = np.max(sim.depth_2d)

            df_dict["Minimum Interface Depth (km)"].append(np.min(cleaned_interface_depth)/1e3)
            df_dict["Mean Interface Depth (km)"].append(np.mean(cleaned_interface_depth)/1e3)
            df_dict["Maximum Interface Depth (km)"].append(np.max(cleaned_interface_depth)/1e3) 
            if np.any(np.isnan(interface_depth)):
                df_dict["Smallest Distance to Ice Ocean Interface (km)"].append(0)
            else:
                df_dict["Smallest Distance to Ice Ocean Interface (km)"].append((max_depth - np.max(cleaned_interface_depth))/1e3)
            df_dict["Ice Ocean Interface Detectability (%)"].append((np.isnan(interface_depth).sum()/interface_depth.size) * 100)
            df_dict["Ice Ocean Interface Detected"].append(np.any(np.isnan(interface_depth)))

attenuation_df = pd.DataFrame(df_dict)
attenuation_df.to_csv(AUX_BASE / "attenuation_data_full_study.csv", index=False)