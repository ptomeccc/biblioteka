from django.contrib import messages
from django.db.models import ProtectedError, Q
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


def lista(request):
    ksiazki = Ksiazka.objects.z_dostepnymi()
    q = request.GET.get('q', '').strip()
    if q:
        ksiazki = ksiazki.filter(Q(tytul__icontains=q) | Q(autor__icontains=q) | Q(isbn__icontains=q))
    return render(request, 'ksiazki/lista.html', {'ksiazki': ksiazki, 'q': q})


def dodaj(request):
    return _zapisz(request, KsiazkaForm, 'Dodaj książkę', 'Dodano książkę „{.tytul}”.', 'lista')


def edytuj(request, pk):
    return _zapisz(request, KsiazkaForm, 'Edytuj książkę', 'Zapisano zmiany w „{.tytul}”.', 'lista',
                   get_object_or_404(Ksiazka, pk=pk))


def usun(request, pk):
    return _usun(request, get_object_or_404(Ksiazka, pk=pk), 'lista')


def czytelnicy(request):
    return render(request, 'ksiazki/czytelnicy.html', {'czytelnicy': Czytelnik.objects.all()})


def czytelnik_dodaj(request):
    return _zapisz(request, CzytelnikForm, 'Dodaj czytelnika', 'Dodano czytelnika {}.', 'czytelnicy')


def czytelnik_edytuj(request, pk):
    return _zapisz(request, CzytelnikForm, 'Edytuj czytelnika', 'Zapisano zmiany: {}.', 'czytelnicy',
                   get_object_or_404(Czytelnik, pk=pk))


def czytelnik_usun(request, pk):
    return _usun(request, get_object_or_404(Czytelnik, pk=pk), 'czytelnicy')


def wypozycz(request, pk=None):
    form = WypozyczenieForm(request.POST or None, initial={'ksiazka': pk})
    if form.is_valid():
        w = form.save()
        messages.success(request, f'Wypożyczono „{w.ksiazka.tytul}” – {w.czytelnik}.')
        return redirect('wypozyczenia')
    return render(request, 'ksiazki/formularz.html', {'form': form, 'naglowek': 'Wypożycz książkę', 'powrot': 'lista'})


def wypozyczenia(request):
    aktywne = Wypozyczenie.objects.filter(data_zwrotu__isnull=True).select_related('ksiazka', 'czytelnik')
    return render(request, 'ksiazki/wypozyczenia.html', {'wypozyczenia': aktywne})


@require_POST
def zwroc(request, pk):
    w = get_object_or_404(Wypozyczenie, pk=pk, data_zwrotu__isnull=True)
    w.data_zwrotu = timezone.localdate()
    w.save(update_fields=['data_zwrotu'])
    messages.success(request, f'Zwrócono „{w.ksiazka.tytul}”.')
    return redirect('wypozyczenia')
