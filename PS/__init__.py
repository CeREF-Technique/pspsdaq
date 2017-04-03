# Define here the link between the Name of the files and the classes
# Must be updated when a module is added
from PS.PS_2042_06B import PS204206B
from PS.PSI_5080_10A import PSI508010A

# dict of the powersupplies names and their corresponding class
classDict = {
    "EA_PS_2042_06B":EA_PS204206B,
    "EA_PSI_5080_10A":EA_PSI508010A
    "EA_PS_8360_10T":EA_PS836010T
    }

__all__ = list(classDict.keys())

