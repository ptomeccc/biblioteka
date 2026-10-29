from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import KsiazkaForm
from .models import Ksiazka

# Create your views here.
def lista(request):
    ksiazki = Ksiazka.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        ksiazki = ksiazki.filter(Q(tytul__icontains=q) | Q(autor__icontains=q) | Q(isbn__icontains=q))
    return render(request, 'ksiazki/lista.html', {'ksiazki': ksiazki, 'q': q})


def dodaj(request):
    form = KsiazkaForm(request.POST or None)
    if form.is_valid():
        ksiazka = form.save()
        messages.success(request, f'Dodano książkę „{ksiazka.tytul}”.')
        return redirect('lista')
    return render(request, 'ksiazki/formularz.html', {'form': form, 'naglowek': 'Dodaj książkę'})


def edytuj(request, pk):
    ksiazka = get_object_or_404(Ksiazka, pk=pk)
    form = KsiazkaForm(request.POST or None, instance=ksiazka)
    if form.is_valid():
        form.save()
        messages.success(request, f'Zapisano zmiany w „{ksiazka.tytul}”.')
        return redirect('lista')
    return render(request, 'ksiazki/formularz.html', {'form': form, 'naglowek': 'Edytuj książkę'})


def usun(request, pk):
    ksiazka = get_object_or_404(Ksiazka, pk=pk)
    if request.method == 'POST':
        ksiazka.delete()
        messages.success(request, f'Usunięto książkę „{ksiazka.tytul}”.')
        return redirect('lista')
    return render(request, 'ksiazki/usun.html', {'ksiazka': ksiazka})
