__version__ = "26.03.14"
__author__  = "Mats Leandersson"


"""
Version 26.03.06    Added kTransformFermiCut().
                    Added from3dslim() to pull out 1d or 2d data from data type from3d.
Version 26.03.05    Added a rudimetary method k-transform kTransformer() method that accepts arrays.
                    Added kTransformARPES() that accepts ARPES data, using kTransformer().
Version 26.02.25    Unimportant update reladed to the hlp keyword arguments. 
Version 26.02.14    All 'help' keyword arguments are now 'hlp'.
Version 26.02.03    Updated compact(). Now handles ccd_2d and ccd3d.
Version 25.11.25    A very, very minor change. Barely worth mentioning.
Version 25.10.20    Added method align(fermi map).
Version 25.10.08    The first version.
"""


import numpy as np
from copy import deepcopy
from colorama import Fore
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon, Circle, Ellipse, Rectangle

try: 
    import ipywidgets as ipw
    from IPython.display import display
except: 
    print(Fore.RED + f'issue: dopey_methods could not import the ipywidget module and/or display from IPython.display.') 
    print('       Interactive plots will not work.' + Fore.RESET)

try: from dopey.dopey_constants import WORKFUNCTION
except:
    try: from dopey_constants import WORKFUNCTION
    except: print(f"{Fore.RED}issue: dopey_methods could not import from dopey_constants.{Fore.RESET}")

try: from dopey.dopey_data_object import DataObject
except:
    try: from dopey_data_object import DataObject
    except: print(f"{Fore.RED}issue: dopey_methods could not import from dopey_data_object.{Fore.RESET}")




def subArray(D = object, axis = -1, **kwargs):
    """
    Returns a sub section of the data in a dopey data object.
    
    Arguments:
        D           dopey data object
        axis        integer             what axis to cut (can e.g. be 0 or 1 for 2d data,...)
    Keyword arguments:
        i1,i2       integers            start and stop indices for axis
        a1,a2       numbers             start and stop values for axis
    
    Use either i1 and i2, or a1 and a2.
    """
    try:
        if kwargs.get("hlp", False): help(subArray)
    except: pass
    #
    shup = kwargs.get("shup", False)
    if not type(shup) is bool: shup = False
    #
    DD = deepcopy(D)
    try: typ = DD.data_type
    except:
        print(f"{Fore.RED}The argument D must be Data object.{Fore.RESET}"); return DD
    #
    int_dim = len(np.shape(DD.intensity))
    #
    if not shup:
        print(f"This data set is of dimension {int_dim} with shape {np.shape(DD.intensity)}.")
        print("The axes are:")
        if int_dim > 0: print(f"axis0    size = {len(DD.axis0)}    ({DD.axis0_label})")
        if int_dim > 1: print(f"axis1    size = {len(DD.axis1)}    ({DD.axis1_label})")
        if int_dim > 2: print(f"axis2    size = {len(DD.axis2)}    ({DD.axis2_label})")
    #
    try: axis = int(axis)
    except:
        print(f"{Fore.RED}The argument axis must be an integer (axis number).{Fore.RESET}"); return DD
    
    #
    # ---------------------------------------- ccd 2d or 3d
    if "ccd" in typ: 
        if int_dim == 2:
            if not axis in [0,1]:
                print(f"{Fore.RED}The argument axis must be an integer (0 or 1).{Fore.RESET}"); return DD
        elif int_dim == 3:
            if not axis in [0,1,2]:
                print(f"{Fore.RED}The argument axis must be an integer (0, 1 or 2).{Fore.RESET}"); return DD
        else:
            print(f"{Fore.RED}I don't recognize the data.{Fore.RESET}"); return DD
        #
        if axis == 0: axis_range = D.axis0
        elif axis == 1: axis_range = D.axis1
        else: axis_range = D.axis2
        #
        i1, i2 = kwargs.get("i1", None), kwargs.get("i2", None)
        a1, a2 = kwargs.get("a1", None), kwargs.get("a2", None)
        try:
            a1, a2 = float(a1), float(a2)
            ii1, ii2 = abs(a1-axis_range).argmin(), abs(a2-axis_range).argmin()
        except:
            try: 
                ii1, ii2 = int(i1), int(i2)
            except:
                ii1, ii2 = -1, -1
        if ii1 == -1 or ii2 == -1:
            print(f"{Fore.RED}Pass either arguments i1 and i2 (indices, integers) or arguments a1 and a2 (axis values, floats) ")
            print(f"as start and end values for axis {axis}. Axis {axis} has {len(axis_range)} points from {axis_range.min()} to {axis_range.max()}.{Fore.RESET}")
            return DD
        if ii1 == ii2:
            print(f"{Fore.RED}The axis range is too narrow.{Fore.RESET}"); return DD
        #
        if axis == 0:
            if int_dim == 2: DD.intensity = DD.intensity[ii1:ii2,:]
            else: DD.intensity = DD.intensity[ii1:ii2,:,:]
            axis_range = axis_range[ii1:ii2]; DD.axis0 = axis_range
        elif axis == 1:
            if int_dim == 2: DD.intensity = DD.intensity[:,ii1:ii2]
            else: DD.intensity = DD.intensity[:,ii1:ii2,:]
            axis_range = axis_range[ii1:ii2]; DD.axis1 = axis_range
        elif axis == 2:
            DD.intensity = DD.intensity[:,:,ii1:ii2]
            axis_range = axis_range[ii1:ii2]
            DD.axis2 = axis_range
        #
        #if not shup:
        #    if axis == 0: axis_str = DD.axis0_label
        #    elif axis == 1: axis_str = DD.axis1_label
        #    elif axis == 2: axis_str = DD.axis2_label
        #    print(f"{Fore.BLUE}Returning data for axis {axis} ({axis_str}) between {axis_range.min()} and {axis_range.max()}.{Fore.RESET}")   
        #
        return DD
    #
    elif "spin" in typ:
        print(f"{Fore.MAGENTA}This method is not ready for spin data yet.{Fore.RESET}"); return DD
    #
    else:
        print(f"{Fore.MAGENTA}This method is not ready for this data type yet.{Fore.RESET}"); return DD
    
        
        




