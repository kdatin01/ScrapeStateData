'''
Created on Apr 24, 2017

@author: datinkm1
'''
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import webbrowser, sys, requests
import os.path
from compiler.ast import Pass
import numpy as np
import pandas as pd
import urllib2
import lxml.html
import re
import matplotlib.pyplot as plt
from collections import defaultdict
from collections import OrderedDict
import pandas as pd
from selenium import webdriver

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfdevice import PDFDevice
#import pdf2text
from cStringIO import StringIO

stateDict = defaultdict(list)
stateDict = {
'Alabama': ['AL', 'Ala.'],
'Alaska': ['AK'],
'Arizona': ['AZ', 'Ariz.'],
'Arkansas': ['AR', 'Ark.'],
'California': ['CA', 'Calif.'],
'Colorado': ['CO', 'Colo.'],
'Connecticut': ['CT', 'Conn.'],
'Delaware': ['DE', 'Del.'],
'Florida': ['FL', 'Fla.'],
'Georgia': ['GA', 'Ga.'],
'Hawaii': ['HI'],
'Idaho': ['ID'],
'Illinois': ['IL', 'Ill.'],
'Indiana': ['IN', 'Ind.'],
'Iowa': ['IA'],
'Kansas': ['KS', 'Kans.'],
'Kentucky': ['KY', 'Ky.'],
'Louisiana': ['LA', 'La.'],
'Maine': ['ME'],
'Maryland': ['MD', 'Md.'],
'Massachusetts': ['MA', 'Mass.'],
'Michigan': ['MI', 'Mich.'],
'Minnesota': ['MN', 'Minn.'],
'Mississippi': ['MS', 'Miss.'],
'Missouri': ['MO', 'Mo.'],
'Montana': ['MT', 'Mont.'],
'Nebraska': ['NE', 'Nebr.'],
'Nevada': ['NV', 'Nev.'],
'New Hampshire': ['NH', 'N.H.'],
'New Jersey': ['NJ', 'N.J.'],
'New Mexico': ['NM', 'N.M.'],
'New York': ['NY', 'N.Y.'],
'North Carolina': ['NC', 'N.C.'],
'North Dakota': ['ND', 'N.D.'],
'Ohio': ['OH'],
'Oklahoma': ['OK', 'Okla.'],
'Oregon': ['OR', 'Ore.'],
'Pennsylvania': ['PA', 'Pa.'],
'Rhode Island': ['RI', 'R.I.'],
'South Carolina': ['SC', 'S.C.'],
'South Dakota': ['SD', 'S.D.'],
'Tennessee': ['TN', 'Tenn.'],
'Texas': ['TX', 'Tex.'],
'Utah': ['UT'],
'Vermont': ['VT', 'Vt.'],
'Virginia': ['VA', 'Va.'],
'Washington': ['WA', 'Wash.'],
'West Virginia': ['WV', 'W.Va.'],
'Wisconsin': ['WI', 'Wis.'],
'Wyoming':['WY', 'Wyo.'],
'District of Columbia': ['DC', 'D.C.']}

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

moneySearch = re.compile('(\$[0-9]+,*[0-9]*\.*[0-9]*)')
operators = ['x', '+', '-', '/']
operatorsText = ['multiple', 'add', 'subtract', 'divide']

lookForward = [0, 1, 2]

status = ['single', 'married', 'blind', 'deaf', 'age 65', 'dependent']
statusKeyWords = '(self)|(spouse)|(single)|(married)|(number\s+of\s+[personal\s+]*exemptions)|(dependent)'
#statusSearch = re.compile('([single]|[married]|[blind]|[deaf]|[age\s+65]|[dependent])')

