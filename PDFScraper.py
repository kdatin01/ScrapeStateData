import re
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfdevice import PDFDevice
from cStringIO import StringIO
import StateClass as st
import IncomeTaxClass as tax

lookForward = [0, 1, 2]
lookForwardMore = [0, 1, 2, 3, 4, 5]
lookAround = [0, 1, -1, 2, -2, 3, -3, 4, -4]
statusSearchSmall = '(single)|(married)|(dependent)|(number\s+of\s+[personal\s+]*exemptions)'
statusKeyWords = '(self)|(spouse)|(single)|(married)|(number\s+of\s+[personal\s+]*exemptions)|(dependent)'
statusKeyWords_NC = 'self|spouse|single|married|number\s+of\s+[personal\s+]*exemptions|dependent|personal'

'''
Purpose: Read PDF document in
Input:  path(str) - path to PDF doc to be read
        pageNums(str) - pages of pdf to be read, if specified
Output: text(str) - text from PDF document
'''
def PDF2TXT(path, pageNums = None):
    if pageNums != None:
        numList = int(pageNums[0]) - 1 #Must decrement by 1 to get actual page text (because page numbers are on the bottom of each pdf page)
        if len(pageNums) > 1:
            for i in range(1,len(pageNums)):
                numList += ',' + int(pageNums[i] - 1)
        pagenos=set([numList])#[48,49,50])
    else:
        pagenos=set()#[48,49,50])
    retstr = StringIO()
    codec = 'utf-8'
    password = ""
    maxpages = 50
    caching = True
    
    #open the PDF file
    fp = open(path, 'rb')
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
    text = re.sub('\s*\n', '\n', text).strip() #strip out excess whitespace
    text = re.sub('^\n+', '', text, flags=re.MULTILINE).strip() #strip out excess newlines
    text = re.sub('^00\n+','', text, flags=re.MULTILINE).strip() #strip out lines of just zeroes
    text = re.sub('^[0-9][A-Za-z]{0,1}\n','',text, flags=re.MULTILINE).strip()
    text = re.sub('^\([A-Za-z]+\)\n','',text, flags = re.MULTILINE).strip()
    
    fp.close()
    device.close()
    retstr.close()
    
    return text

'''
Purpose: Recursive function to search for successive terms in a block of text.
Input:  text(str) - text block to be searched
        termList(list) - list of terms to search for in text block
        numList(list) - list of numbers associated with terms
        lookAhead(list) - list of numbers idicating how far ahead of current line to be searched.
Output: txtGroup(list) - 
'''
def recursiveSearch(text, termList, numList, lookAhead):
    textGroup = []
    statusSearch = '(self)|(spouse)|(single)|(married)|(number\s+of\s+[personal\s+]*exemptions)|(dependent))'
    term = termList.pop(0)
    nums = numList.pop(0)
    for y in nums:
        num = y
        termSearch = '(^|\s+|' + term + '\s*)' + num + '\s+'

        termSplit = re.split(termSearch, text) #FOR SOME REASON, NOT WORKING FOR part iii!!!!!!!!!!!!!!
        for l in range(1, len(termSplit)):
            textGroup.append(termSplit[l])
    if termList:
        for textSub in textGroup:
            txtGroup = recursiveSearch(textSub, termList, numList, lookAhead)
            return txtGroup
    else:
        return textGroup

