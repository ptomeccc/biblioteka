from django.db import models

# Create your models here.

class Ksiazka(models.Model):
    tytul = models.CharField('Tytuł', max_length=200)
    autor = models.CharField('Autor', max_length=200)
    isbn = models.CharField('ISBN', max_length=17, unique=True, blank=True, null=True)
    rok_wydania = models.PositiveIntegerField('Rok wydania', blank=True, null=True)
    gatunek = models.CharField('Gatunek', max_length=100, blank=True)
    liczba_egzemplarzy = models.PositiveIntegerField('Liczba egzemplarzy', default=1)
    dodano = models.DateTimeField('Dodano', auto_now_add=True)

    class Meta:
        verbose_name = 'Książka'
        verbose_name_plural = 'Książki'
        ordering = ['tytul']

    def __str__(self):
        return f'{self.tytul} – {self.autor}'