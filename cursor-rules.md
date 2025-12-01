# EventREQ – Cursor Project Instructions

## 1. Project Overview
EventREQ is a Django based platform where **Event Managers** can create events and **Vendors** can browse, bid, and manage their services based on state-level coverage. The MVP should remain simple, welcoming, and easy to use for people who are not industry experts.

Cursor should produce clean, minimal, maintainable Django code following these instructions.

---

## 2. Tech Stack Requirements
- **Python:** 3.12  
- **Framework:** Django 5.x  
- **Database:** Supabase Postgres (primary), SQLite fallback if `DATABASE_URL` is missing  
- **Auth:** Django’s built in authentication (no custom user model)  
- **UI Framework:** Tailwind CSS  
- **Rendering:** Django Templates  
- **HTMX:** Not required; classic Django for MVP  
- **App Structure:** Single Django app named `core`  
- **Environment:** `.env` file for secrets and database URL  

---

## 3. Project Structure

eventreq/
  manage.py
  eventreq/          
  core/              
  templates/
  static/
  requirements.txt
  cursor-rules.md

The `venv/` folder must never be committed to Git.

---

## 4. Authentication and User Roles

Use Django’s default `User` model. Extend with `UserProfile`:

class UserProfile(models.Model):
    ROLE_EVENT_MANAGER = "event_manager"
    ROLE_VENDOR = "vendor"

    ROLE_CHOICES = [
        (ROLE_EVENT_MANAGER, "Event Manager"),
        (ROLE_VENDOR, "Vendor"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

---

## 5. Location and Coverage Models

State model:

class State(models.Model):
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=50)

VendorProfile:

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

---

## 6. Event Model

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

---

## 7. Matching Logic

def get_matching_events_for_vendor(vendor_profile):
    state_codes = vendor_profile.service_states.values_list("code", flat=True)
    return Event.objects.filter(is_published=True, state__in=state_codes)

---

## 8. Vendor Bids

class EventBid(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bids")
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="bids")
    message = models.TextField()
    estimated_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default="submitted")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

---

## 9. Notifications
- Email vendors when a matching event is published.
- Email event managers when they receive a bid.
- Use Django console backend for dev.

---

## 10. Tailwind Requirements
- Clean, simple UI
- Tailwind components
- Easy forms for non technical users
- Checkboxes for services
- Clear “full service package” option

---

## 11. Pages Cursor Must Build

Public:
- Home
- Login
- Vendor registration
- Event manager registration

Vendor Dashboard:
- Profile edit
- Matching events
- Event detail
- Submit bid

Event Manager Dashboard:
- Event list
- Create event
- Edit event
- Publish event
- View bids
- Bid detail

---

## 12. Rules for Cursor
- Keep everything in a single app: core
- Generate migrations
- Use .env for database configuration
- Do not introduce React, REST API, DRF, etc
- Do not implement radius based coverage yet

---

## 13. Out of Scope
- Multi location vendors  
- Payments  
- REST API  
- Radius coverage  
- File uploads  

# End of Cursor Instructions
