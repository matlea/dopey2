__version__ = "25.11.07"
__author__  = "Mats Leandersson"


"""
Version 25.11.07    Added pickleSave() and pickleLoad()
Version 25.10.16    Small update: added .arrays as a attribute to Data object.
Version 25.10.16    Progressing...
Version 25.10.13    Created an "independent" pure data class instead of having one in the loader class (Data())
Version 25.10.03    The first working version.
version 25.10.02        

"""

from colorama import Fore
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
import pickle

CCD_ANALYZERS  = ["PhoibosCCD", "AnalyzerCCD"]
SPIN_ANALYZERS = ["PhoibosSpin"]





# ==================================================================================================
# ==================================================================================================
# ==================================================================================================

def loadXY(file_name = "", shup = False, keep_raw_data = False):
    """
    """
    if not type(file_name) is str: file_name = ""
    if not type(shup) is bool: shup = False
    if not type(keep_raw_data) is bool: keep_raw_data = False
    #
    retd = {}           # The dict to be returned.
    experiment = {}     # Sub dict, add to dict retd
    parameters = []     # Array, add to dict Experiment
    #
    if not type(file_name) is str: file_name = ""
    if file_name == '':
        print(Fore.RED + "loadXY(): The argument 'file_name' must be a string." + Fore.RESET); return {}
    if not file_name.split(".")[-1].lower() == "xy":
        print(Fore.RED + "loadXY(): The loader only accepts .xy files (the file HAS to have extention .xy)." + Fore.RESET); return {}
    try:
        f = open(file_name, 'r'); f.close()
    except:
        print(Fore.RED + f"loadXY(): I could not find/open the file ({file_name})." + Fore.RESET)
        return {}
    
    retd.update({"file_name": file_name, "spectrum_id": -1, "experiment": {},
                "type": "unidentified", "raw_data": {}})

    data_start_row = -1

    with open(file_name, 'rb') as f:
        ReadHeader = True
        
        for i, row_ in enumerate(f):
            row = row_.decode(errors='ignore')
            row = row.replace('\r', '').replace('\n', '')

            if ReadHeader:
                if row.startswith('# Created by'):
                    experiment.update({'Version': row.split(",")[1].replace(' ','').strip('Version')})
                if row.startswith('#   Energy Axis'):
                    experiment.update({'Energy_Axis': row.split(":")[1].replace(' ','')})
                if row.startswith('#   Count Rate'):
                    experiment.update({'Count_Rate': row.split(": ")[1].replace(' ','').replace('per','/')})
                #
                if row.startswith('# Spectrum ID:'):
                    experiment.update({'Spectrum_ID': row.split(":")[1].replace(' ','')})
                    retd.update({"spectrum_id": experiment["Spectrum_ID"]})
                if row.startswith("# Analysis Method"):   
                    experiment.update({'Analysis_Method': row.split(":")[1].replace(' ','')})
                if row.startswith("# Analyzer:"):   
                    experiment.update({'Analyzer': row.split(":")[1].replace(' ','')})
                if row.startswith("# Analyzer Lens:"):   
                    experiment.update({'Lens_Mode': row.split(":")[1].replace(' ','')})
                if row.startswith("# Scan Mode:"):                                          
                    experiment.update({'Scan_Mode': row.split(":")[1].replace(' ','')})
                if row.startswith("# Curves/Scan:"): 
                    experiment.update({'Curves_Per_Scan': int(row.split(":")[1])})
                if row.startswith("# Values/Curve:"): 
                    experiment.update({'Values_Per_Curve': int(row.split(":")[1])})
                if row.startswith("# Dwell Time:"): 
                    experiment.update({'Dwell_Time': float(row.split(":")[1])})
                if row.startswith("# Excitation Energy:"):
                    experiment.update({'Excitation_Energy': float(row.split(":")[1].replace(' ',''))})
                if row.startswith("# Kinetic Energy:"):   
                    experiment.update({'Ek': float(row.split(":")[1])})
                if row.startswith("# Pass Energy"): 
                    experiment.update({'Ep': float(row.split(":")[1])})
                if row.startswith("# OrdinateRange"):
                    tmp = row.split(":")[1].strip(' ').strip('[').strip(']').split(',')
                    experiment.update({'Ordinate_Range': [float(tmp[0]), float(tmp[1])]})
                if row.startswith("# Comment"):
                    comment = row.split(":")[1].lstrip(" ")
                    experiment.update({"Comment": comment})
                #
                if row == '# Cycle: 0':
                    data_start_row = i
                if row.startswith('# ColumnLabels'):
                    try:
                        column_labels = row.split(':')[1][17:].split(' ')
                    except:
                        column_labels = ['?', '?']
                    ReadHeader = False
                #
                if row.startswith("# Parameter:"):
                    par = row.split(":")[1].split('=')[0].replace('" ', '').replace(' "', '')
                    parameters.append(par)
                if row.startswith("# Number of Scans:"):     ### <<<<<<<<<< ------------------ No leading # ???
                    experiment.update({'Number_of_scans': int(row.split(':')[1])})
            else:
                f.close()
                break
        experiment.update({'parameters': parameters})
        experiment.update({'Column_labels': column_labels})    
    
    # fix some stuff -----
    if experiment.get('Energy_Axis', '') == 'KineticEnergy': experiment.update({'Energy_Axis': 'Kinetic energy (eV)'})
    if experiment.get('Count_Rate', '') == 'Counts/Second': experiment.update({'Count_Rate': 'Intensity (counts/s)'})
    
    if data_start_row == -1:
        print(Fore.RED + "load(): I could not find the start row of the data. Sorry." + Fore.RESET); return {}
    
    # -------- Prepare arrays
    parameter_values = []
    for i in range(len(parameters)): parameter_values.append([])
    # This has created an list of empty lists, one list for each parameter and one for the parameter Step. Eg. [[], [], []]
    
    cycles = []
    curves = []
    steps = []
    non_energy_ordinate = []
    column1, column2 = [], []
    
    # Start loading
    with open(file_name, 'rb') as f:
        for i, row_ in enumerate(f):
            if i >= data_start_row:
                row = row_.decode(errors = 'ignore')
                row = row.replace('\r', '').replace('\n', '')
                
                if "Cycle" in row:
                    if not "Curve" in row:
                        cycles.append( int( row.split(":")[1] ) )
                    else:
                        curves.append( [int(row.split(", ")[0].split(":")[1]), int(row.split(", ")[1].split(":")[1])] )
                                
                if "Parameter" in row:
                    row_parts = row.split(": ")[-1].split(" = ")
                    par_name = row_parts[0].strip('"')
                    par_value = row_parts[-1].lower()
                    for j, p in enumerate(parameters):
                        if par_name == p:
                            if par_name == "NegativePolarity":   # This to translate strings to scalars.
                                if "off" in par_value.lower(): parameter_values[j].append(-1)
                                else: parameter_values[j].append(1)
                            else:
                                parameter_values[j].append(par_value)
                                if par_name == "Step": steps.append(par_value)
                
                if "NonEnergyOrdinate" in row:
                    non_energy_ordinate.append(float(row.split(":")[-1]))
                
                if not row.startswith("#") and len(row) > 0:
                    row_parts = row.split("  ")
                    column1.append(float(row_parts[0]))
                    column2.append(float(row_parts[1]))
    
    cycles = np.array(cycles)
    curves = np.array(curves)
    #parameter_values = np.asfarray(parameter_values)    # np.asfarray was removed from numpy 2.0. Realized by Sven Schemmelmann. 
    parameter_values = np.asarray(parameter_values, dtype = np.float64)
    non_energy_ordinate = np.unique(non_energy_ordinate)
    column1, column2 = np.array(column1), np.array(column2)
    
    return {"experiment": experiment, "parameter_values": parameter_values, "cycles": cycles, "curves": curves,
                "steps": steps, "non_energy_ordinate": non_energy_ordinate, "column1": column1, "column2": column2}
    
    
