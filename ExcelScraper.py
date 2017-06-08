from collections import defaultdict
import os.path
import pandas as pd
import numpy as np
import re

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

'''
Purpose: read excel file for state tax and exemption data for each status
Inputs: path(str) - path to excel doc TF-State-Individual-Income-Tax-Rates-Brackets-2017.xlsx
Outputs:singleRateDict(dict) - dictionary with state tax rate for various income levels for status of single
        marriedRateDict(dict) - dictionary with state tax rate for various income levels for status of married
        singleExemptDict(dict) - dictionary of state exemption amounts for status of single
        marriedExemptDict(dict) - dictionary of state exemption amounts for status of married
        dependentExemptDict(dict) - dictionary of state exemption amounts for status of dependents
'''
def getStateIncomeTaxRateExemption(path):
    if not os.path.exists(path):
        return 'File does not exist'
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
                            break
                        else:
                            for abb in abbrev:
                                if striNew == abb:
                                    state = stateName
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
    return singleRateDict, marriedRateDict, singleExemptDict, marriedExemptDict, dependentExemptDict

'''
Purpose: Extract state specific data from exemption dictionaries
Input:  state(str) - state to be looked up
        exemptDict(dict) - exemption dictionary to be used for lookup
        dependentNum(int) - number of dependents
Output: exemptAmount
'''
def getExemptAmount(state, exemptDict,  dependentNum = None):
    exemptAmount = 0
    if state in exemptDict:
        exemptAmount += exemptDict[state]
    if dependentNum != None: 
        if state in exemptDict:
            exemptAmount = dependentNum * exemptAmount
    return exemptAmount
