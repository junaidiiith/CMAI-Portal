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


def get_records_by_column_value(column_name, value):
    records = cmai_data[~cmai_data[column_name].isna()]
    return records[records[column_name].apply(str.lower).str.contains(value.lower())]


def get_records_by_column_values(column_name, values):
    results = pd.DataFrame()
    for value in values:
        records = get_records_by_column_value(column_name, value)
        results = pd.concat([results, records], ignore_index=True).drop_duplicates().reset_index(drop=True)
    return results


def get_records_by_taxonomies(taxonomies):
    results = pd.DataFrame()
    for taxonomy, data in taxonomies.items():
        records = get_records_by_column_values(taxonomy, data['values'])
        if len(results) == 0:
            results = records
        else:
            if data['operator']:
                results = pd.concat([results, records], ignore_index=True).drop_duplicates().reset_index(
                    drop=True)
            else:
                results = pd.merge(results, records, how='inner')
    return results


def get_records_by_year(gt_value=1980, lt_value=2021):
    gt_records = cmai_data[cmai_data['Year'] >= gt_value]
    lt_records = cmai_data[cmai_data['Year'] <= lt_value]
    results = pd.merge(gt_records, lt_records, how='inner')
    return results


def get_records_by_keywords(search_query):
    text_tokens = word_tokenize(search_query)
    tokens_without_sw = [word for word in text_tokens if word not in stopwords.words() and word.isalpha()]
    title_records = get_records_by_column_values('Title', tokens_without_sw)
    abstract_records = get_records_by_column_values('Abstract', tokens_without_sw)
    results = pd.concat([title_records, abstract_records], ignore_index=True).drop_duplicates().reset_index(drop=True)
    return results


def get_records(taxonomies, search_query, start_year, end_year):
    records_by_keywords = get_records_by_keywords(search_query)
    records_by_taxonomies = get_records_by_taxonomies(taxonomies)
    records_by_year = get_records_by_year(start_year, end_year)
    results = pd.merge(records_by_keywords, records_by_taxonomies, how='inner')
    results = pd.merge(results, records_by_year, how='inner')
    summary = create_results_summary(results)
    return results, summary


def format_records_to_show(df, mandatory_header, badges_columns):
    results = list()
    for i, row in df.iterrows():
        result = {'badges': {'AI': list(), 'CM': list(), 'Others': list()}}
        for column in mandatory_header:
            result[column] = row[column]
        for column in badges_columns:
            if not isinstance(row[column], float):
                result['badges'][badges_categories[column]] += [badge.strip() for badge in row[column].split(',')]
        result['index'] = i
        results.append(result)
    return results


def create_results_summary(results):
    authors_affiliations_summary = get_authors_affiliations_summary(results)
    doc_type_summary = get_document_type_summary(results)
    return {"affiliations_summary": authors_affiliations_summary, "doc_type_summary": doc_type_summary}


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
    }

    return affiliation_summary


def get_document_type_summary(results):
    journals = results.loc[results['Document Type'] == 'Article']['SourceTitle']
    papers = results.loc[results['Document Type'] == 'Conference Paper']['SourceTitle']
    chapters = results[results['Document Type'] == 'Book Chapter']['SourceTitle']
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
    }

    return doc_type_summary
