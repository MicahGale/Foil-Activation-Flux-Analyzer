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
MIN_TO_SEC=60 #const for minutes to seconds
'''
Represents a single location in the pile. May contain multiple foils.

'''
class position():
    '''
    @param foil a single foil object at this postion
    @param X position in x in cm
    @param y ""
    @param z ""
    '''
    def __init__(self,foil,X,Y,Z):
        self.foil=[foil]
        self.X=X
        self.Y=Y
        self.Z=Z
    '''
    Appends another foil to list of foils at position

    @param the new foil object
    '''
    def addFoil(self,foil):
        self.foil.append(foil)
    
    '''
    Calculates the total initial activity here.
    Sums over all foils
    '''
    def calcN0(self):

        N0=0
        sigmaAcum=0

        for foil in self.foil:
            ret=foil.calcN0()  
            N0=N0+ret[0]    #accumulates the total
            sigmaAcum=sigmaAcum+ret[1]**2  #add std dev in quadrature

        return (N0, math.sqrt(sigmaAcum)) #return tuple of value and std dev
    
    '''
    Calculates the specific reaction rate for this position. 

    This should just be a pass through for a single foil position, but can
    handle multiple foils if neeeded. See foil.calcSpecRxRate() for math

    @param startAct- the start time of the foil activation in seconds.
    @return (rx,sigma) rx-the specific reaction rate
    '''
    def calcSpecRxRate(self,start):
        rx=0
        sigmaAcum=0

        for foil in self.foil: #iterate over all foils
            ret=foil.calcSpecRxRate(start)
            rx=rx+ret[0]
            sigmaAcum=sigmaAcum+ret[1]**2
        return (rx,math.sqrt(sigmaAcum))
    '''
    Just gets the total number of counts at positon
    @return total counts detected
    ''''
    def getCounts(self):
        sum=0
        for foil in self.foil:
            sum=sum+foil.getCounts()
        return sum

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        out=''
        i=0
        for foil in self.foil:
            out=out+"\nFoil "+str(i)+": "+foil.__str__()
            i=i+1
        return out


'''
Represents a single foil. Holds it properties and the counts which were taken
of it
'''
class foil():
    '''
    @param mat- foil material
    @param thick-foil thicness
    @param mass-foil mass in g
    '''
    def __init__(self,mat,thick,mass):
        self.mat=mat
        self.thick=thick
        self.mass=mass
        self.counts=[] #the child counts for this dohickey
   
    '''
    Adds the end time of the foil activation.
    @param the foil activation end time in days
    '''
    def addEndTime(self,end):
        self.end=end*DAY_TO_SEC
    '''
    Adds a count object to the current foil
    @param a completely initialized count object
    '''
    def addCount(self,count):
        self.counts.append(count) #adds it to the array of counts
    
    '''
    Calculates the specific reaction rate [s^-1g^-1](\phi\Sigma_c/ \rho)

    @param startAct- the starting time of the foil activation in seconds.
                    Not the time of the start of counting!

    '''
    def calcSpecRxRate(self,startAct):
        N0=self.calcN0() #gets quasi initial activity
        #must init deccayConst in calcN0
        #lambda/(m*(1-e^(-lambda t))
        #t is the total time in seconds of the foil activation
        divider=(self.mass*(1-math.exp(-self.decayConst*(self.end-startAct))))
        multiplier=self.decayConst/divider
        rx=N0[0]*multiplier
        sigma=N0[1]*multiplier

        return (rx,sigma)
    
    '''
    Calculates the Initial activity of the activated foil. 

    this isn't a true activity as the detector efficiency isn't factored in.
    Finds \eta N_0. Only gives meaningful data is the exact same detector
    setup is used for all foils.


    '''
    def calcN0(self):
        #TODO switch from hardcoded half-lives
        self.halfLife=3257.4 #[s] half life for Indium 116-m from NuDat 2.7
        self.decayConst=math.log(2)/self.halfLife #calculate the decay constant

        counts=0
        denominator=0
        sigma=0

        for counter in self.counts: #iterate overr all counting sessions
            #retrieves counting cotribution for counting session
            ret=counter.getCountContribs(self.end,self.decayConst)      
            counts=counts+ret[0]
            denominator=denominator+ret[2]
            sigma=sigma+(ret[1]/ret[2])**2
        if(counts>0):
            #completes the division of the accumulated sums
            activity=(counts)/denominator #[Bq]
            sigma=math.sqrt(sigma)
        else:            #if no counts were taken say it was 0
            activity=0
            sigma=0

        return (activity,sigma)
    '''
    Gets the total counts
    @return the total counts detected
    ''''
    def getCounts(self):
        sum=0
        for count in self.counts:
            sum=sum+count.counts
        return sum
    
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        out="Material: "+str(self.mat)+"\nThickness: "+str(self.thick)
        out=out+"\nMass: "+str(self.mass)+"\nEnd: "+str(self.end)
        i=0
        for count in self.counts:
            out=out+"\nCount "+str(i)+": "+count.__str__()
            i=i+1
        return out

'''
Represents a single counting session for a single foil.
'''
class count():
    '''
    Creates a new count object representing one contiguous counting session.

    @param start- the start time is days since some epoch. (Excel default)
                    Do not convert to seconds! Will be done internally
    @param end- the end time of the count. Same formatting as above
    @pararm counts - the number of raw counts
    @paramm bgCounts- number of background counts
    @param  bgTime   -length of background counting in minutes. Will convert
                     to seconds
    '''
    def __init__(self,start,end,counts,bgCounts,bgTime):
        global DAY_TO_SEC
        global MIN_TO_SEC

        self.start=start*DAY_TO_SEC
        self.end=end*DAY_TO_SEC
        bgTime= bgTime*MIN_TO_SEC  #converrts bg time to seconds

        #C_net=C_n-c_bg*t_cn/t_bg
        self.counts=counts-(self.end-self.start)*bgCounts/bgTime
        #calculates std dev
        #s_net=sqrt(s_n^2+(s_bg*t_cn/t_bg)^2)
        #
        #this simplifies to:
        #s_net=sqrt(C_n+C_bg*(t_cn/t_bg)^2)
        self.sigma=math.sqrt(
                float(counts+bgCounts*((self.start-self.end)/bgTime)**2)) 
        
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return "Start: "+str(self.start)+" End: "\
                +str(self.end)+" Counts:"+str(self.counts)

    '''
    returns the data necessary to combine the counts to get an activity term

    The formula used is:

    N_0=(Sum(counts)*lambda)/(e^(-lambda*t_1)-e^(-lambda*t_2))
    @param endAct - the end of activation t_0 in seconds and not days!!
    @param decayCNST- the decay constant lambda in s^-1
    @return touple (counts, sigma, exponential term)
    '''
    def getCountContribs(self,endAct,decayConst):
        
        #calculates:
        #(e^(-L*t_1)-e^(-Lt_2))
        decay=math.exp(-decayConst*(self.start-endAct))
        decay=decay-math.exp(-decayConst*(self.end-endAct))
        return (self.counts, self.sigma, decay)
