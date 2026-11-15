import numpy as np
import pandas as pd
from pathlib import Path


from europa_eutectic.gaia_sim import GaiaSim
from europa_eutectic import attenuation_interface, eutectic_interface


AUX_BASE = Path("/plp_user/byrn_wi/europa_eutectic/data/auxillary")

shell_visc ="shell_visc"
shell_thermal_constK_varA = "shell_thermal_cond_expan/constK_varA"
shell_thermal_varK_constA = "shell_thermal_cond_expan/varK_constA"
shell_thermal_varK_varA = "shell_thermal_cond_expan/varK_varA"
shell_complex_rheo = "shell_complex_rheo"


parameter_study_set = [shell_visc, shell_thermal_constK_varA, shell_thermal_varK_constA, shell_thermal_varK_varA, shell_complex_rheo]


df_dict = {
    "Eutectic Type": [],
    "Eutectic Temperature (K)": [],
    "log(η_reff) (Pa·s)":[],
    "D (km)": [],
    "Eutectic Depth (km)": [],
    "Detectability Low Loss (%)": [],
    "Detectability High Loss (%)": [],
    "Eutectic Amplitude (%)": [],
    "Sim Folder": []
}

def calculate_attenuation(temp_2d, depth_2d, attenuation_model):
    n_layers, n_shells = temp_2d.shape
    attenuation_2d = np.zeros_like(temp_2d, dtype=float)

    pure_ice = None
    if attenuation_model == "Low Loss":
        pure_ice = True
    elif attenuation_model == "High Loss":
        pure_ice = False
    else:
        raise ValueError("Invalid attenuation model. Must be 'Low Loss' or 'High Loss'.")


    # check for uniform spacing in depth array
    depth_diffs = np.diff(depth_2d, axis=0)
    reference_diff = depth_diffs[0, 0]

    if not np.allclose(depth_diffs, reference_diff):
        raise ValueError("Depth array has non-uniform spacing, or some weird floating point error. Please check the depth array for issues.")

    delta_D_km = abs(reference_diff) / 1000

    for shell in range(n_shells):
        cumulative_attenuation = 0.0

        # avg_temp_2d and depth_2d are ordered from the ice-ocean interface to the surface,
        # so we iterate from the bottom layer to the top layer
        for layer in range(n_layers - 1, -1, -1):
            layer_attenuation = (
                2
                * 0.914 # this is dB/km, so deltaD does need to be in km
                * attenuation_interface.calc_electrical_conductivity(temp_2d[layer, shell], pure_ice)
                * delta_D_km
            )
            cumulative_attenuation += layer_attenuation
            attenuation_2d[layer, shell] = cumulative_attenuation

    return attenuation_2d


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
            df_dict["log(η_reff) (Pa·s)"].append(sim.eta_ref)
            df_dict["D (km)"].append(int(sim.D))
            
            last_output = sim.last_output
            last_temp_2d = last_output.T.formatted_data[:, :, 0] * sim.dim_coef["scale_T"] + sim.dim_data["T0"]
            
            eutectic_temp = eutectic.eutectic_temperature
            last_depth_to_eutectic = np.array([
                eutectic_interface.first_eutectic_depth(sim.depth_2d[:, j], last_temp_2d[:, j], eutectic_temp)
                for j in range(last_temp_2d.shape[1])
            ])
            df_dict["Eutectic Depth (km)"].append(np.nanmean(last_depth_to_eutectic) / 1000)


            last_attenuation_2d_low = calculate_attenuation(last_temp_2d, sim.depth_2d, sim.attenuation_interfaces[0].attenuation_model)
            last_attenuation_2d_high = calculate_attenuation(last_temp_2d, sim.depth_2d, sim.attenuation_interfaces[1].attenuation_model)
            
            last_depth_to_attenuation_limit_low = np.array([
                attenuation_interface.first_attenuation_limit(sim.depth_2d[:, j], last_attenuation_2d_low[:, j], sim.attenuation_interfaces[0].attenuation_limit)
                for j in range(last_temp_2d.shape[1])
            ])
            last_depth_to_attenuation_limit_high = np.array([
                attenuation_interface.first_attenuation_limit(sim.depth_2d[:, j], last_attenuation_2d_high[:, j], sim.attenuation_interfaces[1].attenuation_limit)
                for j in range(last_temp_2d.shape[1])
            ])

            residual_low_loss_depth = last_depth_to_eutectic - last_depth_to_attenuation_limit_low
            residual_high_loss_depth = last_depth_to_eutectic - last_depth_to_attenuation_limit_high


            df_dict["Detectability Low Loss (%)"].append(((residual_low_loss_depth.shape[0] - residual_low_loss_depth[residual_low_loss_depth > 0].shape[0]) / residual_low_loss_depth.shape[0]) * 100)
            df_dict["Detectability High Loss (%)"].append(((residual_high_loss_depth.shape[0] - residual_high_loss_depth[residual_high_loss_depth > 0].shape[0]) / residual_high_loss_depth.shape[0]) * 100)

            isotherm_amplitude = abs(np.min(last_depth_to_eutectic/1000) - np.max(last_depth_to_eutectic/1000))/sim.D * 100 # relative to D
            df_dict["Eutectic Amplitude (%)"].append(isotherm_amplitude)


            df_dict["Sim Folder"].append(sim.parent_dir.name)




eutectic_df = pd.DataFrame(df_dict)
eutectic_df.to_csv(AUX_BASE / "nonavg_eutectic_data_full_study.csv", index=False)