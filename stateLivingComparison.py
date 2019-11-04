import os
import numpy as np
import random
import re
import sys
import math
import csv
import pdb
from datetime import datetime
from collections import Counter, OrderedDict
from scipy import stats
from decimal import *
from sklearn.linear_model import LinearRegression
import operator
from sklearn import preprocessing
import  plotly.figure_factory as ff
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt

R = 6371 #Radius of Earth

locAZCounties = {
'Pinal':[32.8162, 111.2845],
'Maricopa':[33.2918,112.4291],
'Cochise':[31.8285,109.9497],
'Mohave':[35.2143,113.7633],
'Yavapai':[34.6464,112.4291],
'Greenlee':[33.2406,109.2832],
'Apache':[35.5313,109.3783],
'Coconino':[35.6648,111.4753],
'Gila':[33.6371,110.5215],
'Navajo':[35.4020,110.1403],
'Pima':[32.0575,111.6661],
'Santa Cruz':[31.5986,110.8076],
'La Paz':[34.0061,113.9536],
'Graham':[33.0768,109.7592],
'Yuma':[32.6528,113.9536]
}

stateJobs = [
'jobsAL.csv',
'jobsAK.csv',
'jobsAZ.csv',
'jobsAR.csv',
'jobsCA.csv',
'jobsCO.csv',
'jobsDC.csv',
'jobsDE.csv',
'jobsHI.csv',
'jobsIA.csv',
'jobsID.csv',
'jobsIN.csv',
'jobsIL.csv',
'jobsKS.csv',
'jobsKY.csv',
'jobsLA.csv',
'jobsME.csv',
'jobsMA.csv',
'jobsMS.csv',
'jobsMT.csv',
'jobsND.csv',
'jobsNE.csv',
'jobsNH.csv',
'jobsNM.csv',
'jobsNV.csv',
'jobsNY.csv',
'jobsOK.csv',
'jobsOR.csv',
'jobsRI.csv',
'jobsSC.csv',
'jobsSD.csv',
'jobsTX.csv',
'jobsVT.csv',
'jobsWA.csv',
'jobsWI.csv',
'jobsWV.csv',
'jobsWY.csv'
]

jobsPerState={
'CT':150,
'FL':261,
'GA':289,
'MD':332,
'MI':158,
'MN':145,
'MO':113,
'NJ':315,
'NC':304,
'OH':234,
'OR':66,
'PA':381,
'TN':77,
'UT':85,
'VA':787,
}


