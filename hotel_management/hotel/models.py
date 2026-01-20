from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date
from django.templatetags.static import static


class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()
    amenities = models.TextField()

    # Image uploaded from admin (optional)
    image = models.ImageField(upload_to="room_types/", null=True, blank=True)

    is_active = models.BooleanField(default=True)

    # SAFE IMAGE URL (NO ERRORS)
    @property
    def image_url(self):
        # If admin uploaded image → use it
        if self.image:
            return self.image.url

        # 2Fallback images based on room type name
        name = self.name.lower()

        if "standard" in name:
            return static("images/standard.jpeg")
        elif "deluxe" in name:
            return static("images/delux.jpeg")
        elif "suite" in name:
            return static("images/suite.jpeg")

        # 3️⃣ Final fallback
        return static("images/default-room.jpeg")

    def __str__(self):
        return self.name


class Room(models.Model):
    ROOM_STATUS = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
    ]

    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    floor_number = models.IntegerField()

    status = models.CharField(
        max_length=20,
        choices=ROOM_STATUS,
        default="available"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.room_number}"


class Booking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    guest = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_guests = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.check_in_date < date.today():
            raise ValidationError("Check-in date cannot be in the past.")
        if self.check_out_date <= self.check_in_date:
            raise ValidationError("Check-out date must be after check-in date.")

    def __str__(self):
        return f"Booking #{self.id} - {self.guest.username}"


class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHOD = [
        ('upi', 'UPI'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('cash', 'Cash'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD,
        default="cash"
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="pending"
    )

    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Payment for Booking #{self.booking.id}"


class RoomReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="reviews")

    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'room')

    def __str__(self):
        return f"{self.room.room_number} - {self.rating}⭐"
