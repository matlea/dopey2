__author__ = "Mats Leandersson"
__version__ = "2026.02.14"

from colorama import Fore

__all_dopey_modules__ = ["dopey_data_object", "dopey_constants", "dopey_loader", "dopey_spin", "dopey_plot", "dopey_methods", "dopey_extra"]
__all_loaded_dopey_modules__ = []
__missing_dopey_modules__ = []

try: from dopey.dopey_data_object import *
except: pass

try: from dopey.dopey_constants import *
except: pass

try: from dopey.dopey_loader import *
except: pass

try: from dopey.dopey_spin import *
except: pass 

try: from dopey.dopey_plot import *
except: pass

try: from dopey.dopey_methods import *
except: pass

try: from dopey.dopey_extra import *
except: pass


gl = globals()
for m in __all_dopey_modules__:
    if m in gl: __all_loaded_dopey_modules__.append(m)
    else: __missing_dopey_modules__.append(m)
    
if not __all_dopey_modules__ == __all_loaded_dopey_modules__:
    print("\nNot all dopey modules were loaded.")
    print(f"{Fore.GREEN}Loaded:     {__all_loaded_dopey_modules__}{Fore.RESET}")
    print(f"{Fore.RED}Not loaded: {__missing_dopey_modules__}{Fore.RESET}")
    print("This might or might not affect your usage.\n")



            
        
    