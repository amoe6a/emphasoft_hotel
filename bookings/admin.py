from django.contrib import admin
from .models import Room, Booking

class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_night', 'capacity')
    
class BookingAdmin(admin.ModelAdmin):
    list_filter = ('start_date', 'room')

admin.site.register(Room, RoomAdmin)
admin.site.register(Booking, BookingAdmin)