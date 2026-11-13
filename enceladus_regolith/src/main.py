import radar_attenuation.temp_profile_util as tpu
import radar_attenuation.conductive_profile_equations as cpe
import radar_attenuation.heatmap_util as hu
import radar_attenuation.depth_map_util as dmu

import matplotlib.pyplot as plt
from matplotlib import ticker
import matplotlib.transforms as mtransforms
from matplotlib.colors import ListedColormap
from matplotlib.colors import Normalize


import pandas as pd
import numpy as np
import itertools
import seaborn as sns

def load_group_temp_profiles(folderpath, prefix, suffix_list):
    temp_and_depth_dict = {}

    for suffix in suffix_list:

        profile_data = np.loadtxt(f"{folderpath}/{prefix}_{suffix}.txt")
        temp_and_depth_dict[suffix] = {'temp_data': profile_data[:, 2], 'depth_data': profile_data[:, 1]}
    return temp_and_depth_dict


def create_fig1_data():
    print("creating data for Figure 1")
    sim = {"Ro":252.1e3,
    "d_ocean":37e3, 
    "d_ice": 5e3, # ice thickness in m
    "Ts": 60, # surface temperature in K
    "resolution": 10, # model resolution in m
    "density_ice": 925, # kg/m3
    "density_water": 1050, # kg/m3
    "density_silicate": 2400, # kg/m3
    "klayer1"     : 0.025,
    "klayer1_str" : "0025",
    "k0": 651}
    fig1_savepath =  f"../../figures/figure1/data"


    sim["klayer2"] = 651/cpe.calc_TempIceOcean(sim["density_ice"], sim["d_ice"], sim["Ro"])

    sim_combo1 = sim
    sim_combo2 = sim
    sim_combo3 = sim

################################################################################################################################
    sim_combo1['d_regolith'] = 250
    sim_combo1['Rinterface'] = sim_combo1['Ro'] - sim_combo1['d_regolith']

    print("running ice shell depth")
    for attenuation_model in ("low_loss", "high_loss"):
        print(f'running {attenuation_model}')
        df_list = []    
        for ice_shell_depth, steps in [("5km", 10), ("21km", 100), ("35km", 100)]:
            print(f"running {ice_shell_depth}")
            sim_combo1[f'd_ice_{ice_shell_depth}'] = int(ice_shell_depth.split('km')[0])*1e3
            temp_profile, depth_profile = cpe.calc_ConductiveTempProfileVarkT(sim_combo1['klayer1'], sim_combo1['k0'],sim_combo1['Rinterface'], sim_combo1['density_ice'],
                                                sim_combo1[f'd_ice_{ice_shell_depth}'], sim_combo1['Ro'], sim_combo1['Ts'], sim_combo1['resolution'], 
                                                steps)
            
            
            sim_name = f"VarK_shell_depth_d{ice_shell_depth.split('km')[0]}"
            filename = f"{fig1_savepath}/temperature_profiles/ice_shell_depth/{sim_name}.txt"
            conductivity_model  = 'k_regolith = ' +  str(sim_combo1['klayer1']) + ' W/(mK), k_ice = ' + str(sim_combo1['klayer2']) + ' W/(mK), regolith thickness = ' + str(sim_combo1['d_regolith']) + ' m'
            cpe.write_data(filename, sim_combo1['Ro'], temp_profile, depth_profile, sim_combo1[f'd_ice_{ice_shell_depth}'], conductivity_model)
            
            attenuation_df = tpu.calc_attenuation_from_temp_profile(filename, 0, 2, attenuation_model, sim_name)
            attenuation_df.rename(columns= {"depth": "depth_[m]", "thickness":"thickness_[km]", "temp" : "temp_[k]", "twoway_loss":"twoway_loss_[db]"}, inplace = True)
            df_list.append(attenuation_df)
        
        atten_model_shell_depth_df = pd.concat(df_list)
        atten_model_shell_depth_df.to_csv(f"{fig1_savepath}/attenuation_calculations/ice_shell_depth/ice_shell_depth_{attenuation_model}.csv")


################################################################################################################################
    sim_combo2['d_ice'] =  21e3
    print("running regolith depth")
    for attenuation_model in ("low_loss", "high_loss"):
        print(f'running {attenuation_model}')
        df_list = []
        for regolith_depth, steps in [(0, 10), (100, 10), (400, 100), (700, 100)]:

            print(f"running {regolith_depth}")
            sim_combo2['d_regolith'] = regolith_depth
            sim_combo2['Rinterface'] = sim_combo2['Ro'] - sim_combo2['d_regolith']
            temp_profile, depth_profile = cpe.calc_ConductiveTempProfileVarkT(sim_combo2['klayer1'], sim_combo2['k0'],
                                                sim_combo2['Rinterface'], 
                                                sim_combo2['density_ice'], sim_combo2[f'd_ice'], sim_combo2['Ro'], sim_combo2['Ts'], sim_combo2['resolution'], 
                                                steps)
            
            sim_name = f"VarK_Regolith_{regolith_depth}"
            filename = f"{fig1_savepath}/temperature_profiles/regolith_depth/{sim_name}.txt"
            conductivity_model  = 'k_regolith = ' +  str(sim_combo2['klayer1']) + ' W/(mK), k_ice = ' + str(sim_combo2['klayer2']) + ' W/(mK), regolith thickness = ' + str(sim_combo2['d_regolith']) + ' m'
            cpe.write_data(filename, sim_combo2['Ro'], temp_profile, depth_profile, sim_combo2[f'd_ice'], conductivity_model)
            
            attenuation_df = tpu.calc_attenuation_from_temp_profile(filename, 0, 2, attenuation_model, sim_name)
            attenuation_df.rename(columns= {"depth": "depth_[m]", "thickness":"thickness_[km]", "temp" : "temp_[k]", "twoway_loss":"twoway_loss_[db]"}, inplace = True)
            df_list.append(attenuation_df)
        
        atten_model_shell_depth_df = pd.concat(df_list)
        atten_model_shell_depth_df.to_csv(f"{fig1_savepath}/attenuation_calculations/regolith_thickness/regolith_thickness_{attenuation_model}.csv")
