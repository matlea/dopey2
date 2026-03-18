__author__ = "Mats Leandersson"
__version__ = "2026.03.18"

from colorama import Fore, Style
import sys
import types


__all__ = ["dopey_data_object", "dopey_constants", "dopey_loader", "dopey_spin", "dopey_plot", "dopey_methods", "dopey_extra"]
print(f"{Style.BRIGHT}{Fore.BLUE}Dopey{Style.NORMAL}")
print(f"Dopey is used to load, sort, and analyze data produced by SPECS Prodigy and saved")
print(f"to xy-files. The main method is load() which returns a dopey data object. Dopey")
print(f"contains a number of methods for viewing (e.g. plot()) and manipulating the data.{Fore.RESET}\n")



print(f"{Style.BRIGHT}Loading dopey...{Style.NORMAL}")
ok = True
try: 
    from dopey.dopey_data_object import *
    print(f"module loaded: dopey_data_object, version {dopey_data_object.__version__}")
except: 
    ok = False
    print(f"{Fore.RED}module not loaded: dopey_data_object {Style.BRIGHT}** Fatal **{Style.NORMAL}{Fore.RESET}")

try: 
    from dopey.dopey_constants import *
    print(f"module loaded: dopey_constants, version {dopey_constants.__version__}")
except:
    ok = False
    print(f"{Fore.RED}module not loaded: dopey_constants{Fore.RESET}")

try: 
    from dopey.dopey_loader import *
    print(f"module loaded: dopey_loader, version {dopey_loader.__version__}")
except: 
    ok = False
    print(f"{Fore.RED}module not loaded: dopey_loader {Style.BRIGHT}** Fatal **{Style.NORMAL}{Fore.RESET}")

try: 
    from dopey.dopey_spin import *
    print(f"module loaded: dopey_spin, version {dopey_spin.__version__}")
except:
    ok = False
    print(f"{Fore.RED}module not loaded: dopey_spin{Fore.RESET}")

try: 
    from dopey.dopey_plot import *
    print(f"module loaded: dopey_plot, version {dopey_plot.__version__}")
except: 
    ok = False
    print(f"{Fore.RED}module not loaded: dopey_plot{Fore.RESET}")

try: 
    from dopey.dopey_methods import *
    print(f"module loaded: dopey_methods, version {dopey_methods.__version__}")
except: 
    ok = False
    print(f"{Fore.RED}module not loaded: dopey_methods{Fore.RESET}")

try: 
    from dopey.dopey_extra import *
    print(f"module loaded: dopey_extra, version {dopey_extra.__version__}")
except: 
    ok = False
    print(f"{Fore.RED}module not loaded: dopey_extra{Fore.RESET}")

try: 
    from dopey.dopey_photon_energy_scan import *
    print(f"module loaded: dopey_photon_energy_scan, version {dopey_photon_energy_scan.__version__}")
except: 
    ok = False
    print(f"{Fore.RED}module not loaded: dopey_photon_energy_scan{Fore.RESET}")


if not ok:
    print(f"\n{Style.BRIGHT}{Fore.RED}Some of the dopey modules were not loaded. This will very likely limit the functionality.{Fore.RESET}{Style.NORMAL}\n")



def dopeyContent():
    try: dopey_dict = sys.modules["dopey"].__dict__
    except: return
    modules = []
    python_modules = []
    for item in dopey_dict.items():
        if isinstance(item[1], types.ModuleType):
            if "dopey" in item[0]: modules.append(item[0])
            else: python_modules.append(item[0])
    if len(modules) == 0: return
    #
    python_methods = []
    for M in modules:
        print(f"{Style.BRIGHT}Module: {M}{Style.NORMAL}")
        m_dict = sys.modules[f"dopey.{M}"].__dict__
        for item in m_dict.items():
            if item[0] == "DataObject": typ = "DataObject"
            elif isinstance(item[1], types.FunctionType): 
                if item[0] in ["deepcopy", "display",]:
                    python_methods.append(item[0])
                    typ = ""
                else:
                    typ = "method"
            elif type(item[1]) is float: typ = "number"
            else: typ = ""
            if not typ == "" and item[0].startswith("_"): typ = f"{typ} (not a user method)"
            if not typ == "": print(f"{item[0]:<30}{typ}")
        print()
    #
    if len(python_methods) > 0:
        print(f"{Style.BRIGHT}Other methods from standards Python packages:{Style.NORMAL}")
        for item in np.unique(python_methods): print(f"{item}")
    print()
    #
    if len(python_modules) > 0:
        print(f"{Style.BRIGHT}Python packages available through dopey:{Style.NORMAL}")
        for item in np.unique(python_modules): print(f"{item}")
    print()
        

        
    