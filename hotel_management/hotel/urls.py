from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("rooms/", views.room_list, name="room_list"),
    path("room/<int:pk>/", views.room_detail, name="room_detail"),
    path("book/<int:room_id>/", views.make_booking, name="book_room"),
    path("payment/<int:booking_id>/", views.payment, name="payment"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path( "booking/<int:booking_id>/",views.booking_details,name="booking_details"),
    path("booking/cancel/<int:booking_id>/",views.cancel_booking,name="cancel_booking"),
    path("room/<int:room_id>/review/", views.add_review, name="add_review"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

]
