__version__ = "26.02.19"
__author__  = "Mats Leandersson"


"""
version 26.02.19    .asymmetry() had to be renamed calcAsymmetry() since there is an array called asymmetry.
Version 26.02.14    All 'help' keyword arguments are now 'hlp'.
Version 26.02.10    Minor update regarding DataObject.
Version 26.01.28    Bugfix in asymmetry() and polarization().
Version 25.12.08    Bugfix in polarization(). Had forgotten to add 'spin_arpes' as data type.
Version 25.12.07    General upgrades, mostly related to spin_arpes but also other stuff.
Version 25.12.06    Adding rudimentary asymmetry for spin_arpes
Version 25.11.27    Updates after data object update.
Version 25.11.26    Updated projectSpin() so that it seems to work but keep an eye on it!
Version 25.11.25    Bugfix in polarization().
                    projectSpin() is still under construction.
Version 25.11.16    Added projectSpin(). Needs to be verified.
Version 25.11.14    despikeSinManual() works for Map as well (so EDC, MDC, and Map).
Version 25.11.07    Added despikeSpinManual(). Works for EDC and MDC, will add Map.
Version 25.10.31    despikeSpin() works properly for EDC, but not well for MDC. Have not looked at Map yet.
Version 25.10.30    Added a de-spike method but it still not working properly.
Version 25.10.18    asymmetry(), polarization() 
Version 25.10.13    Progressing...
Version 25.10.13    The first version.
"""



import numpy as np
from copy import deepcopy
from colorama import Fore, Back, Style
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

try: from dopey.dopey_constants import SHERMAN
except:
    try: from dopey_constants import SHERMAN
    except: 
        print(Fore.RED + "dopey_loader.py: coluld not import from dopey_constants.py" + Fore.RESET)
        SHERMAN = 0.29

try: from dopey_data_object import DataObject
except:
    try: from dopey.dopey_data_object import DataObject
    except:
        print(Fore.RED + "dopey_spin.py: coluld not import from dopey_data_object.py" + Fore.RESET)

try: 
    import ipywidgets as ipw
    from IPython.display import display
except: print(f"{Fore.RED}{__name__} could not import the ipywidget module and/or display from IPython.display. Some methods will not work.{Fore.RESET}")
        
# Target angle:
TA = np.deg2rad(15)
    
            
        
    
    
# =================================================================    
# =================================================================    
# =================================================================    


def calcAsymmetry(D = object, **kwargs):
    """
    This method takes a data object containing spin data (EDC, MDC, ARPES, or Map) and calculates the
    asymmeetry and distributed intensity ('component intensity'). Returns a data object.
    Accepts keyword arguments exclude (list), normp and normpn (integers)
    """
    try:
        if kwargs.get("hlp", False):
            print(f"{Fore.BLUE}Keyword arguments:")
            print( "exclude     list       list of integers (curve numbers)")
            print( "normp       integer    normalize for intensity between points normp and normpn")
            print( "normpn      integer    -''-")
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
    exclude = kwargs.get("exclude", [])
    if not type(exclude) is list:
        print(f"{Fore.RED}The argument exclude must be a list (of integers). Setting exclude = [].{Fore.RESET}"); exclude = []
    if len(exclude) > 0:
        exclude_ok = True
        for item in exclude:
            if not type(item) is int: exclude_ok = False
            else:
                if item >= len(D.parameter0): exclude_ok = False
        if not exclude_ok:
            print(f"{Fore.RED}The argument exclude must be a list of integers (in the range 0 to {len(D.parameter0)-1}). Setting exclude = [].{Fore.RESET}"); exclude = []
    #
    normp = kwargs.get("normp", 0)
    normpn = kwargs.get("normpn", 0)
    if not (type(normp) is int and type(normpn) is int):
        print(f"{Fore.RED}The arguments normp and normpn must integers. Ignoring them.{Fore.RESET}"); normp, normpn = 0, 0
    if normpn > 0:
        if normp < 0 or normp >= len(D.axis0):
            print(f"{Fore.RED}The argument normp must be in (0, {len(D.axis0)-1}). Setting normp = 0."); normp = 0   # <---
        if normpn > len(D.axis0) - normp:
            print(f"{Fore.RED}The argument normpn must be in (1, {len(D.axis0)-normp}). Setting it to default normpn = 1.{Fore.RESET}"); normpn = 1
    #
    if "edc" in typ or "mdc" in typ or "map" in typ: 
        intensity = []
        intensity1 = []     # off, i.e. -1
        intensity2 = []     # on, i.e. 1
        parameter0 = []
        for i, curve in enumerate(D.intensity):
            if not i in exclude:
                if normpn == 0: norm = 1.
                else: norm = curve[normp:normp+normpn].sum()
                intensity.append(curve/norm)
                parameter0.append(D.parameter0[i])
                if parameter0[-1] == -1: intensity1.append(curve/norm)
                else: intensity2.append(curve/norm)
        #
        intensity1, intensity2 = np.array(intensity1), np.array(intensity2)
        if len(intensity1) == 0 or len(intensity2) == 0:
            print(f"{Fore.RED}I can not calculate an asymmetry.{Fore.RESET}"); return DD    
        DD.intensity = np.array(intensity)
        DD.parameter0 = parameter0
        #
        intensity1, intensity2 = intensity1.sum(axis = 0)/np.shape(intensity1)[0], intensity2.sum(axis = 0)/np.shape(intensity2)[0]
        DD._addProperty("intensity_off", intensity1)
        DD._addProperty("intensity_on", intensity2)
        DD._addProperty("asymmetry", (intensity1-intensity2)/(intensity1+intensity2))
        #
        dims = np.shape(DD.asymmetry)
        if len(dims) == 1:
            for i in range(dims[0]):
                if np.isnan(DD.asymmetry[i]): DD.asymmetry[i] = 0
        else:
            for i in range(dims[0]):
                for j in range(dims[1]):
                    if np.isnan(DD.asymmetry[i][j]): DD.asymmetry[i][j] = 0
        #
        DD._addProperty("component_plus",  (intensity1 + intensity2) * (1 + DD.asymmetry))
        DD._addProperty("component_minus", (intensity1 + intensity2) * (1 - DD.asymmetry))
    
    elif "arpes" in typ:
        DD._addProperty("intensity_off", DD.intensity[0])
        DD._addProperty("intensity_on", DD.intensity[1])
        DD._addProperty("asymmetry", (DD.intensity_off-DD.intensity_on)/(DD.intensity_off+DD.intensity_on))
        DD._addProperty("component_plus",  (DD.intensity_off+DD.intensity_on) * (1 + DD.asymmetry))
        DD._addProperty("component_minus", (DD.intensity_off+DD.intensity_on) * (1 - DD.asymmetry))
        
    #
    return DD
        


