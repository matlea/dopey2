__version__ = "25.10.03"
__author__  = "Mats Leandersson"


"""
Version 25.10.18    Plots asymmetry(), polarization() 
Version 25.10.06    Progressing...
Version 25.10.03    The first version.
"""

from colorama import Fore
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy




# ==============================================================================================================================
# ==============================================================================================================================


def plot(D = object, ax = None, **kwargs):
    """
    """
    #
    try:
        if kwargs.get("help", False):
            print(f"{Fore.BLUE}Arguments:")
            print("D           Data object")
            print("ax          matplotlib.axes._axes.Axes")
            print(Fore.RESET)
    except: pass
    #
    if D.data_type == "ccd_2d": return _plot_data_ccd2d(D = D, ax = ax, **kwargs)
    if D.data_type == "fermi_cut": return _plot_data_ccd2d(D = D, ax = ax, transpose = True, **kwargs)
    if D.data_type == "spin_edc": return _plot_data_spin_edc(D = D, ax = ax, **kwargs)
    if D.data_type == "spin_mdc": return _plot_data_spin_edc(D = D, ax = ax, **kwargs)
    if D.data_type == "spin_map": return _plot_data_spin_map(D = D, ax = ax, **kwargs)
    if D.data_type == "spin_polarization": return _plot_data_spin_polarization(D = D, ax = ax, **kwargs)
        


def _plot_data_ccd2d(D = object, ax = None, transpose = False, shup = False, **kwargs):
    """
    """
    #
    try:
        if kwargs.get("help", False):
            print(f"{Fore.BLUE}Keyword arguments:")
            print("figsize     tuple")
            print(Fore.RESET)
    except: pass
    #
    figsize = kwargs.get("figsize", (4,4))
    if not type(figsize) is tuple: figsize = (4,4)
    #
    if type(ax) is type(None): fig, ax = plt.subplots(figsize = figsize)
    else: fig = None
    #
    if not type(transpose) is bool:
        print(f"{Fore.RED}The argument transpose must be a bool. Setting transpose = False.{Fore.RESET}"); transpose = False
    #
    axis0, axis1, intensity = D.axis0, D.axis1, D.intensity
    xlabel, ylabel = D.axis1_label, D.axis0_label
    if transpose: axis0, axis1, intensity, xlabel, ylabel = axis1, axis0, intensity.T, ylabel, xlabel
    #
    extent = [axis1[0], axis1[-1], axis0[-1], axis0[0]]
    ims = ax.imshow(intensity, aspect = "auto", extent = extent)
    ax.invert_yaxis()
    #
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    #
    if not type(fig) is type(None): fig.tight_layout()
    return ax


