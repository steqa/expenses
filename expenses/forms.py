import random
from django import forms
from django.forms import ModelForm
from .models import Expense, Category


class ExpenseForm(ModelForm):
    class Meta:
        model = Expense
        fields = '__all__'


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'