################################################################################################################################
    
    sim_combo3['d_regolith'] = 250
    sim_combo3['Rinterface'] = sim_combo3['Ro'] - sim_combo3['d_regolith']
    sim_combo3['d_ice'] = 21e3 # ice thickness in m

    print("running regolith depth")

    for attenuation_model in ("low_loss", "high_loss"):
        print(f'running {attenuation_model}')
        df_list = []
        for regolith_conductivity, steps in [(0.1, 10), (0.025, 100), (0.001, 100)]:

            print(f"running {regolith_conductivity}")
            sim_combo3['klayer1'] = regolith_conductivity

            temp_profile, depth_profile = cpe.calc_ConductiveTempProfileVarkT(sim_combo3['klayer1'], sim_combo3['k0'],
                                                sim_combo3['Rinterface'], sim_combo3['density_ice'], sim_combo3[f'd_ice'],  
                                                sim_combo3['Ro'], sim_combo3['Ts'], sim_combo3['resolution'], 
                                                steps)
            
            sim_name = f"VarK_Conductivity_{str(regolith_conductivity).replace('.', '')}"
            filename = f"{fig1_savepath}/temperature_profiles/regolith_conductivity/{sim_name}.txt"
            conductivity_model  = 'k_regolith = ' +  str(sim_combo3['klayer1']) + ' W/(mK), k_ice = ' + str(sim_combo3['klayer2']) + ' W/(mK), regolith thickness = ' + str(sim_combo3['d_regolith']) + ' m'
            cpe.write_data(filename, sim_combo3['Ro'], temp_profile, depth_profile, sim_combo3[f'd_ice'], conductivity_model)
            
            attenuation_df = tpu.calc_attenuation_from_temp_profile(filename, 0, 2, attenuation_model, sim_name)
            attenuation_df.rename(columns= {"depth": "depth_[m]", "thickness":"thickness_[km]", "temp" : "temp_[k]", "twoway_loss":"twoway_loss_[db]"}, inplace = True)
            df_list.append(attenuation_df)
        
        atten_model_shell_depth_df = pd.concat(df_list)
        atten_model_shell_depth_df.to_csv(f"{fig1_savepath}/attenuation_calculations/regolith_conductivity/regolith_conductivity_{attenuation_model}.csv")

    print("Done making the data for figure 1!!")
    return

