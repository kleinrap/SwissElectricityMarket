from mesa import Agent
from model_elec_assets import PlannedAsset
import random


class Investor(Agent):
    '''
    The investors are the agents that own the assets and are able to invest in new assets
    '''

    def __init__(self, unique_id, model):

        super().__init__(unique_id, model)

        self.construct_count = 0
        self.planned_assets = {'Solar': 0, 'Wind': 0, 'CCGT': 0}

    def invest_new_tech(self, model):
        '''
        This function is used to assess whether the investor should invest in a specific technology.
        If it is confirmed, then the asset will be placed into the planning stage
        The algorithm:
        - Go through each technology with dummy plants (solar, wind and CCGT)
        - Go through the NPV()
        - Calculate profitability index (PI)
        - Check if PI is higher than the hurdle rate for that technology
        - Decide on whether to invest and if so in which asset
        :param model:
        :return:
        '''

        tech_types = ['Solar', 'Wind', 'CCGT']

        invest_potential = [0, 0, 0] # [solar, wind and CCGT]
        for i in range(len(tech_types)): # recording investment potentials for all technologies
            tech_type = tech_types[i]
            NPV, profitability_index = self.calculation_NPV(model, tech_type)
            if profitability_index > self.model.hurdle_rate:
                invest_potential[i] = profitability_index

        # limiting the number of planned assets possible
        if self.planned_assets['Solar'] > 10:
            invest_potential[0] = -10
        if self.planned_assets['Wind'] > 10:
            invest_potential[1] = -10
        if self.planned_assets['CCGT'] > 5:
            invest_potential[2] = -10

        invest_bool = False # initialisation of boolean
        for i in range(len(invest_potential)): # checking for possibility of investment
            if invest_potential[i] > 0:
                invest_bool = True
        if invest_bool == True: # investment possible
            invest_potential_max_index = invest_potential.index(max(invest_potential)) # checking highest potential
            if invest_potential_max_index == 0:
                tech_type_invest = 'Solar'
            if invest_potential_max_index == 1:
                tech_type_invest = 'Wind'
            if invest_potential_max_index == 2:
                tech_type_invest = 'CCGT'
            self.planned_assets[tech_type_invest] += 1 # updating planned asset count
            asset = PlannedAsset(self, model, True, False, False, 0, False, False, tech_type_invest)
            model.planned_assets.append(asset) # create the planned asset

    def calculation_profitability(self, years, model, asset):
        '''
        Calculation of the profitability for a plant for a given number of years.
        :param years: years for which the profitability is calculated
        :param model:
        :param asset:
        :return:
        '''

        tech_type = asset.tech_type
        VC = asset.VC
        UF = model.tech_params[tech_type]['UF']
        capacity = asset.installed_capacity
        FC = asset.FC

        price_trend_slope, price_trend_constant = self.calculation_prices(model, tech_type)
        year_time = model.start_year + model.hourCount/8760
        yearly_avoidable_cost = capacity * FC

        profitability = 0
        profits = 0
        losses = 0
        # calculate for five years - run to five
        for p in range(years):
            profits += (((year_time + (p + 1) * 8760) * price_trend_slope + price_trend_constant) - VC) /\
                       (1 + model.discount_rate) ** (p + 1)
            losses += (1 + 1 / (1 + model.discount_rate) ** (p + 1))

        profitability += profits * 8760 * UF * capacity
        profitability -= yearly_avoidable_cost * losses

        return profitability

    def calculation_prices(self, model, tech_type):
        '''
        Calculation of the price trend slope and the price trend constant
        :param model:
        :return:
        '''

        price_avg = [0, 0, 0, 0] # init. of the list
        price_avg[0] = model.elec_price_yearly[tech_type]['m0']
        price_avg[1] = model.elec_price_yearly[tech_type]['m1']
        price_avg[2] = model.elec_price_yearly[tech_type]['m2']
        price_avg[3] = model.elec_price_yearly[tech_type]['m3']
        price_trend_slope = (- 1.5 * (price_avg[3] - ((price_avg[0] + price_avg[1] + price_avg[2] + price_avg[3]) / 4))
                             - 0.5 * (price_avg[2] - ((price_avg[0] + price_avg[1] + price_avg[2] + price_avg[3]) / 4))
                             + 0.5 * (price_avg[1] - ((price_avg[0] + price_avg[1] + price_avg[2] + price_avg[3]) / 4))
                             + 1.5 * (price_avg[0] - ((price_avg[0] + price_avg[1] + price_avg[2] + price_avg[3]) / 4)))\
                            / model.start_year
        price_trend_constant = ((price_avg[0] + price_avg[1] + price_avg[2] + price_avg[3]) / 4) - \
                               ((model.start_year + model.hourCount / 8760) - 2.5) * price_trend_slope

        return price_trend_slope, price_trend_constant

    def calculation_NPV(self, model, tech_type):
        '''
        Calculation of the NPV
        This is based on the work from Paul van Baal, his paper and documentation
        :param model:
        :param tech_type:
        :return:
        '''

        subsidy = 0 # initialisation of the subsidies

        size_plant = model.tech_params[tech_type]['size']
        IC = model.tech_params[tech_type]['IC']
        FC = model.tech_params[tech_type]['FC']
        VC = model.tech_params[tech_type]['VC']

        # include the fuel and carbon price
        if tech_type == 'CCGT':
            VC += model.tech_params[tech_type]['FuC'] + model.tech_params[tech_type]['EC']

        # including subsidies for solar and wind
        if tech_type == 'Solar':
            subsidy = model.pins['SS']
        if tech_type == 'Wind':
            subsidy = model.pins['WTS']

        UF = model.tech_params[tech_type]['UF']
        wacc = model.discount_rate + model.risk_rate

        price_trend_slope, price_trend_constant = self.calculation_prices(model, tech_type)
        price_1 = price_trend_slope * ((model.start_year + model.hourCount / 8760) + 1) + price_trend_constant
        price_2 = price_trend_slope * ((model.start_year + model.hourCount / 8760) + 2) + price_trend_constant
        price_3 = price_trend_slope * ((model.start_year + model.hourCount / 8760) + 3) + price_trend_constant
        price_4 = price_trend_slope * ((model.start_year + model.hourCount / 8760) + 4) + price_trend_constant
        price_5 = price_trend_slope * ((model.start_year + model.hourCount / 8760) + 5) + price_trend_constant

        present_value_1 = (8760 * (price_1 - VC + subsidy) * UF - FC) / (1 + wacc)**1
        present_value_2 = (8760 * (price_2 - VC + subsidy) * UF - FC) / (1 + wacc)**2
        present_value_3 = (8760 * (price_3 - VC + subsidy) * UF - FC) / (1 + wacc)**3
        present_value_4 = (8760 * (price_4 - VC + subsidy) * UF - FC) / (1 + wacc)**4

        NPV_5 = - IC + present_value_1 + present_value_2 + present_value_3 + present_value_4
        NPV_10 = (8760 * (price_5 - VC + subsidy) * UF - FC)\
                  * (1/(1+wacc)**5 + 1/(1+wacc)**6 + 1/(1+wacc)**7 + 1/(1+wacc)**8 + 1/(1+wacc)**9 + 1/(1+wacc)**10)
        NPV_15 = (8760 * (price_5 - VC + subsidy)
                  * (1/(1+wacc)**11 + 1/(1+wacc)**12 + 1/(1+wacc)**13 + 1/(1+wacc)**14 + 1/(1+wacc)**15))
        NPV_20 = (8760 * (price_5 - VC + subsidy)
                  * (1/(1+wacc)**16 + 1/(1+wacc)**17 + 1/(1+wacc)**18 + 1/(1+wacc)**19 + 1/(1+wacc)**20))
        NPV = size_plant * (NPV_5 + NPV_10 + NPV_15 + NPV_20) # NPV calculation
        profitability_index = NPV / (size_plant * IC) # profitability calculation

        return NPV, profitability_index

