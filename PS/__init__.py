# Define here the link between the Name of the files and the classes
# Must be updated when a module is added
from PS.EA_PS_2042_06B import EA_PS204206B
from PS.EA_PSI_5080_10A import EA_PSI508010A
from PS.EA_PS_8360_10T import EA_PS836010T
from PS.IES_ISW8300 import IES_ISW8300

# dict of the powersupplies names and their corresponding class
classDict = {
    "EA_PS_2042_06B":EA_PS204206B,
    "EA_PSI_5080_10A":EA_PSI508010A,
    "EA_PS_8360_10T":EA_PS836010T,
    "IES_ISW8300":IES_ISW8300
    }

__all__ = list(classDict.keys())

