import pandas as pd


data_file = "cmai_survey_file.xlsx"
countries_file = "Countries_count.xlsx"
cmai_data = pd.read_excel(data_file)
countries = pd.read_excel(countries_file)

print("Data Loaded!")
