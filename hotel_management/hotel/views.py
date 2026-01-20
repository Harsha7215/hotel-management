from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
import uuid
from django.db.models import Q
from .models import RoomReview
from .forms import RoomReviewForm
from django.db.models import Avg
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum



from .models import RoomType, Room, Booking, Payment
from .forms import RoomSearchForm, BookingForm, PaymentForm


# HOME PAGE
def home(request):
    room_types = RoomType.objects.all()[:3]
    return render(request, "hotel/home.html", {"room_types": room_types})


# ROOM LIST WITH SEARCH
from django.db.models import Q

def room_list(request):
    rooms = Room.objects.filter(status="available")
    form = RoomSearchForm(request.GET or None)

    if request.GET and form.is_valid():
        check_in = form.cleaned_data.get("check_in")
        check_out = form.cleaned_data.get("check_out")
        guests = form.cleaned_data.get("guests")

        if check_in and check_out:
            booked_rooms = Booking.objects.filter(
                Q(check_in_date__lt=check_out) &
                Q(check_out_date__gt=check_in),
                status__in=["confirmed", "pending"]
            ).values_list("room_id", flat=True)

            rooms = rooms.exclude(id__in=booked_rooms)

        if guests:
            rooms = rooms.filter(room_type__capacity__gte=guests)

    return render(request, "hotel/room_list.html", {
        "form": form,
        "rooms": rooms
    })


# ROOM DETAILS
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    reviews = room.reviews.all()
    avg_rating = reviews.aggregate(Avg("rating"))["rating__avg"]

    return render(request, "hotel/room_detail.html", {
        "room": room,
        "reviews": reviews,
        "avg_rating": avg_rating,
    })



# MAKE BOOKING
@login_required
def make_booking(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.guest = request.user
            booking.room = room

            # DATE VALIDATION
            if booking.check_out_date <= booking.check_in_date:
                messages.error(request, "Check-out date must be after check-in date")
                return render(request, "hotel/make_booking.html", {
                    "form": form,
                    "room": room
                })

            nights = (booking.check_out_date - booking.check_in_date).days
            booking.total_price = nights * room.room_type.price_per_night
            booking.status = "pending"
            booking.save()

            messages.success(request, "Booking created successfully! Please complete payment.")
            return redirect("payment", booking_id=booking.id)
    else:
        form = BookingForm()

    return render(request, "hotel/make_booking.html", {"form": form, "room": room})


# PAYMENT
@login_required
def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, guest=request.user)

    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.transaction_id = str(uuid.uuid4())[:8]
            payment.status = "completed"
            payment.save()

            booking.status = "confirmed"
            booking.save()

            booking.room.status = "occupied"
            booking.room.save()

            messages.success(request, "Payment successful. Booking confirmed!")
            return redirect("booking_details", booking_id=booking.id)
    else:
        form = PaymentForm(initial={"amount": booking.total_price})

    return render(request, "hotel/payment.html", {
        "form": form,
        "booking": booking
    })


# MY BOOKINGS
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(
        guest=request.user
    ).order_by("-created_at")

    return render(request, "hotel/my_bookings.html", {"bookings": bookings})


# BOOKING DETAILS
@login_required
def booking_details(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, guest=request.user)
    payment = Payment.objects.filter(booking=booking).first()
    return render(request, "hotel/booking_detail.html", {
        "booking": booking,
        "payment": payment
    })


# CANCEL BOOKING
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, guest=request.user)

    if booking.status in ["pending", "confirmed"]:
        booking.status = "cancelled"
        booking.save()

        booking.room.status = "available"
        booking.room.save()

        messages.success(request, "Booking cancelled successfully")

    return redirect("my_bookings")

@login_required
def add_review(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    # Check completed booking
    has_stayed = Booking.objects.filter(
        guest=request.user,
        room=room,
        status="completed"
    ).exists()

    if not has_stayed:
        messages.error(request, "You can review only after completing your stay.")
        return redirect("room_detail", pk=room.id)

    if request.method == "POST":
        form = RoomReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.room = room
            review.save()
            messages.success(request, "Thank you for your review!")
            return redirect("room_detail", pk=room.id)
    else:
        form = RoomReviewForm()

    return render(request, "hotel/add_review.html", {
        "form": form,
        "room": room
    })

@staff_member_required
def admin_dashboard(request):
    total_bookings = Booking.objects.count()
    confirmed_bookings = Booking.objects.filter(status="confirmed").count()
    cancelled_bookings = Booking.objects.filter(status="cancelled").count()

    total_revenue = Payment.objects.filter(
        status="completed"
    ).aggregate(total=Sum("amount"))["total"] or 0

    occupied_rooms = Room.objects.filter(status="occupied").count()

    return render(request, "hotel/admin_dashboard.html", {
        "total_bookings": total_bookings,
        "confirmed_bookings": confirmed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "total_revenue": total_revenue,
        "occupied_rooms": occupied_rooms,
    })


   

      
      
      




       