def PDF2TXT(path, pageNums = None):
    if pageNums != None:
        numList = int(pageNums[0]) - 1 #Must decrement by 1 to get actual page text (because page numbers are on the bottom of each pdf page)
        if len(pageNums) > 1:
            for i in range(1,len(pageNums)):
                numList += ',' + int(pageNums[i] - 1)
        print numList
        pagenos=set([numList])#[48,49,50])
    else:
        pagenos=set()#[48,49,50])
    text = 'txt'
    retstr = StringIO()
    codec = 'utf-8'
    password = ""
    maxpages = 11
    caching = True
    
    #open the PDF file
    fp = file(path, 'rb')
    #Create a PDF parser object associated with the file object
    parser = PDFParser(fp)
    #Create a PDF document object that stores the document structure and supply password for initialization(if needed)
    document = PDFDocument(parser, password)
    #Check if doc allows text extraction
    if not document.is_extractable:
        return 0
    #Create PDF Resource Manager object to store shared resources
    rsrcmgr = PDFResourceManager()
    #Set parameters for analysis
    laparams = LAParams(line_margin = 0.2, detect_vertical = True, all_texts = True, boxes_flow = 0.3)
    #Create PDF device object
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    #Create PDF interpreter object
    interpreter = PDFPageInterpreter(rsrcmgr, device)
     
    #Process each page contained in the pdf doc
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable = True):
        interpreter.process_page(page)
    
    text = retstr.getvalue()
    #print text
    text = re.sub('\s*\n', '\n', text).strip()
    text = re.sub('\n+', '\n', text).strip()
    print '__________________________________________________________________________________________________________________________________'
    print text
    #textLow = text.lower()
    
    fp.close()
    device.close()
    retstr.close()
    
    return text

def getExemptionFormInfo(text):
    text = text.lower()
    lineSplit = re.split('\n', text, flags=re.IGNORECASE)
    lineCount = 0
    lineTrack = []
    dependentAmount = 'NA'
    dependentOperator = 'NA'
    personalAmount = 'NA'
    personalOperator = 'NA'
    exemptions = []
        
        
    for line in lineSplit:
        if 'exemption' in line:
            lineTrack.append(lineCount)
        lineCount += 1
    for lineNum in lineTrack:
        if 'dependent exemption' in lineSplit[lineNum]:
            exemptionType = 'dependent'
            for i in range(0,5):
                currentLine = lineNum + i
                print lineSplit[currentLine]
                if '$' in lineSplit[currentLine]:
                    #get money amount from string using regex
                    money = moneySearch.search(lineSplit[currentLine])
                    dependentAmount =  money.group(0)
                    for op in operators:
                        if op in lineSplit[currentLine]:
                            searchTerm = '(' + op + ')'
                            operator = re.search(searchTerm, lineSplit[currentLine])
                            dependentOperator = operator.group(0)
                if dependentAmount != 'NA' and dependentOperator != 'NA':
                    dependentExemption = [exemptionType, dependentAmount, dependentOperator]
                    exemptions.append(dependentExemption)
                    break
        #deal with all exemptions that are not dependent exemptions
        if 'exemption' in lineSplit[lineNum] and 'dependent exemption' not in lineSplit[lineNum]:
            for i in range(0,5):
                currentLine = lineNum + i
                print lineSplit[currentLine]
                if 'personal' in lineSplit[currentLine]:
                    exemptionType = 'personal'
                    for j in range(0,8):
                        currentLine = lineNum + i + j
                        print lineSplit[currentLine]
                        if '$' in lineSplit[currentLine]:
                            money = moneySearch.search(lineSplit[currentLine])
                            personalAmount = money.group(0)
                            for op in operators:
                                if op in lineSplit[currentLine]:
                                    searchTerm = '(' + op + ')'
                                    operator = re.search(searchTerm, lineSplit[currentLine])
                                    personalOperator = operator.group(0)
                                    break
                    if personalAmount != 'NA' and personalOperator != 'NA':
                        personalExemption = [exemptionType, personalAmount, personalOperator]
                        exemptions.append(personalExemption)
                        break
    return exemptions

def recursiveSearch(text, termList, numList, lookAhead):
    textGroup = []
    statusSearch = '(self)|(spouse)|(single)|(married)|(number\s+of\s+[personal\s+]*exemptions)|(dependent))'
    term = termList.pop(0)
    nums = numList.pop(0)
    for y in nums:
        num = y
        if term == 'line':
            termSearch = '[' + term +']*' + '\s*' + num + '\s+'
        else:
            termSearch = term + '\s*' + num
        termSplit = re.split(termSearch, text) #FOR SOME REASON, NOT WORKING FOR part iii!!!!!!!!!!!!!!
        for l in range(1, len(termSplit)):
            print termSplit[l]
            textGroup.append(termSplit[l])
    if termList:
        for textSub in textGroup:
            txtGroup = recursiveSearch(textSub, termList, numList, lookAhead)
            return txtGroup
    else:
        return textGroup

