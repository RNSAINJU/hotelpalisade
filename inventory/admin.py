from django.contrib import admin

# Register your models here.
from .models import InventoryItem  # Assuming InventoryItem is defined in models.py

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
	list_display = ("name", "quantity", "unit", "price_per_unit", "last_updated")
	search_fields = ("name",)
	list_filter = ("unit", "last_updated")
	readonly_fields = ("last_updated",)
	fieldsets = (
		(None, {
			'fields': ("name", "description")
		}),
		("Stock Info", {
			'fields': ("quantity", "unit", "price_per_unit", "last_updated")
		}),
	)
