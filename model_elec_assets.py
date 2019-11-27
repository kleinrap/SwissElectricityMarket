from asset import Asset, AsssetWCost

def calculation_opportunity_cost(self, price_reference):
    '''
    This function is used to estimate the opportunity cost for the technology types that can store their energy in a
    reservoir. This includes the hydro pumping and the waste assets.
    The function returns the marginal costs.
    The opportunity cost calculation is different depending on whether the level of the reservoir is higher than the
    installed capacity or not.
    '''

    # todo - OC does not take into account the lowest alternative right now, it only takes into account the reference price

    if self.installed_capacity > self.reservoir_level: # if capacity higher than water level
        opportunity_cost = (price_reference - self.VC) * (1 - (self.reservoir_level/(2*self.reservoir_level_max)))
    else: # if capacity lower than water level
        opportunity_cost = (price_reference - self.VC) *\
                           (1 - ((self.reservoir_level - self.installed_capacity)/self.reservoir_level_max))
    marginal_cost = opportunity_cost + self.VC

    return marginal_cost

class PlannedAsset():
    '''
    This object is a vessel for a planned asset.
    It is not actually added to the schedule but only contained within the owners planned plants
    '''

    def __init__(self, owner, model, approval, approved, construction, approval_since, approved_since,
                 construction_since, tech_type):
        '''
        Create a planned asset
        '''
        self.model = model
        self.approval = approval                    # [bool] - True: in the approval process, False:
        self.approved = approved                    # [bool] - True: approved
        self.construction = construction            # [bool] - True: in construction
                                                    # approval, approved and construction can only have one True for three
        self.approval_since = approval_since        # [bool/int] - time since the plant has been submitted for approval
        self.approved_since = approved_since        # [bool/int] - time since it has been approved
        self.construction_since = construction_since# [bool/int] - time since construction has started
        self.owner = owner                          # [investor object] - investor owning the plant
        self.tech_type = tech_type                  # [string] - technology type

class SolarAsset(AsssetWCost):

    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF):
        '''
        Create a new solar power plant
        '''
        super().__init__(unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)
        self.renovated = 0

    def calculation_cost(self):
        '''
        Calculation of the marginal costs for the solar power plant
        '''

        return self.VC

    def calculation_supply(self, solar_conditions):
        '''
        Calculation of the supply for the solar power plant
        installed_capacity: [MW]
        solar_conditions: [MW_output/ MW_installed]
        Note: This is calculated over a certain duration
        solar_UF_potential represents the diminishing factor. It considers the fact that new solar will not be placed
        in prime locations.
        '''

        return self.installed_capacity * solar_conditions

class WindAsset(AsssetWCost):

    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF):
        '''
         Create a new wind power plant.
        '''
        super().__init__(unique_id, model, owner, tech_type, installed_capacity, t_life, online, age, IC, FC, VC, UF)
        self.renovated = 0

    def calculation_cost(self):
        '''
        Calculation of the marginal costs for the wind power plant
        costs_variable: [CHF/MWhr]
        '''

        return self.VC

    def calculation_supply(self, wind_conditions):
        '''
        Calculation of the supply for the wind power plant
        installed_capacity: [MW]
        wind_conditions: [MW_output/ MW_installed]
        Note: This is calculated over a certain duration
        wind_UF_potential represents the diminishing factor. It considers the fact that new wind will not be placed
        in prime locations.
        '''

        return self.installed_capacity * wind_conditions

