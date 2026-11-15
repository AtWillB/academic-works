from pathlib import Path
import numpy as np
from europa_eutectic.gaia_sim import GaiaSim
from glob import glob


SIM_BASE = Path("/plp_user/byrn_wi/scr1")
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


for parameter_study_folder in parameter_study_set:
    full_study_path = SIM_BASE / parameter_study_folder
    print("Running save loop for " + parameter_study_folder)

    for sim_path in full_study_path.glob("*"):
        p = Path(sim_path)

        print(f"Loading {p.name} ...")
        if str(AUX_BASE / parameter_study_folder / p.name) + "_data.json" in glob(str(AUX_BASE / parameter_study_folder / "*")):
            print(f"Already saved {p.name}, skipping...")
            continue
        sim = GaiaSim(p)
        sim.save(AUX_BASE / parameter_study_folder)


