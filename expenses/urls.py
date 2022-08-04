from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('expenses-date-filter/<str:period>/', views._expenses_date_filter, name='expenses-date-filter'),
    path('previous-date-period/', views._previous_date_period, name='previous-date-period'),
]
