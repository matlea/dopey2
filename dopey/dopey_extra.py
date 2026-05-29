__version__ = "26.05.06"
__author__  = "Mats Leandersson"


"""
Version 26.05.06    Had forgotten experiment in f.write(f"# spectrum id: {D.experiment.Spectrum_ID}\n")
                    in the export2txt() method.
                    Also, in the same method, changed D.intensity.T[0] to D.intensity.T[i] in
                    f.write( f"{round(D.axis0[i],5)}\t" + "\t".join(str(round(e,5)) for e in D.intensity.T[i]) + "\n" )
Version 26.02.14    All 'help' keyword arguments are now 'hlp'.
Version 25.11.10    Export to text.
"""


import numpy as np
from colorama import Fore



def export2txt(D = object, file_name = "data", **kwargs):
    """
    Export data to text file(s). Pass D as data object and file_name as string (no extention).
    Work in progress, just covering spin edc and spin mdc at the moment.
    
    Version: 2025-11-11
    """
    #
    shup = kwargs.get("shup", False)
    if not type(shup) is bool: shup = False
    #
    accepted_data_types = ["spin_edc", "spin_mdc"]
    #
    hlp = kwargs.get("hlp", False)
    if not type(hlp) is bool: hlp = False
    if hlp:
        print(f"{Fore.BLUE}Arguments:")
        print("D            data object")
        print("file_name    string          file name w.o. extension")
        print(f"{Fore.RESET}")
    #
    try: typ = D.data_type
    except:
        print(f"{Fore.RED}The argument D must be a data object.{Fore.RESET}"); return
    #
    try: file_name = str(file_name).lower()
    except:
        print(f"{Fore.MAGENTA}The argument file_name must be a string. Setting file_name = 'file'.{Fore.RESET}")
        file_name = "data"
    #
    if typ in ["spin_edc", "spin_mdc"]:
        file_name = f"{file_name}.dat"
        with open(file_name, "w") as f:
            f.write(f"# file name:   {D.file_name}\n")
            f.write(f"# spectrum id: {D.experiment.Spectrum_ID}\n")
            f.write("# columns:     x-axis, y-axes\n")
            f.write(f"# x-axis:      {D.axis0_label}\n")
            #
            if not "asymmetry" in D._listAttributes():
                f.write(f"# y-axes:      Negative polarity {str(list(D.parameter0))[1:-1]}\n")
                for i in range(len(D.axis0)):
                    f.write( f"{round(D.axis0[i],5)}\t" + "\t".join(str(round(e,5)) for e in D.intensity.T[i]) + "\n" )
            else:
                f.write(f"# y-axes:      asymmetry, plus component, minus component\n")
                for i in range(len(D.axis0)):
                    f.write( f"{D.axis0[i]:.3f}\t{D.asymmetry[i]:.3f}\t{D.component_plus[i]:.3f}\t{D.component_minus[i]:.3f}\n" )
        #
        if not shup:
            print(f"{Fore.BLUE}Data saved to {file_name}.{Fore.RESET}")    
        
    #
    else:
        print(f"{Fore.RED}I am only accepting the following data types at the moment:{Fore.RESET}")
        for t in accepted_data_types: print(f". {t}")
        print(f"{Fore.RED}Other data types will be added upon request or when needed.{Fore.RESET}")
    
        
    
        
        
    