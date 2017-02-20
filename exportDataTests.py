from export import Export
import unittest
import csv

class ExportTests(unittest.TestCase):
    def testOne(self):
        exp = Export("titi")
        exp.writerow([1,2,3])
        # todo : read with csv and check data

    #todo : write a test with xlsx format
    #todo : write a fail test (with a .bla extention)

    #todo rewrite these tests with a header, chek the file and then append somthing and check the entire file
        

