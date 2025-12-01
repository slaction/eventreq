from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public pages
    path("", views.home, name="home"),
    path("login/", auth_views.LoginView.as_view(template_name='core/login.html'), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/vendor/", views.register_vendor, name="register_vendor"),
    path("register/event-manager/", views.register_event_manager, name="register_event_manager"),
    
    # Dashboard redirect
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # Vendor routes
    path("vendor/dashboard/", views.vendor_dashboard, name="vendor_dashboard"),
    path("vendor/profile/", views.vendor_profile_edit, name="vendor_profile_edit"),
    path("vendor/event/<int:event_id>/", views.event_detail, name="event_detail"),
    
    # Event manager routes
    path("event-manager/dashboard/", views.event_manager_dashboard, name="event_manager_dashboard"),
    path("event-manager/event/create/", views.event_create, name="event_create"),
    path("event-manager/event/<int:event_id>/edit/", views.event_edit, name="event_edit"),
    path("event-manager/event/<int:event_id>/publish/", views.event_publish, name="event_publish"),
    path("event-manager/event/<int:event_id>/bids/", views.event_bids, name="event_bids"),
    path("event-manager/bid/<int:bid_id>/", views.bid_detail, name="bid_detail"),
]