def load(*args, **kwargs):
    """
    Pass file_name (str) or raw_data (dict from loadXY()) as keyword argument.
    """

    if len(args) == 0:
        print(Fore.MAGENTA + "Data(): Pass a file name (xy-file) or a dict from loadXY()." + Fore.MAGENTA); return
    #
    raw_data, file_name, shup = None, None, None
    for a in args:
        if type(a) is dict: raw_data = deepcopy(a)
        if type(a) is str: file_name = a
    shup = kwargs.get("shup", False)
    keep_raw_data = kwargs.get("keep_raw_data", False)
    if not type(shup) is bool: shup = False
    if not type(keep_raw_data) is bool: keep_raw_data = False
    #
    only_raw = kwargs.get("only_raw", False)
    if not type(only_raw) is bool: only_raw = False   
    #
    if type(shup) is type(None): shup = False
    #
    if type(raw_data) is dict:
        # keys I expect to find in the raw_data dict from method loadXY()
        expected_keys = ["experiment", "parameter_values", "cycles", "curves", "steps", "non_energy_ordinate", "column1", "column2"]
        keys_in_dict = list(raw_data.keys())
        missing_keys = []
        for key in expected_keys:
            if not key in keys_in_dict: missing_keys.append(key)
        if len(missing_keys) > 0:
            print(Fore.RED + f"Data(): I could not find all the necessary keys in the passed dict.")
            print(f"        I'm missing {missing_keys}" + Fore.RESET); return
    elif type(file_name) is str:
        raw_data = loadXY(file_name)
        if len(raw_data) == 0: return
    else:
        return
    
    D = _DataObject()      # --------------          
                
    # --- save what we got so far
        
    D._addProperty("file_name", file_name)
    D._addProperty("experiment", raw_data["experiment"])
    D._addProperty("parameters", raw_data["experiment"]["parameters"])
        # ---
        
    if not only_raw:
        # --- first sort of data
        
        if D.experiment["Analyzer"] in CCD_ANALYZERS:
            num_axes = 0
            if len(raw_data["steps"]) == 0:   # the easy case, the one without Steps
                D._addProperty("data_type", "ccd_2d")
                #if not shup: print(f"Data type: {Fore.BLUE}{D.data_type}{Fore.RESET}")
                #
                n = len(raw_data["column1"])
                n1 = len(raw_data["cycles"])
                n2 = len(np.unique(raw_data["curves"].T[1]))
                if n1 == 1:
                    c1, c2 = raw_data["column1"].reshape(n2, int(n/n1/n2)), raw_data["column2"].reshape(n2, int(n/n1/n2))
                    D._addProperty("data_type", "ccd_2d")
                    D._addProperty("intensity", c2)
                    D._addProperty("intensity_label", raw_data["experiment"]["Column_labels"][1])
                    D._addProperty("axis0", raw_data["non_energy_ordinate"])
                    D._addProperty("axis0_label", "ordinate range")
                    D._addProperty("axis1", c1[0])
                    D._addProperty("axis1_label", D.experiment["Energy_Axis"])
                else: 
                    c1, c2 = raw_data["column1"].reshape(n1, n2, int(n/n1/n2)), raw_data["column2"].reshape(n1, n2, int(n/n1/n2))
                    D._addProperty("data_type", "ccd_3d")
                    D._addProperty("intensity", c2)
                    D._addProperty("intensity_label", raw_data["experiment"]["Column_labels"][1])
                    D._addProperty(f"axis0", raw_data["parameter_values"][0].T)
                    D._addProperty(f"axis0_label", raw_data["experiment"]["parameters"][0])
                    D._addProperty("axis1", raw_data["non_energy_ordinate"])
                    D._addProperty("axis1_label", "ordinate range")
                    D._addProperty(f"axis2", c1[0][0])
                    D._addProperty(f"axis2_label", D.experiment["Energy_Axis"])
                #
                #if len(np.shape(c1)) == 3:
                #    #there is hopefully only one parameter, and that parameter is probably the deflector so...
                #    D._addProperty(f"axis2", raw_data["parameter_values"][0].T)
                #    D._addProperty(f"axis2_label", raw_data["experiment"]["parameters"][0])
                #
                if not shup:
                    D.printDataType()
                    D.printAxesAndParameters()
                    
            else:
                print(Fore.MAGENTA + "Data(): I can not sort this data right now. Keeping the raw data." + Fore.RESET)
                keep_raw_data = True
            
        
        elif D.experiment["Analyzer"] in SPIN_ANALYZERS:
            if len(raw_data["steps"]) > 0:
                vpc = int(D.experiment.get("Values_Per_Curve", 1))
                
                # --- spin edc
                if len(D.parameters) == 2 and D.parameters[0] == "NegativePolarity" and D.parameters[1] == "Step" :
                    #
                    D._addProperty("data_type", "spin_edc")
                    #
                    sn0 = len(raw_data["column1"])
                    sn1 = len(np.unique(raw_data["parameter_values"][0]))
                    sn2 = len(np.unique(raw_data["parameter_values"][1]))
                    
                    shp = (sn2, int(sn0/sn2))
                    raw_data.update({"column1": np.reshape(raw_data["column1"], shp), 
                                        "column2": np.reshape(raw_data["column2"], shp)})
                    p0 = np.reshape(raw_data["parameter_values"][0], sn2)
                    p1 = np.reshape(raw_data["parameter_values"][1], sn2)
                    
                    D._addProperty("intensity", np.array(raw_data["column2"]))
                    D._addProperty("intensity_label", raw_data["experiment"]["Column_labels"][1])
                    D._addProperty( "axis0", raw_data["column1"][0] )
                    D._addProperty( "axis0_label", D.experiment["Energy_Axis"])
                    D._addProperty( "parameter0", raw_data["parameter_values"][0] )
                    D._addProperty( "parameter0_label", raw_data["experiment"]["parameters"][0])
                    
                    if not shup:
                        D.printDataType()
                        D.printAxesAndParameters()
                        
                
                # --- spin mdc
                elif len(D.parameters) == 3 and D.parameters[0] == "NegativePolarity" and "Shift" in D.parameters[1] and D.parameters[2] == "Step" and vpc == 1:
                    #
                    # Update this part. See how it is done for spin_mdc and do accordingly!
                    #
                    D._addProperty("data_type", "spin_mdc")
                    #
                    parv2 = np.unique(raw_data["parameter_values"][2])
                    parv1 = np.unique(raw_data["parameter_values"][1])
                    
                    imap = np.zeros([len(parv2), len(parv1)])
                    axis0_2d = np.copy(imap)
                    for i, v in enumerate(raw_data["column2"]):
                        for ip2, p2 in enumerate(parv2):
                            for ip1, p1 in enumerate(parv1):
                                if raw_data["parameter_values"][2][i] == p2 and raw_data["parameter_values"][1][i] == p1:
                                    imap[ip2][ip1] = v
                                    axis0_2d[ip2][ip1] = raw_data["parameter_values"][0][i]
                    D._addProperty("intensity", imap)
                    D._addProperty("intensity_label", raw_data["experiment"]["Column_labels"][1])
                    D._addProperty( "axis0", parv1 )
                    D._addProperty( "axis0_label", raw_data["experiment"]["parameters"][1])
                    D._addProperty("parameter0", axis0_2d.T[0])
                    D._addProperty("parameter0_label", raw_data["experiment"]["parameters"][0])
                    D._addProperty("parameter1", parv1)
                    D._addProperty("parameter1_label", raw_data["experiment"]["parameters"][1])
                    #
                    # ---- flip it so that it matches the edc (with polarity a )
                    
                    if not shup:
                        D.printDataType()
                        D.printAxesAndParameters()
                
                
                # --- spin map
                elif len(D.parameters) == 4 and D.parameters[0] == "NegativePolarity" and "Shift" in D.parameters[1] and "Shift" in D.parameters[2] and D.parameters[3] == "Step" and vpc == 1:
                    #
                    D._addProperty("data_type", "spin_map")
                    #
                    parv3 = np.unique(raw_data["parameter_values"][3])
                    parv2 = np.unique(raw_data["parameter_values"][2])
                    parv1 = np.unique(raw_data["parameter_values"][1])
                    parv0 = np.unique(raw_data["parameter_values"][0])
                    
                    imap = np.zeros([len(parv3), len(parv1), len(parv2)])
                    parv0_3d = np.copy(imap)
                    for i, v in enumerate(raw_data["column2"]):
                        i3 = np.where(raw_data["parameter_values"][3][i] == parv3)[0][0]
                        i2 = np.where(raw_data["parameter_values"][2][i] == parv2)[0][0]
                        i1 = np.where(raw_data["parameter_values"][1][i] == parv1)[0][0]
                        imap[i3][i1][i2] = v
                        parv0_3d[i3][i1][i2] = raw_data["parameter_values"][0][i]
                    D._addProperty("intensity", imap)
                    D._addProperty("intensity_label", raw_data["experiment"]["Column_labels"][1])
                    D._addProperty( "axis0", parv1 )
                    D._addProperty( "axis0_label", raw_data["experiment"]["parameters"][1])
                    D._addProperty( "axis1", parv2 )
                    D._addProperty( "axis1_label", raw_data["experiment"]["parameters"][2])
                    D._addProperty("parameter0", parv0_3d.T[0][0])
                    D._addProperty("parameter0_label", raw_data["experiment"]["parameters"][0])
                    
                    if not shup:
                        D.printDataType()
                        D.printAxesAndParameters()
                
                # -------
                elif len(D.parameters) == 6 and "Lens1" in D.parameters[0]  and "Lens2" in D.parameters[1] and "Lens3" in D.parameters[2] and "Lens4" in D.parameters[3] and "ScatteringEnergy" in D.parameters[4]:
                    #
                    # Parameter 4 (scattering energy) is the axis.
                    #
                    D._addProperty("data_type", "target_scattering_spectrum")
                    #
                    ns = len(raw_data["steps"])
                    parv0, parv1, parv2 = raw_data["parameter_values"][0], raw_data["parameter_values"][1], raw_data["parameter_values"][2]
                    parv3, parv4, parv5 = raw_data["parameter_values"][3], raw_data["parameter_values"][4], raw_data["parameter_values"][5]

                    #n00 = int(raw_data["experiment"]["Values_Per_Curve"])
                    n00 = vpc
                    N00 = np.arange(0,n00,1)
                    imap = np.reshape(raw_data["column2"], (ns, n00))   
                    
                    D._addProperty("intensity", imap)
                    D._addProperty("intensity_label", raw_data["experiment"]["Column_labels"][1])
                    D._addProperty("axis0", parv4)
                    D._addProperty("axis0_label", raw_data["experiment"]["parameters"][4])
                    
                    D._addProperty("parameter0", parv0)
                    D._addProperty("parameter0_label", D.parameters[0])
                    D._addProperty("parameter1", parv1)
                    D._addProperty("parameter1_label", D.parameters[1])
                    D._addProperty("parameter2", parv2)
                    D._addProperty("parameter2_label", D.parameters[2])
                    D._addProperty("parameter3", parv3)
                    D._addProperty("parameter3_label", D.parameters[3])
                    D._addProperty("parameter4", parv4)
                    D._addProperty("parameter4_label", D.parameters[4])   # This one is the same as axis0
                    
                    if not shup:
                        D.printDataType()
                        D.printAxesAndParameters()
                
                # --------- Ferrum arpes
                elif len(D.parameters) == 3 and D.parameters[0] == "NegativePolarity" and "Shift" in D.parameters[1] and D.parameters[2] == "Step" and vpc > 1:
                    if len(np.unique(raw_data["parameter_values"][0])) > 1:
                        print(f"{Fore.MAGENTA}Data():")
                        print("This appears to me to be data from a kind of Ferrum ARPES measurement. HOWEVER, the data seems ")
                        print("to include more than one target magnetization. I can not sort this data. The raw data will be ")
                        print("returned for you to sort yourself.")
                        print("If you have received this message please inform the staff so that they can spend a bit of time ")
                        print(f"updating this code. Thank you.{Fore.RESET}" )
                        keep_raw_data = True
                    else:
                        D._addProperty("data_type", "spin_arpes")
                        #
                        sn = len(raw_data["column1"])
                        #sn0 = len(np.unique(raw_data["parameter_values"][0]))
                        sn1 = len(np.unique(raw_data["parameter_values"][1]))
                        
                        shp = (sn1, int(sn/sn1))
                        raw_data.update({"column1": np.reshape(raw_data["column1"], shp), 
                                            "column2": np.reshape(raw_data["column2"], shp)})
                        #p0 = np.reshape(raw_data["parameter_values"][0], sn1)
                        p1 = np.reshape(raw_data["parameter_values"][1], sn1)
                        
                        D._addProperty("intensity", np.array(raw_data["column2"]))
                        D._addProperty("intensity_label", raw_data["experiment"]["Column_labels"][1])
                        D._addProperty( "axis0", raw_data["column1"][0] )
                        D._addProperty( "axis0_label", D.experiment["Energy_Axis"])
                        D._addProperty( "axis1", raw_data["parameter_values"][1]) 
                        D._addProperty( "axis1_label", raw_data["experiment"]["parameters"][1])
                        D._addProperty( "parameter0", raw_data["parameter_values"][0] )
                        D._addProperty( "parameter0_label", raw_data["experiment"]["parameters"][0])
                        D._addProperty( "parameter1", raw_data["parameter_values"][1] )
                        D._addProperty( "parameter1_label", raw_data["experiment"]["parameters"][1])
                        
                        if not shup:
                            D.printDataType()
                            D.printAxesAndParameters()
                        
                
                elif False:
                    pass
                    
                #
                else:
                    print(Fore.MAGENTA + "Data(): I can not sort this data right now. Keeping the raw data." + Fore.RESET)
                    keep_raw_data = True

                    
            else:
                print(Fore.MAGENTA + "Data(): I can not sort this data right now. Keeping the raw data." + Fore.RESET)
                keep_raw_data = True
        
        else:
            D._addProperty("data_type", "unknown")
            # --- done
    
    # ------------ end sort section
    if keep_raw_data or only_raw:
        D._addProperty("data_type", "raw")
        if not shup: print("Data(): I'm saving the raw data in...")
        for key in raw_data:
            D._addProperty("raw_" + key, raw_data[key])
            if not shup: print(f"  .raw_{key}")
        
    # extras -------
    if len(D.parameters) > 0: D.parameters = D.parameters[:-1]
    for key in ["Spectrum_ID", "Analysis_Method", "Analyzer", "Lens_Mode", "Scan_Mode", "Ek", "Ep", "Comment"]:
        D._addProperty(key, raw_data["experiment"].get(key, None))
    
    
    # ---------------------------------------------
    
    return D
    

 
            

        



                
            


