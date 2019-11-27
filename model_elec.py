from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import math
import random

from model_elec_assets_init import init_assets
from model_elec_agents_init import init_agents
from asset import Asset
from model_elec_assets import SolarAsset, WindAsset, HydroAsset, HydroPumpingAsset, RunOfRiverAsset, WasteAsset,\
	CCGTAsset, NuclearAsset, LTContract, NTCAsset
from model_elec_inputs import inputs_import

'''
- DC None
- PC1 Economy
- PC2 Environment
- S1 Renewable energy production
- S2 Electricity prices
- S3 Renewable investment levels
- S4 Domestic emissions
- S5 Imported emissions
'''

'''
!!! - important - to do
ext. - for extending the code
OC - opportunity costs calculations
technical - technical upgrade for the code for readability
V&V - verification and validation
sim. - for the simulation
'''

'''
6.09.2019 - Observations from the model results:
- There are a lot of blackouts due to the implementation of outages and the implementation of demand growth
- There seems to be a problem of investment
	- The actors are investing into solar the first seven years and then they stop
	- There is no investment in wind (despite the fact that there is no implementation issue as there might be in real
	life)
	- There is no investment in gas, at all.
- Additionally, the prices seem elevated but only a proper averaging of these prices could confirm this. Average yearly
 price is around 50/60 CHF where it should be closer to 45 (this could be due to a problem with how opportunity costs 
 have been implemented)
- The reservoir capacity should oscillate between 0.2 and 0.8 (according to the data from Paul's paper), right now it
is more between 0.01 and 0.2

11.09.2019 - Observations from the model results:
- A msitake in the merit-order algorithm has been fixed.
- New results show a much better reservoir filling curve (ranging from 0.6 to 0.0) but still not what van Baal obtained.
- It also shows prices increasingly growing to 400 CHF by the end of the 15 years simulation.
	This suggests that there is an issue with the investment mechanisms as such a high price should justify the
	investment
	in just about anything. This therefore needs to be checked more thoroughly.
- Somehow, despite investment, the solar never really get close to the theoretical Swiss limit
- Investment for CCGT is now allowed and there is a huge spike for it ... 

24.09.2019 - Observations from the model results:
- There seems to be an issue with the NTC, they are providing a lot of supply. When I say a lot, it is more than twice the
demand that is requried. This might be an issue with the bidding process of the merit order curve.
- This has now be fixed on 25.09 but investment remain at zero. Growth in demand also seems to be inexistant.

25.09.2019 - Observations from the model results:
- There seems to be no investment still. This could be due to a number of issues as the prices are high enough to justify
investment by the investors. It could be a bad update of the prices of bad UF calculation or bad profitability
calculations.
- The demand growth seems to work in the code but it doesn't make a change in the results. It is unclear why at
this point.

27.09.2019 - Observations from the model results:
- The results seem to be correct now. The code has been verified for its entirety.
- Additions to the model at this point are only cosmetic and minor.
'''

# todo [V&V] - introduce the actual prices for 2018 and plot them with the graphs

# todo [sim.] - check the perceived states of the policy actors

# todo [ext.] - add a counter for investements, constructions, plans, decommissioned plants and so on.
# todo [ext.] - change the rejection rates - they are arbitrary right now (tech_params)
# todo [ext.] - for investments - change the permit approval process to take into account of the technology type
#  (wind turbines are not approved the same way as solar)



# Data collector functions
def get_agents_attributes_reservoir_level(model):
	return sum(model.res_lvl_hydro_t_m)/730

def get_agents_attributes_reservoir_level_waste(model):
	return sum(model.res_lvl_waste_t_m) / 730

def get_supply_solar(model):
	return sum(model.solar_m) / 730

def get_supply_wind(model):
	return sum(model.wind_m) / 730

def get_supply_CCGT(model):
	return sum(model.CCGT_m) / 730

def get_supply_hydro(model):
	return sum(model.hydro_m) / 730

def get_supply_hydrop(model):
	return sum(model.hydrop_m) / 730

def get_supply_nuclear(model):
	return sum(model.nuclear_m) / 730

def get_supply_waste(model):
	return sum(model.waste_m) / 730

def get_supply_ror(model):
	return sum(model.runofriver_m) / 730

def get_supply_LTC(model):
	return sum(model.LTC_m) / 730

def get_supply_NTC(model):
	return sum(model.NTC_m) / 730

def get_supply_NTC_FR(model):
	return sum(model.NTC_FR_m) / 730

def get_supply_NTC_DE(model):
	return sum(model.NTC_DE_m) / 730

def get_supply_NTC_IT(model):
	return sum(model.NTC_IT_m) / 730

def get_demand_met(model):
	return sum(model.demand_met_m) / 730

def get_demand_hydrop(model):
	return sum(model.hydrop_de_m) / 730

def get_demand_NTC(model):
	return sum(model.NTC_de_m) / 730

def get_demand_NTC_FR(model):
	return sum(model.NTC_de_FR_m) / 730

def get_demand_NTC_DE(model):
	return sum(model.NTC_de_DE_m) / 730

def get_demand_NTC_IT(model):
	return sum(model.NTC_de_IT_m) / 730

def get_demand(model):
	return sum(model.demand_m) / 730

def get_blackout(model):
	return model.blackout_m / 730

def get_supply_solar_max(model):
	return sum(model.supply_max_solar_m) / 730

def get_supply_wind_max(model):
	return sum(model.supply_max_wind_m) / 730

def get_supply_CCGT_max(model):
	return sum(model.supply_max_CCGT_m) / 730

def get_supply_hydro_max(model):
	return sum(model.supply_max_hydro_m) / 730

def get_supply_hydrop_max(model):
	return sum(model.supply_max_hydrop_m) / 730

def get_supply_waste_max(model): # collecting maximum waste supply possible
	return sum(model.supply_max_waste_m) / 730

def get_supply_runofriver_max(model): # collecting maximum ROR supply possible
	return sum(model.supply_max_ror_m) / 730

def get_pins_SS(model):
	# print('SS', model.pins['SS'])
	return model.pins['SS']

def get_pins_WTS(model):
	return model.pins['WTS']

def get_pins_CD(model):
	return model.pins['CD']

def get_pins_CI(model):
	# print('CI', model.pins['CI'])
	return model.pins['CI']