#info from https://www.tax-brackets.org/
stateIncomeTax = {
'AL':{'single':[
		[499.99,0.02],
		[2999.99,0.04],
		[float("inf"),0.05]
		], 
	'joint':[
		[999.99,0.02],
		[5999.99,0.04],
		[float("inf"),0.05]
		]},
'AK':None,
'AZ':{'single':[
		[10601.99,0.0259],
		[26500.99,0.0288],
		[52999.99,0.0336],
		[158995.99,0.0424],
		[float("inf"),0.0454]
		], 
	'joint':[
		[21201.99,0.0259],
		[52999.99,0.0288],
		[105997.99,0.0336],
		[317989.99,0.0424],
		[float("inf"),0.0454]
		]},
'AR':{'single':[
		[4298.99,0.009],
		[8498.99,0.025],
		[12698.99,0.035],
		[21198.99,0.045],
		[35098.99,0.060],
		[float("inf"),0.069]
		], 
	'joint':[
		[4298.99,0.009],
		[8498.99,0.025],
		[12698.99,0.035],
		[21198.99,0.045],
		[35098.99,0.060],
		[float("inf"),0.069]
		]},
'CA':{'single':[
		[8222.99,0.01],
		[19494.99,0.02],
		[30768.99,0.03],
		[42710.99,0.04],
		[53979.99,0.08],
		[275737.99,0.093],
		[330883.99,0.103],
		[551472.99,0.113],
		[999999.99,0.123],
		[float("inf"),0.133]
		], 
	'joint':[
		[16445.99,0.01],
		[38989.99,0.02],
		[61537.99,0.04],
		[85421.99,0.06],
		[107959.99,0.08],
		[551475.99,0.093],
		[661767.99,0.103],
		[999999.99,0.113],
		[1074995.99,0.123],
		[float("inf"),0.133]
		]},
'CO':{'all': 0.0463},
'CT':{'single':[
		[9999.99,0.03],
		[49999.99,0.05],
		[99999.99,0.055],
		[199999.99,0.06],
		[249999.99,0.065],
		[499999.99,0.069],
		[float("inf"),0.0699]
		], 
	'joint':[
		[19999.99,0.03],
		[99999.99,0.05],
		[199999.99,0.055],
		[399999.99,0.06],
		[499999.99,0.065],
		[999999.99,0.069],
		[float("inf"),0.0699]
		]},
'DC':{'single':[
		[9999.99,0.04],
		[39999.99,0.06],
		[59999.99,0.065],
		[349999.99,0.085],
		[999999.99,0.0875],
		[float("inf"),0.0895]
		], 
	'joint':[
		[9999.99,0.04],
		[39999.99,0.06],
		[59999.99,0.065],
		[349999.99,0.085],
		[999999.99,0.0875],
		[float("inf"),0.0895]
		]},
'DE':{'single':[
		[1999.99,0.00],
		[4999.99,0.022],
		[9999.99,0.039],
		[19999.99,0.048],
		[24999.99,0.052],
		[59999.99,0.055],
		[float("inf"),0.066]
		], 
	'joint':[
		[1999.99,0.00],
		[4999.99,0.022],
		[9999.99,0.039],
		[19999.99,0.048],
		[24999.99,0.052],
		[59999.99,0.055],
		[float("inf"),0.066]
		]},
'FL':None,
'GA':{'single':[
		[749.99,0.01],
		[2249.99,0.02],
		[3749.99,0.03],
		[5249.99,0.04],
		[6999.99,0.05],
		[float("inf"),0.06]
		], 
	'joint':[
		[999.99,0.01],
		[2999.99,0.02],
		[4999.99,0.03],
		[6999.99,0.04],
		[9999.99,0.05],
		[float("inf"),0.06]
		]},
'HI':{'single':[
		[2399.99,0.014],
		[4799.99,0.032],
		[9599.99,0.055],
		[14399.99,0.064],
		[19199.99,0.068],
		[23999.99,0.072],
		[35999.99,0.076],
		[47999.99,0.079],
		[149999.99,0.0825],
		[174999.99,0.09],
		[199999.99,0.10],
		[float("inf"),0.11]
		], 
	'joint':[
		[4799.99,0.014],
		[9599.99,0.032],
		[19199.99,0.055],
		[28799.99,0.064],
		[38399.99,0.068],
		[47999.99,0.072],
		[71999.99,0.076],
		[95999.99,0.079],
		[299999.99,0.0825],
		[349999.99,0.09],
		[399999.99,0.10],
		[float("inf"),0.11]
		]},
'ID':{'single':[
		[1471.99,0.0112],
		[2944.99,0.0312],
		[4416.99,0.0362],
		[5889.99,0.0462],
		[7361.99,0.0562],
		[11042.99,0.0662],
		[float("inf"),0.0692]
		], 
	'joint':[
		[2943.99,0.0112],
		[5889.99,0.0312],
		[8833.99,0.0362],
		[11779.99,0.0462],
		[14723.99,0.0562],
		[22085.99,0.0662],
		[float("inf"),0.0692]
		]},
'IL':{'all':0.0495},
'IN':{'all':0.0323},
'IA':{'single':[
		[1597.99,0.0036],
		[3195.99,0.0072],
		[6391.99,0.0243],
		[14381.99,0.045],
		[23969.99,0.0612],
		[31959.99,0.0648],
		[47939.99,0.068],
		[71909.99,0.0792],
		[float("inf"),0.0898]
		], 
	'joint':[
		[1597.99,0.0036],
		[3195.99,0.0072],
		[6391.99,0.0243],
		[14381.99,0.045],
		[23969.99,0.0612],
		[31959.99,0.0648],
		[47939.99,0.068],
		[71909.99,0.0792],
		[float("inf"),0.0898]
		]},
'KS':{'single':[
		[2499.99, 0.0],
		[14999.99,0.031],
		[29999.99,0.0525],
		[float("inf"),0.057]
		], 
	'joint':[
		[4999.99, 0.0],
		[29999.99,0.031],
		[59999.99,0.0525],
		[float("inf"),0.057]
		]},
'KY':{'all':0.05},
'LA':{'single':[
		[12499.99,0.02],
		[49999.99,0.04],
		[float("inf"),0.06]
		], 
	'joint':[
		[24999.99,0.02],
		[99999.99,0.04],
		[float("inf"),0.06]
		]},
'ME':{'single':[
		[21449.99,0.058],
		[50749.99,0.0675],
		[float("inf"),0.0715]
		], 
	'joint':[
		[42899.99,0.058],
		[101549.99,0.0675],
		[float("inf"),0.0715]
		]},
'MD':{'single':[
		[999.99,0.02],
		[1999.99,0.03],
		[2999.99,0.04],
		[99999.99,0.0475],
		[124999.99,0.05],
		[149999.99,0.0525],
		[249999.99,0.055],
		[float("inf"),0.0575]
		], 
	'joint':[
		[999.99,0.02],
		[1999.99,0.03],
		[2999.99,0.04],
		[149999.99,0.0475],
		[174999.99,0.05],
		[224999.99,0.0525],
		[299999.99,0.055],
		[float("inf"),0.0575]
		]},
'MA':{'all':0.0505},
'MI':{'all':0.0425},
'MN':{'single':[
		[25889.99, 0.0535],
		[85059.99,0.0705],
		[160019.99,0.0785],
		[float("inf"),0.0985]
		], 
	'joint':[
		[37849.99, 0.0535],
		[150379.99,0.0705],
		[266699.99,0.0785],
		[float("inf"),0.0985]
		]},
'MS':{'single':[
		[999.99, 0.0],
		[4999.99,0.03],
		[9999.99,0.04],
		[float("inf"),0.05]
		], 
	'joint':[
		[999.99, 0.0],
		[4999.99,0.03],
		[9999.99,0.04],
		[float("inf"),0.05]
		]},
'MO':{'single':[
		[101.99,0.0],
		[1027.99,0.015],
		[2055.99,0.02],
		[3083.99,0.025],
		[4112.99,0.03],
		[5140.99,0.035],
		[6168.99,0.04],
		[7196.99,0.045],
		[8224.99,0.05],
		[9252.99,0.055],
		[float("inf"),0.059]
		], 
	'joint':[
		[101.99,0.0],
		[1027.99,0.015],
		[2055.99,0.02],
		[3083.99,0.025],
		[4112.99,0.03],
		[5140.99,0.035],
		[6168.99,0.04],
		[7196.99,0.045],
		[8224.99,0.05],
		[9252.99,0.055],
		[float("inf"),0.059]
		]},
'MT':{'single':[
		[2999.99,0.01],
		[5199.99,0.02],
		[7999.99,0.03],
		[10799.99,0.04],
		[13899.99,0.05],
		[17899.99,0.06],
		[float("inf"),0.069]
		], 
	'joint':[
		[2999.99,0.01],
		[5199.99,0.02],
		[7999.99,0.03],
		[10799.99,0.04],
		[13899.99,0.05],
		[17899.99,0.06],
		[float("inf"),0.069]
		]},
'NE':{'single':[
		[3149.99, 0.0246],
		[18879.99,0.0351],
		[30419.99,0.0501],
		[float("inf"),0.0684]
		], 
	'joint':[
		[6289.99, 0.0246],
		[37759.99,0.0351],
		[60479.99,0.0501],
		[float("inf"),0.0684]
		]},
'NV':None,
'NH':None,
'NJ':{'single':[
		[19999.99, 0.014],
		[34999.99, 0.0175],
		[39999.99, 0.035],
		[74999.99, 0.0553],
		[499999.99, 0.0637],
		[float("inf"),0.0897]
		], 
	'joint':[
		[19999.99, 0.014],
		[49999.99, 0.0175],
		[69999.99, 0.0245],
		[79999.99, 0.035],
		[149999.99, 0.0553],
		[499999.99, 0.0637],
		[float("inf"),0.0897]
		]},
'NM':{'single':[
		[5499.99, 0.017],
		[10999.99,0.032],
		[15999.99,0.047],
		[float("inf"),0.049]
		], 
	'joint':[
		[7999.99, 0.017],
		[15999.99,0.032],
		[23999.99,0.047],
		[float("inf"),0.049]
		]},
'NY':{'single':[
		[8499.99,0.04],
		[11699.99,0.045],
		[13899.99,0.0525],
		[21399.99,0.059],
		[80649.99,0.0633],
		[215399.99,0.0657],
		[1077549.99,0.0685],
		[float("inf"),0.0882]
		], 
	'joint':[
		[17149.99,0.04],
		[23599.99,0.045],
		[27899.99,0.0525],
		[42999.99,0.059],
		[161549.99,0.0633],
		[323199.99,0.0657],
		[2155349.99,0.0685],
		[float("inf"),0.0882]
		]},
'NC':{'all':0.0525},
'ND':{'single':[
		[38699.99, 0.011],
		[93699.99,0.0204],
		[195449.99,0.0227],
		[424949.99, 0.0264],
		[float("inf"),0.029]
		], 
	'joint':[
		[64649.99, 0.011],
		[156149.99,0.0204],
		[237949.99,0.0227],
		[424949.99, 0.0264],
		[float("inf"),0.029]
		]},
'OH':{'single':[
		[10849.99, 0.0],
		[16299.99,0.0198],
		[21749.99,0.0248],
		[43449.99,0.0297],
		[86899.99,0.0346],
		[108699.99,0.0396],
		[217399.99,0.046],
		[float("inf"),0.05]
		], 
	'joint':[
		[10649.99, 0.0],
		[15999.99,0.0198],
		[21349.99,0.0248],
		[42649.99,0.0297],
		[85299.99,0.0346],
		[106649.99,0.0396],
		[213349.99,0.046],
		[float("inf"),0.05]
		]},
'OK':{'single':[
		[999.99, 0.005],
		[2499.99,0.01],
		[3749.99,0.02],
		[4899.99, 0.03],
		[7199.99, 0.04],
		[float("inf"),0.05]
		], 
	'joint':[
		[1999.99, 0.005],
		[4999.99,0.01],
		[7499.99,0.02],
		[9799.99, 0.03],
		[12199.99, 0.04],
		[float("inf"),0.05]
		]},
'OR':{'single':[
		[3449.99, 0.05],
		[8699.99,0.07],
		[124999.99,0.09],
		[float("inf"),0.099]
		], 
	'joint':[
		[6899.99, 0.05],
		[17399.99,0.07],
		[249999.99,0.09],
		[float("inf"),0.099]
		]},
'PA':{'all':0.0307},
'RI':{'single':[
		[62549.99,0.0375],
		[149149.99,0.0475],
		[float("inf"),0.0599]
		], 
	'joint':[
		[62549.99,0.0375],
		[149149.99,0.0475],
		[float("inf"),0.0599]
		]},
'SC':{'single':[
		[2969.99, 0.0],
		[5939.99,0.03],
		[8909.99,0.04],
		[11879.99, 0.05],
		[14859.99, 0.06],
		[float("inf"),0.07]
		], 
	'joint':[
		[2969.99, 0.0],
		[5939.99,0.03],
		[8909.99,0.04],
		[11879.99, 0.05],
		[14859.99, 0.06],
		[float("inf"),0.07]
		]},
'SD':None,
'TN':None,
'TX':None,
'UT':{'all':0.0495},
'VT':{'single':[
		[38699.99, 0.0335],
		[93699.99,0.066],
		[195449.99,0.076],
		[float("inf"),0.0875]
		], 
	'joint':[
		[64599.99, 0.0335],
		[156149.99,0.066],
		[237949.99,0.076],
		[float("inf"),0.0875]
		]},
'VA':{'single':[
		[2999.99, 0.02],
		[4999.99,0.03],
		[16999.99,0.05],
		[float("inf"),0.0575]
		], 
	'joint':[
		[2999.99, 0.02],
		[4999.99,0.03],
		[16999.99,0.05],
		[float("inf"),0.0575]
		]},
'WA':None,
'WV':{'single':[
		[9999.99, 0.03],
		[24999.99, 0.04],
		[39999.99, 0.045],
		[59999, 0.06],
		[float("inf"),0.065]
		], 
	'joint':[
		[9999.99, 0.03],
		[24999.99, 0.04],
		[39999.99, 0.045],
		[59999, 0.06],
		[float("inf"),0.065]
		]},
'WI':{'single':[
		[11229.99, 0.04],
		[22469.99,0.0584],
		[252149.99,0.0627],
		[float("inf"),0.0765]
		], 
	'joint':[
		[14979.99, 0.04],
		[29959.99,0.0584],
		[336199.99,0.0627],
		[float("inf"),0.0765]
		]},
'WY':None
}

