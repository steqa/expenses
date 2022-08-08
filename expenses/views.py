from datetime import datetime, timedelta, date, time
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
from .models import Expense, Category


def home(request):
    today = datetime.combine(date.today(), time(0, 0, 0))
    week = timedelta(minutes=60*24*7)
    expenses = Expense.objects.all()[0:2]
    total_expenses = Expense.objects.count()
    categories = Category.objects.all()
    total_year = sum(i.price for i in Expense.objects.filter(created__year=today.year))
    total_month = sum(i.price for i in Expense.objects.filter(created__month=today.month))
    total_week = sum(i.price for i in Expense.objects.filter(created__gte=today-week))
    total_day = sum(i.price for i in Expense.objects.filter(created__day=today.day))
    last_year = sum(i.price for i in Expense.objects.filter(created__year=today.year - 1))
    last_month = sum(i.price for i in Expense.objects.filter(created__month=today.month - 1))
    last_week = sum(i.price for i in Expense.objects.filter(Q(created__gte=today - week - week), Q(created__lte= today - week)))
    last_day = sum(i.price for i in Expense.objects.filter(created__day=today.day - 1))
    percent_last_year = _get_percent_last_year(now=total_year, last=last_year)
    percent_last_month = _get_percent_last_year(now=total_month, last=last_month)
    percent_last_week = _get_percent_last_year(now=total_week, last=last_week)
    percent_last_day = _get_percent_last_year(now=total_day, last=last_day)
    categories_percent = _get_categories_percent(
        expenses=expenses, categories=categories)

    context = {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'categories': categories,
        'categories_percent': categories_percent,
        'period': 'all',
        'total_year': total_year,
        'total_month': total_month,
        'total_week': total_week,
        'total_day': total_day,
        'percent_last_year': percent_last_year,
        'percent_last_month': percent_last_month,
        'percent_last_week': percent_last_week,
        'percent_last_day': percent_last_day,
    }
    return render(request, 'expenses/home.html', context)


def expenses_date_filter(request, period):
    year, month, day, week_start, week_end = '', '', '', '', ''

    _MONTHNAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    today = datetime.combine(date.today(), time(0, 0, 0))
    week = timedelta(minutes=60*24*7)

    if period == 'all':
        expenses = Expense.objects.all()
    elif period == 'year':
        year = today.year
        expenses = Expense.objects.filter(created__year=year)
    elif period == 'month':
        month = today.month
        year = today.year
        expenses = Expense.objects.filter(Q(created__month=month), Q(created__year=year))
        month = _MONTHNAMES[month - 1]
    elif period == 'week':
        week_start = today - week
        week_end = today
        expenses = Expense.objects.filter(created__gte=week_start)
    elif period == 'day':
        day = today.day
        month = today.month
        year = today.year
        expenses = Expense.objects.filter(Q(created__day=day), Q(created__month=month), Q(created__year=year))
        day = f'0{day}' if len(str(day)) == 1 else day
        month = _MONTHNAMES[month - 1]

    if period == 'previous' or period == 'next':
        period_now = request.GET.get('period_now')
        if period_now == 'year':
            year = int(request.GET.get('year'))
            if period == 'previous':
                if year > 2020:
                    year -= 1
            elif period == 'next':
                if year < 2022:
                    year += 1
                
            expenses = Expense.objects.filter(created__year=year)
            period = period_now
            year = year
        elif period_now == 'month':
            month = int(_MONTHNAMES.index(request.GET.get('month'))) + 1
            year = int(request.GET.get('year'))
            if period == 'previous':
                if year == 2020 and month == 1:
                    pass
                else:
                    month -= 1
                    if month == 0:
                        year -= 1
            elif period == 'next':
                if year == 2022 and month == 12:
                    pass
                else:
                    if month == 12:
                        month = 1
                        year += 1
                    else:
                        month += 1
            
            expenses = Expense.objects.filter(Q(created__month=month), Q(created__year=year))
            period = period_now
            month = _MONTHNAMES[month - 1]
            year = year
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
                week_start = week_start - week
                week_end = week_end - week
                if week_start.year < 2020:
                    week_start = week_start + week
                    week_end = week_end + week
            elif period == 'next':
                if week_end < today:
                    week_start = week_start + week
                    week_end = week_end + week
                
            expenses = Expense.objects.filter(Q(created__gte=week_start), Q(created__lte=week_end))
            period = period_now
        elif period_now == 'day':
            day = int(request.GET.get('day'))
            month = int(_MONTHNAMES.index(request.GET.get('month'))) + 1
            year = int(request.GET.get('year'))
            if period == 'previous':
                if day > 1:
                    day -= 1
            elif period == 'next':
                try:
                    datetime(year, month, day + 1)
                    day += 1
                except:
                    day = day
                                
            expenses = Expense.objects.filter(Q(created__day=day), Q(created__month=month), Q(created__year=year))
            day = f'0{day}' if len(str(day)) == 1 else day
            month = _MONTHNAMES[month - 1]
            period = period_now
    
    context = {
        'expenses': expenses,
        'period': period,
        'year': year,
        'month': month,
        'day': day,
        'week_start': week_start,
        'week_end': week_end,
    }
    return render(request, 'expenses/expenses-card.html', context)


def _get_percent_last_year(now, last):
    percent_status = []
    if last == 0:
        percent_status.append(0)
        percent_status.append('Null')
        return percent_status
    else:
        if now >= last:
            percent_status.append((now - last) / last * 100)
            percent_status.append('Up')
            return percent_status
        else:
            percent_status.append((last - now) / last * 100)
            percent_status.append('Down')
            return percent_status


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


def load_more(request):
    total_item = int(request.GET.get('total_item'))
    limit = 2
    expense_obj = list(Expense.objects.values()[total_item:total_item+limit])
    data = {
        'expenses': expense_obj,
    }
    return JsonResponse(data=data)


def dashboard(request):
    return render(request, 'expenses/dashboard.html')
