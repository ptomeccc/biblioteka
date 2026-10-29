from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista, name='lista'),
    path('dodaj/', views.dodaj, name='dodaj'),
    path('<int:pk>/edytuj/', views.edytuj, name='edytuj'),
    path('<int:pk>/usun/', views.usun, name='usun'),
]
