from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import WypozyczenieForm
from .models import Czytelnik, Ksiazka, Wypozyczenie


class WypozyczeniaTest(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_user('u', password='p'))
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

    def test_blokada_wypozyczenia_przez_widok(self):
        self.wypozycz()
        r = self.client.post(reverse('wypozycz'),
                             {'ksiazka': self.k.pk, 'czytelnik': self.c.pk, 'termin_zwrotu': '2030-01-01'})
        self.assertContains(r, 'Brak wolnych egzemplarzy')
        self.assertEqual(Wypozyczenie.objects.count(), 1)

    def test_szczegoly_czytelnika_z_historia(self):
        w = self.wypozycz()
        w.data_zwrotu = timezone.localdate()
        w.save()
        r = self.client.get(reverse('czytelnik_szczegoly', args=[self.c.pk]))
        self.assertContains(r, 'Lalka')
        self.assertEqual(len(r.context['historia']), 1)


class DostepTest(TestCase):
    ADRESY = ['dodaj', 'czytelnicy', 'wypozyczenia', 'wypozycz']

    def test_gosc_widzi_liste_ale_nie_formularze(self):
        self.assertEqual(self.client.get(reverse('lista')).status_code, 200)
        for nazwa in self.ADRESY:
            r = self.client.get(reverse(nazwa))
            self.assertRedirects(r, f"{reverse('admin:login')}?next={reverse(nazwa)}", fetch_redirect_response=False)

    def test_gosc_nie_edytuje_ani_nie_usuwa(self):
        k = Ksiazka.objects.create(tytul='A', autor='B')
        for nazwa in ('edytuj', 'usun'):
            self.assertEqual(self.client.get(reverse(nazwa, args=[k.pk])).status_code, 302)
        self.client.post(reverse('usun', args=[k.pk]))
        self.assertTrue(Ksiazka.objects.filter(pk=k.pk).exists())

    def test_dodawanie_ksiazki_przez_zalogowanego(self):
        self.client.force_login(User.objects.create_user('u', password='p'))
        r = self.client.post(reverse('dodaj'), {'tytul': 'Nowa', 'autor': 'Autor', 'isbn': '', 'liczba_egzemplarzy': 2})
        self.assertRedirects(r, reverse('lista'))
        self.assertTrue(Ksiazka.objects.filter(tytul='Nowa', isbn=None).exists())

    def test_dodawanie_bez_tytulu_pokazuje_blad(self):
        self.client.force_login(User.objects.create_user('u', password='p'))
        r = self.client.post(reverse('dodaj'), {'tytul': '', 'autor': 'A', 'liczba_egzemplarzy': 1})
        self.assertContains(r, 'To pole jest wymagane')
        self.assertEqual(Ksiazka.objects.count(), 0)


class ListaTest(TestCase):
    def test_paginacja_10_na_strone(self):
        for i in range(11):
            Ksiazka.objects.create(tytul=f'K{i:02}', autor='A')
        r = self.client.get(reverse('lista'))
        self.assertEqual(len(r.context['ksiazki']), 10)
        self.assertContains(r, 'pagination')
        self.assertEqual(len(self.client.get(reverse('lista'), {'page': 2}).context['ksiazki']), 1)
        self.assertEqual(self.client.get(reverse('lista'), {'page': 'abc'}).status_code, 200)

    def test_sortowanie_po_roku_z_pustymi_na_koncu(self):
        Ksiazka.objects.create(tytul='Bez', autor='A', rok_wydania=None)
        Ksiazka.objects.create(tytul='Stara', autor='A', rok_wydania=1900)
        Ksiazka.objects.create(tytul='Nowa', autor='A', rok_wydania=2000)
        for sort, oczekiwane in (('rok', ['Stara', 'Nowa', 'Bez']), ('-rok', ['Nowa', 'Stara', 'Bez'])):
            r = self.client.get(reverse('lista'), {'sort': sort})
            self.assertEqual([k.tytul for k in r.context['ksiazki']], oczekiwane)

    def test_nieznane_pole_sortowania_nie_psuje_strony(self):
        self.assertEqual(self.client.get(reverse('lista'), {'sort': 'dodano; drop'}).status_code, 200)
