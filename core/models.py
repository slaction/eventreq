from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class State(models.Model):
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class UserProfile(models.Model):
    ROLE_EVENT_MANAGER = "event_manager"
    ROLE_VENDOR = "vendor"

    ROLE_CHOICES = [
        (ROLE_EVENT_MANAGER, "Event Manager"),
        (ROLE_VENDOR, "Vendor"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class VendorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    base_city = models.CharField(max_length=100, blank=True)
    base_state = models.CharField(max_length=2, blank=True)
    base_zip = models.CharField(max_length=10, blank=True)
    base_latitude = models.FloatField(null=True, blank=True)
    base_longitude = models.FloatField(null=True, blank=True)
    service_states = models.ManyToManyField(State, blank=True)
    use_radius = models.BooleanField(default=False)
    max_travel_radius_miles = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.company_name


class Event(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    country = models.CharField(max_length=2, default="US")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    needs_sound = models.BooleanField(default=False)
    needs_lighting = models.BooleanField(default=False)
    needs_video = models.BooleanField(default=False)
    needs_staging = models.BooleanField(default=False)
    full_service_package = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class EventBid(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bids")
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="bids")
    message = models.TextField()
    estimated_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default="submitted", choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['event', 'vendor']

    def __str__(self):
        return f"{self.vendor.company_name} - {self.event.title}"


# Matching logic function
def get_matching_events_for_vendor(vendor_profile):
    """Get events that match a vendor's service states."""
    state_codes = vendor_profile.service_states.values_list("code", flat=True)
    return Event.objects.filter(is_published=True, state__in=state_codes)