'''
Purpose: search for list of terms in pdf text
Input:  termList(list) - list of terms to be seached for
        numList(list) - list of numbers associated with terms
        page(bool) - indicates if page is present in term list
        fileName(str) - directory of pdf to be searched in
        type(str) - pdf document type
Output: statusDict(dict) - made up of line numbers (keys), status found in that line of text, and the pdf type where the status is found.
'''
def termListSearchText(termList, numList, page, fileName, type, subtractMethod):
    statusDict = dict()
    recTermList = termList[:]
    recNumList = numList[:]
    subOrig = subtractMethod[0]
    for sub in subtractMethod:
        if sub != subOrig:
            print 'Subs are different!'
    if page:
        x = recTermList.index('page')
        recTermList.pop(x)
        for y in recNumList[x]:
            recNumList.pop(x)
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
    
    textGroup = recursiveSearch(instructText, recTermList, recNumList, lookForward)
    if textGroup:
        for text in textGroup:
            splitText = re.split('\n', text)
            for line in splitText:
                statusSearch = re.search(statusKeyWords, line)
                if statusSearch:
                    for i in range(0, len(lineSplit)):
                        if line in lineSplit[i]:
                            status = statusSearch.group(0)
                            statPair = [status, type, subOrig]
                            matchStatus = i
                            gotMatch = True
                            statusDict[matchStatus] = statPair
    else:
        for x in range(0, len(termList)):
            term = termList[x]
            for num in numList[x]:
                searchTerm = '(^|\s+|' + term + '\s*)' + num+'[A-Za-z]{0,1}\.?(\s+|$)'
                statusDict = searchForStatus(lineSplit, type, searchTerm, statusDict, subOrig)
    return statusDict

'''
Purpose: extract all table data from a list of text
Input:  textLines(list) - text block, split into lines
Output: amountList(list) - list of money amounts
        lowRange(list) - low end range limit associated with money amount
        highRange(list) - high range limit associated with money amount
        listColNames(list) - list of column names in table
        rangeExists(bool) - indicates if a range was present in table
'''
def extractTableData(textLines):
    colDict = dict()
    delimiter = '\s*-\s*'
    listColNames = []
    rangeList = []
    amountList = []
    lowRange = []
    highRange = []
    colCounter = 0
    noNum = 0
    rangeExists = False
    
    for x in range(0,len(textLines)):
        if any(char.isdigit() for char in textLines[x]):
            if '-' in textLines[x]:
                textNew = textLines[x].replace(',','')
                rangeExists = True
                noNum = 0
                numberSplit = re.split(delimiter, textNew)
                if len(numberSplit) == 2:
                    if float(numberSplit[0]) < float(numberSplit[1]):
                        lowRange.append(numberSplit[0])
                        highRange.append(numberSplit[1])
                    elif float(numberSplit[0]) > float(numberSplit[1]):
                        lowRange.append(numberSplit[1])
                        highRange.append(numberSplit[0])
                    rangeNum = [numberSplit[0], numberSplit[1]]
                    rangeList.append(rangeNum)
                    colFilled = True
            elif 'over' in textLines[x]:
                noNum = 0
                getNumber = re.search('(\$*[0-9]+,*[0-9]*\.{0,1}[0-9]*)', textLines[x])
                if getNumber:
                    lowRange.append(getNumber.group(0))
                    highRange.append('+')
                    rangeNum = [getNumber.group(0), 'inf']
                    rangeList.append(rangeNum)
                    colFilled = True
            elif 'under' in textLines[x]:
                noNum = 0
                getNumber = re.search('(\$*[0-9]+,*[0-9]*\.{0,1}[0-9]*)', textLines[x])
                if getNumber:
                    lowRange.append('0.00')
                    highRange.append(getNumber)
                    colFilled = True
            elif ',' in textLines[x]:
                noNum = 0
                textNew = textLines[x].replace(',','')
                if textNew.isdigit():
                    getNumber = re.search('(\$*[0-9]+,*[0-9]*\.{0,1}[0-9]*)', textLines[x])
                    if getNumber:
                        amountList.append(getNumber.group(0))
                        colFilled = True
            elif textLines[x].isdigit():
                noNum = 0
                getNumber = re.search('(\$*[0-9]+,*[0-9]*\.{0,1}[0-9]*)', textLines[x])
                if getNumber:
                    amountList.append(getNumber.group(0))
                    colFilled = True
            else:
                noNum += 1
                if amountList and noNum > 3:
                    return amountList, lowRange, highRange, listColNames, rangeExists
        else:
            if x < 1:
                if 'amount' in textLines[x]:
                    colName = 'salary'
                elif 'dependent' in textLines[x] or 'exemption' in textLines[x]:
                    colName = 'exemption'
                elif 'more' in textLines[x]:
                    colName = 'lowRange'
                elif 'less' in textLines[x]:
                    colName = 'highRange'
                listColNames.append(colName)
                colFilled = False
            else:
                if colFilled == True:
                    if 'amount' in textLines[x]:
                        colName = 'salary'
                    elif 'dependent' in textLines[x] or 'exemption' in textLines[x]:
                        colName = 'exemption'
                    elif 'more' in textLines[x]:
                        colName = 'lowRange'
                    elif 'less' in textLines[x]:
                        colName = 'highRange'
                    listColNames.append(textLines[x])
                    colFilled = False
                    noNum += 1
                    rangeList = []
                else:
                    noNum += 1
                if amountList and noNum > 3: 
                    #if there have been no read numbers in 3 lines of text, assume the whole table has been read
                    lastCol = listColNames.pop()
                    return amountList, lowRange, highRange, listColNames, rangeExists 
                
