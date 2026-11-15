import numpy as np
import pandas as pd
from glob import glob
from pathlib import Path

from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import seaborn as sns

from europa_eutectic.util import colors
from europa_eutectic.gaia_sim import GaiaSim
import gaia


base_cmap = sns.color_palette("icy_moon_2", as_cmap = True) # My custom colormap
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

for parameter_study_path in parameter_study_set:
    
    full_path = AUX_BASE / parameter_study_path


    if not any(full_path.glob("*.json")):
        print(f"No simulation .json files found in {full_path}")
        continue


    for sim_path in full_path.glob("*.json"):
        sim = GaiaSim.load_from_json(sim_path)
        
        avg_temp_field = sim.avg_temp_2d
        temp_levels = np.linspace(np.nanmin(avg_temp_field), np.nanmax(avg_temp_field), 256)
        sim.plot_field(avg_temp_field, "Temperature (K)", temp_levels, savepath = full_path / "vis")

        
        sim.plot_eutectics(savepath = full_path / "vis")
        
        for attenuation_field in sim.attenuation_interfaces:
            two_way_attenuation = attenuation_field.attenuation_2d
            two_way_attenuation[two_way_attenuation > attenuation_field.attenuation_limit] = attenuation_field.attenuation_limit 
            attenuation_levels = np.linspace(np.nanmin(two_way_attenuation), np.nanmax(two_way_attenuation), 256)
            inferno = sns.color_palette("inferno", as_cmap = True)
            sim.plot_field(two_way_attenuation, f"Two-Way Attenuation (dB) - {attenuation_field.attenuation_model}", attenuation_levels, cmap = inferno, savepath = full_path / "vis")


        if sim.avg_deformation_2d is not None:
            deformation_field = sim.avg_deformation_2d
            unique_vals = np.unique(deformation_field)
            n_colors = unique_vals.size
            icy_palette = ListedColormap(base_cmap(np.linspace(0.15, 0.82, n_colors)))
            levels = np.arange(unique_vals.min()-0.5, unique_vals.max() + 0.6, 1.0) 

            
            sim.plot_field(deformation_field, "Deformation Index", levels = levels, cmap = icy_palette, savepath = full_path / "vis")

        

        sns.set_theme(style="whitegrid", context="paper", font_scale=1.4)
        
        if sim.rms_velocity_temporal.shape != sim.times.shape:
            sim.rms_velocity_temporal = sim.rms_velocity_temporal[:-1]

        g = sns.lineplot(x = sim.times, y = sim.rms_velocity_temporal)                                
        
        avg_rms_velocity = np.array([sim.avg_rms_velocity for time in sim.times])
        g.plot(sim.times, avg_rms_velocity, color = "grey", linestyle = "--", label = "Average RMS Velocity")

        g.set_xlabel("Time (Myr)")
        g.set_ylabel("RMS Velocity (cm/year)")
        g.set_title(f"{sim.parent_dir.name}: {sim.caseID}")
        g.legend()
        plt.savefig(full_path / "vis" / f"{sim.caseID}_rms_velocity.png", bbox_inches='tight', pad_inches=0, transparent=True, dpi = 160)
        plt.close()

        

            
        
        

