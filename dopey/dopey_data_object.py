__version__ = "26.02.19"
__author__  = "Mats Leandersson"

"""
version 26.02.19    .asymmetry() in dopey_spin.py had to be renamed calcAsymmetry() since there is an array called asymmetry.
version 26.02.18    Added access to dopey methods directly from the DataObject, e.g. do.plot() or do.asymmetry().
version 26.02.14    Added hlp keyword argument (for consistency)
version 26.02.10    Moving the _DataObject out of dopey_loader.py due to various reasons.
                    Renaming it DataObject.
"""


import numpy as np
from copy import deepcopy
from colorama import Fore
import sys


def methodsLoaded(lst = []):
    """
    Returns True if all the methods, variables, modules, etc. in the list lst are loaded.
    """
    if not type(lst) is list: return False
    if len(lst) == 0: return False
    dic = sys.modules["dopey"].__dict__
    for item in lst:
        if not item in dic: return False
    return True


class DataObject():
    """
    This is an object that contains loaded, sorted data, and perhaps manipulated data from Prodigy,
    e.g. created by load(), asymmetry(), etc.
    The data and metadata is accessible as attributes, e.g. .intensity, .axis0, etc.
    Also holds a couple of methods, e.g. .plot(), .slice3D(), subArray(), compact(), align(), 
        fermiMapCut(), asymmetry(),...
    
    """
    def _addProperty(self, name: str, value):
        setattr(DataObject, name, property(self._getter(name), self._setter(name, value)))
        setattr(self, '__'+name, value)
    
    def _setter(self, name: str, value):
        def inner_setter(self, value):
            setattr(self, '__'+name, value)
        return inner_setter

    def _getter(self, name: str):
        def inner_getter(self):
            return getattr(self, '__'+name)
        return inner_getter
    
    # ----------------------------------------------------
    def __init__(self, **kwargs):
        """
        """    
        self._addProperty("dopey", __version__)
        if kwargs.get('hlp', False): help(self)
        #
        # Add methods if available. These methods are collected from other py-files and added (if those files are available, otherwise ignored).
        self._addProperty("plot", self._plot)                       # dopey_plot.py
        self._addProperty("slice3D", self._slice3D)                 # dopey_plot.py
        self._addProperty("subArray", self._subArray)               # dopey_methods.py
        self._addProperty("compact", self._compact)                 # dopey_methods.py
        self._addProperty("align", self._align)                     # dopey_methods.py
        self._addProperty("fermiMapCut", self._fermiMapCut)         # dopey_methods.py
        self._addProperty("calcAsymmetry", self._calcAsymmetry)     # dopey_spin.py
        
    # ---------------------------------------------------- methods from _plot.py, _methods.py, etc., if they are available
    
    def _plot(self, D = object, ax = None, **kwargs):
        try: return sys.modules["dopey"].dopey_plot.plot(D = self, ax = ax, **kwargs)
        except Exception as E:
            print(f"{Fore.MAGENTA}I experienced a problem when trying to use .plot() from dopey_plot.py.{Fore.RESET}\n")
            print(Fore.RED, E, Fore.RESET)
            return ax
    
    def _slice3D(self, D = object, axis = None, shup = False):
        try: return sys.modules["dopey"].dopey_plot.slice3D(D = self, axis = axis, shup = shup)
        except Exception as E:
            print(f"{Fore.MAGENTA}I experienced a problem when trying to use .slice3D() from dopey_plot.py.{Fore.RESET}\n")
            print(Fore.RED, E, Fore.RESET)
            return DataObject()
            
    def _subArray(self, D = object, axis = -1, **kwargs):
        try: return sys.modules["dopey"].dopey_methods.subArray(D = self, axis = axis, **kwargs)
        except Exception as E:
            print(f"{Fore.MAGENTA}I experienced a problem when trying to use .subArray() from dopey_methods.py.{Fore.RESET}")
            print(Fore.RED, E, Fore.RESET)
            return DataObject()
    
    def _compact(self, D = object, **kwargs):
        try: return sys.modules["dopey"].dopey_methods.compact(D = self, **kwargs)
        except Exception as E:
            print(f"{Fore.MAGENTA}I experienced a problem when trying to use .compact() from dopey_methods.py.{Fore.RESET}")
            print(Fore.RED, E, Fore.RESET)
            return DataObject()
    
    def _align(self, D = object, **kwargs):
        try: return sys.modules["dopey"].dopey_methods.align(D = self, **kwargs)
        except Exception as E:
            print(f"{Fore.MAGENTA}I experienced a problem when trying to use .align() from dopey_methods.py.{Fore.RESET}")
            print(Fore.RED, E, Fore.RESET)
            return DataObject()
        
    def _fermiMapCut(self, D = object, **kwargs):
        try: return sys.modules["dopey"].dopey_methods.fermiMapCut(D = self, **kwargs)
        except Exception as E:
            print(f"{Fore.MAGENTA}I experienced a problem when trying to use .fermiMapCut() from dopey_methods.py.{Fore.RESET}")
            print(Fore.RED, E, Fore.RESET)
            return DataObject()
    
    def _calcAsymmetry(self, D = object, **kwargs):
        try: return sys.modules["dopey"].dopey_spin.calcAsymmetry(D = self, **kwargs)
        except Exception as E:
            print(f"{Fore.MAGENTA}I experienced a problem when trying to use .calcAsymmetry() from dopey_spin.py.{Fore.RESET}")
            print(Fore.RED, E, Fore.RESET)
            return DataObject()
            
    
    # ----------------------------------------------------
    
    def __str__(self):
        return dataInfo(self, ret = True)
    
    @property
    def info(self):
        dataInfo(self)
    
    @property
    def arrays(self):
        lst = self._listArrays()
        print(f"Arrays:")
        for attr in lst:
            shape = np.shape(self.__dict__["__"+attr])
            print(f"  {Fore.BLUE}{attr.ljust(20)}{Fore.RESET}shape={shape}")
            
    
    # --------------------------------------------------------------------------
    

    
    def _printDataType(self):
        print(f"Data type:\n  {Fore.BLUE}{self.data_type}{Fore.RESET}")
        
    def _printAxesAndParameters(self):
        print(f"Data, axes, and parameters:")
        for key in self.__dict__.keys():
            name, value = "", ""
            if "label" in key:
                name = key.replace("_label", "").replace("__", "")
                shape = np.shape(self.__dict__["__"+name])
                print(f"  {Fore.BLUE}{name.ljust(20)}{Fore.RESET}{self.__dict__[key].ljust(25)}shape={shape}")
    
    def _listAttributes(self):
        lst = []
        for key in self.__dict__.keys(): lst.append(key.replace("__",""))
        return lst
    
    def _listArrays(self):
        lst = []
        for key in self.__dict__.keys(): 
            if type(self.__dict__.get(key, None)) is np.ndarray:
                lst.append(key.replace("__",""))
        return lst
        