# ================================================================================================================================
# ================================================================================================================================
# ================================================================================================================================
# ================================================================================================================================
# ================================================================================================================================
# ================================================================================================================================





class _DataObject():
    """
    """
    def _addProperty(self, name: str, value):
        setattr(_DataObject, name, property(self._getter(name), self._setter(name, value)))
        setattr(self, '__'+name, value)
    
    def _setter(self, name: str, value):
        def inner_setter(self, value):
            setattr(self, '__'+name, value)
        return inner_setter

    def _getter(self, name: str):
        def inner_getter(self):
            return getattr(self, '__'+name)
        return inner_getter
    
    def __init__(self, **kwargs):
        """
        """    
        self._addProperty("dopey", __version__)
    
    @property
    def info(self):
        dataInfo(self)
    
    @property
    def arrays(self):
        lst = self.listArrays()
        print(f"Arrays:")
        for attr in lst:
            shape = np.shape(self.__dict__["__"+attr])
            print(f"  {Fore.BLUE}{attr.ljust(20)}{Fore.RESET}shape={shape}")
            
    
    # --------------------------------------------------------------------------
    
    def printDataType(self):
        print(f"Data type:\n  {Fore.BLUE}{self.data_type}{Fore.RESET}")
        
    def printAxesAndParameters(self):
        print(f"Data, axes, and parameters:")
        for key in self.__dict__.keys():
            name, value = "", ""
            if "label" in key:
                name = key.replace("_label", "").replace("__", "")
                shape = np.shape(self.__dict__["__"+name])
                print(f"  {Fore.BLUE}{name.ljust(20)}{Fore.RESET}{self.__dict__[key].ljust(25)}shape={shape}")
    
    def listAttributes(self):
        lst = []
        for key in self.__dict__.keys(): lst.append(key.replace("__",""))
        return lst
    
    def listArrays(self):
        lst = []
        for key in self.__dict__.keys(): 
            if type(self.__dict__.get(key, None)) is np.ndarray:
                lst.append(key.replace("__",""))
        return lst
        
    
    
    
    




# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------


def dataInfo(D = None):
    try: _ = D.dopey
    except:
        print(f"{Fore.RED}info(): the argument must be a Data object."); return
    #
    for key in D.__dict__.keys():
        if key.startswith("__"):
            key_name = Fore.BLUE + key.replace('__', '').ljust(20) + Fore.RESET
            item = D.__dict__.get(key)
            typ = type(item)
            if typ is np.ndarray:
                t = "Array".ljust(15)
                s = f"shape = {np.shape(item)}".ljust(25)
                nk = f"{key}_label"
                print(f"{key_name}{t}{s}{D.__dict__.get(nk,'')}")
            #elif typ is str and not "_label" in key_name:
            #    t = "String".ljust(15)
            #    s = item.replace("\n", " ").replace("\t", " ")
            #    print(f"{key_name}{t}{s}")
            elif typ is float or typ is int or typ is np.float64:
                t = "Scalar".ljust(15)
                v = item
                print(f"{key_name}{t}{v}")
    print("-")
    #
    for key in D.__dict__.keys():
        if key.startswith("__"):
            key_name = Fore.BLUE + key.replace('__', '').ljust(20) + Fore.RESET
            item = D.__dict__.get(key)
            typ = type(item)
            if typ is dict:
                t = "Dictionary".ljust(15)
                print(f"{key_name}{t}")
            elif typ is str:# and "_label" in key_name:
                if not "dopey" in key_name:
                    t = "String".ljust(15)
                    s = item.replace("\n", " ").replace("\t", " ")
                    print(f"{key_name}{t}{s}")
            elif typ is list:
                t = "List".ljust(15)
                v = len(item)
                print(f"{key_name}{t}len = {v}")






# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

def pickleSave(D = object, file_name = "file.pickle"):
    """
    """
    try: typ = D.data_type
    except:
        print(f"{Fore.MAGENTA}The argument D is not a data object. I'll save it anyway, tho...{Fore.RESET}")
    try: file_name = str(file_name)
    except:
        print(f"{Fore.MAGENTA}The argument file_name must be a string. Setting it to 'file.pickle'.{Fore.RESET}")
        file_name = "file.pickle"
    if not file_name[-7:].lower() == ".pickle":
        print(f"{Fore.MAGENTA}Adding extension .pickle to the file name.{Fore.RESET}")
        file_name += ".pickle"
    try:
        with open(file_name, "wb") as f:
            pickle.dump(D, f, pickle.HIGHEST_PROTOCOL)
        print(f"{Fore.BLUE}Saved to file {file_name}{Fore.RESET}")
    except:
        print(f"{Fore.RED}Could not save the data to {file_name}{Fore.RESET}")

def pickleLoad(file_name = "file.pickle"):
    """
    """
    try: file_name = str(file_name)
    except:
        print(f"{Fore.MAGENTA}The argument file_name must be a string. Setting it to 'file.pickle'.{Fore.RESET}")
        file_name = "file.pickle"
    try:
        with open(file_name, "rb") as f:
            D = pickle.load(f)
        print(f"{Fore.BLUE}Loaded {file_name}{Fore.RESET}")
        try: typ = D.data_type
        except: typ = ""
    except:
        print(f"{Fore.RED}Could not load data from {file_name}{Fore.RESET}")
        return None
    if typ != "": print(f"{Fore.BLUE}Data type {typ}{Fore.RESET}")
    else: print(f"{Fore.BLUE}Unknown data type.{Fore.RESET}")
    return D