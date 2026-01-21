
from django.contrib import admin
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
	list_display = ("number", "room_type", "is_available", "price_per_night")
	search_fields = ("number",)
	list_filter = ("room_type", "is_available")
	fieldsets = (
		(None, {
			'fields': ("number", "room_type")
		}),
		("Status & Pricing", {
			'fields': ("is_available", "price_per_night")
		}),
	)
