from datetime import datetime, timedelta
from django.shortcuts import render
from .models import Expense, Category


def home(request):
    expenses = Expense.objects.all()
    categories = Category.objects.all()

    categories_percent = _get_categories_percent(
        expenses=expenses, categories=categories)
    
    print(categories_percent)
    for i in categories_percent:
        print(categories_percent[i])

    context = {
        'expenses': expenses,
        'categories': categories,
        'categories_percent': categories_percent,
    }
    return render(request, 'expenses/home.html', context)


def _expenses_filter(request, period):
    if period == 'month':
        now = datetime.now().month
        expenses = Expense.objects.filter(created__month=now)
    elif period == 'all':
        expenses = Expense.objects.all()
    elif period == 'week':
        now = datetime.now() - timedelta(minutes=60*24*7)
        print(now)
        expenses = Expense.objects.filter(created__gte=now)

    return render(request, 'expenses/expenses.html', {'expenses': expenses})


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