# =================================================================    
# =================================================================    
# ================================================================= 



def polarization(**kwargs):
    """
    This method calculates Px, Py, and/or Pz from data from the asymmetry()
    method. Pass any valid combination of asymmetries from coil 1 and coil 2 
    and rotator -1 and +1 as arguments c1rp, c1rm, c2rp, and/or c2rm.
    Also accept the keyword argument sherman.
    """
    global SHERMAN
    try:
        if kwargs.get("hlp", False):
            print(f"{Fore.BLUE}Arguments needed:")
            print("  correct calculation of Px and Py                   c2rp and c2rm")
            print("  correct calculation of Px, Py, and Pz              c1rp, c1rm, c2rp, and c2rm")
            print("  correct calculation of Px and Py estimating Pz     c1rp or c2rp, c2rmp and c2rm")
            print("  estimating Pz                                      c1rp and c2rp")
            print("  estimating Pz                                      c1rp or c2rp")
            print(f"{Fore.BLUE}Keyword arguments:")
            print("  c1rp, c1rm, c2rp, c2rm                             data objects from asymmetry()")
            print(f"  sherman                                            scalar (default {SHERMAN})")
            print(f"Extra keyword arguments:")
            print("  tilt, polar, azimuth                               project lab frame to sample frame")
            print("                                                     (or use method projectSpin in a 2nd step)")
            print(Fore.RESET)
    except: pass
    #
    D = DataObject()
    D._addProperty("data_type", "none")
    #
    c1rp, c1rp_yeah = kwargs.get("c1rp", None), False
    c1rm, c1rm_yeah = kwargs.get("c1rm", None), False
    c2rp, c2rp_yeah = kwargs.get("c2rp", None), False
    c2rm, c2rm_yeah = kwargs.get("c2rm", None), False
    try: _, c1rp_yeah = c1rp.asymmetry, True
    except:  c1rp, c1rp_yeah = None, False
    try: _, c1rm_yeah = c1rm.asymmetry, True
    except: c1rm, c1rm_yeah = None, False
    try: _, c2rp_yeah = c2rp.asymmetry, True
    except: c2rp, c2rp_yeah = None, False
    try: _, c2rm_yeah = c2rm.asymmetry, True
    except: c2rm, c2rm_yeah = None, False
    #
    sherman = kwargs.get("sherman", SHERMAN)
    try: sherman = abs(float(sherman))
    except:
        sherman = SHERMAN
        print(f"{Fore.MAGENTA}The argument sherman must be a number. Setting sherman = {sherman}.{Fore.RESET}")
    #
    # cases
    # all-in
    if c1rp_yeah and c1rm_yeah and c2rp_yeah and c2rm_yeah:                 # 4 sets of data to calculate Px,Py,Pz accurately
        print(f"{Fore.BLUE}I got enough data to calculate all polarization components correctly.{Fore.RESET}")
        case = 1
    #
    elif not c1rp_yeah and not c1rm_yeah and c2rp_yeah and c2rm_yeah:       # 2 sets of data to calculate Px,Py accurately
        print(f"{Fore.BLUE}I got enough data to calculate the in-plane polarization correctly.{Fore.RESET}")
        case = 2
    #
    elif (c1rp_yeah ^ c1rm_yeah) and c2rp_yeah and c2rm_yeah:                # 1 coil1 measurement and two coil2 measurements
        print(f"{Fore.BLUE}I got enough data to calculate the in-plane polarization correctly ")
        print(f"and to estimate the out-of-plane polarization.{Fore.RESET}")
        case = 3
    #
    elif c1rp_yeah and c1rm_yeah and not c2rp_yeah and not c2rm_yeah:         # 2 coil1 measurements for estimating the out-of-plane P
        print(f"{Fore.BLUE}I got enough data to estimate the out-plane polarization but not to correct ")
        print(f"for the influence from a potential in-plane polarization.{Fore.RESET}")
        case = 4
    #
    elif (c1rp_yeah ^ c1rm_yeah) and not c2rp_yeah and not c2rm_yeah:   # ^ = xor
        print(f"{Fore.BLUE}I got enough data to roughly estimate the out-plane polarization but not to correct ")
        print(f"for the influence from a potential in-plane polarization.{Fore.RESET}")
        case = 5        
    #
    elif (c1rp_yeah or c1rm_yeah) and (c2rp_yeah or c2rm_yeah):
        print(f"{Fore.MAGENTA}I got a confusing set of data. Aborting.{Fore.RESET}")
        return D
    else:
        print(f"{Fore.RED}I did not get enough data to calculate anything at all.{Fore.RESET}")
        return D
    #
    D.data_type = "spin_polarization"
    
    # ------
    
    # Accurately Px,Py,Pz
    if case == 1:  
        D._addProperty("axis0", c1rp.axis0)
        D._addProperty("axis0_label", c1rp.axis0_label)
        if "map" in c1rp.data_type or "arpes" in c1rp.data_type:
            D._addProperty("axis1", c1rp.axis1)
            D._addProperty("axis1_label", c1rp.axis1_label)
        #
        px = -(c2rp.asymmetry - c2rm.asymmetry) / np.sqrt(2.) / sherman
        py = (c2rp.asymmetry + c2rm.asymmetry) / np.sqrt(2.) / sherman
        pz = 1/np.cos(TA) * ( (c1rp.asymmetry + c1rm.asymmetry)/2/sherman - np.sin(TA)/np.sqrt(2)*px )
        D._addProperty("px", px)
        D._addProperty("py", py)
        D._addProperty("pz", pz)
        
    # Accurately Px, Py
    elif case == 2:
        D._addProperty("axis0", c2rp.axis0)
        D._addProperty("axis0_label", c2rp.axis0_label)
        if "map" in c2rp.data_type or "arpes" in c2rp.data_type:
            D._addProperty("axis1", c2rp.axis1)
            D._addProperty("axis1_label", c2rp.axis1_label)
        px = -(c2rp.asymmetry - c2rm.asymmetry) / np.sqrt(2.) / sherman
        py = (c2rp.asymmetry + c2rm.asymmetry) / np.sqrt(2.) / sherman
        D._addProperty("px", px)
        D._addProperty("py", py)
        
    elif case == 3:  # Px and Py, estimating Pz with only one coil1 measurement
        if c1rp_yeah: c1 = deepcopy(c1rp)
        else: c1 = deepcopy(c1rm)
        D._addProperty("axis0", c2rp.axis0)
        D._addProperty("axis0_label", c2rp.axis0_label)
        if "map" in c2rp.data_type or "arpes" in c1rp.data_type:
            D._addProperty("axis1", c2rp.axis1)
            D._addProperty("axis1_label", c2rp.axis1_label)
        px = -(c2rp.asymmetry - c2rm.asymmetry) / np.sqrt(2.) / sherman
        py = (c2rp.asymmetry + c2rm.asymmetry) / np.sqrt(2.) / sherman
        pz = 1/np.cos(TA) * ( c1.asymmetry/sherman - np.sin(TA)/np.sqrt(2)*px )
        D._addProperty("px", px)
        D._addProperty("py", py)
        D._addProperty("pz", pz)
        
    elif case == 4:  # Pz with two coil1 measurements but no Px compensation
        D._addProperty("axis0", c1rp.axis0)
        D._addProperty("axis0_label", c1rp.axis0_label)
        if "map" in c1rp.data_type or "arpes" in c1rp.data_type:
            D._addProperty("axis1", c1rp.axis1)
            D._addProperty("axis1_label", c1rp.axis1_label)
        pz = 1/np.cos(TA) * ( (c1rp.asymmetry + c1rm.asymmetry)/2/sherman )
        D._addProperty("pz", pz)
        
    elif case == 5:  # Pz with one coil1 measurements and no Px compensation
        if c1rp_yeah: c1 = deepcopy(c1rp)
        else: c1 = deepcopy(c1rm)
        D._addProperty("axis0", c1.axis0)
        D._addProperty("axis0_label", c1.axis0_label)
        if "map" in c1.data_type or "arpes" in c1rp.data_type:
            D._addProperty("axis1", c1.axis1)
            D._addProperty("axis1_label", c1.axis1_label)
        pz = 1/np.cos(TA) * ( c1.asymmetry/sherman )
        D._addProperty("pz", pz)
        #
        tot_int = (c1.intensity_off + c1.intensity_on)/2
        D._addProperty("intensity", tot_int)
        #
        D._addProperty("intensity_pz_plus", tot_int * (1 + pz))
        D._addProperty("intensity_pz_minus", tot_int * (1 - pz))
    
    else:
        print(f"{Fore.MAGENTA}Something went wrong. Probably sloppy coding.{Fore.RESET}")
        return None
    
    if case == 1:
        tot_int = c1rp.intensity_off + c1rp.intensity_on
        for intensity in [c1rm, c2rp, c2rm]:
            tot_int += intensity.intensity_off + intensity.intensity_on
        tot_int /= 8
        D._addProperty("intensity", tot_int)
        #
        D._addProperty("intensity_px_plus", tot_int * (1 + px))
        D._addProperty("intensity_px_minus", tot_int * (1 - px))
        D._addProperty("intensity_py_plus", tot_int * (1 + py))
        D._addProperty("intensity_py_minus", tot_int * (1 - py))
        D._addProperty("intensity_pz_plus", tot_int * (1 + pz))
        D._addProperty("intensity_pz_minus", tot_int * (1 - pz))
    elif case == 2:
        tot_int = (c2rp.intensity_off + c2rp.intensity_on + c2rm.intensity_off + c2rm.intensity_on)/4
        D._addProperty("intensity", tot_int)
        #
        D._addProperty("intensity_px_plus", tot_int * (1 + px))
        D._addProperty("intensity_px_minus", tot_int * (1 - px))
        D._addProperty("intensity_py_plus", tot_int * (1 + py))
        D._addProperty("intensity_py_minus", tot_int * (1 - py))
    elif case == 3:
        tot_int = c1.intensity_off + c1.intensity_on
        for intensity in [c2rp, c2rm]:
            tot_int += intensity.intensity_off + intensity.intensity_on
        tot_int /= 6
        D._addProperty("intensity", tot_int)
        #
        D._addProperty("intensity_px_plus", tot_int * (1 + px))
        D._addProperty("intensity_px_minus", tot_int * (1 - px))
        D._addProperty("intensity_py_plus", tot_int * (1 + py))
        D._addProperty("intensity_py_minus", tot_int * (1 - py))
        D._addProperty("intensity_pz_plus", tot_int * (1 + pz))
        D._addProperty("intensity_pz_minus", tot_int * (1 - pz))
    elif case == 4:
        tot_int = (c1rp.intensity_off + c1rp.intensity_on + c1rm.intensity_off + c1rm.intensity_on)/4
        D._addProperty("intensity", tot_int)
        #
        D._addProperty("intensity_pz_plus", tot_int * (1 + pz))
        D._addProperty("intensity_pz_minus", tot_int * (1 - pz))
    elif case == 5:
        if c1rp_yeah: tot_int = (c1rp.intensity_off + c1rp.intensity_on)/2
        else: tot_int = (c1rm.intensity_off + c1rm.intensity_on)/2
        D._addProperty("intensity", tot_int)
        #
        D._addProperty("intensity_pz_plus", tot_int * (1 + pz))
        D._addProperty("intensity_pz_minus", tot_int * (1 - pz))
    #
    # ---
    #
    tilt,  polar, azimuth = kwargs.get("tilt", 0.), kwargs.get("polar", 0.), kwargs.get("azimuth", 0)
    try: tilt = float(tilt)
    except:
        print(f"{Fore.RED}Argument tilt must be a number. Setting tilt = 0.{Fore.RESET}"); tilt = 0.
    try: polar = float(polar)
    except:
        print(f"{Fore.RED}Argument polar must be a number. Setting polar = 0.{Fore.RESET}"); polar = 0.
    try: azimuth = float(azimuth)
    except:
        print(f"{Fore.RED}Argument tilt azimuth be a number. Setting azimuth = 0.{Fore.RESET}"); azimuth = 0.
    if not (tilt == 0 and polar == 0 and azimuth == 0):
        print(f"{Fore.BLUE}A value or values for tilt, polar, and/or azimuth is/are non-zero")
        print(f"so I'm calling the projectSpin() method.{Fore.RESET}")
        D = projectSpin(D = D, tilt = tilt, polar = polar, azimuth = azimuth)
    # ---
    return D
            