class HydroAsset(AsssetWCost):
    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 reservoir_level, reservoir_level_max):
        '''
         Create a new hydro power plant.
        '''
        super().__init__(unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)
        self.reservoir_level = reservoir_level          # [MW/hr] - current level of the reservoir
        self.reservoir_level_max = reservoir_level_max  # [MW/hr] - total capacity of the reservoir

    def calculation_cost(self, price_reference):
        '''
        Calculation of the marginal costs for the hydro power plant
        These are the opportunity costs
        '''

        return calculation_opportunity_cost(self, price_reference)

    def calculation_supply(self):
        '''
        Calculation of the supply for the hydro power plant
        '''

        # the supply available is whatever water there is in the reservoir or the installed capacity, whichever is higher
        if self.reservoir_level >= self.installed_capacity:
            return self.installed_capacity
        else:
            return self.reservoir_level

    def reservoir_step_update(self, water_inflow_yearly, water_inflow_hourly, reservoir_level_max_all):
        '''
        Function that updates the reservoir height at the beginning of every step
        This relates to the inflow into the reservoir
        '''

        # calculate the inflow
        # includes the inflow from VSE which is for all reservoirs, so here it is taken down to the level of this reservoir
        # below is given per year
        index_input_yearly = self.model.hourCount%len(water_inflow_yearly) # this is the growth
        index_input_hourly = self.model.hourCount%len(water_inflow_hourly) # this is the actual water
        # inflow given per hour
        inflow = water_inflow_yearly[index_input_yearly] * water_inflow_hourly[index_input_hourly]

        self.reservoir_level += inflow * self.reservoir_level_max / reservoir_level_max_all

        # overflow check - outflow
        if self.reservoir_level > self.reservoir_level_max:
            self.reservoir_level = self.reservoir_level_max

class HydroPumpingAsset(AsssetWCost):

    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 reservoir_level, reservoir_level_max, reservoir_efficiency):
        '''
         Create a new hydro pumping power plant.
        '''
        super().__init__(unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)
        self.reservoir_level = reservoir_level          # [MW/hr] - current level of the reservoir
        self.reservoir_level_max = reservoir_level_max  # [MW/hr] - total capacity of the reservoir
        self.reservoir_efficiency = reservoir_efficiency# [-] - efficiency of the reservoir

    def calculation_cost(self, price_reference):
        '''
        Calculation of the marginal costs for the hydro pumping power plant
        These are the opportunity costs
        '''

        return calculation_opportunity_cost(self, price_reference)

    def calculation_supply(self):
        '''
        Calculation of the supply for the hydro power pumping plant
        '''

        # the supply available is whatever water there is in the reservoir or the installed capacity, whichever is higher
        if self.reservoir_level >= self.installed_capacity:
            return self.installed_capacity
        else:
            return self.reservoir_level

    def calculation_cost_demand(self, price_reference):

        storage_efficiency = 0.9

        return calculation_opportunity_cost(self, price_reference)/storage_efficiency

    def reservoir_step_update(self, water_inflow_yearly, water_inflow_hourly, reservoir_level_max_all):
        '''
        Function that updates the reservoir height at the beginning of every step
        '''

        # calculate the inflow
        # includes the inflow from VSE which is for all reservoirs, so here it is taken down to the level of this reservoir
        # below is given per year
        index_input_yearly = self.model.hourCount%len(water_inflow_yearly) # this is the growth
        index_input_hourly = self.model.hourCount%len(water_inflow_hourly) # this is the actual water
        # inflow given per hour
        inflow = water_inflow_yearly[index_input_yearly] * water_inflow_hourly[index_input_hourly]

        self.reservoir_level += inflow * self.reservoir_level_max / reservoir_level_max_all

        # overflow check - outflow
        if self.reservoir_level > self.reservoir_level_max:
            self.reservoir_level = self.reservoir_level_max

class RunOfRiverAsset(AsssetWCost):

    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF):
        '''
         Create a new hydro pumping power plant.
        '''
        super().__init__(unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)

    def calculation_cost(self):
        '''
        Calculation of the marginal costs for the run of river power plant
        costs_variable: [CHF/MWhr]
        '''

        return self.VC

    def calculation_supply(self, ror_conditions, duration):
        '''
        Calculation of the supply for the run of river power plant
        supply_available: [MWh]
        installed_capacity: [MW]
        ror_conditions: [MW_output/ MW_installed]
        '''

        index_input = self.model.hourCount%len(ror_conditions) # index selection
        supply_available = (self.installed_capacity * ror_conditions[index_input]) * duration

        return supply_available

