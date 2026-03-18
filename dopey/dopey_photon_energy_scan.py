__version__ = "26.03.18 (prototype)"
__author__  = "Mats Leandersson"


"""
Version 26.03.05    Viewer and rudementary k-transform ready. 
Version 26.02.27    First version. 
"""

import matplotlib.pyplot as plt
import numpy as np
from ipywidgets import widgets, interact
from copy import deepcopy
from colorama import Fore, Style

try: from dopey.dopey_methods import kTransformer
except:
    try: from dopey_methods import kTransformer
    except: print(f"{Fore.RED}issue: dopey_photon_energy_scan could not import from dopey_methods.{Fore.RESET}")



def photonEnergyScan(D = object, **kwargs):
    """
    """
    DD = deepcopy(D)
    try: typ = DD.data_type
    except:
        print(f"{Fore.RED}The argument D must be Data object.{Fore.RESET}"); return DD
    if not typ == "photon_energy_scan":
        print(f"{Fore.RED}The argument D must be Data object of type 'photon_energy_scan'.{Fore.RESET}"); return DD
    #
    def image(measurement):
        n = measurement - 1
        fig, ax = plt.subplots(figsize = (3,5))
        if "__kpars" in D.__dict__:
            #intensity = DD.intensities_k[n].T
            non_energy_axis = DD.kpars[n]
            non_energy_label = "kpar"
        else:
            #intensity = DD.intensities[n].T
            non_energy_axis = DD.angle
            non_energy_label = "angle"
        extent = [non_energy_axis[0], non_energy_axis[-1], DD.binding_energy[-1], DD.binding_energy[0]]
        ims = ax.imshow(DD.intensities[n].T, extent = extent, aspect = "auto", cmap = "bone_r")
        ax.invert_yaxis()
        ax.set_title(f"Eph = {DD.photon_energy[n]:.2f}")
        ax.set_xlabel(non_energy_label, fontsize = 10)
        ax.set_ylabel("binding energy", fontsize = 10)
        fig.tight_layout()
    
    interact(image, measurement = widgets.IntSlider(min = 1, max = len(D.photon_energy) - 1, value = 1, description = "Frame:"))


def photonEnergyScanK(D = object, **kwargs):
    """
    """
    print(f"{Fore.MAGENTA}{Style.BRIGHT}Note:{Style.NORMAL} This method is unnecessary slow. It will be updated.{Fore.RESET}")
    DD = deepcopy(D)
    try: typ = DD.data_type
    except:
        print(f"{Fore.RED}The argument D must be Data object.{Fore.RESET}"); return DD
    if not typ == "photon_energy_scan":
        print(f"{Fore.RED}The argument D must be Data object of type 'photon_energy_scan'.{Fore.RESET}"); return DD
    #
    if not "__angle" in D.__dict__:
        if "__kpars" in D.__dict__:
            print(f"{Fore.MAGENTA}The data object already contains kpar values. Aborting.{Fore.RESET}"); return DD
        else:
            print(f"{Fore.RED}The data object is missing values for the the angles.{Fore.RESET}"); return DD
    #
    def kpar(Ek, a): return 0.52611 * np.sqrt(Ek - DD.work_function) * np.sin(a)
    #
    def angle(Ek, k): return np.arcsin(k/0.52611/np.sqrt(Ek-D.work_function))
    #
    INTENSITY = []
    K = []
    ANGLE = np.deg2rad(D.angle)
    #
    for iEph in range(len(D.photon_energy)):
        print(iEph)
        kpdata = kTransformer(intensity = D.intensities[iEph], ek = D.kinetic_energies[iEph], a = ANGLE, wf = D.work_function, shup = True)
        K.append(kpdata["kpar"])
        INTENSITY.append(kpdata["intensity"])
    
    #for ie in range(len(D.photon_energy)):
    #    kmin = kpar(max(DD.kinetic_energies[ie]), min(ANGLE))
    #    kmax = kpar(max(DD.kinetic_energies[ie]), max(ANGLE))
    #    K.append(np.linspace(kmin, kmax, len(ANGLE)))
    #    intensity = np.zeros(np.shape(D.intensities[ie]))*np.NaN
    #    for iek, ek in enumerate(D.kinetic_energies[ie]):
    #        for ik, k in enumerate(K[-1]):
    #            a = angle(ek, k)
    #            if a >= ANGLE.min() and a <= ANGLE.max():
    #                ia = abs(a - ANGLE).argmin()
    #                intensity[ik][iek] = D.intensities[ie][ia][iek]
    #    INTENSITY.append(intensity)
    #
    delattr(DD, "__angle")
    DD._addProperty("kpars", np.array(K))
    DD.intensities = np.array(INTENSITY)
    return DD
                 
        
    
    
    