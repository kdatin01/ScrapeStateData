'''
Created on May 26, 2017

@author: datinkm1
'''

class IncomeTax(object):
    '''
    class for state income tax data
    '''


    def __init__(self):
        self.statList = []
        self.operatorList = []
        self.lowIncomeRangeList = []
        self.highIncomeRangeList = []
        self.subtractAmount = []
        self.subtractType = []
    def setStatusList(self, statList):
        self.statList = statList
    def appendStatus(self, stat):
        self.statList.append(stat)
    def getStatusList(self):
        return self.statList
    def setOperatorList(self, operatorList):
        self.operatorList = operatorList
    def appendOperator(self, operator):
        self.operatorList.append(operator)
    def getOperatorList(self):
        return self.operatorList
    def setLowIncomeRangeList(self, lowRangeList):
        self.lowIncomeRangeList = lowRangeList
    def appendLowIncomeRange(self, lowRange):
        self.lowIncomeRangeList.append(lowRange)
    def getLowIncomeRangeList(self):
        return self.lowIncomeRangeList
    def setHighIncomeRangeList(self, highRangeList):
        self.highIncomeRangeList = highRangeList
    def appendHighIncomeRange(self, highRange):
        self.highIncomeRangeList.append(highRange)
    def getHighIncomeRangeList(self):
        return self.lowIncomeRangeList
    def setSubtractAmountList(self, subtractAmountList):
        self.subtractAmount = subtractAmountList
    def appendSubtractAmount(self, subtractAmount):
        self.subtractAmount.append(subtractAmount)
    def getSubtractAmountList(self):
        return self.subtractAmount
    def setSubtractTypeList(self, subtractTypeList):
        self.subtractType = subtractTypeList
    def appendSubtractType(self, subtractType):
        self.subtractType.append(subtractType)
    def getSubtractTypeList(self):
        return self.subtractType