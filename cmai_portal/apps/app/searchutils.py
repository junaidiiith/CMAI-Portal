import pandas as pd
from apps.app.data import cmai_data


def get_records_by_column_value(column_name, value):
    return cmai_data[cmai_data[column_name].str.contains(value)]


def get_records_by_column_values(column_name, values):
    results = pd.DataFrame()
    for value in values:
        records = get_records_by_column_value(column_name, value)
        if len(results) == 0:
            results = records
        else:
            results = results.merge(results, records, how='outer', on=['Title'])

    return results


def get_records_by_taxonomies(taxonomies):
    results = pd.DataFrame()
    for taxonomy, values in taxonomies.items():
        records = get_records_by_column_values(taxonomy, values)
        if len(results) == 0:
            results = records
        else:
            results = results.merge(results, records, how='outer', on=['Title'])