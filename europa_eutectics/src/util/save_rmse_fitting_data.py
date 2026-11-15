from pathlib import Path
import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

import gaia_studies as gu
from europa_eutectic.scaling_laws import  quad, plot_quad



# Column names in our data set
avg_depth_col = "Eutectic Depth (km)"
eta_col = "log(η_reff) (Pa·s)"
D_col = "D (km)"
color_col = "Eutectic Type"
eut_col_name = "Eutectic Depth (km)"

BASE = Path("../../../data/auxillary")
zol_df, nacl_df = quad.wrangle_data(BASE / "eutectic_data_full_study.csv")



z_col = D_col

func_list = {"Reduced Quadratic": quad.f_xy_x2,
             "Square Root Bend": quad.f_xy_sqrt,
             "Log Bend": quad.f_xy_log,
             "Reciprocal Bend": quad.f_xy_recip}

RMSE_D_solve_dict = {"Function": [],
                   "Solution Number": [],
                   f"RMSE": [], 
                   "a1": [],
                   "b1": [],
                   "c1": [],
                   "d1": [],
                   "a2": [],
                   "b2": [],
                   "c2": [],
                   "d2": []}

for func_name, func in func_list.items():
    func_coeff_f_D_return = quad.fit_func(zol_df, avg_depth_col, D_col, eta_col, func)
    func_coeff_g_D_return = quad.fit_func(nacl_df, avg_depth_col, D_col, eta_col, func)

    func_D_solutions = quad.solve_eq_for_z(func_coeff_f_D_return[-1], 
                                       func_coeff_g_D_return[-1], 
                                       func)
    h_df = pd.DataFrame({
        "Zolotov Depth (km)":  zol_df[eut_col_name].values,
        "NaCl Depth (km)":  nacl_df[eut_col_name].values,
        z_col:  zol_df[z_col].values
    })
    
    i = 0
    for key, solve in func_D_solutions.items():
        if "Solve" in key:

            residuals, rmse = quad.calc_residuals(h_df, "Zolotov Depth (km)", "NaCl Depth (km)", z_col, solve)

            RMSE_D_solve_dict["Function"].append(func_name)
            RMSE_D_solve_dict["Solution Number"].append(i+1)
            RMSE_D_solve_dict[f"RMSE"].append(rmse)
            i += 1
            
        if "Coeff 1" in key:
            for coeff_key, coeff_value in func_D_solutions[key].items():
                RMSE_D_solve_dict[str(coeff_key)].append(coeff_value)
        elif "Coeff 2" in key:
            for coeff_key, coeff_value in func_D_solutions[key].items():
                RMSE_D_solve_dict[str(coeff_key)].append(coeff_value)

RMSE_D_solve_df = pd.DataFrame(RMSE_D_solve_dict, columns=["Function", "Solution Number", f"RMSE", "a1", "b1", "c1", "d1", "a2", "b2", "c2", "d2"])
RMSE_D_solve_df["Solved For"] = "D (km)"

z_col = eta_col

func_list = {"Reduced Quadratic": quad.f_xy_x2,
             "Square Root Bend": quad.f_xy_sqrt,
             "Log Bend": quad.f_xy_log,
             "Reciprocal Bend": quad.f_xy_recip}

RMSE_eta_solve_dict = {"Function": [],
                   "Solution Number": [],
                   f"RMSE": [], 
                   "a1": [],
                   "b1": [],
                   "c1": [],
                   "d1": [],
                   "a2": [],
                   "b2": [],
                   "c2": [],
                   "d2": []}

for func_name, func in func_list.items():
    func_coeff_f_eta_return = quad.fit_func(zol_df, avg_depth_col, eta_col, D_col, func)
    func_coeff_g_eta_return = quad.fit_func(nacl_df, avg_depth_col, eta_col, D_col, func)

    func_eta_solutions = quad.solve_eq_for_z(func_coeff_f_eta_return[-1], 
                                       func_coeff_g_eta_return[-1], 
                                       func)
    h_df = pd.DataFrame({
        "Zolotov Depth (km)":  zol_df[eut_col_name].values,
        "NaCl Depth (km)":  nacl_df[eut_col_name].values,
        z_col:  zol_df[z_col].values
    })
    
    i = 0
    for key, solve in func_eta_solutions.items():
        if "Solve" in key:

            residuals, rmse = quad.calc_residuals(h_df, "Zolotov Depth (km)", "NaCl Depth (km)", z_col, solve)

            RMSE_eta_solve_dict["Function"].append(func_name)
            RMSE_eta_solve_dict["Solution Number"].append(i+1)
            RMSE_eta_solve_dict[f"RMSE"].append(rmse)
            i += 1

        if "Coeff 1" in key:
            for coeff_key, coeff_value in func_eta_solutions[key].items():
                RMSE_eta_solve_dict[str(coeff_key)].append(coeff_value)
        elif "Coeff 2" in key:
            for coeff_key, coeff_value in func_eta_solutions[key].items():
                RMSE_eta_solve_dict[str(coeff_key)].append(coeff_value)
        

RMSE_eta_solve_df = pd.DataFrame(RMSE_eta_solve_dict, columns=["Function", "Solution Number", f"RMSE", "a1", "b1", "c1", "d1", "a2", "b2", "c2", "d2"])
RMSE_eta_solve_df["Solved For"] = "log(η_reff) (Pa·s)"

RMSE_solve_df = pd.concat([RMSE_D_solve_df, RMSE_eta_solve_df], axis=0)
RMSE_solve_df.to_csv("../../../data/auxillary/RMSE_solve_data_full_study.csv", index=False)