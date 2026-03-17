from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import CustomUser, Event, Registration
from django.db.models import Count


# ─── Auth Views ───────────────────────────────────────────────────────────────

def home(request):
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by('date')[:6]
    return render(request, 'events/home.html', {'upcoming_events': upcoming_events})


def register_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()
        password1  = request.POST.get('password1', '')
        password2  = request.POST.get('password2', '')
        role       = request.POST.get('role', 'participant')

        if not username or not email or not password1:
            messages.error(request, 'All fields are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = CustomUser.objects.create_user(username=username, email=email, password=password1)
            user.is_organizer   = (role == 'organizer')
            user.is_participant = (role == 'participant')
            user.save()
            login(request, user)
            messages.success(request, f'Welcome, {username}! Account created.')
            return redirect('dashboard')
    return render(request, 'events/register.html')


def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'events/login.html')


def logout_user(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user = request.user
    if user.is_organizer:
        my_events = Event.objects.filter(organizer=user).annotate(reg_count=Count('registrations')).order_by('-date')
        context = {'my_events': my_events, 'is_organizer': True}
    else:
        my_registrations = Registration.objects.filter(user=user).select_related('event').order_by('-registration_date')
        context = {'my_registrations': my_registrations, 'is_organizer': False}
    return render(request, 'events/dashboard.html', context)


# ─── Event Views ──────────────────────────────────────────────────────────────

def event_list(request):
    query    = request.GET.get('q', '')
    location = request.GET.get('location', '')
    events   = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    if query:
        events = events.filter(title__icontains=query)
    if location:
        events = events.filter(location__icontains=location)
    events = events.annotate(reg_count=Count('registrations'))
    return render(request, 'events/event_list.html', {'events': events, 'query': query, 'location': location})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    is_registered = False
    slots_left    = event.max_participants - event.registrations.count()
    if request.user.is_authenticated:
        is_registered = Registration.objects.filter(user=request.user, event=event).exists()
    registrations = event.registrations.select_related('user').order_by('-registration_date')
    return render(request, 'events/event_detail.html', {
        'event': event,
        'is_registered': is_registered,
        'slots_left': slots_left,
        'registrations': registrations,
    })


@login_required
def create_event(request):
    if not request.user.is_organizer:
        messages.error(request, 'Only organizers can create events.')
        return redirect('dashboard')
    if request.method == 'POST':
        title            = request.POST.get('title', '').strip()
        description      = request.POST.get('description', '').strip()
        date             = request.POST.get('date', '')
        location         = request.POST.get('location', '').strip()
        max_participants = request.POST.get('max_participants', 0)
        if not all([title, description, date, location, max_participants]):
            messages.error(request, 'All fields are required.')
        else:
            Event.objects.create(
                title=title,
                description=description,
                date=date,
                location=location,
                max_participants=int(max_participants),
                organizer=request.user,
            )
            messages.success(request, f'Event "{title}" created successfully!')
            return redirect('event_list')
    return render(request, 'events/create_event.html')


@login_required
def edit_event(request, pk):
    event = get_object_or_404(Event, pk=pk, organizer=request.user)
    if request.method == 'POST':
        event.title            = request.POST.get('title', event.title).strip()
        event.description      = request.POST.get('description', event.description).strip()
        event.date             = request.POST.get('date', event.date)
        event.location         = request.POST.get('location', event.location).strip()
        event.max_participants = int(request.POST.get('max_participants', event.max_participants))
        event.save()
        messages.success(request, 'Event updated successfully!')
        return redirect('event_detail', pk=event.pk)
    return render(request, 'events/edit_event.html', {'event': event})


@login_required
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk, organizer=request.user)
    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" deleted.')
        return redirect('dashboard')
    return render(request, 'events/delete_event.html', {'event': event})


# ─── Registration ─────────────────────────────────────────────────────────────

@login_required
def register_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if not request.user.is_participant:
        messages.error(request, 'Only participants can register for events.')
        return redirect('event_detail', pk=pk)
    if Registration.objects.filter(user=request.user, event=event).exists():
        messages.warning(request, 'You are already registered for this event.')
    elif event.registrations.count() >= event.max_participants:
        messages.error(request, 'This event is fully booked.')
    else:
        Registration.objects.create(user=request.user, event=event)
        messages.success(request, f'Successfully registered for "{event.title}"!')
    return redirect('event_detail', pk=pk)


@login_required
def unregister_event(request, pk):
    event        = get_object_or_404(Event, pk=pk)
    registration = Registration.objects.filter(user=request.user, event=event).first()
    if registration:
        registration.delete()
        messages.success(request, f'Unregistered from "{event.title}".')
    else:
        messages.error(request, 'You are not registered for this event.')
    return redirect('event_detail', pk=pk)
