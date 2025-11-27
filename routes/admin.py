from django.contrib import admin
from .models import Route, RouteNode

class RouteNodeInline(admin.TabularInline):
    model = RouteNode
    extra = 1

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    inlines = [RouteNodeInline]
    list_display = ["name"]

@admin.register(RouteNode)
class RouteNodeAdmin(admin.ModelAdmin):
    list_display = ["route", "airport_code", "position", "duration"]
    list_filter = ["route", "airport_code"]
    ordering = ["route", "position"]