def searchText(termList, numList, page, fileName, type):
    statusDict = dict()
    if page:
        x = termList.index('page')
        termList.pop(x)
        for y in numList[x]:
            numList.pop(x)
            pageNums = y
            instructText = PDF2TXT(fileName, pageNums)
            instructText = instructText.lower()
            wholeText = PDF2TXT(fileName)
            wholeText = wholeText.lower()
            lineSplit = re.split('\n', wholeText)
    else:
        instructText = PDF2TXT(fileName)
        instructText = instructText.lower()
        lineSplit = re.split('\n', instructText)        
    
    textGroup = recursiveSearch(instructText, termList, numList, lookForward)
    for text in textGroup:
        splitText = re.split('\n', text)
        for line in splitText:
            statusSearch = re.search(statusKeyWords, line)
            if statusSearch:
                for i in range(0, len(lineSplit)):
                    if line in lineSplit[i]:
                        status = statusSearch.group(0)
                        statPair = [status, type]
                        matchStatus = i
                        gotMatch = True
                        statusDict[matchStatus] = statPair
    return statusDict

def amountSearch(lines, x, status):
    statusAmount = ''
    operator = ''
    statusLineMatch = ''
    statusAmountPair = []
    print lines[x]
    for y in lookForward:
        moneySearch = re.search('\$([0-9]+,*[0-9]*\.*[0-9]*)', lines[x + y])
        if moneySearch:
            statusAmount = moneySearch.group(0)
            #operator must be on same line as amount
            operatorSearch = re.search('(x|multiply)\s+', lines[x + y])
            if operatorSearch:
                operator = operatorSearch.group(0)
        if statusAmount != '' and operator != '':
            statusAmountPair = [statusAmount, operator]
            statusLineMatch = x + y
        if statusAmount != '' and operator == '':
            operator = '+'
            statusAmountPair = [statusAmount, operator]
            statusLineMatch = x + y
    return statusAmountPair, statusLineMatch
                                    
