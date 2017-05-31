from collections import OrderedDict

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

def calcStateIncomeTax(income, tax):
    leftOverIncome = income - tax
    percentageKept = (leftOverIncome/income)*100.0
    
    return tax, leftOverIncome, percentageKept

def getTaxableIncome(income, exemptAmount):
    return income-exemptAmount 
