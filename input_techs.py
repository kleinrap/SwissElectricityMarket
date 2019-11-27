import pandas as pd
import pickle

'''
IC: investment costs
FC: fixed costs
VC: variable costs
FuC: fuel costs
triple lists for triple scenarios - [0]: low, [1]: medium, [2]: high
Everything has been multiplied to be in MW or MWh units
'''

tech_input = {
	'Solar':
		{'IC': [[],[],[]], 'FC': [[],[],[]]},
	'Wind':
		{'IC': [[],[],[]], 'FC': [[],[],[]]},
	'CCGT':
		{'IC': [[],[],[]], 'FC': [[],[],[]], 'VC': [[],[],[]], 'FuC': [[],[],[]]},
	'Nuclear':
		{'IC': [[],[],[]], 'FC': [[],[],[]], 'VC': [[],[],[]], 'FuC': [[],[],[]]},
	'Hydro':
		{'IC': [[], [], []], 'FC': [[], [], []], 'VC': [[], [], []]},
	'RunOfRiver':
		{'IC': [[], [], []], 'FC': [[], [], []], 'VC': [[], [], []]},
	'Waste':
		{'IC': [[],[],[]], 'FC': [[],[],[]], 'VC': [[],[],[]], 'FuC': [[],[],[]]}
}

year_start = 2016
year_end = 2050
length_sim = year_end - year_start + 1

inputFile_load = 'tech_costs_input.xlsx'

# loading the CCGT inputs
tech_type = 'CCGT'
print('Loading the', tech_type, 'inputs.')

input_load = pd.read_excel(inputFile_load, sheet_name=tech_type)

'''
CAPEX -  ($/kW)
OPEX_fixed - ($/kW-year) 
OPEX_variable -  ($/MWh)
Fuel_cost - ($/MWh)
'''

# [1] for the medium scenario
for j in range(length_sim):
	tech_input[tech_type]['IC'][1].append(round(input_load.iloc[j][1] * 1000,3))
	tech_input[tech_type]['FC'][1].append(round(input_load.iloc[j][2] * 1000,3))
	tech_input[tech_type]['VC'][1].append(round(input_load.iloc[j][3],3))
	tech_input[tech_type]['FuC'][1].append(round(input_load.iloc[j][4],3))


# loading the solar inputs
tech_type = 'Solar'
print('Loading the', tech_type, 'inputs.')
input_load = pd.read_excel(inputFile_load, sheet_name=tech_type)

'''
CAPEX ($/kW) High
CAPEX ($/kW) Average
CAPEX ($/kW) Low
OPEX fixed ($/kW-year) High
OPEX fixed ($/kW-year) Average
OPEX fixed ($/kW-year) Low
'''

for j in range(length_sim):
	tech_input[tech_type]['IC'][0].append(round(input_load.iloc[j][3] * 1000,3))
	tech_input[tech_type]['IC'][1].append(round(input_load.iloc[j][2] * 1000,3))
	tech_input[tech_type]['IC'][2].append(round(input_load.iloc[j][1] * 1000,3))
	tech_input[tech_type]['FC'][0].append(round(input_load.iloc[j][6] * 1000,3))
	tech_input[tech_type]['FC'][1].append(round(input_load.iloc[j][5] * 1000,3))
	tech_input[tech_type]['FC'][2].append(round(input_load.iloc[j][4] * 1000,3))


# loading the wind inputs
tech_type = 'Wind'
print('Loading the', tech_type, 'inputs.')
input_load = pd.read_excel(inputFile_load, sheet_name=tech_type)

'''
CAPEX ($/kW) High
CAPEX ($/kW) Average
CAPEX ($/kW) Low
OPEX fixed ($/kW-year) High
OPEX fixed ($/kW-year) Average
OPEX fixed ($/kW-year) Low
'''

for j in range(length_sim):
	tech_input[tech_type]['IC'][0].append(round(input_load.iloc[j][3] * 1000,3))
	tech_input[tech_type]['IC'][1].append(round(input_load.iloc[j][2] * 1000,3))
	tech_input[tech_type]['IC'][2].append(round(input_load.iloc[j][1] * 1000,3))
	tech_input[tech_type]['FC'][0].append(round(input_load.iloc[j][6] * 1000,3))
	tech_input[tech_type]['FC'][1].append(round(input_load.iloc[j][5] * 1000,3))
	tech_input[tech_type]['FC'][2].append(round(input_load.iloc[j][4] * 1000,3))


# loading the nuclear inputs
tech_type = 'Nuclear'
print('Loading the', tech_type, 'inputs.')
input_load = pd.read_excel(inputFile_load, sheet_name=tech_type)

'''
CAPEX ($/kW)
OPEX fixed ($/kW-year)
OPEX variable ($/MWh)
Fuel cost ($/MWh)
'''

for j in range(length_sim):
	tech_input[tech_type]['IC'][1].append(round(input_load.iloc[j][1] * 1000,3))
	tech_input[tech_type]['FC'][1].append(round(input_load.iloc[j][2] * 1000,3))
	tech_input[tech_type]['VC'][1].append(round(input_load.iloc[j][3],3))
	tech_input[tech_type]['FuC'][1].append(round(input_load.iloc[j][4],3))


# loading the hydro inputs
tech_type = 'Hydro'
print('Loading the', tech_type, 'inputs.')
input_load = pd.read_excel(inputFile_load, sheet_name=tech_type)

'''
CAPEX ($/kW)
OPEX fixed ($/kW-year)
OPEX variable ($/MWh)
'''

for j in range(length_sim):
	tech_input[tech_type]['IC'][1].append(round(input_load.iloc[j][1] * 1000,3))
	tech_input[tech_type]['FC'][1].append(round(input_load.iloc[j][2] * 1000,3))
	tech_input[tech_type]['VC'][1].append(round(input_load.iloc[j][3],3))


# loading the run of river inputs
tech_type = 'RunOfRiver'
print('Loading the', tech_type, 'inputs.')
input_load = pd.read_excel(inputFile_load, sheet_name=tech_type)

'''
CAPEX ($/kW)
OPEX fixed ($/kW-year)
OPEX variable ($/MWh)
'''

for j in range(length_sim):
	tech_input[tech_type]['IC'][1].append(round(input_load.iloc[j][1] * 1000,3))
	tech_input[tech_type]['FC'][1].append(round(input_load.iloc[j][2] * 1000,3))
	tech_input[tech_type]['VC'][1].append(round(input_load.iloc[j][3],3))

# loading the waste inputs
tech_type = 'Waste'
print('Loading the', tech_type, 'inputs.')
input_load = pd.read_excel(inputFile_load, sheet_name=tech_type)

'''
CAPEX ($/kW)
OPEX fixed ($/kW-year)
OPEX variable ($/MWh)
Fuel cost ($/MWh)
'''

for j in range(length_sim):
	tech_input[tech_type]['IC'][1].append(round(input_load.iloc[j][1] * 1000,3))
	tech_input[tech_type]['FC'][1].append(round(input_load.iloc[j][2] * 1000,3))
	tech_input[tech_type]['VC'][1].append(round(input_load.iloc[j][3],3))
	tech_input[tech_type]['FuC'][1].append(round(input_load.iloc[j][4], 3))

with open('input_techs.pkl', 'wb') as f:
	pickle.dump(tech_input, f)