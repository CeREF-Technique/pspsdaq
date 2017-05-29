""" Maxim Dumortier
    First write : Feb 2015
    Adapted to ps2daq : april 2017
    Class for a special type watt meter
"""

from PS import powerSupply
from tkinter import StringVar
import serial          


class IES_ISW8300(powerSupply.PowerSupply):
    """ Classe definissant le comportement de la connection serie avec le wmetre
        A l'initialisation, il est necessaire de donner le numero du port COM
        Maxim Dumortier, CERISIC, 20/02/2015
    """
    # Name to display to the user
    name = "IES ISW8300 Wattmeter"

    def __init__(self, serial_name):
        self.port = serial_name

        self.baudrate = 9600                 # Default baud rate, also available : 1200
        self.timeout = 1                     # Default timeout, seconds
        self.parity = serial.PARITY_EVEN     # Default parity
        self.stopbits = serial.STOPBITS_ONE  # Default stop bits
        self.bytesize = serial.EIGHTBITS
        if serial_name != "":
            self.ser = serial.Serial(self.port, self.baudrate, \
                                 self.bytesize, self.parity, \
                                 self.stopbits, timeout=self.timeout, \
                                 xonxoff=True) # serial port
        else:
            self.ser = 0

        self.max_voltage = 500.0 # Volts
        self.max_current =  15.0 # Amps
        self.max_power = 1000.0 # Watts

        # Available measures for this Device
        # for each, must have label and units
        self.availableMeasures = { "id":      {"label":"ID",         "units":"",  "method":self.getID,
                                               "stringVar":StringVar(), "used":True, "format":"%s"},
                                   "version": {"label":"Version",    "units":"",  "method":self.getVersion,
                                               "stringVar":StringVar(), "used":True, "format":"%s"},
                                   "allData": {"label":"All Data",   "units":"",  "method":self.getAllData,
                                               "stringVar":StringVar(), "used":True, "format":"%s"},
                                   "value":   {"label":"Value",      "units":"",  "method":self.getValue,
                                               "stringVar":StringVar(), "used":True, "format":"%s"}
                                 }
    
    def send(self, message):
        """ Function to send data to the device
            :param message: message to send to the device
        """
        self.ser.write((message + "\r").encode())

    def readLine(self):
        """Function to read data from the Serial port
           :return: the read line
        """
        l = []  # Contains all the letters received for serial port
        try:
            while self.ser:
                r = self.ser.read(1).decode("ascii")
                #print(r)
                if r != "\r":  # look after the last char
                    l.append(r)
                else:
                    break
            word = ''.join(l)  # copy the char table into a string word
        except UnicodeDecodeError:
            print("fail to read in ASCII")
        
        return word
    
    def getSerialData(self, command):
        """ Get the asked data from the power supply through the Serial port
            :param command: command to get the required data
            :return: Give a byte array of the data answered
        """
        self.send(command)
        return self.readLine()

    def getID(self): # fonction cherchant l'info d'identification du wattmetre
        """ Methode permettant d'avoir l'identite du wattmetre """
        message = "*IDN?"
        return self.getSerialData(message)
    
    def getVersion(self):
        """ Methode permettant d'avoir la version du wattmetre """
        message = "VERSION?"
        return self.getSerialData(message)
    
    def getStatus(self):
        """ Methode permettant d'avoir le statut du wattmetre """
        message = "STATUS?"
        return self.self.getSerialData(message)
    
    def getAllData(self):
        """ Methode permettant d'avoir toutes les donnes du wattmetre, les 3 volts, 3 courants, etc """
        message = "DATA?"
        self.send(message)
        line = ""
        for i in range(7): # wattmeter send back 7 lines of values, each contains several values
            line += self.readLine() + "\n"
        return line

    def getValue(self):
        """ Methode permettant de recuperer les valeurs affiches sur le wattmetre"""
        message = "VAL?"
        return self.getSerialData(message)
    
    def getValueAndStatus(self):
        """ Methode permettant de recuperer les valeurs affiches sur le wattmetre ainsi que son statut"""
        message = "VAS?"
        return self.getSerialData(message)

    def setStartContinueMode(self):
        """ Permet d'activer l'envoie en continu de donnees, le wattmetre envoie les donnees des que la mesure est faite, cad tout les 400ms max"""
        message = "MA1"
        self.send(message)

    def setStopContinueMode(self):
        """ Permet d'arreter l'envoie en continu des donnees"""
        message = "MA0"
        self.send(message)

    def lock(self):
        """ Permet de verouiller la face avant du wattmetre"""
        message = "FAV0"
        self.send(message)
        
    def unlock(self):
        """ Permet de verouiller la face avant du wattmetre"""
        message = "FAV1"
        self.send(message)

    def getN(self):
        """Donne le rapport de de courant du transformateur externe entre dans le wmetre"""
        message = "N?"
        return self.getSerialData(message)
    
    def setN(self,N):
        """ Pemet de definir le rapport N du transformateur exterieur au wattmetre"""
        message = "SET:N=%04d"%(N) # format = SET:N=xxxx
        self.send(message)
        return self.getN()

    def setVolt(self):
        """ Affiche les differents voltages"""
        message = "VOLT"
        self.send(message)
        
    def setAmp(self):
        """ Affiche les differents amperages"""
        message = "AMP"
        self.send(message)
        
    def setWatt(self):
        """ Affiche les differents puissances actives"""
        message = "WATT"
        self.send(message)
        
    def setVar(self):
        """ Affiche les differents puissances reactives"""
        message = "VAR"
        self.send(message)
        
    def setVa(self):
        """ Affiche les differents puissances apparentes"""
        message = "VA"
        self.send(message)
        
    def setPF(self):
        """ Affichage du cosinus phi"""
        message = "PF"
        self.send(message)
        
    def setCap(self):
        """ Affichage de la capacitee"""
        message = "CAP"
        self.send(message)
        
    def setPH1(self):
        """ Affiche les donnes de la phase 1"""
        message = "PH1"
        self.send(message)
        
    def setPH2(self):
        """ Affiche les donnes de la phase 2"""
        message = "PH2"
        self.send(message)
        
    def setPH3(self):
        """ Affiche les donnes de la phase 3"""
        message = "PH3"
        self.send(message)

    def setSigma(self):
        """ Affiche les donnes de la somme des phases"""
        message = "SIGMA"
        self.send(message)

    def set15V(self):
        """ Setter le range de tension a 15V"""
        message = "SET:U1"
        self.send(message)
        
    def set50V(self):
        """ Setter le range de tension a 50V"""
        message = "SET:U2"
        self.send(message)
        
    def set150V(self):
        """ Setter le range de tension a 150V"""
        message = "SET:U3"
        self.send(message)
        
    def set500V(self):
        """ Setter le range de tension a 500V"""
        message = "SET:U4"
        self.send(message)
        
    def set500mA(self):
        """ Setter le range de courant a 0,5A"""
        message = "SET:I1"
        self.send(message)
        
    def set1500mA(self):
        """ Setter le range de courant a 1,5A"""
        message = "SET:I2"
        self.send(message)
        
    def set5A(self):
        """ Setter le range de courant a 5A"""
        message = "SET:I1"
        self.send(message)
        
    def set15A(self):
        """ Setter le range de courant a 15A"""
        message = "SET:I4"
        self.send(message)

    def setAutoVolt(self):
        """ Setter le range de tension de maniere automatique"""
        message = "AUTO_U"
        self.send(message)
        
    def setManuVolt(self):
        """ Setter le range de tension de maniere manuelle"""
        message = "MANU_U"
        self.send(message)

    def setAutoAmp(self):
        """ Setter le range de courant de maniere automatique"""
        message = "AUTO_I"
        self.send(message)

    def setManuAmp(self):
        """ Setter le range de courant de maniere manuelle"""
        message = "MANU_I"
        self.send(message)

    def getVolt(self):
        """ Methode renvoyant les donnees de voltages"""
        self.setVolt()
        return self.getValue()

    def getAmp(self):
        """ Methode renvoyant les donnees de courant"""
        self.setAmp()
        return self.getValue()
    
    def getWatt(self):
        """ Methode renvoyant les donnees de puissance active"""
        self.setWatt()
        return self.getValue()
    
    def getVar(self):
        """ Methode renvoyant les donnees de puissance reactive"""
        self.setVar()
        return self.getValue()
    
    def getVa(self):
        """ Methode renvoyant les donnees de puissance apparente"""
        self.setVa()
        return self.getValue()
    
    def getPF(self):
        """ Methode renvoyant les donnees de cosinus phi"""
        self.setPF()
        return self.getValue()
    
    def getCap(self):
        """ Methode renvoyant les donnees de capacites"""
        self.setCap()
        return self.getValue()
    
    def getPH1(self):
        """ Methode renvoyant les donnees de la phase 1"""
        self.setPH1()
        return self.getValue()
    
    def getPH2(self):
        """ Methode renvoyant les donnees de la phase 2"""
        self.setPH2()
        return self.getValue()
    
    def getPH3(self):
        """ Methode renvoyant les donnees de la phase 3"""
        self.setPH3()
        return self.getValue()
    
    def getSigma(self):
        """ Methode renvoyant les donnees de la somme des phase"""
        self.setSigma()
        return self.getValue()

    def normalBeep(self):
        """ Fait sonner un beep sur le watt metre, peut etre utile en cas de releve d'autres appareils simultanement
        ou pour signaler la fin d'une mesure"""
        message = "BEEP"
        self.send(message)

