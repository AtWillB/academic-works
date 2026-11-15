from pathlib import Path

import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

def first_eutectic_depth(depth, temp, eutectic_temp):
    """Interpolate the first temperature crossing in the supplied array order.

    ``depth`` and ``temp`` are corresponding one-dimensional arrays; the
    result uses the same units as ``depth``. Returns NaN if no adjacent pair
    crosses or touches ``eutectic_temp``.
    """
    delta = temp - eutectic_temp
    crossing_idx = np.where(delta[:-1] * delta[1:] <= 0)[0]
    if crossing_idx.size == 0:
        return np.nan

    i = crossing_idx[0]
    d0, d1 = depth[i], depth[i + 1]
    t0, t1 = temp[i], temp[i + 1]

    if t0 == t1:
        return d0

    return d0 + (eutectic_temp - t0) * (d1 - d0) / (t1 - t0)

class EutecticInterface:
    """Calculate the depth of a eutectic temperature across a simulation.

    Parameters
    ----------
    sim : GaiaSim
        Simulation providing temperature, depth, and grid data.
    eutectic_temperature : float
        Target temperature in kelvin.

    Attributes
    ----------
    depth_to_eutectic : ndarray
        Interpolated depth for each shell, in meters; NaN if there is no
        crossing. The first crossing is selected from the ice-ocean interface
        toward the surface.
    distance_along_equator : ndarray
        Distance along the equator for each shell, in meters.
    avg_depth_to_eutectic : float
        Mean eutectic depth, excluding NaNs, in meters.
    """

    def __init__(self, sim, eutectic_temperature):
        self.eutectic_temperature = eutectic_temperature

        self.depth_to_eutectic = np.array([
            first_eutectic_depth(sim.depth_2d[:, j], sim.avg_temp_2d[:, j], eutectic_temperature)
            for j in range(sim.avg_temp_2d.shape[1])
        ])

        # radians * radius = distance along equator
        grid = sim.last_output.grid
        theta_2d = grid.coordsSph[:, 2].reshape(sim.avg_temp_2d.shape)
        theta_surface = theta_2d[-1, :]
        self.distance_along_equator = sim.dim_data["outer_radius"] * (theta_surface - theta_surface.min())

        self.avg_depth_to_eutectic = np.nanmean(self.depth_to_eutectic)


    def plot_interface(self, savefile_path=None):
        """Plot eutectic depth against distance; optionally save to a file."""
        plt.figure(figsize=(10, 6))

        g = sns.lineplot(x=self.distance_along_equator/1000, y=self.depth_to_eutectic/1000)
        
        g.set(
            xlabel='Distance Along Equator (km)',
            ylabel='Depth to Eutectic Interface (km)',
            title=f'Depth to {self.eutectic_temperature} (K)',
        )

        g.invert_yaxis()
        g.grid(True)
        sns.despine(ax=g)

        if savefile_path:
            plt.savefig(str(savefile_path), bbox_inches='tight', pad_inches=0, transparent=True, dpi = 160)
            plt.close()

        plt.show()

        return



    
    
    
    
    
    
    
    
    
    
    