def searchTaxFormParagraphs(text, refList):
    text = text.lower()
    print text
    lineSplit = re.split('\n', text)
    lookAround = [0, 1, -1, 2, -2, 3, -3, 4, -4]
    lookAroundOrdered = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
    matchStatus = -1
    depList = []
    statusAmount = ''
    operator = ''
    depAmount = ''
    depOperator = ''
    amountDict = dict()
    statusDict = dict()
    termDict = []
    gotMatch = False
    statusLineMatch = 0
    termList = []
    numList = []
    useInst = False
    pdfType = 'form'
    
                                
    x = 0
    for outer in refList:
        for out in outer:
            print len(out)
            if 'exemption' in out or 'credit' in out:
                subtractMethod = out
            else:
                if len(out) > 1:
                    #stack terms, assuming that one term will lead to finding the other terms.
                    for terms in out:
                        for term in terms:
                            if term == 'line' or term == 'box' or term == 'page' or term == 'part': 
                                termList.append(term)
                            elif term == True or term == False:
                                useInst = term
                            else:
                                numList.append(term) 
                else:
                    for terms in out:
                        for termx in terms:
                            if termx == 'line' or termx == 'box' or termx == 'page' or termx == 'part' or termx == 'None':
                                term = termx
                            elif termx == True or termx == False:
                                    useInst = termx
                            else:
                                stringSearch = termx
                if useInst == True:
                    if term == 'page':
                            pageNums = stringSearch   
                            instructText = PDF2TXT('/Users/datinkm1/Desktop/Alabama_Income_Instructions.pdf', pageNums)
                            statusSearch = '(single)'
                            amountDict = searchTaxInstructions(instructText, subtractMethod, statusKeyWords)
                            if amountDict:
                                gotMatch = True
                elif not termList:
                    termPair = [term, stringSearch]
                    termDict.append(termPair)
    if termList:
        gotMatch = False
        if 'page' in termList:
            page = True
            pdf = '/Users/datinkm1/Desktop/AlabamaIncomeTaxForm.pdf'
            pdfType = 'form' 
            statusDict = searchText(termList, numList, page, pdf, pdfType)
            
            #If no matches from tax form, look in tax instructions
            if not statusDict:
                page = True
                pdf = '/Users/datinkm1/Desktop/Alabama_Income_Instructions.pdf'
                pdfType = 'instructions'
                statusDict = searchText(termList, numList, page, pdf, pdfType)
                      
        else:
            page = False
            pdf = '/Users/datinkm1/Desktop/AlabamaIncomeTaxForm.pdf'
            pdfType = 'form'
            statusDict = searchText(termList, numList, page, pdf, pdfType)
            
            #If no matches from tax form, search in tax instructions
            if not statusDict:
                page = False
                pdf = '/Users/datinkm1/Desktop/Alabama_Income_Instructions.pdf'
                pdfType = 'instructions'
                statusDict = searchText(termList, numList, page, pdf, pdfType)   
    if termDict:
        for i in lineSplit:
            print repr(i)
            gotIn = False
            for termPair in termDict:
                term = termPair[0]
                stringSearch = termPair[1]
                if term == 'None': #no line, page, part or box numbers to look for
                    for word in stringSearch: 
                        stringMatch = re.search(word, i, re.IGNORECASE)#look for exemption/tax credit string in each line of the form
                        if stringMatch:
                            for y in lookAround: #if found, look 4 lines before to 4 lines after for one of the status words
                                if x + y < len(lineSplit):
                                    print lineSplit[x + y]
                                    statusSearch = re.search(statusKeyWords, lineSplit[x + y], re.IGNORECASE)
                                    if statusSearch:
                                        status = statusSearch.group(0)
                                        statPair = [status, pdfType]
                                        matchStatus = x + y
                                        statusDict[matchStatus] = statPair # add line number where status was found, and the status itself, in the dic                            
                                    
                else:
                    for word in stringSearch:
                        termSearch = '[' + term + ']*\s*' + word+'[A-Za-z]{0,1}\.?(\s+|$)'
                        termMatch = re.search(termSearch, i, flags = re.IGNORECASE|re.DOTALL)
                        if termMatch:
                            #Check if the surrounding lines contain any of the typical status keywords
                            for y in lookAround:
                                if x + y < len(lineSplit):
                                    statusSearch = re.search(statusKeyWords, lineSplit[x + y], re.IGNORECASE)
                                    if statusSearch:
                                        #print lineSplit[x + y]
                                        status = statusSearch.group(0)
                                        statPair = [status, pdfType]
                                        matchStatus = x + y
                                        statusDict[matchStatus] = statPair
                                        gotMatch = True
            x += 1
    
        x = 0
        if gotMatch == False:
            for i in lineSplit:
                for word in stringSearch:
                    termSearch = word
                    #search without term 'Line' or 'Box', should be a lot more matches
                    termMatch = re.search(termSearch, i, re.IGNORECASE)
                    if termMatch:
                        gotMatch = True
                        #because of large number of possible matches, status key term must be on same line as match(aka: No lookAround
                        statusSearch = re.search(statusKeyWords, i, re.IGNORECASE) #
                        if statusSearch:
                            status = statusSearch.group(0)
                            matchStatus = x
                            statusDict[matchStatus] = status
                x += 1
        for line, statusPair in statusDict.iteritems():
            amountDict = dict()
            status = statusPair[0]
            type = statusPair[1]
            if type == 'form':
                currLine = lineSplit[line]
                statusAmountPair, statusLineMatch = amountSearch(lineSplit, line, status)
            if type == 'instructions':
                
                instText = PDF2TXT('/Users/datinkm1/Desktop/Alabama_Income_Instructions.pdf')
                instText = instText.lower()
                instLine = re.split('\n', instText)
                currLine = instLine[line]
                for y in lookForward:
                    statusAmountPair, statusLineMatch = amountSearch(instLine, line, status)
            if statusAmountPair:
                amountDict[status] = statusAmountPair
            else:
                paragraphList, useInst = searchTermInLine(currLine)
                print paragraphList
                    
            
        #Was able to get statusAmount from form, will need to pull dependent info from instructions!  More complicated!!!
        for i in range(statusLineMatch, len(lineSplit)):
            line = lineSplit[i]
            print line
            for term, words in termDict.iteritems():
                for word in words:
                    termSearch = '[' + term + ']*' + '\s*' + word
                    termMatch = re.search(termSearch, line, re.IGNORECASE)
                    if termMatch:
                        print line
                        for y in lookAround:
                            dependentSearch = re.search('(dependents*[(s)]*)', lineSplit[i + y], re.IGNORECASE)
                            if dependentSearch:
                                #print lineSplit[x + y]
                                dependent = dependentSearch.group(0)
                                matchDep = i + y
                                depList.append(matchDep)
                        
        for line in depList:
            print lineSplit[line]
            for y in lookForward:
                moneySearch = re.search('\$([0-9]+)', lineSplit[line + y])
                operatorSearch = re.search('(x|multiply)', lineSplit[line + y])
                if moneySearch:
                    print lineSplit[line + y]
                    depAmount = moneySearch.group(0)
                    if operatorSearch:
                        print lineSplit[line + y]
                        depOperator = operatorSearch.group(0)
                    if depAmount != '' and depOperator != '':
                        statusPair = [depAmount, depOperator]
                        if dependent not in amountDict:
                            amountDict[dependent] = statusPair
            
    return amountDict

