from apps.app.data import cmai_data


filename = "/Users/junaid/PycharmProjects/CMAI/CMAI_FinalPDFs.xlsx"
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


def f(x):
    if x.strip() in reverse_keys:
        return reverse_keys[x.strip()]
    return "Others"


def get_list(pandas_series, delimiter=','):
    values_ = [[v.strip() for v in value_.split(delimiter)]
              if value_ and not isinstance(value_, float) else ""
               for _, value_ in pandas_series.iteritems()]
    unique_values = dict()
    for value_ in values_:
        for v in value_:
            if v in unique_values:
                unique_values[v] += 1
            else:
                unique_values[v] = 1
    return values_, unique_values


def get_taxonomies():
    columns = ['AI Taxonomy Domain', 'AI Taxonomy Subdomain', 'AI Technique', 'AI model Value to CM',
               'Modeling Purpose',
               'Modelling Language', 'Contribution Type', 'Research Type']
    cmai_data['Modelling Language'] = cmai_data['Modelling Language'].apply(
        lambda x: ", ".join(list(map(f, x.split(',')))) if not isinstance(x, float) else "Others")

    taxonomies = {"AI Filters": list(), "CM Filters": list(), "Others": list()}
    for column in columns[:4]:
        taxonomies['AI Filters'].append({'name': column, 'values': list(get_list(cmai_data[column])[1].keys())})
    for column in columns[4:6]:
        taxonomies['CM Filters'].append({'name': column, 'values': list(get_list(cmai_data[column])[1].keys())})
    for column in columns[6:]:
        taxonomies['Others'].append({'name': column, 'values': list(get_list(cmai_data[column])[1].keys())})
    return taxonomies
