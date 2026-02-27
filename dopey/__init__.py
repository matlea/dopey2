__author__ = "Mats Leandersson"
__version__ = "2026.02.25"

from colorama import Fore, Style
import sys
import types


__all__ = ["dopey_data_object", "dopey_constants", "dopey_loader", "dopey_spin", "dopey_plot", "dopey_methods", "dopey_extra"]

print(f"{Style.BRIGHT}Loading dopey...{Style.NORMAL}")
try: 
    from dopey.dopey_data_object import *
    print(f"{Fore.GREEN}dopey_data_object, version {dopey_data_object.__version__}{Fore.RESET}")
except: print(f"{Fore.RED}dopey_data_object, not loaded. {Style.BRIGHT}Fatal.{Style.NORMAL}{Fore.RESET}")

try: 
    from dopey.dopey_constants import *
    print(f"{Fore.GREEN}dopey_constants, version {dopey_constants.__version__}{Fore.RESET}")
except: print(f"{Fore.RED}dopey_constants, not loaded{Fore.RESET}")

try: 
    from dopey.dopey_loader import *
    print(f"{Fore.GREEN}dopey_loader, version {dopey_loader.__version__}{Fore.RESET}")
except: print(f"{Fore.RED}dopey_loader, not loaded{Fore.RESET}")

try: 
    from dopey.dopey_spin import *
    print(f"{Fore.GREEN}dopey_spin, version {dopey_spin.__version__}{Fore.RESET}")
except: print(f"{Fore.RED}dopey_spin, not loaded{Fore.RESET}")

try: 
    from dopey.dopey_plot import *
    print(f"{Fore.GREEN}dopey_plot, version {dopey_plot.__version__}{Fore.RESET}")
except: print(f"{Fore.RED}dopey_plot, not loaded{Fore.RESET}")

try: 
    from dopey.dopey_methods import *
    print(f"{Fore.GREEN}dopey_methods, version {dopey_methods.__version__}{Fore.RESET}")
except: print(f"{Fore.RED}dopey_methods, not loaded{Fore.RESET}")

try: 
    from dopey.dopey_extra import *
    print(f"{Fore.GREEN}dopey_extra, version {dopey_extra.__version__}{Fore.RESET}")
except: print(f"{Fore.RED}dopey_extra, not loaded{Fore.RESET}")




def dopeyContent():
    try: dopey_dict = sys.modules["dopey"].__dict__
    except: return
    modules = []
    for item in dopey_dict.items():
        if isinstance(item[1], types.ModuleType):
            if "dopey" in item[0]: modules.append(item[0])
    if len(modules) == 0: return
    #
    for M in modules:
        print(f"{Style.BRIGHT}Module: {M}{Style.NORMAL}")
        m_dict = sys.modules[f"dopey.{M}"].__dict__
        for item in m_dict.items():
            if item[0] == "DataObject": typ = "DataObject"
            elif isinstance(item[1], types.FunctionType): typ = "method"
            elif type(item[1]) is float: typ = "number"
            else: typ = ""
            if not typ == "" and item[0].startswith("_"): typ = f"{typ} (not a user method)"
            if not typ == "": print(f"{item[0]:<30}{typ}")
        print()

        
    