def compact(D = object, **kwargs):
    """
    Returns a data object with one axis compacted (summed). Use in conjunction with subArray().
    
    Arguments:
        D           dopey data object
    Keyword arguments:
        axis        integer             what axis to compact (can e.g. be 0 or 1 for 2d data,...)
    """
    try:
        if kwargs.get("hlp", False): help(compact)
    except: pass
    shup = kwargs.get("shup", False)
    if not type(shup) is bool: shup = False
    #
    DD = deepcopy(D)
    try: typ = DD.data_type
    except:
        print(f"{Fore.RED}The argument D must be Data object.{Fore.RESET}"); return DD
    #
    int_dim = len(np.shape(DD.intensity))
    #
    if not shup:
        print(f"This data set is of dimension {int_dim} with shape {np.shape(DD.intensity)}.")
        print("The axes are:")
        if int_dim > 0: print(f"axis0    size = {len(DD.axis0)}    ({DD.axis0_label})")
        if int_dim > 1: print(f"axis1    size = {len(DD.axis1)}    ({DD.axis1_label})")
        if int_dim > 2: print(f"axis2    size = {len(DD.axis2)}    ({DD.axis2_label})")
    #
    axis = kwargs.get("axis", None)
    try: axis = abs(int(axis))
    except:
        print(f"{Fore.RED}The argument axis must be an integer (axis number).{Fore.RESET}"); return DD
    #
    if "ccd" in typ or "fermi_cut" in typ:
        if axis >= int_dim:
            print(f"{Fore.RED}The argument axis must be an integer (0 <= axis <= {int_dim - 1}). {Fore.RESET}"); return DD
        if int_dim == 2:
            DD.intensity = D.intensity.sum(axis = axis)
            if axis == 1:
                pass
            elif axis == 0:
                DD.axis0 = DD.axis1
                DD.axis0_label = DD.axis1_label
            del DD.__dict__["__axis1"]
            del DD.__dict__["__axis1_label"]
            DD.data_type = "1d"
        elif int_dim == 3:
            DD.intensity = D.intensity.sum(axis = axis)
            if axis == 0:
                DD.axis0 = DD.axis1
                DD.axis0_label = DD.axis1_label
                DD.axis1 = DD.axis2
                DD.axis1_label = DD.axis2_label
                del DD.__dict__["__axis2"]
                del DD.__dict__["__axis2_label"]
            elif axis == 1:
                DD.axis1 = DD.axis2
                DD.axis1_label = DD.axis2_label
                del DD.__dict__["__axis2"]
                del DD.__dict__["__axis2_label"]
            elif axis == 2:
                del DD.__dict__["__axis2"]
                del DD.__dict__["__axis2_label"]
            DD.data_type = "ccd_2d"
        else:
           print(f"{Fore.MAGENTA}I am not ready for this type of data yet...{Fore.RESET}"); return DD 
                
    #
    else:
        print(f"{Fore.MAGENTA}I am not ready for this type of data yet...{Fore.RESET}"); return DD
    #
    return DD
        

# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================


def fermiMapCut(D = object, **kwargs):
    """
    """
    #
    try:
        if kwargs.get("hlp", False):
            print(f"{Fore.BLUE}Arguments:")
            print("D        Data object\n")
            print("Keyword arguments:")
            print("axis     string      axis to sum over: 'x', 'y', or 'E'")
            print("x1, x2   scalars     limits")
            print("y1, y2   scalars     limits")
            print("E1, E2   scalars     limits")
            print(Fore.RESET)
    except: pass
    #
    DD = deepcopy(D)
    try: typ = DD.data_type
    except:
        print(f"{Fore.RED}The argument D must be Data object.{Fore.RESET}"); return DD
    #
    if not typ == 'ccd_3d':
        print(f"{Fore.RED}I am only accepting Fermi maps.{Fore.RESET}"); return DD
    #
    axis = kwargs.get("axis", -1)
    if not type(axis) is str:
        print(f"{Fore.RED}The argument axis must be a string ('x', 'y', or 'E').{Fore.RESET}"); return DD
    axis = axis.lower()
    if not axis in ['x', 'y', 'e']:
        print(f"{Fore.RED}The argument axis must be a string ('x', 'y', or 'E').{Fore.RESET}"); return DD
    #
    x1, x2 = kwargs.get("x1", None), kwargs.get("x2", None)
    y1, y2 = kwargs.get("y1", None), kwargs.get("y2", None)
    e1, e2 = kwargs.get("E1", None), kwargs.get("E2", None)
    try: x1 = float(x1)
    except: x1 = D.axis0.min()
    try: x2 = float(x2)
    except: x2 = D.axis0.max()
    try: y1 = float(y1)
    except: y1 = D.axis1.min()
    try: y2 = float(y2)
    except: y2 = D.axis1.max()
    try: e1 = float(e1)
    except: e1 = D.axis2.min()
    try: e2 = float(e2)
    except: e2 = D.axis2.max()
    #
    ix1, ix2 = abs(D.axis0 - x1).argmin(), abs(D.axis0 - x2).argmin()
    iy1, iy2 = abs(D.axis1 - y1).argmin(), abs(D.axis1 - y2).argmin()
    ie1, ie2 = abs(D.axis2 - e1).argmin(), abs(D.axis2 - e2).argmin()
    if ix1 > ix2: ix1, ix2 = ix2, ix1
    if iy1 > iy2: iy1, iy2 = iy2, iy1
    if ie1 > ie2: ie1, ie2 = ie2, ie1
    #
    axis0 = D.axis0[ix1:ix2]
    axis1 = D.axis1[iy1:iy2]
    axis2 = D.axis2[ie1:ie2]
    intensity = D.intensity[ix1:ix2, iy1:iy2, ie1:ie2]
    #
    if axis == "e":
        DD.intensity = intensity.sum(axis = 2)
        DD.data_type = "fermi_cut"
        DD.axis0 = axis0
        DD.axis1 = axis1
        DD.Ek = axis2.mean()
        del DD.__dict__["__axis2"]
        del DD.__dict__["__axis2_label"]
    #
    if axis == "y":
        DD.intensity = intensity.sum(axis = 1)
        DD.data_type = "ccd_2d"
        DD.axis0 = axis0
        DD.axis1 = axis2
        DD.axis1_label = DD.axis2_label
        del DD.__dict__["__axis2"]
        del DD.__dict__["__axis2_label"]
    #
    if axis == "x":
        DD.intensity = intensity.sum(axis = 0)
        DD.data_type = "ccd_2d"
        DD.axis0 = axis1
        DD.axis0_label = DD.axis1_label
        DD.axis1 = axis2
        DD.axis1_label = DD.axis2_label
        del DD.__dict__["__axis2"]
        del DD.__dict__["__axis2_label"]
        
    #
    return DD
        
        