class WasteAsset(AsssetWCost):

    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 reservoir_level, reservoir_level_max):
        '''
         Create a new hydro pumping power plant.
        '''
        super().__init__(unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)
        self.reservoir_level = reservoir_level          # [MW/hr] - current level of the reservoir
        self.reservoir_level_max = reservoir_level_max  # [MW/hr] - total capacity of the reservoir

    def calculation_cost(self, price_reference):
        '''
        Calculation of the marginal costs for the waste power plant
        '''

        marginal_cost = calculation_opportunity_cost(self, price_reference)

        return marginal_cost + self.FuC

    def calculation_supply(self):
        '''
        Calculation of the supply for the waste power plant
        '''

        # the supply available is whatever water there is in the reservoir or the installed capacity, whichever is higher
        if self.reservoir_level >= self.installed_capacity:
            # print('Waste reservoir level:', self.reservoir_level)
            return self.installed_capacity
        else:
            # print('Waste reservoir level:', self.reservoir_level)
            return self.reservoir_level

    def reservoir_step_update(self, waste_inflow_hourly, reservoir_capacity_total_waste):
        '''
        Function that updates the reservoir height at the beginning of every step
        '''

        # calculate the inflow
        # below is given per hour
        index_input = self.model.hourCount%len(waste_inflow_hourly)
        # inflow given per hour - assuming a yearly constant inflow
        inflow =  waste_inflow_hourly[index_input] / 8760

        # update the reservoir size
        self.reservoir_level += inflow * self.reservoir_level_max / reservoir_capacity_total_waste

        # overflow check - outflow
        if self.reservoir_level > self.reservoir_level_max:
            self.reservoir_level = self.reservoir_level_max

class CCGTAsset(AsssetWCost):

    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online,
                 IC, FC, VC, UF, EC, emissions):
        '''
         Create a new CCGT power plant.
        '''
        super().__init__(unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)
        self.EC = EC                                    # [CHF/ton] - emissions costs
        self.UF = UF                                    # [-] - utilisation factor
        self.emissions = emissions                      # [ton CO2/hr] - amount of emissions

        self.renovated = 0

    def calculation_cost(self):
        '''
        Calculation of the marginal costs for the CCGT power plant
        '''

        return self.FuC + self.EC + self.VC

    def calculation_supply(self):
        '''
        Calculation of the supply for the CCGT power plant
        '''

        return self.installed_capacity
    
class NuclearAsset(AsssetWCost):

    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
                 maint_month, maint_length):
        '''
         Create a new nuclear power plant.
        '''
        super().__init__(unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF)
        self.maint_month = maint_month                  # [month] - month when the plant is maintained yearly
        self.maint_length = maint_length                # [hr] - during of the maintenance

        self.maint_yearly = False                       # Boolean determining whether in or out of yearly maintenance
        self.renovated = 0                              # renovation counter

    def calculation_cost(self):
        '''
        Calculation of the marginal costs for the nuclear power plant
        '''

        return self.FuC + self.VC

    def calculation_supply(self):
        '''
        Calculation of the supply for the nuclear power plant
        '''

        return self.installed_capacity
    
class LTContract(Asset):

    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, FC, VC, country):
        '''
         Create a new nuclear power plant.
        '''
        super().__init__(unique_id, model, owner, tech_type, installed_capacity, t_life, age, online)
        self.FC = FC # float - [CHF/MWh] - fuel costs
        self.VC = VC # float - [CHF/MWh] - variable costs
        self.country = country # string - [-] - IT or FR or DE

    def calculation_cost(self):
        '''
        Calculation of the marginal costs for the long term contracts
        '''

        return self.VC

    def calculation_supply(self):
        '''
        Calculation of the supply for the LT contracts
        '''

        return self.installed_capacity

class NTCAsset(Asset):

    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, country):
        '''
         Create a new nuclear power plant.
        '''
        super().__init__(unique_id, model, owner, tech_type, installed_capacity, t_life, age, online)
        self.country = country                          # [country] - country with whom the contract is tendered

        self.C = 0
        self.installed_capacity_ex = 0
        self.installed_capacity_im = 0

    def calculation_cost(self):
        '''
        Calculation of the marginal costs for the NTC connections
        The supply from the NTC is provided as the border capacity in the grid.
        The price of the supply is given by the foreign spot price.
        Note: They are obtained directly from inputs
        '''

        return self.C

    def calculation_supply(self):
        '''
        Calculation of the supply for the NTC connections
        The supply from the NTC is provided as the border capacity in the grid.
        The price of the supply is given by the foreign spot price.
        Note: They are obtained directly from inputs
        '''

        # installed capacity list is used to calculate UF
        self.installed_capacity.append(self.installed_capacity_im)
        
        return self.installed_capacity_im
 
    def calculation_demand(self):

        '''
        Calculation of the demand for the NTC connections (imports) 

        Note: They are obtained directly from inputs
        '''
        
        return self.installed_capacity_ex