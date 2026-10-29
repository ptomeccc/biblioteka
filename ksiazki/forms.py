from django import forms
from .models import Ksiazka

class KsiazkaForm(forms.ModelForm):
    class Meta:
        model = Ksiazka
        fields = ['tytul', 'autor', 'isbn', 'rok_wydania', 'gatunek','liczba_egzemplarzy']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_isbn(self):
    # Puste ISBN zapisujemy jako NULL, żeby nie łamać unikalności
        return self.cleaned_data['isbn'] or None