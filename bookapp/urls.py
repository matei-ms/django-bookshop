from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("despre", views.despre, name="despre"),
    path("carti", views.in_lucru, name="carti"),
    path("autori", views.in_lucru, name="autori"),
    path("contact/", views.contact, name="contact"),
    path("info", views.info, name="info"),
    path("log", views.log, name="log"),
    path("simplu", views.simplu, name="simplu"),    
    path("produse", views.produse, name="produse"),
    path("produse/adauga", views.adauga_editie, name="adauga_editie"),
    path("produse/<str:isbn>", views.produs_detaliu, name="produs_detaliu"),
    path("categorii/<str:nume_gen>", views.categorie, name="categorie"),
    path("cos", views.in_lucru, name="cos"),
    path("recomandare", views.in_lucru, name="recomandare"),
    path("secret", views.in_lucru, name="secret"),
    path("interzis", views.interzis, name="interzis"),
]