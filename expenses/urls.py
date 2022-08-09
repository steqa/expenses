from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('total/<str:period>/<str:action>/', views.expenses_date_filter, name='expenses-date-filter'),
]
