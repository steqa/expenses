import random
from datetime import datetime, timedelta, date, time
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Expense, Category, Limit
from .forms import ExpenseForm, CategoryForm


def home(request):
    _MONTHNAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    today = datetime.combine(date.today(), time(0, 0, 0))
    week = timedelta(minutes=60*24*7)
    expenses = Expense.objects.all()[0:5]
    categories = Category.objects.all()
    total_year = sum(i.price for i in Expense.objects.filter(
        created__year=today.year))
    total_month = sum(i.price for i in Expense.objects.filter(
        created__year=today.year, created__month=today.month))
    total_week = sum(i.price for i in Expense.objects.filter(
        created__gte=today - week, created__lte=today))
    total_day = sum(i.price for i in Expense.objects.filter(
        created__year=today.year, created__month=today.month, created__day=today.day))
    last_year = sum(i.price for i in Expense.objects.filter(
        created__year=today.year - 1))
    last_month = sum(i.price for i in Expense.objects.filter(
        created__year=today.year, created__month=today.month - 1))
    last_week = sum(i.price for i in Expense.objects.filter(
        created__gte=today - week - week, created__lte=today - week))
    last_day = sum(i.price for i in Expense.objects.filter(
        created__year=today.year, created__month=today.month, created__day=today.day - 1))
    percent_last_year = _get_percent_last(
        now=total_year, last=last_year)
    percent_last_month = _get_percent_last(
        now=total_month, last=last_month)
    percent_last_week = _get_percent_last(
        now=total_week, last=last_week)
    percent_last_day = _get_percent_last(
        now=total_day, last=last_day)
    categories_percent = _get_categories_percent(
        expenses=Expense.objects.all(), categories=categories)
    expenses_data = []
    for m in range(1, 13):
        expenses_data.append(float(sum(e.price for e in Expense.objects.filter(created__year=today.year, created__month=m))))
    
    try:
        limit = Limit.objects.get(user=request.user)
        limit_percent = (total_month * 100) / limit.number
        limit_progress = limit.number - total_month
        if limit_progress >= 0:
            before_limit = True
        else:
            limit_progress = limit_progress * -1
            before_limit = False

    except:
        limit = False
        limit_percent = False
        limit_progress = False
        before_limit = False
    
    
    
    context = {
        'form': ExpenseForm(),
        'expenses': expenses,
        'categories': categories,
        'categories_percent': categories_percent,
        'total_year': total_year,
        'total_month': total_month,
        'total_week': total_week,
        'total_day': total_day,
        'percent_last_year': percent_last_year,
        'percent_last_month': percent_last_month,
        'percent_last_week': percent_last_week,
        'percent_last_day': percent_last_day,
        'expenses_data': expenses_data,
        'months': _MONTHNAMES,
        'chart_year': today.year,
        'limit': limit,
        'limit_percent': limit_percent,
        'limit_progress': limit_progress,
        'before_limit': before_limit,
    }
    return render(request, 'expenses/home.html', context)