'''
Purpose: search text block for string(refTerm), then find is status key word can be found near to refterm position in text block
Input:  text(list) - block of text to be searched, split into lines
        pdfType(str) - type of pdf doc to be searched
        refTerm(str) - regex string searched for in text
        dictionary(dict) - what is currently stored in statusDict
Output: statusDict(dict) - dictionary of line numbers and status keywords found near the reference term in the text block
'''
def searchForStatus(text, pdfType, refTerm, dictionary, subtractMethod):
    statusDict = dict(dictionary)
    for x in range(0, len(text)):
        gotIn = False
        stringMatch = re.search(refTerm, text[x], re.IGNORECASE)#look for exemption/tax credit string in each line of the form
        if stringMatch:
            for y in lookAround: #if found, look 4 lines before to 4 lines after for one of the status words
                status = []
                if x + y < len(text):
                    statusFind = re.findall(statusKeyWords_NC, text[x + y])
                    if statusFind:
                        for i in statusFind:
                            if i not in status:
                                status.append(i)
                                statPair = [status, pdfType, subtractMethod]
                                matchStatus = x + y
                if status:
                    statusDict[matchStatus] = statPair
    return statusDict

'''
Purpose: appends found tax information to IncomeTax object
Input:  incomeObj(IncomeTax)
        stat(str) - status to be stored (single, married, dependent, ect)
        amount(str) - money amount applied to exemption/tax credit
        operator(str) - operator associated with money amount
        lowRange(str) - low end range limit assoicated with money amount
        highRange(str) - high end range limit assoicated with money amount
        subtractMethod(str) - details whether money is for exemption or tax credit
        fromTable(bool) - says whether tax info comes from a table or not.
Output: None
'''
def appendTaxInfo(incomeObj, stat, amount, operator, lowRange, highRange, subtractMethod, fromTable):
    if fromTable == False and stat not in incomeObj.getStatusList():
        incomeObj.appendStatus(stat)
        incomeObj.appendLowIncomeRange(lowRange)
        incomeObj.appendHighIncomeRange(highRange)
        incomeObj.appendSubtractAmount(amount)
        incomeObj.appendSubtractType(subtractMethod)
    elif fromTable == True:
        incomeObj.appendStatus(stat)
        incomeObj.appendLowIncomeRange(lowRange)
        incomeObj.appendHighIncomeRange(highRange)
        incomeObj.appendSubtractAmount(amount)
        incomeObj.appendSubtractType(subtractMethod)

'''
Purpose:
Input:
Output:
'''
def statInIncomeTaxStatList(incomeObj, stat):
    if stat not in incomeObj.getStatusList():
        return False
    else:
        return True

