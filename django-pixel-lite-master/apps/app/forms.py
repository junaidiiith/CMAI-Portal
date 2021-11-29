from django import forms


class Taxonomy(forms.Form):
    def __init__(self, name, values):
        super(Taxonomy, self).__init__()
        self.name = name
        self.values = [(value, forms.BooleanField()) for value in values]


class CompleteForm(forms.Form):
    def __init__(self, taxonomies):
        super(CompleteForm, self).__init__()
        self.taxonomies = [Taxonomy(taxonomy_name, taxonomy_values)
                           for taxonomy_name, taxonomy_values in taxonomies.items()]
    search = forms.CharField()
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