def chart_year_change(request, action):
    _MONTHNAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    chart_year = int(request.GET.get('chart_year'))
    if action == 'previous':
        chart_year -= 1
    elif action == 'next':
        chart_year += 1
        
    e = []
    for m in range(1, 13):
        e.append(float(sum(e.price for e in Expense.objects.filter(created__year=chart_year, created__month=m))))
        
    if e != [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
        expenses_data = e
    else:
        chart_year = request.GET.get('chart_year')
        
    print(expenses_data)
    context = {
        'expenses_data': expenses_data,
        'months': _MONTHNAMES,
        'chart_year': chart_year,
    }
    return render(request, 'expenses/expense-chart.html', context)


def expenses_date_filter(request, period, action):
    year, month, day, week_start, week_end = '', '', '', '', ''

    _YEARS = [2020, 2021, 2022]
    _MONTHNAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    today = datetime.combine(date.today(), time(0, 0, 0))
    week = timedelta(minutes=60*24*7)
    categories = Category.objects.all()

    q = request.GET.get('q') if request.GET.get('q') is not None else ''

    if period == 'year':
        year = today.year
        expenses = Expense.objects.filter(created__year=year)
    elif period == 'month':
        month = today.month
        year = today.year
        expenses = Expense.objects.filter(
            created__month=month, created__year=year)
        month = _MONTHNAMES[month - 1]
    elif period == 'week':
        week_start = today - week
        week_end = today
        expenses = Expense.objects.filter(created__gte=week_start)
    elif period == 'day':
        day = today.day
        month = today.month
        year = today.year
        expenses = Expense.objects.filter(created__day=day,
            created__month=month, created__year=year)
        day = f'0{day}' if len(str(day)) == 1 else day
        month = _MONTHNAMES[month - 1]

    if action != 'show':
        htmx = True
        if period == 'year':
            year = int(request.GET.get('year'))
            if action == 'previous':
                if year > _YEARS[0]:
                    year -= 1
            elif action == 'next':
                if year < _YEARS[-1]:
                    year += 1

            expenses = Expense.objects.filter(created__year=year, name__iregex=q)
            year = year
        elif period == 'month':
            month = int(_MONTHNAMES.index(request.GET.get('month'))) + 1
            year = int(request.GET.get('year'))
            if action == 'previous':
                if year == _YEARS[0] and month == 1:
                    pass
                else:
                    month -= 1
                    if month == 0:
                        year -= 1
            elif action == 'next':
                if year == _YEARS[-1] and month == 12:
                    pass
                else:
                    if month == 12:
                        month = 1
                        year += 1
                    else:
                        month += 1

            expenses = Expense.objects.filter(
                created__month=month, created__year=year, name__iregex=q)
            month = _MONTHNAMES[month - 1]
            year = year
        elif period == 'week':
            week_start = request.GET.get('week_start')
            week_end = request.GET.get('week_end')

            week_start_year = int(week_start.rstrip(', midnight')[-4:])
            week_start_month = int(_MONTHNAMES.index(week_start[:3])) + 1
            week_start_day = int(week_start.split()[1].rstrip(','))
            week_start = datetime(
                week_start_year, week_start_month, week_start_day)

            week_end_year = int(week_end.rstrip(', midnight')[-4:])
            week_end_month = int(_MONTHNAMES.index(week_end[:3])) + 1
            week_end_day = int(week_end.split()[1].rstrip(','))
            week_end = datetime(week_end_year, week_end_month, week_end_day)

            if action == 'previous':
                week_start = week_start - week
                week_end = week_end - week
                if week_start.year < _YEARS[0]:
                    week_start = week_start + week
                    week_end = week_end + week
            elif action == 'next':
                if week_end < today:
                    week_start = week_start + week
                    week_end = week_end + week

            expenses = Expense.objects.filter(
                created__gte=week_start, created__lte=week_end, name__iregex=q)
        elif period == 'day':
            day = int(request.GET.get('day'))
            month = int(_MONTHNAMES.index(request.GET.get('month'))) + 1
            year = int(request.GET.get('year'))
            if action == 'previous':
                if day > 1:
                    day -= 1
            elif action == 'next':
                try:
                    datetime(year, month, day + 1)
                    day += 1
                except:
                    day = day

            expenses = Expense.objects.filter(created__day=day,
                created__month=month, created__year=year, name__iregex=q)
            day = f'0{day}' if len(str(day)) == 1 else day
            month = _MONTHNAMES[month - 1]
    else:
        htmx = False

    paginator = Paginator(expenses, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'expenses': page_obj,
        'categories': categories,
        'expenses_length': len(expenses),
        'period': period,
        'year': year,
        'month': month,
        'day': day,
        'week_start': week_start,
        'week_end': week_end,
        'years': _YEARS,
        'months': _MONTHNAMES,
    }

    if request.GET.get('load-more') == 'True' or action == 'search':
        return render(request, 'expenses/expenses-card-rows.html', context)

    if htmx == True:
        return render(request, 'expenses/expenses-card.html', context)
    else:
        return render(request, 'expenses/total-period.html', context)


def add_expense(request):
    today = datetime.combine(date.today(), time(0, 0, 0))
    form = ExpenseForm()
    categories = Category.objects.all()
    expenses = Expense.objects.filter(
        Q(created__year=today.year, created__month=today.month, created__day=today.day - 1) |
        Q(created__year=today.year, created__month=today.month, created__day=today.day)
    )
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save()
            expense.user = request.user
            expense.save()
            messages.add_message(request, messages.SUCCESS, 'Expense added!')
            return redirect('add-expense')

    context = {
        'recently_add': True,
        'form': form,
        'expenses': expenses,
        'categories': categories,
    }
    return render(request, 'expenses/add-expense.html', context)


def add_category(request):
    today = datetime.combine(date.today(), time(0, 0, 0))
    form = CategoryForm()
    categories = Category.objects.all()
    recently_categories = Category.objects.filter(
        Q(created__year=today.year, created__month=today.month, created__day=today.day - 1) |
        Q(created__year=today.year, created__month=today.month, created__day=today.day)
    )
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            category.user = request.user
            category.save()
            messages.add_message(request, messages.SUCCESS, 'Category added!')
            return redirect('add-category')
        else:
            print('ERROR')
    
    context = {
        'form': form,
        'categories': categories,
        'recently_categories': recently_categories,
    }
    return render(request, 'expenses/add-category.html', context)


def update_expense(request, pk):
    expense = Expense.objects.get(pk=pk)
    name = request.POST.get('name')
    price = request.POST.get('price')
    
    if _expense_validator(request, name=name, price=price):
        expense.name = name
        expense.price = price
        expense.category.clear()
        for pk in request.POST.getlist('category'):
            expense.category.add(Category.objects.get(pk=pk))
            
        expense.save()
        messages.add_message(request, messages.SUCCESS, 'Expense updated!')
        
    return redirect(request.META.get('HTTP_REFERER'))


def update_category(request, pk):
    category = Category.objects.get(pk=pk)
    name = request.POST.get('name')
    color = request.POST.get('color')
    if _category_validator(request, name=name):
        category.name = name
        category.color = color
        category.save()
        messages.add_message(request, messages.SUCCESS, 'Category updated!')
    
    return redirect(request.META.get('HTTP_REFERER'))
    

def delete_expense(request, pk):
    expense = Expense.objects.get(pk=pk)
    expense.delete()
    messages.add_message(request, messages.SUCCESS, 'Expense deleted!')
    return redirect(request.META.get('HTTP_REFERER'))


def delete_category(request, pk):
    category = Category.objects.get(pk=pk)
    category.delete()
    messages.add_message(request, messages.SUCCESS, 'Category deleted!')
    return redirect(request.META.get('HTTP_REFERER'))
    

def set_limit(request):
    number = request.POST.get('number')
    try:
        limit = Limit.objects.get(user=request.user)
        limit.number = number
        limit.save()
    except:
        Limit.objects.create(user=request.user, number=number)
        
    return redirect('home')    


def dashboard(request):
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        categories = Category.objects.all()
        words = ['phone', 'notebook', 'pen', 'beautiful', 'big', 'small', 'simple', 'mouse', 'keyboard', 'milk', 'chocolate', 'shirt',
                 'bucket', 'cheese', 'tea', 'coffee', 'car', 'wheel', 'backpack', 'adidas', 'nike', 'off-white', 'supreme', 'cable', 'lamp', 'chair']
        for q in range(int(quantity)):
            expense = Expense.objects.create(
                user=request.user,
                name=' '.join(random.choice(words)
                              for i in range(random.randint(1, 7))).capitalize(),
                price=random.randint(200, 2500),
            )
            for i in range(random.randint(1, 4)):
                expense.category.add(random.choice(categories))

    return render(request, 'expenses/dashboard.html')


def _get_percent_last(now, last):
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
            print(i)
            sum += i.price
        if sum > 0:
            categories_percent[category.name] = sum / all_sum * 100
        else:
            categories_percent[category.name] = 0

    return categories_percent


def _expense_validator(request, name, price):
    valid = False
    if len(name) == 0:
        messages.add_message(request, messages.ERROR, 'The name must contain at least 1 character!')
    elif len(name) > 100:
        messages.add_message(request, messages.ERROR, 'The name must be less than 100 characters!')
    elif float(price) < 0.01:
        messages.add_message(request, messages.ERROR, 'The price should be more than $0.01!')
    elif float(price) > 9999999999.99:
        messages.add_message(request, messages.ERROR, 'The price should be less than $9999999999.99!')
    else:
        valid = True
        
    return valid


def _category_validator(request, name):
    valid = False
    if len(name) == 0:
        messages.add_message(request, messages.ERROR, 'The name must contain at least 1 character!')
    elif len(name) > 100:
        messages.add_message(request, messages.ERROR, 'The name must be less than 100 characters!')
    else:
        valid = True
        
    return valid