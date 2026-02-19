__author__ = "Mats Leandersson"
__version__ = "2026.02.18"

from colorama import Fore

__all__ = ["dopey_data_object", "dopey_constants", "dopey_loader", "dopey_spin", "dopey_plot", "dopey_methods", "dopey_extra"]

try: 
    from dopey.dopey_data_object import *
    print(f"{Fore.GREEN}dopey_data_object, version {dopey_data_object.__version__}{Fore.RESET}")
except: print(f"{Fore.RED}dopey_data_object, not loaded{Fore.RESET}")

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




 