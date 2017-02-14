""" 
 Maxim Dumortier
 Feb. 2017
 Cerisic, Mons, Belgium
 
 This class is used to export the data in the wanted way
 Available : 
  - CSV
  - Xlsx ? TODO
  - odt ? TODO
  - XML ? TODO

 """

from enum import Enum
import csv

class Type(Enum):
	"""
	Enum of the diffrent possible types of exporting
	"""
	
	CSV = 0
	XLSX = 1
	ODT = 2
	XML = 3


class Export:

	def __init__(self, file_path, type = "csv", header = "" ):
		if type.lower() == 'csv':
			self.type = Type.CSV
		elif type.lower() == 'xlsx':
			self.type = Type.XLSX
		elif type.lower() == 'odt':
			self.type = Type.ODT
		elif type.lower() == 'xml':
			self.type = Type.XML
		else:
			raise ValueError('Unknown type : ', type)
			
		self.file_path = file_path + "." + type.lower()
		
		source = open(self.file_path,'w')
		source.close()
		
		if header != "":
			self.writerow(header)
	
	def writerow(self, line):
		if(self.type == Type.CSV):
			with open(self.file_path,'a') as source:
				writer = csv.writer(source, delimiter=';', lineterminator='\n')
				writer.writerow(line)
		
