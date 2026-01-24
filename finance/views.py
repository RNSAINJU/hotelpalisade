from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, FloatField
from datetime import datetime
from .models import Expense, Employee, SalaryPayment, SundryDebtor, SundryCreditor


# Balance Sheet View
@login_required(login_url='login')
def balance_sheet(request):
    from inventory.models import InventoryItem
    from sales.models import SalesBill
    
    # ASSETS
    # Current Assets - Inventory
    inventory_value = float(InventoryItem.objects.aggregate(
        total=Sum(F('quantity') * F('price_per_unit'), output_field=FloatField())
    )['total'] or 0)
    
    # Current Assets - Cash (Total Sales)
    total_cash = float(SalesBill.objects.aggregate(total=Sum('total_amount'))['total'] or 0)
    
    # Current Assets - Sundry Debtors (Accounts Receivable)
    total_debtors = float(SundryDebtor.objects.filter(is_paid=False).aggregate(
        total=Sum('amount_due')
    )['total'] or 0)
    
    total_assets = inventory_value + total_cash + total_debtors
    
    # LIABILITIES
    # Current Liabilities - Sundry Creditors (Accounts Payable)
    total_creditors = float(SundryCreditor.objects.filter(is_paid=False).aggregate(
        total=Sum('amount_payable')
    )['total'] or 0)
    
    # Current Liabilities - Expenses
    total_expenses = float(Expense.objects.aggregate(total=Sum('amount'))['total'] or 0)
    
    # Current Liabilities - Salary Payments
    total_salaries_paid = float(SalaryPayment.objects.aggregate(total=Sum('amount'))['total'] or 0)
    
    total_liabilities = total_creditors + total_expenses + total_salaries_paid
    
    # EQUITY (Assets - Liabilities)
    total_equity = total_assets - total_liabilities
    
    context = {
        'inventory_value': inventory_value,
        'total_cash': total_cash,
        'total_debtors': total_debtors,
        'total_assets': total_assets,
        'total_creditors': total_creditors,
        'total_expenses': total_expenses,
        'total_salaries_paid': total_salaries_paid,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'current_date': datetime.now().strftime('%B %d, %Y'),
    }
    return render(request, 'finance/balance_sheet.html', context)


# Expense Views
@login_required(login_url='login')
def expense_list(request):
    expenses = Expense.objects.all()
    return render(request, 'finance/expenses/list.html', {'expenses': expenses})


@login_required(login_url='login')
def expense_create(request):
    if request.method == 'POST':
        Expense.objects.create(
            title=request.POST['title'],
            description=request.POST.get('description', ''),
            amount=request.POST['amount'],
            category=request.POST['category'],
            date=request.POST['date']
        )
        return redirect('expense_list')
    return render(request, 'finance/expenses/create.html')


@login_required(login_url='login')
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.title = request.POST['title']
        expense.description = request.POST.get('description', '')
        expense.amount = request.POST['amount']
        expense.category = request.POST['category']
        expense.date = request.POST['date']
        expense.save()
        return redirect('expense_list')
    return render(request, 'finance/expenses/update.html', {'expense': expense})


@login_required(login_url='login')
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    return render(request, 'finance/expenses/delete.html', {'expense': expense})


# Employee Views
@login_required(login_url='login')
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'finance/employees/list.html', {'employees': employees})


@login_required(login_url='login')
def employee_create(request):
    if request.method == 'POST':
        Employee.objects.create(
            name=request.POST['name'],
            position=request.POST['position'],
            phone=request.POST['phone'],
            email=request.POST.get('email', ''),
            address=request.POST['address'],
            monthly_salary=request.POST['monthly_salary'],
            date_joined=request.POST['date_joined'],
            is_active=request.POST.get('is_active') == 'on'
        )
        return redirect('employee_list')
    return render(request, 'finance/employees/create.html')


@login_required(login_url='login')
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.name = request.POST['name']
        employee.position = request.POST['position']
        employee.phone = request.POST['phone']
        employee.email = request.POST.get('email', '')
        employee.address = request.POST['address']
        employee.monthly_salary = request.POST['monthly_salary']
        employee.date_joined = request.POST['date_joined']
        employee.is_active = request.POST.get('is_active') == 'on'
        employee.save()
        return redirect('employee_list')
    return render(request, 'finance/employees/update.html', {'employee': employee})


@login_required(login_url='login')
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    return render(request, 'finance/employees/delete.html', {'employee': employee})


# Salary Payment Views
@login_required(login_url='login')
def salary_payment_list(request):
    payments = SalaryPayment.objects.all()
    return render(request, 'finance/salary_payments/list.html', {'payments': payments})