def _plot_data_spin_edc(D = object, ax = None, **kwargs):
    """
    """
    #
    try:
        if kwargs.get("help", False):
            print(f"{Fore.BLUE}Keyword arguments:")
            print("figsize     tuple")
            print("exclude     list")
            print("polarity    integer     -1:off, +1:on")
            print("asymmetry   bool        applicable for data from asymmetry()")
            print("mean        bool        applicable for data from asymmetry()")
            print("legend      bool        default True, applicable for edc")
            print(Fore.RESET)
    except: pass          
    #
    what_to_plot = "intensity"
    #
    asymmetry = kwargs.get("asymmetry", False)
    mean = kwargs.get("mean", False)
    if asymmetry and "asymmetry" in D.listAttributes():
        what_to_plot = "asymmetry"
    elif mean and "intensity_off" in D.listAttributes():
        what_to_plot = "mean"
    #
    figsize = kwargs.get("figsize", (6,4))
    if not type(figsize) is tuple: figsize = (6,4)
    #
    exclude = kwargs.get("exclude", [])
    if not type(exclude) is list:
        print(f"{Fore.RED}The argument exclude must be a list. Setting default exclude = [].{Fore.RESET}"); exclude = []
    # ----
    polarity = kwargs.get("polarity", 0)
    try: polarity = int(polarity)
    except:
        print(f"{Fore.RED}The argument polarity must be an integer, -1, 0, or 1. Setting default polarity = 0.{Fore.RESET}"); polarity = 0
    if not polarity in [-1,0,1]:
        print(f"{Fore.RED}The argument polarity must be an integer, -1, 0, or 1. Setting default polarity = 0.{Fore.RESET}"); polarity = 0
    #
    np = kwargs.get("np", 0)
    npn = kwargs.get("npn", 0)
    if not (type(np) is int and type(npn) is int):
        print(f"{Fore.RED}The arguments np and npn must integers. Ignoring them.{Fore.RESET}"); np, npn = 0, 0
    if npn > 0:
        if np < 0 or np >= len(D.axis0):
            print(f"{Fore.RED}The argument np must be in (0, {len(D.axis0)-1}). Setting np = 0."); np = 0
        if npn > len(D.axis0) - np:
            print(f"{Fore.RED}The argument npn must be in (1, {len(D.axis0)-np}). Setting it to default npn = 1.{Fore.RESET}"); npn = 1
    #
    legend = kwargs.get("legend", True)
    if not type(legend) is bool:
        print(f"{Fore.RED}The argument legend must be a bool. Setting legend = True."); legend = True
    #
    if type(ax) is type(None): fig, ax = plt.subplots(figsize = figsize)
    else: fig = None
    #
    if what_to_plot == "intensity":
        for i, curve in enumerate(D.intensity):
            if not i in exclude:
                if npn > 0: 
                    norm = curve[np:np+npn].sum(); print("yay", i, np, npn)
                else: norm = 1
                if polarity == 0:
                    ax.plot(D.axis0, curve/norm, label = f"pol={D.parameter0[i]} (c={i})", linewidth = 0.7)
                elif polarity == -1 and D.parameter0[i] == -1:
                    ax.plot(D.axis0, curve/norm, label = f"c={i}", linewidth = 0.7)
                elif polarity == 1 and D.parameter0[i] == 1:
                    ax.plot(D.axis0, curve/norm, label = f"c={i}", linewidth = 0.7)
        ax.set_ylabel(D.intensity_label)
        if legend: ax.legend(fontsize = 8)
    elif what_to_plot == "asymmetry":
        ax.plot(D.axis0, D.asymmetry, linewidth = 0.75)
    elif what_to_plot == "mean":
        ax.plot(D.axis0, D.intensity_off, label = "OFF", color = "tab:blue", linewidth = 0.7)
        ax.plot(D.axis0, D.intensity_on, label = "OFF", color = "tab:red", linewidth = 0.7)
        ax.legend(fontsize = 8)
    #
    ax.set_xlabel(D.axis0_label)
    
    #
    if not type(fig) is type(None): fig.tight_layout()
    return ax

                
