from apps.app.data import cmai_data

filename = "/Users/junaid/PycharmProjects/CMAI/CMAI_FinalPDFs.xlsx"


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

    taxonomies = {"AI Filters": list(), "CM Filters": list(), "Others": list()}
    for column in columns[:4]:
        taxonomies['AI Filters'].append({'name': column,
                                         'values': {value: {'count': 0, 'checked': True, 'to_show': True} for value in list(get_list(cmai_data[column])[1].keys())},
                                         'count': 0})
    for column in columns[4:6]:
        taxonomies['CM Filters'].append({'name': column,
                                         'values': {value: {'count': 0, 'checked': True, 'to_show': True} for value in list(get_list(cmai_data[column])[1].keys())},
                                         'count': 0})
    for column in columns[6:]:
        taxonomies['Others'].append({'name': column,
                                     'values': {value: {'count': 0, 'checked': True, 'to_show': True} for value in list(get_list(cmai_data[column])[1].keys())},
                                     'count': 0})
    return taxonomies