def searchTermInLine(line):
    paragraphList = []
    useInst = False
    if 'instruction' in line:
        useInst = True
    splitTerm = re.split('(line)|(box)|(page)|(part)', line)
    for y in range(1,len(splitTerm)):
        refList = []
        split = splitTerm[y]
        print split
        if split != None and split != '':
            romanNum = re.search('(x|ix|vii|vii|vi|v|iv|iii|ii|\s+i)', split)
            if split == 'line':
                term = 'line'
            elif split == 'box':
                term = 'box'
            elif split == 'page':
                term = 'page'
            elif split == 'part':
                term = 'part'
            elif any(char.isdigit() for char in split):
                if ',' in split:
                    commaSplit = re.split('\s*,\s*', split)
                    for x in commaSplit:
                        if x != '':
                            refSearch = re.search('([0-9]+[A-Za-z]*)', x)
                            ref = refSearch.group(0)
                            refList.append(ref)
                            outerRefSearch = re.search('[a-z]+', ref)
                            if outerRefSearch:
                                outerRef = re.search('([0-9]+)', ref)
                                refList.append(outerRef)
                    refListing = [term, refList, useInst]
                    paragraphList.append(refListing)
                else:
                    refSearch = re.search('([0-9]+[A-Za-z]*)', split)
                    ref = refSearch.group(0)
                    refList.append(ref)
                    outerRefSearch = re.search('[a-z]+', ref)
                    if outerRefSearch:#to capture parent reference number, along with any sub-reference numbers captured above
                        outerRef = re.search('([0-9]+)', ref)
                        refList.append(outerRef.group(0))
                    refListing = [term, refList, useInst]
                    paragraphList.append(refListing)
            elif romanNum:
                if ',' in split:
                    commaSplit = re.split('\s*,\s*', split)
                    for x in commaSplit:
                        if x != '':
                            refSearch = re.search('(x|ix|viii|vii|vi|v|iv|iii|ii|i)', x)
                            ref = refSearch.group(0)
                            refList.append(ref)
                    refListing = [term, refList, useInst]
                    paragraphList.append(refListing)
                else:
                    refSearch = re.search('(x|ix|viii|vii|vi|v|iv|iii|ii|i)', split)
                    ref = refSearch.group(0)
                    refList.append(ref)
                    refListing = [term, refList, useInst]
                    paragraphList.append(refListing)
    return paragraphList, useInst

def getParagraphList(text, stringSearch):
    #split on each newline
    text = text.lower()
    print text
    gotSearch = False
    lineSplit = re.split('\n', text, flags=re.IGNORECASE)
    #match = regex.search(text)
    subtractionType = ''
    referenceList = []
    for i in lineSplit:
        #search for Personal Exemption, Personal Tax Credit
        print repr(i)
        searchTerm = []
        for word in stringSearch:
            searchMatch = re.search(word, i, flags = re.IGNORECASE|re.DOTALL)
            if searchMatch:
                if 'exemption' in word:
                    subtractionType = 'personal\s+exemption'
                elif 'credit' in word:
                    subtractionType = 'personal\s+[tax\s+]*credit'
                paragraphList = []
                if 'line' in i or 'box' in i or 'page' in i or 'part' in i:
                    gotSearch = True
                    paragraphList, useInst = searchTermInLine(i)                     
                if gotSearch == False: #No line, box, page or part found in line!
                    refList = []
                    term = 'None'
                    refList.append(searchMatch.group(0))
                    refListing = [term, refList, useInst]
                    paragraphList.append(refListing)
            
                refPair = [subtractionType, paragraphList]
                referenceList.append(refPair)
                   
    print referenceList
    return referenceList
    #For tomorrow, consider making this function recursive!!!  Thereby getting rid of need for searchTaxFormParagraphs                    
                                       
                            