def plot_fig1():
    root_filepath = "../../figures/figure1/data/temperature_profiles"

    shell_thicknes_dict = load_group_temp_profiles(f"{root_filepath}/ice_shell_depth", "VarK_shell_depth", ['d5', 'd21', 'd35'])
    regolith_thickness_dict = load_group_temp_profiles(f"{root_filepath}/regolith_depth", "VarK_Regolith", ['0', '100', '400', "700"])
    regolith_cond_dict = load_group_temp_profiles(f"{root_filepath}/regolith_conductivity", "VarK_Conductivity", ['01', '0025', '0001'])

    fig, ax = plt.subplots(3, 3, figsize=(24,24), dpi = 500)
    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True) 
    formatter.set_powerlimits((-1,1)) 
    fig.tight_layout()

    ax[0, 0].plot(shell_thicknes_dict['d5']['temp_data'], shell_thicknes_dict['d5']['depth_data']/1e3, color='dodgerblue', label='d$_{ice}$ = 5 km', linewidth=4)
    ax[0, 0].plot(shell_thicknes_dict['d21']['temp_data'], shell_thicknes_dict['d21']['depth_data']/1e3, color='blue', label='d$_{ice}$ = 21 km',linewidth=4)
    ax[0, 0].plot(shell_thicknes_dict['d35']['temp_data'], shell_thicknes_dict['d35']['depth_data']/1e3, color='darkviolet', label='d$_{ice}$ = 35 km', linewidth=4)
    ax[0, 0].set_ylabel('Depth [km]', fontsize = 28.0) # Y label
    ax[0, 0].set_xlabel('Temperature [K]', fontsize = 28) # X label
    ax[0, 0].tick_params(axis="x", labelsize=24)
    ax[0, 0].tick_params(axis="y", labelsize=24)
    ax[0, 0].set_ylim(max(shell_thicknes_dict['d35']['depth_data']/1e3), 0)
    ax[0, 0].grid()
    ax[0, 0].legend(loc='lower left',fontsize = 28)
    ax[0, 0].set_xticklabels([])
    ax[0, 0].set_xlabel('') 
    leg = ax[0, 0].legend(loc='lower left',title='d$_{porous\; layer}$ = 250 m,\n k$_{porous\; layer}$ = 0.025 W/(mK)',fontsize = 18, title_fontsize = 18)
    leg.get_title().set_multialignment('center')

    txt_list = ['../../figures/figure1/data/temperature_profiles/ice_shell_depth/VarK_shell_depth_d5.txt','../../figures/figure1/data/temperature_profiles/ice_shell_depth/VarK_shell_depth_d21.txt','../../figures/figure1/data/temperature_profiles/ice_shell_depth/VarK_shell_depth_d35.txt']
    legend_labels = ['5 km', '21 km', '35 km']
    linewidths = [4, 7, 10]
    low_ice_df = tpu.mk_multi_attenuation_profile(txt_list, 0, 2, "low_loss", "Ice Shell Thickness", linewidths, legend_labels, ax[0, 1])
     #.apply_multi_attenuation(txt_list, "low_loss", "Regolith Conductivity Variation", "Ice Shell Depth", linestyle_list, sim_name_list, ax = ax[0,1])
    ax[0, 1].set_ylabel('')  # Empty string for the label
    ax[0, 1].grid()
    ax[0, 1].set_xlabel('', fontsize = 28) # X label
    ax[0, 1].set_xticklabels([])
    ax[0, 1].text(130, -0.35, s = 'Low Loss', fontweight = 'bold', fontsize = 35)
    ax[0, 1].set_yticklabels([])  # Empty list for tick labels

    txt_list = ["../../figures/figure1/data/temperature_profiles/ice_shell_depth/VarK_shell_depth_d5.txt", "../../figures/figure1/data/temperature_profiles/ice_shell_depth/VarK_shell_depth_d21.txt", "../../figures/figure1/data/temperature_profiles/ice_shell_depth/VarK_shell_depth_d35.txt"]
    legend_labels = ['5 km', '21 km', '35 km']
    linewidths = [4, 7, 10]
    high_ice_df = tpu.mk_multi_attenuation_profile(txt_list, 0, 2, "high_loss", "Ice Shell Thickness", linewidths, legend_labels, ax[0, 2])
    ax[0, 2].set_ylabel('')  # Empty string for the label
    ax[0, 2].grid()
    ax[0, 2].set_xlabel('', fontsize = 28) # X label
    ax[0, 2].set_xticklabels([])
    ax[0, 2].text(130, -0.35, s = 'High Loss', fontweight = 'bold', fontsize = 35)
    ax[0, 2].set_yticklabels([])  # Empty list for tick labels



    ax[1,0].plot(regolith_thickness_dict['0']['temp_data'], regolith_thickness_dict['0']['depth_data']/1e3, '--', color='black', label='d$_{porous\; layer}$ = 0 m', linewidth=4)
    ax[1,0].plot(regolith_thickness_dict['100']['temp_data'], regolith_thickness_dict['100']['depth_data']/1e3, color='dodgerblue', label='d$_{porous\; layer}$ = 100 m', linewidth=4)
    ax[1,0].plot(regolith_thickness_dict['400']['temp_data'], regolith_thickness_dict['400']['depth_data']/1e3, color='blue', label='d$_{porous\; layer}$ = 400 m',linewidth=4)
    ax[1,0].plot(regolith_thickness_dict['700']['temp_data'], regolith_thickness_dict['700']['depth_data']/1e3, color='darkviolet', label='d$_{porous\; layer}$ = 700 m', linewidth=4)
    ax[1,0].set_ylabel('Depth [km]', fontsize = 28.0) # Y label
    ax[1,0].set_xlabel('Temperature [K]', fontsize = 28) # X label
    ax[1,0].tick_params(axis="x", labelsize=24)
    ax[1,0].tick_params(axis="y", labelsize=24)
    ax[1,0].set_ylim(max(regolith_thickness_dict['700']['depth_data']/1e3), 0)
    ax[1,0].grid()
    ax[1,0].set_xticklabels([])
    ax[1,0].set_xlabel('') 
    leg = ax[1,0].legend(loc='lower left',title='d$_{ice}$ = 21 km,\n k$_{porous\; layer}$ = 0.025 W/(mK)',fontsize = 18, title_fontsize = 18)
    leg.get_title().set_multialignment('center')

    txt_list = ['../../figures/figure1/data/temperature_profiles/regolith_depth/VarK_Regolith_0.txt', '../../figures/figure1/data/temperature_profiles/regolith_depth/VarK_Regolith_100.txt', '../../figures/figure1/data/temperature_profiles/regolith_depth/VarK_Regolith_400.txt', '../../figures/figure1/data/temperature_profiles/regolith_depth/VarK_Regolith_700.txt']
    legend_labels = ['0 meters', '100 meters', '400 meters', '700 meters']
    linewidths = [3, 6, 9, 12]
    low_reg_df = tpu.mk_multi_attenuation_profile(txt_list, 0, 2, "low_loss",  "Porous Layer Thickness", linewidths, legend_labels, ax[1, 1])
    ax[1, 1].set_ylabel('')  # Empty string for the label
    ax[1, 1].grid()
    ax[1, 1].set_xlabel('', fontsize = 28) # X label
    ax[1, 1].set_yticklabels([])  # Empty list for tick labels
    ax[1, 1].set_xticklabels([])  # Empty list for tick labels

    txt_list = ['../../figures/figure1/data/temperature_profiles/regolith_depth/VarK_Regolith_0.txt', '../../figures/figure1/data/temperature_profiles/regolith_depth/VarK_Regolith_100.txt', '../../figures/figure1/data/temperature_profiles/regolith_depth/VarK_Regolith_400.txt', '../../figures/figure1/data/temperature_profiles/regolith_depth/VarK_Regolith_700.txt']
    legend_labels = ['0 meters', '100 meters', '400 meters', '700 meters']
    linewidths = [3, 6, 9, 12]
    high_reg_df = tpu.mk_multi_attenuation_profile(txt_list, 0, 2, "high_loss",  "Porous Layer Thickness", linewidths, legend_labels, ax[1, 2])
    ax[1, 2].set_ylabel('')  # Empty string for the label
    ax[1, 2].grid()
    ax[1, 2].set_xlabel('', fontsize = 28) # X label
    ax[1, 2].set_yticklabels([])  # Empty list for tick labels
    ax[1, 2].set_xticklabels([])  # Empty list for tick labels


    ax[2, 0].plot(regolith_cond_dict['01']['temp_data'], regolith_cond_dict['01']['depth_data']/1e3, color='dodgerblue', label='k$_{porous\; layer}$ = 0.1 W/(mK)', linewidth=4)
    ax[2, 0].plot(regolith_cond_dict['0025']['temp_data'], regolith_cond_dict['0025']['depth_data']/1e3, color='blue', label='k$_{porous\; layer}$ = 0.025 W/(mK)',linewidth=4)
    ax[2, 0].plot(regolith_cond_dict['0001']['temp_data'], regolith_cond_dict['0001']['depth_data']/1e3, color='darkviolet', label='k$_{porous\; layer}$ = 0.001 W/(mK)', linewidth=4)
    ax[2, 0].set_ylabel('Depth [km]', fontsize = 28.0) # Y label
    ax[2, 0].set_xlabel('Temperature [K]', fontsize = 28) # X label
    ax[2, 0].tick_params(axis="x", labelsize=24)
    ax[2, 0].tick_params(axis="y", labelsize=24)
    ax[2, 0].set_ylim(max( regolith_cond_dict['0001']['depth_data']/1e3), 0)
    ax[2, 0].grid()
    leg = ax[2,0].legend(loc='lower left',title='d$_{ice}$ = 21 km,\n d$_{porous\; layer}$ = 250 m',fontsize = 18, title_fontsize = 18)
    leg.get_title().set_multialignment('center')

    txt_list = ['../../figures/figure1/data/temperature_profiles/regolith_conductivity/VarK_Conductivity_0001.txt', '../../figures/figure1/data/temperature_profiles/regolith_conductivity/VarK_Conductivity_0025.txt', '../../figures/figure1/data/temperature_profiles/regolith_conductivity/VarK_Conductivity_01.txt']
    legend_labels = ['0.001 W/(mK)', '0.025 W/(mK)', '0.1 W/(mK)']
    linewidths = [5, 7.5, 10]
    low_cond_df = tpu.mk_multi_attenuation_profile(txt_list, 0, 2, "low_loss",  "Porous Layer Conductivity", linewidths, legend_labels, ax[2, 1])
    ax[2, 1].set_ylabel('')  # Empty string for the label
    ax[2, 1].set_yticklabels([])  # Empty list for tick labels
    ax[2, 1].grid()
    ax[2, 1].set_xlabel('Temperature [K]', fontsize = 28) # X label

    txt_list = ['../../figures/figure1/data/temperature_profiles/regolith_conductivity/VarK_Conductivity_0001.txt', '../../figures/figure1/data/temperature_profiles/regolith_conductivity/VarK_Conductivity_0025.txt', '../../figures/figure1/data/temperature_profiles/regolith_conductivity/VarK_Conductivity_01.txt']
    legend_labels = ['0.001 W/(mK)', '0.025 W/(mK)', '0.1 W/(mK)']
    linewidths = [5, 7.5, 10]
    high_cond_df = tpu.mk_multi_attenuation_profile(txt_list, 0, 2, "high_loss",  "Porous Layer Conductivity", linewidths, legend_labels, ax[2, 2])
    ax[2, 2].set_ylabel('')  # Empty string for the label
    ax[2, 2].set_yticklabels([])  # Empty list for tick labels
    ax[2, 2].grid()
    ax[2, 2].set_xlabel('Temperature [K]', fontsize = 28) # X label

    label_list = ["a)", "d)", "g)", "b)", "e)", "h)", "c)",  "f)", "i)"]

    for label, ax in zip(label_list, ax.flatten()):
        # label physical distance in and down:
        trans = mtransforms.ScaledTranslation(10/72, -5/72, fig.dpi_scale_trans)
        ax.text(0.02, 0.98, label, transform=ax.transAxes + trans,
                fontsize= 24+6, verticalalignment='top', fontfamily='serif',
                bbox=dict(facecolor='none', edgecolor = "none", pad=3.0))
    
    # for ax in fig.get_axes():  # Loop through all axes in the figure
    #     legend = ax.get_legend()
    #     frame = legend.get_frame()
    #     frame.set_alpha(0.3)

    plt.savefig("../../figures/figure1/image(s)/fig1.png", format = "png", bbox_inches='tight')
    plt.show()

    stats_df = pd.concat([tpu.calc_multiplot_stats(low_ice_df, 'low_loss'), 
                          tpu.calc_multiplot_stats(high_ice_df, 'high_loss'), 
                          tpu.calc_multiplot_stats(low_reg_df, 'low_loss'), 
                          tpu.calc_multiplot_stats(high_reg_df, 'high_loss'), 
                          tpu.calc_multiplot_stats(low_cond_df, 'low_loss'),
                          tpu.calc_multiplot_stats(high_cond_df, 'high_loss')])
    
    return stats_df


