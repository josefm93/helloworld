# pages/urls.py
from django.urls import path, include
from .views import homePageView, aboutPageView, namePageView, homePost, results, todos, register, message, secretArea\
    , predictionsPageView, predictions_post, scores

urlpatterns = [
    path('', homePageView, name='home'),
    path('about/', aboutPageView, name='about'),
    path('josef/', namePageView, name='josef'),
    path('homePost/', homePost, name='homePost'),
    path('results/', results, name='results'),
    path('todos', todos, name='todos'),
    path("register/", register, name="register"),
    path('message/<str:msg>/<str:title>/', message, name="message"),
    path('', include("django.contrib.auth.urls")),
    path("secret/", secretArea, name="secret"),
    path("predictions/", predictionsPageView, name="predictions"),
    path("predictions_post/", predictions_post, name="predictions_post"),
    path("scores/", scores, name="scores"),
]
