__version__ = "25.11.07"
__author__  = "Mats Leandersson"


"""
Version 25.11.07    Added despikeSpinManual(). Works for EDC and MDC, will add Map.
Version 25.10.31    despikeSpin() works properly for EDC, but not well for MDC. Have not looked at Map yet.
Version 25.10.30    Added a de-spike method but it still not working properly.
Version 25.10.18    asymmetry(), polarization() 
Version 25.10.13    Progressing...
Version 25.10.13    The first version.
"""



import numpy as np
from copy import deepcopy
from colorama import Fore
import matplotlib.pyplot as plt

try: from dopey.dopey_constants import SHERMAN
except:
    try: from dopey_constants import SHERMAN
    except: 
        print(Fore.RED + "dopey_loader.py: coluld not import from dopey_constants.py" + Fore.RESET)
        SHERMAN = 0.29

try: from dopey.dopey_loader import _DataObject
except:
    try: from dopey_loader import _DataObject
    except:
        print(Fore.RED + "dopey_spin.py: coluld not import from dopey_loader.py" + Fore.RESET)

try: 
    import ipywidgets as ipw
    from IPython.display import display
except: print(f"{Fore.RED}{__name__} could not import the ipywidget module and/or display from IPython.display. Some methods will not work.{Fore.RESET}")
        
# Target angle:
TA = np.deg2rad(15)
    
            
        
    
    
# =================================================================    
# =================================================================    
# =================================================================    


def asymmetry(D = object, **kwargs):
    """
    """
    try:
        if kwargs.get("help", False):
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
    DD._addProperty("component_plus",  (intensity1 + intensity2) * (1 + DD.asymmetry))
    DD._addProperty("component_minus", (intensity1 + intensity2) * (1 - DD.asymmetry))
    #
    return DD
        


# =================================================================    
# =================================================================    
# ================================================================= 



def polarization(**kwargs):
    """
    """
    global SHERMAN
    try:
        if kwargs.get("help", False):
            print(f"{Fore.BLUE}Arguments needed:")
            print("  correct calculation of Px and Py                   c2rp and c2rm")
            print("  correct calculation of Px, Py, and Pz              c1rp, c1rm, c2rp, and c2rm")
            print("  correct calculation of Px and Py estimating Pz     c1rp or c2rp, c2rmp and c2rm")
            print("  estimating Pz                                      c1rp and c2rp")
            print("  estimating Pz                                      c1rp or c2rp")
            print(f"{Fore.BLUE}Keyword arguments:")
            print("  c1rp, c1rm, c2rp, c2rm                             data objects from asymmetry()")
            print(f"  sherman                                            scalar (default {SHERMAN})")
            print(Fore.RESET)
    except: pass
    #
    D = _DataObject()
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
    elif (c1rp_yeah or c1rm_yeah) and c2rp_yeah and c2rm_yeah:                # 1 coil1 measurement and two coil2 measurements
        print(f"{Fore.BLUE}I got enough data to calculate the in-plane polarization correctly ")
        print(f"and to estimate the out-of-plane polarization.{Fore.RESET}")
        case = 3
    #
    elif c1rp_yeah and c1rm_yeah and not c2rp_yeah and not c2rm_yeah:         # 2 coil1 measurements for estimating the out-of-plane P
        print(f"{Fore.BLUE}I got enough data to estimate the out-plane polarization but not to correct ")
        print(f"for the influence from a potential in-plane polarization.{Fore.RESET}")
        case = 4
    #
    elif (c1rp_yeah or c1rm_yeah) and not c2rp_yeah and not c2rm_yeah:
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
    
    D.data_type = "spin_polarization"
    
    # ------
    
    # Accurately Px,Py,Pz
    if case == 1:  
        D._addProperty("axis0", c1rp.axis0)
        D._addProperty("axis0_label", c1rp.axis0_label)
        if "map" in c1rp.data_type:
            D._addProperty("axis1", c1rp.axis1)
            D._addProperty("axis1_label", c1rp.axis1_label)
        #
        px = -(c2rp.asymmetry - c2rm.asymmetry) / np.sqrt(2.) / sherman
        py = (c2rp.asymmetry + c2rm.asymmetry) / np.sqrt(2.) / sherman
        pz = 1/np.cos(TA) * ( (c1rp.asymmetry + c1rm.asymmetry)/2/sherman - np.sin(TA)/np.sqrt(2)*px )
        D._addProperty("px", px)
        D._addProperty("py", py)
        D._addProperty("pz", pz)
        #
        
        
    # Accurately Px, Py
    elif case == 2:
        D._addProperty("axis0", c2rp.axis0)
        D._addProperty("axis0_label", c2rp.axis0_label)
        if "map" in c2rp.data_type:
            D._addProperty("axis1", c2rp.axis1)
            D._addProperty("axis1_label", c2rp.axis1_label)
        px = -(c2rp.asymmetry - c2rm.asymmetry) / np.sqrt(2.) / sherman
        py = (c2rp.asymmetry + c2rm.asymmetry) / np.sqrt(2.) / sherman
        D._addProperty("px", px)
        D._addProperty("py", py)
        #
        
        
    elif case == 3:  # Px and Py, estimating Pz with only one coil1 measurement
        if c1rp_yeah: c1 = deepcopy(c1rp)
        else: c1 = deepcopy(c1rm)
        D._addProperty("axis0", c2rp.axis0)
        D._addProperty("axis0_label", c2rp.axis0_label)
        if "map" in c2rp.data_type:
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
        if "map" in c1rp.data_type:
            D._addProperty("axis1", c1rp.axis1)
            D._addProperty("axis1_label", c1rp.axis1_label)
        pz = 1/np.cos(TA) * ( (c1rp.asymmetry + c1rm.asymmetry)/2/sherman )
        D._addProperty("pz", pz)
        
    
    elif case == 5:  # Pz with one coil1 measurements and no Px compensation
        if c1rp_yeah: c1 = deepcopy(c1rp)
        else: c1 = deepcopy(c1rm)
        D._addProperty("axis0", c1.axis0)
        D._addProperty("axis0_label", c1.axis0_label)
        if "map" in c1.data_type:
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
    #
    #polar = kwargs.get("polar", 0)
    #try: polar = float(polar)
    #except:
    #    polar = 0
    #    print(f"{Fore.MAGENTA}The argument polar must be a number. Setting it to 0.{Fore.RESET}")
    
    #if not polar == 0:
    #    polarr = np.deg2rad(polar)
    #    if case in [1,3]:
    #        p1, p2, p3 = D.pz, D.px, D.py
    #        P1 = p1 * np.cos(polarr) - p2 * np.sin(polarr)
    #        P2 = p1 * np.sin(polarr) + p2 * np.cos(polarr)
    #        P3 = p3 # not rotated by the polar angle
    #        D.px, D.py, D.pz = P2, 
    #        
    #        p1, p2, p3 = np.copy(pz), np.copy(px), np.copy(py)
    #        P1 = p1 * np.cos(angle) - p2 * np.sin(angle)
    #        P2 = p1 * np.sin(angle) + p2 * np.cos(angle)
    #        P3 = p3 # not rotated by the polar angle
    
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
        tot_int = (c1rp.intensity_off + c1rp.intensity_on + c1rm.intensity_off + c1rm.intensity_on)/4
        D._addProperty("intensity", tot_int)
        #
        D._addProperty("intensity_pz_plus", tot_int * (1 + pz))
        D._addProperty("intensity_pz_minus", tot_int * (1 - pz))
        
        
    #
    return D
            
    
    
    