def _plot_data_spin_map(D = None, ax = None, **kwargs):
    """
    """
    #
    try:
        if kwargs.get("help", False):
            print(f"{Fore.BLUE}Keyword arguments:")
            print("polarity       integer       default 0, pass -1 or 1 for only positive or only negative Negative(!) polarity (yes...)")
            print("asymmetry      bool          applicable for data from asymmetry()")
            print("mean           bool          applicable for data from asymmetry()")
            print("components     bool          applicable for data from asymmetry()")
            print("cbar           bool          colorbar (default False)")
            print("vmin/vmax      scalars")
            print(Fore.RESET)
    except: pass
    #
    DD = deepcopy(D)
    #
    try: typ = DD.data_type
    except:
        print(f"{Fore.RED}The argument D must be Data object.{Fore.RESET}"); return DD
    if not "spin" in typ:
        print(f"{Fore.RED}The argument D must be Data object containing (sorted!) spin data.{Fore.RESET}"); return DD
    #
    asymmetry  = kwargs.get("asymmetry", False)
    means      = kwargs.get("means", False)
    components = kwargs.get("components", False)
    maps       = kwargs.get("maps", False)
    if not type(asymmetry) is bool:
        print(f"{Fore.MAGENTA}The argument asymmetry must be a bool. Seeting asymmetry = False{Fore.RESET}."); asymmetry = False
    if not type(means) is bool:
        print(f"{Fore.MAGENTA}The argument means must be a bool. Seeting means = False{Fore.RESET}."); means = False
    if not type(components) is bool:
        print(f"{Fore.MAGENTA}The argument components must be a bool. Seeting components = False{Fore.RESET}."); components = False
    if not type(maps) is bool:
        print(f"{Fore.MAGENTA}The argument maps must be a bool. Seeting maps = False{Fore.RESET}."); maps = False
    #    
    if asymmetry and not "asymmetry" in D.listAttributes(): asymmetry = False
    if components and not "component_plus" in D.listAttributes(): components = False
    if means and not "intensity_off" in D.listAttributes(): means = False
    if not (asymmetry or components or means or maps): maps = True
    #
    if maps: 
        numax = len(D.intensity)
        figsize = (numax * 2.5, 2.5)
    elif components or means: 
        numax = 2
        figsize, numax = (numax * 3, 3), 2 
    elif asymmetry: 
        numax = 1
        figsize, numax = (3,3), 1
    #
    fig = None
    if type(ax) is type(None):
        fig, ax = plt.subplots(ncols = numax, figsize = figsize)
    if not type(ax) is np.ndarray: ax = np.array([ax])
    #
    cbar = kwargs.get("cbar", False)
    if not type(cbar) is bool:
        print(f"{Fore.MAGENTA}The argument cbar must be a bool. Seeting cbar = False{Fore.RESET}."); cbar = False
    #
    extent = [D.axis0[0], D.axis0[-1], D.axis1[-1], D.axis1[0]]
    ims = []
    if maps:
        vmin, vmax = [], []
        for mp in D.intensity:
            vmin.append(mp.min()); vmax.append(mp.max())
        vmin, vmax = min(vmin), max(vmax)
        for i, mp in enumerate(D.intensity):
            ims.append( ax[i].imshow(mp.T, aspect = "equal", vmin = vmin, vmax = vmax, extent = extent) )
            ax[i].set_title(f"map {i}, neg. pol {D.parameter0[i]}", fontsize = 9)
    #
    elif components:
        vmin = min([D.component_plus.min(), D.component_minus.min()])
        vmax = min([D.component_plus.max(), D.component_minus.max()])
        ims.append( ax[0].imshow(D.component_plus.T,   aspect = "equal", vmin = vmin, vmax = vmax, extent = extent) )
        ims.append( ax[1].imshow(D.component_minus.T,  aspect = "equal", vmin = vmin, vmax = vmax, extent = extent) )  
        ax[0].set_title("component Plus", fontsize = 10)
        ax[1].set_title("component Minus", fontsize = 10)
    #
    elif means:
        vmin = min([D.intensity_off.min(), D.intensity_on.min()])
        vmax = min([D.intensity_off.max(), D.intensity_on.max()])
        ims.append( ax[0].imshow(D.intensity_off.T, aspect = "equal", vmin = vmin, vmax = vmax, extent = extent) )
        ims.append( ax[1].imshow(D.intensity_on.T,  aspect = "equal", vmin = vmin, vmax = vmax, extent = extent) )
        ax[0].set_title("mean intensity Off", fontsize = 10)
        ax[1].set_title("mean intensity On", fontsize = 10)
    elif asymmetry:
        ims.append( ax[0].imshow(D.asymmetry.T, aspect = "equal", extent = extent, cmap = "bwr") )
        ax[0].set_title("asymmetry", fontsize = 10)
    #
    for i, a in enumerate(ax):
        a.invert_yaxis()
        a.set_xlabel(D.axis0_label, fontsize = 9)
        a.set_ylabel(D.axis1_label, fontsize = 9)
        if cbar: _ = plt.colorbar(ims[i], ax = a)
        
    if not type(fig) is type(None): fig.tight_layout()
    return ax
    


