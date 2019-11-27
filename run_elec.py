from model_elec import Electricity
import time
import matplotlib.pyplot as plt

'''
File used to run the electricity model
'''

year_simulated = 30 # [years] length of the simulation
check = False # bool - check activation (plotting some results every five years)
repetition_runs = 50
demand_growth = [0.00, 0.015, 0.03]

for demand_ite in range(len(demand_growth)):

	for rep_runs in range(repetition_runs):

		model_run_elec = Electricity(demand_growth[demand_ite], 10, 10) # model initialisation

		print("************************ \n Start of the simulation: \n ")
		print("Demand growth:", demand_growth[demand_ite], ", rep_run:", rep_runs)

		start = time.time() # recording time

		policy = [None, None, None, None, None] # [array] - initialising the policy array - needed for hybrid model

		for i in range(year_simulated): # iteration for the yearly duration of the simulation

			model_run_elec.step(policy) # one .step() is equal to one year of simulation

			# if i % (5) == 0 and i != 0 and check: # plotting some data every five years (used for checks)
			# 	dataPlot_Elec_model = model_run_elec.datacollector.get_model_vars_dataframe()
			# 	dataPlot_Elec_model.plot("step", ["electricity price"])
			# 	plt.show()

		end = time.time() # recording time

		print('Simulation run time:', end - start)
		print(' ')

		# collecting the data from the datacollector
		dataPlot_Elec_model = model_run_elec.datacollector.get_model_vars_dataframe()
		# dataPlot_Elec_agents = model_run_elec.datacollector.get_agent_vars_dataframe()

		# dataPlot_Elec_model.plot("step", ["electricity price"]) # plotting some data
		# plt.show()

		dataPlot_Elec_model.to_csv('O_E1_alone_model_' + str(demand_growth[demand_ite]) + '_Run' + str(rep_runs) + '.csv') # printing data to csv file

'''
Run times -
24.07.0219 - 0731: 17 years - 523.60 seconds [laptop]
24.07.2019 - 1114: 17 years - 428.80 seconds [laptop]
25.07.2019 - 1230: 17 years - 518.30 seconds [laptop]
06.08.2019 - 1243: 17 years - 292.96 seconds [laptop]
09.09.2019 - 1524: 17 years - 266.94 seconds [laptop]
09.09.2019 - 1549: 17 years - 213.17 seconds [laptop]
09.09.2019 - 1651: 17 years - 242.72 seconds [laptop]
11.09.2019 - 1532: 17 years - 274.04 seconds [laptop]
12.09.2019 - 1542: 17 years - 374.52 seconds [laptop]
13.09.2019 - 1630: 17 years - 429.13 seconds [laptop]
16.09.2019 - 1432: 17 years - 371.99 seconds [desktop]
16.09.2019 - 1853: 17 years - 395.78 seconds [desktop]
24.09.2019 - 1842: 17 years - 095.57 seconds [desktop]
25.09.2019 - 1350: 17 years - 128.18 seconds [laptop]
25.09.2019 - 1548: 17 years - 082.36 seconds [laptop]
26.09.2019 - 1639: 17 years - 483.57 seconds [laptop]
26.09.2019 - 1816: 17 years - 422.75 seconds [laptop]
'''