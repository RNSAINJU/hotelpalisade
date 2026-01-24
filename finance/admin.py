from django.contrib import admin
from .models import Expense, Employee, SalaryPayment, SundryDebtor, SundryCreditor

admin.site.register(Expense)
admin.site.register(Employee)
admin.site.register(SalaryPayment)
admin.site.register(SundryDebtor)
admin.site.register(SundryCreditor)
