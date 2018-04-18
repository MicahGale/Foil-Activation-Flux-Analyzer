#!/bin/python3

'''
Copyright 2018 Micah Gale

Permission is hereby granted, free of charge, to any person 
obtaining a copy of this software and associated documentation 
files (the "Software"), to deal in the Software without 
restriction, including without limitation the rights to use, 
copy, modify, merge, publish, distribute, sublicense, and/or sell 
copies of the Software, and to permit persons to whom the Software 
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be 
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import xlrd
from  natAbund import *
from dataStruct import *
class foilExper():
    '''
    A class for parsing foil activation excel files
    '''
    def __init__(self, Name):
       self.book=xlrd.open_workbook(filename=Name)
       self.foil=''
    
    def parseFoils(self):
        if (self.foil==''):  #if foilMass isn't set populate it
            #pulls out the excel sheet with the foil properties
            sheet=self.book.sheet_by_name('foilData')
        
            #pulls out the header row and searches for the right columns
            #makes it tolerant to people moving around columns
            headers=sheet.row(0)
            maxR=   sheet.nrows  #get the number of rows
            massCol=foilExper.findColumn(headers,'Mass')
            foilCol=foilExper.findColumn(headers,'Foil')
            thickCol=foilExper.findColumn(headers,'Thickness')
            
            self.foil={}

            for i in range(1,maxR):
                #add all of the foil masses to the dictionary
                #TODO actually care about the materials which are used
                buffer=foil('In',sheet.cell(i,thickCol).value,sheet.cell(i,massCol).value)
                #parses the foil object properties
                self.foil[sheet.cell(i,foilCol).value]=buffer
        
    '''
    Parses the counts data, and stores them inside the appropriate foils
    '''
    def parseCounts(self):
        sheet=self.book.sheet_by_name('CountData')
        headers=sheet.row(0) #get the header row

        #finds the columns which are desired.
        foilCol=foilExper.findColumn(headers,'Foil')
        startCol=foilExper.findColumn(headers,'Count Start')
        endCol=foilExper.findColumn(headers,  'Count End')
        countCol=foilExper.findColumn(headers, 'Counts')
        
        end=sheet.nrows

        #parses the data
        for i in range(1,end):
            if( sheet.cell(i,foilCol).value!=''): #if an actual data row
                buffer=count(sheet.cell(i,startCol).value,sheet.cell(i,endCol).value,
                        sheet.cell(i,countCol).value)
                #add the counts to the appropriate foil
                self.foil[sheet.cell(i,foilCol).value].addCount(buffer)

    def parsePosition(self):
        sheet=self.book.sheet_by_name('PositionData')
        header=sheet.row(0)
        foilCol=foilExper.findColumn(header,'Foil')
        layerCol=foilExper.findColumn(header,'Layer')
        posCol=foilExper.findColumn(header,'Position')
        endCol=foilExper.findColumn(header,'Finish Activation')
        
        #pulls out all of the layer numbers
        #finds the max one and then useds that to initialize
        #the list of dictionaries
        layers=[]
        for cell in sheet.col(layerCol):
            if(cell.ctype==2): #if this cell is a number
                layers.append(cell.value)

        end= sheet.nrows
        #initializes the list with enough space to breath
        self.positions=[{} for i in range(0,int(max(layers))+1)]
        for i in range(1,end):
            if(sheet.cell(i,foilCol).value!=''): #if it isn't blank
                foil=sheet.cell(i,foilCol).value
                self.foil[foil].addEndTime(sheet.cell(i,endCol).value)
              
                #update the end of the irradiation for the foil
                layer=int(sheet.cell(i,layerCol).value)
                pos=int(sheet.cell(i,posCol).value)
                
                #check for initialization
                if layer not in self.positions or pos not in self.positions[layer]:
                    self.positions[layer][pos]=position(self.foil[foil]) 
                    #if the object doesn't exist make it and add the foil
                else: 
                    #otherwise just pop the appropriate foil onto the stack
                    self.positions[layer][pos].addFoil(self.foil[foil])

                
        
    '''
    Looks through the header row provided to find the desired column number

    @param header an array of the column headers
    @param target the string of the column that is desired
    @return the column number

    '''
    def findColumn(header,target):
       i=0
       for col in header:
           if(target in col.value):
               return i
           i=i+1
       return -1

test=foilExper('test_sigma.xlsx')
test.parseFoils()
test.parseCounts()
test.parsePosition()
print(test.positions[5][7].foil[0].calcN0())
