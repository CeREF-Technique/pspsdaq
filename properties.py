""" 
 Maxim Dumortier
 April 2017
 Cerisic, Mons, Belgium
 
 This class is used to read and write data from the ps2daq properties file
 In order to read this, the csv library is used

 Here are just a few methods 

"""

import csv
import time
import logging

PROPERTIES_PATH = "./res/ps2daq.properties" # Path to the file


def is_int(s):
    """
    Function which test is a object is a int or not
    :return: True is it's an int (or it can be coverted to int) else False
    """
    try:
        int(s)
    except ValueError:
        return False

    return True


def is_float(s):
    """
    Function which test is a object is a float or not
    :return: True is it's an float (or it can be coverted to float) else False
    """
    try:
        s = s.replace(",",".")
        float(s)
    except ValueError:
        return False

    return True


def readProperties():
    """
    Function which can read the data from the properties file and return a dict of them (key, property)
    :return: a dict of the properties contained in the file
    """
    dict2Read = {} # initialize empty dict
    
    with open(PROPERTIES_PATH, 'r') as propFile:
        propReader = csv.reader(propFile, delimiter='=')
        
        for prop in propReader:
            try:
                if not str(prop[0]).startswith("#"):
                    if is_int(prop[1]):
                        dict2Read[prop[0]] = int(prop[1])
                    elif is_float(prop[1]):
                        dict2Read[prop[0]] = float(prop[1])
                    else:
                        dict2Read[prop[0]] = prop[1]
            except:
                if len(''.join(prop)) == 0 :
                    logging.error("Unable to parse an empty property")
                else:
                    logging.error("Unable to parse the property : " + ''.join(prop))
                pass
            
    return dict2Read


def writeProperties(dictToWrite):
    """
    Function which can write the data into the properties file (key, property)
    :param dictToWrite: dict of the values that must be written
    """
    with open(PROPERTIES_PATH, 'w') as propFile:
        writer = csv.writer(propFile, delimiter='=', lineterminator='\n')
        writer.writerow(["# Written on " + time.strftime("%Y/%m/%d - %H:%M:%S")])
        for prop in list(dictToWrite.keys()):
            writer.writerow([prop, dictToWrite[prop]])
            
        
