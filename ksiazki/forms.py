from django import forms
from .models import Czytelnik, Ksiazka, Wypozyczenie

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


class CzytelnikForm(forms.ModelForm):
    class Meta:
        model = Czytelnik
        fields = ['imie', 'nazwisko', 'email', 'numer_karty']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class WypozyczenieForm(forms.ModelForm):
    class Meta:
        model = Wypozyczenie
        fields = ['ksiazka', 'czytelnik', 'termin_zwrotu']
        widgets = {'termin_zwrotu': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-select' if name in ('ksiazka', 'czytelnik') else 'form-control'

    def clean(self):
        cleaned = super().clean()
        ksiazka = cleaned.get('ksiazka')
        if ksiazka and ksiazka.ile_dostepnych() < 1:
            self.add_error('ksiazka', 'Brak wolnych egzemplarzy tej książki.')
        return cleaned
