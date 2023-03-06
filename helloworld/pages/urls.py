# pages/urls.py
from django.urls import path
from .views import homePageView, aboutPageView, namePageView, homePost, results

urlpatterns = [
    path('', homePageView, name='home'),
    path('about/', aboutPageView, name='about'),
    path('josef/', namePageView, name='josef'),
    path('homePost/', homePost, name='homePost'),
    path('results/<int:choice>/<str:gmat>/', results, name='results'),
]