dataScienceAvgSalary = {
'AL':99131,
'AK':None,
'AZ':129076,
'AR':87532,
'CA':143948,
'CO':115823,
'CT':147620,
'DE':None,
'DC':122498,
'FL':114738,
'GA':108320,
'HI':None,
'ID':None,
'IL':109257,
'IN':99337,
'IA':101907,
'KS':107797,
'KY':68717,
'LA':None,
'ME':None,
'MD':111070,
'MA':119702,
'MI':98276,
'MN':107678,
'MS':None,
'MO':108742,
'MT':55203,
'NE':None,
'NV':None,
'NH':None,
'NJ':105002,
'NM':None,
'NY':135536,
'NC':112255,
'ND':None,
'OH':112750,
'OK':115796,
'OR':99513,
'PA':129690,
'RI':None,
'SC':85764,
'SD':None,
'TN':None,
'TX':113993,
'UT':None,
'VT':None,
'VA':118270,
'WA':113979,
'WV':None,
'WI':103495,
'WY':None
}

fipsAZ = {
'Apache':'04001',
'Cochise':'04003',
'Coconino':'04005',
'Gila':'04007',
'Graham':'04009',
'Greenlee':'04011',
'La Paz':'04012',
'Maricopa':'04013',
'Mohave':'04015',
'Navajo':'04017',
'Pima':'04019',
'Pinal':'04021',
'Santa Cruz':'04023',
'Yavapai':'04025',
'Yuma':'04027'
}