'''
Purpose: search a line of text for string containing line, box, part or page numbers and if 
    the instruction document should be used for the search of these terms
Input:  line(str) - line of text
Output: paragraphList(list) - contains info on any line, box, page, or part data contained in line,
    as well as if the instruction form should be used
'''
def searchTermInLine(line, subtractionType):
    paragraphList = []
    refAdd  = []
    addIt = []
    useInst = False
    if 'instruction' in line:
        useInst = True
    splitTerm = re.split('(line)|(box)|(page)|(part)', line)
    for y in range(1,len(splitTerm)):
        refList = []
        split = splitTerm[y]
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
                            if refSearch:
                                ref = refSearch.group(0)
                                refList.append(ref)
                                outerRefSearch = re.search('[a-z]+', ref)
                                if outerRefSearch:
                                    outerRef = re.search('([0-9]+)', ref)
                                    refList.append(outerRef.group(0))
                    refListing = [term, refList, useInst]
                    refAdd.append(refListing)
                else:
                    refSearch = re.search('([0-9]+[A-Za-z]*)', split)
                    ref = refSearch.group(0)
                    refList.append(ref)
                    outerRefSearch = re.search('[a-z]+', ref)
                    if outerRefSearch:#to capture parent reference number, along with any sub-reference numbers captured above
                        outerRef = re.search('([0-9]+)', ref)
                        refList.append(outerRef.group(0))
                    refListing = [term, refList, useInst]
                    refAdd.append(refListing)
            elif romanNum:
                if ',' in split:
                    commaSplit = re.split('\s*,\s*', split)
                    for x in commaSplit:
                        if x != '':
                            refSearch = re.search('(x|ix|viii|vii|vi|v|iv|iii|ii|i)', x)
                            ref = refSearch.group(0)
                            refList.append(ref)
                    refListing = [term, refList, useInst]
                    refAdd.append(refListing)
                else:
                    refSearch = re.search('(x|ix|viii|vii|vi|v|iv|iii|ii|i)', split)
                    ref = refSearch.group(0)
                    refList.append(ref)
                    refListing = [term, refList, useInst]
                    refAdd.append(refListing)
    
    paragraphList.append(subtractionType)
    for ref in refAdd:
        paragraphList.append(ref)
    return paragraphList

'''
Purpose: search a block of text(text) for any instances of a list of strings (stringSearch).
Input: text(str) - block of text to be searched
       stringSearch(list) - string that is searched for in text
Output: referenceList(list) - list of search terms found in PDF and numerical data related to search terms
'''
def getParagraphList(text, stringSearch):
    #split on each newline
    text = text.lower()
    gotSearch = False
    lineSplit = re.split('\n', text, flags=re.IGNORECASE)
    subtractionType = ''
    referenceList = []
    useInst = False
    for i in lineSplit:
        #search for Personal Exemption, Personal Tax Credit
        gotSearch = False
        searchMatch = re.search(stringSearch, i, flags = re.IGNORECASE|re.DOTALL)
        if searchMatch:
            subtractionType = searchMatch.group(0)
            paragraphList = []
            if 'line' in i or 'box' in i or 'page' in i or 'part' in i:
                gotSearch = True
                paragraphList = searchTermInLine(i, subtractionType) 
            elif 'instruction' in i:
                gotSearch = True
                nums = []
                term = 'instruction'
                useInst = True
                termListing = [term, nums, useInst]
                paragraphList.append(subtractionType)
                paragraphList.append(termListing)                    
            if gotSearch == False: #No line, box, page or part found in line!
                term = 'None'
                nums = []
                termListing = [term, nums, useInst]
                paragraphList.append(subtractionType)
                paragraphList.append(termListing)
            referenceList.append(paragraphList)
                   
    return referenceList