def align(D = object, **kwargs):
    """
    """
    #
    try:
        if kwargs.get("hlp", False):
            print(f"{Fore.BLUE}Arguments:")
            print("D           Data object")
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
    cmap = kwargs.get("cmap", "bone_r")
    if not type(cmap) is str:
        print(f"{Fore.MAGENTA}The argument cmap must be a (valid) string. Ignoring it.{Fore.RESET}"); cmap = "viridis"
    #
    ENERGY, ANGLEX, ANGLEY = D.axis2, D.axis0, D.axis1
    DE = (ENERGY[-1] - ENERGY[0]) / (len(ENERGY) -1)
    DAX = (ANGLEX[-1] - ANGLEX[0]) / (len(ANGLEX) -1)
    DAY = (ANGLEY[-1] - ANGLEY[0]) / (len(ANGLEY) -1)

    SliderE = ipw.FloatSlider(min=ENERGY[0], max=ENERGY[-1], step = DE, description = 'Energy', value = ENERGY.mean(), readout_format = ".3f")
    SliderDE = ipw.FloatSlider(min=0, max=20*DE, step = DE, description = 'dE', value = 1*DE, readout_format = ".3f")
    extent = [ANGLEX[0], ANGLEX[-1], ANGLEY[-1], ANGLEY[0]]

    SliderVmin = ipw.FloatSlider(min=0, max=D.intensity.max(), step = D.intensity.max()/20, description = 'Imin', value = 0, readout_format = ".1f")
    SliderVmax = ipw.FloatSlider(min=0, max=D.intensity.max(), step = D.intensity.max()/20, description = 'Imax', value = D.intensity.max(), readout_format = ".1f")

    DropdownFigure = ipw.Dropdown(options = ["Cross", "Square", "Rectangle", "Hexagon", "Ellipse", "Circle"], value = "Hexagon", description = "Shape")
    SliderX = ipw.FloatSlider(min = ANGLEX[0], max = ANGLEX[-1], step = DAX, description = 'X', value = ANGLEX.mean(), readout_format = ".2f")
    SliderY = ipw.FloatSlider(min = ANGLEY[0], max = ANGLEY[-1], step = DAY, description = 'Y', value = ANGLEY.mean(), readout_format = ".2f")
    SliderA = ipw.FloatSlider(min = -90, max = 90, step = 1, description = 'Angle', value = 0, readout_format = ".1f")
    SliderS = ipw.FloatSlider(min = 0, max = 15, step = 0.1, description = 'Size', value = 5, readout_format = ".1f")
    SliderS2 = ipw.FloatSlider(min = 0, max = 15, step = 0.1, description = 'Size2', value = 5, readout_format = ".1f")

    vbox1 = ipw.VBox([SliderE, SliderDE])
    vbox2 = ipw.VBox([DropdownFigure, SliderX, SliderY, SliderA, SliderS, SliderS2])
    vbox3 = ipw.VBox([SliderVmin, SliderVmax])
    vbox = ipw.VBox([vbox1, vbox2, vbox3])
    

    def plot(E, DE, VMIN, VMAX, X, Y, A, S, S2, Figure):
        fig, ax = plt.subplots(figsize = (7,7))
        plt.tight_layout()
        #
        if VMIN > VMAX: VMIN = VMAX
        #
        XY = fermiMapCut(D = D, axis = "E", E1 = E-DE/2, E2 = E+DE/2)
        #XY = subArray(D = D, axis = "x", v1 = E-DE/2, v2 = E+DE/2, shup = True), axis = 'x', shup = True)
        _ = ax.imshow(XY.intensity.T, extent = extent, aspect = 'equal', cmap = cmap, vmin = VMIN, vmax = VMAX)
        #
        #slider_vmin = np.min([XY["intensity"].min(), YE["intensity"].min(), XE["intensity"].min()])
        #slider_vmax = np.min([XY["intensity"].max(), YE["intensity"].max(), XE["intensity"].max()])
        #SliderVmin.min, SliderVmin.max = slider_vmin, slider_vmax
        #SliderVmax.min, SliderVmax.max = slider_vmin, slider_vmax
        #
        #if VMIN > VMAX: VMIN = VMAX
        #VMIN, VMAX = None, None
        ax.invert_yaxis()

        if Figure == "Cross":
            x1, y1 = X + S * np.sin(np.deg2rad(A)), Y + S * np.cos(np.deg2rad(A))
            x2, y2 = X - S * np.sin(np.deg2rad(A)), Y - S * np.cos(np.deg2rad(A))
            ax.plot([x1, x2], [y1, y2], color = "tab:red")
            x1, y1 = X + S2 * np.sin(np.deg2rad(A+90)), Y + S2 * np.cos(np.deg2rad(A+90))
            x2, y2 = X - S2 * np.sin(np.deg2rad(A+90)), Y - S2 * np.cos(np.deg2rad(A+90))
            ax.plot([x1, x2], [y1, y2], color = "tab:red")
        elif Figure == "Square":
            polygon = RegularPolygon((X, Y), numVertices=4, radius=S, orientation = -np.deg2rad(A+45), alpha=0.2, edgecolor='k', facecolor = "tab:red")
            ax.add_patch(polygon)
        elif Figure == "Rectangle":
            polygon = Rectangle((X, Y), width = 2*S, height = 2*S2, angle = -A, alpha=0.2, edgecolor='k', facecolor = "tab:red")
            ax.add_patch(polygon)
        elif Figure == "Hexagon":
            polygon = RegularPolygon((X, Y), numVertices=6, radius=S, orientation = -np.deg2rad(A+30), alpha=0.2, edgecolor='k', facecolor = "tab:red")
            ax.add_patch(polygon)
        elif Figure == "Ellipse":
            ellipse = Ellipse((X, Y), width = 2*S, height = 2*S2, angle = -A, alpha=0.2, edgecolor='k', facecolor = "tab:red")
            ax.add_patch(ellipse)
        elif Figure == "Circle":
            circle = Circle((X, Y), radius=S, alpha=0.2, edgecolor='k', facecolor = "tab:red")
            ax.add_patch(circle)
        #
        s = 0.5
        x1, y1 = X + s * np.sin(np.deg2rad(A)), Y + s * np.cos(np.deg2rad(A))
        x2, y2 = X - s * np.sin(np.deg2rad(A)), Y - s * np.cos(np.deg2rad(A))
        ax.plot([x1, x2], [y1, y2], color = "tab:red", linewidth = 0.5)
        x1, y1 = X + s * np.sin(np.deg2rad(A+90)), Y + s * np.cos(np.deg2rad(A+90))
        x2, y2 = X - s * np.sin(np.deg2rad(A+90)), Y - s * np.cos(np.deg2rad(A+90))
        ax.plot([x1, x2], [y1, y2], color = "tab:red", linewidth = 0.5)
        #
        ax.set_xlabel('X (°)')
        ax.set_ylabel('Y (°)')
        #
        #ax.set_title("ID {0}".format(D.get('experiment', {}).get('Spectrum_ID', '')))
        fig.tight_layout()
    #
    Interact = ipw.interactive_output(plot, {'E': SliderE, 
                                             'DE': SliderDE, 
                                             "VMIN": SliderVmin,
                                             "VMAX": SliderVmax,
                                             "X": SliderX,
                                             "Y": SliderY,
                                             "A": SliderA,
                                             "S": SliderS,
                                             "S2": SliderS2,
                                             "Figure": DropdownFigure})
    #
    box_out = ipw.HBox([Interact, vbox])
    box_out.layout = ipw.Layout(border="solid 1px gray", margin="5px", padding="2")
    display(box_out)
    
    
    
    
    
    
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================


