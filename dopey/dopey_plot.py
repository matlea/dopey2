__version__ = "25.12.07"
__author__  = "Mats Leandersson"


"""
Version 25.12.07    General upgrades, mostly related to spin_arpes but also other stuff.
Version 25.12.06    Adding rudimentary plot for spin_arpes
Version 25.11.26    Updates after data object update.
Version 25.11.16    Minor bugfix.
Version 25.10.30    Small update to plot component intensities for asymmetry data.
Version 25.10.20    Added fermi map viewer, not ready but can be used
Version 25.10.18    Plots asymmetry(), polarization() 
Version 25.10.06    Progressing...
Version 25.10.03    The first version.
"""

from colorama import Fore
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from copy import deepcopy

try: from dopey.dopey_methods import fermiMapCut, subArray
except: 
    try: from dopey.dopey_methods import fermiMapCut, subArray
    except: print(f"{Fore.RED}{__name__} could not import required methods from dopey_methods.{Fore.RESET}")

try: 
    import ipywidgets as ipw
    from IPython.display import display
except: print(f"{Fore.RED}{__name__} could not import the ipywidget module and/or display from IPython.display.{Fore.RESET}")



# ==============================================================================================================================
# ==============================================================================================================================
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
    if D.data_type == "1d": return _plot_data_1d(D = D, ax = ax, **kwargs)
    if D.data_type == "ccd_2d": return _plot_data_ccd2d(D = D, ax = ax, **kwargs)
    if D.data_type == "fermi_cut": return _plot_data_ccd2d(D = D, ax = ax, transpose = True, **kwargs)
    if D.data_type == "spin_edc": return _plot_data_spin_edc(D = D, ax = ax, **kwargs)
    if D.data_type == "spin_mdc": return _plot_data_spin_edc(D = D, ax = ax, **kwargs)
    if D.data_type == "spin_arpes": return _plot_data_spin_arpes(D = D, ax = ax, **kwargs)
    if D.data_type == "spin_map": return _plot_data_spin_map(D = D, ax = ax, **kwargs)
    if D.data_type == "spin_polarization": return _plot_data_spin_polarization(D = D, ax = ax, **kwargs)
    if D.data_type == "ccd_3d": return _plot_data_ccd3d(D = D, ax = ax, **kwargs)
        



def _plot_data_1d(D = object, ax = None, **kwargs):
    """
    """
    try:
        if kwargs.get("help", False):
            print(f"{Fore.BLUE}Keyword arguments:")
            print("figsize     tuple")
            print(Fore.RESET)
    except: pass
    #
    figsize = kwargs.get("figsize", (5,3))
    if not type(figsize) is tuple: figsize = (4,4)
    #
    if type(ax) is type(None): fig, ax = plt.subplots(figsize = figsize)
    else: fig = None
    #
    ax.plot(D.axis0, D.intensity, linewidth = 0.7, color = "k")
    ax.set_xlabel(D.axis0_label, fontsize = 9)
    ax.set_ylabel(D.intensity_label, fontsize = 9)
    #
    if not type(fig) is type(None): fig.tight_layout()
    return ax
    


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
            print("component   bool        applicable for data from asymmetry()")
            print("legend      bool        default True, applicable for edc")
            print(Fore.RESET)
    except: pass          
    #
    what_to_plot = "intensity"
    #
    asymmetry = kwargs.get("asymmetry", False)
    mean = kwargs.get("mean", False)
    component = kwargs.get("component", False)
    if asymmetry and "asymmetry" in D._listAttributes():
        what_to_plot = "asymmetry"
    elif component and "component_plus" in D._listAttributes():
        what_to_plot = "component"
    elif mean and "intensity_off" in D._listAttributes():
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
    elif what_to_plot == "component":
        ax.plot(D.axis0, D.component_plus,  linewidth = 0.75, color = "tab:blue", label = "plus")
        ax.plot(D.axis0, D.component_minus, linewidth = 0.75, color = "tab:red",  label = "minus")
        ax.set_ylabel("Intensity, a.u.")
        ax.legend(fontsize = 8)
    elif what_to_plot == "mean":
        ax.plot(D.axis0, D.intensity_off, label = "OFF", color = "tab:blue", linewidth = 0.7)
        ax.plot(D.axis0, D.intensity_on, label = "OFF", color = "tab:red", linewidth = 0.7)
        ax.legend(fontsize = 8)
    #
    ax.set_xlabel(D.axis0_label)
    
    #
    if not type(fig) is type(None): fig.tight_layout()
    return ax



