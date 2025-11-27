from django.urls import path
from . import views

urlpatterns = [
     path("", views.route_tools, name="route_tools"),
     
]