# ==================================================================================================================
# ==================================================================================================================
# ==================================================================================================================



def projectSpin(D = object, tilt = 0, polar = 0, azimuth = 0, **kwargs):
    """
    This method is used to project the calculated spin (lab frame) on to the sample. Use when the
    sample is in off-normal position.
    Pass the output from the polarization() method plus arguments tilt, polar, and azimuth.
    Returns a data object.
    """
    print(f"\n{Fore.MAGENTA}projectSpin(): I'm in development. {Style.BRIGHT}Verify that the output make sense.{Style.RESET_ALL} Data type spin_arpes throws an error.{Fore.RESET}\n")
    #
    DD = deepcopy(D)
    #
    try: typ = DD.data_type
    except:
        print(f"{Fore.RED}The argument D must be Data object.{Fore.RESET}"); return DD
    #
    if not "spin_polarization" in typ:
        print(f"{Fore.RED}The argument D must be Data object from polarization().{Fore.RESET}"); return DD
    # -----------------------------------
    existingAttributes = DD._listAttributes()
    if "px" in existingAttributes and "py" in existingAttributes and "pz" in existingAttributes: case = "xyz"
    elif "px" in existingAttributes and "py" in existingAttributes and not "pz" in existingAttributes: case = "xy"
    elif "pz" in existingAttributes: case = "z"
    else:
        print(f"{Fore.RED}Something went wrong.{Fore.RESET}"); return DD
    if case == "xyz":
        print(f"{Fore.BLUE}The data contains values for Px, Py, and Pz (assuming lab frame).\nThese values will be projected onto the sample surface.{Fore.RESET}")
    elif case == "xy":
        print(f"{Fore.BLUE}The data contains values for Px and Py (assuming lab frame).\These values will be projected onto the sample surface,\n while assuming that there is no Pz in the sample.{Fore.RESET}")
    elif case == "z":
        print(f"{Fore.BLUE}The data contains values for Pz (assuming lab frame).\These values will be projected onto the sample surface,\n while assuming that there is no Px or Py in the sample.{Fore.RESET}")

    # -----------------------------------
    if "axis0" in existingAttributes and not "axis1" in existingAttributes: dim = 1
    elif "axis0" in existingAttributes and "axis1" in existingAttributes: dim = 2
    else:
        print(f"{Fore.RED}Something went wrong.{Fore.RESET}"); return DD
    #
    try: tilt, polar, azimuth = float(tilt), float(polar), float(azimuth)
    except:
        print(f"{Fore.RED}The arguments tilt, polar, and azimuth must be scalars (deg.).{Fore.RESET}"); return DD
    if not azimuth == 0:
        azimuth = 0
        print(f"{Fore.MAGENTA}For the moment, for various reasons, I have disabled the azimuth. Setting azimuth = 0.{Fore.RESET}")
    #
    # -----
    # u and are the vectors defining the sample in normal emission
    u, v = np.array([1.,0.,0.]), np.array([0.,1.,0.])
    # uu and vv are the vectors defining the sample after rotation(s)
    uu, vv = rotX(tilt).dot(u),     rotX(tilt).dot(v)     # tilt
    uu, vv = rotY(polar).dot(uu),   rotY(polar).dot(vv)   # polar
    uu, vv = rotZ(azimuth).dot(uu), rotZ(azimuth).dot(vv) # azimuth
    # ww is the sample normal after rotation
    ww = np.cross(uu, vv)
    # 
    #
    if case == "xyz" :
        if dim == 1:
            px = np.zeros([len(DD.axis0)]); py, pz = np.copy(px), np.copy(px)
            for i in range(len(DD.axis0)):
                p = np.array([D.px[i], D.py[i], D.pz[i]])           # p-vector in on point (Ek or deflector)
                px_ = projAonB(a = p, b = uu)   # projection to sample-x
                py_ = projAonB(a = p, b = vv)   # projection to sample-y
                pz_ = projAonB(a = p, b = ww)   # projection to sample-z
                px[i] = np.linalg.norm( px_ ) * np.sign(px_[0])  # the size and sign.  ### IS THIS CORRECT??? ###
                py[i] = np.linalg.norm( py_ ) * np.sign(py_[1]) 
                pz[i] = np.linalg.norm( pz_ ) * np.sign(pz_[2]) 
        elif dim == 2:
            px = np.zeros([len(DD.axis0), len(DD.axis1)]); py, pz = np.copy(px), np.copy(px)
            for i in range(len(DD.axis0)):
                for j in range(DD.axis1):
                    p = np.array([D.px[i,j], D.py[i,j], D.pz[i,j]])
                    px[i,j] = projAonB(a = p, b = uu)
                    py[i,j] = projAonB(a = p, b = vv) 
                    pz[i,j] = projAonB(a = p, b = ww) 
                    px[i,j] = np.linalg.norm( px[i,j] ) * np.sign(px[i,j,0])  ### IS THIS CORRECT??? ###
                    py[i,j] = np.linalg.norm( py[i,j] ) * np.sign(py[i,j,1])
                    pz[i,j] = np.linalg.norm( pz[i,j] ) * np.sign(pz[i,j,2])
        DD.px, DD.py, DD.pz = px, py, pz
        DD.intensity_px_plus =  D.intensity * (1+px)
        DD.intensity_px_minus = D.intensity * (1-px)
        DD.intensity_py_plus =  D.intensity * (1+py)
        DD.intensity_py_minus = D.intensity * (1-py)
        DD.intensity_pz_plus =  D.intensity * (1+pz)
        DD.intensity_pz_minus = D.intensity * (1-pz)
    #
    elif case == "xy":
        # In this case, the user has chosen to not measure Pz, assuming that it is zero in the sample.
        # The projections (x and y) onto the sample are thus
        DD.px /= np.cos(np.deg2rad(polar))
        DD.py /= np.cos(np.deg2rad(tilt))
        DD.intensity_px_plus =  D.intensity * (1+DD.px)
        DD.intensity_px_minus = D.intensity * (1-DD.px)
        DD.intensity_py_plus =  D.intensity * (1+DD.py)
        DD.intensity_py_minus = D.intensity * (1-DD.py)
    #
    elif case == "z":
        # In this case, the user has chosen to only measure Pz, assuming that Px and Py are zero in the sample.
        # The projection of Pz onto the sample is thus
        DD.pz = DD.pz / np.cos(np.deg2rad(polar)) / np.cos(np.deg2rad(tilt))
        DD.intensity_pz_plus =  D.intensity * (1+DD.pz)
        DD.intensity_pz_minus = D.intensity * (1-DD.pz)
    #
    return DD




