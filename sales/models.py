
from django.db import models

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
	items = models.ManyToManyField(FoodItem, through="SalesBillItem")
	total_amount = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return f"Bill #{self.id} - {self.guest_name}"

class SalesBillItem(models.Model):
	sales_bill = models.ForeignKey(SalesBill, on_delete=models.CASCADE)
	food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField(default=1)
	price = models.DecimalField(max_digits=8, decimal_places=2)

	def __str__(self):
		return f"{self.food_item.name} x {self.quantity}"