# =================================================================    
# =================================================================    
# ================================================================= 

def despikeSpin(D = object, **kwargs):
    """
    """
    try:
        if kwargs.get("help", False):
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
    nstd = kwargs.get("nstd", 3)
    try: nstdv = abs(float(nstd))
    except:
        print(f"{Fore.MAGENTA}The argument nstd must be a number. Setting nstd = 3.{Fore.RESET}")
        nstd = 3
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
        parameter0 = []
        for i, curve in enumerate(D.intensity):  # only include non-excluded curves...
            if not i in exclude:
                parameter0.append(D.parameter0[i])
                if parameter0[-1] == -1: int1.append(curve)
                else: int2.append(curve)
        int1, int2 = np.array(int1).T, np.array(int2).T
        int1_, int2_ = np.copy(int1), np.copy(int2)
        #
        int1m, int2m = int1.mean(axis = 1), int2.mean(axis = 1)
        int1s, int2s = int1.std(axis = 1), int2.std(axis = 1)
        for i in range(0, len(int1)):
            for j in range(0, len(int1[i])):
                if abs(int1[i][j] - int1m[i]) > nstd * int1s[i]:
                    if  0 < i and i < len(int1)-2:  int1_[i][j] = 0.5 * (int1[i-1][j] + int1[i+1][j])
                    elif i == 0: int1_[i][j] = int1[i+1][j]
                    else: int1_[i][j] = int1[i-1][j]                            
            for j in range(0, len(int2[i])):
                if abs(int2[i][j] - int2m[i]) > nstd * int2s[i]:
                    if  0 < i and i < len(int2)-2:  int2_[i][j] = 0.5 * (int2[i-1][j] + int2[i+1][j])
                    elif i == 0: int2_[i][j] = int2[i+1][j]
                    else: int2_[i][j] = int2[i-1][j]        
        #
        intensity = []
        for curve in int1_.T: intensity.append(curve)
        for curve in int2_.T: intensity.append(curve)
        DD.intensity = np.array(intensity)
        DD.parameter0 = parameter0
    #
    elif typ == "spin_map":
        print(f"{Fore.MAGENTA}I have not yet implemented despiking for Map yet.{Fore.RESET}"); return DD
    #
    else:
        print(f"{Fore.MAGENTA}I only deal with data types spin EDC, MDC, and Map.{Fore.RESET}"); return DD
    #
    return DD
    






# =================================================================    
# =================================================================    
# ================================================================= 


def despikeSpinManual(D = object, **kwargs):
    """
    """
    print(f"{Fore.MAGENTA}Note: There's an issue with the plot being duplicated. Try to ignore it for now.{Fore.RESET}")
    try:
        if kwargs.get("help", False):
            print(f"{Fore.BLUE}Arguments needed:")
            print("  D             spin data object from .load()")
            print("Keyword arguments:")
            print("  none")
            print("Description:")
            print("  Manually remove spikes in the data. Works for spin EDC and MDC, Map will be added.")
            print("  After despiking, save the data with pickleSave(). Use pickleLoad() to load it.")
            print(Fore.RESET)
            print(f"{Fore.MAGENTA}Note: There's sometimes an issue with the plot being duplicated...{Fore.RESET}")
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
    else:
        print(f"{Fore.MAGENTA}Works for EDC and MDC, not yet Map...{Fore.RESET}"); return DD


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
                                      
    
    