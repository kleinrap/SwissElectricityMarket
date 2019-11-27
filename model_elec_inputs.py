import pickle

def inputs_import(self):


    '''
    Solar inputs
    '''
    # loading the solar from input data
    # each cell represents the number of hours
    print('Loading the solar input data')
    with open('input_solar_conditions.pkl', 'rb') as f:
        self.solar_conditions = pickle.load(f)

    '''
    Wing inputs
    '''
    # loading the wind from input data
    print('Loading the wind input data')
    with open('input_wind_conditions.pkl', 'rb') as f:
        self.wind_conditions = pickle.load(f)

    '''
    Run of river inputs
    '''
    # loading the run of river from input data
    print('Loading the run of river input data')
    with open('input_ror.pkl', 'rb') as f:
        self.ror_conditions = pickle.load(f)

    '''
    Foreign related inputs
    '''
    # loading the foreign electricity prices from input data
    print('Loading the foreign electricity prices')
    with open('input_price_foreign.pkl', 'rb') as f:
        price_foreign = pickle.load(f)
    self.price_FR = price_foreign[0] # list - [CHF] - prices for France
    self.price_DE = price_foreign[1] # list - [CHF] - prices for Germany
    self.price_IT = price_foreign[2] # list - [CHF] - prices for Italy
    self.price_foreign = [self.price_FR, self.price_DE, self.price_IT]

    # loading the french border capacity of river from input data
    print('Loading the foreign border capacity')
    with open('input_capacity_foreign.pkl', 'rb') as f:
        capacity_foreign = pickle.load(f)
    self.capacity_ex = capacity_foreign[0] # exports
    self.capacity_im = capacity_foreign[1] # imports

    '''
    Waste inputs
    '''
    # loading the inflow of waste for the entire Switzerland
    print('Loading the yearly waste inflow')
    self.waste_inflow = [233000 for f in range((2050 - self.start_year) * 8760)]

    '''
    Hydro and hydrop inputs
    '''
    # loading the yearly water inflow
    # this is the natural inflow over all reservoirs (VSE scenario based)
    print('Loading the yearly water inflow scenarios')
    self.water_inflow_year = []
    # period 2015-2020 (18733000 - 18767000)
    for i in range((2020 - self.start_year) * 8760):
        water_inflow1 = (34 / 5 * (2015 + i / 8760) + 5031) * 1000
        self.water_inflow_year.append(water_inflow1)
    # period 2020-2025 (18767 - 18767)
    for i in range((2025 - 2020) * 8760):
        water_inflow2 = 18767000
        self.water_inflow_year.append(water_inflow2)
    # period 2025-2035 (18767000 - 18833000)
    for i in range((2035 - 2025) * 8760):
        water_inflow3 = (33 / 5 * (2025 + i / 8760) + 5402) * 1000
        self.water_inflow_year.append(water_inflow3)
    # period 2035-2050 (18933000 - 18933000)
    for i in range((2050 - 2035) * 8760):
        water_inflow4 = 18933000
        self.water_inflow_year.append(water_inflow4)

    # loading the inflow of water from input data (this is the hourly distribution)
    print('Loading the hourly water inflow input data')
    with open('input_hydro_conditions.pkl', 'rb') as f:
        self.inflow_conditions = pickle.load(f)

    '''
    CCGT inputs
    '''
    # loading the emissions prices for carbon ton
    print('Loading the carbon prices')
    self.emission_price = []
    self.emission_factor = 0.342834  # TC/MWh (NREL, 2018)
    # period 2017-2020 (9 CHF/ton)
    for i in range((2020 - self.start_year)):
        emission_period1 = 9 * self.emission_factor
        self.emission_price.append(emission_period1)
    # period 2020-2025 (15 CHF/ton)
    for i in range((2025 - 2020)):
        emission_period2 = 15 * self.emission_factor
        self.emission_price.append(emission_period2)
    # period 2025-2030 (22 CHF/ton)
    for i in range((2030 - 2025)):
        emission_period3 = 22 * self.emission_factor
        self.emission_price.append(emission_period3)
    # period 2030-2035 (33 CHF/ton)
    for i in range((2035 - 2030)):
        emission_period4 = 33 * self.emission_factor
        self.emission_price.append(emission_period4)
    # period 2035-2050 (42 CHF/ton)
    for i in range((2050 - 2035)):
        emission_period5 = 42 * self.emission_factor
        self.emission_price.append(emission_period5)
    # period 2050-2100 (73 CHF/ton)
    for i in range((2100 - 2050)):
        emission_period6 = 73 * self.emission_factor
        self.emission_price.append(emission_period6)

    # loading the energy mix scenario per country
    # built from a number of sources cited in the documentation
    self.mix_FR_coal = []
    self.mix_FR_CCGT = []
    self.mix_DE_coal = []
    self.mix_DE_CCGT = []
    self.mix_IT_coal = []
    self.mix_IT_CCGT = []
    # period start_year-2020
    for i in range((2020 - self.start_year)):
        self.mix_FR_coal.append(0.00)
        self.mix_FR_CCGT.append(0.03)
        self.mix_DE_coal.append(0.45)
        self.mix_DE_CCGT.append(0.15)
        self.mix_IT_coal.append(0.16)
        self.mix_IT_CCGT.append(0.44)
    # period 2020-2025
    for i in range((2025 - 2020)):
        self.mix_FR_coal.append(0.00)
        self.mix_FR_CCGT.append(0.03)
        self.mix_DE_coal.append(0.20)
        self.mix_DE_CCGT.append(0.17)
        self.mix_IT_coal.append(0.14)
        self.mix_IT_CCGT.append(0.40)
    # period 2025-2030
    for i in range((2030 - 2025)):
        self.mix_FR_coal.append(0.00)
        self.mix_FR_CCGT.append(0.03)
        self.mix_DE_coal.append(0.19)
        self.mix_DE_CCGT.append(0.17)
        self.mix_IT_coal.append(0.12)
        self.mix_IT_CCGT.append(0.36)
    # period 2030-2035
    for i in range((2035 - 2030)):
        self.mix_FR_coal.append(0.00)
        self.mix_FR_CCGT.append(0.03)
        self.mix_DE_coal.append(0.12)
        self.mix_DE_CCGT.append(0.17)
        self.mix_IT_coal.append(0.10)
        self.mix_IT_CCGT.append(0.34)
    # period 2035-2040
    for i in range((2040 - 2035)):
        self.mix_FR_coal.append(0.00)
        self.mix_FR_CCGT.append(0.03)
        self.mix_DE_coal.append(0.05)
        self.mix_DE_CCGT.append(0.09)
        self.mix_IT_coal.append(0.08)
        self.mix_IT_CCGT.append(0.32)
    # period 2040-2100
    for i in range((2100 - 2040)):
        self.mix_FR_coal.append(0.00)
        self.mix_FR_CCGT.append(0.03)
        self.mix_DE_coal.append(0.00)
        self.mix_DE_CCGT.append(0.12)
        self.mix_IT_coal.append(0.06)
        self.mix_IT_CCGT.append(0.30)

    '''
    Load inputs
    '''
    # loading the load curve from input data
    print('Loading the load curve')
    with open('input_load_input.pkl', 'rb') as f:
        load_input = pickle.load(f)
    self.load = load_input[0]
    self.load_factor = load_input[1]

    '''
    Technology inputs
    '''
    # loading the load curve from input data
    print('Loading the technology parameter curves')
    with open('input_techs.pkl', 'rb') as f:
        self.tech_input = pickle.load(f)