def _plot_data_spin_polarization(D = object, ax = None, **kwargs):
    """
    """
    #
    try:
        if kwargs.get("help", False):
            print(f"{Fore.BLUE}Keyword arguments:")
            print(Fore.RESET)
    except: pass
    #
    if "px" in D.listAttributes() and "py" in D.listAttributes() and "pz" in D.listAttributes(): fig_type = "xyz"
    elif "px" in D.listAttributes() and "py" in D.listAttributes() and not "pz" in D.listAttributes(): fig_type = "xy"
    elif not "px" in D.listAttributes() and not "py" in D.listAttributes() and "pz" in D.listAttributes(): fig_type = "z"
    dim = 1
    if "axis1" in D.listAttributes(): 
        dim = 2
        extent = [D.axis0[0], D.axis0[-1], D.axis1[-1], D.axis1[0]]
    #
    if fig_type == "xyz" and dim == 1:
        fig, ax = plt.subplots(nrows = 3, ncols = 3, figsize = (9,7))
        for i in [0,1,2]: ax[i][0].plot(D.axis0, D.intensity, linewidth = 0.7, color = "k", )
        
        ax[0][1].plot(D.axis0, D.px, linewidth = 0.7, color = "k")
        ax[0][1].fill_between(D.axis0, D.px, 0, where = D.px > 0, color = "blue", alpha = 0.2)
        ax[0][1].fill_between(D.axis0, D.px, 0, where = D.px < 0, color = "red", alpha = 0.2)
        
        ax[1][1].plot(D.axis0, D.py, linewidth = 0.7, color = "k")
        ax[1][1].fill_between(D.axis0, D.py, 0, where = D.py > 0, color = "blue", alpha = 0.2)
        ax[1][1].fill_between(D.axis0, D.py, 0, where = D.py < 0, color = "red", alpha = 0.2)
        
        ax[2][1].plot(D.axis0, D.pz, linewidth = 0.7, color = "k")
        ax[2][1].fill_between(D.axis0, D.pz, 0, where = D.pz > 0, color = "blue", alpha = 0.2)
        ax[2][1].fill_between(D.axis0, D.pz, 0, where = D.pz < 0, color = "red", alpha = 0.2)
        
        ax[0][2].plot(D.axis0, D.intensity_px_plus,  linewidth = 0.7, color = "blue")
        ax[0][2].plot(D.axis0, D.intensity_px_minus, linewidth = 0.7, color = "red")
        ax[0][2].fill_between(D.axis0, D.intensity_px_plus, D.intensity_px_minus, where = D.intensity_px_plus > D.intensity_px_minus, color = "blue", alpha = 0.2)
        ax[0][2].fill_between(D.axis0, D.intensity_px_minus, D.intensity_px_plus, where = D.intensity_px_plus < D.intensity_px_minus, color = "red",  alpha = 0.2)
        
        ax[1][2].plot(D.axis0, D.intensity_py_plus,  linewidth = 0.7, color = "blue")
        ax[1][2].plot(D.axis0, D.intensity_py_minus, linewidth = 0.7, color = "red")
        ax[1][2].fill_between(D.axis0, D.intensity_py_plus, D.intensity_py_minus, where = D.intensity_py_plus > D.intensity_py_minus, color = "blue", alpha = 0.2)
        ax[1][2].fill_between(D.axis0, D.intensity_py_minus, D.intensity_py_plus, where = D.intensity_py_plus < D.intensity_py_minus, color = "red",  alpha = 0.2)
        
        ax[2][2].plot(D.axis0, D.intensity_pz_plus,  linewidth = 0.7, color = "blue")
        ax[2][2].plot(D.axis0, D.intensity_pz_minus, linewidth = 0.7, color = "red")
        ax[2][2].fill_between(D.axis0, D.intensity_pz_plus, D.intensity_pz_minus, where = D.intensity_pz_plus > D.intensity_pz_minus, color = "blue", alpha = 0.2)
        ax[2][2].fill_between(D.axis0, D.intensity_pz_minus, D.intensity_pz_plus, where = D.intensity_pz_plus < D.intensity_pz_minus, color = "red",  alpha = 0.2)
        
        for i in [0,1,2]:
            ax[i][1].axhline(y = 0, linewidth = 0.5, color = "k")
            ax[i][1].set_ylim(-1,1)
        
        ymax = []
        for i in [0,1,2]: ymax.append(ax[i][2].get_ylim()[1])
        ymax = max(ymax)
        for i in [0,1,2]: ax[i][2].set_ylim(-0.05*ymax, ymax)
        
        for i, ttl in enumerate(["Px", "Py", "Pz"]):
            ax[i][0].set_title("Total intensity", fontsize = 10);   ax[i][0].set_ylabel("Intensity, a.u.", fontsize = 9)
            ax[i][1].set_title(ttl, fontsize = 10);                 ax[i][1].set_ylabel("Polarization", fontsize = 9)
            ax[i][2].set_title(f"{ttl}-components", fontsize = 10); ax[i][2].set_ylabel("Intensity, a.u.", fontsize = 9)
            ax[2][i].set_xlabel(D.axis0_label, fontsize = 9)
        
        
        
    elif fig_type == "xy" and dim == 1:
        fig, ax = plt.subplots(nrows = 2, ncols = 3, figsize = (9,4.8))
        for i in [0,1]: ax[i][0].plot(D.axis0, D.intensity, linewidth = 0.7, color = "k", )
        
        ax[0][1].plot(D.axis0, D.px, linewidth = 0.7, color = "k")
        ax[0][1].fill_between(D.axis0, D.px, 0, where = D.px > 0, color = "blue", alpha = 0.2)
        ax[0][1].fill_between(D.axis0, D.px, 0, where = D.px < 0, color = "red", alpha = 0.2)
        
        ax[1][1].plot(D.axis0, D.py, linewidth = 0.7, color = "k")
        ax[1][1].fill_between(D.axis0, D.py, 0, where = D.py > 0, color = "blue", alpha = 0.2)
        ax[1][1].fill_between(D.axis0, D.py, 0, where = D.py < 0, color = "red", alpha = 0.2)
        
        ax[0][2].plot(D.axis0, D.intensity_px_plus,  linewidth = 0.7, color = "blue")
        ax[0][2].plot(D.axis0, D.intensity_px_minus, linewidth = 0.7, color = "red")
        ax[0][2].fill_between(D.axis0, D.intensity_px_plus, D.intensity_px_minus, where = D.intensity_px_plus > D.intensity_px_minus, color = "blue", alpha = 0.2)
        ax[0][2].fill_between(D.axis0, D.intensity_px_minus, D.intensity_px_plus, where = D.intensity_px_plus < D.intensity_px_minus, color = "red",  alpha = 0.2)
        
        ax[1][2].plot(D.axis0, D.intensity_py_plus,  linewidth = 0.7, color = "blue")
        ax[1][2].plot(D.axis0, D.intensity_py_minus, linewidth = 0.7, color = "red")
        ax[1][2].fill_between(D.axis0, D.intensity_py_plus, D.intensity_py_minus, where = D.intensity_py_plus > D.intensity_py_minus, color = "blue", alpha = 0.2)
        ax[1][2].fill_between(D.axis0, D.intensity_py_minus, D.intensity_py_plus, where = D.intensity_py_plus < D.intensity_py_minus, color = "red",  alpha = 0.2)
        
        for i in [0,1]:
            ax[i][1].axhline(y = 0, linewidth = 0.5, color = "k")
            ax[i][1].set_ylim(-1,1)
        
        ymax = []
        for i in [0,1]: ymax.append(ax[i][2].get_ylim()[1])
        ymax = max(ymax)
        for i in [0,1]: ax[i][2].set_ylim(-0.05*ymax, ymax)
        
        for i, ttl in enumerate(["Px", "Py"]):
            ax[i][0].set_title("Total intensity", fontsize = 10);   ax[i][0].set_ylabel("Intensity, a.u.", fontsize = 9)
            ax[i][1].set_title(ttl, fontsize = 10);                 ax[i][1].set_ylabel("Polarization", fontsize = 9)
            ax[i][2].set_title(f"{ttl}-components", fontsize = 10); ax[i][2].set_ylabel("Intensity, a.u.", fontsize = 9)
        
        for i in [0,1,2]: ax[1][i].set_xlabel(D.axis0_label, fontsize = 9)
    
    
    
    elif fig_type == "z" and dim == 1:
        fig, ax = plt.subplots(nrows = 1, ncols = 3, figsize = (9,2.4))
        ax[0].plot(D.axis0, D.intensity, linewidth = 0.7, color = "k", )
        
        ax[1].plot(D.axis0, D.pz, linewidth = 0.7, color = "k")
        ax[1].fill_between(D.axis0, D.pz, 0, where = D.pz > 0, color = "blue", alpha = 0.2)
        ax[1].fill_between(D.axis0, D.pz, 0, where = D.pz < 0, color = "red", alpha = 0.2)
    
        ax[2].plot(D.axis0, D.intensity_pz_plus,  linewidth = 0.7, color = "blue")
        ax[2].plot(D.axis0, D.intensity_pz_minus, linewidth = 0.7, color = "red")
        ax[2].fill_between(D.axis0, D.intensity_pz_plus, D.intensity_pz_minus, where = D.intensity_pz_plus > D.intensity_pz_minus, color = "blue", alpha = 0.2)
        ax[2].fill_between(D.axis0, D.intensity_pz_minus, D.intensity_pz_plus, where = D.intensity_pz_plus < D.intensity_pz_minus, color = "red",  alpha = 0.2)
        
        ax[1].axhline(y = 0, linewidth = 0.5, color = "k")
        ax[1].set_ylim(-1,1)
        
        ax[0].set_title("Total intensity", fontsize = 10);   ax[0].set_ylabel("Intensity, a.u.", fontsize = 9)
        ax[1].set_title("Pz", fontsize = 10);                ax[1].set_ylabel("Polarization", fontsize = 9)
        ax[2].set_title("Pz-components", fontsize = 10);     ax[2].set_ylabel("Intensity, a.u.", fontsize = 9)
        
        for i in [0,1,2]: ax[i].set_xlabel(D.axis0_label, fontsize = 9)
    
    
    
    elif fig_type == "xyz" and dim == 2:
        fig, ax = plt.subplots(nrows = 3, ncols = 4, figsize = (12,9))
        
        vmin = min([D.intensity_px_plus.min(), D.intensity_px_minus.min(), D.intensity_py_plus.min(), D.intensity_py_minus.min(), D.intensity_pz_plus.min(), D.intensity_pz_minus.min()])
        vmax = max([D.intensity_px_plus.max(), D.intensity_px_minus.max(), D.intensity_py_plus.max(), D.intensity_py_minus.max(), D.intensity_pz_plus.max(), D.intensity_pz_minus.max()])
                            
        ax[0][0].imshow(D.intensity.T, extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        ax[0][1].imshow(D.px.T,        extent = extent, aspect = "equal", cmap = "bwr",    vmin = -1,   vmax = 1)
        ax[1][0].imshow(D.intensity.T, extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        ax[1][1].imshow(D.py.T,        extent = extent, aspect = "equal", cmap = "bwr",    vmin = -1,   vmax = 1)
        ax[2][0].imshow(D.intensity.T, extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        ax[2][1].imshow(D.pz.T,        extent = extent, aspect = "equal", cmap = "bwr",    vmin = -1,   vmax = 1)
        
        ax[0][2].imshow(D.intensity_px_plus.T,  extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        ax[0][3].imshow(D.intensity_px_minus.T, extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        ax[1][2].imshow(D.intensity_px_plus.T,  extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        ax[1][3].imshow(D.intensity_px_minus.T, extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        ax[2][2].imshow(D.intensity_pz_plus.T,  extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        ax[2][3].imshow(D.intensity_pz_minus.T, extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        
        for i, ttl in enumerate(["Total intensity", "", "-intensity Plus", "-intensity Minus"]):
            for j in [0,1,2]:
                ax[j][i].set_title(ttl, fontsize = 10)
                ax[j][i].invert_yaxis()
                ax[j][i].set_xlabel(D.axis0_label, fontsize = 9)
                ax[j][i].set_ylabel(D.axis1_label, fontsize = 9)
        
        for i, txt in zip ([0, 1], ["Px", "Py", "Pz"]):
            for j in [1,2,3]: ax[i][j].set_title(f"{txt}{ax[i][j].get_title()}", fontsize = 10)
            
            
    
    elif fig_type == "xy" and dim == 2:
        fig, ax = plt.subplots(nrows = 2, ncols = 4, figsize = (12,4.8))
        
        vmin = min([D.intensity_px_plus.min(), D.intensity_px_minus.min(), D.intensity_py_plus.min(), D.intensity_py_minus.min()])
        vmax = max([D.intensity_px_plus.max(), D.intensity_px_minus.max(), D.intensity_py_plus.max(), D.intensity_py_minus.max()])
                            
        ax[0][0].imshow(D.intensity.T, extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        ax[0][1].imshow(D.px.T,        extent = extent, aspect = "equal", cmap = "bwr",    vmin = -1,   vmax = 1)
        ax[1][0].imshow(D.intensity.T, extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        ax[1][1].imshow(D.py.T,        extent = extent, aspect = "equal", cmap = "bwr",    vmin = -1,   vmax = 1)
        
        ax[0][2].imshow(D.intensity_px_plus.T,  extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        ax[0][3].imshow(D.intensity_px_minus.T, extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        ax[1][2].imshow(D.intensity_px_plus.T,  extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        ax[1][3].imshow(D.intensity_px_minus.T, extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        
        for i, ttl in enumerate(["Total intensity", "", "-intensity Plus", "-intensity Minus"]):
            for j in [0,1]:
                ax[j][i].set_title(ttl, fontsize = 10)
                ax[j][i].invert_yaxis()
                ax[j][i].set_xlabel(D.axis0_label, fontsize = 9)
                ax[j][i].set_ylabel(D.axis1_label, fontsize = 9)
        
        for i, txt in zip ([0, 1], ["Px", "Py"]):
            for j in [1,2,3]: ax[i][j].set_title(f"{txt}{ax[i][j].get_title()}", fontsize = 10)
        
    
    
    elif fig_type == "z" and dim == 2:
        fig, ax = plt.subplots(nrows = 1, ncols = 4, figsize = (12,2.4))
        
        ax[0].imshow(D.intensity.T, extent = extent, aspect = "equal", cmap = "bone_r")
        ax[1].imshow(D.pz.T, extent = extent, aspect = "equal", cmap = "bwr")
        
        vmin = min([D.intensity_pz_plus.min(), D.intensity_pz_minus.min()])
        vmax = max([D.intensity_pz_plus.max(), D.intensity_pz_minus.max()])
        
        ax[2].imshow(D.intensity_pz_plus.T, extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        ax[3].imshow(D.intensity_pz_minus.T, extent = extent, aspect = "equal", cmap = "bone_r", vmin = vmin, vmax = vmax)
        
        for a, ttl in zip(ax, ["Total intensity", "Pz", "Pz-intensity Plus", "Pz-intensity Minus"]):
            a.set_title(ttl, fontsize = 10)
            a.invert_yaxis()
            a.set_xlabel(D.axis0_label, fontsize = 9)
            a.set_ylabel(D.axis1_label, fontsize = 9)
    
    else:
        print(f"{Fore.MAGENTA}Something went wrong."); return
        

    #
    fig.tight_layout()
        
    
        