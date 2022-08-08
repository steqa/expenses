from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('expenses-date-filter/<str:period>/', views.expenses_date_filter, name='expenses-date-filter'),
    path('load-more/', views.load_more, name='load-more')
]
