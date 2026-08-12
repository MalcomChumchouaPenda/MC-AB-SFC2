
# def test_government_updates_fiscal_policy_integration():

#     model = EcoModel()

#     government = GovernmentAgent(model)

#     country = CountrySpace(
#         model,
#         government,
#         national_cb=None,
#     )

#     country.average_price = 2
#     country.average_productivity = 3
#     country.gdp = 1000

#     government.initial_public_spending = 10
#     government.public_spending = 100
#     government.tax_rate = 0.20

#     government.deficit_ratio = 0.10
#     government.dmax = 0.05

#     government.tax_min = 0.10
#     government.tax_max = 0.50

#     government.g_min = 0.05
#     government.g_max = 0.20

#     government.delta = 0.10

#     government.calc_desired_public_spending()

#     government.update_fiscal_policy(
#         random_value=0.05
#     )

#     assert government.desired_public_spending == 60

#     assert government.public_spending == 95

#     assert government.next_tax_rate == 0.21

# def test_government_increases_spending_when_deficit_is_low():

#     model = EcoModel()

#     government = GovernmentAgent(model)

#     country = CountrySpace(
#         model,
#         government,
#         national_cb=None,
#     )

#     country.average_price = 2
#     country.average_productivity = 3
#     country.gdp = 1000

#     government.initial_public_spending = 10
#     government.public_spending = 100
#     government.tax_rate = 0.20

#     government.deficit_ratio = 0.02
#     government.dmax = 0.05
#     government.delta = 0.10

#     government.calc_desired_public_spending()

#     government.update_fiscal_policy(
#         random_value=0.05
#     )

#     assert government.public_spending == 105
#     assert government.next_tax_rate == 0.20