'''
Purpose: search for exemption/credit amount in pdf doc using keywords, adds all tax info collected during search to State object.
Input:  stateObj (State) - State object
        text(str) - state income tax form PDF text
        refList(list) - list of references initially found in form to be further investigated
Output: None                   
'''                    
def searchTaxFormParagraphs(stateObj, text, refList):
    text = text.lower()
    lineSplit = re.split('\n', text)
    amountDict = dict()
    pdfType = 'form'
    foundMoney = 0
    diffSubs = False
    statusDict = dict()
    statList = []
    amountList = []
    incomeObj = tax.IncomeTax()
    gotMatch = False
    
    
    for bunch in refList:
        page = False
        if len(bunch) <= 2:
            subtractMethod, statList, searchTermList, useInstList, numsList = readReferenceList(bunch)
            for x in range(0, len(useInstList)):
                if useInstList[x] == True:
                    if searchTermList:
                        if searchTermList[x] == 'page':
                            pageNums = numsList[x]
                            if pageNums:
                                instructText = PDF2TXT(stateObj.getInstrDir(), pageNums)
                            else:
                                instructText = PDF2TXT(stateObj.getInstrDir()) 
                            stat, amount, operator, statusLineMatch, lowRange, highRange = searchTaxInstructions(instructText, subtractMethod[x], statusKeyWords)#again, might want to use statusList, rather than subtractMethod
                            if amount:
                                for k in range(0, len(amount)):
                                    gotMatch = True
                                    foundTable = False
                                    appendTaxInfo(incomeObj, stat[k], amount[k], operator[k], lowRange[k], highRange[k], subtractMethod[x], foundTable)
                        else: #no page specified
                            instructText = PDF2TXT(stateObj.getInstrDir())
                            stat, amount, operator, statusLineMatch, lowRange, highRange = searchTaxInstructions(instructText, subtractMethod[x], statusKeyWords)
                            if amount:
                                for k in range(0, len(amount)):
                                    gotMatch = True
                                    foundTable = False
                                    appendTaxInfo(incomeObj, stat[k], amount[k], operator[k], lowRange[k], highRange[k], subtractMethod[x], foundTable) 
                    else: #no searchTermList specified
                        instructText = PDF2TXT(stateObj.getInstrDir())
                        stat, amount, operator, statusLineMatch, lowRange, highRange = searchTaxInstructions(instructText, subtractMethod[x], statusKeyWords)
                        if amount:
                            for k in range(0, len(amount)):
                                gotMatch = True
                                foundTable = False
                                appendTaxInfo(incomeObj, stat[k], amount[k], operator[k], lowRange[k], highRange[k], subtractMethod[x], foundTable)                           
                else:#if useInst is False
                    if searchTermList[x] == 'None':
                        stringSearch = subtractMethod[x]
                        statusDict = searchForStatus(lineSplit, pdfType, stringSearch, statusDict, subtractMethod[x])
                    else:
                        if isinstance(numsList[x],(list)):
                            for num in numsList[x]:
                                termSearch = '[' + searchTermList[x] + ']*\s*' + num+'[A-Za-z]{0,1}\.?(\s+|$)'
                                statusDict = searchForStatus(lineSplit, pdfType, termSearch, statusDict, subtractMethod[x])           
        elif len(bunch) > 2:
            newStatusDict = dict()
            subtractMethod, statList, searchTermList, useInstList, numsList = readReferenceList(bunch)
            if 'page' in searchTermList:
                page = True
            newStatusDict = termListSearchText(searchTermList, numsList, page, stateObj.getFormDir(), 'form', subtractMethod)
            if not newStatusDict:
                newStatusDict = termListSearchText(searchTermList, numsList, page, stateObj.getInstrDir(), 'instructions', subtractMethod)
            if newStatusDict:
                statusDict.update(newStatusDict) #merge newStatusDict entries into original statusDict

    totalLine = 0
    if statusDict:
        for line, statusPair in statusDict.iteritems():
            hasTable = False #determined from reading the file and finding multiple lines with just numbers
            moneyFound = []
            moneyMatch = True
            status = statusPair[0]
            type = statusPair[1]
            subtractMethod = statusPair[2]
            foundTable = False
            keepGoing = False
            
            for stat in status:    
                if type == 'form':
                    currLine = lineSplit[line]
                    amount, operator, statusLineMatch, lowRange, highRange = amountSearch(lineSplit, line, stat)
                    if amount:
                        gotMatch = True
                        appendTaxInfo(incomeObj, stat, amount, operator, lowRange, highRange, subtractMethod, foundTable)
                    
                if type == 'instructions':
                    instText = PDF2TXT(stateObj.getInstrDir())
                    instText = instText.lower()
                    instLine = re.split('\n', instText)
                    currLine = instLine[line]
                    for y in lookForward:
                        amount, operator, statusLineMatch, lowRange, highRange = amountSearch(instLine, line, stat)
                        if amount:
                            gotMatch = True
                            appendTaxInfo(incomeObj, stat, amount, operator, lowRange, highRange, subtractMethod, foundTable)
                    
                if amount and stat not in amountDict:
                    amountDict[stat] = amount
                elif not amount and stat not in amountDict:
                    referenceList = getParagraphList(currLine, statusSearchSmall)
                    if referenceList:
                        for bunch in referenceList:
                            page = False
                            if len(bunch) <= 2:
                                    sub, statList, searchTermList, useInstList, numsList = readReferenceList(bunch)
                                    for stat in statList:
                                        if not statInIncomeTaxStatList(incomeObj, stat):
                                            keepGoing = True       

                            elif len(bunch) > 2:
                                sub, statList, searchTermList, useInstList, numsList = readReferenceList(bunch)
                                if 'page' in searchTermList:
                                    page = True
                            if page == True:
                                ind = searchTermList.index('page')
                                pageNums = numsList[ind]
                                if not useInstList[ind]:
                                    pdfText = PDF2TXT(stateObj.getFormDir(), pageNums)
                                    if not pdfText:
                                        pdfText = PDF2TXT(stateObj.getInstrDir(), pageNums)
                                    if pdfText:
                                        pdfText = pdfText.lower()
                                        instrLines = re.split('\n', pdfText)
                                        for term in searchTermList:
                                            if term != 'page':
                                                ind = searchTermList.index(term)
                                                num = numsList[ind]
                                                for lineNew in instrLines:
                                                    for number in num:
                                                        termSearch = term + '\s*' + number + '\s+'
                                                        findTerm = re.search(termSearch, lineNew, flags = re.DOTALL)
                                                        if findTerm:
                                                            print 'term found'
                                        if not findTerm and statList:
                                            subSearch = statList[0]
                                            for i in range(1,len(statList)):
                                                if statList[i] != subSearch:
                                                    diffSubs = True
                                            for x in range(0, len(instrLines)):
                                                findSub = re.search(subSearch, instrLines[x])
                                                if findSub and foundTable == False:
                                                    for y in lookForwardMore:
                                                        totalLine = x + y
                                                        if totalLine < len(instrLines):
                                                            findMoney = re.search('(\$*[0-9]+,*[0-9]*\.{0,1}[0-9]*)', instrLines[x + y])
                                                            findLetters = re.search('[A-Za-z]+', instrLines[x + y])
                                                            if findMoney and not findLetters:
                                                                foundMoney += 1
                                                                moneyFound.append(findMoney.group(0))
                                                            else:
                                                                foundMoney  = 0
                                                            if foundMoney >= 2:
                                                                origMoney = moneyFound[0]
                                                                for mon in moneyFound:
                                                                    if mon != origMoney:
                                                                        moneyMatch = False
                                                                if moneyMatch == False:
                                                                    hasTable = True
                                                        if hasTable == True:
                                                            moneyList, lowRange, highRange, listColNames, rangeExists = extractTableData(instrLines)
                                                            if len(moneyList) == len(lowRange) and len(lowRange) == len(highRange) and moneyList:
                                                                foundTable = True
                                                                for k in range(0, len(moneyList)):
                                                                    gotMatch = True
                                                                    appendTaxInfo(incomeObj, subSearch, moneyList[k], 'x', lowRange[k], highRange[k], subtractMethod, foundTable)
                                                                
                                                            else:
                                                                print "table lists are not the same length"
                                                            break
                                            if diffSubs == True:
                                                for i in range(1,len(statList)):
                                                    if statList[i] != sub:
                                                        findSub = re.search(statList[i], instrLines[x])
                                                        if findSub:
                                                            for y in lookForward:
                                                                if (x + y) <= len(instrLines):
                                                                    findMoney = re.search('(\$*[0-9]+,*[0-9]*\.{0,1}[0-9]*)', instrLines[x + y])
                                                                    findLetters = re.search('[A-Za-z]+', instrLines[x + y])
                                                                    if findMoney and not findLetters:
                                                                        foundMoney += 1
                                                                    else:
                                                                        foundMoney  = 0
                                                                        if foundMoney >= 2:
                                                                            hasTable = True
                                            if foundTable:
                                                break
                                else:
                                    print 'Use Instructions'
                            elif page == False and keepGoing == True:
                                print 'Not page'
    if gotMatch == False:
        print 'Nothing found!  Better update code for this state!'
    else:
        stateObj.setIncomeTax(incomeObj)
        
