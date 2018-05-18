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
'''
TODO beautify graph
TODO add more comments
TODO update excel template
TODO add data type checks
'''


import xlrd
import csv
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats #for the linear regressioni
from scipy.optimize import least_squares #regression
import math
#from  natAbund import *
from dataStruct import position, foil, count, DAY_TO_SEC


class foilExper():
    '''
    A class for parsing foil activation excel files
    '''
    def __init__(self, Name):
       self.book=xlrd.open_workbook(filename=Name)
       self.foil=''
       self.parse()
    
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
        bgCol=foilExper.findColumn(headers,'Background')
        bgTimeCol=foilExper.findColumn(headers,'BG_TIME')
        
        end=sheet.nrows

        #parses the data
        for i in range(1,end):
            if( sheet.cell(i,foilCol).value!=''): #if an actual data row
                buffer=count(sheet.cell(i,startCol).value,sheet.cell(i,endCol).value,
                        sheet.cell(i,countCol).value,sheet.cell(i,bgCol).value,
                        sheet.cell(i,bgTimeCol).value)
                #add the counts to the appropriate foil
                self.foil[sheet.cell(i,foilCol).value].addCount(buffer)

    def parsePosition(self):
        sheet=self.book.sheet_by_name('PositionData')
        header=sheet.row(0)
        foilCol=foilExper.findColumn(header,'Foil')
        layerCol=foilExper.findColumn(header,'Layer')
        posCol=foilExper.findColumn(header,'Position')
        endCol=foilExper.findColumn(header,'Finish Activation')
        xCol=foilExper.findColumn(header,'X [cm]')
        yCol=foilExper.findColumn(header,'Y [cm]')
        zCol=foilExper.findColumn(header,'Z [cm]')
        
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
                X=sheet.cell(i,xCol).value
                Y=sheet.cell(i,yCol).value
                Z=sheet.cell(i,zCol).value

                #check for initialization
                if layer not in self.positions or pos not in self.positions[layer]:
                    self.positions[layer][pos]=position(self.foil[foil],X,Y,Z) 
                    #if the object doesn't exist make it and add the foil
                else: 
                    #otherwise just pop the appropriate foil onto the stack
                    self.positions[layer][pos].addFoil(self.foil[foil])
    '''
    Parses the start time for the experiment.
    '''
    def parseStart(self):
        global DAY_TO_SEC
        sheet=self.book.sheet_by_name('ExperimentInfo')
        header=sheet.row(0)
        col=foilExper.findColumn(header,'TimeStamp')
        header=sheet.col(0)
        row=foilExper.findColumn(header,'Source Insertion')
        self.start=sheet.cell(row,col).value*DAY_TO_SEC  #caches the
        #experiment start time in seconds

    def parse(self):
        self.parseFoils()
        self.parseCounts()
        self.parsePosition()
        self.parseStart()

    '''
    Pulls out the radial specific reaction rate data for a layer

    @param layer the layer to examine
    @return (pos,flux,sigma) Pos=position in x data
        flux=specific reaction rate
        sigma=uncertainty
    '''
    def getRadData(self,level):
        row=self.positions[level] #pull out underlying dict
        size=len(row)
        pos=np.zeros(size)
        flux=np.zeros(size)
        sigma=np.zeros(size)

        pointer=0

        for  key, val in row.items(): #iterate over the things
            try: #catches exception for unitialized object
                if(val.getCounts()>0): #tests that there is actual data aswell
                    pos[pointer]=val.X
                    ret=val.calcSpecRxRate(self.start)
                    flux[pointer]=ret[0]
                    sigma[pointer]=ret[1]
                    pointer=pointer+1
            except NameError: #if uninit have no data and don't care
                pass

        return (pos,flux,sigma)


    '''
    Plots the radial specific reaction rate for a given level


    @param level the level at which to do the radial traverse
    @param fileName the fileName to which to save the pdf do not include
    extension
    @param ax   the subplot object. This allows you to combine plots on a
        figure
    @param font the font specification for the axis labels
    <https://matplotlib.org/api/matplotlib_configuration_api.html#matplotlib.rc>
    @param save If true the plot will be saved to FileName
    @param xAxisLabel If true will add a X axis Label
    @param yAxisLabel if True will add y axis label. Usefule for making a
    common label
    @param title the title for the plot. Useful for combined plots
    '''
    def plotRadial(self, level,ax,fileName=None, font={'family':'normal',
            'weight':'normal',
                'size' :18},save=True,xAxisLabel=True, yAxisLabel=True,title=''):
        
        ret=self.getRadData(level)
        pos=ret[0]
        flux=ret[1]
        sigma=ret[2]
        #plot it!
        ax.errorbar(pos,flux,yerr=sigma, fmt='s',color='k',capsize=5) 
        #add labels
        if(xAxisLabel):
            ax.set_xlabel("Position on X[cm]",**font)
       
        if(yAxisLabel): #sets the yaxis
            ax.set_ylabel("Uncorrected Specific "\
                    "Reaction Rate\n($\\eta\\phi\\Sigma_c/\\rho$)[$s^{-1}g^{-1}]$", **font)
        plt.xlim((-105,105)) #statically sets the x-axis. Change for non-GEP
        ax.set_title(title,**font) #sets the title
        if(save):
            plt.savefig(fileName+'.pdf')
    
    '''
    Gets the axial spec. reaction rate data for a specific position.

    @param position the radial position to use
    @return (pos, flux,sigma) pos=axial position in z
            flux=spec reaction rate
            sigma=uncertainty
    '''
    def getAxialData(self,position):
        size=len(self.positions)-1
        pos=np.zeros(size)
        flux=np.zeros(size)
        sigma=np.zeros(size)
 
        pointer=0
 
        for  key, val in enumerate(self.positions): #iterate over the things
            if(val!={}):
                if(val[position].getCounts()>0):
                    pos[pointer]=val[position].Z
                    ret=val[position].calcSpecRxRate(self.start)
                    flux[pointer]=ret[0]
                    sigma[pointer]=ret[1]
                    pointer=pointer+1
        
        return (pos,flux,sigma)

    '''
    Plots the axial specific reaction rate for a given position
  
    @param level the level at which to do the radial traverse
    @param fileName the fileName to which to save the pdf do not include
    extension
    @param ax   the subplot object. This allows you to combine plots on a
        figure
    @param font the font specification for the axis labels
    <https://matplotlib.org/api/matplotlib_configuration_api.html#matplotlib.rc>
    @param save If true the plot will be saved to FileName
    @param xAxisLabel If true will add a X axis Label
    @param yAxisLabel if True will add y axis label. Usefule for making a
    common label
    @param If true will create a log-log plot else it will be lin-lin
    @param title the title for the plot. Useful for combined plots
    '''
    def plotAxial(self, position, ax,fileName=None, font={'family':'normal',
             'weight':'normal',
                 'size' :18},save=True,xAxisLabel=True,
                 yAxisLabel=True,logLog=False, title=''):
        
        ret= self.getAxialData(position) #gets axial data
        pos=ret[0]
        flux=ret[1]
        sigma=ret[2]
        
        #plot it!
        ax.errorbar(pos,flux,yerr=sigma,fmt='s',color='k',capsize=5) 
        #turn on or off log-log
        if(logLog):
            ax.set_yscale('log')
        #    ax.set_xscale('log')
        #add x-label
        if(xAxisLabel):
            ax.set_xlabel('Position in z [cm]',**font)

        #add the y-label
        if(yAxisLabel):
            ax.set_ylabel("Uncorrected Specific "\
                    "Reaction Rate\n($\\eta\\phi\\Sigma_c/\\rho$)[$s^{-1}g^{-1}]$",**font)
        
        ax.set_title(title,**font)
        if(save):
            plt.savefig(fileName+".pdf")
    
  
  
    '''
    Creates a csv table for viewing raw interpreted data

    '''
    def writeTable(self,fileName):
        # open file for writing
        with open(fileName, 'w') as file:
            dumper=csv.writer(file)
            dumper.writerow(['Layer','X','Y','Z','counts','$I_0$','Reaction Rate'
                ,'Error','Relative Error'])

            for key, layer in enumerate(self.positions): #iterate over layers
                if(layer!={}):
                    for key2,pos in layer.items(): #iterate over all positions
                        X=pos.X
                        Y=pos.Y
                        Z=pos.Z
                        counts=pos.getCounts()
                        I0=pos.calcN0()
                        rx=pos.calcSpecRxRate(self.start)
                        if(counts>0):
                            dumper.writerow([key,X,Y,Z,counts,I0[0],rx[0],rx[1],rx[1]/rx[0]])
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


