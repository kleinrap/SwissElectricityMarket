class Asset:
    """ Base class for a model agent. """
    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online):
        '''
        _init_ a new asset - Copied from the Agent class from mesa and expanded

        :param unique_id: int - ID of the asset
        :param model: object - electricity model reference
        :param owner: object - owner
        :param tech_type: string - name of the technology
        :param installed_capacity: int - installed capacity
        :param t_life: int - maximum lifetime
        :param age: int - age
        :param online: bool - status of the asset
        '''

        self.unique_id = unique_id                      # [-]
        self.model = model                              # [-]
        self.owner = owner                              # [-]
        self.tech_type = tech_type                      # [-]
        self.installed_capacity = installed_capacity    # [MWh]
        self.t_life = t_life                            # [hours]
        self.online = online                            # [-]
        self.age = age                                  # [hours]

        self.elec_supplied_year = 0     # float - [MW/year] - electricity supplied in the last year
        self.elec_revenue_year = 0      # float - [CHF] - revenue per year
        self.mothballed = False         # bool - mothballing of power plants
        self.maint = False              # bool - maintenance parameter for random outages

    def step(self):
        """ A single step of the agent. """
        pass

    @property
    def random(self):
        return self.model.random

class AsssetWCost(Asset):
    """ Agent class that include costs. This means all assets except for LTC and NTC assets """
    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF):
        '''
        _init_ a new asset with costs

        :param unique_id: int - ID of the asset
        :param model: object - electricity model reference
        :param owner: object - owner
        :param tech_type: string - name of the technology
        :param installed_capacity: int - installed capacity
        :param t_life: int - maximum lifetime
        :param age: int - age
        :param online: bool - status of the asset
        :param IC: float - investment costs
        :param FC: float - fixed costs
        :param VC: float - variable costs
        :param UF: float - utilisation factor
        '''

        super().__init__(unique_id, model, owner, tech_type, installed_capacity, t_life, age, online)
        self.IC = IC  # [CHF/kW]
        self.FC = FC  # [CHF/kW/year]
        self.VC = VC  # [CHF/MWh]
        self.UF = UF  # [%]

    def step(self):
        """ A single step of the agent. """
        pass

    @property
    def random(self):
        return self.model.random

'''
Structure of the assets

class SolarAsset(Asset):
    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF):

class WindAsset(Asset):
    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF):

class HydroAsset(Asset):
    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
    reservoir_level, reservoir_level_max):

class HydroPumpingAsset(Asset):
    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
    reservoir_level, reservoir_level_max, reservoir_efficiency, storage):

class RunOfRiverAsset(Asset):
    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF):

class WasteAsset(Asset):
    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
    reservoir_level, reservoir_level_max):

class CCGTAsset(Asset):
    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF, EC,
    emissions):

class NuclearAsset(Asset):
    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, IC, FC, VC, UF,
    maintenance, maintenance_length):

class LTContract(Asset):
    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, FC, VC, country):

class NTCAsset(Asset):
    def __init__(self, unique_id, model, owner, tech_type, installed_capacity, t_life, age, online, country):
'''