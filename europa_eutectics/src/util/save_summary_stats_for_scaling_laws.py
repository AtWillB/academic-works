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
    "Eutectic Type": [],
    "Eutectic Temperature (K)": [],
    "log(η_ref) (Pa·s)":[],
    "D (km)": [],
    "Eutectic Depth (km)": [],
    "Stagnant Lid Thickness (km)": [],
    "Detectability Low Loss (%)": [],
    "Detectability High Loss (%)": [],
    "Eutectic Amplitude (%)": [],
    "Sim Folder": []
}

for parameter_study_path in parameter_study_set:
    
    full_path = AUX_BASE / parameter_study_path

    if not any(full_path.glob("*.json")):
        print(f"No simulation .json files found in {full_path}")
        continue

    for sim_path in full_path.glob("*.json"):


        sim = GaiaSim.load_from_json(sim_path)
        for eutectic in sim.eutectics:
            eutectic_type = ""

            if eutectic.eutectic_temperature == 237.15:
                eutectic_type = "Zolotov"
            elif eutectic.eutectic_temperature == 252.05:
                eutectic_type = "NaCl"
                
            df_dict["Eutectic Type"].append(eutectic_type)
            df_dict["Eutectic Temperature (K)"].append(eutectic.eutectic_temperature)
            df_dict["log(η_ref) (Pa·s)"].append(sim.eta_ref)
            df_dict["D (km)"].append(int(sim.D))
            df_dict["Eutectic Depth (km)"].append(eutectic.avg_depth_to_eutectic/1000)
            df_dict["Stagnant Lid Thickness (km)"].append(np.mean(sim.avg_stagnant_lid_depth))

            residual_low_loss_depth = eutectic.depth_to_eutectic - sim.attenuation_interfaces[0].depth_to_attenuation_limit
            df_dict["Detectability Low Loss (%)"].append(((residual_low_loss_depth.shape[0] - residual_low_loss_depth[residual_low_loss_depth > 0].shape[0]) / residual_low_loss_depth.shape[0]) * 100)
            residual_high_loss_depth = eutectic.depth_to_eutectic - sim.attenuation_interfaces[1].depth_to_attenuation_limit
            df_dict["Detectability High Loss (%)"].append(((residual_high_loss_depth.shape[0] - residual_high_loss_depth[residual_high_loss_depth > 0].shape[0]) / residual_high_loss_depth.shape[0]) * 100)

            isotherm_amplitude = abs(np.min(eutectic.depth_to_eutectic/1000) - np.max(eutectic.depth_to_eutectic/1000))/sim.D * 100 # relative to D
            df_dict["Eutectic Amplitude (%)"].append(isotherm_amplitude)

            df_dict["Sim Folder"].append(sim.parent_dir.name)


eutectic_df = pd.DataFrame(df_dict)
eutectic_df.to_csv(AUX_BASE / "eutectic_data_full_study.csv", index=False)