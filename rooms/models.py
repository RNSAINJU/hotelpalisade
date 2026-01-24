
from django.db import models

class Room(models.Model):
	ROOM_TYPES = [
		("single", "Single"),
		("double", "Double"),
		("suite", "Suite"),
	]
	STATUS_CHOICES = [
		("available", "Available"),
		("booked", "Booked"),
		("occupied", "Occupied"),
		("maintenance", "Maintenance"),
	]
	number = models.CharField(max_length=10, unique=True)
	room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
	status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="available")
	is_available = models.BooleanField(default=True)
	price_per_night = models.DecimalField(max_digits=8, decimal_places=2)

	def __str__(self):
		return f"Room {self.number} ({self.room_type})"

class Guest(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	email = models.EmailField(blank=True)
	phone = models.CharField(max_length=20, blank=True)
	check_in = models.DateField()
	check_out = models.DateField()
	room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="guests")

	def __str__(self):
		return f"{self.first_name} {self.last_name}"