def _plot_data_spin_arpes(D = None, ax = None, **kwargs):
    """
    """
    try:
        if kwargs.get("help", False):
            print(f"{Fore.BLUE}Keyword arguments:")
            print("intensity   bool        plot raw intensities for ON and OFF.")
            print("asymmetry   bool        plot the asymmetry (applicable for data from asymmetry()).")
            print("component   bool        plot raw components for ON and OFF (applicable for data from asymmetry()).")
            print("show        bool        (applicable for data from asymmetry()).")
            print("cbar        bool        show colorbar, default False")
            print("cmap        str         colormap")
            print("vmin, vmax  numbers")
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
    what_to_plot = "intensity"
    #
    intensity = kwargs.get("intensity", False)
    asymmetry = kwargs.get("asymmetry", False)
    component = kwargs.get("component", False)
    show = kwargs.get("show", False)
    if intensity:
        pass
    elif asymmetry and "asymmetry" in D._listAttributes():
        what_to_plot = "asymmetry"
    elif component and "component_plus" in D._listAttributes():
        what_to_plot = "component"
    elif show and "asymmetry" in D._listAttributes():
        what_to_plot = "show"
    else:
        what_to_plot = "intensity"
    #
    if what_to_plot in ["intensity", "component"]: 
        numax = 2
        figsize = (5, 2.5)
    elif what_to_plot in ["asymmetry", "show"]: 
        numax = 1
        figsize = (2.5, 3)
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
    vmin, vmax = kwargs.get("vmin", None), kwargs.get("vmax", None)
    try: vmin, vmax = float(vmin), float(vmax)
    except: vmin, vmax = None, None
    #
    cmap = kwargs.get("cmap", None)
    if not type(cmap) is str: cmap = None
    #
    extent = [D.axis0[0], D.axis0[-1], D.axis1[-1], D.axis1[0]]
    ims = []
    #
    
    if what_to_plot in ["intensity"]:
        if type(vmin) is type(None):
            vmin, vmax = [], []
            for mp in D.intensity:
                vmin.append(mp.min()); vmax.append(mp.max())
            vmin, vmax = min(vmin), max(vmax)
        if not type(cmap) is str: cmap = "hot"
        for i in [0,1]:
            ims.append( ax[i].imshow(D.intensity[i], aspect = "auto", vmin = vmin, vmax = vmax, extent = extent, cmap = cmap) )
            ax[i].set_title(f"neg. pol {D.parameter0[0]}", fontsize = 9)
            
    elif what_to_plot in ["component"]:
        if type(vmin) is type(None):
            vmin = min([D.component_plus.min(), D.component_minus.min()])
            vmax = max([D.component_plus.max(), D.component_minus.max()])
        if not type(cmap) is str: cmap = "hot"
        ims.append( ax[0].imshow(D.component_minus, aspect = "auto", vmin = vmin, vmax = vmax, extent = extent, cmap = cmap) )
        ims.append( ax[1].imshow(D.component_plus, aspect = "auto", vmin = vmin, vmax = vmax, extent = extent, cmap = cmap) )
        ax[0].set_title(f"component MINUS", fontsize = 9)
        ax[1].set_title(f"component PLUS", fontsize = 9)
    
    elif what_to_plot in ["asymmetry"]:
        if type(vmin) is type(None):
            v = max([abs(D.asymmetry.min()), abs(D.asymmetry.max())])
            vmin, vmax = -v, v
        if not type(cmap) is str: cmap = "bwr"
        ims.append( ax[0].imshow(D.asymmetry, aspect = "auto", vmin = vmin, vmax = vmax, extent = extent, cmap = cmap) )
        ax[0].set_title(f"asymmetry", fontsize = 9)
    
    elif what_to_plot in ["show"]:
        I = (D.component_plus - D.component_minus) / (D.component_plus + D.component_minus)
        if type(vmin) is type(None):
            v = max([abs(I.min()), abs(I.max())])
            vmin, vmax = -v, v
        if not type(cmap) is str: cmap = "bwr"
        ims.append( ax[0].imshow(I, aspect = "auto", vmin = vmin, vmax = vmax, extent = extent, cmap = "bwr") )
        ax[0].set_title(f"", fontsize = 9)
    
    cbar = kwargs.get("cbar", False)
    for i, a in enumerate(ax):
        if cbar: plt.colorbar(ims[i], ax = a)
        a.set_xlabel(D.axis0_label, fontsize = 9)
        a.set_ylabel(D.axis1_label, fontsize = 9)
        a.invert_yaxis()
        
    if not type(fig) is type(None): fig.tight_layout()
    return ax



                