'''
Represents an experimental Subcritical Pile
'''
class subCritPile():

    '''
    Creates an object which isn meant to analyze foil data for a sub-crit pile

    @param fileName the name of the xlsx file which contains the foil counts
    @param a- the width of the pile in X in cm
    @param b- the depth of the pile in Y in cm
    @param c- the height of the pile in Z above the source plane in cm
    '''
    def __init__(self,fileName,a,b,c):
        self.data=foilExper(fileName) #loads the data in
        self.a=a
        self.b=b
        self.c=c

    '''
    Goal function for sinh fit
    
    @param g the paramaters [0]A [1]gamma
    y=Asinh(gamma(c-x))
    @param x xvalue
    @param y actual y value of data
    '''
    def goalSinh(self,g,x,y):
        return g[0]*np.sinh(g[1]*(self.c-x))-y

    '''
    Goal function for cos amplitude fit

    @param g- the paramters [0]A
    @param x x-value
    @param y y-value from data
    '''
    def goalCos(self,g,x,y):
        return g[0]*np.cos(math.pi*x/self.a)-y

    '''
    Calculates \gamma_{1,1} stores to self.gamma
    
    gamma[0] is amplitude of mode. gamma[1] is the \gamma

    @param position the radial position to use
    '''
    def calcFundGamma(self,position):
        
        ret=self.data.getAxialData(position)

        pos=ret[0]
        flux=ret[1]

        pointer=0
                    
        #self.gamma,self.Intercept,rval,pval,self.gamStdErr=stats.linregress(pos,flux)
        x0=np.ones(2)
        x0=[10, 0.02]
        fit= least_squares(self.goalSinh, x0, args=(pos[2:],flux[2:]))
        print(fit.x) 
        self.gamma=fit.x
    
    '''
    Plots the axially fitted function on the given subplot

    Note: pulls out self.gamma must be invoked after self.calcFundGamma
    
    @param ax the subplot object for plotting the figure
    @param printGamma- will print gamma value on the figure if true
    '''
    def plotAxialFunc(self,ax,printGamma=True):
        x=np.linspace(0,self.c,100)
        if(printGamma):
            ax.text(200,30,"$\\gamma_{1,1}$=%.5f" %self.gamma[1],fontsize=15)
        
        line=self.gamma[0]*np.sinh(self.gamma[1]*(self.c-x))
        ax.plot(x,line,color='k')
    '''
    Calculates the Material Buckling, and the critical Reactor size.

    Note: uses self.gamma needs to be invoked after self.calcFundGamma.
    
    @return (Bm2,s) Bm2=B_m^2-material buckling, s=side length of critical
                    reactor cube
    '''
    def calcGeoBuckle(self,position):
        Bm2=(math.pi/self.a)**2+(math.pi/self.b)**2-self.gamma[1]**2
        
        s=np.sqrt(3)*math.pi/math.sqrt(Bm2)

        return(Bm2,s) 
    
    '''
    Fits the fundamental cosine to the data.

    @param layer -the layer to examine
    @return the amplitude of the fundamental mode
    '''
    def fitFundRadial(self,layer):
        ret=self.data.getRadData(layer) #pulls out the radial data desired
        
        x0=[1] #guess 1 first

        fit=least_squares(self.goalCos,x0, args=(ret[0],ret[1])) #fits data
        
        return fit.x[0] #return the amplitude

    '''
    Plots the cosine fit on the given plot.

    @param ax the given subplot to print on
    @param A the amplitude of the cosine from the fit before
    '''
    def plotFundRad(self,ax,A):
        
        x=np.linspace(-self.a/2,self.a/2,100) #make dummy x
        line=A*np.cos(math.pi*x/self.a) #defines the line function
        ax.plot(x,line,color='k') #plots it
