from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('expenses-filter/<str:period>/', views._expenses_filter, name='expenses-filter')
]
