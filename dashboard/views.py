
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core import serializers
from decimal import Decimal
from inventory.models import InventoryItem
from sales.models import SalesBill, FoodItem, SalesBillItem, PaymentDetail
from rooms.models import Room, Guest
from django.db.models import Sum, F, FloatField
from django import forms
import json


# ============ Authentication Views ============

def custom_login(request):
	"""Custom login view"""
	if request.user.is_authenticated:
		return redirect('dashboard')
	
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		
		if user is not None:
			login(request, user)
			return redirect('dashboard')
		else:
			context = {
				'form_error': 'Invalid username or password. Please try again.',
				'username': username
			}
			return render(request, 'login.html', context)
	
	return render(request, 'login.html')


@require_POST
def custom_logout(request):
	"""Custom logout view"""
	logout(request)
	return redirect('login')


@login_required(login_url='login')
def dashboard(request):
	from datetime import datetime, timedelta
	from django.db.models import Count
	
	inventory_count = InventoryItem.objects.count()
	total_inventory_amount = InventoryItem.objects.aggregate(
		total=Sum(F('quantity') * F('price_per_unit'), output_field=FloatField())
	)["total"] or 0
	sales_count = SalesBill.objects.count()
	total_sales_amount = SalesBill.objects.aggregate(
		total=Sum('total_amount')
	)["total"] or 0
	
	# Get sales data for the last 7 days
	today = datetime.now().date()
	last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
	
	# Get daily sales amounts
	daily_sales = []
	daily_labels = []
	for day in last_7_days:
		next_day = day + timedelta(days=1)
		sales_amount = SalesBill.objects.filter(
			created_at__gte=day,
			created_at__lt=next_day
		).aggregate(total=Sum('total_amount'))['total'] or 0
		daily_sales.append(float(sales_amount))
		daily_labels.append(day.strftime('%b %d'))
	
	context = {
		'inventory_count': inventory_count,
		'total_inventory_amount': total_inventory_amount,
		'sales_count': sales_count,
		'total_sales_amount': total_sales_amount,
		'daily_sales': json.dumps(daily_sales),
		'daily_labels': json.dumps(daily_labels),
	}
	return render(request, 'dashboard/dashboard.html', context)


@login_required(login_url='login')
def inventory_list(request):
	items = InventoryItem.objects.all().order_by('-last_updated')
	return render(request, 'dashboard/inventory/list.html', {'items': items})


class InventoryItemForm(forms.ModelForm):
	class Meta:
		model = InventoryItem
		fields = ['name', 'description', 'quantity', 'unit', 'price_per_unit']


@login_required(login_url='login')
def inventory_create(request):
	if request.method == 'POST':
		form = InventoryItemForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/dashboard/inventory/')
	else:
		form = InventoryItemForm()
	return render(request, 'dashboard/inventory/create.html', {'form': form})


@login_required(login_url='login')
def inventory_update(request, pk):
	item = get_object_or_404(InventoryItem, pk=pk)
	if request.method == 'POST':
		form = InventoryItemForm(request.POST, instance=item)
		if form.is_valid():
			form.save()
			return redirect('/dashboard/inventory/')
	else:
		form = InventoryItemForm(instance=item)
	return render(request, 'dashboard/inventory/update.html', {'form': form, 'item': item})


@login_required(login_url='login')
def inventory_delete(request, pk):
	item = get_object_or_404(InventoryItem, pk=pk)
	if request.method == 'POST':
		item.delete()
		return redirect('/dashboard/inventory/')
	return render(request, 'dashboard/inventory/delete.html', {'item': item})


# ============ Rooms Views ============

class RoomForm(forms.ModelForm):
	class Meta:
		model = Room
		fields = ['number', 'room_type', 'status', 'is_available', 'price_per_night']


@login_required(login_url='login')
def room_list(request):
	rooms = Room.objects.all().order_by('number')
	return render(request, 'dashboard/rooms/list.html', {'rooms': rooms})


@login_required(login_url='login')
def room_create(request):
	if request.method == 'POST':
		form = RoomForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/dashboard/rooms/')
	else:
		form = RoomForm()
	return render(request, 'dashboard/rooms/create.html', {'form': form})


@login_required(login_url='login')
def room_update(request, pk):
	room = get_object_or_404(Room, pk=pk)
	if request.method == 'POST':
		form = RoomForm(request.POST, instance=room)
		if form.is_valid():
			form.save()
			return redirect('/dashboard/rooms/')
	else:
		form = RoomForm(instance=room)
	return render(request, 'dashboard/rooms/update.html', {'form': form, 'room': room})


@login_required(login_url='login')
def room_delete(request, pk):
	room = get_object_or_404(Room, pk=pk)
	if request.method == 'POST':
		room.delete()
		return redirect('/dashboard/rooms/')
	return render(request, 'dashboard/rooms/delete.html', {'room': room})


