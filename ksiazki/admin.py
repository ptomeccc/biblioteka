from django.contrib import admin
from .models import Ksiazka

# Register your models here.
@admin.register(Ksiazka)
class KsiazkaAdmin(admin.ModelAdmin):
    list_display = ('tytul', 'autor', 'isbn', 'rok_wydania', 'gatunek','liczba_egzemplarzy')
    list_editable = ('liczba_egzemplarzy',)
    list_filter = ('gatunek', 'rok_wydania')
    search_fields = ('tytul', 'autor', 'isbn')