def create_fig2_data():
    print("creating data for Figure 2")

    sim = {"Ro":252.1e3,
    "d_ocean":37e3, 
    "d_ice": 5e3, # ice thickness in m
    "Ts": 60, # surface temperature in K
    "resolution": 10, # model resolution in m
    "density_ice": 925, # kg/m3
    "density_water": 1050, # kg/m3
    "density_silicate": 2400, # kg/m3
    "klayer1"     : 0.025,
    "klayer1_str" : "0025",
    "k0": 651}
    sim["klayer2"] = 651/cpe.calc_TempIceOcean(sim["density_ice"], sim["d_ice"], sim["Ro"])
    fig2_savepath = "../../figures/figure2/data/"



    regolith_list = [0, 100, 250, 400, 700]
    klayer1_list = [0.1, 0.025, 0.001]
    d_ice_list = [5e3, 21e3, 35e3]

    all_combinations = list(itertools.product(regolith_list, klayer1_list, d_ice_list))
    
    steps = 0

    print("Combos in the form (regolith_thickness, regolith_conductivity, ice_shell_thickness)")
    for sim_combo in all_combinations:
        sim['Rinterface'] = sim['Ro'] - sim_combo[0]
        sim['klayer1'] = sim_combo[1]
        sim['klayer1_str'] = str(sim_combo[1]).replace(".", "")
        sim['d_ice'] = sim_combo[2]
        if sim_combo[2] == 5e3:
            steps = 10
        else:
            steps = 100

        temp_profile,depth_profile = cpe.calc_ConductiveTempProfileVarkT(sim['klayer1'], sim['k0'], sim['Rinterface'], sim['density_ice'], sim['d_ice'], sim['Ro'], sim['Ts'], sim['resolution'], steps)


        filename = f"Regolith_{sim_combo[0]}_icedepth_{int(sim['d_ice']/1000)}_conduct_{sim['klayer1_str']}.txt"
        conductivity_model  = 'k_regolith = ' +  str(sim['klayer1']) + ' W/(mK), k_ice = ' + str(sim['klayer2']) + ' W/(mK), regolith thickness = ' + str(sim_combo[0]) + ' m'

        cpe.write_data(fig2_savepath+"temperature_profiles_Ts_60/"+filename, sim['Ro'], temp_profile, depth_profile, sim['d_ice'], conductivity_model)
        print(f"Finished temp profile combos {all_combinations.index(sim_combo)+1}: {sim_combo} of {len(all_combinations)}!")

    print('starting heatmap data generation')
    atten_models = ['low_loss', 'high_loss']
    ice_shell_thicknesses = [5, 21, 35]

    for atten_model, ice_shell_thickness in list(itertools.product(atten_models, ice_shell_thicknesses)):
        print(f"Generating heatmap with attenuation mode {atten_model} and ice shell thickness {ice_shell_thickness}...")
        heat_df = hu.mk_heatmap(ice_shell_thickness,0, 2, atten_model, fig2_savepath+"temperature_profiles_Ts_60/", save = True, savepath = fig2_savepath+"attenuation_calculations/")

    print('Done!')

    return 