# ============ Food Items Views ============

class FoodItemForm(forms.ModelForm):
	class Meta:
		model = FoodItem
		fields = ['name', 'description', 'price', 'available']


@login_required(login_url='login')
def food_item_list(request):
	food_items = FoodItem.objects.all().order_by('name')
	return render(request, 'dashboard/food_items/list.html', {'food_items': food_items})


@login_required(login_url='login')
def food_item_create(request):
	if request.method == 'POST':
		form = FoodItemForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/dashboard/food-items/')
	else:
		form = FoodItemForm()
	return render(request, 'dashboard/food_items/create.html', {'form': form})


@login_required(login_url='login')
def food_item_update(request, pk):
	food_item = get_object_or_404(FoodItem, pk=pk)
	if request.method == 'POST':
		form = FoodItemForm(request.POST, instance=food_item)
		if form.is_valid():
			form.save()
			return redirect('/dashboard/food-items/')
	else:
		form = FoodItemForm(instance=food_item)
	return render(request, 'dashboard/food_items/update.html', {'form': form, 'food_item': food_item})


@login_required(login_url='login')
def food_item_delete(request, pk):
	food_item = get_object_or_404(FoodItem, pk=pk)
	if request.method == 'POST':
		food_item.delete()
		return redirect('/dashboard/food-items/')
	return render(request, 'dashboard/food_items/delete.html', {'food_item': food_item})


# ============ Sales Bills Views ============

class SalesBillForm(forms.ModelForm):
	class Meta:
		model = SalesBill
		fields = ['guest_name', 'room', 'total_amount']


@login_required(login_url='login')
def sales_bill_list(request):
	bills = SalesBill.objects.all().order_by('-created_at')
	return render(request, 'dashboard/sales_bills/list.html', {'bills': bills})


@login_required(login_url='login')
def sales_bill_create(request):
	if request.method == 'POST':
		form = SalesBillForm(request.POST)
		if form.is_valid():
			bill = form.save(commit=False)
			
			# Calculate room charge if room is selected
			room_charge = 0
			if bill.room:
				room_charge = bill.room.price_per_night
			bill.room_charge = room_charge
			
			# Handle adding items to the bill
			food_items = request.POST.getlist('food_items[]')
			quantities = request.POST.getlist('quantities[]')
			
			# Calculate food items total
			items_total = 0
			items_to_create = []
			for food_id, qty in zip(food_items, quantities):
				if food_id and qty:
					food = FoodItem.objects.get(id=food_id)
					qty_int = int(qty)
					item_price = food.price * qty_int
					items_total += item_price
					items_to_create.append({
						'food': food,
						'quantity': qty_int,
						'price': food.price
					})
			
			# Get discount values from form
			discount_percentage = Decimal(request.POST.get('discount_percentage', 0))
			discount_amount = Decimal(request.POST.get('discount_amount', 0))
			
			# Calculate total amount with discount
			subtotal = items_total + room_charge
			bill.discount_percentage = discount_percentage
			bill.discount_amount = discount_amount
			bill.total_amount = subtotal - discount_amount
			bill.save()
			
			# Create bill items
			for item_data in items_to_create:
				SalesBillItem.objects.create(
					sales_bill=bill,
					food_item=item_data['food'],
					quantity=item_data['quantity'],
					price=item_data['price']
				)
			
			# Handle multiple payment methods
			payment_methods = request.POST.getlist('payment_methods[]')
			payment_amounts = request.POST.getlist('payment_amounts[]')
			
			for method, amount in zip(payment_methods, payment_amounts):
				if method and amount:
					PaymentDetail.objects.create(
						sales_bill=bill,
						payment_method=method,
						amount=Decimal(amount)
					)
			
			return redirect('/dashboard/sales-bills/')
	else:
		form = SalesBillForm()
	
	food_items = FoodItem.objects.filter(available=True)
	rooms = Room.objects.all()
	return render(request, 'dashboard/sales_bills/create.html', {'form': form, 'food_items': food_items, 'rooms': rooms})


@login_required(login_url='login')
def sales_bill_detail(request, pk):
	bill = get_object_or_404(SalesBill, pk=pk)
	items = SalesBillItem.objects.filter(sales_bill=bill)
	return render(request, 'dashboard/sales_bills/detail.html', {'bill': bill, 'items': items})


@login_required(login_url='login')
def sales_bill_delete(request, pk):
	bill = get_object_or_404(SalesBill, pk=pk)
	if request.method == 'POST':
		bill.delete()
		return redirect('/dashboard/sales-bills/')
	return render(request, 'dashboard/sales_bills/delete.html', {'bill': bill})


