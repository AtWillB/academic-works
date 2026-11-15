from pathlib import Path
import json

import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import gaia # propriatary library for simulations in DLR
from .attenuation_interface import AttenuationInterface
from .eutectic_interface import EutecticInterface
import europa_eutectic.util.colors as colors

base_cmap = sns.color_palette("icy_moon_2", as_cmap = True) # My custom colormap




def compute_stagnant_lid_depth(o, D_ref, velocity_threshold=0.01):
    """Estimate stagnant-lid depth for each column of a GAIA output.

    Parameters
    ----------
    o : GAIA output
        Simulation output containing grid and velocity data.
    D_ref : float
        Reference shell thickness in meters.
    velocity_threshold : float
        Fraction of the maximum velocity used as the threshold.

    Returns
    -------
    ndarray
        Estimated lid depth for each column, in kilometers.
    """

    plot_stagnant_lid_depth = []
    depth = (o.grid.outerRadius - o.grid.shellRadius)
    depth[depth < 0] = 0.0
    depth[depth > 1] = 1.0
    depth = depth*D_ref*1e-3
    
    # Loop over each column
    for i in range(o.grid.nCellsPerShell[0]):
        # Initializing the index of stagnant lid depth
        lid_depth_idx = 0
        j = 0

        # Loop over each cell in a column
        while j < (len(o.vmag.formatted_data[:, i, 0]) - 1):
            # Check if the velocity is below the threshold
            if o.vmag.formatted_data[j, i, 0] > velocity_threshold * np.max(o.vmag.formatted_data[:, :, 0]):
                lid_depth_idx = j
            j += 1
        
        # Compute lid depth
        lid_depth = depth[lid_depth_idx + 1]  # [km]
        plot_stagnant_lid_depth.append(lid_depth)
        plot_stagnant_lid_depth_array = np.array(plot_stagnant_lid_depth)

    return plot_stagnant_lid_depth_array


