import ast

from apps.app.data import cmai_data, countries
from apps.app import cmai_taxonomies

years = [year for year in range(1980, 2022)]
country_names = countries['Country'].values.tolist()
country_names.sort()
country_names = [country for country in country_names]

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

        # if "operator:"+filter_taxonomy['name'] in request_post_dict:
        #     filter_taxonomy['operator'] = True


def update_year(request_post_dict, non_taxonomies):
    tax_years = non_taxonomies['years']
    filter_years = list()
    for k, v in request_post_dict.items():
        if k.startswith("years_check:"):
            filter_years.append(int(k.split(':')[1]))
    for year, year_data in tax_years['values']:
        if year not in filter_years:
            year_data['checked'] = False

    return tax_years


def update_country(request_post_dict, non_taxonomies):
    tax_countries = non_taxonomies['years']
    filter_countries = list()
    for k, v in request_post_dict.items():
        if k.startswith("countries_check:"):
            filter_countries.append(int(k.split(':')[1]))
    for country, country_data in tax_countries['values']:
        if country not in filter_countries:
            country_data['checked'] = False

    return tax_countries


def update_taxonomies(request, search_query, search_type):
    request_post_dict = request.POST.dict()
    key = 'taxonomies_and_non_taxonomies_data' + search_query.lower() + search_type.lower()
    assert key in request.session
    data = request.session[key]
    taxonomies, non_taxonomies = data['taxonomies'], data['non_taxonomies']
    for k, v in request_post_dict.items():
        if k.startswith("apply_filter"):
            taxonomy = k.split(":")[1]
            update_taxonomy(request_post_dict, taxonomy, taxonomies)
            break
        elif k.startswith("filter_year"):
            update_year(request_post_dict, non_taxonomies)
            break
        elif k.startswith("filter_country"):
            update_country(request_post_dict, non_taxonomies)
            break
    # initialise_count(taxonomies, non_taxonomies)
    return taxonomies, non_taxonomies


def initialise_taxonomies(request, search_query, search_type):
    taxonomies = cmai_taxonomies.get_taxonomies()
    non_taxonomies = {
        "years": {
            "name": "years",
            "values": {year: {'count': 0, 'checked': True, 'to_show': True} for year in years},
            "count": 0
        },
        "countries": {
            "name": "countries",
            "values": {country: {'count': 0, 'checked': True, 'to_show': True} for country in country_names},
            "count": 0
        },
    }
    tax_key = 'taxonomies_and_non_taxonomies_data' + search_query.lower() + search_type.lower()
    request.session[tax_key] = {
        "taxonomies": taxonomies,
        "non_taxonomies": non_taxonomies
    }
    return taxonomies, non_taxonomies


def initialise_count(all_taxonomies, non_taxonomies):
    for taxonomy_type, taxonomies in all_taxonomies.items():
        for taxonomy in taxonomies:
            taxonomy['count'] = 0
            for _, values in taxonomy['values'].items():
                values['count'] = 0

    for taxonomy_type, values in non_taxonomies.items():
        for value, data in values.items():
            data['values']['count'] = 0


def get_taxonomies_based_on_request(request, search_query, search_type):
    request_post_dict = request.POST.dict()
    filter_applied = False
    for k, v in request_post_dict.items():
        if k.startswith("apply_filter") or k.startswith("filter_years") or k.startswith("filter_countries"):
            filter_applied = True
    if filter_applied:
        taxonomies, non_taxonomies = update_taxonomies(request, search_query, search_type)
    else:
        taxonomies, non_taxonomies = initialise_taxonomies(request, search_query, search_type)

    return taxonomies, non_taxonomies


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
