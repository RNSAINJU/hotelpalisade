from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Inventory URLs
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/create/', views.inventory_create, name='inventory_create'),
    path('inventory/<int:pk>/update/', views.inventory_update, name='inventory_update'),
    path('inventory/<int:pk>/delete/', views.inventory_delete, name='inventory_delete'),
    
    # Rooms URLs
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/create/', views.room_create, name='room_create'),
    path('rooms/<int:pk>/update/', views.room_update, name='room_update'),
    path('rooms/<int:pk>/delete/', views.room_delete, name='room_delete'),
    
    # Food Items URLs
    path('food-items/', views.food_item_list, name='food_item_list'),
    path('food-items/create/', views.food_item_create, name='food_item_create'),
    path('food-items/<int:pk>/update/', views.food_item_update, name='food_item_update'),
    path('food-items/<int:pk>/delete/', views.food_item_delete, name='food_item_delete'),
    
    # Sales Bills URLs
    path('sales-bills/', views.sales_bill_list, name='sales_bill_list'),
    path('sales-bills/create/', views.sales_bill_create, name='sales_bill_create'),
    path('sales-bills/<int:pk>/', views.sales_bill_detail, name='sales_bill_detail'),
    path('sales-bills/<int:pk>/delete/', views.sales_bill_delete, name='sales_bill_delete'),
]

