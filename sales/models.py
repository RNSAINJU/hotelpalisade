
from django.db import models
from rooms.models import Room

class FoodItem(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	price = models.DecimalField(max_digits=8, decimal_places=2)
	available = models.BooleanField(default=True)

	def __str__(self):
		return self.name

class SalesBill(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	guest_name = models.CharField(max_length=100)
	room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_bills")
	room_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	items = models.ManyToManyField(FoodItem, through="SalesBillItem")
	discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	total_amount = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return f"Bill #{self.id} - {self.guest_name}"
	
	def calculate_total(self):
		"""Calculate total including food items and room charge"""
		items_total = sum(item.price * item.quantity for item in self.salesbillitem_set.all())
		return items_total + self.room_charge
	
	def get_payment_methods_display(self):
		"""Get comma-separated list of payment methods"""
		payments = self.payments.all()
		if not payments:
			return "N/A"
		return ", ".join([f"{p.get_payment_method_display()} (Rs{p.amount})" for p in payments])

class SalesBillItem(models.Model):
	sales_bill = models.ForeignKey(SalesBill, on_delete=models.CASCADE)
	food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField(default=1)
	price = models.DecimalField(max_digits=8, decimal_places=2)

	def __str__(self):
		return f"{self.food_item.name} x {self.quantity}"

class PaymentDetail(models.Model):
	PAYMENT_METHODS = [
		('cash', 'Cash'),
		('card', 'Card'),
		('online', 'Online'),
		('upi', 'UPI'),
	]
	sales_bill = models.ForeignKey(SalesBill, on_delete=models.CASCADE, related_name='payments')
	payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
	amount = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return f"{self.get_payment_method_display()} - Rs{self.amount}"
