from django.urls import path
from . import views

urlpatterns = [
    # Balance Sheet URL
    path('balance-sheet/', views.balance_sheet, name='balance_sheet'),
    
    # Expense URLs
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/update/', views.expense_update, name='expense_update'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    # Employee URLs
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/update/', views.employee_update, name='employee_update'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    
    # Salary Payment URLs
    path('salary-payments/', views.salary_payment_list, name='salary_payment_list'),
    path('salary-payments/create/', views.salary_payment_create, name='salary_payment_create'),
    path('salary-payments/<int:pk>/delete/', views.salary_payment_delete, name='salary_payment_delete'),
    
    # Sundry Debtor URLs
    path('debtors/', views.debtor_list, name='debtor_list'),
    path('debtors/create/', views.debtor_create, name='debtor_create'),
    path('debtors/<int:pk>/update/', views.debtor_update, name='debtor_update'),
    path('debtors/<int:pk>/delete/', views.debtor_delete, name='debtor_delete'),
    
    # Sundry Creditor URLs
    path('creditors/', views.creditor_list, name='creditor_list'),
    path('creditors/create/', views.creditor_create, name='creditor_create'),
    path('creditors/<int:pk>/update/', views.creditor_update, name='creditor_update'),
    path('creditors/<int:pk>/delete/', views.creditor_delete, name='creditor_delete'),
]
