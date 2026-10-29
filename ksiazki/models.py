from datetime import timedelta

from django.db import models
from django.db.models import Count, F, Q
from django.utils import timezone

# Create your models here.

class KsiazkaQuerySet(models.QuerySet):
    def z_dostepnymi(self):
        # jedyna definicja dostępności: egzemplarze minus aktywne wypożyczenia
        return self.annotate(
            wypozyczone=Count('wypozyczenia', filter=Q(wypozyczenia__data_zwrotu__isnull=True)),
        ).annotate(dostepne=F('liczba_egzemplarzy') - F('wypozyczone'))


class Ksiazka(models.Model):
    tytul = models.CharField('Tytuł', max_length=200)
    autor = models.CharField('Autor', max_length=200)
    isbn = models.CharField('ISBN', max_length=17, unique=True, blank=True, null=True)
    rok_wydania = models.PositiveIntegerField('Rok wydania', blank=True, null=True)
    gatunek = models.CharField('Gatunek', max_length=100, blank=True)
    liczba_egzemplarzy = models.PositiveIntegerField('Liczba egzemplarzy', default=1)
    dodano = models.DateTimeField('Dodano', auto_now_add=True)

    objects = KsiazkaQuerySet.as_manager()

    class Meta:
        verbose_name = 'Książka'
        verbose_name_plural = 'Książki'
        ordering = ['tytul']

    def __str__(self):
        return f'{self.tytul} – {self.autor}'

    def ile_dostepnych(self):
        return Ksiazka.objects.z_dostepnymi().get(pk=self.pk).dostepne


class Czytelnik(models.Model):
    imie = models.CharField('Imię', max_length=100)
    nazwisko = models.CharField('Nazwisko', max_length=100)
    email = models.EmailField('E-mail', unique=True)
    numer_karty = models.CharField('Numer karty', max_length=20, unique=True)

    class Meta:
        verbose_name = 'Czytelnik'
        verbose_name_plural = 'Czytelnicy'
        ordering = ['nazwisko', 'imie']

    def __str__(self):
        return f'{self.imie} {self.nazwisko}'


def za_30_dni():
    return timezone.localdate() + timedelta(days=30)


class Wypozyczenie(models.Model):
    # PROTECT: nie gubimy historii wypożyczeń przy usunięciu książki lub czytelnika
    ksiazka = models.ForeignKey(Ksiazka, on_delete=models.PROTECT, related_name='wypozyczenia', verbose_name='Książka')
    czytelnik = models.ForeignKey(Czytelnik, on_delete=models.PROTECT, related_name='wypozyczenia', verbose_name='Czytelnik')
    data_wypozyczenia = models.DateField('Data wypożyczenia', default=timezone.localdate)
    termin_zwrotu = models.DateField('Termin zwrotu', default=za_30_dni)
    data_zwrotu = models.DateField('Data zwrotu', null=True, blank=True)

    class Meta:
        verbose_name = 'Wypożyczenie'
        verbose_name_plural = 'Wypożyczenia'
        ordering = ['termin_zwrotu']

    def __str__(self):
        return f'{self.ksiazka} → {self.czytelnik}'

    @property
    def aktywne(self):
        return self.data_zwrotu is None

    @property
    def po_terminie(self):
        return self.aktywne and self.termin_zwrotu < timezone.localdate()