def kTransformer(intensity = None, ek = None, a = None, wf = None, **kwargs):
    """
    This method does not accept dopey data objects but arrays!
    
    Transforms an (angle,ek) intensity map to a (kpar,ek) intensity map.
    
    Arguments:
        intensity   array   intensity array (angle, kinetic energy)
        a           array   angle axis, deg.
        ek          array   kinetic energy axis, eV
        wf          float   work function
    
    Returns a dict {kpar, ek, intensity}
        
    """
    shup = kwargs.get("shup", False)
    hlp  = kwargs.get("hlp", False)
    if not type(shup) is bool: shup = False
    if not type(hlp) is bool: hlp = False
    #
    ret_dict = {"kpar": None, "ek": None, "intensity": None}
    #
    if not type(intensity) is np.ndarray:
        print(f"{Fore.RED}The argument 'intensity' must be a 2D array.{Fore.RESET}"); return ret_dict
    if not len(np.shape(intensity)) == 2:
        print(f"{Fore.RED}The argument 'intensity' must be a 2D array.{Fore.RESET}"); return ret_dict
    if not type(ek) is np.ndarray:  
        print(f"{Fore.RED}The argument 'ek' must be a 1D array.{Fore.RESET}"); return ret_dict
    if not len(np.shape(ek)) == 1:
        print(f"{Fore.RED}The argument 'ek' must be a 1D array.{Fore.RESET}"); return ret_dict
    if not type(a) is np.ndarray:  
        print(f"{Fore.RED}The argument 'a' must be a 1D array.{Fore.RESET}"); return ret_dict
    if not len(np.shape(a)):
        print(f"{Fore.RED}The argument 'a' must be a 1D array.{Fore.RESET}"); return ret_dict
    try: wf = abs(float(wf))
    except:
        print(f"{Fore.RED}The argument 'wf' must be a positive number.{Fore.RESET}"); return ret_dict
    #
    ishape = np.shape(intensity)
    if not (ishape[0] == len(a) and ishape[1] == len(ek)):
        print(f"{Fore.RED}The dimension of the intensity array does not match the sizes of the axes.{Fore.RESET}")
        print(f"  intensity: {ishape[0]} x {ishape[1]}")
        print(f"  a:         {len(a)}")
        print(f"  ek:        {len(ek)}")
        return ret_dict
    #
    def kpar(Ek, a): return 0.52611 * np.sqrt(Ek - wf) * np.sin(a)
    #
    def angle(Ek, k): return np.arcsin(k/0.52611/np.sqrt(Ek-wf))
    #
    INTENSITY = np.zeros(np.shape(intensity))
    ANGLE = np.deg2rad(a)
    EK = np.copy(ek)
    KPAR = np.linspace(kpar(max(EK), min(ANGLE)),  kpar(max(EK), max(ANGLE)), len(ANGLE))
    del a, ek
    #
    for iek, ek in enumerate(EK):
        for ik, k in enumerate(KPAR):
            a = angle(ek, k)
            if a >= ANGLE.min() and a <= ANGLE.max():
                ia = abs(a - ANGLE).argmin()
                INTENSITY[ik][iek] = intensity[ia][iek]
    #
    ret_dict.update({"intensity": INTENSITY, "ek": EK, "kpar": KPAR})
    return ret_dict
    