def rotX(angle = 0):
    """
    Returns a rotation matrix (around the x-axis). Argument angle in deg.
    """
    try: angler = np.deg2rad(angle)
    except:
        print(f"{Fore.RED}The attribute angle must be a number (deg.).")
        return np.array([1,0,0],[0,1,0],[0,0,1])
    return np.array([[1, 0,               0],
                     [0, np.cos(angler), -np.sin(angler)],
                     [0, np.sin(angler),  np.cos(angler)]])

def rotY(angle = 0):
    """
    Returns a rotation matrix (around the y-axis). Argument angle in deg.
    """
    try: angler = np.deg2rad(angle)
    except:
        print(f"{Fore.RED}The attribute angle must be a number (deg.).")
        return np.array([1,0,0],[0,1,0],[0,0,1])
    return np.array([[ np.cos(angler), 0,  np.sin(angler)],
                     [ 0,              1,  0],
                     [-np.sin(angler), 0,  np.cos(angler)]])
    
def rotZ(angle = 0):
    """
    Returns a rotation matrix (around the z-axis). Argument angle in deg.
    """
    try: angler = np.deg2rad(angle)
    except:
        print(f"{Fore.RED}The attribute angle must be a number (deg.).")
        return np.array([1,0,0],[0,1,0],[0,0,1])
    return np.array([[ np.cos(angler), -np.sin(angler), 0],
                     [ np.sin(angler),  np.cos(angler), 0],
                     [ 0,               0,              1]])
        
        
