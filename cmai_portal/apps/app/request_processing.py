import ast

from apps.app.data import cmai_data

columns = ["AI Taxonomy Domain", 'AI Taxonomy Subdomain', 'AI Technique', 'AI model Value to CM',
           'Modeling Purpose', 'Modelling Language', 'Contribution Type', 'Research Type']
searchFor = ["Publications", "Journals", "Conferences", "Institutions", "Authors"]
SEARCH_BOX = 'search-box'
START_YEAR = "start-year"
END_YEAR = "end-year"
MIN_YEAR = 1980
MAX_YEAR = 2021
COUNTRY = 'country'


def process_request_parameters(request):
    request_dict = request.POST.dict()
    taxonomies = dict()
    for column in columns:
        taxonomies[column] = {"values": list(), "to_show": True, "operator": True}
        for key, value in request_dict.items():
            if key.startswith(column):
                taxonomies[column]['values'].append(key.split(":")[1])

    for key, value in request_dict.items():
        if key.startswith("all:"):
            taxonomies[key.split(":")[1]]['to_show'] = False

    for key, value in request_dict.items():
        if key.startswith("operator:"):
            taxonomies[key.split(":")[1]]['operator'] = False

    search_query = request_dict[SEARCH_BOX]
    searchForTypes = list()
    for searchForType in searchFor:
        for key, value in request_dict.items():
            if key.endswith(searchForType):
                searchForTypes.append(key.split(":")[1])

    start_year, end_year = MIN_YEAR, MAX_YEAR
    if not request_dict[START_YEAR] == 'Start Year':
        start_year = int(request_dict[START_YEAR])
    if not request_dict[END_YEAR] == 'End Year':
        end_year = int(request_dict[END_YEAR])

    countries = list(set([country for countries in cmai_data['Countries']
                          for country in set(ast.literal_eval(countries))]))
    if COUNTRY in request_dict and request_dict[COUNTRY] != 'Country':
        countries = request_dict[COUNTRY]

    context = {
        'search_query': search_query,
        'taxonomies': taxonomies,
        'searchForTypes': searchForTypes,
        'start_year': start_year,
        'end_year': end_year,
        'countries': countries,
    }

    return context


def get_dummy_publications():
    data = list()
    for i, row in cmai_data.iterrows():
        data_row = dict()
        for column in cmai_data.columns:
            data_row[column] = row[column]
        data.append(data_row)
        if i == 10:
            break
    return data

