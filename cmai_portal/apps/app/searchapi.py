from apps.app.searchutils import *


def search_records(context):
    mandatory_header = ["Title", "Year", "Authors", "DOI", "Abstract", "SourceTitle", "DocumentType"]
    badges_columns = ["AI Taxonomy Domain", 'AI Taxonomy Subdomain', 'AI Technique', 'AI model Value to CM',
                      'Modeling Purpose', 'Modelling Language', 'Contribution Type', 'Research Type']

    taxonomies, non_taxonomies = context['taxonomies'], context['non_taxonomies']
    search_query = context['search_query']

    records, summary, taxonomy_count, non_taxonomy_count = get_records(taxonomies, non_taxonomies, search_query, context['search_type'])
    if context['search_type'] == "Publications":
        records = format_publications_to_show(records, mandatory_header, badges_columns)
    elif context['search_type'] == "Authors":
        records = format_authors_to_show(records, search_query, mandatory_header, badges_columns)
    else:
        records = format_venues_to_show(records, search_query, mandatory_header, badges_columns)
    return records, summary, taxonomy_count, non_taxonomy_count

