from django.urls import path
from . import views

urlpatterns = [
    path('',                            views.home,             name='home'),
    path('register/',                   views.register_user,    name='register'),
    path('login/',                      views.login_user,       name='login'),
    path('logout/',                     views.logout_user,      name='logout'),
    path('dashboard/',                  views.dashboard,        name='dashboard'),
    path('events/',                     views.event_list,       name='event_list'),
    path('events/<int:pk>/',            views.event_detail,     name='event_detail'),
    path('events/create/',              views.create_event,     name='create_event'),
    path('events/<int:pk>/edit/',       views.edit_event,       name='edit_event'),
    path('events/<int:pk>/delete/',     views.delete_event,     name='delete_event'),
    path('events/<int:pk>/register/',   views.register_event,   name='register_event'),
    path('events/<int:pk>/unregister/', views.unregister_event, name='unregister_event'),
]