def searchTaxInstructions(text, term = None, searchList = None, scrapeTable = None):
    amountDict = dict()
    lookForward = [0, 1, 2]
    lookAround = [0, 1, -1, 2, -2, 3, -3, 4, -4]
    text = text.lower()
    print text
    lineSplit = re.split('\n', text, flags=re.IGNORECASE)
    
    if scrapeTable == True:
        print text
    if searchList != None:
        for n in range(0,len(lineSplit)):
            amount = ''
            operator = ''
            print lineSplit[n]
            termSearch = re.search(term, lineSplit[n])
            if termSearch:
                for i in lookAround:
                    print lineSplit[n+i]
                    statusSearch = re.search(searchList, lineSplit[n+i])
                    if statusSearch:
                        status = statusSearch.group(0)
                        for j in lookForward:
                            print lineSplit[n+i+j]
                            amountSearch = moneySearch.search(lineSplit[n+i+j])
                            operatorSearch = re.search('(x|multiply)', lineSplit[n+i+j])
                            if amountSearch:
                                amount = amountSearch.group(0)
                            if operatorSearch:
                                if operatorSearch.group(0) == 'multiply':
                                    operator = 'x'
                                else:
                                    operator = operatorSearch.group(0)
                        if amount != '' and operator !='':
                            statusAmountPair = [amount, operator]
                            if status not in amountDict:
                                amountDict[status] = statusAmountPair
                                statusLineMatch = n + i + j
                        if amount != '' and operator == '':
                            operator = '+'
                            statusAmountPair = [amount, operator]
                            if status not in amountDict:
                                amountDict[status] = statusAmountPair
                                statusLineMatch = n + i + j
    if not amountDict:
        print 'No matches found!!!  Problem with script!'                                
    
    return amountDict

