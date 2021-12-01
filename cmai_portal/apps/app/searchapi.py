from apps.app.searchutils import *


def search_publications(context):
    mandatory_header = ["Title", "Year", "Authors", "DOI", "Abstract"]
    badges_columns = ["AI Taxonomy Domain", 'AI Taxonomy Subdomain', 'AI Technique', 'AI model Value to CM',
                      'Modeling Purpose', 'Modelling Language', 'Contribution Type', 'Research Type']

    taxonomies = context['taxonomies']
    search_query = context['search_query']
    for taxonomy, data in taxonomies.items():
        if not data['to_show']:
            badges_columns.remove(taxonomy)

    records, summary = get_records(taxonomies, search_query, context['start_year'], context['end_year'])
    publications = format_records_to_show(records, mandatory_header, badges_columns)
    return publications, summary


def search_authors(context):
    print("Authors Search!!")


def search_journals(context):
    pass


def search_conferences(context):
    pass


def search_institutions(context):
    pass


def search_authors_by_country(context):
    pass


def search_authors_by_institution(context):
    pass


def search_publication_by_institution(context):
    pass
