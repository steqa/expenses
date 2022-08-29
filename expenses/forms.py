from django.forms import ModelForm
from .models import Expense, Category


class ExpenseForm(ModelForm):
    class Meta:
        model = Expense
        fields = ['name', 'price', 'category']


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color']