def getStateIncomeTaxRateExemption(path):
    #stateTaxInfo = defaultdict(list)
    if not os.path.exists(path):
        return 'File does not exist'
        #print path
    stateTaxData = pd.read_excel(path, header=None, index_col=False, skiprows = 2)
    singleBracketDict = {}
    marriedBracketDict = {}
    singleRateDict = {}
    marriedRateDict = {}
    singleExemptDict = {}
    marriedExemptDict = {}
    dependentExemptDict = {}
    state = 'NAN'
            
    for row in stateTaxData.itertuples():
        if isinstance(row[2], float):
            if np.isnan(row[2]):
                marriedBracketDict = {}
                singleBracketDict = {}
                state = 'NAN'
                continue
        getSingleRate = False
        getSingleBracket = False
        getMarriedRate = False
        getMarriedBracket = False
        singleRate = 'NAN'
        marriedRate = 'NAN'
        getDummy = False
        getDeduct1 = False
        getDeduct2 = False
        getSingleExempt = False
        getMarriedExempt = False
        getDependentExempt = False
                
        for i in row:
            #print i
            if isinstance(i, unicode):
                stri = i.encode('ascii','ignore')
                if stri == 'n.a.' and getDeduct1 == True and getDeduct2 == False:
                    getDeduct2 = True
                if stri == 'n.a.' and getDeduct1 == False and getDeduct2 == False:
                    getDeduct1 = True
                if 'of federal' in stri and getSingleRate == True and getMarriedRate == False:
                    #When state has flat income tax rate, no brackets
                    getMarriedRate = True
                    #use regex to get % from string
                    rate = [float(s) for s in re.findall(r'\d+\.\d+', stri)]
                    marriedRate = rate[0]/100.0
                    marriedBracket = 0.0
                    marriedBracketDict[marriedRate] = marriedBracket
                    marriedRateDict[state] = marriedBracketDict
                if 'of federal' in stri and getSingleRate == False:
                    #When state has flat income tax rate, no brackets
                    getSingleRate = True
                    #use regex to get % from string
                    rate = [float(s) for s in re.findall(r'\d+\.\d+', stri)]
                    singleRate = rate[0]/100.0
                    singleBracket = 0.0
                    singleBracketDict[singleRate] = singleBracket
                    singleRateDict[state] = singleBracketDict
                if stri == 'none':
                    #When the state has no income tax
                    marriedRate = 0.0
                    singleRate = 0.0
                    marriedBracket = 0.0
                    singleBracket = 0.0
                    marriedBracketDict[marriedRate] = marriedBracket
                    marriedRateDict[state] = marriedBracketDict
                    singleBracketDict[singleRate] = singleBracket
                    singleRateDict[state] = singleBracketDict
                    break
                if '(c)' in stri: #Needed for pesky Tennessee and N.H
                    striNew = stri.replace(' (c)', '')
                    striNew = striNew.strip()
                else:
                    striNew = stri.strip()
                if state == 'NAN':
                    for stateName, abbrev in stateDict.iteritems():
                        if striNew == stateName:
                            state = stateName
                            #print striNew + '\t' + stateName
                            break
                        else:
                            for abb in abbrev:
                                if striNew == abb:
                                    state = stateName
                                    #print striNew + '\t' + stateName
                                    break
            elif isinstance(i, float) and not np.isnan(i):
                if getMarriedRate == True and getMarriedBracket == False and getSingleRate == True and getSingleBracket == True:
                    getMarriedBracket = True
                    marriedBracket = i
                    marriedBracketDict[marriedRate] = marriedBracket
                    marriedRateDict[state] = marriedBracketDict
                if i < 1.0 and getMarriedRate == False and getSingleRate == True and getSingleBracket == True:
                    getMarriedRate = True
                    marriedRate = i
                if getSingleRate == True and getSingleBracket == False:
                    getSingleBracket = True
                    singleBracket = i
                    singleBracketDict[singleRate] = singleBracket
                    singleRateDict[state] = singleBracketDict
                if i < 1.0 and getSingleRate == False:
                    getSingleRate = True
                    singleRate = i
            elif isinstance(i, int):
                if getSingleRate == True and getMarriedRate == True and getDeduct1 == True and getDeduct2 == True and getSingleExempt == True and getMarriedExempt == True and getDependentExempt == False:
                    getDependentExempt = True
                    dependentExemptAmount = i
                    dependentExemptDict[state] = dependentExemptAmount
                if getSingleRate == True and getMarriedRate == True and getDeduct1 == True and getDeduct2 == True and getSingleExempt == True and getMarriedExempt == False:
                    getMarriedExempt = True
                    marriedExemptAmount = i
                    marriedExemptDict[state] = marriedExemptAmount
                if getSingleRate == True and getMarriedRate == True and getDeduct1 == True and getDeduct2 == True and getSingleExempt == False:
                    getSingleExempt = True
                    singleExemptAmount = i
                    singleExemptDict[state] = singleExemptAmount
                if getSingleRate == True and getMarriedRate == True and getDeduct1 == True and getDeduct2 == False:
                    getDeduct2 = True
                if getSingleRate == True and getMarriedRate == True and getDeduct1 == False and getDummy == True:
                    getDeduct1 = True
                if getDummy == False:
                    getDummy = True
        #for state, rates in marriedRateDict.iteritems():
        #    print state
        #    for x, y in rates.iteritems():
        #        print str(x) + '\t>\t' + str(y)
        #    print '___________________________________'
    return singleRateDict, marriedRateDict, singleExemptDict, marriedExemptDict, dependentExemptDict

def calcStateIncomeTax(income, tax):
    leftOverIncome = income - tax
    percentageKept = (leftOverIncome/income)*100.0
    
    return tax, leftOverIncome, percentageKept
    
def getTaxOwed(income, rate):
    taxOwed = 0.0
    rateOrdered = OrderedDict(sorted(rate.items(), key=lambda t: t[1], reverse = True))
    for percent, min in rateOrdered.iteritems():
        if income > min:
            taxOwed += (income-min)*percent
            income = min-1
        elif float(income) <= min:
            continue
        #elif float(income) > min:
        #    taxRate = percent
    return taxOwed

def getExemptAmount(state, status, singleExemptDict, marriedExemptDict, dependentExemptDict, dependentNum):
    exemptAmount = 0
    if status == 0: # status is single, use singleExemptDict
        if state in singleExemptDict:
            exemptAmount += singleExemptDict[state]
    if status == 1: # status is married(filing jointly), use marriedExemptDict
        if state in marriedExemptDict:
            exemptAmount += marriedExemptDict[state]
    if dependentNum > 0: #status is 1 dependent
        if state in dependentExemptDict:
            dependentExemptAmount = dependentNum * dependentExemptDict[state]
            exemptAmount += dependentExemptAmount
    return exemptAmount
        
def getTaxableIncome(income, exemptAmount):
    return income-exemptAmount  