class GaiaSim:
    """Load a GAIA simulation and derive its averaged fields and interfaces.

    Parameters
    ----------
    p : pathlib.Path
        Simulation directory; its name is used as the case ID.
    eutectics : sequence of float
        Eutectic temperatures in kelvin. Defaults to 237.15 and 252.05 K.
    attenuation_params : sequence of (float, str)
        Pairs of attenuation threshold in dB and model name (``"Low Loss"``
        or ``"High Loss"``). Defaults to 100 dB for each model.

    Attributes
    ----------
    avg_temp_2d : ndarray
        Temperature field averaged over the final 10% of saved outputs, in K.
    depth_2d : ndarray
        Depth field in meters, measured from the outermost grid radius.
    eutectics : list of EutecticInterface
        One interface for each requested eutectic temperature, in order.
    attenuation_interfaces : list of AttenuationInterface
        One interface for each threshold and model pair, in input order.
    times : ndarray
        Simulation output times in millions of years.

    Other averaged fields and summary statistics are available as attributes.
    ``save`` stores the interface parameters, and ``load_from_json``
    reconstructs the interfaces from those parameters.
    """

    def __init__(self, p, eutectics = [237.15, 252.05], attenuation_params = [(100, "Low Loss"), (100, "High Loss")]):
        ## load the sim and get the temp profile
        ## turn this into a function that gets the average temp profile for the last 10% of the sim. 
        ## then we can use this to get an average stagnant lid depth, and an average Nusselt number
        caseID = p.stem
        
        sim = gaia.Simulation(caseid=caseID, sim_dir = str(p), grid_dir = str(p))

        self.path = str(p)
        self.sim = sim
        self.caseID = caseID
        self.parent_dir = p.parent

        with open(p / f"{caseID}.json", "r") as dimensional_data_file:
            self.dim_data = json.load(dimensional_data_file)
        dim_coef = {}
        self.dim_coef = self.load_dim_coefs(dim_coef)


        self.times = sim.getTimes()
        last_10_percent = self.times[int(len(self.times)*0.9):]
        last_10_percent_outputs = [sim.getAtTime(t, read_fields="*") for t in last_10_percent]
        self.last_output = sim.getLast(read_fields = "*")


        # what we are really interested in
        self.avg_temp_2d = None

        self.avg_deformation_2d = None
        self.rms_velocity_temporal = None
        self.avg_rms_velocity = None
        
        
        self.avg_stagnant_lid_depth = None
        self.avg_Nusselt_top = None
        self.avg_Nusselt_bottom = None
        self.avg_Ra_interior = None

        self.load_averages(last_10_percent_outputs)

        # valueable metadata
        self.rad_2d = self.last_output.grid.coordsSph[:, 0].reshape(self.avg_temp_2d.shape) * self.dim_coef["scale_D"]
        self.depth_2d = np.max(self.rad_2d) - self.rad_2d

        self.eta_ref = self.dim_data["log_10(eta_ref)"]
        self.Ra = self.dim_data["Ra"]
        self.D = self.dim_data["Dref"]/1000

        self.eutectics = [EutecticInterface(self, eut_temp) for eut_temp in eutectics]
        self.attenuation_interfaces = [AttenuationInterface(self, attenuation_limit, attenuation_model) for attenuation_limit, attenuation_model in attenuation_params]

        self.times = self.times * self.dim_coef["scale_t"] * 1/(3600*24*365) * 1e-6# in Myr
        self.final_time = self.times[-1]
        
        
    
    def plot_eutectics(self, savepath = None):
        """Plot eutectic interfaces and their means; optionally save to a directory."""
        df_list = []
        avg_df_list = []

        for eutectic in self.eutectics:
            eut_dict = {}

            eut_dict["Depth to Eutectic (km)"] = eutectic.depth_to_eutectic/1000 # km
            eut_dict["Distance Along Equator (km)"] = eutectic.distance_along_equator/1000 # km
            eut_dict["Eutectic Temperature (K)"] = [eutectic.eutectic_temperature for _ in range(len(eutectic.depth_to_eutectic))]

            df_list.append(pd.DataFrame(eut_dict))

            avg_df_list.append(pd.DataFrame({
                "Depth to Eutectic (km)": np.full(
                    len(eutectic.depth_to_eutectic),
                    np.mean(eutectic.depth_to_eutectic) / 1000,
                ),
                "Distance Along Equator (km)": eutectic.distance_along_equator/1000,
                "Eutectic Temperature (K)": [eutectic.eutectic_temperature for _ in range(len(eutectic.depth_to_eutectic))],
            }))
        
        eut_df = pd.concat(df_list)
        avg_eut_df = pd.concat(avg_df_list)

        hue_order = sorted(eut_df["Eutectic Temperature (K)"].unique())
        n_lines = len(hue_order)
        positions = np.linspace(0.2, 0.85, n_lines)
        line_palette = [base_cmap(pos) for pos in positions]
        color_lookup = dict(zip(hue_order, line_palette))

        sns.set_context("paper", font_scale=1.3)
        sns.set_style("whitegrid")
        g = sns.lineplot(data=eut_df, 
                     x="Distance Along Equator (km)", 
                     y="Depth to Eutectic (km)", 
                     hue="Eutectic Temperature (K)",
                     hue_order=hue_order,
                     palette=line_palette)

        for eutectic_temperature, avg_group in avg_eut_df.groupby("Eutectic Temperature (K)"):
            g.plot(
                avg_group["Distance Along Equator (km)"],
                avg_group["Depth to Eutectic (km)"],
                linestyle="--",
                color=color_lookup[eutectic_temperature],
            )
        
        g.invert_yaxis()
        g.set_title(f"{self.parent_dir.name}: {self.caseID}")
        handles, labels = g.get_legend_handles_labels()
        handles.append(Line2D([0], [0], color="black", linestyle="--", label="Average Depth"))
        labels.append("Average Depth")
        legend = g.legend(handles=handles, labels=labels, loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)
        legend.set_title("Eutectic Temperature (K)")

        if savepath:
            legend.remove()
            plt.savefig(str(savepath / f"{self.caseID}_eutectic_interfaces.png"), bbox_inches='tight', pad_inches=0, transparent=True, dpi = 160)
            plt.close()

        plt.show()
        return


    def __repr__(self):
        return (
            f"""GaiaSimcaseID={self.caseID!r}, 
            parent_dir={str(self.parent_dir)!r}, 
            "Shell thickness"={self.dim_data['thickness']:.2f} (m),
            "log_10(eta_ref)"={self.dim_data['log_10(eta_ref)']:.2f} log_10(Pa s),
            Ra={self.Ra!r}, 
            final_time={self.final_time:.6g} Myr)"""
        )

    def load_dim_coefs(self, dim_coef):
        """Populate and return dimensional scaling coefficients from simulation data."""
        dim_coef["scale_T"] = self.dim_data["Tb"] - self.dim_data["T0"] # k
        dim_coef["scale_C"] = self.dim_data["rho_mix"] - self.dim_data["rho_solid"] # km/m^3
        dim_coef["scale_D"] = self.dim_data["outer_radius"] - self.dim_data["inner_radius"] # m

        dim_coef["scale_v"] = self.dim_data["therm_diff_ref"]/dim_coef["scale_D"] # m/s 
        dim_coef["scale_t"] = dim_coef["scale_D"]**2 / self.dim_data["therm_diff_ref"] # seconds
        return dim_coef

    def load_averages(self, last_10_percent_outputs):
        """Compute averaged fields and summary statistics from GAIA outputs."""
        dim_coef = self.dim_coef
        dim_data = self.dim_data

        avg_temp_2d = []

        avg_deformation_2d = []
        avg_rms_velocity = []

        avg_stagnant_lid_depth = []
        avg_Nusselt_top = []
        avg_Nusselt_bottom = []
        avg_Ra_interior = []


        # add mode of m-field here
        # add RMS velocity for whole time series
        # add avg RMS velocity over the last 10% here
        rad_2d = self.last_output.grid.coordsSph[:, 0].reshape(self.last_output.T.formatted_data[:, :, 0].shape) * self.dim_coef["scale_D"]
        depth_2d = np.max(rad_2d) - rad_2d
        Ra_i_func = lambda g, alpha, rho, deltaT, D, eta_i, kappa: (g * alpha * rho * deltaT * D**3) / (eta_i * kappa)

        for o in last_10_percent_outputs:
            T = o.T.formatted_data[:, :, 0] * dim_coef["scale_T"] + dim_data["T0"]
            avg_temp_2d.append(T)
            if "m" in o.fields:
                avg_deformation_2d.append(o.m.formatted_data[:, :, 0]) # no dimension, its just an index 

            stagnant_lid_depth = compute_stagnant_lid_depth(o, dim_coef["scale_D"])
            avg_stagnant_lid_depth.append(stagnant_lid_depth)

            Nu_bot, Nu_top, _, _ = o.getNusselt()
            avg_Nusselt_top.append(Nu_top)
            avg_Nusselt_bottom.append(Nu_bot)

            avg_rms_velocity.append(o.getStats()["vmag_mean2"] * dim_coef["scale_v"] * 3600*24*365 * 100) # cm/year
            
            below_lid_mask = depth_2d > stagnant_lid_depth[np.newaxis, :]

            lid_row_idx = np.argmin(
                np.abs(depth_2d - stagnant_lid_depth[np.newaxis, :]),
                axis=0,
            )
            exact_lid_mask = np.zeros_like(depth_2d, dtype=bool)
            exact_lid_mask[lid_row_idx, np.arange(depth_2d.shape[1])] = True

            eta = o.V.formatted_data[:, :, 0] * self.dim_data["log_10(eta_ref)"] # always use eta_ref for dimensionalization, even with complex_rheo
            eta_i = np.mean(eta[below_lid_mask])

            mean_stagnant_T = np.mean(T[exact_lid_mask])
            deltaT = self.dim_data["Tb"] - mean_stagnant_T



            Ra_i = Ra_i_func(
                self.dim_data["gravity"],
                self.dim_data["therm_exp"]*1e-6, # It will vary, and likely be less, but its soo much dam work. So I think you just call it here. 
                self.dim_data["rho_mix"],
                deltaT,
                self.dim_data["Dref"],
                eta_i,
                self.dim_data["therm_diff_ref"],
            )
            avg_Ra_interior.append(Ra_i)
            
            
        
        if avg_deformation_2d:
            stack = np.stack(avg_deformation_2d)
            values = np.unique(stack)
            # the below line is the numpy equivalent of finding the mode. Sadly, there is no np.mode
            self.avg_deformation_2d = values[np.argmax(np.stack([(stack == v).sum(axis=0) for v in values]), axis=0)]

        self.avg_temp_2d = np.stack(avg_temp_2d).mean(axis = 0)
        self.avg_stagnant_lid_depth = np.stack(avg_stagnant_lid_depth).mean(axis=0)
        self.avg_Nusselt_top = np.mean(avg_Nusselt_top)
        self.avg_Nusselt_bottom = np.mean(avg_Nusselt_bottom)
        self.avg_Ra_interior = np.mean(avg_Ra_interior)

        self.avg_rms_velocity = np.mean(avg_rms_velocity)
        self.rms_velocity_temporal = self.sim.getStats(read_fields="vmag")["vmag_mean2"] * self.dim_coef["scale_v"] * 3600*24*365 * 100 # cm/year

        
    
    def save(self, p):
        """Save summary data and interface parameters as JSON in directory ``p``."""
        with open(p / f"{self.caseID}_data.json", "w") as f:
            json.dump({
                "path": str(Path(self.path).resolve()),
                "caseID": self.caseID,
                "parent_dir": str(self.parent_dir),

                "dim_data": self.dim_data,
                "times": self.times.tolist(),

                # on load_time, re-load last 10% of outputs

                "avg_temp_2d": self.avg_temp_2d.tolist(), 
                "avg_deformation_2d": self.avg_deformation_2d.tolist() if self.avg_deformation_2d is not None else None,
                "avg_stagnant_lid_depth": self.avg_stagnant_lid_depth.tolist(),
                "avg_Nusselt_top": self.avg_Nusselt_top,
                "avg_Nusselt_bottom": self.avg_Nusselt_bottom,
                "avg_Ra_interior": self.avg_Ra_interior,

                "avg_rms_velocity": self.avg_rms_velocity,
                "rms_velocity_temporal": self.rms_velocity_temporal.tolist(),

                "eta_ref": self.eta_ref,
                "Ra": self.Ra,
                "D": self.D,

                "eutectics": [eut.eutectic_temperature for eut in self.eutectics],
                "attenuation_params": [(att.attenuation_limit, att.attenuation_model) for att in self.attenuation_interfaces],


                "final_time": self.final_time,
            }, f)
        

        print(f"You have saved {f'{self.caseID}_data.json'} at {str(p)}")
        print(self.__repr__())
    
    @classmethod
    def load_from_json(cls, p):
        """Load saved summary data and reconstruct interfaces from a JSON file.

        The original simulation directory remains necessary to load the grid
        and final GAIA output.
        """
        p = Path(p)

        with open(p, "r") as f:
            data = json.load(f)

        sim = cls.__new__(cls)
        sim_path = Path(data["path"])
        if not sim_path.is_absolute():
            sim_path = (p.parent / sim_path).resolve()

        sim.path = str(sim_path)
        sim.caseID = data["caseID"]
        sim.parent_dir = Path(data["parent_dir"])
        sim.sim = gaia.Simulation(caseid=sim.caseID, sim_dir=sim.path, grid_dir=sim.path) 


        sim.dim_data = data["dim_data"]
        sim.dim_coef = sim.load_dim_coefs({})
        sim.times = np.array(data["times"]) # don't need to worry here, since the averaging has already been done

        sim.last_output = sim.sim.getLast()


        sim.avg_temp_2d = np.array(data["avg_temp_2d"])
        sim.avg_deformation_2d = np.array(data["avg_deformation_2d"]) if data["avg_deformation_2d"] is not None else None
        sim.avg_stagnant_lid_depth = np.array(data["avg_stagnant_lid_depth"])
        sim.avg_Nusselt_top = data["avg_Nusselt_top"]
        sim.avg_Nusselt_bottom = data["avg_Nusselt_bottom"]
        #sim.avg_Ra_interior = data["avg_Ra_interior"]

        sim.avg_rms_velocity = data["avg_rms_velocity"]
        sim.rms_velocity_temporal = np.array(data["rms_velocity_temporal"])

        sim.rad_2d = sim.last_output.grid.coordsSph[:, 0].reshape(sim.avg_temp_2d.shape) * sim.dim_coef["scale_D"] 

        # so 0 depth is the surface, and no negative depths. 
        # This does mean that there is a correction, and every simulations depth value will be off by half a cell 
        # @60km, a cell is 182 m long
        # I think for now, I will ignore this problem. If it becomes an issue, I will see how to fix this. 
        sim.depth_2d = np.max(sim.rad_2d) - sim.rad_2d # depth 0 is 50km, so depth[max(i)] is 0

        sim.eta_ref = data["eta_ref"]
        sim.Ra = data["Ra"]
        sim.D = data["D"]

        # load interfaces
        eutectic_temps = data.get("eutectics", [237.15, 252.05])
        sim.eutectics = [EutecticInterface(sim, eut_temp) for eut_temp in eutectic_temps]

        attenuation_params = data.get("attenuation_params", [(100, "Low Loss"), (100, "High Loss")])
        sim.attenuation_interfaces = [AttenuationInterface(sim, attenuation_limit, attenuation_model) for attenuation_limit, attenuation_model in attenuation_params]
        
        sim.final_time = data["final_time"]

        return sim
    
    def plot_field(self, field, field_name, levels, transparent=False, cmap = base_cmap, eutectics = None, savepath = None):
        """Plot a gridded field, optionally overlaying eutectics or saving it.

        ``eutectics`` enables overlays of this simulation's eutectic interfaces;
        ``savepath`` is the directory for the output image.
        """

        coords = np.array(self.last_output.grid.shellCoords)
        x = coords[:, :, 0]
        y = coords[:, :, 1]
        
        field = field.squeeze()
        

        if savepath:
            fig, ax = plt.subplots( figsize=(8.5, 14), dpi=180) # ask Tina if this is right

            ax.contourf(x, y, field, levels, cmap = cmap, extend="both")

            ax.set_aspect('equal') # I think this line is necessary
            ax.set_axis_off()

            if eutectics:
                for eutectic, color in zip(self.eutectics, ("black", "grey")):
                    zol_broadcast = np.broadcast_to(np.asarray(eutectic.depth_to_eutectic).reshape(1, -1), self.depth_2d.shape)

                    diff = np.abs(self.depth_2d.squeeze() - zol_broadcast)
                    best_row_indices = np.argmin(diff, axis=0)

                    clean_mask = np.zeros_like(self.depth_2d.squeeze(), dtype=int)
                    cols = np.arange(clean_mask.shape[1])
                    clean_mask[best_row_indices, cols] = 1

                    ax.contour(y, x, clean_mask, levels=[0.5], colors=color, linewidths=1)

            fig.savefig(str(savepath / f"{self.caseID}_{field_name}.png"), bbox_inches='tight', pad_inches=0, transparent=True)
            plt.close(fig)
            return


        fig, ax = plt.subplots(figsize=(10, 6))
        contour = ax.contourf(y, x, field, levels, cmap=cmap, extend="both")
        cbar = fig.colorbar(contour, ax=ax, orientation="horizontal")
        cbar.set_label(field_name)
        ax.set_aspect("equal")
        ax.set_axis_off()

        if eutectics:
            for eutectic, color in zip(self.eutectics, ("black", "grey")):
                zol_broadcast = np.broadcast_to(np.asarray(eutectic.depth_to_eutectic).reshape(1, -1), self.depth_2d.shape)

                diff = np.abs(self.depth_2d.squeeze() - zol_broadcast)
                best_row_indices = np.argmin(diff, axis=0)

                clean_mask = np.zeros_like(self.depth_2d.squeeze(), dtype=int)
                cols = np.arange(clean_mask.shape[1])
                clean_mask[best_row_indices, cols] = 1

                ax.contour(y, x, clean_mask, levels=[0.5], colors=color, linewidths=1)

        if transparent:
            fig.patch.set_alpha(0)
            ax.patch.set_alpha(0)

        plt.show()

        return