def kTansformARPES(D = object, **kwargs):
    """
    Accepts dopey data objects containing ARPES data (y-angle or x-deflector as angle) and
    return a data object with k-transformed intensity.
    
    Arguments:
        D       dopey data object
    Keyword Arguments:
        wf      number              work function. if not passed then the default from dopey_constants.py will be used.
        shup    bool                
        hlp     bool                
    """
    try:
        if kwargs.get("hlp", False): help(kTansformARPES)
    except: pass
    shup = kwargs.get("shup", False)
    if not type(shup) is bool: shup = False
    #
    wf = kwargs.get("wf", WORKFUNCTION)
    try: wf = abs(float(wf))
    except:
        print(f"{Fore.RED}The keyword argument wf (work function) must be positive number. Setting default wf = {WORKFUNCTION}{Fore.RESET}")
        wf = WORKFUNCTION
    #
    DD = deepcopy(D)
    try: typ = DD.data_type
    except:
        print(f"{Fore.RED}The argument D must be dopey data object.{Fore.RESET}"); return DD
    #
    if typ != "ccd_2d":
        if typ == 'from3d':
            print(f"{Fore.BLUE}The data comes from dopey_plot.slice3D() and contains both 2d and 1d data.") 
            print(f"Use from3dslim() to get the 2d data and run this method again.{Fore.RESET}"); return DD
        elif typ == 'fermi_cut':
            print(f"{Fore.MAGENTA}I'm sending this data to kTransformFermiCut()...{Fore.RESET}")
            return kTransformFermiCut(D = D, **kwargs)
        else:
            print(f"{Fore.RED}The argument D must be an ARPES data object.{Fore.RESET}"); return DD
    #
    if D.axis0_label.lower().startswith("k"):
        print(f"{Fore.RED}This data is already k-transformed.{Fore.RESET}"); return DD
    #
    kt = kTransformer(intensity = D.intensity, ek = D.axis1, a = D.axis0, wf = wf)
    DD.intensity = kt["intensity"]
    DD.axis0 = kt["kpar"]
    DD.axis0_label = "k (1/Å)"
    return DD


