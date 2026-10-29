from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import WypozyczenieForm
from .models import Czytelnik, Ksiazka, Wypozyczenie


class WypozyczeniaTest(TestCase):
    def setUp(self):
        self.k = Ksiazka.objects.create(tytul='Lalka', autor='Prus', liczba_egzemplarzy=1)
        self.c = Czytelnik.objects.create(imie='Jan', nazwisko='Kowalski', email='j@k.pl', numer_karty='1')

    def wypozycz(self):
        return Wypozyczenie.objects.create(ksiazka=self.k, czytelnik=self.c)

    def test_termin_domyslnie_30_dni(self):
        self.assertEqual(self.wypozycz().termin_zwrotu, timezone.localdate() + timedelta(days=30))

    def test_dostepnosc_i_lista(self):
        self.assertEqual(self.k.ile_dostepnych(), 1)
        w = self.wypozycz()
        self.assertEqual(self.k.ile_dostepnych(), 0)
        r = self.client.get(reverse('lista'), {'q': 'lal'})
        self.assertEqual(r.context['ksiazki'][0].dostepne, 0)
        self.assertContains(r, 'disabled')
        self.client.post(reverse('zwroc', args=[w.pk]))
        self.assertEqual(self.k.ile_dostepnych(), 1)

    def test_formularz_odrzuca_brak_egzemplarzy(self):
        self.wypozycz()
        f = WypozyczenieForm({'ksiazka': self.k.pk, 'czytelnik': self.c.pk, 'termin_zwrotu': '2030-01-01'})
        self.assertFalse(f.is_valid())
        self.assertIn('ksiazka', f.errors)

    def test_po_terminie(self):
        w = self.wypozycz()
        w.termin_zwrotu = timezone.localdate() - timedelta(days=1)
        self.assertTrue(w.po_terminie)
        w.data_zwrotu = timezone.localdate()
        self.assertFalse(w.po_terminie)

    def test_zwroc_tylko_post(self):
        w = self.wypozycz()
        self.assertEqual(self.client.get(reverse('zwroc', args=[w.pk])).status_code, 405)

    def test_nie_usuwa_ksiazki_z_wypozyczeniem(self):
        self.wypozycz()
        self.client.post(reverse('usun', args=[self.k.pk]))
        self.assertTrue(Ksiazka.objects.filter(pk=self.k.pk).exists())

    def test_czytelnik_unikalny_email(self):
        r = self.client.post(reverse('czytelnik_dodaj'),
                             {'imie': 'A', 'nazwisko': 'B', 'email': 'j@k.pl', 'numer_karty': '2'})
        self.assertContains(r, 'text-danger')