def projAonB(a = np.array([1,0,0]), b = np.array([0,0,1])):
    """
    Returns the projection of vector a on vector b.
    Arguments a and b must be vectors of size 3.
    """
    try: a, b = np.array(a), np.array(b)
    except:
        print(f"{Fore.RED}The attributes a and b must be vectores of size 3."); return np.array([0,0,0])
    if not len(a) == 3 and len(b) == 3:
        print(f"{Fore.RED}The attributes a and b must be vectores of size 3."); return np.array([0,0,0])
    return a.dot(b) / b.dot(b) * b
    
    




    
    
# ==================================================================================================================
# ==================================================================================================================
# ==================================================================================================================


def despikeSpin(D = object, **kwargs):
    """
    """
    try:
        if kwargs.get("hlp", False):
            print(f"{Fore.BLUE}Arguments needed:")
            print("  D             spin data object from .load()")
            print("Keyword arguments:")
            print("  exclude       list of curves to exclude")
            print("  nstd          number")
            print("Description:")
            print("  If the intensity in one point is nstd times higher than the standard deviation")
            print("  it will be replaced by the average value of the neighbouring points.")
            print("  Curves from NegativePolarity ON and OFF are treated seperately.")
            print(Fore.RESET)
    except: pass
    #
    DD = deepcopy(D)
    #
    try: typ = DD.data_type
    except:
        print(f"{Fore.RED}The argument D must be Data object.{Fore.RESET}"); return DD
    #
    if not "spin" in typ:
        print(f"{Fore.RED}The argument D must be Data object containing (sorted!) spin data.{Fore.RESET}"); return DD
    #
    n_std_p = kwargs.get("n_std_p", 2)
    n_std_n = kwargs.get("n_std_n", 2)
    try: n_std_p, n_std_n = float(n_std_p), float(n_std_n)
    except:
        n_std_p, n_std_n = 2., 2.
        print(f"{Fore.MAGENTA}The arguments n_std_p and n_std_n must be numbers. Setting n_std_p = n_std_n = 2.{Fore.RESET}")
    #
    exclude = kwargs.get("exclude", [])
    if not type(exclude) is list:
        print(f"{Fore.MAGENTA}The argument exclude must be a list (of integers). Setting exclude = [].{Fore.RESET}"); exclude = []
    if len(exclude) > 0:
        exclude_ok = True
        for item in exclude:
            if not type(item) is int: exclude_ok = False
            else:
                if item >= len(D.parameter0): exclude_ok = False
        if not exclude_ok:
            print(f"{Fore.MAGENTA}The argument exclude must be a list of integers (in the range 0 to {len(D.parameter0)-1}). Setting exclude = [].{Fore.RESET}"); exclude = []
    #
    if typ in ["spin_edc", "spin_mdc"]:
        #
        if "mdc" in typ: print(f"{Fore.MAGENTA}(I have issues with despiking MDC data which I'm still working on.){Fore.RESET}")
        #
        int1 = []     # off, i.e. -1
        int2 = []     # on, i.e. 1
        parameter0_1 = []
        parameter0_2 = []
        for i, curve in enumerate(D.intensity):  # only include non-excluded curves...
            if not i in exclude:
                if D.parameter0[i] == -1: 
                    int1.append(curve); parameter0_1.append(-1)
                else: 
                    int2.append(curve); parameter0_2.append(1)
        int1, int2 = np.array(int1).T, np.array(int2).T
        int1_, int2_ = np.copy(int1), np.copy(int2)
        #
        int1m, int2m = int1.mean(axis = 1), int2.mean(axis = 1)
        int1s, int2s = int1.std(axis = 1), int2.std(axis = 1)
        for i in range(0, len(int1)):
            for j in range(0, len(int1[i])):
                if abs(int1[i][j] - int1m[i]) > n_std_n * int1s[i]:
                    if  0 < i and i < len(int1)-2:  int1_[i][j] = 0.5 * (int1[i-1][j] + int1[i+1][j])
                    elif i == 0: int1_[i][j] = int1[i+1][j]
                    else: int1_[i][j] = int1[i-1][j]                            
            for j in range(0, len(int2[i])):
                if abs(int2[i][j] - int2m[i]) > n_std_p * int2s[i]:
                    if  0 < i and i < len(int2)-2:  int2_[i][j] = 0.5 * (int2[i-1][j] + int2[i+1][j])
                    elif i == 0: int2_[i][j] = int2[i+1][j]
                    else: int2_[i][j] = int2[i-1][j]        
        #
        intensity = []
        for curve in int1_.T: intensity.append(curve)
        for curve in int2_.T: intensity.append(curve)
        DD.intensity = np.array(intensity)
        DD.parameter0 = np.concatenate([parameter0_1, parameter0_2])
    #
    elif typ == "spin_map":
        #
        int1 = []     # off, i.e. -1
        int2 = []     # on, i.e. 1
        parameter0_1 = []
        parameter0_2 = []
        for i, map in enumerate(D.intensity):  # only include non-excluded curves...
            if not i in exclude:
                if D.parameter0[i] == -1:
                    int1.append(map); parameter0_1.append(-1)
                else: 
                    int2.append(map); parameter0_2.append(1)
        int1, int2 = np.array(int1), np.array(int2)
        int1_, int2_ = np.copy(int1), np.copy(int2)
        #
        int1m, int2m = int1.mean(axis = 0), int2.mean(axis = 0)
        int1s, int2s = int1.std(axis = 0), int2.std(axis = 0)
        debug = kwargs.get("debug", False)
        if debug:
            fig, ax = plt.subplots(nrows = 2, ncols = 2, figsize = (6,6))
            ims = ax[0][0].imshow(int1m.T); plt.colorbar(ims)
            ims = ax[1][0].imshow(int2m.T); plt.colorbar(ims)
            ims = ax[0][1].imshow(int1s.T); plt.colorbar(ims)
            ims = ax[1][1].imshow(int2s.T); plt.colorbar(ims)
            fig.tight_layout()
        #
        c,cc = 0,0
        shp = np.shape(int1)
        for i in range(0,shp[1]):
            for j in range(0,shp[2]):
                for k in range(0,shp[0]):
                    c+=1
                    if abs(int1[k][i][j] - int1m[i][j]) > n_std_n * int1s[i][j]:
                        cc+=1
                        int1_[k][i][j] = 0
        print(f"{c = }, {cc = }")
        #
        c,cc = 0,0
        shp = np.shape(int2)
        for i in range(0,shp[1]):
            for j in range(0,shp[2]):
                for k in range(0,shp[0]):
                    c+=1
                    if abs(int2[k][i][j] - int2m[i][j]) > n_std_p * int2s[i][j]:
                        cc+=1
                        int2_[k][i][j] = 0
        print(f"{c = }, {cc = }")
        #
        intensity = []
        for map in int1_: intensity.append(map)
        for map in int2_: intensity.append(map)
        DD.intensity = np.array(intensity)
        DD.parameter0 = np.concatenate([parameter0_1, parameter0_2])
                    
    #
    else:
        print(f"{Fore.MAGENTA}I only deal with data types spin EDC, MDC, and Map.{Fore.RESET}"); return DD
    #
    return DD
    






