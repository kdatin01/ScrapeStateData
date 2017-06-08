'''
Created on Jun 1, 2017

@author: datinkm1
'''

class IncomeTaxStatus(object):

    def __init__(self):
        '''
        Constructor
        '''
    def getSingleExAmount(self):
        return self.singleExAmount
    def setSingleExAmount(self, amount):
        self.singleExAmount = amount
    def getSingleLowRange(self):
        return self.singleLowRange
    def setSingleLowRange(self, lowRange):
        self.singleLowRange = lowRange
    def getSingleHighRange(self):
        return self.singleHighRange
    def setSingleHighRange(self, highRange):
        self.singleHighRange = highRange
        
    def getMarriedExAmount(self):
        return self.marriedExAmount
    def setMarriedExAmount(self, amount):
        self.marriedExAmount = amount
    def getMarriedLowRange(self):
        return self.marriedLowRange
    def setMarriedLowRange(self, lowRange):
        self.marriedLowRange = lowRange
    def getMarriedHighRange(self):
        return self.marriedHighRange
    def setMarriedHighRange(self, highRange):
        self.marriedHighRange = highRange
        
    def getDependentExAmount(self):
        return self.dependentExAmount
    def setDependentExAmount(self, amount):
        self.dependentExAmount = amount
    def getDependentLowRange(self):
        return self.dependentLowRange
    def setDependentLowRange(self, lowRange):
        self.dependentLowRange = lowRange
    def getDependentHighRange(self):
        return self.dependentHighRange
    def setDependentHighRange(self, highRange):
        self.dependentHighRange = highRange
    
    