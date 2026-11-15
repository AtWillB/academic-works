import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import matplotlib.cm as cm
import vtkplotlib as vpl
import numpy as np
import json
import os
from pathlib import Path


def _srgb_to_linear(rgb):
    rgb = np.asarray(rgb, dtype=float)
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def _linear_to_srgb(rgb):
    rgb = np.asarray(rgb, dtype=float)
    return np.where(rgb <= 0.0031308, 12.92 * rgb, 1.055 * np.power(rgb, 1 / 2.4) - 0.055)


def _rgb_to_lab(rgb):
    rgb = np.clip(np.asarray(rgb, dtype=float), 0.0, 1.0)
    lin = _srgb_to_linear(rgb)

    x = 0.4124564 * lin[..., 0] + 0.3575761 * lin[..., 1] + 0.1804375 * lin[..., 2]
    y = 0.2126729 * lin[..., 0] + 0.7151522 * lin[..., 1] + 0.0721750 * lin[..., 2]
    z = 0.0193339 * lin[..., 0] + 0.1191920 * lin[..., 1] + 0.9503041 * lin[..., 2]

    xn, yn, zn = 0.95047, 1.00000, 1.08883
    xr, yr, zr = x / xn, y / yn, z / zn

    delta = 6 / 29

    def f(t):
        return np.where(t > delta ** 3, np.cbrt(t), (t / (3 * delta ** 2)) + (4 / 29))

    fx, fy, fz = f(xr), f(yr), f(zr)
    l = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    return np.stack([l, a, b], axis=-1)


def _lab_to_rgb(lab):
    lab = np.asarray(lab, dtype=float)
    l, a, b = lab[..., 0], lab[..., 1], lab[..., 2]

    fy = (l + 16) / 116
    fx = fy + (a / 500)
    fz = fy - (b / 200)

    delta = 6 / 29

    def finv(t):
        return np.where(t > delta, t ** 3, 3 * delta ** 2 * (t - 4 / 29))

    xr, yr, zr = finv(fx), finv(fy), finv(fz)

    xn, yn, zn = 0.95047, 1.00000, 1.08883
    x, y, z = xr * xn, yr * yn, zr * zn

    r_lin = 3.2404542 * x - 1.5371385 * y - 0.4985314 * z
    g_lin = -0.9692660 * x + 1.8760108 * y + 0.0415560 * z
    b_lin = 0.0556434 * x - 0.2040259 * y + 1.0572252 * z

    rgb_lin = np.stack([r_lin, g_lin, b_lin], axis=-1)
    rgb = _linear_to_srgb(np.clip(rgb_lin, 0.0, 1.0))
    return np.clip(rgb, 0.0, 1.0)


def _register_cmap(cmap):
    try:
        plt.colormaps.register(cmap, force=True)
    except TypeError:
        try:
            plt.colormaps.register(cmap)
        except ValueError:
            pass


def _build_paraview_colormap(cmap_name, color_space, rgb_points):
    colors = []
    positions = []

    for i in range(0, len(rgb_points), 4):
        positions.append(rgb_points[i])
        colors.append((rgb_points[i + 1], rgb_points[i + 2], rgb_points[i + 3]))

    min_pos = min(positions)
    max_pos = max(positions)
    if max_pos == min_pos:
        normalized_positions = [0.0 for _ in positions]
    else:
        normalized_positions = [(p - min_pos) / (max_pos - min_pos) for p in positions]

    if str(color_space).upper() == 'LAB':
        sample_x = np.linspace(0.0, 1.0, 256)
        pos = np.asarray(normalized_positions, dtype=float)
        rgb = np.asarray(colors, dtype=float)
        lab = _rgb_to_lab(rgb)
        sampled_lab = np.empty((len(sample_x), 3), dtype=float)

        for i, x in enumerate(sample_x):
            if x <= pos[0]:
                sampled_lab[i] = lab[0]
            elif x >= pos[-1]:
                sampled_lab[i] = lab[-1]
            else:
                j = np.searchsorted(pos, x) - 1
                x0, x1 = pos[j], pos[j + 1]
                t = 0.0 if x1 == x0 else (x - x0) / (x1 - x0)
                sampled_lab[i] = (1.0 - t) * lab[j] + t * lab[j + 1]

        sampled_rgb = _lab_to_rgb(sampled_lab)
        return ListedColormap(sampled_rgb, name=cmap_name)

    color_list = list(zip(normalized_positions, colors))
    return LinearSegmentedColormap.from_list(cmap_name, color_list)

# Load and register the paraview icy_moon colormap
def _load_paraview_colormap(json_path):
    """Load the paraview_icy_moon colormap from JSON and register it with matplotlib."""
    # The JSON file is at /plp_user/byrn_wi/paraview_icy_moon.json
    # This file is at /plp_user/byrn_wi/radar_attenuation/src/radar_attenuation/colors.py
    # So we need to go up 3 levels
    cmap_name = json_path.stem

    if not os.path.exists(json_path):
        print(f"Warning: paraview_icy_moon.json not found at {json_path}")
        return
    
    with open(json_path, 'r') as f:
        colormap_data = json.load(f)
    
    # Extract the colormap data
    cmap_info = colormap_data[0]
    color_space = str(cmap_info.get('ColorSpace', 'RGB')).upper()
    rgb_points = cmap_info['RGBPoints']
    _register_cmap(_build_paraview_colormap(cmap_name, color_space, rgb_points))



def _load_vtkplotlib_colormaps():
    """Register all vtkplotlib colormaps with matplotlib."""
    try:
        # vtkplotlib registers its colormaps automatically when imported
        # Access them to ensure they're loaded
        if hasattr(vpl, 'cmaps'):
            # Register each vtkplotlib colormap with matplotlib
            for cmap_name in dir(vpl.cmaps):
                if not cmap_name.startswith('_'):
                    try:
                        cmap = getattr(vpl.cmaps, cmap_name)
                        if hasattr(cmap, 'name'):
                            _register_cmap(cmap)
                    except Exception:
                        pass
    except Exception as e:
        print(f"Warning: Could not load vtkplotlib colormaps: {e}")

# Load the colormap on import
_load_vtkplotlib_colormaps()

BASE = Path(__file__).with_name("colormaps")

for json_file in BASE.glob("*.json"):
    _load_paraview_colormap(json_file)