def getJobCount(flnm, stateJobsDict):
	jobCount = 0
	jobsPerCity = {}
	state = None
	jobCount = 0
	
	with open(flnm) as csv_file:
		#if flnm == 'jobsDC.csv':
		#	pdb.set_trace()
		line_count = 0
		csv_reader = csv.reader(csv_file, delimiter=',')
		pattern = re.compile(r""".*\-\s*(?P<city>.*?),\s*(?P<state>[A-Z][A-Z]?).*""",re.VERBOSE)
		for row in csv_reader:
			if line_count > 0:
				loc = row[10]
				locGroup = pattern.match(loc)
				if locGroup:
					city = locGroup.group("city")
					state = locGroup.group("state")
					if len(state) != 2:
						print "Problem with regex!!!!"
						pdb.set_trace()
					jobCount += 1
					if state == 'AZ':
						if city not in jobsPerCity:
							jobsPerCity[city] = 1
						else:
							jobsPerCity[city] += 1
					if state not in stateJobsDict:
						stateJobsDict[state] = 1
					else:
						stateJobsDict[state] += 1
			line_count += 1
	csv_file.close()
	return stateJobsDict, jobsPerCity
	
def getPercent(string):
	if '<' in string:
		return 1
	elif '>' in string:
		return 99
	elif "*" in string:
		return None
	else:
		return float(string)

