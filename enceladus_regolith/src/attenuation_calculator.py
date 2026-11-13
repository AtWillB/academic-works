# attenuation_calculator.py was written by William Byrne in the Fall of 2023
# To be used by DLR - Institute of Planetary Research
# Attenuaiton calculations based on Kalousova et al. 2017.
# Attenuation models based on Souckek et al. 2023

import math
import numpy as np
import pandas as pd
import pdb


def calc_electrical_conductivity(temp, cl_conc):
    """
    calc_electrical_conductivity calculates the eletrical conductivity for ice at a given temeprature with a given concentration of cloride

    param temp: temperature at a given layer (in kelvin)
    param cl_conc: concentration of cloride at a given layer (in micromoles)
    """
    Kb = 8.617*(10**-5)     # boltzman constant(eV K^−1)
    Tr = 251                #refrence temperature

    𝜎0 = 7.2                # electrical conductivity of pure ice
    C0 = 1                  # Auxiliary constant
    E0 = 0.55               # Activation energy of pure ice

    𝜎1 = 0.43               # Molar electrical conductivity of Cloride
    E1 = 0.19               # Activation energy of Cloride


    i1 =(𝜎0*C0*np.exp((-(E0)/(Kb)*((1/temp) - (1/Tr))))) # pure ice
    i2 = (𝜎1*cl_conc*np.exp((-(E1)/(Kb)*((1/temp) - (1/Tr))))) # cloride
    return i1+i2



# def andi_calc_twoway_attenuation(depth_array, temp_array, attenuation_model):
#     """
#     calc_twoway_attenuation creates a dictionary containing the depth, temperature, and attenuation value at every layer of a 1-D temperature profile
#     The attenuation values are calculated using one of theree attenuation models. 
#     Attenuaiton models are based on material assumtptions of ice shell that impact electrical conductivity. Called from calc_electrical_conductivity

#     param depth_array: numpy array containing the depth values at each layer (in meters)
#     param temp_array: numpy array containing the temperature values at each layer (in kelvin)
#     param attenuation_model: categorical variable(Either "high_loss", "mid_loss", or "low_loss") that determines which model to use for 2-way attenuation calculation
#     return: dictionary contaning depth, temperature, and attenuation values
#     """

#     # sort depth/temp arrays in ascending order, so layer 0 is the surface layer
#     # Assume that the surface layer has depth of 0.0 meters
#     if depth_array[0] != 0.0:
#         depth_array = np.flip(depth_array)
#         temp_array = np.flip(temp_array)

#     thickness = abs(np.diff(depth_array))
#     thickness = np.append(thickness, abs(depth_array[-1]-depth_array[-2]))

#     if not isinstance(attenuation_model, list):
#         attenuation_model_array = [attenuation_model] * len(depth_array)


#     if attenuation_model == "low_loss":
#         attRate = 2*(0.914*calc_electrical_conductivity(temp_array, 0))*(thickness/1000)#    summand = 2*(0.914*calc_electrical_conductivity(layer['temp'], 0))*(layer['thickness']/1000)
#     elif attenuation_model == "mid_loss":
#         attRate = 2*(0.914*calc_electrical_conductivity(temp_array, 150))*(thickness/1000)#    summand = 2*(0.914*calc_electrical_conductivity(layer['temp'], 150))*(layer['thickness']/1000) 
#     elif attenuation_model == "high_loss":
#         attRate = 2*(0.914*calc_electrical_conductivity(temp_array, 300))*(thickness/1000)#    summand = 2*(0.914*calc_electrical_conductivity(layer['temp'], 300))*(layer['thickness']/1000)
#     else:
#         raise Exception(f"The attenuation model {attenuation_model} is not supported. Please use one of the following: ['low_loss', 'mid_loss', 'high_loss']")

#     two_way_att = np.zeros(len(depth_array))
#     for ii in range(len(thickness)-1):
#         two_way_att[ii+1] = np.sum(attRate[:ii+2])


#     layers_dict = {
#         'layerNum':np.arange(len(depth_array))+1,
#         'depth':depth_array,
#         'thickness':thickness,
#         'temp':temp_array,
#         'attenuation_model':attenuation_model_array,
#         'twoway_loss':two_way_att}

#     return layers_dict


def calc_twoway_attenuation(depth_array, temp_array, attenuation_model):
    """
    calc_twoway_attenuation creates a dictionary containing the depth, temperature, and attenuation value at every layer of a 1-D temperature profile
    The attenuation values are calculated using one of theree attenuation models. 
    Attenuaiton models are based on material assumtptions of ice shell that impact electrical conductivity. Called from calc_electrical_conductivity

    param depth_array: numpy array containing the depth values at each layer (in meters)
    param temp_array: numpy array containing the temperature values at each layer (in kelvin)
    param attenuation_model: categorical variable(Either "high_loss", "mid_loss", or "low_loss") that determines which model to use for 2-way attenuation calculation
    return: dictionary contaning depth, temperature, and attenuation values
    """

    # sort depth/temp arrays in ascending order, so layer 0 is the surface layer
    # Assume that the surface layer has depth of 0.0 meters
    if depth_array[0] != 0.0:
        depth_array = np.flip(depth_array)
        temp_array = np.flip(temp_array)

    depth_array = list(depth_array)
    temp_array = list(temp_array)


    # columns 
    layer_array = list(range(1, len(depth_array) + 1))
    thickness_array = [abs(depth_array[i] - depth_array[i-1]) for i in range(1, len(depth_array))]
    thickness_array.append(abs(depth_array[-2] - depth_array[-1]))

    if not isinstance(attenuation_model, list):
        attenuation_model_array = [attenuation_model] * len(depth_array)
    
    attenuation_array = []
    for layer_num, attenuation_model in zip(layer_array, attenuation_model_array):
        index = layer_num - 1

        # One-way attenuation calculation has layer thickness in kilometers
        if attenuation_model == "low_loss":
            summand = 2 * (0.914 * calc_electrical_conductivity(temp_array[index], 0)) * (thickness_array[index] / 1000)
        elif attenuation_model == "mid_loss":
            summand = 2 * (0.914 * calc_electrical_conductivity(temp_array[index], 150)) * (thickness_array[index] / 1000)
        elif attenuation_model == "high_loss":
            summand = 2 * (0.914 * calc_electrical_conductivity(temp_array[index], 300)) * (thickness_array[index] / 1000)
        else:
            raise Exception(f"The attenuation model {attenuation_model} is not supported. Please use one of the following: ['low_loss', 'mid_loss', 'high_loss']")

        if attenuation_array:
            attenuation_array.append(attenuation_array[-1] + summand)
        else:
            attenuation_array.append(summand)

    layers_dict = {
            'layerNum':layer_array,
            'depth':depth_array,
            'thickness':thickness_array,
            'temp':temp_array,
            'attenuation_model':attenuation_model_array,
            'twoway_loss':attenuation_array
    }

   
    return layers_dict


def dict_to_df(layers_dict):
    """
    dict_to_df takes in the layers_dict dictionary and returns a Pandas DataFrame with the appropriate column names

    param layers_dict: python dictionary containing metadata about simulation layers and their attributes
    return: Pandas DataFrame with the appropriate column names with layer number set to index
    """

    df = pd.DataFrame(layers_dict)
    df.set_index('layerNum', inplace = True)

    return df