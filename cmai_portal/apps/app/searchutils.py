import ast

import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from apps.app.data import cmai_data

nltk.download('stopwords')
nltk.download('punkt')

badges_categories = {
    "AI Taxonomy Domain": 'AI',
    'AI Taxonomy Subdomain': 'AI',
    'AI Technique': 'AI',
    'AI model Value to CM': 'AI',
    'Modeling Purpose': 'CM',
    'Modelling Language': 'CM',
    'Contribution Type': 'Others',
    'Research Type': 'Others'
}
search_type_columns = {
    'Publications': ['Title', 'Abstract'],
    'Venues': ['SourceTitle'],
    'Authors': ['Authors']
}

SOURCE_TITLE = 'SourceTitle'


def get_records_by_column_value(column_name, value):
    records = cmai_data[~cmai_data[column_name].isna()]
    return records[records[column_name].apply(str.lower).str.contains(value.lower())]


def get_records_by_column_values(column_name, values):
    results = pd.DataFrame()
    for value in values:
        records = get_records_by_column_value(column_name, value)
        results = pd.concat([results, records], ignore_index=True).drop_duplicates().reset_index(drop=True)
    return results


def get_checked_values(values):
    checked_values = list()
    for value, value_data in values.items():
        if value_data['checked']:
            checked_values.append(value)
    return checked_values


def get_records_by_taxonomies(taxonomies_data, checked=False):
    results_intersection = pd.DataFrame()
    for taxonomy_type, taxonomies in taxonomies_data.items():
        for taxonomy in taxonomies:
            if taxonomy['operator']:
                values = get_checked_values(taxonomy['values']) if checked else list(taxonomy['values'].keys())
                records = get_records_by_column_values(taxonomy['name'], values)
                if len(results_intersection) == 0:
                    results_intersection = records
                else:
                    results_intersection = pd.merge(results_intersection, records, how='inner')

    results_union = pd.DataFrame()
    for taxonomy_type, taxonomies in taxonomies_data.items():
        for taxonomy in taxonomies:
            if not taxonomy['operator']:
                values = get_checked_values(taxonomy['values']) if checked else list(taxonomy['values'].keys())
                records = get_records_by_column_values(taxonomy['name'], values)
                if len(results_union) == 0:
                    results_union = records
                else:
                    results_union = pd.concat([results_union, records], ignore_index=True).drop_duplicates()\
                        .reset_index(drop=True)
    if len(results_intersection):
        results = pd.merge(results_intersection, results_union, how='inner')
    else:
        results = results_union
    return results


def get_records_by_year(gt_value=1980, lt_value=2021):
    gt_records = cmai_data[cmai_data['Year'] >= gt_value]
    lt_records = cmai_data[cmai_data['Year'] <= lt_value]
    results = pd.merge(gt_records, lt_records, how='inner')
    return results


def get_records_by_keywords(search_query, search_type):
    text_tokens = word_tokenize(search_query)
    if search_type == "Publications":
        text_tokens = [word for word in text_tokens if word not in stopwords.words() and word.isalpha()]

    results = pd.DataFrame()
    for column in search_type_columns[search_type]:
        records = get_records_by_column_values(column, text_tokens)
        results = pd.concat([results, records], ignore_index=True).drop_duplicates().reset_index(drop=True)
    return results


def present_in_request(taxonomy_value, request_dict):
    for k, v in request_dict.items():
        if taxonomy_value in k:
            return True
    return False


def get_taxonomies_count(results, request_taxonomies):
    for taxonomy_type, taxonomies in request_taxonomies.items():
        for taxonomy in taxonomies:
            for i, result in results.iterrows():
                if not isinstance(result[taxonomy['name']], float):
                    record_values = [value.strip() for value in result[taxonomy['name']].split(",")]
                    for value in record_values:
                        taxonomy['values'][value]['count'] += 1

    final_taxonomies = dict()
    for taxonomy_type, taxonomies in request_taxonomies.items():
        taxonomy_type_list = list()
        for taxonomy in taxonomies:
            temp_taxonomy = dict()
            temp_taxonomy['count'] = sum(v['count'] for v in taxonomy['values'].values())
            temp_taxonomy['name'] = taxonomy['name']
            temp_taxonomy['operator'] = taxonomy['operator']
            t_values = dict()
            for k, v in taxonomy['values'].items():
                if v['count']:
                    t_values[k] = {
                        "count": v['count'],
                        "checked": v['checked']
                    }

            temp_taxonomy['values'] = t_values
            taxonomy_type_list.append(temp_taxonomy)
        final_taxonomies[taxonomy_type] = taxonomy_type_list
    return final_taxonomies


