from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Event, Registration

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_organizer', 'is_participant', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Role Configuration', {'fields': ('is_organizer', 'is_participant')}),
    )

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'organizer', 'max_participants')
    list_filter = ('date', 'location', 'organizer')
    search_fields = ('title', 'description', 'location')

class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'registration_date')
    list_filter = ('event', 'registration_date')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Registration, RegistrationAdmin)
