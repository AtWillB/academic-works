from pathlib import Path

import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

def first_eutectic_depth(depth, temp, eutectic_temp):
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
    def __init__(self, sim, eutectic_temperature):
        self.eutectic_temperature = eutectic_temperature

        # for each depth column, find the first depth (from the ice-ocean interface)
        # where the temperature crosses the eutectic temperature
        # do this for every shell
        # do linear interpolation to find the depth of the eutectic interface between two depth points
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



    
    
    
    
    
    
    
    
    
    
    
