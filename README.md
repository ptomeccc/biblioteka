# Biblioteka

Aplikacja Django do zarządzania książkami, czytelnikami i wypożyczeniami (Django 4.2, Bootstrap 5, interfejs po polsku).

## Zrealizowane funkcje

- Książki: lista, dodawanie, edycja, usuwanie (ze stroną potwierdzenia), unikalny opcjonalny ISBN
- Wyszukiwarka po tytule, autorze i ISBN (bez rozróżniania wielkości liter)
- Paginacja (10 na stronę) i sortowanie po kliknięciu nagłówka: tytuł, autor, rok
- Czytelnicy: CRUD, unikalny e-mail i numer karty, strona szczegółów z historią wypożyczeń
- Wypożyczenia: termin zwrotu domyślnie +30 dni, zwrot przyciskiem (POST), podświetlenie przeterminowanych
- Kolumna „Dostępne” (egzemplarze minus aktywne wypożyczenia, jedno zapytanie) i blokada wypożyczenia przy braku egzemplarzy
- Logowanie: dodawanie, edycja i usuwanie oraz widoki czytelników i wypożyczeń tylko dla zalogowanych; lista książek publiczna
- Panel admina: edycja liczby egzemplarzy z listy, filtry, wypożyczenia jako inline na stronie książki
- Testy automatyczne (19)

## Uruchomienie

```bash
python3 -m venv venv
source venv/bin/activate
pip install "Django>=4.2,<5"
python manage.py migrate
python manage.py createsuperuser   # konto z uprawnieniami staff służy do logowania
python manage.py runserver
```

Aplikacja: http://127.0.0.1:8000/, panel admina: http://127.0.0.1:8000/admin/.
Logowanie odbywa się przez `/admin/login/` (wymaga konta `is_staff`).

## Testy

```bash
python manage.py test
```

## Konfiguracja

`SECRET_KEY` jest czytany ze zmiennej środowiskowej `DJANGO_SECRET_KEY`. Gdy jej brak, tworzony jest lokalny plik `.secret_key` (poza gitem). Baza `db.sqlite3` także nie jest w repozytorium.