class Electricity(Model):
	'''
	Electricity model.
	'''

	def __init__(self, demand_growth=0.02, height=20, width=20):
		'''Initialisation of the electricity model'''

		# todo check the MWh vs kWh units throughout the notes

		self.price_foreign = None
		self.height = height # int - height of the grid
		self.width = width # int - width of the grid
		self.grid = SingleGrid(height, width, torus=True)  # type of grid considered
		self.schedule = RandomActivation(self)  # activation of agents order

		self.hourCount = 0 # int - hour counter initialisation
		self.yearCount = 0 # int - year counter initialisation

		self.verbose = 'blackout'  # string - print-monitoring
		# Options: False, merit-order, blackout

		self.demand = 0 # float - [MWh] - demand counter initialisation
		self.demand_growth = demand_growth # float - [-] - demand growth in percentage
		self.demand_increase = 1 # float - [-] - demand increase counter initialisation

		self.t_outage = 67 # int - [hrs] - maintenance time for outage
		self.outage_prob = 0.04/67 # float - probability for an outage

		self.elec_price = 0 # float - [CHF] - electricity price initialisation
		self.elec_price_cum = 0 # float - [CHF] - cumulative electricity price over a year (for averaging)
		self.hurdle_rate = 0.1 # float - [-] - hurdle rate for investors investments
		self.discount_rate = 0.08 # float - [-] - discount rate for investors investments
		self.risk_rate = 0.01 # float - [-] - risk rate for investors investments
		self.max_renovation_number = 2 # int - [-] - limit for asset renovation number
		self.approved_plan_expiry = 5 * 8760  # float - [hrs] - time a plan is allowed to remain in an investor options

		self.demand_met = 0 # float - [MWh] - demand met counter initialisation
		self.unique_id_counter = 0 # int - [-] - ID counter for new assets creation

		self.start_year = 2016 # int - [year] - year of the start of the simulation

		self.VOLL = 3000 # [CHF/MWh] int - - value of lost load

		self.pins = {'SS': 0.04, 'WTS': 0.04, 'CD': 10, 'CI': 10} # dict - policy instrument initialisation - for hybrid model

		self.EOF_time_check = 10 # int - [-] - time before end of life to start actions

		self.collect_data_list_reset() # reset lists to collect monthly data

		# creation of the datacollector vector
		self.datacollector = DataCollector(
			# Model-level variables
			model_reporters =  {
				"step": "hourCount",
				"electricity price": "elec_price",
				"demand": get_demand,
				"supply_solar": get_supply_solar,
				"supply_wind": get_supply_wind,
				"supply_CCGT": get_supply_CCGT,
				"supply_hydro": get_supply_hydro,
				"supply_hydrop": get_supply_hydrop,
				"supply_nuclear": get_supply_nuclear,
				"supply_waste": get_supply_waste,
				"supply_ror": get_supply_ror,
				"supply_LTC": get_supply_LTC,
				"supply_NTC": get_supply_NTC,
				"supply_NTC_FR": get_supply_NTC_FR,
				"supply_NTC_DE": get_supply_NTC_DE,
				"supply_NTC_IT": get_supply_NTC_IT,
				"reservoir_capacity_total_water": "reservoir_capacity_total_water",
				"reservoir_level": get_agents_attributes_reservoir_level,
				"reservoir_level_waste": get_agents_attributes_reservoir_level_waste,
				"supply_solar_max": get_supply_solar_max,
				"supply_wind_max": get_supply_wind_max,
				"supply_CCGT_max": get_supply_CCGT_max,
				"supply_hydro_max": get_supply_hydro_max,
				"supply_hydrop_max": get_supply_hydrop_max,
				"supply_waste_max": get_supply_waste_max,
				"supply_runofriver_max": get_supply_runofriver_max,
				"blackout": get_blackout,
				"demand_met": get_demand_met,
				"demand_hydrop": get_demand_hydrop,
				"demand_NTC": get_demand_NTC,
				"demand_NTC_FR": get_demand_NTC_FR,
				"demand_NTC_DE": get_demand_NTC_DE,
				"demand_NTC_IT": get_demand_NTC_IT,
				"solar_subsidies": get_pins_SS,
				"wind_subsidies": get_pins_WTS,
				"hurdle_rate": "hurdle_rate",
				"domestic_tax": get_pins_CD,
				"import_tax": get_pins_CI
				},
			# Agent-level variables
			agent_reporters = {}
			)

		self.planned_assets = []  # list - list of planned assets
		self.elec_price_yearly = {'All': {'m0': 36.085, 'm1': 40.96, 'm2': 40, 'm3': 40, 'm4': 40},
								  'CCGT': {'m0': 36.085, 'm1': 40.96, 'm2': 40, 'm3': 40, 'm4': 40},
								  'Solar': {'m0': 36.085, 'm1': 40.96, 'm2': 40, 'm3': 40, 'm4': 40},
								  'Wind': {'m0': 36.085, 'm1': 40.96, 'm2': 40, 'm3': 40, 'm4': 40},
								  'Nuclear': {'m0': 36.085, 'm1': 40.96, 'm2': 40, 'm3': 40, 'm4': 40}}
								# dict - [MWh/CHF] - initialisation of yearly electricity prices
		self.invest_saving = {'Solar': 0, 'Wind': 0, 'CCGT': 0} # dict - [CHF] - recording total investments
		self.supply_saving_hourly = {'Hydro': 0, 'Hydrop': 0, 'Solar': 0, 'Wind': 0, 'Nuclear': 0, 'NTC': 0,
								 'LTC': 0, 'CCGT': 0, 'Waste': 0, 'RunOfRiver': 0, 'NTC_FR': 0, 'NTC_DE': 0,
									 'NTC_IT': 0} # dict - [MWh/CHF] - supply recording
		self.demand_saving_hourly = {'Hydrop': 0, 'NTC': 0, 'NTC_FR': 0, 'NTC_DE': 0, 'NTC_IT': 0}
									# dict - [MWh/hrs] - demand recording
		self.supply_saving_yearly = {'Hydro': 0, 'Hydrop': 0, 'Solar': 0, 'Wind': 0, 'Nuclear': 0, 'NTC': 0,
									 'LTC': 0, 'CCGT': 0, 'Waste': 0, 'RunOfRiver': 0, 'NTC_FR': 0, 'NTC_DE': 0,
									 'NTC_IT': 0}  # dict - [MWh/annum] - supply recording
		self.demand_saving_yearly = {'Hydrop': 0, 'NTC': 0, 'NTC_FR': 0, 'NTC_DE': 0, 'NTC_IT': 0}
									# dict - [MWh/annum] - demand recording
		self.tech_params = {
			'CCGT': {'size': 250, 't_permit': int(3 * 8760), 't_construct': int(2 * 8760),
					 't_life': int(55 * 8760), 'rejection_rate': 0.2, 'FC': 10.4, 'VC': None, 'UF': 0.8,
					 'IC': None, 'FuC': None, 'EC': None, 'emissions': 0.342834},
			'Solar': {'size': 40, 't_permit': int(1 * 8760 / 12), 't_construct': int(1 * 8760),
					  't_life': int(30 * 8760), 'rejection_rate': 0.2, 'FC': None, 'VC': 0, 'UF': 0.135, 'IC': None},
			'Wind': {'size': 100, 't_permit': int(1 * 8760 / 12), 't_construct': int(2 * 8760),
					 't_life': int(25 * 8760), 'rejection_rate': 0.6, 'FC': None, 'VC': 0, 'UF': 0.309, 'IC': None},
			'Nuclear': {'UF': 0.8},
			'Coal': {'emissions': 0.88091}}
			# dict -  investment values for new assets
			# size [MW]
			# permit time [hours], construction time [hours], lifetime [hours]
			# rejection rate [%], UF [%],
			# annual fixed costs [CHF/kW/yr], variable costs [CHF/MWh],  investments costs [CHF/MW],
			# emissions [TC/MWh]

		self.scenario = 1 # int - [-] - scenario selection for some of the inputs (0: high, 1: medium, 2: low)
		self.investor_list = [] # list - investors

		init_agents(self) # creation of the agents
		inputs_import(self) # importing all inputs
		init_assets(self) # creation of the assets

		self.calculation_solar_UF_potential() # calculation of utilisation factor for solar
		self.calculation_wind_UF_potential() # calculation of utilisation factor for wind

		# calculation - total reservoir levels
		self.reservoir_capacity_total_waste = 0 # float - [MWh] - initialisation of total waste reservoir counter
		self.reservoir_capacity_total_water = 0 # float - [MWh] - initialisation of total hydro reservoir counter
		for asset_i in self.schedule.agent_buffer(shuffled = False): # calculation of the total hydro and waste potential
			if isinstance(asset_i, WasteAsset):
				self.reservoir_capacity_total_waste += asset_i.reservoir_level_max
			if isinstance(asset_i, HydroAsset) or isinstance(asset_i, HydroPumpingAsset):
				self.reservoir_capacity_total_water += asset_i.reservoir_level_max

		self.blackout = False # bool - [-] - check for blackout

		self.running = True # bool [-] - mesa property (not used here)
		self.numberOfAgents = self.schedule.get_agent_count() # counting the number of agents
		self.datacollector.collect(self) # collecting the data

	def policy_implementation(self, policy):
		'''
		This function performs the implementation of the policy chosen by the policy makers in the policy process.
		:param policy:
		:return:
		'''

		print(policy)

		# [SS] - Solar subsidy
		if policy[0] != None:
			print('0,', self.pins['SS'] + policy[0])
		if policy[0] != None and self.pins['SS'] + policy[0] >= 0:
			self.pins['SS'] += policy[0]

		# [WTS] - Wind turbine subsidy
		if policy[1] != None:
			print('1,', self.pins['WTS'] + policy[1])
		if policy[1] != None and self.pins['WTS'] + policy[1] >= 0:
			self.pins['WTS'] += policy[1]

		# [HR] - Hurdle rate
		if policy[2] != None:
			print('2,', self.hurdle_rate + policy[2])
		if policy[2] != None and self.hurdle_rate + policy[2] >= 0:
			self.hurdle_rate += policy[2]

		# [CD] - Carbon tax domestic
		if policy[3] != None:
			print('3,', self.pins['CD'] + policy[3])
		if policy[3] != None and self.pins['CD'] + policy[3] >= 0:
			self.pins['CD'] += policy[3]

		# [CI] - Carbon tax imports
		if policy[4] != None:
			print('4,', self.pins['CI'] + policy[4])
		if policy[4] != None and self.pins['CI'] + policy[4] >= 0:
			self.pins['CI'] += policy[4]

		print('SS', self.pins['SS'],'- WTS', self.pins['WTS'], '- HR', self.hurdle_rate, '- CD', self.pins['CD'],
			  '- CI', self.pins['CI'])

	def step(self, policy):
		'''
		The step considered here is used for the hybrid model to simulate one year at a time.
		'''

		print(' ')
		print('Year:', self.yearCount)

		self.policy_implementation(policy) # implementing policy chosen
		self.parameter_update_yearly(self.yearCount)  # yearly update of initial parameters

		for i in range(8760): # simulating one year
			self.step_hourly

		pp_KPIs = self.pp_KPI_calculation() # calculating KPIs for policy process
		self.yearCount += 1

		return pp_KPIs

	@property
	def step_hourly(self):

		'''
		A step in this model represents one hour.
		'''

		'''**********************************************************************************************************'''
		'''beginning of step actions - step updates'''

		solar_conditions, wind_conditions, price_reference =  self.parameter_update_hourly() # update initial parameters

		'''**********************************************************************************************************'''
		'''creation of the demand and supply lists (along with their associated costs)'''

		'''supply'''
		supply_list = [] # initialisation of the supply list

		# structure: cost, supply, asset, owner
		for asset_i in self.schedule.agent_buffer(shuffled = False):

			if (isinstance(asset_i, CCGTAsset) or isinstance(asset_i, NuclearAsset)) and asset_i.online:
				cost = asset_i.calculation_cost()
				supply = asset_i.calculation_supply()
				if supply > 0:
					supply_list.append([cost, supply, asset_i, asset_i.owner])

			if isinstance(asset_i, WindAsset) and asset_i.online:
				cost = asset_i.calculation_cost()
				supply = asset_i.calculation_supply(wind_conditions)
				if supply > 0:
					supply_list.append([cost, supply, asset_i, asset_i.owner])

			if isinstance(asset_i, SolarAsset) and asset_i.online:
				cost = asset_i.calculation_cost()
				supply = asset_i.calculation_supply(solar_conditions)
				if supply > 0:
					supply_list.append([cost, supply, asset_i, asset_i.owner])

			if (isinstance(asset_i, WasteAsset) or isinstance(asset_i, HydroAsset)
				or isinstance(asset_i, HydroPumpingAsset)) and asset_i.online:
				cost = asset_i.calculation_cost(price_reference)
				supply = asset_i.calculation_supply()
				if supply > 0:
					supply_list.append([cost, supply, asset_i, asset_i.owner])

			if isinstance(asset_i, RunOfRiverAsset) and asset_i.online:
				cost = asset_i.calculation_cost()
				supply = asset_i.calculation_supply(self.ror_conditions, 1)
				if supply > 0:
					supply_list.append([cost, supply, asset_i, asset_i.owner])

			if isinstance(asset_i, LTContract) and asset_i.online:
				cost = asset_i.calculation_cost()
				supply = asset_i.calculation_supply()
				if supply > 0:
					supply_list.append([cost, supply, asset_i, asset_i])
					# a fourth item supply is added as original supply

			if isinstance(asset_i, NTCAsset) and asset_i.online:
				cost = asset_i.calculation_cost()
				supply = asset_i.calculation_supply()
				if supply > 0 and not math.isnan(cost):
					supply_list.append([cost, supply, asset_i, asset_i])
					if asset_i.country == 'FR':
						self.bordercapacity_france = supply

			if not asset_i.online and asset_i.maint: # progressing offline assets due to outage
				asset_i.maint_time += 1
				if asset_i.maint_time == self.t_outage:
					asset_i.online = True
					asset_i.maint = False

		def getKey(item): # sorting function
			return item[0]

		supply_list = sorted(supply_list, key=getKey) # sorting supplies by lowest cost

		'''demand'''
		demand_list = []

		# structure: cost, demand, asset, owner
		demand_list.append([self.VOLL, self.demand, 0, None]) # inelastic demand

		for asset_i in self.schedule.agent_buffer(shuffled = False): # elastic demand
			if isinstance(asset_i, NTCAsset):
				cost = asset_i.calculation_cost() * 1.01 # importing costs slightly higher than exporting costs (1% increase)
				demand = asset_i.calculation_demand()
				if demand > 0:
					demand_list.append([cost, demand, asset_i, 'NTC'])
			if isinstance(asset_i, HydroPumpingAsset):
				cost = asset_i.calculation_cost_demand(price_reference)
				supply = asset_i.calculation_supply()
				demand = 0
				# making sure that the reservoir is not full already and not empyy
				if asset_i.reservoir_level < asset_i.reservoir_level_max:  
					# making sure there is no over flow
					if supply + asset_i.reservoir_level < asset_i.reservoir_level_max:  
						# print('Reservoir is not full - all capacity available')
						demand = supply
					# if reservoir is almost full - only propose capacity for what is left
					if supply + asset_i.reservoir_level >= asset_i.reservoir_level_max:  
						# print('Reservoir is almost full - only fill up what space is left')
						demand = asset_i.reservoir_level_max - asset_i.reservoir_level
				if demand > 0: # if demand, append
						demand_list.append([cost, demand, asset_i, asset_i.owner])

		demand_list = sorted(demand_list, key=getKey) # sorting the demand list by lowest costs
		demand_list.reverse() # reverse to get highest prices

		if self.verbose == 'merit-order':
			print('\n Hour: ', self.hourCount)
			print('Supply:', supply_list)
			print('Demand:', demand_list, '\n')

		'''**********************************************************************************************************'''
		'''merit-order dispatch of the electricity market'''

		demand_check = 0
		supply_check = 0
		k = 0  # counter to make sure supply is not added twice

		for i in range(len(demand_list)): # going through the demand list
			_demand_cost = demand_list[i][0]
			_demand_level = demand_list[i][1]
			_demand_asset = demand_list[i][2]

			demand_check += _demand_level # updating the demand check
			last_added = 'demand'  # check outlining what was added last
			if isinstance(_demand_asset, HydroPumpingAsset) and _demand_level != 0:# hydrop check
				self.hydro_demand_supply_check(supply_list, _demand_asset)

			for j in range(len(supply_list) - k): # going through the supply list
				# setting some proxy parameters
				_supply_cost = supply_list[k][0]
				_supply_level = supply_list[k][1]
				_supply_asset = supply_list[k][2]

				'''sorting issues with the NTC and LTC FR border capacity'''
				# check that the border capacity with France is not over the limit
				# if the asset is a NTC, then no LTC can be used - all capacity has been taken - LTC supply need
				# to be set to zero
				# but then how to make sure they are not placed into the assignment of funds later on ...
				if isinstance(_supply_asset, NTCAsset) and _supply_asset.country == 'FR':
					for p in range(len(supply_list) - k):  # going through the remainder of the supply assets
						_supply = supply_list[p + k][1]
						_asset_temp = supply_list[p + k][2]
						if isinstance(_asset_temp, LTContract):
							_supply = 0

				# if the asset is a LTC - the NTC capacity has to be decreased by the LTC amount -
				# check performed on the other LTC to make sure that their supply is not larger than the new NTC capacity
				if isinstance(_supply_asset, LTContract) :
					_bordercapacity_FR = 0

					for p in range(len(supply_list) - k): # 1st check the NTC to get a better idea of the capacity left
						_supply = supply_list[p+k][1]
						_asset_temp = supply_list[p+k][2]
						if isinstance(_asset_temp, NTCAsset) and _asset_temp.country == 'FR':
							_supply -= _supply_level
							if _supply < 0: # make sure it is not negative
								_supply = 0
							_bordercapacity_FR = _supply
							break # if capacity is nul or less than zero - move on to next one

					for p in range(len(supply_list) - k): # 2nd check the LTC to make sure they are updated
						_supply = supply_list[p+k][1]
						_asset_temp = supply_list[p+k][2]
						if isinstance(_asset_temp, LTContract):
							# if the supply provided is larger than the border capacity, set the supply to the border
							# capacity
							if _supply >= _bordercapacity_FR:
								_supply = _bordercapacity_FR

				'''case 1 - supply higher than demand and demand costs higher than supply costs
				   add demand'''
				if _demand_cost > _supply_cost and supply_check >= demand_check:
					if i == len(demand_list) - 1: # in the case where all the demand has been met, set price and supply
						self.elec_price = _demand_cost
						self.demand_met = demand_check
					break

				'''case 2 - supply lower than demand and demand costs higher than supply
				   add supply'''
				if _demand_cost > _supply_cost and supply_check <= demand_check:
					supply_check += _supply_level
					last_added = 'supply'

					k += 1 # moving to the next supplier
					if isinstance(_supply_asset, HydroPumpingAsset) and _supply_level != 0: # hydrop check
						self.hydro_demand_supply_check(demand_list, _supply_asset)

				'''case 3 - supply is higher than demand and supply costs higher than demand costs
							   lines crossed - determine crossing point'''
				if _demand_cost <= _supply_cost:
					break

			'''calculating demand met and selecting the electricity price'''
			if _demand_cost <= _supply_cost:

				if last_added == 'supply':  # demand sets the price, supply the amount of electricity
					self.elec_price = _demand_cost  # setting the price of electricity for the entire model
					for p in range(k - 1):  # defining the total demand as the amount produced by the last supplier
						self.demand_met += supply_list[p][1]
					# print(self.hourCount, 'supply:', self.demand_met)

				if last_added == 'demand':  # supply sets the price, demand the amount of electricity
					self.elec_price = _supply_cost  # setting the price of electricity for the entire model
					if i > 1:
						for p in range(i - 1):
							self.demand_met += demand_list[p][1]
					else:
						self.demand_met = demand_list[0][1]
					# print(self.hourCount, 'demand:', self.demand_met)

				if self.verbose == 'merit-order':
					print('The lines have crossed, k:', k)
					if last_added == 'supply':
						print('Supply based')
					if last_added == 'demand':
						print('Demand based')
					print('Supply:', round(supply_check, 2), 'and demand:', round(demand_check, 2),
						  '. With supply cost:', round(_supply_cost, 2), ', and demand cost:', round(_demand_cost, 2),
						  '.\n')

				break # cut first loop

			'''case 4 - runs out the list of supply below demand costs'''
			if self.demand_met == 0 and i == (len(demand_list) - 1)\
					and k == len(supply_list):  # in case runs out of supply but demand costs are still higher
				self.elec_price = _demand_cost
				self.demand_met = supply_check

		# blackout check
		if demand_list[0][1] > self.demand_met and self.verbose == 'blackout': # only considering the inelastic demand
			print('The demand is not met - Blackout at', self.hourCount - (8760*self.yearCount), 'hours.')
			print('The missing amount is:', round(demand_list[0][1] - self.demand_met, 2))
			self.blackout = True

		if self.demand_met == 0: # checking part of the code
			print('Hours:', self.hourCount)
			print(last_added, 'i:', i, ', and k:', k)
			print(self.hourCount, 'demand costs:', round(_demand_cost, 3), ', supply cost:', round(_supply_cost, 3),
				  ', demand check', round(demand_check, 3), ', supply check:', round(supply_check, 3))
			print('Demand met is null \n', 'supply:', supply_list, '\n', 'demand', demand_list)
			supply_list_check = []
			for p in range(len(supply_list)):
				supply_list_check.append(round(supply_list[p][1],2))
			demand_list_check = []
			for p in range(len(demand_list)):
				demand_list_check.append(round(demand_list[p][1],2))
			print('supply:', sum(supply_list_check), supply_list_check, '\n', 'demand',
				  sum(demand_list_check), demand_list_check)
			print(len(demand_list), len(supply_list))
			supply_test = 0
			for i in range(len(supply_list)):
				supply_test += supply_list[i][1]
			print('Supply available:', supply_test, '\n')

		self.elec_price_cum += self.elec_price # cumulative price update

		if self.verbose == 'merit-order':
			print('Outcome is electricity price of', round(self.elec_price, 2), 'CHF; electricity demand of',
				  round(self.demand_met, 2), 'kWh and electricity provided', round(self.demand_met, 2), 'kWh.')
		# end_sup = time.time()
		# print('Time for algo:', end_sup - start_sup)

		'''**********************************************************************************************************'''
		'''attribution of the supply and demand to the agents and/or assets'''

		'''attribute supply'''
		_elec_supplied = 0  # counter used to account for the last item in the merit order
		for i in range(len(supply_list)):
			_supply = supply_list[i][1]
			_asset = supply_list[i][2]

			if self.demand_met - (_elec_supplied + _supply) <= 0: # if last in merit order
				_elec_supplied_last_tech = self.demand_met - _elec_supplied
				_elec_supplied += _elec_supplied_last_tech # update the counter
				self.saving_supply(_asset, _elec_supplied_last_tech)  # datacollector
				_asset.elec_supplied_year += _elec_supplied_last_tech # for UF calculation
				_asset.elec_revenue_year += _elec_supplied_last_tech * self.elec_price # attributing revenue
				if isinstance(_asset, HydroAsset) or isinstance(_asset, HydroPumpingAsset)\
						or isinstance(_asset, WasteAsset):
					_asset.reservoir_level -= _elec_supplied_last_tech # updating reservoir level
				break

			if self.demand_met - (_elec_supplied + _supply) > 0: # if not last in merit order
				_elec_supplied += _supply # update the counter
				self.saving_supply(_asset, _supply)  # datacollector
				_asset.elec_supplied_year += _supply # for UF calculation
				_asset.elec_revenue_year += _supply * self.elec_price # attributing revenue
				if isinstance(_asset, HydroAsset) or isinstance(_asset, HydroPumpingAsset)\
						or isinstance(_asset, WasteAsset):
					_asset.reservoir_level -= _supply # updating reservoir level

		'''attribute demand'''
		_demand_supplied = 0  # counter used to account for the last item in the merit order
		for i in range(len(demand_list)):
			_demand = demand_list[i][1]
			_asset = demand_list[i][2]

			if self.demand_met - (_demand_supplied + _demand) <= 0: # if last in merit order
				_elec_demanded_last_tech = self.demand_met - _demand_supplied # calculating demand left over
				self.saving_demand(_asset, _elec_demanded_last_tech) # datacollector
				if isinstance(_asset, HydroPumpingAsset): # updating reservoir level
					_asset.reservoir_level += _elec_demanded_last_tech
				break # end loop here

			if self.demand_met - (_demand_supplied + _demand) > 0: # if not last in merit order
				_demand_supplied += _demand  # update the counter
				self.saving_demand(_asset, _demand) # datacollector
				if isinstance(_asset, HydroPumpingAsset):
					_asset.reservoir_level += _demand # updating reservoir level

		'''**********************************************************************************************************'''
		'''end of step actions'''

		for asset in self.schedule.agent_buffer(shuffled=False):

			'''nuclear maintenance *********************'''
			# nuclear power plant planned yearly maintenance algorithm
			if isinstance(asset, NuclearAsset):
				if self.hourCount % int(asset.maint_month * 30 * 24) == 0 and self.hourCount > 10:
					# turning off at right time
					asset.online = False
					asset.maint_yearly = True
					asset.maint_yearly_counter = 0  # reset the maintenance counter

				if not asset.online and asset.maint_yearly: # iterate the maintenance time
					asset.maint_yearly_counter += 1  # increment the maintenance counter
					if asset.maint_yearly_counter == asset.maint_length: # turn back on
						asset.online = True
						asset.maint_yearly = False

			'''asset ageing *********************'''
			if isinstance(asset, NuclearAsset) or isinstance(asset, CCGTAsset) or isinstance(asset, WindAsset)\
					or isinstance(asset, SolarAsset) or isinstance(asset, LTContract):
				asset.age += 1

		m = 24 * 7 * 4 # actors and assets decisions interval - every four weeks

		'''investment algorithm *********************'''
		if self.hourCount % m == 0 and self.yearCount >= 2:
			for actor in self.investor_list:
				actor.invest_new_tech(self)  # performing investment checks for the actors

		'''end of life actions (nuclear, CCGT, LTC, wind and solar) *********************'''
		if self.hourCount % m == 0 and self.hourCount != 0:
			self.end_of_life(m) # end of life actions for assets
			self.planned_assets_invest() # updating planned assets

		self.hourCount += 1 # iterate the steps counter

		''' data collection *********************'''
		''' The demand collected is the inflexible demand
			The demand related to cross-country exchanges and hydro pumping is not considered'''

		self.collect_data_list() # collecting data hourly

		if self.hourCount % 730 == 0:
			self.datacollector.collect(self) # recording the data
			self.collect_data_list_reset()

		self.pp_supply_recording() # pp - recording supply

	def collect_data_list(self):
		'''
		This function is used to collect data for the datacollector - this data will be monthly averaged before it is
		output into a csv file.
		:return:
		'''

		# reservoir levels saving
		res_lvl_hydro = []
		res_lvl_waste = []
		for asset in self.schedule.agent_buffer(shuffled=False):
			if isinstance(asset, HydroAsset) or isinstance(asset, HydroPumpingAsset):
				res_lvl_hydro.append(asset.reservoir_level)
			if isinstance(asset, WasteAsset):
				res_lvl_waste.append(asset.reservoir_level)
		res_lvl_hydro_t = sum(res_lvl_hydro)
		res_lvl_waste_t = sum(res_lvl_waste)
		self.res_lvl_hydro_t_m.append(res_lvl_hydro_t)
		self.res_lvl_waste_t_m.append(res_lvl_waste_t)

		# energy supply saving
		self.solar_m.append(self.supply_saving_hourly['Solar'])
		self.wind_m.append(self.supply_saving_hourly['Wind'])
		self.CCGT_m.append(self.supply_saving_hourly['CCGT'])
		self.hydro_m.append(self.supply_saving_hourly['Hydro'])
		self.hydrop_m.append(self.supply_saving_hourly['Hydrop'])
		self.nuclear_m.append(self.supply_saving_hourly['Nuclear'])
		self.waste_m.append(self.supply_saving_hourly['Waste'])
		self.runofriver_m.append(self.supply_saving_hourly['RunOfRiver'])
		self.LTC_m.append(self.supply_saving_hourly['LTC'])
		self.NTC_m.append(self.supply_saving_hourly['NTC'])
		self.NTC_FR_m.append(self.supply_saving_hourly['NTC_FR'])
		self.NTC_DE_m.append(self.supply_saving_hourly['NTC_DE'])
		self.NTC_IT_m.append(self.supply_saving_hourly['NTC_IT'])
		self.demand_met_m.append(self.demand_met)
		self.hydrop_de_m.append(self.demand_saving_hourly['Hydrop'])
		self.NTC_de_m.append(self.demand_saving_hourly['NTC'])
		self.NTC_de_FR_m.append(self.demand_saving_hourly['NTC_FR'])
		self.NTC_de_DE_m.append(self.demand_saving_hourly['NTC_DE'])
		self.NTC_de_IT_m.append(self.demand_saving_hourly['NTC_IT'])
		self.demand_m.append(self.demand)
		if self.blackout:
			self.blackout_m += 1

		# maximum capacities
		supply_max_solar = 0
		supply_max_wind = 0
		supply_max_CCGT = 0
		supply_max_hydro = 0
		supply_max_hydrop = 0
		supply_max_waste = 0
		supply_max_ror = 0
		for asset in self.schedule.agent_buffer(shuffled=False):
			if isinstance(asset, SolarAsset):
				supply_max_solar += asset.installed_capacity
			if isinstance(asset, WindAsset):
				supply_max_wind += asset.installed_capacity
			if isinstance(asset, CCGTAsset):
				supply_max_CCGT += asset.installed_capacity
			if isinstance(asset, HydroAsset):
				supply_max_hydro += asset.installed_capacity
			if isinstance(asset, HydroPumpingAsset):
				supply_max_hydrop += asset.installed_capacity
			if isinstance(asset, WasteAsset):
				supply_max_waste += asset.installed_capacity
			if isinstance(asset, RunOfRiverAsset):
				supply_max_ror += asset.installed_capacity

		self.supply_max_solar_m.append(supply_max_solar)
		self.supply_max_wind_m.append(supply_max_wind)
		self.supply_max_CCGT_m.append(supply_max_CCGT)
		self.supply_max_hydro_m.append(supply_max_hydro)
		self.supply_max_hydrop_m.append(supply_max_hydrop)
		self.supply_max_waste_m.append(supply_max_waste)
		self.supply_max_ror_m.append(supply_max_ror)

	def collect_data_list_reset(self):
		'''
		This function is used to reset the data for the lists collecting the data for the monthly data
		:return:
		'''

		self.res_lvl_hydro_t_m = []
		self.res_lvl_waste_t_m = []
		self.solar_m = []
		self.wind_m = []
		self.CCGT_m = []
		self.hydro_m = []
		self.hydrop_m = []
		self.nuclear_m = []
		self.waste_m = []
		self.runofriver_m = []
		self.LTC_m = []
		self.NTC_m = []
		self.NTC_FR_m = []
		self.NTC_DE_m = []
		self.NTC_IT_m = []
		self.demand_met_m = []
		self.hydrop_de_m = []
		self.NTC_de_m = []
		self.NTC_de_FR_m = []
		self.NTC_de_DE_m = []
		self.NTC_de_IT_m = []
		self.demand_m = []
		self.blackout_m = 0
		self.supply_max_solar_m = []
		self.supply_max_wind_m = []
		self.supply_max_CCGT_m = []
		self.supply_max_hydro_m = []
		self.supply_max_hydrop_m = []
		self.supply_max_waste_m = []
		self.supply_max_ror_m = []


	def hydro_demand_supply_check(self, listing, asset):
		'''
		This function is used to reset the hydro supply or demand if it is already supplying or demanding
		This is done to avoid having a hydro pumping plant both providing and supplying
		:param listing: either demand or supply list
		:param asset: the asset that needs to be checked
		:return:
		'''

		for m in range(len(listing)):
			_asset_temp = listing[m][2]
			if isinstance(_asset_temp, HydroPumpingAsset) and asset.unique_id == _asset_temp.unique_id:
				listing[m][1] = 0  # set demand to 0

	def end_of_life(self, m):
		'''
		Function that performs the end of life actions for the nuclear, solar, wind CCGT assets and LT Contracts
		:return:
		'''

		for asset in self.schedule.agent_buffer(shuffled=False):
			if isinstance(asset, NuclearAsset) or isinstance(asset, CCGTAsset) or isinstance(asset, WindAsset)\
					or isinstance(asset, SolarAsset): # end of life actions for CCGT, wind, solar and nuclear

				if asset.age >= asset.t_life - self.EOF_time_check * 8760: # checking years before actual EOF

					if asset.mothballed: # if asset is mothballed
						asset.mothballed_t_counter += m # add to counter
						if asset.mothballed_t_counter - asset.mothballed_start >= 8760: # mothball gone for one year
							self.end_of_life_profitability(asset, True) # check new profitability

					if not asset.mothballed: # if asset not mothballed
						self.end_of_life_profitability(asset, False) # check profitability

			if isinstance(asset, LTContract): # end of life actions for LTContracts
				if asset.age >= asset.t_life:
					self.asset_decommissioning(asset)

	def end_of_life_profitability(self, asset, mothball_check):
		'''
		Checking profitability of assets at their end of life and choosing on the appropriate actions to be performed
		:param asset:
		:param mothball_check:
		:return:
		'''

		five_year_profitability = asset.owner.calculation_profitability(5, self, asset)
		one_year_profitability = asset.owner.calculation_profitability(1, self, asset)

		if one_year_profitability < 0 and asset.t_life >= asset.age:
			'''# if negative one year - decommission (if at age)'''
			self.asset_decommissioning(asset)

		elif five_year_profitability >= 0 and one_year_profitability < 0:
			'''if positive five year but negative one year - mothball'''
			self.asset_mothball(asset)

		elif one_year_profitability > 0:
			'''positive - renovate'''
			if asset.renovated == self.max_renovation_number and asset.age >= asset.t_life:
				'''if renovated enough - decommission'''
				self.asset_decommissioning(asset)

			elif asset.renovated < self.max_renovation_number:
				'''if not renovated enough - renovate once more'''
				asset.renovated += 1
				asset.t_life += 5 * 8760  # adding 5 years to the t_life of the plant
				asset.renovated += 1

				if mothball_check:
					self.asset_demothball(asset)

			elif asset.renovated == self.max_renovation_number and asset.age < asset.t_life:
				'''if renovated enough but below life limit - let it continue (and demothball if it had been)'''
				asset.renovated += 1
				asset.t_life += 5 * 8760  # adding 5 years to the t_life of the plant
				asset.renovated += 1

				if mothball_check:
					self.asset_demothball(asset)

	def asset_decommissioning(self, asset):

		'''
		Function used to decommission assets
		:param asset:
		:return:
		'''

		asset.online = False # turning asset offline
		self.schedule.remove(asset)  # remove from schedule
		if asset.tech_type == 'Solar':  # UF update after decommissionning
			self.calculation_solar_UF_potential()
		if asset.tech_type == 'Wind':  # UF update after decommissionning
			self.calculation_wind_UF_potential()

	def asset_mothball(self, asset):

		'''
		Function used to mothball assets. This can be done during renovation or can be assessed on a yearly basis.
		:param asset:
		:return:
		'''

		asset.mothballed = True
		asset.mothballed_start = self.hourCount
		asset.mothballed_t_counter = self.hourCount
		asset.online = False
		asset.t_life += 8760 # increase asset life by one year

	def asset_demothball(self, asset):

		'''
		Function used to take asset sout of mothballing. This is assessed one year after one year of mothballing
		:param asset:
		:return:
		'''

		asset.mothballed = False
		asset.online = True

	def saving_supply(self, asset, supply):

		'''
		Recording the supply for the assets
		:param asset:
		:param supply:
		:return:
		'''

		tech_types_all = ['Hydro', 'Hydrop', 'Solar', 'Wind', 'Nuclear', 'Waste', 'CCGT', 'RunOfRiver', 'LTC', 'NTC']
		tech_assets_all = [HydroAsset, HydroPumpingAsset, SolarAsset, WindAsset, NuclearAsset, WasteAsset,
								CCGTAsset, RunOfRiverAsset, LTContract, NTCAsset]

		for p in range(len(tech_types_all)):
			if isinstance(asset, tech_assets_all[p]):
				self.supply_saving_hourly[tech_types_all[p]] += supply

		if isinstance(asset, NTCAsset):
			if asset.country == 'FR':
				self.supply_saving_hourly['NTC_FR'] += supply
			if asset.country == 'DE':
				self.supply_saving_hourly['NTC_DE'] += supply
			if asset.country == 'IT':
				self.supply_saving_hourly['NTC_IT'] += supply

	def saving_demand(self, asset, demand):

		'''
		Recording the demand for the assets
		:param asset:
		:param demand:
		:return:
		'''

		if isinstance(asset, HydroPumpingAsset):
			self.demand_saving_hourly['Hydrop'] += demand
		if isinstance(asset, NTCAsset):
			self.demand_saving_hourly['NTC'] += demand
			if asset.country == 'FR':
				self.demand_saving_hourly['NTC_FR'] += demand
			if asset.country == 'DE':
				self.demand_saving_hourly['NTC_DE'] += demand
			if asset.country == 'IT':
				self.demand_saving_hourly['NTC_IT'] += demand

	def planned_assets_invest(self):
		'''
		This is the function that is used to deal with the planned assets - approve them - construct them - remove them
		Steps: approval and approval_since -> approved and approved_since -> construction and construction_since
		:return:
		'''

		for asset_k in self.planned_assets:
			# todo [ext.] - introduce different approval procedures for solar and wind and CCGT

			if asset_k.approval:
				'''in approval process'''
				if asset_k.approval_since >= self.tech_params[asset_k.tech_type]['t_permit']: # permit provided or not
					permit_check = random.random() # generating a random number
					if permit_check >= 0.2: # permit given
						asset_k.approved = True # bool - [-] - setting approved to true
						asset_k.approved_since = 0 # int - [-] - resetting the approval waiting time counter
						asset_k.approval = False # bool - [-] - resetting approval variable
						asset_k.approval_since = False # int - [-] - resetting approval timer variable

					else: # permit not given
						self.planned_assets.remove(asset_k) # removing the asset from planned asset list
						asset_k.owner.planned_assets[asset_k.tech_type] -= 1  # updating the owner planned assets count

			'''approved - not yet in construction'''
			if asset_k.approved:
				if asset_k.approved_since >= self.approved_plan_expiry: # plan is too old, remove asset
					self.planned_assets.remove(asset_k) # removing the asset from the planned asset list
					asset_k.owner.planned_assets[asset_k.tech_type] -= 1  # updating the planned assets count
				else: # profitability check for construction
					owner_ = asset_k.owner # selecting the owner
					tech_type_ = asset_k.tech_type # selecting the tech type
					NPV, profitability_index = owner_.calculation_NPV(self, tech_type_) # profitability calculation
					if profitability_index > self.hurdle_rate \
						and owner_.construct_count < 5: # the asset is profitable, allow construction
						asset_k.construction = True # bool - [-] - setting construction to true
						asset_k.construction_since = 0 # int - [-] - resetting the construction counter
						asset_k.approved = False # bool - [-] - resetting approved to false
						asset_k.approved_since = False # int - [-] - resetting approved timer variable
						owner_.construct_count += 1 # update construction count
						self.pp_investment_recording(asset_k) # pp - record the investment [hybrid model]

			'''in construction'''
			if asset_k.construction and asset_k.construction_since >= self.tech_params[asset_k.tech_type]['t_construct']:
				'''construction of the asset and addition to the schedule'''
				unique_id_ = 250 + self.unique_id_counter # int - [-] - setting a unique ID
				self.unique_id_counter += 1 # incrementing the unique ID
				tech_type_ = asset_k.tech_type # selecting the tech type
				size_plant_ = self.tech_params[tech_type_]['size'] # selecting the plant size
				t_life_ = self.tech_params[tech_type_]['t_life'] # selecting the life time
				cost_capital_ = size_plant_ * self.tech_params[tech_type_]['IC'] # selecting the investment costs
				FC_ = self.tech_params[tech_type_]['FC'] # selecting the fixed costs
				VC_ = self.tech_params[tech_type_]['VC'] # selecting the variable costs
				UF_ = self.tech_params[tech_type_]['UF'] # selecting the utilisation factor
				owner_ = asset_k.owner # selecting the owner
				owner_.construct_count -= 1  # update construction count
				age_ = 0 # int - [hrs] - resetting the age
				online_ = True # bool - [-] - resetting the online variable

				if tech_type_ == 'Solar': # solar
					asset_new = SolarAsset(unique_id_, self, owner_, tech_type_, size_plant_, t_life_, age_, online_,
										   cost_capital_, FC_, VC_, UF_) # creation of solar asset
					self.schedule.add(asset_new) # adding new asset to schedule
					self.calculation_solar_UF_potential() # update of solar utilisation factor potential

				if tech_type_ == 'Wind': # wind
					asset_new = WindAsset(unique_id_, self, owner_, tech_type_, size_plant_, t_life_, age_, online_,
										  cost_capital_, FC_, VC_, UF_) # creation of wind asset
					self.schedule.add(asset_new) # adding new asset to schedule
					self.calculation_wind_UF_potential() # update of wind utilisation factor potential

				if tech_type_ == 'CCGT': # CCGT
					emissions_ = self.tech_params[tech_type_]['emissions']
					EC_ = self.tech_params[tech_type_]['EC'] # selecting emissions costs
					asset_new = CCGTAsset(unique_id_, self, owner_, tech_type_, size_plant_, t_life_, age_, online_,
										  cost_capital_, FC_, VC_, UF_, EC_,emissions_) # creation of CCGT asset
					step = int(self.hourCount / 8760)
					asset_new.FuC = self.tech_input['Waste']['FuC'][self.scenario][step]
					self.schedule.add(asset_new) # adding new asset to schedule

				self.planned_assets.remove(asset_k) # remove asset from planned asset list
				owner_.planned_assets[tech_type_] -= 1  # updating the planned assets count

	def elec_UF_elec_prices_updates(self):

		'''
		This is that function that is used to update the electricity prices and utilization factors per technology
		types for which a profitability study is needed or a NPV is needed
		:param n: this is the time step (usually set at 8760 but occasionally changed for testing)
		:return:
		'''

		tech_types = ['Solar', 'Wind', 'CCGT', 'Nuclear'] # list - [-] - technology types
		elec_price_yearly = {'Solar': 0, 'Wind': 0, 'CCGT': 0, 'Nuclear': 0} # dict - [-] - initialisation
		UF_temp = {'Solar': 0, 'Wind': 0, 'CCGT': 0, 'Nuclear': 0} # dict - [-] - initialisation
		number_assets = {'Solar': 0, 'Wind': 0, 'CCGT': 0, 'Nuclear': 0} # dict - [-] - initialisation

		for asset in self.schedule.agent_buffer(shuffled=False): # looking through the schedule
			if isinstance(asset, SolarAsset) or isinstance(asset, WindAsset) or isinstance(asset, CCGTAsset)\
					or isinstance(asset, NuclearAsset): # select only solar, wind, CCGT and nuclear assets
				capacity = asset.installed_capacity # assign capacity
				supply = asset.elec_supplied_year # assign supply
				revenue = asset.elec_revenue_year # assign revenue
				if isinstance(asset, SolarAsset): # assign tech type
					tech_type = 'Solar'
				if isinstance(asset, WindAsset): # assign tech type
					tech_type = 'Wind'
				if isinstance(asset, CCGTAsset): # assign tech type
					tech_type = 'CCGT'
				if isinstance(asset, NuclearAsset): # assign tech type
					tech_type = 'Nuclear'

				UF_temp[tech_type] += supply / (capacity * 8760) # update the utilisation factor per asset
				if supply != 0: # make sure that the supply is not null
					elec_price_yearly[tech_type] += revenue / supply # calculating price per MWh
				else: # in case there is no supply
					elec_price_yearly[tech_type] += 0
				number_assets[tech_type] += 1 # incrementing the number of assets per tech type

		# updating the former electricity prices for all technologies
		for i in range(len(tech_types)):
			# updating the historical prices forward by one year
			self.elec_price_yearly[tech_types[i]]['m4'] = self.elec_price_yearly[tech_types[i]]['m3']
			self.elec_price_yearly[tech_types[i]]['m3'] = self.elec_price_yearly[tech_types[i]]['m2']
			self.elec_price_yearly[tech_types[i]]['m2'] = self.elec_price_yearly[tech_types[i]]['m1']
			self.elec_price_yearly[tech_types[i]]['m1'] = self.elec_price_yearly[tech_types[i]]['m0']

			# calculate the yearly average price
			if number_assets[tech_types[i]] != 0: # checking for number of assets
				self.elec_price_yearly[tech_types[i]]['m0'] =\
					elec_price_yearly[tech_types[i]] / number_assets[tech_types[i]] # calculating price for that year
			else: # if number of assets is null
				self.elec_price_yearly[tech_types[i]]['m0'] = 0

			# updating the utilisation factors
			if number_assets[tech_types[i]] != 0: # checking for number of assets
				self.tech_params[tech_types[i]]['UF'] = UF_temp[tech_types[i]] / number_assets[tech_types[i]]
																# calculating utilisation factor for that year
			else: # if number of assets is null
				self.tech_params[tech_types[i]]['UF'] = 0

	def pp_investment_recording(self, asset_k):

		'''
		This function is used for the policy process KPI to record the amount of investments
		:param asset_k:
		:return:
		'''

		if asset_k.tech_type == 'CCGT':
			self.invest_saving['CCGT'] += self.tech_params[asset_k.tech_type]['IC']
		if asset_k.tech_type == 'Solar':
			self.invest_saving['Solar'] += self.tech_params[asset_k.tech_type]['IC']
		if asset_k.tech_type == 'Wind':
			self.invest_saving['Wind'] += self.tech_params[asset_k.tech_type]['IC']

	def pp_supply_recording(self):

		'''
		This function is used for the policy process KPI to record the amount of supply per technology type
		:return:
		'''

		self.supply_saving_yearly['Solar'] += self.supply_saving_hourly['Solar']
		self.supply_saving_yearly['CCGT'] += self.supply_saving_hourly['CCGT']
		self.supply_saving_yearly['Wind'] += self.supply_saving_hourly['Wind']
		self.supply_saving_yearly['Nuclear'] += self.supply_saving_hourly['Nuclear']
		self.supply_saving_yearly['Hydro'] += self.supply_saving_hourly['Hydro']
		self.supply_saving_yearly['Hydrop'] += self.supply_saving_hourly['Hydrop']
		self.supply_saving_yearly['Waste'] += self.supply_saving_hourly['Waste']
		self.supply_saving_yearly['RunOfRiver'] += self.supply_saving_hourly['RunOfRiver']
		self.supply_saving_yearly['LTC'] += self.supply_saving_hourly['LTC']
		self.supply_saving_yearly['NTC'] += self.supply_saving_hourly['NTC']
		self.supply_saving_yearly['NTC_FR'] += self.supply_saving_hourly['NTC_FR']
		self.supply_saving_yearly['NTC_DE'] += self.supply_saving_hourly['NTC_DE']
		self.supply_saving_yearly['NTC_IT'] += self.supply_saving_hourly['NTC_IT']

	def parameter_update_yearly(self, step):
		'''
		This function consists of all the parameters that are only updated yearly
		It is divided between parameters updated at the beginning of a step and those at the end
		:return:
		'''

		# update for the individual asset calculations - yearly parameters only
		for asset_i in self.schedule.agent_buffer(shuffled=False):
			if isinstance(asset_i, SolarAsset):
				asset_i.IC = self.tech_input['Solar']['IC'][self.scenario][step]
				asset_i.FC = self.tech_input['Solar']['FC'][self.scenario][step]
			if isinstance(asset_i, WindAsset):
				asset_i.IC = self.tech_input['Wind']['IC'][self.scenario][step]
				asset_i.FC = self.tech_input['Wind']['FC'][self.scenario][step]
			if isinstance(asset_i, CCGTAsset):
				asset_i.IC = self.tech_input['CCGT']['IC'][self.scenario][step]
				asset_i.FC = self.tech_input['CCGT']['FC'][self.scenario][step]
				asset_i.VC = self.tech_input['CCGT']['VC'][self.scenario][step]
				asset_i.FuC = self.tech_input['CCGT']['FuC'][self.scenario][step]
				asset_i.EC = self.emission_price[step] + self.pins['CD']
			if isinstance(asset_i, NuclearAsset):
				asset_i.IC = self.tech_input['Nuclear']['IC'][self.scenario][step]
				asset_i.FC = self.tech_input['Nuclear']['FC'][self.scenario][step]
				asset_i.VC = self.tech_input['Nuclear']['VC'][self.scenario][step]
				asset_i.FuC = self.tech_input['Nuclear']['FuC'][self.scenario][step]
			if isinstance(asset_i, HydroAsset) or isinstance(asset_i, HydroPumpingAsset):
				asset_i.IC = self.tech_input['Hydro']['IC'][self.scenario][step]
				asset_i.FC = self.tech_input['Hydro']['FC'][self.scenario][step]
				asset_i.VC = self.tech_input['Hydro']['VC'][self.scenario][step]
			if isinstance(asset_i, RunOfRiverAsset):
				asset_i.IC = self.tech_input['RunOfRiver']['IC'][self.scenario][step]
				asset_i.FC = self.tech_input['RunOfRiver']['FC'][self.scenario][step]
				asset_i.VC = self.tech_input['RunOfRiver']['VC'][self.scenario][step]
			if isinstance(asset_i, WasteAsset):
				asset_i.IC = self.tech_input['Waste']['IC'][self.scenario][step]
				asset_i.FC = self.tech_input['Waste']['FC'][self.scenario][step]
				asset_i.VC = self.tech_input['Waste']['VC'][self.scenario][step]
				asset_i.FuC = self.tech_input['Waste']['FuC'][self.scenario][step]

		# update for the agent investments calculations
		tech_type = 'Solar'
		self.tech_params[tech_type]['IC'] = self.tech_input[tech_type]['IC'][self.scenario][step]
		self.tech_params[tech_type]['FC'] = self.tech_input[tech_type]['FC'][self.scenario][step]
		tech_type = 'Wind'
		self.tech_params[tech_type]['IC'] = self.tech_input[tech_type]['IC'][self.scenario][step]
		self.tech_params[tech_type]['FC'] = self.tech_input[tech_type]['FC'][self.scenario][step]
		tech_type = 'CCGT'
		self.tech_params[tech_type]['IC'] = self.tech_input[tech_type]['IC'][self.scenario][step]
		self.tech_params[tech_type]['FC'] = self.tech_input[tech_type]['FC'][self.scenario][step]
		self.tech_params[tech_type]['VC'] = self.tech_input[tech_type]['VC'][self.scenario][step]
		self.tech_params[tech_type]['FuC'] = self.tech_input[tech_type]['FuC'][self.scenario][step]
		self.tech_params[tech_type]['EC'] = self.emission_price[step] + self.pins['CD']

		# update of the country coal and CCGT mixes
		CCGT_em = self.tech_params['CCGT']['emissions']
		coal_em = self.tech_params['Coal']['emissions']
		self.share_CCGT_DE = self.mix_DE_CCGT[step]
		self.share_coal_DE = self.mix_DE_coal[step]
		self.import_DE_em = self.pins['CI'] * (self.share_CCGT_DE * CCGT_em + self.share_coal_DE * coal_em)
		self.share_CCGT_FR = self.mix_FR_CCGT[step]
		self.share_coal_FR = self.mix_FR_coal[step]
		self.import_FR_em = self.pins['CI'] * (self.share_CCGT_FR * CCGT_em + self.share_coal_FR * coal_em)
		self.share_coal_IT = self.mix_IT_coal[step]
		self.share_CCGT_IT = self.mix_IT_CCGT[step]
		self.import_IT_em = self.pins['CI'] * (self.share_CCGT_IT * CCGT_em + self.share_coal_IT * coal_em)

		if self.yearCount != 0: # updates to be done at the end of the step

			self.elec_UF_elec_prices_updates() # update historical prices and utilisation factors

			# updating the historical electricity prices (general)
			self.elec_price_yearly['All']['m4'] = self.elec_price_yearly['All']['m3']
			self.elec_price_yearly['All']['m3'] = self.elec_price_yearly['All']['m2']
			self.elec_price_yearly['All']['m2'] = self.elec_price_yearly['All']['m1']
			self.elec_price_yearly['All']['m1'] = self.elec_price_yearly['All']['m0']
			self.elec_price_yearly['All']['m0'] = self.elec_price_cum / 8760 # calculate the yearly average price
			self.elec_price_cum = 0 # reset the cumulative electricity price

			# adjusting run of river supply growth
			ror_yearly_production = 0 # reset run of river yearly production
			for asset in self.schedule.agent_buffer(shuffled=False):
				if isinstance(asset, RunOfRiverAsset):
					ror_yearly_production += asset.elec_supplied_year # calculating run of river supply

			# adjusting run of river growth
			if ror_yearly_production != 0: # making sure production is not null
				if self.yearCount < (2020 - self.start_year):
					self.ror_capacity_growth = 16400000 / ror_yearly_production
				if self.yearCount >= (2020 - self.start_year) and self.yearCount < (2025 - self.start_year):
					self.ror_capacity_growth = 16700000 / ror_yearly_production
				if self.yearCount >= (2025 - self.start_year) and self.yearCount < (2035 - self.start_year):
					self.ror_capacity_growth = 16933000 / ror_yearly_production
				if self.yearCount >= (2035 - self.start_year) and self.yearCount < (2050 - self.start_year):
					self.ror_capacity_growth = 17533000 / ror_yearly_production
				if self.yearCount >= (2050 - self.start_year):
					self.ror_capacity_growth = 18333000 / ror_yearly_production
			else:
				self.ror_capacity_growth = 0

			for asset in self.schedule.agent_buffer(shuffled=False):
				asset.elec_revenue_year = 0  # reset of the revenue per asset
				if not isinstance(asset, NTCAsset):
					asset.UF = asset.elec_supplied_year / (asset.installed_capacity * 8760) # utilisation factor calc.
					asset.elec_supplied_year = 0 # yearly reset of electricity supplied
				if isinstance(asset, RunOfRiverAsset):
					asset.installed_capacity *= self.ror_capacity_growth # updating installed capacity of run of river
				if isinstance(asset, NTCAsset): # NTC calculation (considering the variable capacity over time)
					asset.UF = asset.elec_supplied_year / (sum(asset.installed_capacity))
					asset.elec_supplied_year = 0 # yearly reset of electricity supplied
					asset.installed_capacity = [] # reset the list for the upcoming year

			self.invest_saving = {'Solar': 0, 'Wind': 0, 'CCGT': 0}  # reset of investment recording dict [hybrid model]
			self.supply_saving_yearly = {'Hydro': 0, 'Hydrop': 0, 'Solar': 0, 'Wind': 0, 'Nuclear': 0, 'NTC': 0,
										 'LTC': 0, 'CCGT': 0, 'Waste': 0, 'RunOfRiver': 0, 'NTC_FR': 0, 'NTC_DE': 0,
										 'NTC_IT': 0}  # dict for supply recording reset

			self.demand_increase *= (1 + self.demand_growth) # demand growth

	def parameter_update_hourly(self):
		'''
		This function consists of all the parameters that are updated hourly
		:return:
		'''

		self.supply_saving_hourly = {'Hydro': 0, 'Hydrop': 0, 'Solar': 0, 'Wind': 0, 'Nuclear': 0, 'NTC': 0,
									 'LTC': 0, 'CCGT': 0, 'Waste': 0, 'RunOfRiver': 0, 'NTC_FR': 0, 'NTC_DE': 0,
									 'NTC_IT': 0}  # reset the supply saving dictionnary
		self.demand_saving_hourly = {'Hydrop': 0, 'NTC': 0, 'NTC_FR': 0, 'NTC_DE': 0, 'NTC_IT': 0}
										# reset the demand saving dictionnary
		self.demand_met = 0 # reset the demand met parameter
		self.blackout = False # reset blackout parameter

		for asset_i in self.schedule.agent_buffer(shuffled = False): # reservoir level updates
			if isinstance(asset_i, HydroAsset) or isinstance(asset_i, HydroPumpingAsset):
				asset_i.reservoir_step_update(self.water_inflow_year, self.inflow_conditions,
											  self.reservoir_capacity_total_water)
			if isinstance(asset_i, WasteAsset):
				asset_i.reservoir_step_update(self.waste_inflow, self.reservoir_capacity_total_waste)

		for asset_i in self.schedule.agent_buffer(shuffled=False): # update export and import capacities and prices
			if isinstance(asset_i, NTCAsset):
				capacity_ex = self.capacity_ex # capacity export selection
				capacity_im = self.capacity_im # capacity import selection
				price_foreign = self.price_foreign # foreign price selection
				if asset_i.country == 'FR':
					index_country = 0 # index selection for the country
					imports = self.import_FR_em # carbon tax pricing [hybrid model]
				if asset_i.country == 'DE':
					index_country = 1 # index selection for the country
					imports = self.import_DE_em # carbon tax pricing [hybrid model]
				if asset_i.country == 'IT':
					index_country = 2 # index selection for the country
					imports = self.import_IT_em # carbon tax pricing [hybrid model]
				index_input_c = self.hourCount % len(capacity_ex[index_country]) # selection of the index
				asset_i.installed_capacity_ex = capacity_ex[index_country][index_input_c] # export capacity updates
				asset_i.installed_capacity_im = capacity_im[index_country][index_input_c] # import capacity updates
				index_input_p = self.hourCount % len(price_foreign[index_country]) # selection of the index
				asset_i.C = self.price_foreign[index_country][index_input_p] + imports # costs updates

		for asset_k in self.planned_assets: # incremental age updates of the planned assets
			if asset_k.approval:
				asset_k.approval_since += 1
			if asset_k.approved:
				asset_k.approved_since += 1
			if asset_k.construction:
				asset_k.construction_since += 1

		index_input = self.hourCount % len(self.load) # demand index selection
		self.demand = self.load[index_input] * self.demand_increase # demand update dependent on growth

		for asset_i in self.schedule.agent_buffer(shuffled=False): # random outages
			if random.random() <= self.outage_prob:
				asset_i.online = False
				asset_i.maint = True
				asset_i.maint_time = 0

		index_input = self.hourCount % len(self.solar_conditions) # selection of the index
		solar_conditions = self.solar_conditions[index_input] * self.solar_UF_potential # condition calculation solar

		index_input = self.hourCount % len(self.wind_conditions) # selection of the index
		wind_conditions = self.wind_conditions[index_input] * self.wind_UF_potential # condition calculation wind

		# price reference used for opportunity costs calculation [hourly]
		price_reference = 2 * (1 / 6) * (
				3 * self.elec_price_yearly['All']['m0'] + 2 * self.elec_price_yearly['All']['m1'] +
				self.elec_price_yearly['All']['m2'])

		return solar_conditions, wind_conditions, price_reference

	def calculation_solar_UF_potential(self):

		'''
		Calculate the utilisation factor potential for solar
		Done at the beginning and for every new construction
		:return:
		'''

		solar_total_capacity = 0 # float - [MW] - initialisation of counter
		for asset_i in self.schedule.agent_buffer(shuffled=False):
			if isinstance(asset_i, SolarAsset):
				solar_total_capacity += asset_i.installed_capacity # calculation of total installed capacity
		solar_maximum = 19702  # float - [MW] - theoretical maximum for Switzerland
		ratio = solar_total_capacity / solar_maximum # calculating the ratio
		if ratio < 0.0367:
			self.solar_UF_potential = 0.0147
		if ratio >= 0.0367 and ratio < 0.9306:
			self.solar_UF_potential = 0.1358
		if ratio >= 0.9306 and ratio < 1:
			self.solar_UF_potential = 0.114155
		if ratio == 1:
			self.solar_UF_potential = 0.100114

	def calculation_wind_UF_potential(self):

		'''
		Calculate the utilisation factor potential for wind
		Done at the beginning and for every new construction
		:return:
		'''

		wind_total_capacity = 0 # float - [MW] - initialisation of counter
		for asset_i in self.schedule.agent_buffer(shuffled=False):
			if isinstance(asset_i, WindAsset):
				wind_total_capacity += asset_i.installed_capacity # calculation of total installed capacity
		wind_maximum = 2282  # float - [MW] - theoretical maximum for Switzerland
		ratio = wind_total_capacity / wind_maximum # calculating the ratio
		if ratio < 0.181:
			self.wind_UF_potential = 0.3196
		if ratio >= 0.181 and ratio < 0.195:
			self.wind_UF_potential = 0.2497
		if ratio >= 0.195 and ratio < 0.267:
			self.wind_UF_potential = 0.2457
		if ratio >= 0.267 and ratio < 1:
			self.wind_UF_potential = 0.2301
		if ratio == 1:
			self.wind_UF_potential = 0.1608

	def pp_KPI_calculation(self):
		'''
		This is the function that is used to calculate the KPIs that are used for the policy process agents
		[hybrid model]
		:return:
		'''

		# unpacking the parameters for simplicity
		supply_solar = self.supply_saving_yearly['Solar']
		supply_CCGT = self.supply_saving_yearly['CCGT']
		supply_wind = self.supply_saving_yearly['Wind']
		supply_nuclear = self.supply_saving_yearly['Nuclear']
		supply_hydro = self.supply_saving_yearly['Hydro']
		supply_hydrop = self.supply_saving_yearly['Hydrop']
		supply_waste = self.supply_saving_yearly['Waste']
		supply_ror = self.supply_saving_yearly['RunOfRiver']
		supply_LTC = self.supply_saving_yearly['LTC']
		supply_NTC_FR = self.supply_saving_yearly['NTC_FR']
		supply_NTC_DE = self.supply_saving_yearly['NTC_DE']
		supply_NTC_IT = self.supply_saving_yearly['NTC_IT']

		# KPI calculation - renewable energy production
		'''0: no electricity is RES - 1: all electricity is RES'''
		total_supply = supply_solar + supply_CCGT + supply_wind + supply_nuclear + \
					   supply_hydro + supply_hydrop + supply_waste + supply_ror # obtaining total supply of electricity
		RES_supply = supply_solar + supply_wind + supply_hydro + supply_hydrop + supply_ror
															# obtainining renewable supply of electricity
		self.S1_RES_supply = RES_supply / total_supply # normalising

		# KPI calculation - electricity prices
		'''0: prices are at the maximum - 1: prices are null'''
		elec_prices_max = 200 # selecting an abritrary maximum price (based on modeller experience)
		elec_prices_avg = self.elec_price_yearly['All']['m0']
		if elec_prices_avg <= elec_prices_max: # making sure that the avg price is not too high
			self.S2_elec_prices = (elec_prices_max - elec_prices_avg) / elec_prices_max # normalising
		else: # making sure that the KPI will not be negative
			self.S2_elec_prices = 0
			print('Warning! The yearly average electricity price is too high for this calculation to work.')

		# KPI calculation - renewable energy investment level
		'''0: no investments in RES - 1: all investments are RES'''
		total_invest = self.invest_saving['Wind'] + self.invest_saving['Solar']\
					   + self.invest_saving['CCGT'] # calculating total investments
		renew_invest = self.invest_saving['Wind'] + self.invest_saving['Solar'] # calculating renewable investments
		if total_invest == 0: # making sure that there is no division by 0
			self.S3_RES_invest = 0
		else:
			self.S3_RES_invest = renew_invest / total_invest # normalising

		# KPI calculation - domestic emissions level
		'''0: domestic emissions are maximum - 1: domestic emissions are minimum'''
		# if self.yearCount == 0:
		# 	self.supply_CCGT_max = (supply_CCGT) * 5
		self.supply_CCGT_max = 20000000 # arbitrary value used for the normalisation
		self.S4_dome_em_t = (self.supply_CCGT_max - supply_CCGT) / self.supply_CCGT_max

		# KPI calculation - imported emissions level
		'''0: imported emissions are very high - 1: imported emissions are null'''
		CCGT_em = self.tech_params['CCGT']['emissions']
		coal_em = self.tech_params['Coal']['emissions']
		# recording the amount of imports per country
		import_FR_em = (supply_NTC_FR + supply_LTC) * (self.share_CCGT_FR * CCGT_em + self.share_coal_FR * coal_em)
		import_DE_em = supply_NTC_DE * (self.share_CCGT_DE * CCGT_em + self.share_coal_DE * coal_em)
		import_IT_em = supply_NTC_IT * (self.share_CCGT_IT * CCGT_em + self.share_coal_IT * coal_em)
		import_em = import_FR_em + import_DE_em + import_IT_em
		# calculation of the maximum import as 5% of the maximum initial set up
		# if self.yearCount < 2: # checking for the first three rounds
		# 	self.import_em_max = (import_FR_em + import_DE_em + import_IT_em) * 1.50
		# 	if self.import_em_max < import_em:
		# 		self.import_em_max == (import_FR_em + import_DE_em + import_IT_em) * 1.50
		self.import_em_max = 9000000 # arbitrary value used for the normalisation
		# print('S5:', round(import_em, 2), round(self.import_em_max, 2))
		# normalising
		self.S5_import_em_t = (self.import_em_max - import_em) / self.import_em_max

		# KPI calculation - economy
		'''
		The economy policy core problem focuses on low energy prices, and amount of renewable investments.
		self.S2_elec_prices should be at 1
		self.S3_RES_invest should be at 1
		'''
		self.PC1_economy = 0.75 * self.S2_elec_prices + 0.25 * self.S3_RES_invest

		# KPI calculation - environment
		'''
		The environment is related to the emissions both imported and domestic (average of both) and the amount of
		renewable energy production.
		self.S1_RES_supply should be at 1
		self.S3_RES_invest should be at 1
		self.S4_dome_em_t should be at 1
		self.S5_import_em_t should be at 1
		'''

		self.PC2_environment = 0.25 * self.S1_RES_supply + 0.25 * self.S3_RES_invest + 0.25 * self.S4_dome_em_t\
							   + 0.25 * self.S5_import_em_t

		# KPI storage
		'''Note that even if no DC are considered, a value needs to be placed in for the merging
		with the policy process model'''
		KPIs = [0, self.PC1_economy, self.PC2_environment,
				self.S1_RES_supply, self.S2_elec_prices, self.S3_RES_invest, self.S4_dome_em_t, self.S5_import_em_t]

		print(KPIs)

		return KPIs