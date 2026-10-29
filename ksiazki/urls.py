from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista, name='lista'),
    path('dodaj/', views.dodaj, name='dodaj'),
    path('<int:pk>/edytuj/', views.edytuj, name='edytuj'),
    path('<int:pk>/usun/', views.usun, name='usun'),
    path('<int:pk>/wypozycz/', views.wypozycz, name='wypozycz_ksiazke'),
    path('czytelnicy/', views.czytelnicy, name='czytelnicy'),
    path('czytelnicy/dodaj/', views.czytelnik_dodaj, name='czytelnik_dodaj'),
    path('czytelnicy/<int:pk>/edytuj/', views.czytelnik_edytuj, name='czytelnik_edytuj'),
    path('czytelnicy/<int:pk>/usun/', views.czytelnik_usun, name='czytelnik_usun'),
    path('wypozycz/', views.wypozycz, name='wypozycz'),
    path('wypozyczenia/', views.wypozyczenia, name='wypozyczenia'),
    path('wypozyczenia/<int:pk>/zwroc/', views.zwroc, name='zwroc'),
]
