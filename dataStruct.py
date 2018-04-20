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

import math

#"constant" for converting days to seconds
DAY_TO_SEC=86400
'''
Represents a single location in the pile. May contain multiple foils.

'''
class position():
    
    def __init__(self,foil):
        self.foil=[foil]

    def addFoil(self,foil):
        self.foil.append(foil)

    def calcN0(self):

        N0=0
        sigmaAcum=0

        for foil in self.foil:
            ret=foil.calcN0()  
            N0=N0+ret[0]    #accumulates the total
            sigmaAcum=sigmaAcum+ret[1]**2  #add std dev in quadrature

        return (N0, math.sqrt(sigmaAcum)) #return tuple of value and std dev
    
    def calcRelFlux(self,start):
        flux=0
        sigmaAcum=0

        for foil in self.foil:
            ret=foil.calcRelFlux(start)
            flux=flux+ret[0]    #accumulates the total
            sigmaAcum=sigmaAcum+ret[1]**2  #add std dev in quadrature

        return (flux, math.sqrt(sigmaAcum)) #return tuple of value and std dev


'''
Represents a single foil. Holds it properties and the counts which were taken
of it
'''
class foil():
    
    def __init__(self,mat,thick,mass):
        self.mat=mat
        self.thick=thick
        self.mass=mass
        self.counts=[] #the child counts for this dohickey
   
    #adds the end time for the foil activation
    def addEndTime(self,end):
        self.end=end*DAY_TO_SEC

    def addCount(self,count):
        self.counts.append(count) #adds it to the array of counts

    def calcRelFlux(self,start):
        N0=self.calcN0() #calcs the initial foil activity
        #also loads up my hacky decay constants
        
        multiplier=(1-math.exp(-self.decayConst*(self.end-start)))/self.mass
        flux=N0[0]*multiplier
        sigma=N0[1]*multiplier #propogate counting uncertainty 

        return (flux, sigma)

    def calcN0(self):
        #TODO switch from hardcoded half-lives
        self.halfLife=3257.4 #[s] half life for Indium 116-m from NuDat 2.7
        self.decayConst=-math.log(0.5)/self.halfLife #calculate the decay constant

        counts=0
        denominator=0
        sigma=0

        for counter in self.counts:
            ret=counter.getCountContribs(self.end,self.decayConst)
            counts=counts+ret[0]
            denominator=denominator+ret[2]
        activity=(counts*self.decayConst)/denominator #[Bq]
        sigma=(math.sqrt(counts)*self.decayConst)/denominator

        return (activity,sigma)

'''
Represents a single counting session for a single foil.
'''
class count():

    def __init__(self,start,end,counts):
        global DAY_TO_SEC
        self.start=start*DAY_TO_SEC
        self.end=end*DAY_TO_SEC
        self.counts=counts
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return "Start: "+str(self.start)+" End: "+str(self.end)+" Counts:"+str(self.counts)

    '''
    returns the data necessary to combine the counts to get an activity term

    The formula used is:

    N_0=(Sum(counts)*lambda)/(e^(-lambda*t_1)-e^(-lambda*t_2))
    @param endAct - the end of activation t_0 in seconds and not days!!
    @param decayCNST- the decay constant lambda in s^-1
    @return touple (counts, sigma, exponential term)
    '''
    def getCountContribs(self,endAct,decayConst):
        sigma=math.sqrt(float(self.counts))
        decay=math.exp(-decayConst*(self.start-endAct))
        decay=decay-math.exp(-decayConst*(self.end-endAct))
        return (self.counts, sigma, decay)
