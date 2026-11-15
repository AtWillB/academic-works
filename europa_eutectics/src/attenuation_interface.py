from pathlib import Path

import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt


# Kalousova et al 2016, 10.1002/2016JE005110

def calc_electrical_conductivity(temp, pure_ice = True):
    """Calculate ice electrical conductivity using Kalousova et al. (2016).

    Parameters
    ----------
    temp : float or ndarray
        Temperature in kelvin.
    pure_ice : bool
        If true, use pure ice; otherwise include acid and salt contributions.

    Returns
    -------
    float or ndarray
        Electrical conductivity in microSiemens per meter.
    """
    final_cond = 0

    Kb = 8.617*(10**-5)     # boltzman constant(eV K^−1)
    Tr = 251                #refrence temperature (K)

    𝜎0 = 9.2                # μS m^-1
    C0 = 1                  # no-units
    E0 = 0.51               # eV
    
    𝜎1 = 3.2                # S m−1 M−1
    C1 = 1.2                # μM
    E1 = 0.20               # eV

    𝜎2 = 0.43               # S m−1 M−1
    C2 = 4.1                # μM
    E2 = 0.19               # eV

    i0 = (𝜎0 * C0 * np.exp((-(E0/Kb) * ((1/temp) - (1/Tr))))) # pure ice
    i1 = (𝜎1 * C1 * np.exp((-(E1/Kb) * ((1/temp) - (1/Tr))))) # acids
    i2 = (𝜎2 * C2 * np.exp((-(E2/Kb) * ((1/temp) - (1/Tr))))) # salts
    

    if pure_ice:
        final_cond = i0
    else:
        final_cond = i0 + i1 + i2

    return final_cond

def first_attenuation_limit(depth, attenuation, attenuation_limit):
    """Interpolate the first threshold crossing in the supplied array order.

    ``depth``(m) and ``attenuation`` (dB) are corresponding one-dimensional arrays;
    the result uses the same units as ``depth``. Returns NaN if no adjacent
    pair crosses or touches ``attenuation_limit``.
    """
    delta = attenuation - attenuation_limit
    crossing_idx = np.where(delta[:-1] * delta[1:] <= 0)[0]
    if crossing_idx.size == 0:
        return np.nan

    i = crossing_idx[0]
    d0, d1 = depth[i], depth[i + 1]
    a0, a1 = attenuation[i], attenuation[i + 1]

    if a0 == a1:
        return d0
    # same linear interpolation formula as in eutectic interface
    return d0 + (attenuation_limit - a0) * (d1 - d0) / (a1 - a0) 

class AttenuationInterface:
    """Calculate radar attenuation and its threshold depth for a simulation.

    Parameters
    ----------
    sim : GaiaSim
        Simulation providing temperature, depth, and grid data. Depth spacing
        must be uniform.
    attenuation_limit : float
        Two-way attenuation threshold in dB.
    attenuation_model : {"Low Loss", "High Loss"}
        Conductivity model used for the calculation.

    Attributes
    ----------
    attenuation_2d : ndarray
        Cumulative two-way attenuation by depth and shell, in dB.
    depth_to_attenuation_limit : ndarray
        Interpolated threshold depth for each shell, in meters; NaN if there
        is no crossing.
    distance_along_equator : ndarray
        Distance along the equator for each shell, in meters.
    avg_depth_to_attenuation_limit : float
        Mean threshold depth, excluding NaNs, in meters.

    Raises
    ------
    ValueError
        If the attenuation model is invalid or depth spacing is not uniform.
    """

    def __init__(self, sim, attenuation_limit, attenuation_model):
        self.attenuation_limit = attenuation_limit
        self.attenuation_model = attenuation_model

        pure_ice = None
        if attenuation_model == "Low Loss":
            pure_ice = True
        elif attenuation_model == "High Loss":
            pure_ice = False
        else:
            raise ValueError("Invalid attenuation model. Must be 'Low Loss' or 'High Loss'.")

        n_layers, n_shells = sim.avg_temp_2d.shape
        self.attenuation_2d = np.zeros_like(sim.avg_temp_2d, dtype=float)

        
        # check for uniform spacing in depth array
        depth_diffs = np.diff(sim.depth_2d, axis=0)
        reference_diff = depth_diffs[0, 0]

        if not np.allclose(depth_diffs, reference_diff):
            raise ValueError("Depth array has non-uniform spacing, or some weird floating point error. Please check the depth array for issues.")

        delta_D_km = abs(reference_diff) / 1000

        for shell in range(n_shells):
            cumulative_attenuation = 0.0

            # avg_temp_2d and depth_2d are ordered from the ice-ocean interface to the surface,
            # but attenuation to a target depth must be accumulated along the radar path from the surface downward.
            for layer in range(n_layers - 1, -1, -1):
                layer_attenuation = (
                    2
                    * 0.914 # this is dB/km, so deltaD does need to be in km
                    * calc_electrical_conductivity(sim.avg_temp_2d[layer, shell], pure_ice)
                    * delta_D_km
                )
                cumulative_attenuation += layer_attenuation
                self.attenuation_2d[layer, shell] = cumulative_attenuation
        
        

        self.depth_to_attenuation_limit = np.array([
            first_attenuation_limit(sim.depth_2d[:, j], self.attenuation_2d[:, j], attenuation_limit)
            for j in range(sim.avg_temp_2d.shape[1])
        ])

        # radians * radius = distance along equator
        grid = sim.last_output.grid
        theta_2d = grid.coordsSph[:, 2].reshape(sim.avg_temp_2d.shape)
        theta_surface = theta_2d[-1, :]
        self.distance_along_equator = sim.dim_data["outer_radius"] * (theta_surface - theta_surface.min())

        self.avg_depth_to_attenuation_limit = np.nanmean(self.depth_to_attenuation_limit)


    def plot_interface(self):
        """Display threshold depth against distance along the equator."""
        plt.figure(figsize=(10, 6))
        g = sns.lineplot(x=self.distance_along_equator/1000, y=self.depth_to_attenuation_limit/1000)
        g.set(
            xlabel='Distance Along Equator (km)',
            ylabel='Depth to Attenuation Limit (km)',
            title=f'Depth to {self.attenuation_limit} dB ({self.attenuation_model})',
        )
        g.invert_yaxis()
        g.grid(True)
        sns.despine(ax=g)
        plt.show()

        return



    
    
    
    
    
    
    
    
    
    
    