# ==================================================================================================================
# ==================================================================================================================
# ==================================================================================================================


def despikeSpinManual(D = object, **kwargs):
    """
    """
    print(f"{Fore.MAGENTA}Note: There's occationally an issue with the plot being duplicated. Try to ignore it for now.{Fore.RESET}")
    try:
        if kwargs.get("hlp", False):
            print(f"{Fore.BLUE}Arguments needed:")
            print("  D             spin data object from .load()")
            print("Keyword arguments:")
            print("  none")
            print("Description:")
            print("  Manually remove spikes in the data. Works for spin EDC, MDC, and Map.")
            print("  After despiking, save the data with pickleSave(). Use pickleLoad() to load it.")
            print(Fore.RESET)
    except: pass
    #
    DD = deepcopy(D)
    #
    try: typ = DD.data_type
    except:
        print(f"{Fore.RED}The argument D must be Data object.{Fore.RESET}"); return DD
    #
    if not "spin" in typ:
        print(f"{Fore.RED}The argument D must be Data object containing (sorted!) spin data.{Fore.RESET}"); return DD
    #
    if "edc" in typ:  _despikeSpinManualEDC(D = D, **kwargs)
    elif "mdc" in typ:  _despikeSpinManualEDC(D = D, **kwargs)
    elif "map" in typ: _despikeSpinManualMap(D = D, **kwargs)
    else:
        print(f"{Fore.MAGENTA}Works for EDC, MDC, and Map...{Fore.RESET}"); return DD


