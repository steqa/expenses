from calendar import month
from datetime import datetime, timedelta, date, time
from tkinter import N
from django.shortcuts import render
from django.db.models import Q
from .models import Expense, Category


def home(request):
    expenses = Expense.objects.all()
    categories = Category.objects.all()

    categories_percent = _get_categories_percent(
        expenses=expenses, categories=categories)

    context = {
        'expenses': expenses,
        'categories': categories,
        'categories_percent': categories_percent,
        'period': 'all',
    }
    return render(request, 'expenses/home.html', context)


def _expenses_date_filter(request, period):
    filter_date, filter_date_2 = None, None
    
    _MONTHNAMES = [None, "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    day_now = date.today()
    time_null = time(0, 0, 0)
    today = datetime.combine(day_now, time_null)
    week = timedelta(minutes=60*24*7)
    today.year
    today.month

    if period == 'previous':
        period_now = request.GET.get('period_now')
        if period_now == 'week':
            pass
            # week_day = str(filter_date)[8:10]
            # week_month = str(filter_date)[5:7] if int(str(filter_date)[5]) != 0 else str(filter_date)[6:7]
            # week_year = str(filter_date)[0:4]
            # print(f'{week_day} {week_month} {week_year}')

    if period == 'all':
        expenses = Expense.objects.all()
    elif period == 'year':
        expenses = Expense.objects.filter(created__year=today.year)
        filter_date = today.year
    elif period == 'month':
        expenses = Expense.objects.filter(created__month=today.month)
        filter_date = _MONTHNAMES[today.month]
    elif period == 'week':
        expenses = Expense.objects.filter(created__gte=today-week)
        filter_date = today - week
        print('-----')
        print(filter_date)
        filter_date_2 = today
        
    if filter_date is None:
        filter_date = ''
    if filter_date_2 is None:
        filter_date_2 = ''

    context = {
        # 'expenses': expenses,
        'period': period,
        'filter_date': filter_date,
        'filter_date_2': filter_date_2,
    }
    return render(request, 'expenses/expenses-card.html', context)


def _previous_date_period(request):
    _MONTHNAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    day_now = date.today()
    time_null = time(0, 0, 0)
    today = datetime.combine(day_now, time_null)
    period = request.GET.get('period')
    show_date = request.GET.get('show_date')
    show_date_2 = request.GET.get('show_date_2')
    if period == 'year':
        show_date = str(int(show_date) - 1)
        expenses = Expense.objects.filter(created__year=show_date)
    elif period == 'month':
        show_date = _MONTHNAMES.index(show_date) - 1
        expenses = Expense.objects.filter(Q(created__month=show_date), Q(created__year=today.year))
        show_date = _MONTHNAMES[show_date]
    elif period == 'week':
        month_1 = _MONTHNAMES.index(show_date[:3]) + 1
        print(month_1)
        print(show_date)
        print(show_date_2)
        
    if show_date is None:
        show_date = ''
    if show_date_2 is None:
        show_date_2 = ''
        
    context = {
        # 'expenses': expenses,
        'period': period,
        'show_date': show_date,
    }
    return render(request, 'expenses/expenses-card.html', context)


def _get_categories_percent(expenses, categories):
    categories_percent = dict()
    all_sum = 0
    for e in expenses:
        all_sum += e.price

    for category in categories:
        sum = 0
        for i in category.category.all():
            sum += i.price
        if sum > 0:
            categories_percent[category.name] = sum / all_sum * 100

    return categories_percent


def dashboard(request):
    return render(request, 'expenses/dashboard.html')
