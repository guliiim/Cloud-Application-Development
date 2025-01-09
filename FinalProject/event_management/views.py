from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Event, Category, EventCategory, Venue, Registration, Ticket, Payment, Review, Notification
from django.contrib.auth.models import User
import requests 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer, EventSerializer, RegistrationSerializer

# Home page
def home(request):
    return render(request, 'base.html')

# Register View
def register_user(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        function_url = "https://us-central1-plated-howl-435508-q1.cloudfunctions.net/send_welcome_email"

        payload = {'username': username,'to_email': email}

        response = requests.post(function_url, json=payload)

        if response.status_code == 200:
            print("Email sent successfully!")
        else:
            print(f"Error sending email: {response.text}")

        return redirect('login')

    return render(request, 'register.html')

# Login View
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return JsonResponse({'error': 'Invalid credentials'})
    return render(request, 'login.html')

# Logout View
def logout_user(request):
    logout(request)
    return redirect('login')

# Create and Manage Events
@login_required
def create_event(request):
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        date_time = request.POST['date_time']
        location = request.POST['location']
        category_ids = request.POST.getlist('categories')

        user = request.user

        # If needed, force the user to be loaded properly
        if hasattr(user, '_wrapped'):
            user = user._wrapped  # This ensures it resolves the lazy object

        # Ensure the user is indeed a User instance
        if not isinstance(user, User):
            return JsonResponse({'error': 'Invalid user instance'}, status=400)
            
        event = Event.objects.create(
            title=title,
            description=description,
            date_time=date_time,
            location=location,
            created_by=user
        )
        for category_id in category_ids:
            EventCategory.objects.create(event=event, category_id=category_id)

        return JsonResponse({'message': 'Event created successfully'})

    categories = Category.objects.all()
    return render(request, 'create_event.html', {'categories': categories})

# Manage Event Venues
@login_required
def manage_venues(request):
    if request.method == "POST":
        name = request.POST['name']
        address = request.POST['address']
        capacity = request.POST['capacity']
        contact_info = request.POST['contact_info']

        Venue.objects.create(name=name, address=address, capacity=capacity, contact_info=contact_info)
        return JsonResponse({'message': 'Venue added successfully'})

    venues = Venue.objects.all()
    return render(request, 'manage_venues.html', {'venues': venues})

# Browse Events
def browse_events(request):
    events = Event.objects.all()

    if request.method == 'POST':
        # Handle review submission
        event_id = request.POST['event_id']
        rating = request.POST['rating']
        comment = request.POST['comment']

        # Ensure the event exists
        event = get_object_or_404(Event, id=event_id)

        # Create a review for the event
        Review.objects.create(
            event=event,
            user=request.user,
            rating=rating,
            comment=comment
        )

        # Send a success message
        return JsonResponse({'message': 'Review submitted successfully'})

    return render(request, 'browse_events.html', {'events': events})

# Register for Events
@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    tickets = Ticket.objects.filter(event_id=event_id)

    if request.method == 'POST':
        ticket_type = request.POST['ticket_type']
        number_of_tickets = int(request.POST['number_of_tickets'])

        registration = Registration.objects.create(
            user_id=request.user.id,
            event_id=event.id,
            registration_date=request.POST['registration_date'],
            ticket_type=ticket_type,
            number_of_tickets=number_of_tickets
        )

        send_notification(request.user, event, 'You have successfully registered for the event.')
        return JsonResponse({'message': 'Registered successfully'})

    return render(request, 'register_event.html', {'event': event, 'tickets': tickets})

# Make Payments
@login_required
def make_payment(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id)

    if request.method == 'POST':
        amount = request.POST['amount']

        Payment.objects.create(
            registration_id=registration.id,
            amount=amount,
            status='Completed',
            payment_date=request.POST['payment_date']
        )

        send_notification(request.user, registration.event, 'Payment successful.')
        return JsonResponse({'message': 'Payment completed successfully'})

    return render(request, 'make_payment.html', {'registration': registration})

# Function to send notifications
def send_notification(user, event, message):
    Notification.objects.create(user_id=user.id, event_id=event.id, message=message)

@api_view(['POST'])
def register_user_api(request):
    if request.method == "POST":
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User registered successfully', 'user': serializer.data}, status=201)
        return Response(serializer.errors, status=400)

@api_view(['POST'])
def create_event_api(request):
    if request.method == "POST":
        title = request.data['title']
        description = request.data['description']
        date_time = request.data['date_time']
        location = request.data['location']
        category_ids = request.data.get('categories', [])

        event = Event.objects.create(
            title=title,
            description=description,
            date_time=date_time,
            location=location,
            created_by=request.user
        )

        for category_id in category_ids:
            EventCategory.objects.create(event=event, category_id=category_id)

        return Response({'message': 'Event created successfully', 'event': EventSerializer(event).data}, status=201)

@api_view(['POST'])
def register_event_api(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    tickets = Ticket.objects.filter(event_id=event_id)

    ticket_type = request.data['ticket_type']
    number_of_tickets = request.data['number_of_tickets']

    registration = Registration.objects.create(
        user=request.user,
        event=event,
        ticket_type=ticket_type,
        number_of_tickets=number_of_tickets,
        registration_date=request.data['registration_date']
    )

    return Response({'message': 'Registered successfully', 'registration': RegistrationSerializer(registration).data}, status=201)
