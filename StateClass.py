'''
Created on May 26, 2017

@author: datinkm1
'''

class State(object):
    '''
    class for state data from input XML and tax PDF
    '''


    def __init__(self):
        self.formDir = ''
        self.formHTML = ''
        self.formHasTable = False
        self.instrDir = ''
        self.instrHTML = ''
        self.instrHasTable = False
        self.stateWebsite = ''
    def setFormDir(self, formDir):
        self.formDir = formDir
    def getFormDir(self):
        return self.formDir
    def setFormHTML(self, formHTML):
        self.formHTML = formHTML
    def getFormHTML(self):
        return self.formHTML
    def setFormHasTable(self, formHasTable):
        self.formHasTable = formHasTable
    def getFormHasTable(self):
        return self.formHasTable
    def setInstrDir(self, instrDir):
        self.instrDir = instrDir
    def getInstrDir(self):
        return self.instrDir
    def setInstrHTML(self,instrHTML):
        self.instrHTML = instrHTML
    def getInstrHTML(self):
        return self.instrHTML
    def setInstrHasTable(self, instrHasTable):
        self.instrHasTable = instrHasTable
    def getInstrHasTable(self):
        return self.instrHasTable
    def setStateWebsite(self, stateWebsite):
        self.stateWebsite = stateWebsite
    def getStateWebsite(self):
        return self.stateWebsite
    def setIncomeTax(self, incomeTax):
        self.incomeTax = incomeTax
    def getIncomeTax(self):
        return self.incomeTax