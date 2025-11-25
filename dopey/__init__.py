__author__ = "Mats Leandersson"
__version__ = "2025.11.24"


from colorama import Fore

import_errors = []

try:  from dopey.dopey_constants import *
except Exception as E: 
    print(f"  {Fore.RED}{'dopey_constants':<25}{Fore.RESET}"); import_errors.append(E)

try: from dopey.dopey_spin import *
except Exception as E: 
    print(f"  {Fore.RED}{'dopey_spin':<25}{Fore.RESET}"); import_errors.append(E)

try: from dopey.dopey_loader import *
except Exception as E: 
    print(f"  {Fore.RED}{'dopey_loader':<25}{Fore.RESET}"); import_errors.append(E)

try: from dopey.dopey_plot import *
except Exception as E: 
    print(f"  {Fore.RED}{'dopey_plot':<25}{Fore.RESET}"); import_errors.append(E)

try: from dopey.dopey_methods import *
except Exception as E: 
    print(f"  {Fore.RED}{'dopey_methods':<25}{Fore.RESET}"); import_errors.append(E) 

try: from dopey.dopey_extra import *
except Exception as E: 
    print(f"  {Fore.RED}{'dopey_extra':<25}{Fore.RESET}"); import_errors.append(E) 


if len(import_errors) > 0:
    print(f"\nImport errors:{Fore.RED}")
    for E in import_errors: print(E, "\n")
    print(f"{Fore.RESET}")


