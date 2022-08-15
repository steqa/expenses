from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-expense/', views.add_expense, name='add-expense'),
    path('add-category/', views.add_category, name='add-category'),
    path('update-expense/<int:pk>/', views.update_expense, name='update-expense'),
    path('update-category/<int:pk>/', views.update_category, name='update-category'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('total/<str:period>/<str:action>/', views.expenses_date_filter, name='expenses-date-filter'),
]
