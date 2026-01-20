from django import forms
from datetime import date
from .models import Booking, Payment


#  ROOM SEARCH FORM
class RoomSearchForm(forms.Form):
    check_in = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )
    guests = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=2
    )

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")

        if check_in and check_out:
            if check_in < date.today():
                raise forms.ValidationError(
                    "Check-in date cannot be in the past."
                )

            if check_out <= check_in:
                raise forms.ValidationError(
                    "Check-out date must be after check-in date."
                )

        return cleaned_data


#  BOOKING FORM
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["check_in_date", "check_out_date", "number_of_guests"]
        widgets = {
            "check_in_date": forms.DateInput(attrs={"type": "date"}),
            "check_out_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get("check_in_date")
        check_out = cleaned_data.get("check_out_date")

        if check_in and check_out:
            if check_in < date.today():
                raise forms.ValidationError(
                    "Check-in date cannot be in the past."
                )

            if check_out <= check_in:
                raise forms.ValidationError(
                    "Check-out date must be after check-in date."
                )

        return cleaned_data


# PAYMENT FORM
class PaymentForm(forms.ModelForm):
    card_number = forms.CharField(
        max_length=16,
        min_length=16,
        required=False
    )
    expiry_date = forms.CharField(
        max_length=5,
        help_text="MM/YY",
        required=False
    )
    cvv = forms.CharField(
        max_length=3,
        min_length=3,
        required=False
    )

    class Meta:
        model = Payment
        fields = ["payment_method", "amount"]
        widgets = {
            "payment_method": forms.Select(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly"
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get("payment_method")

        #  Conditional validation (REAL-WORLD FEATURE)
        if method in ["credit_card", "debit_card"]:
            if not cleaned_data.get("card_number"):
                raise forms.ValidationError("Card number is required.")
            if not cleaned_data.get("expiry_date"):
                raise forms.ValidationError("Expiry date is required.")
            if not cleaned_data.get("cvv"):
                raise forms.ValidationError("CVV is required.")

        return cleaned_data


from .models import RoomReview

class RoomReviewForm(forms.ModelForm):
    class Meta:
        model = RoomReview
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Write your review..."
            }),
        }
