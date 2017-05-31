'''
Created on Apr 24, 2017

@author: datinkm1
'''
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import webbrowser, sys, requests
import os.path
from compiler.ast import Pass
import urllib2
import lxml.html
import re
import ast
import matplotlib.pyplot as plt
from selenium import webdriver
import StateClass as st
import PDFScraper as pdfScrape
import ExcelScraper as excScrape
import HtmlScraper as htmlScrape

#import pdf2text



singleSalaryList =[
25000.0,
50000.0,
75000.0,
100000.0,
125000.0,
150000.0,
175000.0,
200000.0]

marriedSalaryList = [
500000.0,
75000.0,
100000.0,
125000.0,
150000.0,
175000.0,
200000.0,
225000.0,
250000.0]

moneySearch = re.compile('(\$[0-9]+,*[0-9]*\.{0,1}[0-9]*)')
operators = ['x', '+', '-', '/']
operatorsText = ['multiple', 'add', 'subtract', 'divide']

#statusSearch = re.compile('([single]|[married]|[blind]|[deaf]|[age\s+65]|[dependent])')



'''
Purpose: scrape data from xml line
Input:  line(str) - xml line from xml doc
        tagName(str) - tag name to be extracted from line
Output: value(str) - data from xml tag
'''
def scrapeXMLTags(line, tagName):
    tag = '<' + tagName + '>'
    begin = line.find('<' + tagName + '>')
    end = line.find('</' + tagName + '>')
    value = line[begin + len(tag):end]
    if begin == -1 or end == -1:
        return
    return value

''' 
Purpose: download PDF documents from provided URL to specified directory
Input:  url(str) - url to pdf
        dir(str) - intended directory and file name of downloaded pdf
Output: None
'''
def downloadPDF(url, dir):
    response = urllib2.urlopen(url)
    file = open(dir, 'w')
    file.write(response.read())
    file.close()  

if __name__ == '__main__':
    #CA: Done
    #AR: Done, just form
    #DE: Done, form + instructions
    #AL: Done
    #AZ: in progress
    if len(sys.argv) > 1:
        #Get file path
        stateRecords = dict()
        stateCount = 0
        path = ' '.join(sys.argv[1:])
        dir = os.path.dirname(__file__)
        status = 0
        dependentNum = 0
        singleRate, marriedRate, singleExempt, marriedExempt, dependentExempt = excScrape.getStateIncomeTaxRateExemption(path)
        """Read xml file"""
        file = open('/Users/datinkm1/Desktop/stateDocumentation.xml', 'r')
        for line in file:
            statesTag = '<state>'
            if line.find(statesTag) != -1:
                stateObj = st.State()
                state = scrapeXMLTags(line, 'state')
                name = scrapeXMLTags(state, 'name')
                active = ast.literal_eval(scrapeXMLTags(state, 'active'))
                stateRecords[name] = stateObj
                form = ast.literal_eval(scrapeXMLTags(state, 'form'))
                if form == True:
                    formInfo = scrapeXMLTags(state, 'formInfo')
                    formDir = scrapeXMLTags(formInfo, 'dir')
                    formDir = os.path.join(dir,formDir)
                    formDownload = scrapeXMLTags(formInfo, 'download')
                    #if form PDF does not exist in directory, download and save
                    if os.path.isfile(formDir):
                        stateObj.setFormDir(formDir)
                    else:
                        downloadPDF(formDownload, formDir)
                        stateObj.setFormDir(formDir)   
                    stateObj.setFormHTML(formDownload)
                    formTable = ast.literal_eval(scrapeXMLTags(formInfo, 'hasTable'))
                    stateObj.setFormHasTable(formTable)
                instructions = ast.literal_eval(scrapeXMLTags(state, 'instructions'))
                if instructions == True:
                    instrInfo = scrapeXMLTags(state, 'instrInfo')
                    instrDir = os.path.join(dir, scrapeXMLTags(instrInfo, 'dir'))
                    instrDownload = scrapeXMLTags(instrInfo, 'download')
                    # if instruction PDF does not exist in directory, download and save
                    if os.path.isfile(instrDir):
                        stateObj.setInstrDir(instrDir)
                    else:
                        downloadPDF(instrDownload, instrDir)
                        stateObj.setInstrDir(instrDir)
                    stateObj.setInstrHTML(instrDownload)
                    instrTable = ast.literal_eval(scrapeXMLTags(instrInfo, 'hasTable'))
                    stateObj.setInstrHasTable(instrTable)
                website = scrapeXMLTags(state, 'website')
                stateObj.setStateWebsite(website)
                #get exemptAmount for state as specified TF-State-Individual-Income-Tax-Rates-Brackets-2017.xlsx
                rate = singleRate[name]
                if status == 0: #single
                    exemptAmount = excScrape.getExemptAmount(name, singleExempt)
                elif status == 1: #married
                    exemptAmount = excScrape.getExemptAmount(name, marriedExempt)
                elif status == 2: #dependents
                    exemptAmount = excScrape.getExemptAmount(name, dependentExempt, dependentNum)

                if (instructions == True or form == True) and active == True:
                    formText = pdfScrape.PDF2TXT(stateObj.getFormDir())
                    stringSearch = '(personal\s+exemption)|(personal\s+[tax\s+]*credit)|(dependent\s+exemption)|(exemption)'
                    referenceList = pdfScrape.getParagraphList(formText, stringSearch)
                    #referenceList = getParagraphList(formText, stringSearch)
                        #paragraphList, searchTerm, subtractionType = getParagraphList(formText, ['(personal\s+exemption)', '(personal\s+[tax\s+]*credit)', '(dependent\s+exemption)'])
                    pdfScrape.searchTaxFormParagraphs(stateObj, formText, referenceList)
                    #searchTaxFormParagraphs(stateObj, formText, referenceList)
    print 'Done'
                      
                     
                        
                        
                        
                            
        
            
    