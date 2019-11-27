from model_elec_agents import Investor

def init_agents(self):

	'''creation of the investor agents'''
	# Investor agent 1
	unique_id = 1
	agent = Investor(unique_id, self)
	self.investor_list.append(agent)

	# Investor agent 2
	unique_id = 2
	agent = Investor(unique_id, self)
	self.investor_list.append(agent)

	# Investor agent 3
	unique_id = 3
	agent = Investor(unique_id, self)
	self.investor_list.append(agent)

	# Investor agent 4
	unique_id = 4
	agent = Investor(unique_id, self)
	self.investor_list.append(agent)