def _despikeSpinManualEDC(D = object, **kwargs):
    """
    """
    DD = deepcopy(D)
    num_curves = len(D.intensity)-1
    num_points = len(D.intensity.T)-1
    Slider_curve = ipw.IntSlider(min=0, max=num_curves, step = 1, description = 'Curve', value = 0)
    Slider_point = ipw.IntSlider(min=0, max=num_points, step = 1, description = 'Point', value = 0)
    Slider_intensity = ipw.IntSlider(min=0, max=200, step = 1, description = 'Int.', value = 100)
    
    Button_next = ipw.Button(description = "Next")
    def on_button_clicked(b):
        Slider_point.value = 0
        Slider_intensity.value = 100
    Button_next.on_click(on_button_clicked)
    
    Button_done = ipw.Button(description = "Done")
    def on_button_clicked2(b):
        Slider_curve.disabled = True
        Slider_point.disabled = True
        Slider_intensity.disabled = True
        Button_next.disabled = True
        Button_done.disabled = True
    Button_done.on_click(on_button_clicked2)
    
    def plot(CURVE, POINT, INTENSITY):
        fig, ax = plt.subplots(figsize = (6,3))
        if not INTENSITY == 100: disabled = True
        else: disabled = False 
        Slider_curve.disabled = disabled
        Slider_point.disabled = disabled
        #
        D.intensity[CURVE][POINT] = INTENSITY/100 * DD.intensity[CURVE][POINT]
        ax.plot(D.axis0, DD.intensity[CURVE], linewidth = 0.6, linestyle = "--", color = "blue")
        ax.plot(D.axis0, D.intensity[CURVE], linewidth = 0.6, linestyle = "-", color = "red")
        ax.axvline(x = D.axis0[POINT], linewidth = 0.6, linestyle = ":", color = "k")
        ax.scatter(D.axis0[POINT], D.intensity[CURVE][POINT], marker = "x", color = "red")
        ax.set_title(f"curve {CURVE}, polarity {D.parameter0[CURVE]}", fontsize = 10)
        fig.tight_layout()
        
    Interact = ipw.interactive_output(plot, {'CURVE': Slider_curve, 
                                             'POINT': Slider_point,
                                             'INTENSITY': Slider_intensity})
    
    widget_box = ipw.VBox([Slider_curve, Slider_point, Slider_intensity, Button_next, Button_done])
    box_out = ipw.HBox([Interact, widget_box])
    box_out.layout = ipw.Layout(border="solid 1px gray", margin="5px", padding="2")
    display(box_out)
                                      
    