def degreesToRadians(deg):
	return deg*(math.pi/180)

def earthToPlaneDistance(lat1, lat2, lon1, lon2):
	lat1Rad = degreesToRadians(lat1)
	lat2Rad = degreesToRadians(lat2)
	lon1Rad = degreesToRadians(lon1)
	lon2Rad = degreesToRadians(lon2)
	
	deltaLat = (lat2Rad) - (lat1Rad)
	deltaLon = (lon2Rad) - (lon1Rad)
	
	meanLat = ((lat1Rad) + (lat2Rad))/(2)
	
	D = R * math.sqrt(pow(deltaLat,2) + pow(math.cos(meanLat)*deltaLon,2))
	return D

def getSchoolPerf():
	schoolFile = 'AzMERIT20172018.csv'
	countyPerf = {}
	with open(schoolFile) as csv_file:
		line_count = 0
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			if line_count > 0:
				county = row[1]
				testLevel = row[3]
				subgroup = row[4]
				level4Perc = getPercent(row[10])
				if testLevel == 'All' and subgroup == 'All Students' and level4Perc != None:
					if county not in countyPerf:
						countyPerf[county] = level4Perc
					else:
						#each county reports for Math and English parts of AzMERIT. We will take the lower of the 2 scores
						#for comparison between counties.
						if level4Perc < countyPerf[county]:
							countyPerf[county] = level4Perc	
			line_count += 1
	level4 = []
	countyList = []
	for county, perc in countyPerf.items():
		countyList.append(county)
		level4.append(perc)
	normLevel4 = preprocessing.normalize([level4])
	countyScore = {}
	for i in range(len(countyList)):
		countyScore[countyList[i]]= normLevel4[0][i]
	#not returning nomralized values right now, for graphing purposes
	return countyPerf

