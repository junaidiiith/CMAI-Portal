import pandas as pd


def f(x):
    if x.strip() in reverse_keys:
        return reverse_keys[x.strip()]
    return "Others"


data_file = "cmai_survey_file.xlsx"
countries_file = "Countries_count.xlsx"
cmai_data = pd.read_excel(data_file)
countries = pd.read_excel(countries_file)

d = dict()
d['UML & UML Diagram Type & UML Profile'] = ['UML', 'UML Profile', 'Class Diagram', 'State Machine Diagram',
                                             'Activity Diagram', 'Object Diagram', 'Use Case Diagram',
                                             'State Diagram',
                                             'Sequence Diagram', 'State Chart Diagram']
d['Petri Nets'] = ['Petri Net', 'Fuzzy Petri Net', 'Petri Net extension']
d['Entity Relationship'] = ['Entity Relationship Diagram', 'EER']
d['Goal Model & iStar'] = ['Goal Model', 'iStar']
d['SysML'] = ['SysML', 'SysML Profile']
d['DSML'] = ['DSML', 'DSML (document metamodel)']

reverse_keys = dict()
for key, values in d.items():
    for value in values:
        reverse_keys[value] = key

reverse_keys['Domain Ontology'] = 'Domain Ontology'
reverse_keys["Ecore"] = "Ecore"
reverse_keys['BPMN'] = "BPMN"

cmai_data['Modelling Language'] = cmai_data['Modelling Language'].apply(
        lambda x: ", ".join(list(map(f, x.split(',')))) if not isinstance(x, float) else "Others")

print("Data Loaded!")