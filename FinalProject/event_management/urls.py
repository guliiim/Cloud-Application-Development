from django.urls import path
from . import views


urlpatterns = [
    path('home/', views.home, name= 'home'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('create-event/', views.create_event, name='create_event'),
    path('manage-venues/', views.manage_venues, name='manage_venues'),
    path('browse-events/', views.browse_events, name='browse_events'),
    path('register-event/<int:event_id>/', views.register_event, name='register_event'),
    path('api/register/', views.register_user_api, name='register_user_api'),
    path('api/create-event/', views.create_event_api, name='create_event_api'),
    path('api/register-event/<int:event_id>/', views.register_event_api, name='register_event_api'),
]

