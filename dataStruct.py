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
Represents a single location in the pile. May contain multiple foils.

'''
class position():
    pass

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

    def addCount(self,count):
        self.counts.append(count) #adds it to the array of counts

'''
Represents a single counting session for a single foil.
'''
class count():

    def __init__(self,start,end,counts):
        self.start=start
        self.end=end
        self.counts=counts
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return "Start: "+str(self.start)+" End: "+str(self.end)+" Counts:"+str(self.counts)