'''
Below are notes from Paul about the NPV calculation (from Excel and Vensim)

The NPV is calculated for each of the assets owned by the investor
The NPV is used to establish what to do with a current plant or whether to build a future plant

All of the equations below have been obtained from Paul's excel or his thesis

discount rate: 0.08

risk rate: 0.01

WACC: discount rate + risk rate

utilization factor:
if(type="gas")
{plants_owned_type_on.Average utilization factor*
(plants_all.Sum derated capacity 3/
(plants_all.Sum derated capacity 3+investment size*plants_owned_type_on.Average utilization factor))}
else {plants_owned_type_on.Average utilization factor}

solar utilization factor lookup:
0,1,0,1,0,0.147,0.0367,0.1358,0.9306,0.114155,1,0.100114

wind utilization factor lookup:
0,1,0,1,0,0.3196,0.181,0.2497,0.195,0.2457,0.267,0.2301,1,0.1608

NPV5: -cost investment [$/MW]
+(time.hours per year * (price 1-cost marginal) * utilization factor - cost operating fixed) / (1 + WACC) ^ 1
+(time.hours per year * (price 2-cost marginal) * utilization factor - cost operating fixed) / (1 + WACC) ^ 2
+(time.hours per year * (price 3-cost marginal) * utilization factor - cost operating fixed) / (1 + WACC) ^ 3
+(time.hours per year * (price 4-cost marginal) * utilization factor - cost operating fixed) / (1 + WACC) ^ 4

NPV10: (time.hours per year*(price 5 - cost marginal)*utilization factor - cost operating fixed)*
(1/(1+WACC)^5 + 1/(1+WACC)^6 + 1/(1+WACC)^7 + 1/(1+WACC)^8 + 1/(1+WACC)^9 + 1/(1+WACC)^10)

NPV15:
(time.hours per year*(price 5 - cost marginal)*utilization factor - cost operating fixed)*
(1/(1+WACC)^11 + 1/(1+WACC)^12 + 1/(1+WACC)^13 + 1/(1+WACC)^14 + 1/(1+WACC)^15)

NPV20:
(time.hours per year*(price 5 - cost marginal)*utilization factor - cost operating fixed)*
(1/(1+WACC)^16 + 1/(1+WACC)^17 + 1/(1+WACC)^18 + 1/(1+WACC)^19 + 1/(1+WACC)^20)

cost marginal
cost operating variable + plants_owned_type_on.Average fuel cost - IfThenElse(((type="solar") 
OR (type="wind")),market.production subsidy,0)

corporate hurdle rate:
0.1
This decides whether a project is implemented or not ...

a market forecast module is needed for the investment - this is provided below:

price trend slope:
(-1.5*(price average m3- ((price average + price average m1 + price average m2 + price average m3)/4))
 -0.5*(price average m2- ((price average + price average m1 + price average m2 + price average m3)/4))
 +0.5*(price average m1- ((price average+price average m1+price average m2+price average m3)/4))
 +1.5*(price average-((price average+price average m1+price average m2+price average m3)/4)))
/min(time.year AD,5)

price 1: - this seems to be in the future
plants_owned_type_on.price trend slope*(time.year AD+1) + plants_owned_type_on.price trend constant

price 2: - this seems to be in the future
plants_owned_type_on.price trend slope*(time.year AD+2) + plants_owned_type_on.price trend constant

price 3: - this seems to be in the future
plants_owned_type_on.price trend slope*(time.year AD+3)+plants_owned_type_on.price trend constant

price 4: - this seems to be in the future
plants_owned_type_on.price trend slope*(time.year AD+4)+plants_owned_type_on.price trend constant

price 5: - this seems to be in the future
plants_owned_type_on.price trend slope*(time.year AD+5)+plants_owned_type_on.price trend constant

price trend constant:
((price average+price average m1+price average m2+price average m3)/4)-(time.year AD-2.5)*price trend slope

five year profitability:
((((time.year AD+1)*price trend slope+price trend constant)-marginal cost)/(1+investor.discount rate)+
(((time.year AD+2)*price trend slope+price trend constant)-marginal cost)/(1+investor.discount rate)^2+
(((time.year AD+3)*price trend slope+price trend constant)-marginal cost)/(1+investor.discount rate)^3+
(((time.year AD+4)*price trend slope+price trend constant)-marginal cost)/(1+investor.discount rate)^4+
(((time.year AD+5)*price trend slope+price trend constant)-marginal cost)/(1+investor.discount rate)^5)
*time.hours per year*utilization factor*capacity fixed
-yearly avoidable costs*(1+1/(1+investor.discount rate)
+1/(1+investor.discount rate)^2+1/(1+investor.discount rate)^3+1/(1+investor.discount rate)^4+1
/(1+investor.discount rate)^5)

next year profitability
-yearly avoidable costs+capacity constructed*utilization factor*time.hours per year*
(-marginal cost+((time.year AD+1)*price trend slope+price trend constant))

profitability index:
NPV/investment costs
'''