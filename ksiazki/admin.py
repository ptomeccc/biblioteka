from django import forms
from django.contrib import admin
from .models import Czytelnik, Ksiazka, Wypozyczenie

# Register your models here.
class WypozyczenieAdminForm(forms.ModelForm):
    """Ta sama blokada braku egzemplarzy co w WypozyczenieForm, także dla inline (tam pole ksiazka nie jest w formularzu)."""

    class Meta:
        model = Wypozyczenie
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        ksiazka = cleaned.get('ksiazka') or Ksiazka.objects.filter(pk=self.instance.ksiazka_id).first()
        # tylko nowe, aktywne wypożyczenia; edycja istniejącego nie zmienia zajętości
        if self.instance.pk is None and not cleaned.get('data_zwrotu') and ksiazka and ksiazka.ile_dostepnych() < 1:
            raise forms.ValidationError('Brak wolnych egzemplarzy tej książki.')
        return cleaned


class WypozyczenieInline(admin.TabularInline):
    model = Wypozyczenie
    form = WypozyczenieAdminForm
    extra = 0
    can_delete = False  # historia wypożyczeń nie jest kasowana (spójnie z PROTECT)
    raw_id_fields = ('czytelnik',)


@admin.register(Ksiazka)
class KsiazkaAdmin(admin.ModelAdmin):
    list_display = ('tytul', 'autor', 'isbn', 'rok_wydania', 'gatunek','liczba_egzemplarzy')
    list_editable = ('liczba_egzemplarzy',)
    list_filter = ('gatunek', 'rok_wydania')
    search_fields = ('tytul', 'autor', 'isbn')
    inlines = [WypozyczenieInline]


@admin.register(Czytelnik)
class CzytelnikAdmin(admin.ModelAdmin):
    list_display = ('nazwisko', 'imie', 'email', 'numer_karty')
    search_fields = ('imie', 'nazwisko', 'email', 'numer_karty')


@admin.register(Wypozyczenie)
class WypozyczenieAdmin(admin.ModelAdmin):
    list_display = ('ksiazka', 'czytelnik', 'data_wypozyczenia', 'termin_zwrotu', 'data_zwrotu')
    form = WypozyczenieAdminForm
    list_filter = ('data_zwrotu',)