def get_records(taxonomies, search_query, search_type, start_year, end_year):
    records_by_keywords = get_records_by_keywords(search_query, search_type)
    records_by_taxonomies = get_records_by_taxonomies(taxonomies)
    records_by_taxonomies_checked = get_records_by_taxonomies(taxonomies, checked=True)
    records_by_year = get_records_by_year(start_year, end_year)
    results = pd.merge(records_by_keywords, records_by_taxonomies, how='inner')
    results = pd.merge(results, records_by_year, how='inner')
    results_checked = pd.merge(records_by_keywords, records_by_taxonomies_checked, how='inner')
    results_checked = pd.merge(results_checked, records_by_year, how='inner')
    taxonomies_count = get_taxonomies_count(results, taxonomies)
    summary = create_results_summary(results)
    return results_checked, summary, taxonomies_count


def get_badges(result, badges_columns):
    badges = {'AI': list(), 'CM': list(), 'Others': list()}
    for column in badges_columns:
        if not isinstance(result[column], float):
            badges[badges_categories[column]] += [badge.strip() for badge in result[column].split(',')]
    return badges


def get_author_from_authors_list(authors, query):
    authors_list = list()
    authors = [author.strip() for author in authors.split(',')]
    for author in authors:
        if query.lower() in author.lower():
            authors_list.append(author)
    return authors_list


def get_authors_by_publications(publications, search_query):
    author_set = set()
    for i, row in publications.iterrows():
        for author in get_author_from_authors_list(row['Authors'], search_query):
            author_set.add(author)
    authors_data = dict()
    for i, publication in publications.iterrows():
        record = publication
        for author in author_set:
            if author in record['Authors']:
                if author in authors_data:
                    authors_data[author].append(record)
                else:
                    authors_data[author] = [record]
    return authors_data


def get_venues_by_publications(publications, search_query):
    venues_set = set()
    for i, row in publications.iterrows():
        if search_query.lower() in row[SOURCE_TITLE].lower():
            venues_set.add(row[SOURCE_TITLE])
    venues_data = dict()
    for i, publication in publications.iterrows():
        record = publication
        for venue in venues_set:
            if venue == record[SOURCE_TITLE]:
                if venue in venues_data:
                    venues_data[venue].append(record)
                else:
                    venues_data[venue] = [record]
    return venues_data


def format_publications_to_show(df, mandatory_header, badges_columns):
    results = list()
    for i, row in df.iterrows():
        result = dict()
        for column in mandatory_header:
            result[column] = row[column]
        result['badges'] = get_badges(row, badges_columns)
        result['index'] = i + 1
        results.append(result)
    return results


def format_authors_to_show(df, search_query, mandatory_header, badges_columns):
    authors_data = get_authors_by_publications(df, search_query)
    authors_results = list()
    for author, publications in authors_data.items():
        author_result = {'name': author}
        publications_list = list()
        for publication in publications:
            publication_data = dict()
            for column in mandatory_header:
                publication_data[column] = publication[column]
            publication_data['affiliations'] = get_affiliations_list(publication['Author Affiliations'], search_query)
            publication_data['badges'] = get_badges(publication, badges_columns)
            publication_data['hash'] = hash(publication['Title'])
            publications_list.append(publication_data)
        author_result['publications'] = publications_list
        authors_results.append(author_result)
    return authors_results


def format_venues_to_show(df, search_query, mandatory_header, badges_columns):
    venues_data = get_venues_by_publications(df, search_query)
    venues_results = list()
    for venue, publications in venues_data.items():
        venue_result = {'name': venue}
        publications_list = list()
        for publication in publications:
            publication_data = dict()
            for column in mandatory_header:
                publication_data[column] = publication[column]
            publication_data['affiliations'] = get_affiliations_list(publication['Author Affiliations'])
            publication_data['badges'] = get_badges(publication, badges_columns)
            publications_list.append(publication_data)
        venue_result['publications'] = publications_list
        venues_results.append(venue_result)
    return venues_results


def create_results_summary(results):
    authors_affiliations_summary = get_authors_affiliations_summary(results)
    doc_type_summary = get_document_type_summary(results)
    years = results['Year'].unique().tolist()
    years.sort()
    return {
        "affiliations_summary": authors_affiliations_summary,
        "doc_type_summary": doc_type_summary,
        'years': {'name': 'Year', 'values': years}
    }


def add_if_present(keys, dictionary):
    for key in keys:
        if key in dictionary:
            dictionary[key] += 1
        else:
            dictionary[key] = 1
    return dictionary


def getTopN(d, n=5):
    return sorted(d.items(), key=lambda x: x[1], reverse=True)[:n]


