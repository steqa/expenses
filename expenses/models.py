from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    color = models.CharField(max_length=7, default='#0d6efd')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['user', '-created']


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    category = models.ManyToManyField(
        Category, related_name='category', blank=True)
    color = models.CharField(max_length=7, default='#0d6efd')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['user', '-created']