def getTownsInCounties():
	townFile = 'townsAndCounties.csv'
	countyTownMap = {}
	with open(townFile) as csv_file:
		line_count = 0
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			town = row[0]
			county = row[2]
			countyTownMap[town] = county
		line_count += 1
	return countyTownMap

def getCountiesWithJobs(jobsPerCity):
#gets all the counties with at least 1 job listing currently. Higher weight should
#be given to counties with more jobs (/future/)
	countiesWithJobs = {}
	countyTownMap = getTownsInCounties()
	for town, i in jobsPerCity.items():
		if town in countyTownMap:
			county = countyTownMap[town]
			if county not in countiesWithJobs:
				countiesWithJobs[county] = 1
			else:
				countiesWithJobs[county] += 1
	return countiesWithJobs
	
def getDistanceFromJobs(countiesWithJobs):
#if a county has no job listings, we calculate distance to nearest county with jobs
	minDistJobs = {}
	for county, loc in locAZCounties.items():
		minDist = float("inf")
		if county not in countiesWithJobs:
			for countyPrime in countiesWithJobs:
				lat1 = locAZCounties[countyPrime][0]
				lon1 = locAZCounties[countyPrime][1]
				lat2 = loc[0]
				lon2 = loc[1]
				d = earthToPlaneDistance(lat1, lat2, lon1, lon2)
				if d < minDist:
					minDist = d
			minDistJobs[county] = minDist
		else:
			minDistJobs[county] = 0
	return minDistJobs
		
'''def compareCounties():
	countySchoolScore = getSchoolPerf()
	jobsPerCity, jobsPerState = getJobCount()
	countiesWithJobs = getCountiesWithJobs(jobsPerCity)
	minDistJobs = getDistanceFromJobs(countiesWithJobs)
	counties = []
	dist = []
	countyDistScore = {}
	for county, d in minDistJobs.items():
		counties.append(county)
		dist.append(d)
	normDist = preprocessing.normalize([dist])
	for i in range(len(counties)):
		countyDistScore[counties[i]] = 1 - normDist[0][i]
	
	#countyOverall adds the normalized scores of distance to jobs(from countyDistScore) and 
	#from school performance (countySchoolScore) to get the overall score for the county. Each
	#variable is given equal wait, which can be changed</future/>
	overallScore = {}
	for county, score in countySchoolScore.items():
		overallScore[county] = score + countyDistScore[county]

	return overallScore'''