def _plot_data_spin_map(D = None, ax = None, **kwargs):
    """
    """
    #
    try:
        if kwargs.get("help", False):
            print(f"{Fore.BLUE}Keyword arguments:")
            print("polarity       integer       default 0, pass -1 or 1 for only positive or only negative NegativePolarity")
            print("asymmetry      bool          applicable for data from asymmetry()")
            print("mean           bool          applicable for data from asymmetry()")
            print("components     bool          applicable for data from asymmetry()")
            print("show           bool          applicable for data from asymmetry()")
            print("cbar           bool          colorbar")
            print("cmap           bool          colorbar")
            print("vmin/vmax      scalars       sometimes applicable...")
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
    show       = kwargs.get("show", False)
    if not type(asymmetry) is bool:
        print(f"{Fore.MAGENTA}The argument asymmetry must be a bool. Seeting asymmetry = False{Fore.RESET}."); asymmetry = False
    if not type(means) is bool:
        print(f"{Fore.MAGENTA}The argument means must be a bool. Seeting means = False{Fore.RESET}."); means = False
    if not type(components) is bool:
        print(f"{Fore.MAGENTA}The argument components must be a bool. Seeting components = False{Fore.RESET}."); components = False
    if not type(maps) is bool:
        print(f"{Fore.MAGENTA}The argument maps must be a bool. Seeting maps = False{Fore.RESET}."); maps = False
    if not type(show) is bool:
        print(f"{Fore.MAGENTA}The argument show must be a bool. Seeting show = False{Fore.RESET}."); show = False
    #    
    if asymmetry and not "asymmetry" in D._listAttributes(): asymmetry = False
    if components and not "component_plus" in D._listAttributes(): components = False
    if means and not "intensity_off" in D._listAttributes(): means = False
    if show and not "intensity_off" in D._listAttributes(): means = False
    if not (asymmetry or components or means or maps or show): maps = True
    
    #
    if maps or show: 
        numax = len(D.intensity)
        figsize = (numax * 2.5, 2.5)
    elif components or means: 
        numax = 2
        figsize, numax = (numax * 3, 3), 2 
    elif asymmetry or show: 
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
    cmap = kwargs.get("cmap", None)
    if not type(cmap) is str: cmap = None
    #
    vmin, vmax = kwargs.get("vmin", None), kwargs.get("vmax", None)
    try: vmin, vmax = float(vmin), float(vmax)
    except: vmin, vmax = None, None
    #
    extent = [D.axis0[0], D.axis0[-1], D.axis1[-1], D.axis1[0]]
    ims = []
    if maps:
        if type(vmin) is type(None):
            vmin, vmax = [], []
            for mp in D.intensity:
                vmin.append(mp.min()); vmax.append(mp.max())
            vmin, vmax = min(vmin), max(vmax)
        if not type(cmap) is str: cmap = "hot"
        for i, mp in enumerate(D.intensity):
            ims.append( ax[i].imshow(mp.T, aspect = "equal", vmin = vmin, vmax = vmax, extent = extent, cmap = cmap) )
            ax[i].set_title(f"map {i}, neg. pol {D.parameter0[i]}", fontsize = 9)
    #
    elif components:
        if type(vmin) is type(None):
            vmin = min([D.component_plus.min(), D.component_minus.min()])
            vmax = min([D.component_plus.max(), D.component_minus.max()])
        if not type(cmap) is str: cmap = "hot"
        ims.append( ax[0].imshow(D.component_plus.T,   aspect = "equal", vmin = vmin, vmax = vmax, extent = extent, cmap = cmap) )
        ims.append( ax[1].imshow(D.component_minus.T,  aspect = "equal", vmin = vmin, vmax = vmax, extent = extent, cmap = cmap) )  
        ax[0].set_title("component Plus", fontsize = 10)
        ax[1].set_title("component Minus", fontsize = 10)
    #
    elif means:
        if type(vmin) is type(None):
            vmin = min([D.intensity_off.min(), D.intensity_on.min()])
            vmax = min([D.intensity_off.max(), D.intensity_on.max()])
        if not type(cmap) is str: cmap = "hot"
        ims.append( ax[0].imshow(D.intensity_off.T, aspect = "equal", vmin = vmin, vmax = vmax, extent = extent, cmap = cmap) )
        ims.append( ax[1].imshow(D.intensity_on.T,  aspect = "equal", vmin = vmin, vmax = vmax, extent = extent, cmap = cmap) )
        ax[0].set_title("mean intensity Off", fontsize = 10)
        ax[1].set_title("mean intensity On", fontsize = 10)
    elif asymmetry:
        if type(vmin) is type(None):
            v = max([abs(D.asymmetry.min()), abs(D.asymmetry.max())])
            vmin, vmax = -v, v
        if not type(cmap) is str: cmap = "bwr"
        ims.append( ax[0].imshow(D.asymmetry.T, aspect = "equal", extent = extent, cmap = cmap, vmin = vmin, vmax = vmax) )
        ax[0].set_title("asymmetry", fontsize = 10)
    elif show:
        array = (D.component_plus.T - D.component_minus.T) / (D.component_plus.T + D.component_minus.T)
        if type(vmin) is type(None):
            v = max([abs(array.min()), abs(array.max())])
            vmin, vmax = -v, v
        if not type(cmap) is str: cmap = "bwr"
        ims.append( ax[0].imshow(D.component_plus.T - D.component_minus.T, aspect = "equal", extent = extent, cmap = "bwr", vmin = vmin, vmax = vmax) )
        ax[0].set_title("'show'", fontsize = 10)
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
            print("None, at the moment.")
            print(f"{Fore.RESET}")
    except: pass
    #
    if "px" in D._listAttributes() and "py" in D._listAttributes() and "pz" in D._listAttributes(): fig_type = "xyz"
    elif "px" in D._listAttributes() and "py" in D._listAttributes() and not "pz" in D._listAttributes(): fig_type = "xy"
    elif not "px" in D._listAttributes() and not "py" in D._listAttributes() and "pz" in D._listAttributes(): fig_type = "z"
    dim = 1
    if "axis1" in D._listAttributes(): 
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
        ax[1].imshow(D.pz.T, extent = extent, aspect = "equal", cmap = "bwr", vmin = -1, vmax = 1)
        
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
        
    