'''
Purpose: extract list info from reference Lsit
Input:  refListGroup(list) - list to be extracted
Output: subtractMethod(list) - subtract methods(exemption or tax cradit) in reference list
        statList(list) - status (single, married, dependent, ect) in reference list
        searchTermList(list) - search words (page, part, box, line, etc.) in reference list
        useInstList(list) - indication that instructions should be searched for that reference
        numsList (list) - number associated with search word in reference list
'''
def readReferenceList(refListGroup):
    subtractMethod = []
    statList = []
    searchTermList = []
    useInstList = []
    numsList = []
    for term in refListGroup:
        if 'exemption' in term or 'credit' in term:
            subtractMethod.append(term)
        elif 'dependent' in term or 'single' in term or 'married' in term or 'number of' in term and 'exemption' not in term and 'credit' not in term:
            statList.append(term)
        elif isinstance(term, (list, tuple)):
            for sub in term:
                if sub == 'None' or sub == 'page' or sub == 'line' or sub == 'part' or sub == 'box':
                    searchTermList.append(sub)
                elif sub == True or sub == False:
                    useInstList.append(sub)
                elif isinstance(sub, (list, tuple)):
                    numsList.append(sub)
    return subtractMethod, statList, searchTermList, useInstList, numsList

'''
Purpose: search for money string in text block around a specific line number
Input:  lines(list) -  text block
        x(int) - line number to be searched around
        status(str) - status associated with monetary amount
Output: statusAmount(str) - amount of money found associated with status
        operator(str) - operator associated with amount of money found
        statusLineMatch(str) - line number that amount was found in, within text block
        rangeLow(str) - low end range limit assoicated with money amount
        rangeHigh(str) - high end range limit associated with money amount
'''
def amountSearch(lines, x, status):
    statusLineMatch = ''
    for y in lookForward:
        operator = ''
        statusAmount = ''
        rangeLow = ''
        rangeHigh = ''
        moneySearch = re.search('\$([0-9]+,*[0-9]*\.{0,1}[0-9]*)', lines[x + y])
        if moneySearch:
            statusAmount = moneySearch.group(0)
            rangeLow = '0'
            rangeHigh = 'inf'
            #operator must be on same line as amount
            operatorSearch = re.search('(x|multiply)\s+', lines[x + y])
            if operatorSearch:
                operator = operatorSearch.group(0)
        if statusAmount != '' and operator != '':
            statusLineMatch = x + y
            break
        if statusAmount != '' and operator == '':
            operator = '+'
            statusLineMatch = x + y
            break
    return statusAmount, operator, statusLineMatch, rangeLow, rangeHigh
                                    
