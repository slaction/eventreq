from django.contrib import admin
from .models import State, UserProfile, VendorProfile, Event, EventBid


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'user', 'base_city', 'base_state']
    list_filter = ['base_state']
    search_fields = ['company_name', 'user__username']
    filter_horizontal = ['service_states']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'city', 'state', 'date', 'is_published']
    list_filter = ['is_published', 'state', 'date']
    search_fields = ['title', 'description', 'city']
    date_hierarchy = 'date'


@admin.register(EventBid)
class EventBidAdmin(admin.ModelAdmin):
    list_display = ['event', 'vendor', 'status', 'estimated_budget', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['event__title', 'vendor__company_name']
    date_hierarchy = 'created_at'