def get_authors_affiliations_summary(results):
    universities, countries, authors = dict(), dict(), dict()
    universities_count, countries_count, authors_count = dict(), dict(), dict()

    for i, row in results.iterrows():
        t_authors, t_country, t_uni = list(), list(), list()
        title = row['Title']
        affiliations = ast.literal_eval(row['Author Affiliations'])
        for affiliation in affiliations:
            name = affiliation['name']
            t_authors.append(name)
            aff = affiliation['Affiliation(s)']
            if not aff:
                continue
            if isinstance(aff[0], tuple):
                aff = list(aff)

            if isinstance(aff, list):
                for a in aff:
                    country = a[-1]
                    university = " ".join(a[:-1]).strip()
                    if "," in university and "university of" == university.split(',')[1].lower().strip():
                        university = " ".join(university.split(',')[::-1]).strip()
                    t_country.append(country)
                    t_uni.append(university)

            elif isinstance(aff, tuple):
                country = aff[-1]
                university = " ".join(aff[:-1]).strip()
                if "," in university and "university of" == university.split(',')[1].lower().strip():
                    university = " ".join(university.split(',')[::-1]).strip()
                t_country.append(country)
                t_uni.append(university)

        authors[title] = t_authors
        countries[title] = t_country
        universities[title] = t_uni
        universities_count = add_if_present(set(t_uni), universities_count)
        countries_count = add_if_present(set(t_country), countries_count)
        authors_count = add_if_present(set(t_authors), authors_count)
        assert len(t_authors) == len(affiliations)

    affiliation_summary = {
        "author_count": len(authors_count),
        "uni_count": len(universities_count),
        "country_count": len(countries_count),
        "topNAuthors": getTopN(authors_count, 10),
        "topNUniversities": getTopN(universities_count, 10),
        "topNCountries": getTopN(countries_count, 10),
        "authors": {
            'name': "Authors",
            'values': list(authors_count.keys())
        },
        "Institutions": {
            'name': "Institutions",
            'values': list(universities_count.keys())
        },
        "countries": {
            "name": "Countries",
            "values": list(countries.keys())
        }
    }

    return affiliation_summary


def get_document_type_summary(results):
    journals = results.loc[results['DocumentType'] == 'Article']['SourceTitle']
    papers = results.loc[results['DocumentType'] == 'Conference Paper']['SourceTitle']
    chapters = results[results['DocumentType'] == 'Book Chapter']['SourceTitle']
    chapter_count, paper_count, journal_count = dict(), dict(), dict()
    for paper in papers:
        try:
            paper_count[paper] += 1
        except KeyError:
            paper_count[paper] = 1

    for chapter in chapters:
        try:
            chapter_count[chapter] += 1
        except KeyError:
            chapter_count[chapter] = 1

    for journal in journals:
        try:
            journal_count[journal] += 1
        except KeyError:
            journal_count[journal] = 1
    doc_type_summary = {
        'journal_count': len(journals),
        'chapters_count': len(chapters),
        'conferences_count': len(papers),
        "topNJournals": getTopN(journal_count, 5),
        "topNConferences": getTopN(paper_count, 5),
        "conferences": {
            'name': "Conference Papers",
            'values': list(paper_count.keys()),
        },
        "journals": {
            'name': "Journals",
            'values': list(journal_count.keys())
        }
    }

    return doc_type_summary


def get_country_and_university_from_affiliation(aff):
    country = aff[-1]
    university = " ".join(aff[:-1]).strip()
    if "," in university and "university of" == university.split(',')[1].lower().strip():
        university = " ".join(university.split(',')[::-1]).strip()
    return university, country


def get_affiliations_list(affiliations, search_query=None):
    affiliations_list = list()
    affiliations = ast.literal_eval(affiliations)
    for affiliation in affiliations:
        affiliation_data = {
            "author": affiliation['name'],
            'searched_author': True if search_query and search_query.lower() in affiliation['name'].lower() else False
        }
        aff = affiliation['Affiliation(s)']
        institute_countries = list()
        if not aff:
            affiliation_data['institute_countries'] = list()
            continue
        if isinstance(aff[0], tuple):
            aff = list(aff)

        if isinstance(aff, list):
            for a in aff:
                u, c = get_country_and_university_from_affiliation(a)
                institute_countries.append({'university': u, 'country': c})

        elif isinstance(aff, tuple):
            u, c = get_country_and_university_from_affiliation(aff)
            institute_countries.append({'university': u, 'country': c})
        affiliation_data['institute_countries'] = institute_countries
        affiliations_list.append(affiliation_data)

    return affiliations_list