def plot_fig2():
    fig, ax = plt.subplots(3,2, figsize = (10,12), dpi = 500)
    fig.tight_layout()
    label_fontsize = 14
    tick_fontsize = label_fontsize - 3
    annot = True
    vmax = 105
    vmin = 0
    fmt = ".3g"
    atten_limit = 100
    cmap = hu.custom_cmap()
    temp_profiles_path = "../../figures/figure2/data/temperature_profiles_Ts_60/"
    savepath  = '../../figures/figure2/data/attenuation_calculations/'
    save = False

    heat_df_5_low = hu.mk_heatmap(5, 0, 2, "low_loss", temp_profiles_path, atten_limit, save, savepath)
    sns.heatmap(heat_df_5_low, cmap = cmap, ax = ax[0,0],vmax = vmax, vmin = vmin, annot = annot, lw = 0.5, linecolor= "black", fmt = fmt)
    hu.heatmap_formatting(ax[0,0], y_ticks = True)
    ax[0, 0].text(1.1, -.1, s = 'Low Loss', fontweight = 'bold', fontsize = label_fontsize+1)
    ax[0, 0].text(-0.6, 2.8, s = '5 km', fontweight = 'bold', fontsize = label_fontsize+1, rotation = 90)
    heat_df_5_high = hu.mk_heatmap(5, 0, 2, "high_loss", temp_profiles_path, atten_limit, save, savepath)
    sns.heatmap(heat_df_5_high, cmap = cmap, ax = ax[0,1],vmax = vmax, vmin = vmin, annot = annot, lw = 0.5, linecolor= "black", fmt = fmt)
    hu.heatmap_formatting(ax[0,1])
    ax[0, 1].text(1, -0.1, s = 'High Loss', fontweight = 'bold', fontsize = label_fontsize+1)



    heat_df_21_low = hu.mk_heatmap(21, 0, 2, "low_loss", temp_profiles_path, atten_limit, save, savepath)
    sns.heatmap(heat_df_21_low, cmap = cmap, ax = ax[1,0],vmax = vmax, vmin = vmin, annot = annot, lw = 0.5, linecolor= "black", fmt = fmt)
    hu.heatmap_formatting(ax[1,0], y_ticks=True)
    ax[1, 0].text(-0.6, 2.9, s = '21 km', fontweight = 'bold', fontsize = label_fontsize+1, rotation = 90)
    heat_df_21_high = hu.mk_heatmap(21, 0, 2, "high_loss", temp_profiles_path, atten_limit, save, savepath)
    sns.heatmap(heat_df_21_high, cmap = cmap, ax = ax[1,1],vmax = vmax, vmin = vmin, annot = annot, lw = 0.5, linecolor= "black", fmt = fmt)
    hu.heatmap_formatting(ax[1,1])



    heat_df_35_low = hu.mk_heatmap(35, 0, 2, "low_loss", temp_profiles_path, atten_limit, save, savepath)
    sns.heatmap(heat_df_35_low, cmap = cmap, ax = ax[2,0],vmax = vmax, vmin = vmin, annot = annot, lw = 0.5, linecolor= "black", fmt = fmt)
    hu.heatmap_formatting(ax[2,0], y_ticks=True, x_ticks=True)
    ax[2, 0].text(-0.6, 2.9, s = '35 km', fontweight = 'bold', fontsize = label_fontsize+1, rotation = 90)
    heat_df_35_high = hu.mk_heatmap(35, 0, 2, "high_loss", temp_profiles_path, atten_limit, save, savepath)
    sns.heatmap(heat_df_35_high, cmap = cmap, ax = ax[2,1],vmax = vmax, vmin = vmin, annot = annot, lw = 0.5, linecolor= "black", fmt = fmt)
    hu.heatmap_formatting(ax[2,1], x_ticks=True)



    hu.mk_custom_cbar([.045,-0.06,.93, .035], fig, "Relative Pen. Depth [%]", [0, 20, 40, 60, 80, 100])

    label_list  = ["a)", "d)", "b)", "e)", "c)", "f)"]
    for label, ax in zip(label_list, ax.flatten()):
        if label in ("d)", "e)", "f)"):
            color = "white"     
        else: 
            color = "black"

        trans = mtransforms.ScaledTranslation(10/72, -5/72, fig.dpi_scale_trans)
        ax.text(0.02, 0.98, label, transform=ax.transAxes + trans,
                fontsize= 12, verticalalignment='top', fontfamily='serif', color = color,
                bbox=dict(facecolor='none', edgecolor = "none", pad=3.0))
    plt.savefig("../../figures/figure2/image(s)/fig2.png", format = "png", bbox_inches='tight')
    plt.show()


    stats_df = pd.concat([hu.calc_heatmap_stats(heat_df_5_low, 5, 'low_loss'), 
                          hu.calc_heatmap_stats(heat_df_5_high, 5, 'high_loss'), 
                          hu.calc_heatmap_stats(heat_df_21_low, 21, 'low_loss'), 
                          hu.calc_heatmap_stats(heat_df_21_high, 21, 'high_loss'), 
                          hu.calc_heatmap_stats(heat_df_35_low, 35, 'low_loss'), 
                          hu.calc_heatmap_stats(heat_df_35_high, 35, 'high_loss')])


    return stats_df


def create_fig3_data():
    print("creating data for Figure 3")

    fig3_savepath = "../../figures/figure3/data/attenuation_calculations_maps/"

    regolith_map_dict = dmu.create_regolith_maps()
    shell_thickness_map = np.loadtxt("../../figures/figure3/data/ice_shell_depth_maps/Hemingway_depth_map_a.csv", delimiter= ',')
    
    regolith_map_list = ['no', 'bc', 'exp']
    attenuation_model = ['low_loss', 'high_loss']

    for reg_map_key, atten_model in list(itertools.product(regolith_map_list, attenuation_model)):
        print(f"creating a relative depth penetration map from regolith map {reg_map_key} and attenuation model {atten_model}...")
        depth_to_100db_map = dmu.create_attuenation_map_data(shell_thickness_map, regolith_map_dict[reg_map_key], 2, atten_model, datatype = 'depth')
        relative_depth_pen = dmu.create_depth_pen(depth_to_100db_map, shell_thickness_map)
        
        dmu.write_map(fig3_savepath+atten_model+"/", relative_depth_pen, "hemingway_map_a", reg_map_key, atten_model, "relative")


    print("Done!")