# ==============================================================================================================================
# ==============================================================================================================================
# ==============================================================================================================================
# ==============================================================================================================================



def _plot_data_ccd3d(D = object, ax = None, **kwargs):
    """
    """
    try:
        if kwargs.get("help", False):
            print(f"{Fore.BLUE}Arguments:")
            print("D           Data object")
            print("ax          matplotlib.axes._axes.Axes")
            print(Fore.RESET)
    except: pass
    #
    try: d_type = D.data_type
    except: d_type = "not_ccd_3d"
    if not type(d_type) is str:
        print(f"{Fore.RED}I expected a data object of type Fermi map.{Fore.RESET}"); return
    if not d_type == "ccd_3d":
        print(f"{Fore.RED}I expected a data object of type Fermi map.{Fore.RESET}"); return
    #
    ENERGY, ANGLEX, ANGLEY = D.axis2, D.axis0, D.axis1
    DE = (ENERGY[-1] - ENERGY[0]) / (len(ENERGY) -1)
    DAX = (ANGLEX[-1] - ANGLEX[0]) / (len(ANGLEX) -1)
    DAY = (ANGLEY[-1] - ANGLEY[0]) / (len(ANGLEY) -1)

    SliderE = ipw.FloatSlider(min=ENERGY[0], max=ENERGY[-1], step = DE, description = 'Energy', value = ENERGY.mean(), readout_format = ".3f")
    SliderDE = ipw.FloatSlider(min=DE, max=20*DE, step = DE, description = 'dE', value = 1*DE, readout_format = ".3f")
    SliderX = ipw.FloatSlider(min=ANGLEX[0], max=ANGLEX[-1], step = DAX, description = 'ShiftX', value = ANGLEX.mean(), readout_format = ".3f")
    SliderDX = ipw.FloatSlider(min=2*DAX, max=20*DAX, step = DAX, description = 'dX', value = 2*DAX, readout_format = ".3f")
    SliderY = ipw.FloatSlider(min=ANGLEY[0], max=ANGLEY[-1], step = DAY, description = 'ThetaY', value = ANGLEY.mean(), readout_format = ".3f")
    SliderDY = ipw.FloatSlider(min=DAY, max=20*DAY, step = DAY, description = 'dY', value = 1*DAY, readout_format = ".3f")
    extentE = [ANGLEX[0], ANGLEX[-1], ANGLEY[-1], ANGLEY[0]]
    extentX = [ANGLEY[0], ANGLEY[-1], ENERGY[-1], ENERGY[0]]
    extentY = [ANGLEX[0], ANGLEX[-1], ENERGY[-1], ENERGY[0]]

    #SliderVmin = ipw.FloatSlider(min=0, max=D.intensity.max(), step = D.intensity.max()/20, description = 'Imin', value = 0, readout_format = ".1f")
    #SliderVmax = ipw.FloatSlider(min=0, max=D.intensity.max(), step = D.intensity.max()/20, description = 'Imax', value = D.intensity.max(), readout_format = ".1f")
    
    DropdownCMAP = ipw.Dropdown(options = ["hot_r", "bone_r", "viridis", "Blues", "gnuplot2"], value = "bone_r", description = "Color map")

    box1 = ipw.HBox( [ipw.VBox([SliderE, SliderDE]), ipw.VBox([SliderX, SliderDX]), ipw.VBox([SliderY, SliderDY])])

    def plot(E, DE, X, DX, Y, DY, CMAP):
        #fig, ax = plt.subplots(ncols = 3, figsize = (9,3))
        fig, ax = plt.figure(figsize = (12,3)), []
        gs = gridspec.GridSpec(1, 13)
        ax.append(fig.add_subplot(gs[0, 0:3])) #0:2
        ax.append(fig.add_subplot(gs[0, 3:6])) #2:4
        ax.append(fig.add_subplot(gs[0, 8:11])) #5:7
        ax.append(fig.add_subplot(gs[0, 6:8]))   #4
        ax.append(fig.add_subplot(gs[0, 11:13]))   #7

        #
        Emap = fermiMapCut(D, axis = "E", E1 = E-DE/2, E2 = E+DE/2).intensity.T
        ax[0].imshow(Emap, extent = extentE, aspect = "equal", cmap = CMAP)
        Xmap = fermiMapCut(D, axis = "x", x1 = X-DX/2, x2 = X+DX/2).intensity.T
        ax[1].imshow(Xmap, extent = extentX, aspect = "auto", cmap = CMAP)
        Ymap = fermiMapCut(D, axis = "y", y1 = Y-DY/2, y2 = Y+DY/2).intensity.T
        ax[2].imshow(Ymap, extent = extentY, aspect = "auto", cmap = CMAP)
        #
        ax[0].axvline(x = X, color = "red", linewidth = 0.7, linestyle = "--")
        ax[0].axhline(y = Y, color = "red", linewidth = 0.7, linestyle = "--")
        ax[1].axhline(y = E, color = "red", linewidth = 0.7, linestyle = "--")
        ax[2].axhline(y = E, color = "red", linewidth = 0.7, linestyle = "--")
        #
        tmp = subArray(D, axis = 0, a1 = X-DX/2, a2 = X+DX/2, shup = True )
        tmp = subArray(tmp, axis = 0, a1 = X-DX/2, a2 = X+DX/2, shup = True )
        #
        for i, txt in enumerate(["X-Y", "Y-E", "X-E"]): 
            ax[i].invert_yaxis()
            ax[i].set_title(txt, fontsize = 10)
        ax[0].set_ylabel("ThetaY", fontsize = 9)
        ax[0].set_xlabel("ShiftX", fontsize = 9)
        ax[1].set_ylabel("Kinetic energy", fontsize = 9)
        ax[1].set_xlabel("ThetaY", fontsize = 9)
        ax[2].set_ylabel("Kinetic energy", fontsize = 9)
        ax[2].set_xlabel("ShiftX", fontsize = 9)
        #
        #ax[3].set_yticks([])
        #ax[4].set_yticks([])
        fig.tight_layout()
    
    Interact = ipw.interactive_output(plot, {'E': SliderE, 
                                             'DE': SliderDE, 
                                             "X": SliderX,
                                             "DX": SliderDX,
                                             "Y": SliderY,
                                             "DY": SliderDY,
                                             "CMAP": DropdownCMAP})
    
    #
    box_out = ipw.VBox([Interact, box1, DropdownCMAP])
    box_out.layout = ipw.Layout(border="solid 1px gray", margin="5px", padding="2")
    display(box_out)