@login_required(login_url='login')
def settings_view(request):
	return render(request, 'dashboard/settings.html')


@login_required(login_url='login')
def settings_export(request):
	from inventory.models import InventoryItem
	from rooms.models import Room, Guest
	from sales.models import FoodItem, SalesBill, SalesBillItem
	from django.core import serializers
	
	# Collect all data
	data = {
		'inventory_items': json.loads(serializers.serialize('json', InventoryItem.objects.all())),
		'rooms': json.loads(serializers.serialize('json', Room.objects.all())),
		'guests': json.loads(serializers.serialize('json', Guest.objects.all())),
		'food_items': json.loads(serializers.serialize('json', FoodItem.objects.all())),
		'sales_bills': json.loads(serializers.serialize('json', SalesBill.objects.all())),
		'sales_bill_items': json.loads(serializers.serialize('json', SalesBillItem.objects.all())),
	}
	
	# Create response
	response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
	response['Content-Disposition'] = 'attachment; filename="hotel_data_export.json"'
	return response


@login_required(login_url='login')
def settings_import(request):
	if request.method == 'POST':
		try:
			uploaded_file = request.FILES.get('import_file')
			if not uploaded_file:
				messages.error(request, 'No file uploaded.')
				return redirect('/dashboard/settings/')
			
			# Read and parse JSON
			file_content = uploaded_file.read().decode('utf-8')
			data = json.loads(file_content)
			
			from inventory.models import InventoryItem
			from rooms.models import Room, Guest
			from sales.models import FoodItem, SalesBill, SalesBillItem
			from django.core import serializers
			
			# Import data in order (to respect foreign keys)
			for obj_data in data.get('inventory_items', []):
				InventoryItem.objects.update_or_create(
					id=obj_data['pk'],
					defaults=obj_data['fields']
				)
			
			for obj_data in data.get('rooms', []):
				Room.objects.update_or_create(
					id=obj_data['pk'],
					defaults=obj_data['fields']
				)
			
			for obj_data in data.get('guests', []):
				fields = obj_data['fields'].copy()
				# Handle foreign key for room
				if 'room' in fields and fields['room']:
					fields['room'] = Room.objects.get(id=fields['room'])
				Guest.objects.update_or_create(
					id=obj_data['pk'],
					defaults=fields
				)
			
			for obj_data in data.get('food_items', []):
				FoodItem.objects.update_or_create(
					id=obj_data['pk'],
					defaults=obj_data['fields']
				)
			
			for obj_data in data.get('sales_bills', []):
				fields = obj_data['fields'].copy()
				# Handle foreign keys
				if 'guest' in fields and fields['guest']:
					fields['guest'] = Guest.objects.get(id=fields['guest'])
				if 'room' in fields and fields['room']:
					fields['room'] = Room.objects.get(id=fields['room'])
				SalesBill.objects.update_or_create(
					id=obj_data['pk'],
					defaults=fields
				)
			
			for obj_data in data.get('sales_bill_items', []):
				fields = obj_data['fields'].copy()
				# Handle foreign keys
				if 'sales_bill' in fields and fields['sales_bill']:
					fields['sales_bill'] = SalesBill.objects.get(id=fields['sales_bill'])
				if 'food_item' in fields and fields['food_item']:
					fields['food_item'] = FoodItem.objects.get(id=fields['food_item'])
				SalesBillItem.objects.update_or_create(
					id=obj_data['pk'],
					defaults=fields
				)
			
			messages.success(request, 'Data imported successfully!')
		except Exception as e:
			messages.error(request, f'Error importing data: {str(e)}')
		
		return redirect('/dashboard/settings/')
	
	return redirect('/dashboard/settings/')


@login_required(login_url='login')
def settings_delete_all(request):
	if request.method == 'POST':
		# Verify confirmation code
		confirmation_code = request.POST.get('confirmation_code', '')
		if confirmation_code != 'DELETE123':
			messages.error(request, 'Invalid confirmation code. Data not deleted.')
			return redirect('/dashboard/settings/')
		
		try:
			from inventory.models import InventoryItem
			from rooms.models import Room, Guest
			from sales.models import FoodItem, SalesBill, SalesBillItem
			
			# Delete in reverse order of dependencies
			SalesBillItem.objects.all().delete()
			SalesBill.objects.all().delete()
			Guest.objects.all().delete()
			FoodItem.objects.all().delete()
			Room.objects.all().delete()
			InventoryItem.objects.all().delete()
			
			messages.success(request, 'All data deleted successfully!')
		except Exception as e:
			messages.error(request, f'Error deleting data: {str(e)}')
		
		return redirect('/dashboard/settings/')
	
	return redirect('/dashboard/settings/')