def plot_fig3():

    hemingway_a_depth_map = np.loadtxt("../../figures/figure3/data/ice_shell_depth_maps/Hemingway_depth_map_a.csv", delimiter= ',')
    regolith_depth_dict = dmu.create_regolith_maps()
    #low loss maps
    filepath = "../../figures/figure3/data/attenuation_calculations_maps/low_loss/hemingway_map_A_bc_relative_low_loss.csv"
    hemingway_low_a_bc_reg_depthpen =  np.loadtxt(filepath, delimiter= ",")
    filepath = "../../figures/figure3/data/attenuation_calculations_maps/low_loss/hemingway_map_A_exp_relative_low_loss.csv"
    hemingway_low_a_exp_reg_depthpen = np.loadtxt(filepath, delimiter= ",")
    filepath = "../../figures/figure3/data/attenuation_calculations_maps/low_loss/hemingway_map_A_no_relative_low_loss.csv"
    hemingway_low_a_no_reg_depthpen =  np.loadtxt(filepath, delimiter= ",")
    # high loss maps
    filepath = "../../figures/figure3/data/attenuation_calculations_maps/high_loss/hemingway_map_A_bc_relative_high_loss.csv"
    hemingway_high_a_bc_reg_depthpen = np.loadtxt(filepath, delimiter= ",")
    filepath = "../../figures/figure3/data/attenuation_calculations_maps/high_loss/hemingway_map_A_exp_relative_high_loss.csv"
    hemingway_high_a_exp_reg_depthpen = np.loadtxt(filepath, delimiter= ",")
    filepath = "../../figures/figure3/data/attenuation_calculations_maps/high_loss/hemingway_map_A_no_relative_high_loss.csv"
    hemingway_high_a_no_reg_depthpen = np.loadtxt(filepath, delimiter= ",")

    x, y = dmu.create_coords(181, 361)
    fig, ax = plt.subplots(3, 3, figsize = (39, 15), dpi = 500)
    label_fontsize = 24
    tick_fontsize = label_fontsize - 4
    x_label = 'Longitude [deg]'
    y_label = 'Latitude [deg]'
    limit = 100
    calc_layer_num = 100
    rocket_colors = sns.color_palette('rocket', 99) + [(0.9955451416666666, 0.97512059, 0.960499675)]
    rocket_cmap = ListedColormap(sns.color_palette(rocket_colors, as_cmap=True))


    dmu.mk_depth_map(hemingway_a_depth_map/1000, x, y, "cividis", 'Ice Shell Depth [km]', 7, fig, label_fontsize, ax = ax[0, 0], depth_map_limit = np.array(hemingway_a_depth_map/1000).max())
    dmu.depth_map_formatting(ax[0, 0], y_ticks=True, label_fontsize = label_fontsize)
    cbar = dmu.mk_depth_map(hemingway_low_a_no_reg_depthpen, x, y, rocket_cmap, '2-Way Attenuation [dB]', calc_layer_num, fig, label_fontsize, ax = ax[0, 1],  atten_limit = limit)
    dmu.depth_map_formatting(ax[0, 1], cbar, label_fontsize = label_fontsize)
    cbar = dmu.mk_depth_map(hemingway_high_a_no_reg_depthpen, x, y, rocket_cmap, '2-Way Attenuation [dB]', calc_layer_num, fig, label_fontsize, ax = ax[0, 2], atten_limit = limit)
    dmu.depth_map_formatting(ax[0, 2], cbar, label_fontsize = label_fontsize)

    ax[0, 1].text(-40, 95, s = 'Low Loss', fontweight = 'bold', fontsize = label_fontsize+10)
    ax[0, 2].text(-40, 95, s = 'High Loss', fontweight = 'bold', fontsize = label_fontsize+10)

    ax[0, 0].text(-250-15, -68-10, s = "No Porous Layer", fontweight = 'bold', fontsize = label_fontsize+5, rotation = 90)
    ax[1, 0].text(-250-15, -40-10, s = "Exp-Global", fontweight = 'bold', fontsize = label_fontsize+5, rotation = 90)
    ax[2, 0].text(-250-15, -68-10, s = "Exp-Hemispheric", fontweight = 'bold', fontsize = label_fontsize+5, rotation = 90)

    cbar = dmu.mk_depth_map(regolith_depth_dict['exp']/1000, x, y, "cividis", 'Regolith Depth [km]', 20, fig, label_fontsize, ax = ax[1, 0], depth_map_limit = np.array(regolith_depth_dict['exp']/1000).max())
    dmu.depth_map_formatting(ax[1, 0], cbar, y_ticks=True, label_fontsize = label_fontsize)
    cbar = dmu.mk_depth_map(hemingway_low_a_exp_reg_depthpen, x, y, rocket_cmap, '2-Way Attenuation [dB]', calc_layer_num, fig, label_fontsize, ax = ax[1, 1], atten_limit = limit)
    dmu.depth_map_formatting(ax[1, 1], cbar, label_fontsize = label_fontsize)
    cbar = dmu.mk_depth_map(hemingway_high_a_exp_reg_depthpen, x, y, rocket_cmap, '2-Way Attenuation [dB]', calc_layer_num, fig, label_fontsize, ax = ax[1, 2], atten_limit = limit)
    dmu.depth_map_formatting(ax[1, 2], cbar, label_fontsize = label_fontsize)

    
    cbar = dmu.mk_depth_map(regolith_depth_dict['bc']/1000, x, y, "cividis", 'Regolith Depth [km]', 20, fig, label_fontsize, ax = ax[2, 0], depth_map_limit = 0.5)
    dmu.depth_map_formatting(ax[2, 0], cbar, y_ticks = True, x_ticks= True, label_fontsize = label_fontsize)
    cbar = dmu.mk_depth_map(hemingway_low_a_bc_reg_depthpen, x, y, rocket_cmap, '2-Way Attenuation [dB]', calc_layer_num, fig, label_fontsize,ax = ax[2, 1], atten_limit = limit)
    dmu.depth_map_formatting(ax[2, 1], cbar, x_ticks= True, label_fontsize = label_fontsize)
    cbar = dmu.mk_depth_map(hemingway_high_a_bc_reg_depthpen, x, y, rocket_cmap, '2-Way Attenuation [dB]', calc_layer_num, fig, label_fontsize,ax = ax[2, 2], atten_limit = limit)
    dmu.depth_map_formatting(ax[2, 2], cbar, x_ticks= True, label_fontsize = label_fontsize)

    # Colorbar for both exponential and best case regolith distributions
    norm = plt.Normalize(0, 700)
    cmap = plt.get_cmap('cividis', 20)
    sm = plt.cm.ScalarMappable(cmap= cmap, norm=norm)
    sm.set_array([])
    cbar_ax = [0.326, 0.1, .0055, .525]
    cbar_ax = fig.add_axes(cbar_ax)
    cb = fig.colorbar(sm, orientation="vertical", pad=0.02, shrink=0.8, cax = cbar_ax)
    cb.set_label("Porous Layer Thickness [m]", fontsize = label_fontsize - 3)
    cb.set_ticklabels([0, 100, 200, 300, 400, 500, 600, 700], fontsize = tick_fontsize)


    cbar_ax = [0.595, 0.1, .006, .8]
    dmu.mk_custom_cbar(cbar_ax, fig, label_fontsize = label_fontsize)
    cbar_ax = [0.86, 0.1, .006, .8]
    dmu.mk_custom_cbar(cbar_ax, fig, label_fontsize = label_fontsize)


    # plt.tight_layout()
    plt.subplots_adjust(left= 0.1,
                        bottom = 0.1, 
                        right = 0.9, 
                        top = 0.9, 
                        wspace = 0, 
                        hspace=0.1)

    label_list = ["a)", "d)", "g)", "b)", "e)", "h)", "c)",  "f)", "i)"]
    for label, ax in zip(label_list, ax.flatten()):
        if label in ("a)", "b)", "c)"):
            color = "white"
        else:
            color = "black"
        trans = mtransforms.ScaledTranslation(10/72, -5/72, fig.dpi_scale_trans)
        ax.text(0.02, 0.98, label, transform=ax.transAxes + trans,
                fontsize= label_fontsize+6, verticalalignment='top', fontfamily='serif', color = color,
                bbox=dict(facecolor='none', edgecolor = "none", pad=3.0))
    
    plt.savefig("../../figures/figure3/image(s)/fig3.png",format = "png", bbox_inches='tight')
    plt.show()

    stats_df = pd.concat([ dmu.calc_depth_map_stats(hemingway_low_a_no_reg_depthpen, 'hemingway_map_a', 'no_regolith', 'low_loss'), 
    dmu.calc_depth_map_stats(hemingway_high_a_no_reg_depthpen, 'hemingway_map_a', 'no_regolith', 'high_loss'), 
    dmu.calc_depth_map_stats(hemingway_low_a_exp_reg_depthpen, 'hemingway_map_a', 'exponential_regolith', 'low_loss'), 
     dmu.calc_depth_map_stats(hemingway_high_a_exp_reg_depthpen, 'hemingway_map_a', 'exponential_regolith', 'high_loss'), 
    dmu.calc_depth_map_stats(hemingway_low_a_bc_reg_depthpen, 'hemingway_map_a', 'bestcase_regolith', 'low_loss'), 
    dmu.calc_depth_map_stats(hemingway_high_a_bc_reg_depthpen, 'hemingway_map_a', 'bestcase_regolith', 'high_loss')])
    stats_df.set_index(['icesehll_map', 'regolith_distribution', 'attenuation_model'], inplace = True)

    return stats_df


