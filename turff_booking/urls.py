from django.contrib import admin
from django.urls import path
from turff_app.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('turfs/', TurfListCreateView.as_view()),
    path('turfs/<int:t_id>/',TurfGetUpdateDelete.as_view()),
    path('booking/',BookingCreateView.as_view()),
    path("booking/<int:b_id>/",BookingGetCancelDelete.as_view()),
    path("availability/",TurffAvailability.as_view())
]