def _despikeSpinManualMap(D = object, **kwargs):
    """
    """
    #   
    DD = deepcopy(D)
    #
    cmap = kwargs.get("cmap", "rainbow")
    figsize = kwargs.get("figsize", (8,3))
    #
    num_maps = len(D.intensity)-1
    num_defl1 = len(D.axis0)-1
    num_defl2 = len(D.axis1)-1
    Slider_map = ipw.IntSlider(min=0, max=num_maps, step = 1, description = 'Map', value = 0)
    Slider_defl1 = ipw.IntSlider(min=0, max=num_defl1, step = 1, description = f'defl1', value = 0)
    Slider_defl2 = ipw.IntSlider(min=0, max=num_defl2, step = 1, description = f'defl2', value = 0)
    Slider_intensity = ipw.IntSlider(min=0, max=200, step = 1, description = 'Intensity', value = 100)
    
    Button_next = ipw.Button(description = "Next")
    def on_button_clicked(b):
        Slider_defl1.value = 0
        Slider_defl2.value = 0
        Slider_intensity.value = 100
    Button_next.on_click(on_button_clicked)
    
    Button_done = ipw.Button(description = "Done")
    def on_button_clicked2(b):
        Slider_map.disabled = True
        Slider_defl1.disabled = True
        Slider_defl2.disabled = True
        Slider_intensity.disabled = True
        Button_next.disabled = True
        Button_done.disabled = True
    Button_done.on_click(on_button_clicked2)
    
    def plot(MAP, DEFL1, DEFL2, INTENSITY):
        fig, ax = plt.figure(figsize = figsize), []
        gs = gridspec.GridSpec(2, 3)
        ax.append(fig.add_subplot(gs[0:2, 0]))
        ax.append(fig.add_subplot(gs[0:2, 1]))
        ax.append(fig.add_subplot(gs[0, 2]))
        ax.append(fig.add_subplot(gs[1, 2]))
        
        if not INTENSITY == 100: disabled = True
        else: disabled = False 
        Slider_map.disabled = disabled
        Slider_defl1.disabled = disabled
        Slider_defl1.disabled = disabled
        #
        D.intensity[MAP][DEFL1][DEFL2] = INTENSITY/100 * DD.intensity[MAP][DEFL1][DEFL2]
        ims0 = ax[0].imshow(DD.intensity[MAP].T, cmap = cmap, aspect = "auto")
        ims1 = ax[1].imshow(D.intensity[MAP].T,  cmap = cmap, aspect = "auto")
        for i in [0,1]:
            ax[i].axhline(y = DEFL2, linewidth = 0.75, linestyle = "-", color = "blue")
            ax[i].axvline(x = DEFL1, linewidth = 0.75, linestyle = "-", color = "red")
        ax[2].plot(D.intensity[MAP].T[DEFL2], color = "blue", linewidth = 0.75)
        ax[3].plot(D.intensity[MAP][DEFL1],   color = "red",  linewidth = 0.75)
        for i in [2,3]: ax[i].set_yticks([])
        ax[2].axvline(x = DEFL1, linewidth = 0.75, color = "k")
        ax[3].axvline(x = DEFL2, linewidth = 0.75, color = "k")
        
        for i, txt in enumerate(["original", "edited", "horizontal profile", "vertical profile"]): ax[i].set_title(txt, fontsize = 9)
        fig.tight_layout()
        
    Interact = ipw.interactive_output(plot, {'MAP': Slider_map, 
                                             'DEFL1': Slider_defl1,
                                             'DEFL2': Slider_defl2,
                                             'INTENSITY': Slider_intensity})
    
    widget_box = ipw.VBox([Slider_map, Slider_defl1, Slider_defl2, Slider_intensity, Button_next, Button_done])
    box_out = ipw.HBox([Interact, widget_box])
    box_out.layout = ipw.Layout(border="solid 1px gray", margin="5px", padding="2")
    display(box_out)
    
    