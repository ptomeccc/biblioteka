from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CzytelnikForm, KsiazkaForm, WypozyczenieForm
from .models import Czytelnik, Ksiazka, Wypozyczenie


def _zapisz(request, form_class, naglowek, komunikat, powrot, instance=None):
    form = form_class(request.POST or None, instance=instance)
    if form.is_valid():
        obiekt = form.save()
        messages.success(request, komunikat.format(obiekt))
        return redirect(powrot)
    return render(request, 'ksiazki/formularz.html', {'form': form, 'naglowek': naglowek, 'powrot': powrot})


def _usun(request, obiekt, powrot):
    if request.method == 'POST':
        try:
            obiekt.delete()
        except ProtectedError:
            messages.error(request, f'Nie można usunąć „{obiekt}” – ma powiązane wypożyczenia.')
        else:
            messages.success(request, f'Usunięto „{obiekt}”.')
        return redirect(powrot)
    return render(request, 'ksiazki/usun.html', {'obiekt': obiekt, 'powrot': powrot})


SORTOWANIE = {'tytul': ('Tytuł', 'tytul'), 'autor': ('Autor', 'autor'), 'rok': ('Rok', 'rok_wydania')}


def lista(request):
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'tytul')
    klucz, malejaco = sort.lstrip('-'), sort.startswith('-')
    if klucz not in SORTOWANIE:  # whitelist: nie przekazujemy GET do order_by
        klucz, malejaco = 'tytul', False

    ksiazki = Ksiazka.objects.z_dostepnymi()
    if q:
        ksiazki = ksiazki.filter(Q(tytul__icontains=q) | Q(autor__icontains=q) | Q(isbn__icontains=q))
    pole = F(SORTOWANIE[klucz][1])
    # nulls_last w obu kierunkach (rok bywa pusty), pk daje stabilny porządek między stronami
    ksiazki = ksiazki.order_by(pole.desc(nulls_last=True) if malejaco else pole.asc(nulls_last=True), 'pk')

    strona = Paginator(ksiazki, 10).get_page(request.GET.get('page'))
    kolumny = []
    for k, (etykieta, _) in SORTOWANIE.items():
        aktywna = k == klucz
        nastepny = '-' + k if aktywna and not malejaco else k
        kolumny.append({
            'etykieta': etykieta,
            'link': '?' + urlencode({'q': q, 'sort': nastepny}),
            'ikona': ('bi-sort-down' if malejaco else 'bi-sort-up') if aktywna else '',
        })
    return render(request, 'ksiazki/lista.html', {
        'ksiazki': strona, 'q': q, 'kolumny': kolumny,
        'sort': ('-' if malejaco else '') + klucz,
        'qs': urlencode({'q': q, 'sort': ('-' if malejaco else '') + klucz}),  # do linków paginacji
        'strony': list(strona.paginator.get_elided_page_range(strona.number)),
    })


@login_required
def dodaj(request):
    return _zapisz(request, KsiazkaForm, 'Dodaj książkę', 'Dodano książkę „{.tytul}”.', 'lista')


@login_required
def edytuj(request, pk):
    return _zapisz(request, KsiazkaForm, 'Edytuj książkę', 'Zapisano zmiany w „{.tytul}”.', 'lista',
                   get_object_or_404(Ksiazka, pk=pk))


@login_required
def usun(request, pk):
    return _usun(request, get_object_or_404(Ksiazka, pk=pk), 'lista')


@login_required
def czytelnicy(request):
    return render(request, 'ksiazki/czytelnicy.html', {'czytelnicy': Czytelnik.objects.all()})


@login_required
def czytelnik_szczegoly(request, pk):
    czytelnik = get_object_or_404(Czytelnik, pk=pk)
    historia = czytelnik.wypozyczenia.select_related('ksiazka').order_by('-data_wypozyczenia', '-pk')
    return render(request, 'ksiazki/czytelnik.html', {'czytelnik': czytelnik, 'historia': historia})


@login_required
def czytelnik_dodaj(request):
    return _zapisz(request, CzytelnikForm, 'Dodaj czytelnika', 'Dodano czytelnika {}.', 'czytelnicy')


@login_required
def czytelnik_edytuj(request, pk):
    return _zapisz(request, CzytelnikForm, 'Edytuj czytelnika', 'Zapisano zmiany: {}.', 'czytelnicy',
                   get_object_or_404(Czytelnik, pk=pk))


@login_required
def czytelnik_usun(request, pk):
    return _usun(request, get_object_or_404(Czytelnik, pk=pk), 'czytelnicy')


@login_required
def wypozycz(request, pk=None):
    form = WypozyczenieForm(request.POST or None, initial={'ksiazka': pk})
    if form.is_valid():
        w = form.save()
        messages.success(request, f'Wypożyczono „{w.ksiazka.tytul}” – {w.czytelnik}.')
        return redirect('wypozyczenia')
    return render(request, 'ksiazki/formularz.html', {'form': form, 'naglowek': 'Wypożycz książkę', 'powrot': 'lista'})


@login_required
def wypozyczenia(request):
    aktywne = Wypozyczenie.objects.filter(data_zwrotu__isnull=True).select_related('ksiazka', 'czytelnik')
    return render(request, 'ksiazki/wypozyczenia.html', {'wypozyczenia': aktywne})


@login_required
@require_POST
def zwroc(request, pk):
    w = get_object_or_404(Wypozyczenie, pk=pk, data_zwrotu__isnull=True)
    w.data_zwrotu = timezone.localdate()
    w.save(update_fields=['data_zwrotu'])
    messages.success(request, f'Zwrócono „{w.ksiazka.tytul}”.')
    return redirect('wypozyczenia')