def kTransformFermiCut(D = object, **kwargs):
    """
    Under development.
    """
    try:
        if kwargs.get("hlp", False): help(kTransformFermiCut)
    except: pass
    shup = kwargs.get("shup", False)
    if not type(shup) is bool: shup = False
    #
    wf = kwargs.get("wf", WORKFUNCTION)
    try: wf = abs(float(wf))
    except:
        print(f"{Fore.RED}The keyword argument wf (work function) must be positive number. Setting default wf = {WORKFUNCTION}{Fore.RESET}")
        wf = WORKFUNCTION
    #
    DD = deepcopy(D)
    try: typ = DD.data_type
    except:
        print(f"{Fore.RED}The argument D must be dopey data object.{Fore.RESET}"); return DD
    #
    if not typ == "fermi_cut":
        print(f"{Fore.RED}The argument D must be an fermicut data object.{Fore.RESET}"); return DD
    #
    if D.axis0_label.lower().startswith("k"):
        print(f"{Fore.RED}This data is already k-transformed.{Fore.RESET}"); return DD
    #
    # check if the x-axis and y-axis are what I expect them to be. It might be that I (in the future) add some new method
    # that does something weird...
    if not ("ShiftX" in D.axis0_label and "ordinate" in D.axis1_label):
        DD.axis0, DD.axis0_label = D.axis1, D.axis1_label
        DD.axis1, DD.axis1_label = D.axis0, D.axis0_label
        DD.intensity = D.intensity.T
    #
    def kpar(Ek, a): return 0.52611 * np.sqrt(Ek - wf) * np.sin(a)
    def angle(Ek, k): return np.arcsin(k/0.52611/np.sqrt(Ek-wf))
    #
    SHIFTX = np.deg2rad(DD.axis0)
    ANGLE = np.deg2rad(DD.axis1)
    kxmin, kxmax = kpar(DD.Ek, SHIFTX.min()), kpar(DD.Ek, SHIFTX.max())
    kymin, kymax = kpar(DD.Ek, ANGLE.min()), kpar(DD.Ek, ANGLE.max())
    KX = np.linspace(kxmin, kxmax, len(SHIFTX))
    KY = np.linspace(kymin, kymax, len(ANGLE))
    intensityk = np.zeros([len(KX), len(KY)]) * np.NaN
    #
    for ikx, kx in enumerate(KX):
        ax = angle(DD.Ek, kx)
        if ax >= SHIFTX.min() and ax <= SHIFTX.max():
            iax = abs(ax - SHIFTX).argmin()
            for iky, ky in enumerate(KY):
                ay = angle(DD.Ek, ky)
                if ay >= ANGLE.min() and ax <= ANGLE.max():
                    iay = abs(ay - ANGLE).argmin()
                    intensityk[ikx][iky] = DD.intensity[iax][iay]
    DD.intensity = intensityk
    DD.axis0 = KX
    DD.axis0_label = "kx (1/Å)"
    DD.axis1 = KY
    DD.axis1_label = "ky (1/Å)"
    #
    return DD

            

