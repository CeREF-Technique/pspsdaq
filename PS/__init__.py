# Define here the link between the Name of the files and the classes
# Must be updated when a module is added
from PS.PS_2042_06B import PS204206B
from PS.PSI_5080_10A import PSI508010A

# dict of the powersupplies names and their corresponding class
classDict = {
    "PS_2042_06B":PS204206B,
    "PSI_5080_10A":PSI508010A
    }

__all__ = list(classDict.keys())