'''
Purpose:
Input:  text(str) - text block to be searched
        term(str) - term to be searched for in text
        searchList(str) - regex search terms to be searched for once term has been found
        scrapeTable(bool) - inidcation that table is beng searched
Output: statusList(list) - list of statuses found in text
        amountList(list) - list of money amounts found in text, associated with status in statusList
        operatorList(list) - list of operators found in text, associated with the money in amountList
        statusLineMatch(int) - line number where amount was found
        lowRangeList(list) - list of low end range limit assoicated with money in amount list
        highRangeList(list) - list of high end range limit associated with money in aount list
'''                            
def searchTaxInstructions(text, term = None, search = None, scrapeTable = None):
    amountDict = dict()
    lookForward = [0, 1, 2]
    lookAround = [0, 1, -1, 2, -2, 3, -3, 4, -4]
    text = text.lower()
    amountList = []
    operatorList = []
    lowRangeList = []
    highRangeList = []
    statusList = []
    amount = ''
    lineSplit = re.split('\n', text, flags=re.IGNORECASE)
    
    if search != None:
        for n in range(0,len(lineSplit)):
            termSearch = re.search(term, lineSplit[n])
            if termSearch:
                for i in lookAround:
                    statusSearch = re.search(search, lineSplit[n+i])
                    if statusSearch:
                        status = statusSearch.group(0)
#                         statusAmountPair, statusLineMatch = amountSearch(lineSplit, n+i, status)
                        amount, operator, statusLineMatch, lowRange, highRange = amountSearch(lineSplit, n+i, status)
                        if amount != '':
                            amountList.append(amount)
                            operatorList.append(operator)
                            lowRangeList.append(lowRange)
                            highRangeList.append(highRange)
                            statusList.append(status)                               
    
    return statusList, amountList, operatorList, statusLineMatch, lowRangeList, highRangeList