def create_fig4_data():
    print("creating data for Figure 4")
    folderpath = "../../figures/figure4/data/attenuation_calculations_map_a/"
    hemingway_map_a = np.loadtxt("../../figures/figure4/data/ice_shell_depth_maps/Hemingway_depth_map_a.csv", delimiter= ',')


    atten_models = ['low_loss', 'high_loss']
    eutectic_atten_list = ['eutectic_NH4CL_attenuation', 'eutectic_NH3_attenuation']
    reg_dict = dmu.create_regolith_maps()

    print("Making depth maps at each eutectic...")
    # creating the first column in figure 4. 
    # Note that because we are getting the depth to a eutectic, attenuation model does not matter (high_loss or low_loss)
    eutectic_atten_map = dmu.create_attuenation_map_data(hemingway_map_a, reg_dict['bc'], 2, "low_loss", "eutectic_NH4CL_depth")
    dmu.write_map(folderpath, eutectic_atten_map, "nh4cl_eutectic_depth", 'bc', "no_loss", "eutectic_NH4CL_depth")
    eutectic_atten_map = dmu.create_attuenation_map_data(hemingway_map_a, reg_dict['bc'], 2, "low_loss", "eutectic_NH3_depth")
    dmu.write_map(folderpath, eutectic_atten_map, "nh3_eutectic_depth", 'bc', "no_loss", "eutectic_NH3_depth")

    # making the attenuation maps, or coloumns 2 and 3, for figure 4
    for atten_type, atten_model in itertools.product(eutectic_atten_list, atten_models):
        print(f"Making {atten_type} with attenuation model {atten_model}...")

        eutectic_atten_map = dmu.create_attuenation_map_data(hemingway_map_a, reg_dict['bc'], 0.5, atten_model, atten_type)
        dmu.write_map(folderpath, eutectic_atten_map, atten_type, 'bc', atten_model, atten_type)
    
    print('Done!')
    return

