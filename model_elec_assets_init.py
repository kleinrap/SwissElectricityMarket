from mesa import Agent

from model_elec_assets import SolarAsset, WindAsset, CCGTAsset, NuclearAsset, HydroAsset,\
	HydroPumpingAsset, RunOfRiverAsset, WasteAsset, LTContract, NTCAsset, PlannedAsset

'''
Note that the simulation starts in 2015, so the cost values are valid for 2015 within this file

There are 8760 hours in a year - every time is provided in hours within this model
'''

def init_assets(self):

	# pre-defining the agents for asset assignment
	for agent in self.investor_list:
		if agent.unique_id == 1:
			agent1 = agent
		if agent.unique_id == 2:
			agent2 = agent
		if agent.unique_id == 3:
			agent3 = agent
		if agent.unique_id == 4:
			agent4 = agent
	# for agent in self.schedule.agent_buffer(shuffled=True):
	# 		if isinstance(agent, Agent):
	# 			if agent.unique_id == 1:
	# 				agent1 = agent
	# 			if agent.unique_id == 2:
	# 				agent2 = agent
	# 			if agent.unique_id == 3:
	# 				agent3 = agent
	# 			if agent.unique_id == 4:
	# 				agent4 = agent

	online = True

	'''
	Creation of the initial wind assets
	Arguments:

	Note:
	'''

	tech_type = 'Wind'
	IC = self.tech_input[tech_type]['IC'][self.scenario][0]
	t_life = 25 * 8760
	FC = self.tech_input[tech_type]['FC'][self.scenario][0]
	VC = 0
	UF = 0.309

	# Wind power plant 0
	unique_id = 30
	installed_capacity = 20
	owner = agent1
	age = 1*8760
	asset = WindAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)

	self.schedule.add(asset)

	# Wind power plant 1
	unique_id = 31
	installed_capacity = 20
	owner = agent2
	age = 2*8760
	asset = WindAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)
	self.schedule.add(asset)

	# Wind power plant 2
	unique_id = 32
	installed_capacity = 20
	owner = agent3
	age = 3*8760
	asset = WindAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)
	self.schedule.add(asset)

	'''creation of the initial solar assets'''

	# general inputs
	tech_type = 'Solar'
	IC = self.tech_input[tech_type]['IC'][self.scenario][0]
	t_life = 30 * 8760
	FC = self.tech_input[tech_type]['FC'][self.scenario][0]
	VC = 0
	UF = 0.135

	# Solar power plant 0
	unique_id = 40
	installed_capacity = 500
	owner = agent4
	age = 1*8760
	asset = SolarAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)
	self.schedule.add(asset)

	# Solar power plant 1
	unique_id = 41
	installed_capacity = 500
	owner = agent1
	age = 2*8760
	asset = SolarAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)
	self.schedule.add(asset)

	# Solar power plant 2
	unique_id = 42
	installed_capacity = 394
	owner = agent2
	age = 3*8760
	asset = SolarAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)
	self.schedule.add(asset)

	# Solar power plant 3 - in construction
	owner = agent3
	asset = PlannedAsset(owner, self, True, False, False, 0, False, False, 'Solar')
	self.planned_assets.append(asset)

	'''creation of the initial CCGT assets'''

	# general inputs
	tech_type = 'CCGT'
	IC = self.tech_input[tech_type]['IC'][self.scenario][0]
	t_life = 55 * 8760
	FC = self.tech_input[tech_type]['FC'][self.scenario][0]
	VC = self.tech_input[tech_type]['VC'][self.scenario][0]
	EC = 0
	UF = 0.8
	emissions = self.tech_params[tech_type]['emissions']

	# CCGT power plant 0
	unique_id = 50
	installed_capacity = 180
	owner = agent4
	age = 20*8760
	asset = CCGTAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online,
					  IC, FC, VC, UF, EC, emissions)
	self.schedule.add(asset)

	# CCGT power plant 1
	unique_id = 51
	installed_capacity = 180
	owner = agent1
	age = 21*8760
	asset = CCGTAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online,
					  IC, FC, VC, UF, EC, emissions)
	self.schedule.add(asset)

	# CCGT power plant 2
	unique_id = 52
	installed_capacity = 180
	owner = agent2
	age = 22*8760
	asset = CCGTAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online,
					  IC, FC, VC, UF, EC, emissions)
	self.schedule.add(asset)

	'''
	Creation of the initial nuclear assets
	Added arguments:
	maintenance - corresponds to the month of the year
	maintenance_length - provided in hours
	
	Note:
	no new nuclear plants will be constructed
	'''

	# general inputs
	tech_type = 'Nuclear'
	IC = self.tech_input[tech_type]['IC'][self.scenario][0]
	t_life = 50 * 8760
	FC = self.tech_input[tech_type]['FC'][self.scenario][0]
	VC = self.tech_input[tech_type]['VC'][self.scenario][0]
	UF = 0.87
	maint_length = 1095

	# Nuclear power plant 0 - Mühleberg (2019)
	unique_id = 60
	installed_capacity = 390
	maint_month = 6 # month number
	owner = agent3
	age = 46*8760
	asset = NuclearAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 		maint_month, maint_length)
	self.schedule.add(asset)

	# Nuclear power plant 1 - Gösgen (2039)
	unique_id = 61
	installed_capacity = 1035
	maint = 8 # month number
	owner = agent4
	age = 39*8760
	asset = NuclearAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 		maint, maint_length)
	self.schedule.add(asset)

	# Nuclear power plant 2 - Biznau (2029)
	unique_id = 62
	installed_capacity = 380
	maint = 5 # month number
	owner = agent1
	age = 49*8760
	asset = NuclearAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 		maint_month, maint_length)
	self.schedule.add(asset)

	# Nuclear power plant 3 - Biznau (2032)
	unique_id = 63
	installed_capacity = 380
	maint = 9 # month number
	owner = agent2
	age = 47*8760
	asset = NuclearAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 		maint_month, maint_length)
	self.schedule.add(asset)

	# Nuclear power plant 4 - Leibstadt (2044)
	unique_id = 64
	installed_capacity = 1245
	maint = 7 # month number
	owner = agent3
	age = 34*8760
	asset = NuclearAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 		maint_month, maint_length)
	self.schedule.add(asset)

	'''
	Creation of the initial hydro assets
	Added arguments:
	reservoir_level - level of water within the reserveoir
	reservoir_level_max - total capacity of the reservoir

	Note:
	There will be no new construction of hydro asset
	'''

	# general inputs
	tech_type = 'Hydro'
	IC = self.tech_input[tech_type]['IC'][self.scenario][0]
	t_life = 80 * 8760
	FC = self.tech_input[tech_type]['FC'][self.scenario][0]
	VC = self.tech_input[tech_type]['VC'][self.scenario][0]
	UF = False
	age = 0

	# Hydro power plant 0
	unique_id = 70
	installed_capacity = 3000
	reservoir_level = 1329603
	reservoir_level_max = 2110480
	owner = agent4
	asset = HydroAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 reservoir_level, reservoir_level_max)
	self.schedule.add(asset)

	# Hydro power plant 1
	unique_id = 71
	installed_capacity = 3000
	reservoir_level = 1329603
	reservoir_level_max = 2110480
	owner = agent1
	asset = HydroAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 reservoir_level, reservoir_level_max)
	self.schedule.add(asset)

	# Hydro power plant 2
	unique_id = 72
	installed_capacity = 2746
	reservoir_level = 1217030
	reservoir_level_max = 1931793
	owner = agent2
	asset = HydroAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 reservoir_level, reservoir_level_max)
	self.schedule.add(asset)


	'''
	Creation of the initial hydro pumping assets
	Added arguments:
	reservoir_level - water level of the reservoir
	reservoir_level_max - total capacity of the reservoir
	storage - boolean value

	Note:
	There will be no new construction of new hydro pumping assets
	'''

	# general inputs
	tech_type = 'Hydro'
	IC = self.tech_input[tech_type]['IC'][self.scenario][0]
	t_life = 80 * 8760
	FC = self.tech_input[tech_type]['FC'][self.scenario][0]
	VC = self.tech_input[tech_type]['VC'][self.scenario][0]
	reservoir_efficiency = 0.8
	UF = False
	age = 0

	tech_type = 'Hydrop'

	# Hydro pumping power plant 0
	unique_id = 80
	installed_capacity = 1000
	reservoir_level = 443201
	reservoir_level_max = 703493
	owner = agent3
	asset = HydroPumpingAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 reservoir_level, reservoir_level_max, reservoir_efficiency)
	self.schedule.add(asset)

	# Hydro pumping power plant 1
	unique_id = 81
	installed_capacity = 1000
	reservoir_level = 443201
	reservoir_level_max = 703493
	owner = agent4
	asset = HydroPumpingAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 reservoir_level, reservoir_level_max, reservoir_efficiency)
	self.schedule.add(asset)

	# Hydro pumping power plant 2
	unique_id = 82
	installed_capacity = 1763
	reservoir_level = 781363
	reservoir_level_max = 1240259
	owner = agent1
	asset = HydroPumpingAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 reservoir_level, reservoir_level_max, reservoir_efficiency)
	self.schedule.add(asset)


	'''
	Creation of the initial run of river assets
	Added arguments:

	Note:
	There will be no new construction of run of river asset
	'''

	# general inputs
	tech_type = 'RunOfRiver'
	IC = self.tech_input[tech_type]['IC'][self.scenario][0]
	t_life = 80 * 8760
	FC = self.tech_input[tech_type]['FC'][self.scenario][0]
	VC = self.tech_input[tech_type]['VC'][self.scenario][0]
	UF = False
	age = 0

	# Run of river power plant 0
	unique_id = 90
	installed_capacity = 2000
	owner = agent2
	asset = RunOfRiverAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)
	self.schedule.add(asset)

	# Run of river power plant 1
	unique_id = 91
	installed_capacity = 1000
	age = 0
	owner = agent3
	asset = RunOfRiverAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)
	self.schedule.add(asset)

	# Run of river power plant 2
	unique_id = 92
	installed_capacity = 1633
	owner = agent4
	asset = RunOfRiverAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)
	self.schedule.add(asset)


	'''
	Creation of the initial waste assets
	Added arguments:

	Note:
	'''

	# general inputs
	tech_type = 'Waste'
	IC = False
	t_life = 80 * 8760
	FC = self.tech_input[tech_type]['FC'][self.scenario][0]
	VC = self.tech_input[tech_type]['VC'][self.scenario][0]
	UF = False
	age = 0

	# Waste power plant 0
	unique_id = 100
	installed_capacity = 200
	reservoir_level = 67200
	reservoir_level_max = 134400
	owner = agent1
	asset = WasteAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 reservoir_level, reservoir_level_max)
	self.schedule.add(asset)

	# Waste power plant 1
	unique_id = 101
	installed_capacity = 100
	reservoir_level = 33600
	reservoir_level_max = 67200
	owner = agent2
	asset = WasteAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 reservoir_level, reservoir_level_max)
	self.schedule.add(asset)

	# Waste power plant 2
	unique_id = 102
	installed_capacity = 64
	reservoir_level = 21504
	reservoir_level_max = 43008
	owner = agent3
	asset = WasteAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 reservoir_level, reservoir_level_max)
	self.schedule.add(asset)


	'''
	Creation of the initial LTC contracts
	Added arguments:
	
	Note:
	'''

	# general inputs
	tech_type = 'LTC'
	t_life = 50 * 8760
	FC = 0
	VC = 35
	owner = None

	# Long term contract 0
	unique_id = 110
	country = 'FR'
	installed_capacity = 768
	age = 48*8760
	asset = LTContract(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, FC, VC, country)
	self.schedule.add(asset)

	# Long term contract 1
	unique_id = 111
	country = 'FR'
	installed_capacity = 256
	age = 43*8760
	asset = LTContract(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, FC, VC, country)
	self.schedule.add(asset)

	# Long term contract 2
	unique_id = 112
	country = 'FR'
	installed_capacity = 257
	age = 38*8760
	asset = LTContract(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, FC, VC, country)
	self.schedule.add(asset)

	# Long term contract 3
	unique_id = 113
	country = 'FR'
	installed_capacity = 767
	age = 33*8760
	asset = LTContract(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, FC, VC, country)
	self.schedule.add(asset)

	# Long term contract 4
	unique_id = 114
	country = 'FR'
	installed_capacity = 640
	age = 28*8760
	asset = LTContract(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, FC, VC, country)
	self.schedule.add(asset)


	'''
	Creation of the NTC assets
	Added arguments:

	Note:
	
	'''

	# general inputs
	tech_type = 'NTC'
	owner = None
	t_life = 100 * 8760
	age = 0
	installed_capacity = []

	# NTC - France
	unique_id = 120
	country = 'FR'
	asset = NTCAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, country)
	self.schedule.add(asset)

	# NTC - Germany
	unique_id = 121
	country = 'DE'
	asset = NTCAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, country)
	self.schedule.add(asset)

	# NTC - Italy
	unique_id = 122
	country = 'IT'
	asset = NTCAsset(unique_id, self, owner, tech_type, installed_capacity, t_life, age, online, country)
	self.schedule.add(asset)