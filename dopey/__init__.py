__author__ = "Mats Leandersson"
__version__ = "2025.11.19"


#print(f"{__name__}, {__author__}")


from colorama import Fore

import_errors = []
print("Loading dopey...")

try: 
    from dopey.dopey_constants import *
    print(f"  {Fore.BLUE}{'dopey_constants':<25}({dopey_constants.__version__}){Fore.RESET}")
except Exception as E: 
    print(f"  {Fore.RED}{'dopey_constants':<25}{Fore.RESET}"); import_errors.append(E)
try: 
    from dopey.dopey_spin import *
    print(f"  {Fore.BLUE}{'dopey_spin':<25}({dopey_spin.__version__}){Fore.RESET}")
except Exception as E: 
    print(f"  {Fore.RED}{'dopey_spin':<25}{Fore.RESET}"); import_errors.append(E)
try: 
    from dopey.dopey_loader import *
    print(f"  {Fore.BLUE}{'dopey_loader':<25}({dopey_loader.__version__}){Fore.RESET}")
except Exception as E: 
    print(f"  {Fore.RED}{'dopey_loader':<25}{Fore.RESET}"); import_errors.append(E)
try: 
    from dopey.dopey_plot import *
    print(f"  {Fore.BLUE}{'dopey_plot':<25}({dopey_plot.__version__}){Fore.RESET}")
except Exception as E: 
    print(f"  {Fore.RED}{'dopey_plot':<25}{Fore.RESET}"); import_errors.append(E)
try: 
    from dopey.dopey_methods import *
    print(f"  {Fore.BLUE}{'dopey_methods':<25}({dopey_methods.__version__}){Fore.RESET}")
except Exception as E: 
    print(f"  {Fore.RED}{'dopey_methods':<25}{Fore.RESET}"); import_errors.append(E) 
try: 
    from dopey.dopey_extra import *
    print(f"  {Fore.BLUE}{'dopey_extra':<25}({dopey_extra.__version__}){Fore.RESET}")
except Exception as E: 
    print(f"  {Fore.RED}{'dopey_extra':<25}{Fore.RESET}"); import_errors.append(E) 


if len(import_errors) > 0:
    print(f"\nImport errors:{Fore.RED}")
    for E in import_errors: print(E)
    print(f"{Fore.RESET}")
        

