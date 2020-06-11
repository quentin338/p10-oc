from django import forms


class SearchForm(forms.Form):
    search = forms.CharField(max_length=100, label="", required=True,
                             widget=forms.TextInput(attrs={"class": "search-form bg-nav-search"}))