def plotCountyComp(distScore, schoolScore):
	colorscale = [
								'rgb(65, 53, 132)',
								'rgb(101,104,168)',
								'rgb(144,148,194)',
								'rgb(195, 196, 222)',
								'rgb(239,239,239)',
								'rgb(193, 193, 193)'
								]

	fipsScore = []
	fips = []
	fipsSchool = []
	fipsSchoolScore = []
	for county, score in distScore.items():
		fips.append(fipsAZ[county])
		fipsScore.append(score)
	for county1, score1 in schoolScore.items():
		fipsSchool.append(fipsAZ[county1])
		fipsSchoolScore.append(score1)

	fig1 = ff.create_choropleth(fips=fips, values=fipsScore,scope=['AZ'], county_outline={'color': 'rgb(255,255,255)', 'width': 0.5}, round_legend_values=True,binning_endpoints=[50, 100, 200, 300, 400],colorscale=colorscale,title ='Best County to Live in AZ based on Distance to Data Science Jobs',legend_title='Distance(km)')
	fig1.layout.template = None
	fig1.show()

	fig2 = ff.create_choropleth(fips=fipsSchool, values=fipsSchoolScore, scope=['AZ'], county_outline={'color': 'rgb(255,255,255)', 'width': 0.5}, title ='Best County to Live in AZ based on 2018 AzMERIT Performance',legend_title='% Students in Highest Score Bracket')
	fig2.layout.template = None
	fig2.show()

def plotStateAnalysis(states, jobs, incomes):
	plt.figure(figsize=(15,8))
	for i, state in enumerate(states):
		x = jobs[i]
		y = incomes[i]
		plt.scatter(x,y,marker='.', color='blue')
		plt.text(x+1, y, state, fontsize=9,horizontalalignment='right', verticalalignment='bottom')
	plt.ylabel('After Tax Income')
	plt.xlabel('Number of Job Listings')
	plt.title('After Tax Income v. Number of Data Science Job Listings Per State')
	plt.xlim(-40,1800)
	plt.ylim(50000,143000)
	plt.show()


def stateAnalysis(incomeAfterTaxes):
	stateJobsDict = {}
	for fileNM in stateJobs:
		stateJobsDict, jobsPerCity= getJobCount(fileNM, stateJobsDict)
		if jobsPerCity:
			AZAnalysis(jobsPerCity)
	
	states=[]
	jobs=[]
	incomes=[]
	for state,income in incomeAfterTaxes.items():
		if state in stateJobsDict:
			job = stateJobsDict[state]
		else:
			job = jobsPerState[state]
		states.append(state)
		jobs.append(job)
		incomes.append(income)

	plotStateAnalysis(states, jobs, incomes)

def AZAnalysis(jobsPerCity):
	countySchoolScore = getSchoolPerf()
	countiesWithJobs = getCountiesWithJobs(jobsPerCity)
	minDistJobs = getDistanceFromJobs(countiesWithJobs)
	plotCountyComp(minDistJobs, countySchoolScore)

def getAfterTaxIncome():
	incomeAfterTaxes = {}
	for state, salary in dataScienceAvgSalary.items():
		if salary != None:
			taxBracket = stateIncomeTax[state]
			if taxBracket == None:
				incomeAfterTaxes[state] = salary
			elif len(stateIncomeTax[state]) == 1:
				taxAll = stateIncomeTax[state]
				tax = taxAll['all']
				incomeAfterTaxes[state] = salary - (salary*tax)
			else:
				bracketSingle = stateIncomeTax[state]['single']
				bracketJoint = stateIncomeTax[state]['joint']
				#For our first case, we only care about single Data Scientists
				#we'll be using the single brackets for all salaries and states
				for i in bracketSingle:
					max = i[0]
					tax = i[1]
					if salary <= max:
						incomeAfterTaxes[state] = salary -(salary*tax)
						break
	return incomeAfterTaxes


if __name__ == '__main__':
	
	incomeAfterTaxes = getAfterTaxIncome()

	stateAnalysis(incomeAfterTaxes)
	
					
			
			
			
				
		