def plot_fig4():
    filepath = "../../figures/figure4/data/attenuation_calculations_map_a/"

    nh4cl_depth = np.loadtxt(filepath+"nh4cl_eutectic_depth_bc_eutectic_NH4CL_depth_no_loss.csv", delimiter= ",")/1000
    nh3_depth   = np.loadtxt(filepath+"nh3_eutectic_depth_bc_eutectic_NH3_depth_no_loss.csv", delimiter= ",")/1000

    nh4cl_low =   np.loadtxt(filepath+"eutectic_NH4CL_attenuation_bc_eutectic_NH4CL_attenuation_low_loss.csv", delimiter= ",")
    nh4cl_high =  np.loadtxt(filepath+"eutectic_NH4CL_attenuation_bc_eutectic_NH4CL_attenuation_high_loss.csv", delimiter= ",")

    nh3_low =     np.loadtxt(filepath+"eutectic_NH3_attenuation_bc_eutectic_NH3_attenuation_low_loss.csv", delimiter= ",")
    nh3_high =    np.loadtxt(filepath+"eutectic_NH3_attenuation_bc_eutectic_NH3_attenuation_high_loss.csv", delimiter= ",")

    x, y = dmu.create_coords(181, 361)
    rocket_colors = sns.color_palette('rocket', 99) + [(0.9955451416666666, 0.97512059, 0.960499675)]
    rocket_cmap = ListedColormap(sns.color_palette(rocket_colors, as_cmap=True))
    fig, ax = plt.subplots(2, 3, figsize = (39, 10), dpi = 500) # 39, 10
    label_fontsize = 24
    tick_fontsize = label_fontsize - 4
    limit = 100

    cbar = dmu.mk_depth_map(nh3_depth, x, y, "cividis", 'Depth to Eutectic [km]', 7 , fig,label_fontsize, ax[0, 0], depth_map_limit = np.max(nh4cl_depth))
    dmu.depth_map_formatting(ax[0, 0], cbar, y_ticks=True, label_fontsize = label_fontsize)
    cbar = dmu.mk_depth_map(nh4cl_depth, x, y, "cividis", 'Depth to Eutectic [km]', 7 , fig,label_fontsize, ax[1, 0], depth_map_limit = np.max(nh4cl_depth))
    dmu.depth_map_formatting(ax[1, 0], cbar, y_ticks=True, x_ticks=True, label_fontsize = label_fontsize)


    cbar = dmu.mk_depth_map(nh3_low, x, y, rocket_cmap, 'Two-Way Attenuation [dB]', 100 , fig,label_fontsize, ax[0, 1], np.max(nh3_high))
    dmu.depth_map_formatting(ax[0, 1], cbar, label_fontsize = label_fontsize)
    cbar = dmu.mk_depth_map(nh4cl_low, x, y, rocket_cmap, 'Two-Way Attenuation [dB]', 100 , fig,label_fontsize, ax[1, 1], limit)
    dmu.depth_map_formatting(ax[1, 1], cbar, x_ticks=True, label_fontsize = label_fontsize)

    cbar = dmu.mk_depth_map(nh3_high, x, y, rocket_cmap, 'Two-Way Attenuation [dB]', 100 , fig,label_fontsize, ax[0, 2],  np.max(nh3_high))
    dmu.depth_map_formatting(ax[0, 2], cbar, label_fontsize = label_fontsize)
    cbar = dmu.mk_depth_map(nh4cl_high, x, y, rocket_cmap, 'Two-Way Attenuation [dB]', 100 , fig,label_fontsize, ax[1, 2], limit)
    dmu.depth_map_formatting(ax[1, 2], cbar, x_ticks=True, label_fontsize = label_fontsize)


    # cbar_ax = [0.849, 0.1, .008, .38]
    # dmu.mk_custom_cbar(cbar_ax, fig, 'Two-Way Attenuation [dB]', 18)

    ax[0, 1].text(-40, 95, s = 'Low Loss', fontweight = 'bold', fontsize = label_fontsize+7)
    ax[0, 2].text(-40, 95, s = 'High Loss', fontweight = 'bold', fontsize = label_fontsize+7)
    ax[0, 0].text(-245-12, -53-8, s = 'NH3 Eutectic', fontweight = 'bold', fontsize = label_fontsize+6, rotation = 90)
    ax[1, 0].text(-245-12, -65-8, s = 'NH4Cl Eutectic', fontweight = 'bold', fontsize = label_fontsize+6, rotation = 90)



    cbar_ax = [0.329, 0.1, .006, .80]
    norm = plt.Normalize(0, np.max(nh4cl_depth))
    rocket_colors = sns.color_palette('cividis', 7)
    cmap = ListedColormap(sns.color_palette(rocket_colors, as_cmap=True))
    sm = plt.cm.ScalarMappable(cmap= cmap, norm=norm)
    sm.set_array([])
    cbar_ax = fig.add_axes(cbar_ax)
    cb = fig.colorbar(sm, orientation="vertical", pad=0.02, shrink=0.8, cax = cbar_ax)
    cb.set_label("Depth to Eutectic [km]", fontsize = label_fontsize - 2)
    cb.ax.tick_params(labelsize=tick_fontsize)

    cbar_ax = [0.849, 0.1, .008, .38]
    norm = Normalize(vmin = 0, vmax = 100)
    rocket_colors = sns.color_palette('rocket', 39) + [(0.9955451416666666, 0.97512059, 0.960499675)]
    rocket_cmap = ListedColormap(sns.color_palette(rocket_colors, as_cmap=True))
    sm = plt.cm.ScalarMappable(cmap= rocket_cmap, norm=norm)
    sm.set_array([])
    cbar_ax = fig.add_axes(cbar_ax)
    cb = fig.colorbar(sm, orientation="vertical", pad=0.02, shrink=0.8, cax = cbar_ax)
    cb.set_label("Two-way Attenuation [dB]", fontsize = label_fontsize - 2)
    cb.ax.tick_params(labelsize=tick_fontsize)

    cbar_ax = [0.849, 0.52, .008, .38]
    norm = Normalize(vmin = 0, vmax =  np.max(nh3_high))
    rocket_colors = sns.color_palette('rocket', 40)
    rocket_cmap = ListedColormap(sns.color_palette(rocket_colors, as_cmap=True))
    sm = plt.cm.ScalarMappable(cmap= rocket_cmap, norm=norm)
    sm.set_array([])
    cbar_ax = fig.add_axes(cbar_ax)
    cb = fig.colorbar(sm, orientation="vertical", pad=0.02, shrink=0.8, cax = cbar_ax)
    cb.set_label("Two-way Attenuation [dB]", fontsize = label_fontsize - 2)
    cb.ax.tick_params(labelsize=tick_fontsize)



    plt.subplots_adjust(left= 0.1,
                        bottom = 0.1, 
                        right = 0.9, 
                        top = 0.9, 
                        wspace = -0.07, # -0.10
                        hspace=0.1)

    label_list  = ["a)", "c)", "e)", "b)", "d)", "f)"]
    for label, ax in zip(label_list, ax.flatten()):
        if label in ("a)", "b)", "c)", "d)", "e)"):
            color = "white"     
        else: 
            color = "black"
        trans = mtransforms.ScaledTranslation(10/72, -5/72, fig.dpi_scale_trans)
        ax.text(0.02, 0.98, label, transform=ax.transAxes + trans,
                fontsize= label_fontsize+6, verticalalignment='top', fontfamily='serif', color = color,
                bbox=dict(facecolor='none', edgecolor = "none", pad=3.0))
    
    plt.savefig("../../figures/figure4/image(s)/fig4.png", format = "png", bbox_inches='tight')
    plt.show()
    
    stats_df = pd.concat([dmu.calc_depth_map_stats(nh3_low, 'hemingway_map_a', 'bestcase_regolith', 'low_loss_nh3_eutectic'), 
                          dmu.calc_depth_map_stats(nh3_high, 'hemingway_map_a', 'bestcase_regolith', 'high_loss_nh3_eutectic'), 
                          dmu.calc_depth_map_stats(nh4cl_low, 'hemingway_map_a', 'bestcase_regolith', 'low_loss_nh4cl_eutectic'),
                          dmu.calc_depth_map_stats(nh4cl_high, 'hemingway_map_a', 'bestcase_regolith', 'high_loss_nh4cl_eutectic')])
    stats_df.set_index(['icesehll_map', 'regolith_distribution', 'attenuation_model'], inplace = True)

    return stats_df
    
    

if __name__ == '__main__':
    input = input("""What figure would you like to plot?\n
                  fig1, fig2, fig3, or fig4?""")
    
    if input == 'fig1':
        plot_fig1()
    elif input == 'fig2':
        plot_fig2()
    elif input == 'fig3':
        plot_fig3()
    elif input == 'fig4':
        plot_fig4()
    else:
        print("please only input `figx` where x is 1, 2, 3, or 4")