def from3dslim(D = object, keep = 0):
    """
    """
    DD = deepcopy(D)
    try:
        if not D.data_type == "from3d":
            print(f"{Fore.RED}The argument D must be of type 'from3d' from slice3D().{Fore.RESET}"); return DD
    except:
        print(f"{Fore.RED}The argument D must be of type 'from3d' from slice3D().{Fore.RESET}"); return DD
    #
    try: keep = int(keep)
    except:
        print(f"{Fore.RED}The argument keep must be an integer (0,1, or 2).{Fore.RESET}"); return DD
    if not keep in [0,1,2]:
        print(f"{Fore.RED}The argument keep must be an integer (0,1, or 2).{Fore.RESET}"); return DD
    #
    newD = DataObject()
    if keep == 0:
        newD._addProperty("intensity", D.intensity0.T)
        newD._addProperty("axis0", D.axis1)
        newD._addProperty("axis1", D.axis2)
        newD._addProperty("axis0_label", D.axis1_label)
        newD._addProperty("axis1_label", D.axis2_label)
        if ("shiftx" in newD.axis0_label.lower() or "shiftx" in newD.axis1_label.lower()) and ("ordinate" in newD.axis0_label.lower() or "ordinate" in newD.axis1_label.lower()):
            newD._addProperty("data_type", "fermi_cut")
            newD._addProperty("Ek", D.params.axis0)
        elif "kinetic" in newD.axis0_label.lower() or "kinetic" in newD.axis1_label.lower():
            newD._addProperty("data_type", "ccd_2d")
    #
    elif keep == 1:
        newD._addProperty("intensity", D.intensity1)
        newD._addProperty("axis0", D.axis1)
        newD._addProperty("intensity_label", "")
        newD._addProperty("axis0_label", D.axis1_label)
        newD._addProperty("data_type", "1d")
    #
    elif keep == 2:
        newD._addProperty("intensity", D.intensity2)
        newD._addProperty("axis0", D.axis2)
        newD._addProperty("intensity_label", "")
        newD._addProperty("axis0_label", D.axis2_label)
        newD._addProperty("data_type", "1d")
    #
    newD._addProperty("experiment", D.experiment)
    return newD
        

        
    
    