def dataInfo(D = None, ret = False):
    try: _ = D.dopey
    except:
        print(f"{Fore.RED}info(): the argument must be a Data object."); return
    #
    out = ""
    for key in D.__dict__.keys():
        if key.startswith("__"):
            key_name = Fore.BLUE + key.replace('__', '').ljust(20) + Fore.RESET
            item = D.__dict__.get(key)
            typ = type(item)
            if typ is np.ndarray:
                t = "Array".ljust(15)
                s = f"shape = {np.shape(item)}".ljust(25)
                nk = f"{key}_label"
                out += f"{key_name}{t}{s}{D.__dict__.get(nk,'')}\n"
            elif typ is float or typ is int or typ is np.float64:
                t = "Scalar".ljust(15)
                v = item
                out += f"{key_name}{t}{v}\n"
    out += "\n"
    #
    for key in D.__dict__.keys():
        if key.startswith("__"):
            key_name = Fore.BLUE + key.replace('__', '').ljust(20) + Fore.RESET
            item = D.__dict__.get(key)
            typ = type(item)
            if typ is dict:
                t = "Dictionary".ljust(15)
                out += f"{key_name}{t}\n"
            elif typ is str:# and "_label" in key_name:
                if not "dopey" in key_name:
                    t = "String".ljust(15)
                    s = item.replace("\n", " ").replace("\t", " ")
                    out += f"{key_name}{t}{s}\n"
            elif typ is list:
                t = "List".ljust(15)
                v = len(item)
                out += f"{key_name}{t}len = {v}\n"
    out += "\n"
    #
    for key in D.__dict__.keys():
        if key.startswith("__"):
            key_name = key.replace('__', '')
            item = D.__dict__.get(key)
            typ = type(item)
            key_name = Fore.BLUE + key.replace('__', '').ljust(20) + Fore.RESET
            if typ is type(DataObject()):
                t = "DataObject".ljust(15)
                out += f"{key_name}{t}(use .info to see contents)\n"
        
    if ret: return out
    else: print(out)
