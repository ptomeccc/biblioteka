from django.contrib import admin
from .models import Czytelnik, Ksiazka, Wypozyczenie

# Register your models here.
class WypozyczenieInline(admin.TabularInline):
    model = Wypozyczenie
    extra = 0
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
    list_filter = ('data_zwrotu',)