def getExemptStateRules(state):
    pathToPhantom = '/Users/datinkm1/Desktop/phantomjs-2.1.1-macosx/bin'
    browser = webdriver.PhantomJS(executable_path = '/Users/datinkm1/Desktop/phantomjs-2.1.1-macosx/bin/phantomjs')
    url = 'https://revenue.alabama.gov/incometax/2016_forms/16f40ablk.pdf'
    browser.get(url)
    
    browser.switch_to_default_content()
    frameset = browser.find_elements_by_tag_name('frame')
    for a in frameset:
        print a.get_attribute('h3')
    #browser.switch_to_frame(browser.find_element_by_xpath('/html/frameset/frame'))
    #browser.switch_to_default_content()
    browser.switch_to_frame("left")
    table = browser.find_element_by_tag_name('table')
    tbody = table.find_element_by_tag_name('tbody')
    
    body_rows = tbody.find_elements_by_tag_name('tr')
    for row in body_rows:
        data = row.find_elements_by_tag_name('td')
        for data1 in data:
            link = data1.find_elements_by_tag_name('a')
            file_row = []
            for datum in link:
                datumText = datum.text.encode('utf8')
                regex = re.compile('pers*', re.IGNORECASE)
                match = regex.search(datumText)
                if 'Personal Exemption' in datumText:
                    link =  datum.get_attribute('href')
                    browser.get(link)
                    browser.switch_to_default_content()
           
    #for tr in table:
    #    print tr.get_attribute('a')
    
    
    print state
    
    
    
    
    resp = requests.get('http://www.alabamatax.net/leftborder.htm')
    print state

    soup = BeautifulSoup(resp.content, 'html.parser')
    
    webText = soup.get_text()
    print soup
    print webText
    
    
    
    #print soup
    #for link in dom.xpath('//a/@href'):
    #    print link
    #personalExemption = soup.find_all("Personal Exemptions")
    

if __name__ == '__main__':
    #CA: Done
    #AR: Done, just form
    #DE: Done, uses form and instructions
    #AL: status done, working on dependents
    if len(sys.argv) > 1:
        #Get file path
        path = ' '.join(sys.argv[1:])
        singleRate, marriedRate, singleExempt, marriedExempt, dependentExempt = getStateIncomeTaxRateExemption(path)
        
        instructionsPresent = True #if false, there is no useful information to be scraped from the income tax instructions
        formPresent = True #if false, there is no useful information to be scraped from the income tax form
        hasTable = True #if pdf has table that needs to be scraped
        pdf = '/Users/datinkm1/Desktop/AlabamaIncomeTaxForm.pdf'
        
        for income in singleSalaryList:
            status = 0 #single
            dependentNum = 0
            
            for state, rate in singleRate.iteritems():
                exemptAmount = getExemptAmount(state, status, singleExempt, marriedExempt, dependentExempt, dependentNum)
                if instructionsPresent == True and formPresent == True:
                    formText = PDF2TXT(pdf)
                    referenceList = getParagraphList(formText, ['(personal\s+exemption)', '(personal\s+[tax\s+]*credit)', '(dependent\s+exemption)'])
                    #paragraphList, searchTerm, subtractionType = getParagraphList(formText, ['(personal\s+exemption)', '(personal\s+[tax\s+]*credit)', '(dependent\s+exemption)'])
                    rules = searchTaxFormParagraphs(formText, referenceList)
                    #instructText = PDF2TXT('/Users/datinkm1/Desktop/ArkansasIncomeTaxInstructions.pdf')
                    #text = searchTaxInstructions(instructText, hasTable)
                elif instructionsPresent == True and formPresent == False:
                    instructText = PDF2TXT('/Users/datinkm1/Desktop/ConnecticutIncomeTaxInstructions.pdf')
                    text = searchTaxInstructions(instructText, hasTable)
                else:
                    #currently setup for CA only!
                    formExemptions = getExemptionFormInfo(formText)
                
                
                getExemptStateRules(state)
                taxableIncome = getTaxableIncome(income, exemptAmount)
                singleTaxAmount = getTaxOwed(taxableIncome, rate)
                taxOut, remainder, percentage = calcStateIncomeTax(income, singleTaxAmount)
                print state + '\t' +str(income) + '\t' +  str(percentage) + '%'
                
        
        #for state, rate in singleRate.iteritems():
        #    print state
        #    for x, y in rate.iteritems():
        #        print str(x) + '\t>\t' + str(y)
        #    print '___________________________________'
        
            
                     
                        
                        
                        
                            
        
            
    