@login_required(login_url='login')
def salary_payment_create(request):
    if request.method == 'POST':
        SalaryPayment.objects.create(
            employee_id=request.POST['employee'],
            amount=request.POST['amount'],
            payment_date=request.POST['payment_date'],
            month=request.POST['month'],
            notes=request.POST.get('notes', '')
        )
        return redirect('salary_payment_list')
    employees = Employee.objects.filter(is_active=True)
    return render(request, 'finance/salary_payments/create.html', {'employees': employees})


@login_required(login_url='login')
def salary_payment_delete(request, pk):
    payment = get_object_or_404(SalaryPayment, pk=pk)
    if request.method == 'POST':
        payment.delete()
        return redirect('salary_payment_list')
    return render(request, 'finance/salary_payments/delete.html', {'payment': payment})


# Sundry Debtor Views
@login_required(login_url='login')
def debtor_list(request):
    debtors = SundryDebtor.objects.all()
    return render(request, 'finance/debtors/list.html', {'debtors': debtors})


@login_required(login_url='login')
def debtor_create(request):
    if request.method == 'POST':
        SundryDebtor.objects.create(
            name=request.POST['name'],
            contact=request.POST['contact'],
            email=request.POST.get('email', ''),
            amount_due=request.POST['amount_due'],
            due_date=request.POST['due_date'],
            description=request.POST.get('description', ''),
            is_paid=request.POST.get('is_paid') == 'on',
            payment_date=request.POST.get('payment_date') if request.POST.get('is_paid') == 'on' else None
        )
        return redirect('debtor_list')
    return render(request, 'finance/debtors/create.html')


@login_required(login_url='login')
def debtor_update(request, pk):
    debtor = get_object_or_404(SundryDebtor, pk=pk)
    if request.method == 'POST':
        debtor.name = request.POST['name']
        debtor.contact = request.POST['contact']
        debtor.email = request.POST.get('email', '')
        debtor.amount_due = request.POST['amount_due']
        debtor.due_date = request.POST['due_date']
        debtor.description = request.POST.get('description', '')
        debtor.is_paid = request.POST.get('is_paid') == 'on'
        debtor.payment_date = request.POST.get('payment_date') if request.POST.get('is_paid') == 'on' else None
        debtor.save()
        return redirect('debtor_list')
    return render(request, 'finance/debtors/update.html', {'debtor': debtor})


@login_required(login_url='login')
def debtor_delete(request, pk):
    debtor = get_object_or_404(SundryDebtor, pk=pk)
    if request.method == 'POST':
        debtor.delete()
        return redirect('debtor_list')
    return render(request, 'finance/debtors/delete.html', {'debtor': debtor})


# Sundry Creditor Views
@login_required(login_url='login')
def creditor_list(request):
    creditors = SundryCreditor.objects.all()
    return render(request, 'finance/creditors/list.html', {'creditors': creditors})


@login_required(login_url='login')
def creditor_create(request):
    if request.method == 'POST':
        SundryCreditor.objects.create(
            name=request.POST['name'],
            contact=request.POST['contact'],
            email=request.POST.get('email', ''),
            amount_payable=request.POST['amount_payable'],
            due_date=request.POST['due_date'],
            description=request.POST.get('description', ''),
            is_paid=request.POST.get('is_paid') == 'on',
            payment_date=request.POST.get('payment_date') if request.POST.get('is_paid') == 'on' else None
        )
        return redirect('creditor_list')
    return render(request, 'finance/creditors/create.html')


@login_required(login_url='login')
def creditor_update(request, pk):
    creditor = get_object_or_404(SundryCreditor, pk=pk)
    if request.method == 'POST':
        creditor.name = request.POST['name']
        creditor.contact = request.POST['contact']
        creditor.email = request.POST.get('email', '')
        creditor.amount_payable = request.POST['amount_payable']
        creditor.due_date = request.POST['due_date']
        creditor.description = request.POST.get('description', '')
        creditor.is_paid = request.POST.get('is_paid') == 'on'
        creditor.payment_date = request.POST.get('payment_date') if request.POST.get('is_paid') == 'on' else None
        creditor.save()
        return redirect('creditor_list')
    return render(request, 'finance/creditors/update.html', {'creditor': creditor})


@login_required(login_url='login')
def creditor_delete(request, pk):
    creditor = get_object_or_404(SundryCreditor, pk=pk)
    if request.method == 'POST':
        creditor.delete()
        return redirect('creditor_list')
    return render(request, 'finance/creditors/delete.html', {'creditor': creditor})
