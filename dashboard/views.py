
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from inventory.models import InventoryItem
from sales.models import SalesBill, FoodItem, SalesBillItem
from rooms.models import Room, Guest
from django.db.models import Sum, F, FloatField
from django import forms

@staff_member_required
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


@staff_member_required
def inventory_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('/dashboard/inventory/')
    return render(request, 'dashboard/inventory/delete.html', {'item': item})

@staff_member_required
def dashboard(request):
	inventory_count = InventoryItem.objects.count()
	total_inventory_amount = InventoryItem.objects.aggregate(
		total=Sum(F('quantity') * F('price_per_unit'), output_field=FloatField())
	)["total"] or 0
	sales_count = SalesBill.objects.count()
	total_sales_amount = SalesBill.objects.aggregate(
		total=Sum('total_amount')
	)["total"] or 0
	context = {
		'inventory_count': inventory_count,
		'total_inventory_amount': total_inventory_amount,
		'sales_count': sales_count,
		'total_sales_amount': total_sales_amount,
	}
	return render(request, 'dashboard/dashboard.html', context)


@staff_member_required
def inventory_list(request):
	items = InventoryItem.objects.all().order_by('-last_updated')
	return render(request, 'dashboard/inventory/list.html', {'items': items})


class InventoryItemForm(forms.ModelForm):
	class Meta:
		model = InventoryItem
		fields = ['name', 'description', 'quantity', 'unit', 'price_per_unit']


@staff_member_required
def inventory_create(request):
	if request.method == 'POST':
		form = InventoryItemForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/dashboard/inventory/')
	else:
		form = InventoryItemForm()
	return render(request, 'dashboard/inventory/create.html', {'form': form})


# ============ Rooms Views ============

class RoomForm(forms.ModelForm):
	class Meta:
		model = Room
		fields = ['number', 'room_type', 'is_available', 'price_per_night']


@staff_member_required
def room_list(request):
	rooms = Room.objects.all().order_by('number')
	return render(request, 'dashboard/rooms/list.html', {'rooms': rooms})


@staff_member_required
def room_create(request):
	if request.method == 'POST':
		form = RoomForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/dashboard/rooms/')
	else:
		form = RoomForm()
	return render(request, 'dashboard/rooms/create.html', {'form': form})


@staff_member_required
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


@staff_member_required
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


@staff_member_required
def food_item_list(request):
	food_items = FoodItem.objects.all().order_by('name')
	return render(request, 'dashboard/food_items/list.html', {'food_items': food_items})


@staff_member_required
def food_item_create(request):
	if request.method == 'POST':
		form = FoodItemForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/dashboard/food-items/')
	else:
		form = FoodItemForm()
	return render(request, 'dashboard/food_items/create.html', {'form': form})


@staff_member_required
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


@staff_member_required
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
		fields = ['guest_name', 'total_amount']


@staff_member_required
def sales_bill_list(request):
	bills = SalesBill.objects.all().order_by('-created_at')
	return render(request, 'dashboard/sales_bills/list.html', {'bills': bills})


@staff_member_required
def sales_bill_create(request):
	if request.method == 'POST':
		form = SalesBillForm(request.POST)
		if form.is_valid():
			bill = form.save()
			# Handle adding items to the bill
			food_items = request.POST.getlist('food_items[]')
			quantities = request.POST.getlist('quantities[]')
			for food_id, qty in zip(food_items, quantities):
				if food_id and qty:
					food = FoodItem.objects.get(id=food_id)
					SalesBillItem.objects.create(
						sales_bill=bill,
						food_item=food,
						quantity=int(qty),
						price=food.price
					)
			return redirect('/dashboard/sales-bills/')
	else:
		form = SalesBillForm()
	
	food_items = FoodItem.objects.filter(available=True)
	return render(request, 'dashboard/sales_bills/create.html', {'form': form, 'food_items': food_items})


@staff_member_required
def sales_bill_detail(request, pk):
	bill = get_object_or_404(SalesBill, pk=pk)
	items = SalesBillItem.objects.filter(sales_bill=bill)
	return render(request, 'dashboard/sales_bills/detail.html', {'bill': bill, 'items': items})


@staff_member_required
def sales_bill_delete(request, pk):
	bill = get_object_or_404(SalesBill, pk=pk)
	if request.method == 'POST':
		bill.delete()
		return redirect('/dashboard/sales-bills/')
	return render(request, 'dashboard/sales_bills/delete.html', {'bill': bill})

