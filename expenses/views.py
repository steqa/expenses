from datetime import datetime, timedelta, date, time
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

    _MONTHNAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    today = datetime.combine(date.today(), time(0, 0, 0))
    week = timedelta(minutes=60*24*7)

    if period == 'all':
        expenses = Expense.objects.all()
    elif period == 'year':
        filter_date = today.year
        expenses = Expense.objects.filter(created__year=filter_date)
    elif period == 'month':
        filter_date = today.month
        filter_date_2 = today.year
        expenses = Expense.objects.filter(Q(created__month=filter_date), Q(created__year=filter_date_2))
        filter_date = _MONTHNAMES[filter_date - 1]
    elif period == 'week':
        filter_date = today - week
        filter_date_2 = today
        expenses = Expense.objects.filter(created__gte=filter_date)

    if period == 'previous' or period == 'next':
        period_now = request.GET.get('period_now')
        if period_now == 'year':
            filter_date = int(request.GET.get('filter_date'))
            if period == 'previous':
                filter_date -= 1
            elif period == 'next':
                filter_date += 1
                
            expenses = Expense.objects.filter(created__year=filter_date)
            period = period_now
        elif period_now == 'month':
            filter_date = int(_MONTHNAMES.index(request.GET.get('month'))) + 1
            filter_date_2 = int(request.GET.get('year'))
            if period == 'previous':
                filter_date -= 1
            elif period == 'next':
                if filter_date == 12:
                    filter_date = 1
                else:
                    filter_date += 1
            
            expenses = Expense.objects.filter(created__month=filter_date)
            period = period_now
            filter_date = _MONTHNAMES[filter_date - 1]
        elif period_now == 'week':
            week_start = request.GET.get('week_start')
            week_end = request.GET.get('week_end')
            
            week_start_year = int(week_start.rstrip(', midnight')[-4:])
            week_start_month = int(_MONTHNAMES.index(week_start[:3])) + 1
            week_start_day = int(week_start.split()[1].rstrip(','))
            week_start = datetime(week_start_year, week_start_month, week_start_day)
            
            week_end_year = int(week_end.rstrip(', midnight')[-4:])
            week_end_month = int(_MONTHNAMES.index(week_end[:3])) + 1
            week_end_day = int(week_end.split()[1].rstrip(','))
            week_end = datetime(week_end_year, week_end_month, week_end_day)
            
            if period == 'previous':
                filter_date = week_start - week
                filter_date_2 = week_end - week
            elif period == 'next':
                filter_date = week_start + week
                filter_date_2 = week_end + week
                
            expenses = Expense.objects.filter(Q(created__gte=filter_date), Q(created__lte=filter_date_2))
            period = period_now
        
    if filter_date is None:
        filter_date = ''
    if filter_date_2 is None:
        filter_date_2 = ''

    context = {
        'expenses': expenses,
        'period': period,
        'filter_date': filter_date,
        'filter_date_2': filter_date_2,
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
