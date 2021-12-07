import ast

from apps.app.data import cmai_data
from apps.app import cmai_taxonomies


columns = ["AI Taxonomy Domain", 'AI Taxonomy Subdomain', 'AI Technique', 'AI model Value to CM',
           'Modeling Purpose', 'Modelling Language', 'Contribution Type', 'Research Type']

taxonomy_map = {
    "AI Taxonomy Domain": "AI Filters",
    'AI Taxonomy Subdomain': "AI Filters",
    'AI Technique': "AI Filters",
    'AI model Value to CM': "AI Filters",
    'Modeling Purpose': "CM Filters",
    'Modelling Language': "CM Filters",
    'Contribution Type': "Others",
    'Research Type': "Others"
}
searchFor = ["Publications", "Journals & Conferences", "Authors"]
SEARCH_BOX = 'search-box'
START_YEAR = "start-year"
END_YEAR = "end-year"
MIN_YEAR = 1980
MAX_YEAR = 2021
COUNTRY = 'country'
SEARCH_TYPE_POST = 'search-type'
SEARCH_TYPE_GET = 'search_type'
PAGE_ID = 'page_index'
SEARCH_QUERY = 'search_query'


def update_taxonomy(request_post_dict, taxonomy, taxonomies):
    filter_taxonomies = taxonomies[taxonomy_map[taxonomy]]
    for filter_taxonomy in filter_taxonomies:
        if filter_taxonomy['name'] == taxonomy:
            values = filter_taxonomy['values']
        else:
            continue
        for value, _ in values.items():
            found = False
            for k, v in request_post_dict.items():
                if value in k:
                    found = True
            if not found:
                values[value]['checked'] = False

        if "operator:"+filter_taxonomy['name'] in request_post_dict:
            filter_taxonomy['operator'] = True


def update_taxonomies(request, search_query, search_type):
    request_post_dict = request.POST.dict()
    tax_key = 'taxonomies' + search_query.lower() + search_type.lower()
    assert tax_key in request.session
    taxonomies = request.session[tax_key]
    for k, v in request_post_dict.items():
        if k.startswith("apply_filter"):
            taxonomy = k.split(":")[1]
            update_taxonomy(request_post_dict, taxonomy, taxonomies)
    initialise_count(taxonomies)
    return taxonomies


def initialise_taxonomies(request, search_query, search_type):
    taxonomies = cmai_taxonomies.get_taxonomies()
    tax_key = 'taxonomies' + search_query.lower() + search_type.lower()
    request.session[tax_key] = taxonomies
    return taxonomies


def initialise_count(all_taxonomies):
    for taxonomy_type, taxonomies in all_taxonomies.items():
        for taxonomy in taxonomies:
            taxonomy['count'] = 0
            for _, values in taxonomy['values'].items():
                values['count'] = 0


def get_taxonomies_based_on_request(request, search_query, search_type):
    request_post_dict = request.POST.dict()
    filter_applied = False
    for k, v in request_post_dict.items():
        if k.startswith("apply_filter"):
            filter_applied = True
    if filter_applied:
        taxonomies = update_taxonomies(request, search_query, search_type)
    else:
        taxonomies = initialise_taxonomies(request, search_query, search_type)

    return taxonomies


def process_request_parameters(request):
    request_post_dict = request.POST.dict()
    request_get_dict = request.GET.dict()
    if SEARCH_BOX in request_post_dict:
        search_query = request_post_dict[SEARCH_BOX]
    else:
        search_query = request_get_dict[SEARCH_QUERY]
    searchForTypes = list()
    for searchForType in searchFor:
        for key, value in request_post_dict.items():
            if key.endswith(searchForType):
                searchForTypes.append(key.split(":")[1])

    start_year, end_year = MIN_YEAR, MAX_YEAR

    countries = list(set([country for countries in cmai_data['Countries']
                          for country in set(ast.literal_eval(countries))]))
    if COUNTRY in request_post_dict and request_post_dict[COUNTRY] != 'Country':
        countries = request_post_dict[COUNTRY]

    if SEARCH_TYPE_POST in request_post_dict:
        search_type = request_post_dict[SEARCH_TYPE_POST]
        if search_type == "Journals & Conferences":
            search_type = "Venues"
    else:
        search_type = request_get_dict[SEARCH_TYPE_GET]

    page_index = request_get_dict[PAGE_ID] if PAGE_ID in request_get_dict else 0

    context = {
        'search_query': search_query,
        'searchForTypes': searchForTypes,
        'start_year': start_year,
        'end_year': end_year,
        'countries': countries,
        'search_type': search_type,
        'page_id': page_index
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

