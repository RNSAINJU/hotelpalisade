
from django.db import models

class InventoryItem(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	quantity = models.PositiveIntegerField(default=0)
	unit = models.CharField(max_length=20)
	price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
	last_updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name
