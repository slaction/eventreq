from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import UserProfile, VendorProfile, Event, EventBid, State
from .forms import UserRegistrationForm, VendorProfileForm, EventForm, EventBidForm
from .models import get_matching_events_for_vendor


def home(request):
    """Home page - public"""
    return render(request, 'core/home.html')


def login_view(request):
    """Login view - using Django's built-in"""
    from django.contrib.auth.views import LoginView
    return LoginView.as_view(template_name='core/login.html')(request)


def register_vendor(request):
    """Vendor registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Please complete your vendor profile.')
            return redirect('vendor_profile_edit')
    else:
        form = UserRegistrationForm(initial={'role': UserProfile.ROLE_VENDOR})
    return render(request, 'core/register.html', {'form': form, 'role': 'vendor'})


def register_event_manager(request):
    """Event manager registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('event_manager_dashboard')
    else:
        form = UserRegistrationForm(initial={'role': UserProfile.ROLE_EVENT_MANAGER})
    return render(request, 'core/register.html', {'form': form, 'role': 'event_manager'})


@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user role"""
    try:
        profile = request.user.userprofile
        if profile.role == UserProfile.ROLE_VENDOR:
            return redirect('vendor_dashboard')
        elif profile.role == UserProfile.ROLE_EVENT_MANAGER:
            return redirect('event_manager_dashboard')
    except UserProfile.DoesNotExist:
        pass
    return redirect('home')


@login_required
def vendor_dashboard(request):
    """Vendor dashboard - matching events"""
    try:
        vendor_profile = request.user.vendorprofile
        matching_events = get_matching_events_for_vendor(vendor_profile)
        context = {
            'vendor_profile': vendor_profile,
            'events': matching_events,
        }
    except VendorProfile.DoesNotExist:
        messages.warning(request, 'Please complete your vendor profile first.')
        return redirect('vendor_profile_edit')
    return render(request, 'core/vendor/dashboard.html', context)


@login_required
def vendor_profile_edit(request):
    """Edit vendor profile"""
    try:
        vendor_profile = request.user.vendorprofile
    except VendorProfile.DoesNotExist:
        vendor_profile = None

    if request.method == 'POST':
        form = VendorProfileForm(request.POST, instance=vendor_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Profile updated successfully!')
            return redirect('vendor_dashboard')
    else:
        form = VendorProfileForm(instance=vendor_profile)

    return render(request, 'core/vendor/profile_edit.html', {'form': form})


@login_required
def event_detail(request, event_id):
    """Event detail page - for vendors to view and bid"""
    event = get_object_or_404(Event, id=event_id, is_published=True)
    vendor_profile = None
    existing_bid = None

    try:
        vendor_profile = request.user.vendorprofile
        existing_bid = EventBid.objects.filter(event=event, vendor=vendor_profile).first()
    except VendorProfile.DoesNotExist:
        pass

    if request.method == 'POST' and vendor_profile:
        form = EventBidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.event = event
            bid.vendor = vendor_profile
            bid.save()
            messages.success(request, 'Bid submitted successfully!')
            return redirect('vendor_dashboard')
    else:
        form = EventBidForm()

    context = {
        'event': event,
        'vendor_profile': vendor_profile,
        'form': form,
        'existing_bid': existing_bid,
    }
    return render(request, 'core/vendor/event_detail.html', context)


@login_required
def event_manager_dashboard(request):
    """Event manager dashboard - list of events"""
    events = Event.objects.filter(created_by=request.user)
    context = {
        'events': events,
    }
    return render(request, 'core/event_manager/dashboard.html', context)


@login_required
def event_create(request):
    """Create new event"""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_manager_dashboard')
    else:
        form = EventForm()
    return render(request, 'core/event_manager/event_form.html', {'form': form, 'action': 'Create'})


@login_required
def event_edit(request, event_id):
    """Edit event"""
    event = get_object_or_404(Event, id=event_id, created_by=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_manager_dashboard')
    else:
        form = EventForm(instance=event)
    return render(request, 'core/event_manager/event_form.html', {'form': form, 'event': event, 'action': 'Edit'})


@login_required
def event_publish(request, event_id):
    """Publish/unpublish event"""
    event = get_object_or_404(Event, id=event_id, created_by=request.user)
    event.is_published = not event.is_published
    event.save()
    status = 'published' if event.is_published else 'unpublished'
    messages.success(request, f'Event {status} successfully!')
    return redirect('event_manager_dashboard')


@login_required
def event_bids(request, event_id):
    """View bids for an event"""
    event = get_object_or_404(Event, id=event_id, created_by=request.user)
    bids = EventBid.objects.filter(event=event)
    context = {
        'event': event,
        'bids': bids,
    }
    return render(request, 'core/event_manager/event_bids.html', context)


@login_required
def bid_detail(request, bid_id):
    """View bid detail"""
    bid = get_object_or_404(EventBid, id=bid_id)
    # Ensure the event manager owns the event
    if bid.event.created_by != request.user:
        messages.error(request, 'You do not have permission to view this bid.')
        return redirect('event_manager_dashboard')
    return render(request, 'core/event_manager/bid_detail.html', {'bid': bid})
