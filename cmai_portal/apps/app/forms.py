from django import forms
from apps.app.data import countries

logical_operators = [('and', 'AND'), ('or', 'OR')]
years = [(str(year), year) for year in range(1980, 2022)]
country_names = countries['Country'].values.tolist()
country_names.sort()
country_names = [(country, country) for country in country_names]


class Taxonomy(forms.Form):
    def __init__(self, taxonomy):
        super(Taxonomy, self).__init__()
        self.name = taxonomy['name']
        self.values = [(forms.BooleanField(label=key), value_check['count'], value_check['checked'])
                       for key, value_check in taxonomy['values'].items()]
        self.operator = forms.BooleanField(label="results_merge_type"), taxonomy['operator']
        self.id = "".join(self.name.split())
        self.count = taxonomy['count']


class CompleteForm(forms.Form):
    def __init__(self, taxonomies, search_query, search_types):
        super(CompleteForm, self).__init__()
        self.ai_taxonomies = [Taxonomy(taxonomy) for taxonomy in taxonomies['AI Filters']]
        self.cm_taxonomies = [Taxonomy(taxonomy) for taxonomy in taxonomies['CM Filters']]
        self.others = [Taxonomy(taxonomy) for taxonomy in taxonomies['Others']]
        self.search_types = [forms.BooleanField(label=search_type) for search_type in search_types]
        self.search_query = search_query

    start_year = forms.ChoiceField(label="search_start_date", choices=years)
    end_year = forms.ChoiceField(label="search_end_date", choices=years)
    country = forms.ChoiceField(label="country", choices=country_names)
    taxonomy_merge = forms.BooleanField()
